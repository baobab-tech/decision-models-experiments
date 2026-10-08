# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "torch==2.14.1",
#   "transformers==5.19.0",
#   "datasets==5.1.0",
#   "huggingface_hub>=1.16,<2",
#   "numpy",
#   "pycountry==24.6.1",
# ]
# ///
"""Experiment 02: per-label and macro scores for each fine-tuned tagger (common/per_label.py).

Reads probabilities from the repo's probs.npz or results/probs/<repo name>.npz (predict_saved.py), applies the
run's fitted threshold and the country lookup, checks the test micro-F1 against the run's metrics.json, and writes
results/per_label/<repo name>.json with two reports: test (600 excerpts) and pooled validation + test (900).
The threshold was fitted on validation, so the pooled report is slightly optimistic; it gives rare labels more positives.

Usage: uv run score_per_label.py [repo ...]   (default: every repo with probabilities)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download

from train_encoder import DATASET, FIELDS, country_lookup, label_space, score, to_sets

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from per_label import per_label_report  # noqa: E402


def probs_for(api, repo) -> np.lib.npyio.NpzFile | None:
    local = HERE / "results/probs" / f"{repo.split('/')[-1]}.npz"
    if local.exists():
        return np.load(local)
    if "probs.npz" in api.list_repo_files(repo):
        return np.load(hf_hub_download(repo, "probs.npz"))
    return None


def main() -> None:
    api = HfApi()
    repos = sys.argv[1:] or [m.id for m in api.list_models(author="baobabtech", search="evaldocs-excerpt-tagger")
                             if "lookup" in m.id]
    out_dir = HERE / "results/per_label"
    out_dir.mkdir(parents=True, exist_ok=True)
    lookup, cache, summary = country_lookup(), {}, []
    for repo in repos:
        probs = probs_for(api, repo)
        if probs is None:
            print(f"skip {repo}: no probabilities")
            continue
        run = json.load(open(hf_hub_download(repo, "run.json")))
        metrics = json.load(open(hf_hub_download(repo, "metrics.json")))
        rev = run["dataset_revision"]
        if rev not in cache:
            d = load_dataset(DATASET, "llm_labels", revision=rev)
            cache[rev] = ({s: list(d[s]) for s in ("train", "validation", "test")},
                          load_dataset(DATASET, "taxonomy", split="train", revision=rev))
        data, tax = cache[rev]
        space, country_region = label_space(tax, run["exclude_fields"])
        train = data["train"]
        if run["train_sample"] != "all":
            train = [r for r in train if r.get("sample", "random") == run["train_sample"]]
        if run.get("limit_train"):
            train = train[:run["limit_train"]]
        t = metrics["threshold"]
        preds = {}
        for split, key in (("validation", "val"), ("test", "test")):
            rows = data[split]
            assert list(probs[f"{key}_ids"]) == [r["excerpt_id"] for r in rows], f"{repo}: {split} order differs"
            preds[split] = to_sets(probs[key], rows, space, country_region, t, lookup)
        fields = tuple(run["fields_scored"])
        check = score(preds["test"], data["test"], fields)["mean_field_score"]
        expected = metrics["fitted"]["mean_field_score"]
        flag = "" if abs(check - expected) < 0.3 else f"  MISMATCH (metrics.json {expected:.1f})"
        name = repo.split("/")[-1]
        report = {
            "repo": repo, "threshold": t, "test_mean_field_score": round(check, 2),
            "test": per_label_report(preds["test"], data["test"], fields, train),
            "validation_and_test": per_label_report({**preds["validation"], **preds["test"]},
                                                    data["validation"] + data["test"], fields, train),
        }
        json.dump(report, open(out_dir / f"{name}.json", "w"), indent=1)
        macro = {f: report["validation_and_test"][f]["macro_f1"] for f in fields}
        print(f"{name}: micro mean {check:.1f}{flag}; macro (val+test) {macro}")
        summary.append((name.removeprefix("evaldocs-excerpt-tagger-"), check, report["validation_and_test"]))
    if not sys.argv[1:]:
        write_summary(summary, out_dir / "summary.md")


def write_summary(summary, path) -> None:
    """Micro (test) and macro (validation + test) per model, and per-label F1 for themes and methods."""
    fields = ("themes", "regions", "methods")
    lines = ["| Model | Micro mean (test) | " + " | ".join(f"Macro {f} [95% CI]" for f in fields) + " |",
             "|---|---:|" + "---:|" * len(fields)]
    first = summary[0][2] if summary else None
    lines.insert(0, "Macro over labels with ≥5 reference positives in validation + test (900 excerpts). "
                    "LLM vs LLM macro: " + ", ".join(f"{f} {first[f]['llm_macro_f1']}" for f in fields) + ".\n" if first else "")
    for name, micro, rep in sorted(summary, key=lambda x: -x[1]):
        lines.append(f"| {name} | {micro:.1f} | " + " | ".join(
            f"{rep[f]['macro_f1']} [{rep[f]['macro_ci'][0]}, {rep[f]['macro_ci'][1]}]" for f in fields) + " |")
    for f in ("themes", "methods"):
        codes = [c for c, s in first[f]["labels"].items() if s["n_ref"] >= first[f]["min_support"]]
        codes.sort(key=lambda c: -first[f]["labels"][c]["n_ref"])
        lines += ["", f"Per-label F1, {f} (validation + test)", "",
                  "| Label | Ref. positives | LLM vs LLM | " + " | ".join(n for n, _, _ in summary) + " |",
                  "|---|---:|---:|" + "---:|" * len(summary)]
        for c in codes:
            s0 = first[f]["labels"][c]
            lines.append(f"| {c} | {s0['n_ref']:.0f} | {s0['llm_f1']} | " + " | ".join(
                str(rep[f]["labels"].get(c, {}).get("model_f1")) for _, _, rep in summary) + " |")
    path.write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()

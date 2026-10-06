"""Fit per-model, per-field Noul thresholds on the validation sample, then re-score the test run with them.

Reads the latest validation and test runs of a model from results/raw/ (no new model calls).
Objective: micro-F1, mean over the two labelling LLMs. Grid 0.05-0.95 step 0.05; ties go to the higher threshold.
Countries are fitted first; regions are then fitted as direct region Nouls ∪ regions of countries at the
fitted country threshold.

Usage: uv run fit.py --model jev
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from run import HERE, add_regions, load
from score import FIELDS, LLMS, items, micro_f1, references, score

GRID = [round(0.05 * i, 2) for i in range(1, 20)]


def latest_raw(model: str, split: str, variant: str, countries: str) -> Path:
    tag = f"{model}-{variant}-{countries}-{'val-' if split == 'validation' else ''}2026"
    runs = sorted(p for p in (HERE / "results/raw").glob(f"{tag}*") if (p / "responses.jsonl").exists())
    if not runs:
        raise SystemExit(f"no {split} run for {model} ({tag}*)")
    return runs[-1] / "responses.jsonl"


def probabilities(path: Path) -> dict:
    """{excerpt_id: {field: {code: p}}} from a run's responses."""
    out: dict = {}
    for r in map(json.loads, path.open()):
        if "error" in r:
            continue
        eid, field, _ = r["id"].split("::")
        out.setdefault(eid, {}).setdefault(field, {}).update(
            {k.split("__", 1)[1]: a.get("noul", 0.0) for k, a in r["answers"].items()})
    return out


def predict(probs: dict, thresholds: dict, tax) -> dict:
    preds = {e: {f: {c for c, p in codes.items() if p >= thresholds[f]} for f, codes in fields.items()}
             for e, fields in probs.items()}
    add_regions(preds, tax)
    return preds


def fit(probs: dict, sample, tax) -> tuple[dict, dict]:
    refs = references(sample)
    thresholds = {f: 0.5 for f in FIELDS}
    curves = {}
    for f in ("themes", "countries", "methods", "regions"):  # regions last: depends on the country threshold
        ids = items(sample, f)
        curve = {}
        for t in GRID:
            preds = predict(probs, {**thresholds, f: t}, tax)
            curve[t] = sum(micro_f1(preds, refs[m], ids, f) for m in LLMS) / len(LLMS)
        best = max(curve.values())
        thresholds[f] = max(t for t, v in curve.items() if v == best)
        curves[f] = curve
    return thresholds, curves


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--variant", default="definitions")
    ap.add_argument("--countries", default="excerpts")
    args = ap.parse_args()

    tax, val = load(None, "validation")
    _, test = load(None, "test")
    val_path = latest_raw(args.model, "validation", args.variant, args.countries)
    test_path = latest_raw(args.model, "test", args.variant, args.countries)
    thresholds, curves = fit(probabilities(val_path), val, tax)

    metrics = {"fitted": score(predict(probabilities(test_path), thresholds, tax), test),
               "at_0.5": score(predict(probabilities(test_path), {f: 0.5 for f in FIELDS}, tax), test),
               "validation_fitted": score(predict(probabilities(val_path), thresholds, tax), val)}
    out = HERE / "results" / f"{args.model}-{args.variant}-{args.countries}-thresholds"
    out.mkdir(parents=True, exist_ok=True)
    (out / "thresholds.json").write_text(json.dumps({
        "model": args.model, "date": datetime.now(timezone.utc).isoformat(), "thresholds": thresholds,
        "objective": "micro-F1, mean vs glm and deepseek, on the validation sample", "grid": [GRID[0], GRID[-1], 0.05],
        "ties": "higher threshold", "validation_run": val_path.parent.name, "test_run": test_path.parent.name,
        "validation_curves": curves}, indent=1) + "\n")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    print(f"{args.model}: thresholds {thresholds}")
    for k in ("at_0.5", "fitted"):
        m = metrics[k]
        print(f"  test {k:7} mean {m['mean_field_score']:5.1f} | " + " ".join(
            f"{f} {v['micro_f1']:5.1f} ({v['labels_per_item']:.2f}/it)" for f, v in m["fields"].items()))
    print(f"  validation fitted mean {metrics['validation_fitted']['mean_field_score']:.1f}")


if __name__ == "__main__":
    main()

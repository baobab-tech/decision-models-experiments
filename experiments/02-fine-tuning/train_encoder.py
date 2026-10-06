# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "torch==2.14.1",
#   "transformers==5.19.0",
#   "datasets==5.1.0",
#   "huggingface_hub>=1.16,<2",
#   "numpy",
# ]
# ///
"""Experiment 02, first step: fine-tune a small encoder (default ModernBERT-base) to tag evaluation-report excerpts.

Input: the excerpt followed by its document context (title, first 100 words, executive summary and abstract),
the same text the labelling LLMs saw. One forward pass per excerpt; one sigmoid output per label (themes 22, regions 17, countries 198, methods 24).
Findings and recommendations supervise themes, regions and countries; methodology excerpts supervise methods.
Targets are soft: the share of labelling LLMs (GLM-5.3-Flash, DeepSeek-V4.1-Flash) that chose the label.
Scoring matches experiment 01: micro-F1 x 100 per field against each labelling LLM, averaged, on the 600 test excerpts,
regions = predicted regions ∪ regions of predicted countries. One threshold is fitted on the 300-excerpt
validation sample (grid 0.05-0.95; ties go higher). Everything is read from the Hub, so anyone can rerun it:

  hf jobs uv run --flavor a10g-small --timeout 1h --namespace baobabtech -s HF_TOKEN \
      experiments/02-fine-tuning/train_encoder.py -- --labels llm --base jhu-clsp/ettin-encoder-150m

No human gold labels exist: scores measure agreement with LLMs, not correctness.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import time
from datetime import datetime, timezone

import numpy as np
import torch
from datasets import load_dataset, load_from_disk
from huggingface_hub import HfApi
from transformers import AutoModel, AutoTokenizer

DATASET = "baobabtech/decision-models-evaluation-docs"
BASE = "answerdotai/ModernBERT-base"  # default; --base picks another encoder
FIELDS = ("themes", "regions", "countries", "methods")
FINDINGS_FIELDS = ("themes", "regions", "countries")
LABELLERS = ("glm", "deepseek")


class Tagger(torch.nn.Module):
    def __init__(self, n_labels: int, base: str, revision: str, trust_remote_code: bool):
        super().__init__()
        self.encoder = AutoModel.from_pretrained(base, revision=revision, trust_remote_code=trust_remote_code)
        self.head = torch.nn.Linear(self.encoder.config.hidden_size, n_labels)

    def forward(self, input_ids, attention_mask):
        hidden = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        pooled = (hidden * attention_mask.unsqueeze(-1)).sum(1) / attention_mask.sum(1, keepdim=True)
        return self.head(pooled)


def label_space(tax) -> tuple[list[tuple[str, str]], dict[str, str]]:
    """(field, code) for every output, and country -> region."""
    asked = tax.filter(lambda r: r["in_excerpts"])
    space = [(r["field"], r["code"]) for r in asked if r["field"] in FIELDS]
    country_region = {r["code"]: r["region"] for r in tax if r["field"] == "countries"}
    return space, country_region


def targets(row, space, source: str) -> tuple[list[float], list[float]]:
    """Soft target and loss mask per output."""
    methodology = row["type"] == "methodology"
    y, mask = [], []
    for field, code in space:
        active = (field == "methods") == methodology
        mask.append(1.0 if active else 0.0)
        if not active:
            y.append(0.0)
        elif source == "pipeline":
            y.append(1.0 if code in (row[f"{field}_pipeline"] or []) else 0.0)
        else:
            y.append(sum(code in (row[f"{field}_{m}"] or []) for m in LABELLERS) / len(LABELLERS))
    return y, mask


def predict(model, tok, rows, device, max_len, batch) -> np.ndarray:
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(rows), batch):
            enc = tok([r["input"] for r in rows[i:i + batch]], truncation=True, max_length=max_len, padding=True,
                      return_tensors="pt").to(device)
            out.append(torch.sigmoid(model(enc["input_ids"], enc["attention_mask"])).float().cpu().numpy())
    return np.concatenate(out)


def to_sets(probs, rows, space, country_region, t) -> dict:
    preds = {}
    for p, row in zip(probs, rows):
        fields = ("methods",) if row["type"] == "methodology" else FINDINGS_FIELDS
        sets = {f: {code for (field, code), v in zip(space, p) if field == f and v >= t} for f in fields}
        if "regions" in sets:
            sets["regions"] |= {country_region[c] for c in sets["countries"] if country_region.get(c)}
        preds[row["excerpt_id"]] = sets
    return preds


def score(preds, rows) -> dict:
    """Micro-F1 x 100 per field against each labelling LLM, averaged over LLMs; mean over fields."""
    out = {}
    for f in FIELDS:
        ids = [r for r in rows if (r["type"] == "methodology") == (f == "methods")]
        vs = []
        for m in LABELLERS:
            tp = fp = fn = 0
            for r in ids:
                p, ref = preds[r["excerpt_id"]].get(f, set()), set(r[f"{f}_{m}"] or [])
                tp, fp, fn = tp + len(p & ref), fp + len(p - ref), fn + len(ref - p)
            vs.append(100 * 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 100.0)
        out[f] = {"micro_f1": sum(vs) / len(vs), "n": len(ids),
                  "labels_per_item": sum(len(preds[r["excerpt_id"]].get(f, ())) for r in ids) / len(ids)}
    return {"fields": out, "mean_field_score": sum(v["micro_f1"] for v in out.values()) / len(FIELDS)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", choices=("llm", "pipeline"), default="llm")
    ap.add_argument("--base", default=BASE, help="encoder to fine-tune")
    ap.add_argument("--base-revision", default=None, help="commit; resolved and recorded if omitted")
    ap.add_argument("--trust-remote-code", action="store_true", help="needed for e.g. chandar-lab/NeoBERT")
    ap.add_argument("--dataset-revision", default="main")
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--max-len", type=int, default=1024, help="input = excerpt + document context (~600 tokens)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--local-data", help="load llm_labels from a save_to_disk folder (smoke tests)")
    ap.add_argument("--limit-train", type=int, help="smoke tests: first N training excerpts")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--push-to", default="baobabtech/evaldocs-tagger", help="repo prefix; base and labels appended")
    args = ap.parse_args()

    random.seed(args.seed), np.random.seed(args.seed), torch.manual_seed(args.seed)
    device = "cuda" if torch.cuda.is_available() else ("mps" if torch.backends.mps.is_available() else "cpu")
    started = datetime.now(timezone.utc)

    tax = load_dataset(DATASET, "taxonomy", split="train", revision=args.dataset_revision)
    data = load_from_disk(args.local_data) if args.local_data else \
        load_dataset(DATASET, "llm_labels", revision=args.dataset_revision)
    train, val, test = (list(data[s]) for s in ("train", "validation", "test"))
    if args.limit_train:
        train = train[:args.limit_train]
    space, country_region = label_space(tax)
    print(f"device {device}; outputs {len(space)}; train {len(train)} val {len(val)} test {len(test)}; "
          f"labels {args.labels}")

    base_revision = HfApi().model_info(args.base, revision=args.base_revision).sha
    tok = AutoTokenizer.from_pretrained(args.base, revision=base_revision, trust_remote_code=args.trust_remote_code)
    model = Tagger(len(space), args.base, base_revision, args.trust_remote_code).to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=args.lr, weight_decay=0.01)
    steps = args.epochs * -(-len(train) // args.batch)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=args.lr, total_steps=steps, pct_start=0.1)
    ys = [targets(r, space, args.labels) for r in train]

    t0 = time.perf_counter()
    for epoch in range(args.epochs):
        model.train()
        order = list(range(len(train)))
        random.shuffle(order)
        total = 0.0
        for i in range(0, len(order), args.batch):
            idx = order[i:i + args.batch]
            enc = tok([train[j]["input"] for j in idx], truncation=True, max_length=args.max_len, padding=True,
                      return_tensors="pt").to(device)
            y = torch.tensor([ys[j][0] for j in idx], device=device)
            mask = torch.tensor([ys[j][1] for j in idx], device=device)
            logits = model(enc["input_ids"], enc["attention_mask"])
            loss = (torch.nn.functional.binary_cross_entropy_with_logits(logits, y, reduction="none") * mask).sum() \
                / mask.sum()
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
            total += loss.item() * len(idx)
        val_score = score(to_sets(predict(model, tok, val, device, args.max_len, 64), val, space, country_region, 0.5),
                          val)["mean_field_score"]
        print(f"epoch {epoch + 1}: train loss {total / len(train):.4f}; validation mean at 0.5 {val_score:.1f}")
    train_s = time.perf_counter() - t0

    val_probs = predict(model, tok, val, device, args.max_len, 64)
    grid = [round(0.05 * i, 2) for i in range(1, 20)]
    curve = {t: score(to_sets(val_probs, val, space, country_region, t), val)["mean_field_score"] for t in grid}
    best_t = max(t for t, v in curve.items() if v == max(curve.values()))

    t1 = time.perf_counter()
    test_probs = predict(model, tok, test, device, args.max_len, 64)
    infer_s = time.perf_counter() - t1
    results = {t_name: score(to_sets(test_probs, test, space, country_region, t), test)
               for t_name, t in (("at_0.5", 0.5), ("fitted", best_t))}
    tokens = [len(tok(r["input"], truncation=True, max_length=args.max_len)["input_ids"]) for r in test]
    params = sum(p.numel() for p in model.parameters())
    metrics = {
        **results, "threshold": best_t, "validation_curve": curve,
        "compute": {"parameters": params, "tokens_per_excerpt": float(np.mean(tokens)),
                    "flops_per_excerpt_est": 2 * params * float(np.mean(tokens))},
        "train_seconds": round(train_s, 1), "test_inference_seconds": round(infer_s, 1),
    }
    run = {
        "experiment": "02-fine-tuning", "step": "first", "date": started.isoformat(), "base": args.base,
        "base_revision": base_revision, "dataset": DATASET, "dataset_revision": args.dataset_revision,
        "training_labels": "soft share of glm, deepseek" if args.labels == "llm" else "pipeline",
        "reference": "test: mean agreement with glm and deepseek", "device": device,
        "gpu": torch.cuda.get_device_name() if device == "cuda" else None,
        "job_id": os.environ.get("JOB_ID"), **{k: v for k, v in vars(args).items() if k not in ("push_to", "local_data", "no_push", "base", "base_revision")},
    }
    print(json.dumps({"run": run, "metrics": {k: metrics[k] for k in ("at_0.5", "fitted", "threshold", "compute")}},
                     indent=1))

    if args.no_push:
        return
    repo = f"{args.push_to}-{args.base.split('/')[-1].lower()}-{args.labels}"
    api = HfApi()
    api.create_repo(repo, private=True, exist_ok=True)
    os.makedirs("out", exist_ok=True)
    torch.save(model.state_dict(), "out/model.pt")
    tok.save_pretrained("out")
    json.dump({"labels": [f"{f}:{c}" for f, c in space]}, open("out/labels.json", "w"))
    json.dump(run, open("out/run.json", "w"), indent=1)
    json.dump(metrics, open("out/metrics.json", "w"), indent=1)
    api.upload_folder(folder_path="out", repo_id=repo, commit_message=f"Run {started:%Y-%m-%dT%H:%M}Z")
    print(f"pushed to {repo}")


if __name__ == "__main__":
    main()

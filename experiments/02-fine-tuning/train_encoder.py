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

import re

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
CONTEXT_HEADING = "## CONTEXT SECTIONS"  # `input` = excerpt block, then this heading and the document context
EXCERPTS_PER_DOC = 134.6  # dataset `excerpts` config: 191,136 excerpts over 1,420 documents


COUNTRY_ALIASES = {  # names pycountry does not list, or lists differently
    "vietnam": "VN", "tanzania": "TZ", "bolivia": "BO", "laos": "LA", "lao pdr": "LA", "syria": "SY", "iran": "IR",
    "russia": "RU", "south korea": "KR", "north korea": "KP", "moldova": "MD", "drc": "CD", "dr congo": "CD",
    "democratic republic of the congo": "CD", "republic of congo": "CG", "côte d'ivoire": "CI", "cote d'ivoire": "CI",
    "ivory coast": "CI", "palestine": "PS", "gaza": "PS", "west bank": "PS", "uk": "GB", "united kingdom": "GB",
    "usa": "US", "united states": "US", "venezuela": "VE", "turkey": "TR", "türkiye": "TR", "czech republic": "CZ",
    "kyrgyzstan": "KG", "cape verde": "CV", "eswatini": "SZ", "swaziland": "SZ", "burma": "MM", "myanmar": "MM",
    "macedonia": "MK", "kosovo": "XK", "micronesia": "FM", "taiwan": "TW", "the gambia": "GM", "gambia": "GM",
}


def country_lookup():
    """Country-name lookup over the excerpt, title and Document Start (not the summaries, which mention
    comparison and donor countries). Returns text -> set of ISO alpha-2 codes."""
    import pycountry
    names = {n.lower(): c.alpha_2 for c in pycountry.countries
             for n in {c.name, getattr(c, "common_name", None), getattr(c, "official_name", None)} - {None}}
    names.update(COUNTRY_ALIASES)
    pat = re.compile(r"\b(" + "|".join(sorted(map(re.escape, names), key=len, reverse=True)) + r")\b", re.I)

    def find(input_text: str) -> set[str]:
        excerpt, context = split_input(input_text)
        text = excerpt + "\n" + context.split("### Executive Summary")[0].split("### Abstract")[0]
        return {names[m.group(1).lower()] for m in pat.finditer(text)}
    return find


def split_input(text: str) -> tuple[str, str]:
    """(excerpt block, document context block) of an `input` string."""
    i = text.find(CONTEXT_HEADING)
    return (text, "") if i < 0 else (text[:i].strip(), text[i:].strip())


def special_ids(tok) -> tuple[list[int], list[int], int]:
    """Start and separator ids (CLS/SEP, or BOS/EOS for decoder-style tokenizers) and the pad id."""
    start = tok.cls_token_id if tok.cls_token_id is not None else tok.bos_token_id
    sep = tok.sep_token_id if tok.sep_token_id is not None else tok.eos_token_id
    pad = tok.pad_token_id if tok.pad_token_id is not None else (sep if sep is not None else 0)
    return ([start] if start is not None else []), ([sep] if sep is not None else []), pad


def pad_batch(seqs: list[list[int]], masks: list[list[int]], pad: int, device) -> dict:
    n = max(len(x) for x in seqs)
    ids = torch.tensor([x + [pad] * (n - len(x)) for x in seqs], device=device)
    att = torch.tensor([[1] * len(x) + [0] * (n - len(x)) for x in seqs], device=device)
    pool = torch.tensor([m + [0] * (n - len(m)) for m in masks], device=device, dtype=torch.float)
    return {"input_ids": ids, "attention_mask": att, "pool_mask": pool}


def encode(tok, rows, max_len: int, device, arch: str, context_first: bool = False) -> dict:
    """joint: [start] excerpt [sep] context [sep], pooled over the excerpt's tokens only. With context_first
    (for one-directional decoders, whose tokens see only earlier tokens): [start] context [sep] excerpt [sep].
    two_tower: excerpt and context encoded separately (context once per document at inference)."""
    start, sep, pad = special_ids(tok)
    parts = [split_input(r["input"]) for r in rows]
    ex = [tok(e, add_special_tokens=False)["input_ids"][: max_len // 2] for e, _ in parts]
    cx = [tok(c, add_special_tokens=False)["input_ids"] for _, c in parts]
    if arch == "joint":
        seqs, masks = [], []
        for e, c in zip(ex, cx):
            room = max_len - len(start) - len(e) - 2 * len(sep)
            c = c[:max(room, 0)]
            if context_first:
                seq = start + c + sep + e + sep
                masks.append([0] * (len(start) + len(c) + len(sep)) + [1] * len(e) + [0] * len(sep))
            else:
                seq = start + e + sep + c + sep
                masks.append([0] * len(start) + [1] * len(e) + [0] * (len(seq) - len(start) - len(e)))
            seqs.append(seq)
        return {"joint": pad_batch(seqs, masks, pad, device)}
    exs = [start + e + sep for e in ex]
    cxs = [start + c[: max_len - len(start) - len(sep)] + sep for c in cx]
    return {"excerpt": pad_batch(exs, [[1] * len(x) for x in exs], pad, device),
            "context": pad_batch(cxs, [[1] * len(x) for x in cxs], pad, device)}


class Tagger(torch.nn.Module):
    """joint: one pass over excerpt + context, mean-pooled over the excerpt's tokens.
    two_tower: one shared encoder; excerpt vector e and document-context vector c combined as [e, c, e*c]."""

    def __init__(self, n_labels: int, base: str, revision: str, trust_remote_code: bool, arch: str):
        super().__init__()
        self.arch = arch
        self.encoder = AutoModel.from_pretrained(base, revision=revision, trust_remote_code=trust_remote_code)
        h = self.encoder.config.hidden_size if hasattr(self.encoder.config, "hidden_size") \
            else self.encoder.config.get_text_config().hidden_size
        self.head = torch.nn.Linear(h, n_labels) if arch == "joint" else \
            torch.nn.Sequential(torch.nn.LayerNorm(3 * h), torch.nn.Linear(3 * h, n_labels))

    def pool(self, input_ids, attention_mask, pool_mask):
        hidden = self.encoder(input_ids=input_ids, attention_mask=attention_mask).last_hidden_state
        return (hidden * pool_mask.unsqueeze(-1)).sum(1) / pool_mask.sum(1, keepdim=True).clamp(min=1)

    def forward(self, batch):
        if self.arch == "joint":
            return self.head(self.pool(**batch["joint"]))
        e, c = self.pool(**batch["excerpt"]), self.pool(**batch["context"])
        return self.head(torch.cat([e, c, e * c], dim=-1))


def label_space(tax, exclude=()) -> tuple[list[tuple[str, str]], dict[str, str]]:
    """(field, code) for every output, and country -> region."""
    asked = tax.filter(lambda r: r["in_excerpts"])
    space = [(r["field"], r["code"]) for r in asked if r["field"] in FIELDS and r["field"] not in exclude]
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


def predict(model, tok, rows, device, max_len, batch, arch, context_first=False) -> np.ndarray:
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(rows), batch):
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=device == "cuda"):
                logits = model(encode(tok, rows[i:i + batch], max_len, device, arch, context_first))
            out.append(torch.sigmoid(logits.float()).cpu().numpy())
    return np.concatenate(out)


def to_sets(probs, rows, space, country_region, t, lookup=None) -> dict:
    """Labels at threshold t; with lookup, countries come from the country-name lookup instead of the model."""
    preds = {}
    for p, row in zip(probs, rows):
        fields = ("methods",) if row["type"] == "methodology" else FINDINGS_FIELDS
        sets = {f: {code for (field, code), v in zip(space, p) if field == f and v >= t} for f in fields}
        if lookup is not None and "countries" in sets:
            sets["countries"] = lookup(row["input"])
        if "regions" in sets:
            sets["regions"] |= {country_region[c] for c in sets["countries"] if country_region.get(c)}
        preds[row["excerpt_id"]] = sets
    return preds


def score(preds, rows, fields=FIELDS) -> dict:
    """Micro-F1 x 100 per field against each labelling LLM, averaged over LLMs; mean over fields."""
    out = {}
    for f in fields:
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
    return {"fields": out, "mean_field_score": sum(v["micro_f1"] for v in out.values()) / len(fields)}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--labels", choices=("llm", "pipeline"), default="llm")
    ap.add_argument("--base", default=BASE, help="encoder to fine-tune")
    ap.add_argument("--arch", choices=("joint", "two_tower"), default="joint",
                    help="joint: excerpt + context in one pass, pooled over the excerpt; "
                         "two_tower: context encoded once per document")
    ap.add_argument("--exclude-fields", nargs="*", default=(), choices=FIELDS,
                    help="train without these outputs, e.g. countries")
    ap.add_argument("--country-lookup", action="store_true",
                    help="countries from the country-name lookup (excerpt, title, Document Start), not the model")
    ap.add_argument("--context-first", action="store_true",
                    help="joint input with context before the excerpt, for one-directional (decoder) encoders")
    ap.add_argument("--base-revision", default=None, help="commit; resolved and recorded if omitted")
    ap.add_argument("--trust-remote-code", action="store_true", help="needed for e.g. chandar-lab/NeoBERT")
    ap.add_argument("--dataset-revision", default="main")
    ap.add_argument("--epochs", type=int, default=5)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--batch", type=int, default=32, help="effective batch (optimizer step)")
    ap.add_argument("--micro-batch", type=int, default=8, help="examples per forward pass; gradients accumulate")
    ap.add_argument("--max-len", type=int, default=1024, help="input = excerpt + document context (~600 tokens)")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--local-data", help="load llm_labels from a save_to_disk folder (smoke tests)")
    ap.add_argument("--limit-train", type=int, help="smoke tests: first N training excerpts")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--push-to", default="baobabtech/evaldocs-excerpt-tagger", help="repo prefix; base and labels appended")
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
    space, country_region = label_space(tax, args.exclude_fields)
    lookup = country_lookup() if args.country_lookup else None
    scored = tuple(f for f in FIELDS if f not in args.exclude_fields or (f == "countries" and lookup))
    print(f"device {device}; outputs {len(space)}; train {len(train)} val {len(val)} test {len(test)}; "
          f"labels {args.labels}")

    base_revision = HfApi().model_info(args.base, revision=args.base_revision).sha
    tok = AutoTokenizer.from_pretrained(args.base, revision=base_revision, trust_remote_code=args.trust_remote_code)
    model = Tagger(len(space), args.base, base_revision, args.trust_remote_code, args.arch).to(device)
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
            # micro-batches with gradient accumulation keep the effective batch at --batch within GPU memory
            n_active = sum(sum(ys[j][1]) for j in idx)
            opt.zero_grad()
            for k in range(0, len(idx), args.micro_batch):
                sub = idx[k:k + args.micro_batch]
                batch_in = encode(tok, [train[j] for j in sub], args.max_len, device, args.arch, args.context_first)
                y = torch.tensor([ys[j][0] for j in sub], device=device)
                mask = torch.tensor([ys[j][1] for j in sub], device=device)
                with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=device == "cuda"):
                    logits = model(batch_in)
                loss = (torch.nn.functional.binary_cross_entropy_with_logits(logits.float(), y, reduction="none")
                        * mask).sum() / n_active
                loss.backward()
                total += loss.item() * len(idx)
            opt.step()
            sched.step()
        val_score = score(to_sets(predict(model, tok, val, device, args.max_len, 16, args.arch, args.context_first), val, space, country_region, 0.5, lookup),
                          val, scored)["mean_field_score"]
        print(f"epoch {epoch + 1}: train loss {total / len(train):.4f}; validation mean at 0.5 {val_score:.1f}")
    train_s = time.perf_counter() - t0

    val_probs = predict(model, tok, val, device, args.max_len, 16, args.arch, args.context_first)
    grid = [round(0.05 * i, 2) for i in range(1, 20)]
    curve = {t: score(to_sets(val_probs, val, space, country_region, t, lookup), val, scored)["mean_field_score"]
             for t in grid}
    best_t = max(t for t, v in curve.items() if v == max(curve.values()))

    t1 = time.perf_counter()
    test_probs = predict(model, tok, test, device, args.max_len, 16, args.arch, args.context_first)
    infer_s = time.perf_counter() - t1
    results = {t_name: score(to_sets(test_probs, test, space, country_region, t, lookup), test, scored)
               for t_name, t in (("at_0.5", 0.5), ("fitted", best_t))}
    ex_tok = [len(tok(split_input(r["input"])[0], add_special_tokens=False)["input_ids"]) for r in test]
    cx_tok = [len(tok(split_input(r["input"])[1], add_special_tokens=False)["input_ids"]) for r in test]
    # joint reads excerpt + context per excerpt; two_tower reads the context once per document
    per_excerpt = [e + c for e, c in zip(ex_tok, cx_tok)] if args.arch == "joint" else \
        [e + c / EXCERPTS_PER_DOC for e, c in zip(ex_tok, cx_tok)]
    tokens = per_excerpt
    params = sum(p.numel() for p in model.parameters())
    metrics = {
        **results, "threshold": best_t, "validation_curve": curve,
        "compute": {"parameters": params, "tokens_per_excerpt": float(np.mean(tokens)),
                    "excerpt_tokens": float(np.mean(ex_tok)), "context_tokens": float(np.mean(cx_tok)),
                    "excerpts_per_document_assumed": EXCERPTS_PER_DOC if args.arch == "two_tower" else None,
                    "flops_per_excerpt_est": 2 * params * float(np.mean(tokens))},
        "train_seconds": round(train_s, 1), "test_inference_seconds": round(infer_s, 1),
    }
    run = {
        "experiment": "02-fine-tuning", "step": "first", "date": started.isoformat(), "base": args.base,
        "base_revision": base_revision, "dataset": DATASET, "dataset_revision": args.dataset_revision,
        "training_labels": "soft share of glm, deepseek" if args.labels == "llm" else "pipeline",
        "reference": "test: mean agreement with glm and deepseek", "device": device,
        "gpu": torch.cuda.get_device_name() if device == "cuda" else None,
        "job_id": os.environ.get("JOB_ID"), "fields_scored": list(scored),
        **{k: (list(v) if isinstance(v, tuple) else v) for k, v in vars(args).items()
           if k not in ("push_to", "local_data", "no_push", "base", "base_revision")},
    }
    print(json.dumps({"run": run, "metrics": {k: metrics[k] for k in ("at_0.5", "fitted", "threshold", "compute")}},
                     indent=1))

    if args.no_push:
        return
    repo = f"{args.push_to}-{args.base.split('/')[-1].lower()}-{args.labels}" + ("-2tower" if args.arch == "two_tower" else "") \
        + ("-no" + "-".join(args.exclude_fields) if args.exclude_fields else "") + ("-lookup" if args.country_lookup else "")
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

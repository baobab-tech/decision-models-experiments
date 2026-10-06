"""Experiment 01 runner, task B: tag excerpts with a decision model, one Noul per label, and score.

One request per (excerpt, field), split into chunks of at most 128 questions: state = the excerpt;
questions = one Noul per code, thresholded at 0.5.
Raw responses go to results/raw/<run_id>/ (gitignored); run.json and metrics.json go to results/<run_id>/.

Usage:
  uv run run.py --model jev --limit 9
  uv run run.py --model d1 --variant labels --countries all
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import platform
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx
from datasets import load_dataset
from dotenv import load_dotenv

from score import FIELDS, score

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATASET = "baobabtech/decision-models-evaluation-docs"
DATASET_REVISION = "5017706"
THRESHOLD = 0.5
MAX_QUESTIONS = 128  # d1 rejects requests with more than 128 questions (2026-10-04); default chunk size
# Per-model caps: laya-serve rejects more than 64 questions (HTTP 413). Nouls are answered independently,
# so chunk size does not change answers.

# backend, model id, options
MODELS = {
    "jev": ("gateway", "typesafe-ai/jev", {"only": "typesafe-ai"}),
    "d1": ("gateway", "liquid/d1", {"only": "liquid"}),
    "glide": ("systemone", "fastino/GLiDE", {"url": "https://api.fastino.ai/v1/systemone", "key_env": "FASTINO_API_KEY",
                                            "key_header": "X-API-Key", "usd_per_m_input": 0.30}),
    "kev-4b": ("systemone", "kev-latest", {"url": "http://127.0.0.1:8009/v1/systemone",
                                           "revision": "jaredpalmer/kev-4b@139fdd94", "serving": "kev.serve, MLX, bf16"}),
    "kev-0.8b": ("systemone", "kev-latest", {"url": "http://127.0.0.1:8010/v1/systemone",
                                             "revision": "jaredpalmer/kev-0.8b@9a45d25e", "serving": "kev.serve, MLX, bf16"}),
    "gliner-decide": ("bridge", "fastino/GLiNER2.5-Decide", {
        "python": "third_party/gliner/.venv/bin/python", "script": "local/gliner_bridge.py", "args": ["--device", "mps"],
        "revision": "fastino/GLiNER2.5-Decide", "serving": "gliner2 2.0.0, native multi-label, MPS"}),
    "verdict": ("bridge", "heman10x/rlcd-modernbert-151m", {
        "python": "third_party/Verdict-open-jev/.venv/bin/python", "script": "local/verdict_bridge.py",
        "args": ["--device", "cpu"], "revision": "Verdict-open-jev@30f1556; HF calibrator 8af2496e",
        "serving": "rlcd 0.1.0, ONNX Runtime CPU, Nouls"}),
    "laya": ("systemone", None, {"url": "http://127.0.0.1:8000/v1/systemone", "key_env": "LAYA_API_KEY",
                                 "key_header": "Authorization", "max_questions": 64,
                                 "revision": "laya 0.3.27 (Router)", "serving": "laya-serve, PyTorch MPS"}),
}


LABELS = HERE / "results/labels"
LLMS = ("glm", "deepseek")


def attach_llm_labels(sample, suffix: str) -> None:
    """Add <field>_<llm> columns from results/labels/excerpts_<llm>_doc_summary<suffix>.jsonl."""
    per_llm = {m: {r["excerpt_id"]: r["labels"] for r in map(json.loads, (LABELS / f"excerpts_{m}_doc_summary{suffix}.jsonl").open())}
               for m in LLMS}
    for f in FIELDS:
        for m in LLMS:
            sample[f"{f}_{m}"] = [sorted(per_llm[m][e].get(f, [])) for e in sample.index]


def load(limit: int | None, split: str = "test"):
    tax = load_dataset(DATASET, "taxonomy", split="train", revision=DATASET_REVISION).to_pandas()
    exc = load_dataset(DATASET, "excerpts", split=split, revision=DATASET_REVISION).to_pandas()
    if split == "test":
        sample = exc[exc.eval_sample].set_index("excerpt_id").sort_index()
    else:  # threshold-fitting sample; LLM labels come from results/labels, not the dataset
        ids = json.loads((LABELS / "validation_sample.json").read_text())["excerpt_ids"]
        sample = exc.set_index("excerpt_id").loc[sorted(ids)].copy()
        for f in FIELDS:
            sample[f] = sample[f].map(lambda v: list(v) if v is not None else [])
        attach_llm_labels(sample, "_validation")
    if limit:  # spread over the three excerpt types
        sample = sample.groupby("type").head(-(-limit // 3)).iloc[:limit]
    return tax, sample


def options(tax, field: str, countries: str) -> list[tuple[str, str, str | None]]:
    """(code, label, definition) for the codes asked for a field."""
    rows = tax[tax.field == field]
    if not (field == "countries" and countries == "all"):
        rows = rows[rows.in_excerpts]
    return [(r.code, r.label, r.definition_excerpts if isinstance(r.definition_excerpts, str) else None)
            for r in rows.itertuples()]


def noul_text(field: str, label: str, definition: str | None, variant: str) -> str:
    if field == "themes":
        base = f"The excerpt is about {label}"
        return f"{base}: {definition}" if variant == "definitions" and definition else base
    if field == "methods":
        return f"The excerpt describes a {definition or label} method used in the evaluation"
    if field == "regions":
        return f"The excerpt substantively discusses {label} or countries in it, not just a passing mention"
    return f"The excerpt substantively discusses {label}, not just a passing mention"


def build_requests(tax, sample, variant: str, countries: str, max_questions: int = MAX_QUESTIONS) -> list[dict]:
    reqs = []
    for eid, row in sample.iterrows():
        fields = ("methods",) if row["type"] == "methodology" else ("themes", "regions", "countries")
        for f in fields:
            opts = options(tax, f, countries)
            questions = [(f"{f}__{code}", {"type": "noul", "instructions": noul_text(f, label, d, variant)})
                         for code, label, d in opts]
            # label metadata for native multi-label backends (GLiNER); Jev-format backends ignore it
            meta = {f"{f}__{code}": {"label": label,
                                     "description": d if (f == "methods" or variant == "definitions") else None}
                    for code, label, d in opts}
            for i in range(0, len(questions), max_questions):
                chunk = dict(questions[i:i + max_questions])
                reqs.append({"id": f"{eid}::{f}::{i // max_questions}", "state": row["text"], "questions": chunk,
                             "labels": {k: meta[k] for k in chunk}})
    return reqs


def call_gateway(model_id: str, opts: dict, reqs: list[dict], concurrency: int) -> list[dict]:
    cmd = ["node", str(HERE / "gateway/evaluate.mjs"), "--model", model_id, "--concurrency", str(concurrency)]
    if opts.get("only"):
        cmd += ["--only", opts["only"]]
    proc = subprocess.run(cmd, input="".join(json.dumps(r) + "\n" for r in reqs), capture_output=True, text=True,
                          check=True)
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip()]


def call_bridge(opts: dict, reqs: list[dict]) -> list[dict]:
    """Pipe requests through a local Python bridge running in the model's own environment."""
    cmd = [str(ROOT / opts["python"]), str(HERE / opts["script"]), *opts.get("args", [])]
    proc = subprocess.run(cmd, input="".join(json.dumps(r) + "\n" for r in reqs), capture_output=True, text=True,
                          check=True)
    return [json.loads(line) for line in proc.stdout.splitlines() if line.strip().startswith("{")]


async def call_systemone(model_id: str | None, opts: dict, reqs: list[dict], concurrency: int) -> list[dict]:
    headers = {}
    if opts.get("key_env") and os.getenv(opts["key_env"]):
        key = os.environ[opts["key_env"]]
        headers[opts["key_header"]] = f"Bearer {key}" if opts["key_header"] == "Authorization" else key
    sem = asyncio.Semaphore(concurrency)

    async def one(client, req):
        body = {"state": req["state"], "questions": req["questions"], **({"model": model_id} if model_id else {}),
                **opts.get("extra", {})}
        async with sem:
            for attempt in range(5):
                t0 = time.perf_counter()
                try:
                    r = await client.post(opts["url"], json=body, headers=headers)
                    if r.status_code in (425, 429, 500, 502, 503) and attempt < 4:
                        await asyncio.sleep(float(r.headers.get("retry-after", 2 ** attempt * 5)))
                        continue
                    r.raise_for_status()
                    data = r.json()
                    return {"id": req["id"], "answers": data["answers"], "usage": data.get("usage"),
                            "latency_ms": round((time.perf_counter() - t0) * 1000), "model_id": data.get("model")}
                except Exception as e:
                    if attempt == 4:
                        return {"id": req["id"], "error": repr(e)[:500]}
                    await asyncio.sleep(2 ** attempt)

    async with httpx.AsyncClient(timeout=300) as client:  # Fastino advises >= 300 s
        return await asyncio.gather(*(one(client, r) for r in reqs))


def add_regions(preds: dict, tax) -> dict[str, dict]:
    """Regions = direct region Nouls ∪ regions of predicted countries. Returns the direct and derived-only variants."""
    country_region = dict(tax[tax.field == "countries"][["code", "region"]].itertuples(index=False))
    variants = {"regions_direct": {}, "regions_derived": {}}
    for eid, fields in preds.items():
        if "countries" not in fields and "regions" not in fields:
            continue
        direct = fields.get("regions", set())
        derived = {country_region[c] for c in fields.get("countries", ()) if c in country_region}
        variants["regions_direct"][eid] = {"regions": direct}
        variants["regions_derived"][eid] = {"regions": derived}
        fields["regions"] = direct | derived
    return variants


def to_predictions(responses: list[dict]) -> dict:
    preds: dict = {}
    for r in responses:
        if "error" in r:
            continue
        eid, field, _chunk = r["id"].split("::")
        preds.setdefault(eid, {}).setdefault(field, set()).update(
            k.split("__", 1)[1] for k, a in r["answers"].items() if a.get("noul", 0) >= THRESHOLD)
    return preds


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=MODELS, required=True)
    ap.add_argument("--variant", choices=("definitions", "labels"), default="definitions",
                    help="themes asked with or without the excerpt definitions")
    ap.add_argument("--countries", choices=("excerpts", "all"), default="excerpts",
                    help="country codes seen in the excerpts (198) or all ISO codes in the taxonomy (250)")
    ap.add_argument("--limit", type=int, help="first N eval_sample excerpts, spread over the three types")
    ap.add_argument("--split", choices=("test", "validation"), default="test",
                    help="validation: the 300-excerpt threshold-fitting sample")
    ap.add_argument("--concurrency", type=int, default=8)
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    backend, model_id, opts = MODELS[args.model]
    tax, sample = load(args.limit, args.split)
    reqs = build_requests(tax, sample, args.variant, args.countries, opts.get("max_questions", MAX_QUESTIONS))

    started = datetime.now(timezone.utc)
    run_id = f"{args.model}-{args.variant}-{args.countries}-{'val-' if args.split == 'validation' else ''}" \
             f"{'n' + str(len(sample)) + '-' if args.limit else ''}" \
             f"{started:%Y%m%dT%H%M}"
    print(f"{run_id}: {len(sample)} excerpts, {len(reqs)} requests, "
          f"{sum(len(r['questions']) for r in reqs)} Nouls")
    t0 = time.perf_counter()
    if backend == "gateway":
        responses = call_gateway(model_id, opts, reqs, args.concurrency)
    elif backend == "bridge":
        responses = call_bridge(opts, reqs)
    else:
        responses = asyncio.run(call_systemone(model_id, opts, reqs, args.concurrency))
    wall_s = time.perf_counter() - t0

    raw = HERE / "results/raw" / run_id
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "responses.jsonl").write_text("".join(json.dumps(r) + "\n" for r in responses))

    preds = to_predictions(responses)
    variants = add_regions(preds, tax)
    fields = tuple(f for f in FIELDS if any(f in p for p in preds.values()))
    metrics = score(preds, sample, fields)
    if "regions" in fields:
        metrics["regions_variants"] = {k: score(v, sample, ("regions",))["fields"]["regions"]
                                       for k, v in variants.items()}
    ok = [r for r in responses if "error" not in r]
    lat = sorted(r["latency_ms"] for r in ok)
    cost = sum(float((r.get("provider_metadata") or {}).get("gateway", {}).get("cost", 0) or 0) for r in ok)
    if opts.get("usd_per_m_input"):  # list price × reported input tokens
        cost = sum((r.get("usage") or {}).get("input_tokens", 0) for r in ok) * opts["usd_per_m_input"] / 1e6
    metrics.update({
        "errors": len(responses) - len(ok),
        "latency_p50_ms": lat[len(lat) // 2] if lat else None,
        "latency_p95_ms": lat[int(len(lat) * 0.95)] if lat else None,
        "wall_s": round(wall_s, 1),
        "cost_usd": round(cost, 6),
        "input_tokens": sum((r.get("usage") or {}).get("inputTokens") or (r.get("usage") or {}).get("input_tokens") or 0
                            for r in ok),
    })

    out = HERE / "results" / run_id
    out.mkdir(parents=True, exist_ok=True)
    run = {
        "experiment": "01-many-option-classification", "phase": 1, "task": "B", "run_id": run_id,
        "date": started.isoformat(), "model": args.model, "model_id": model_id,
        "where": "gateway" if backend == "gateway" else ("api" if opts.get("url", "").startswith("https") else "local"),
        "provider": sorted({r.get("provider") for r in ok if r.get("provider")}) or None,
        "dataset": DATASET, "dataset_version": DATASET_REVISION, "split": args.split,
        "subset": "eval_sample" if args.split == "test" else "results/labels/validation_sample.json",
        "n": len(sample), "question_format": "noul-per-label", "threshold": THRESHOLD,
        "variant": args.variant, "countries": args.countries,
        "regions": "direct region Nouls ∪ regions of predicted countries (taxonomy map); variants in metrics.json", "reference": "mean agreement with glm and deepseek",
        "hardware": f"{platform.machine()} {platform.system()} (client)" if backend == "gateway" or opts.get("url", "").startswith("https")
        else "Apple M5 Max, 128 GB", "revision": opts.get("revision"), "serving": opts.get("serving"),
        "max_questions_per_request": opts.get("max_questions", MAX_QUESTIONS), "concurrency": args.concurrency,
    }
    (out / "run.json").write_text(json.dumps(run, indent=2) + "\n")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")

    print(f"errors {metrics['errors']}, wall {metrics['wall_s']} s, p50 {metrics['latency_p50_ms']} ms, "
          f"cost ${metrics['cost_usd']}")
    print(f"{'field':10} {'n':>4} {'vsLLMs':>6} {'vsGLM':>6} {'vsDS':>6} {'vsPipe':>6} {'lab/it':>6}")
    for f, m in metrics["fields"].items():
        print(f"{f:10} {metrics['n'][f]:4} {m['micro_f1']:6.1f} {m['micro_f1_vs_glm']:6.1f} {m['micro_f1_vs_deepseek']:6.1f} "
              f"{m['micro_f1_vs_pipeline']:6.1f} {m['labels_per_item']:6.2f}")
    for k, v in metrics.get("regions_variants", {}).items():
        print(f"  {k:16} vsLLMs {v['micro_f1']:5.1f}  lab/it {v['labels_per_item']:.2f}")
    print(f"mean_field_score {metrics['mean_field_score']:.1f} (vs pipeline {metrics['mean_field_score_vs_pipeline']:.1f})")


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.11"
# dependencies = ["datasets>=3", "pandas", "openai>=1.50", "python-dotenv"]
# ///
"""Relabel task B excerpts with an LLM via HF Inference Providers, using the prompts in prompts/excerpt-tagging.md.

Writes one JSON line per excerpt to --out (resumable: excerpts already in the file are skipped).

Usage:
  uv run experiments/common/label_excerpts.py --model glm --limit 10
  uv run experiments/common/label_excerpts.py --model deepseek
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

from datasets import load_dataset
from dotenv import load_dotenv
from openai import AsyncOpenAI

DATASET = "baobabtech/decision-models-evaluation-docs"
DATASET_REVISION = "fcd40f8785aa0e8e6e87f0931dd762368e5c602f"
MODELS = {  # short name -> router model id with pinned provider
    "glm": "zai-org/GLM-5.3-Flash:deepinfra",
    "deepseek": "deepseek-ai/DeepSeek-V4.1-Flash:deepinfra",
    "qwen": "Qwen/Qwen3.8-Flash-Next:featherless-ai",
}
MAX_TOKENS = 16384  # high cap so reasoning never truncates; billing is per token used
TIMEOUT_S = 180
CONCURRENCY = {"glm": 8, "deepseek": 8, "qwen": 2}  # featherless-ai caps concurrent requests per user
ROOT = Path(__file__).resolve().parents[2]

FINDINGS_SYSTEM = """You are an expert evaluator classifying excerpts from evaluation documents.

## Task

Classify the excerpt below by themes, regions and countries.

## Themes (select 1 to 3 maximum per excerpt)

{themes}

## Geography

### Regions
{regions}

### Countries
Use ISO 3166-1 alpha-2 codes (2-letter codes). Examples: GB, KE, US, IN, BD

## Classification Rules

1. Assign 1 to 3 themes per excerpt based on content
2. Include regions and countries substantively discussed (not passing mentions)
3. Leave arrays empty if cannot be determined

## Output Format

Return only a JSON object:
```json
{{"themes": ["theme_code"], "regions": ["region_code"], "countries": ["XX"]}}
```"""

FINDINGS_USER = """Excerpt type: {type}

<excerpt>
{text}
</excerpt>"""

METHODS_SYSTEM = """You are an expert evaluator classifying methodology excerpts from evaluation documents.

## Task

Classify the methodology excerpt below with the research methods used.

## Methods (select all that apply per excerpt)

{methods}

## Classification Rules

1. Assign all relevant methods mentioned in each excerpt
2. Leave array empty if no specific methods can be identified

## Output Format

Return only a JSON object:
```json
{{"methods": ["method_code"]}}
```"""

METHODS_USER = """<excerpt>
{text}
</excerpt>"""


def build_prompts() -> tuple[str, str, dict[str, set[str]]]:
    tax = load_dataset(DATASET, "taxonomy", split="train", revision=DATASET_REVISION).to_pandas()
    asked = tax[tax.in_excerpts]
    themes = asked[asked.field == "themes"]
    regions = asked[asked.field == "regions"]
    methods = asked[asked.field == "methods"]
    findings = FINDINGS_SYSTEM.format(
        themes="\n".join(f"- `{r.code}` ({r.label}): {r.definition_excerpts}" for r in themes.itertuples()),
        regions=", ".join(f"`{c}`" for c in regions.code),
    )
    method = METHODS_SYSTEM.format(
        methods="\n".join(f"- `{r.code}` - {r.definition_excerpts}" for r in methods.itertuples()),
    )
    valid = {
        "themes": set(themes.code),
        "regions": set(regions.code),
        "countries": set(tax[tax.field == "countries"].code),  # any ISO code, as the prompt allows
        "methods": set(methods.code),
    }
    return findings, method, valid


VALIDATION_SAMPLE = {"findings": 150, "recommendations": 75, "methodology": 75}
VALIDATION_IDS = ROOT / "experiments/01-many-option-classification/results/labels/validation_sample.json"


def validation_sample() -> list[dict]:
    """Fixed threshold-fitting sample from the validation split; ids written to VALIDATION_IDS."""
    df = load_dataset(DATASET, "excerpts", split="validation", revision=DATASET_REVISION).to_pandas()
    picks = [df[df["type"] == t].sample(n=n, random_state=0) for t, n in VALIDATION_SAMPLE.items()]
    rows = [r for p in picks for r in p[["excerpt_id", "type", "text"]].to_dict("records")]
    VALIDATION_IDS.parent.mkdir(parents=True, exist_ok=True)
    VALIDATION_IDS.write_text(json.dumps({"dataset_revision": DATASET_REVISION, "split": "validation",
                                          "design": VALIDATION_SAMPLE, "seed": 0,
                                          "excerpt_ids": [r["excerpt_id"] for r in rows]}, indent=1) + "\n")
    return rows


TRAIN_SAMPLE = {"findings": 5000, "recommendations": 2500, "methodology": 2500}
TRAIN_IDS = ROOT / "experiments/02-fine-tuning/results/labels/train_sample.json"


def train_sample() -> list[dict]:
    """Fixed experiment-02 training sample from the train split; ids written to TRAIN_IDS."""
    df = load_dataset(DATASET, "excerpts", split="train", revision=DATASET_REVISION).to_pandas()
    picks = [df[df["type"] == t].sample(n=n, random_state=0) for t, n in TRAIN_SAMPLE.items()]
    rows = [r for p in picks for r in p[["excerpt_id", "type", "text"]].to_dict("records")]
    TRAIN_IDS.parent.mkdir(parents=True, exist_ok=True)
    TRAIN_IDS.write_text(json.dumps({"dataset_revision": DATASET_REVISION, "split": "train", "design": TRAIN_SAMPLE,
                                     "seed": 0, "excerpt_ids": [r["excerpt_id"] for r in rows]}, indent=1) + "\n")
    return rows


def parse(content: str, fields: tuple[str, ...], valid: dict[str, set[str]]) -> tuple[dict | None, dict]:
    """First JSON object in content -> per-field code lists, keeping only valid codes; also returns dropped codes."""
    match = re.search(r"\{.*\}", content or "", re.S)
    if not match:
        return None, {}
    try:
        obj = json.loads(match.group(0))
    except json.JSONDecodeError:
        return None, {}
    labels, dropped = {}, {}
    for f in fields:
        codes = obj.get(f) or []
        codes = [c.upper() if f == "countries" else c for c in codes if isinstance(c, str)]
        labels[f] = sorted({c for c in codes if c in valid[f]})
        bad = [c for c in codes if c not in valid[f]]
        if bad:
            dropped[f] = bad
    return labels, dropped


async def label_one(client, model, row, prompts, valid, sem) -> dict:
    findings_sys, methods_sys = prompts
    if row["type"] == "methodology":
        system, user, fields = methods_sys, METHODS_USER.format(text=row["text"]), ("methods",)
    else:
        system, user, fields = findings_sys, FINDINGS_USER.format(type=row["type"], text=row["text"]), (
            "themes", "regions", "countries")
    async with sem:
        for attempt in range(6):
            t0 = time.perf_counter()
            try:
                resp = await client.chat.completions.create(
                    model=model,
                    messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                    temperature=0,
                    max_tokens=MAX_TOKENS,
                )
                break
            except Exception as e:  # rate limits and transient provider errors
                if attempt == 5:
                    return {"excerpt_id": row["excerpt_id"], "error": repr(e)[:500]}
                await asyncio.sleep(2 ** attempt * 5)
    latency_ms = round((time.perf_counter() - t0) * 1000)
    choice = resp.choices[0]
    labels, dropped = parse(choice.message.content, fields, valid)
    return {
        "excerpt_id": row["excerpt_id"],
        "type": row["type"],
        "labels": labels,
        "dropped": dropped,
        "finish_reason": choice.finish_reason,
        "content": choice.message.content,
        "usage": resp.usage.model_dump() if resp.usage else None,
        "latency_ms": latency_ms,
        "model": model,
    }


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=MODELS, required=True)
    ap.add_argument("--limit", type=int, help="label only the first N excerpts of eval_sample")
    ap.add_argument("--split", choices=("test", "validation", "train"), default="test",
                    help="test: the 600 eval_sample excerpts; validation: the threshold-fitting sample "
                         "(150 findings, 75 recommendations, 75 methodology, seed 0); train: the experiment-02 "
                         "training sample (5,000 findings, 2,500 recommendations, 2,500 methodology, seed 0)")
    ap.add_argument("--concurrency", type=int, help="default: per-model value in CONCURRENCY")
    ap.add_argument("--out", type=Path, help="default: experiments/01-many-option-classification/results/raw/labels_<model>.jsonl")
    args = ap.parse_args()

    load_dotenv(ROOT / ".env")
    model = MODELS[args.model]
    suffix = "" if args.split == "test" else f"_{args.split}"
    exp = "02-fine-tuning" if args.split == "train" else "01-many-option-classification"
    out = args.out or ROOT / f"experiments/{exp}/results/raw/labels_{args.model}{suffix}.jsonl"
    out.parent.mkdir(parents=True, exist_ok=True)

    findings_sys, methods_sys, valid = build_prompts()
    if args.split == "test":
        ds = load_dataset(DATASET, "excerpts", split="test", revision=DATASET_REVISION)
        rows = [r for r in ds if r["eval_sample"]]
    elif args.split == "validation":
        rows = validation_sample()
    else:
        rows = train_sample()
    rows.sort(key=lambda r: r["excerpt_id"])
    if args.limit:
        # spread the pilot over the three excerpt types
        by_type = {t: [r for r in rows if r["type"] == t] for t in ("findings", "recommendations", "methodology")}
        rows = [r for i in range(args.limit) for t in by_type if i < len(by_type[t]) for r in [by_type[t][i]]][: args.limit]

    done = set()
    if out.exists():
        # keep parsed records; errors, truncated and unparsed replies are retried
        kept = [l for l in out.read_text().splitlines() if l.strip() and json.loads(l).get("labels") is not None]
        out.write_text("".join(l + "\n" for l in kept))
        done = {json.loads(l)["excerpt_id"] for l in kept}
    todo = [r for r in rows if r["excerpt_id"] not in done]
    print(f"{model}: {len(todo)} to label, {len(done)} already done -> {out}")

    client = AsyncOpenAI(
        timeout=TIMEOUT_S,
        max_retries=0,
        base_url="https://router.huggingface.co/v1",
        api_key=os.environ["HF_TOKEN"],
        default_headers={"X-HF-Bill-To": "baobabtech"},
    )
    sem = asyncio.Semaphore(args.concurrency or CONCURRENCY[args.model])
    started = datetime.now(timezone.utc).isoformat()
    with out.open("a") as f:
        for coro in asyncio.as_completed([label_one(client, model, r, (findings_sys, methods_sys), valid, sem) for r in todo]):
            rec = await coro
            rec["date"] = started
            rec["dataset_revision"] = DATASET_REVISION
            f.write(json.dumps(rec) + "\n")
            f.flush()

    recs = [json.loads(l) for l in out.read_text().splitlines() if l.strip()]
    errors = sum("error" in r for r in recs)
    unparsed = sum(r.get("labels") is None and "error" not in r for r in recs)
    truncated = sum(r.get("finish_reason") == "length" for r in recs)
    tokens = sum((r.get("usage") or {}).get("total_tokens", 0) for r in recs)
    print(f"records {len(recs)}, errors {errors}, unparsed {unparsed}, truncated {truncated}, total tokens {tokens}")


if __name__ == "__main__":
    asyncio.run(main())

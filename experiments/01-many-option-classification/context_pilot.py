"""Context pilot: which context gives the best excerpt tags for the least input?

50 random test eval_sample excerpts (seed 0) x 5 context variants x GLM-5.3-Flash and DeepSeek-V4.1-Flash.
Reports, per variant: GLM-DeepSeek agreement, each LLM's agreement with the pipeline labels, labels per excerpt,
and input tokens. Raw responses go to results/raw/context_pilot/ (gitignored); the summary to
results/context_pilot/summary.json.

Usage: uv run context_pilot.py [--n 50]
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "common"))
from context import VARIANTS, load_source, user_prompt  # noqa: E402
from label_excerpts import MAX_TOKENS, MODELS, TIMEOUT_S, build_prompts, parse  # noqa: E402

LABELLERS = ("glm", "deepseek")
FIELDS = ("themes", "regions", "countries", "methods")


def f1(a: dict, b: dict, ids: list[str], field: str) -> float:
    tp = fp = fn = 0
    for e in ids:
        p, r = set(a[e].get(field, [])), set(b[e].get(field, []))
        tp, fp, fn = tp + len(p & r), fp + len(p - r), fn + len(r - p)
    return round(100 * 2 * tp / (2 * tp + fp + fn), 1) if tp + fp + fn else None


async def call(client, model, system, user, fields, valid, sem):
    async with sem:
        for attempt in range(6):
            try:
                t0 = time.perf_counter()
                r = await client.chat.completions.create(model=model, temperature=0, max_tokens=MAX_TOKENS,
                                                         messages=[{"role": "system", "content": system},
                                                                   {"role": "user", "content": user}])
                labels, dropped = parse(r.choices[0].message.content, fields, valid)
                if labels is None and attempt < 5:
                    continue
                return {"labels": labels, "dropped": dropped, "usage": r.usage.model_dump(),
                        "latency_ms": round((time.perf_counter() - t0) * 1000), "content": r.choices[0].message.content}
            except Exception as e:
                if attempt == 5:
                    return {"error": repr(e)[:300]}
                await asyncio.sleep(2 ** attempt * 3)


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=50)
    args = ap.parse_args()
    load_dotenv(HERE.parents[1] / ".env")

    ex, win, doc = load_source("test")
    from datasets import load_dataset
    sample = load_dataset("baobabtech/decision-models-evaluation-docs", "excerpts", split="test",
                          revision="bfaf706").to_pandas()
    ids = sample[sample.eval_sample].sample(n=args.n, random_state=0).excerpt_id.tolist()
    rows = ex.loc[ids]
    print("pilot types:", rows.type.value_counts().to_dict())

    findings_sys, methods_sys, valid = build_prompts()
    client = AsyncOpenAI(base_url="https://router.huggingface.co/v1", api_key=os.environ["HF_TOKEN"],
                         timeout=TIMEOUT_S, max_retries=0, default_headers={"X-HF-Bill-To": "baobabtech"})
    sem = asyncio.Semaphore(16)
    jobs = []
    for v in VARIANTS:
        for m in LABELLERS:
            for e, r in rows.iterrows():
                meth = r["type"] == "methodology"
                fields = ("methods",) if meth else ("themes", "regions", "countries")
                jobs.append(((v, m, e), call(client, MODELS[m], methods_sys if meth else findings_sys,
                                             user_prompt(r, win, doc, v), fields, valid, sem)))
    results = dict(zip([k for k, _ in jobs], await asyncio.gather(*(c for _, c in jobs))))

    raw = HERE / "results/raw/context_pilot"
    raw.mkdir(parents=True, exist_ok=True)
    (raw / "responses.jsonl").write_text("".join(
        json.dumps({"variant": v, "model": m, "excerpt_id": e, **res}) + "\n" for (v, m, e), res in results.items()))

    pipe = {e: {f: list(r[f]) if r[f] is not None else [] for f in FIELDS} for e, r in rows.iterrows()}
    summary = {"n": args.n, "excerpt_ids": ids, "variants": {}}
    print(f"\n{'variant':12} {'tok/exc':>7} | GLM-DS agree (them/reg/ctry/meth: mean) | vs pipeline GLM / DS | "
          f"labels/exc GLM: them reg ctry meth")
    for v in VARIANTS:
        lab = {m: {e: (results[(v, m, e)].get("labels") or {}) for e in ids} for m in LABELLERS}
        errs = sum("error" in results[(v, m, e)] for m in LABELLERS for e in ids)
        per = {f: [e for e in ids if (rows.loc[e, "type"] == "methodology") == (f == "methods")] for f in FIELDS}
        agree = {f: f1(lab["glm"], lab["deepseek"], per[f], f) for f in FIELDS}
        vs_pipe = {m: {f: f1(lab[m], pipe, per[f], f) for f in FIELDS} for m in LABELLERS}
        mean = lambda d: round(sum(x for x in d.values() if x is not None) / sum(x is not None for x in d.values()), 1)
        tok = sum(results[(v, m, e)].get("usage", {}).get("prompt_tokens", 0) for m in LABELLERS for e in ids) / (2 * len(ids))
        lpe = {f: round(sum(len(lab["glm"][e].get(f, [])) for e in per[f]) / len(per[f]), 2) for f in FIELDS}
        summary["variants"][v] = {"input_tokens_per_excerpt": round(tok), "glm_deepseek": agree,
                                  "glm_deepseek_mean": mean(agree), "vs_pipeline": vs_pipe,
                                  "vs_pipeline_mean": {m: mean(vs_pipe[m]) for m in LABELLERS},
                                  "labels_per_excerpt_glm": lpe, "errors": errs}
        print(f"{v:12} {tok:7.0f} | {' / '.join(str(agree[f]) for f in FIELDS)}: {mean(agree):5.1f} | "
              f"{mean(vs_pipe['glm']):5.1f} / {mean(vs_pipe['deepseek']):5.1f} | "
              f"{lpe['themes']} {lpe['regions']} {lpe['countries']} {lpe['methods']}  (errors {errs})")
    out = HERE / "results/context_pilot"
    out.mkdir(parents=True, exist_ok=True)
    (out / "summary.json").write_text(json.dumps(summary, indent=1) + "\n")


if __name__ == "__main__":
    asyncio.run(main())

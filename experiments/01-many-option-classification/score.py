"""Task B scoring: micro-F1 x 100 per field against each labelling LLM (GLM-5.3-Flash, DeepSeek-V4.1-Flash).

Predictions are {excerpt_id: {field: set(codes)}}. Fields: themes, regions, countries on findings and
recommendations; methods on methodology. The main score is the mean over the two LLMs; the LLM range is their
agreement with each other. No human gold exists, so scores measure agreement with LLMs, not correctness.
"""

from __future__ import annotations

import pandas as pd

FIELDS = ("themes", "regions", "countries", "methods")
LLMS = ("glm", "deepseek")


def items(sample: pd.DataFrame, field: str) -> list[str]:
    methodology = sample["type"] == "methodology"
    return list(sample.index[methodology if field == "methods" else ~methodology])


def micro_f1(pred: dict, ref: dict, ids: list[str], field: str) -> float:
    tp = fp = fn = 0
    for e in ids:
        p, r = set(pred.get(e, {}).get(field, ())), set(ref[e][field])
        tp, fp, fn = tp + len(p & r), fp + len(p - r), fn + len(r - p)
    return 100 * 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 100.0


def _codes(v) -> list:
    """Label lists arrive as lists, numpy arrays (pandas) or None."""
    return [] if v is None else list(v)


def references(sample: pd.DataFrame) -> dict[str, dict]:
    """Label sets keyed by name: each LLM, and the pipeline."""
    return {name: {e: {f: set(_codes(sample.at[e, f + suffix])) for f in FIELDS} for e in sample.index}
            for name, suffix in [*[(m, f"_{m}") for m in LLMS], ("pipeline", "_pipeline")]}


def score(pred: dict, sample: pd.DataFrame, fields: tuple[str, ...] = FIELDS) -> dict:
    refs = references(sample)
    out = {"n": {f: len(items(sample, f)) for f in fields}, "fields": {}}
    for f in fields:
        ids = items(sample, f)
        vs = {m: micro_f1(pred, refs[m], ids, f) for m in LLMS}
        out["fields"][f] = {
            "micro_f1": sum(vs.values()) / len(LLMS),
            **{f"micro_f1_vs_{m}": v for m, v in vs.items()},
            "micro_f1_vs_pipeline": micro_f1(pred, refs["pipeline"], ids, f),
            "labels_per_item": sum(len(pred.get(e, {}).get(f, ())) for e in ids) / len(ids),
        }
    if fields:
        out["mean_field_score"] = sum(out["fields"][f]["micro_f1"] for f in fields) / len(fields)
        out["mean_field_score_vs_pipeline"] = sum(out["fields"][f]["micro_f1_vs_pipeline"] for f in fields) / len(fields)
    return out


def llm_range(sample: pd.DataFrame) -> dict:
    """GLM vs DeepSeek agreement per field and mean: the level a model needs to count as LLM-level."""
    refs = references(sample)
    per = {f: micro_f1(refs["glm"], refs["deepseek"], items(sample, f), f) for f in FIELDS}
    return {"fields": per, "mean_field_score": sum(per.values()) / len(per)}

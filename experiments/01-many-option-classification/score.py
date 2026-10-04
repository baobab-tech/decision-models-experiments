"""Task B scoring: micro-F1 per field against the 3-LLM majority and against each LLM.

Predictions are {excerpt_id: {field: set(codes)}}. Fields: themes, regions, countries on findings and
recommendations; methods on methodology. No human gold exists, so scores measure agreement with LLMs.
"""

from __future__ import annotations

import pandas as pd

FIELDS = ("themes", "regions", "countries", "methods")
LLMS = ("glm", "deepseek", "qwen")


def items(sample: pd.DataFrame, field: str) -> list[str]:
    methodology = sample["type"] == "methodology"
    return list(sample.index[methodology if field == "methods" else ~methodology])


def micro_f1(pred: dict, ref: dict, ids: list[str], field: str) -> float:
    tp = fp = fn = 0
    for e in ids:
        p, r = set(pred.get(e, {}).get(field, ())), set(ref[e][field])
        tp, fp, fn = tp + len(p & r), fp + len(p - r), fn + len(r - p)
    return 100 * 2 * tp / (2 * tp + fp + fn) if tp + fp + fn else 100.0


def macro_f1(pred: dict, ref: dict, ids: list[str], field: str) -> float:
    codes = {c for e in ids for c in ref[e][field]}
    scores = []
    for c in codes:
        tp = sum(c in pred.get(e, {}).get(field, ()) and c in ref[e][field] for e in ids)
        fp = sum(c in pred.get(e, {}).get(field, ()) and c not in ref[e][field] for e in ids)
        fn = sum(c not in pred.get(e, {}).get(field, ()) and c in ref[e][field] for e in ids)
        scores.append(2 * tp / (2 * tp + fp + fn))
    return 100 * sum(scores) / len(scores) if scores else float("nan")


def references(sample: pd.DataFrame) -> dict[str, dict]:
    """Label sets keyed by name: majority, each LLM, and pipeline."""
    refs = {}
    for name, suffix in [("majority", "_majority"), *[(m, f"_{m}") for m in LLMS], ("pipeline", "")]:
        refs[name] = {e: {f: set(sample.at[e, f + suffix]) for f in FIELDS} for e in sample.index}
    return refs


def score(pred: dict, sample: pd.DataFrame, fields: tuple[str, ...] = FIELDS) -> dict:
    refs = references(sample)
    out = {"n": {f: len(items(sample, f)) for f in fields}, "fields": {}}
    for f in fields:
        ids = items(sample, f)
        out["fields"][f] = {
            "micro_f1": micro_f1(pred, refs["majority"], ids, f),
            "macro_f1": macro_f1(pred, refs["majority"], ids, f),
            "micro_f1_mean_vs_llms": sum(micro_f1(pred, refs[m], ids, f) for m in LLMS) / len(LLMS),
            "micro_f1_vs_pipeline": micro_f1(pred, refs["pipeline"], ids, f),
            "labels_per_item": sum(len(pred.get(e, {}).get(f, ())) for e in ids) / len(ids),
        }
    for key in ("micro_f1", "micro_f1_mean_vs_llms", "micro_f1_vs_pipeline"):
        out[f"mean_field_score{'' if key == 'micro_f1' else key.removeprefix('micro_f1')}"] = (
            sum(out["fields"][f][key] for f in fields) / len(fields))
    return out

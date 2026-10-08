"""Per-label and macro scoring against the two labelling LLMs (experiments 01 and 02).

Micro-F1 pools every (excerpt, label) decision, so frequent labels set the score. This reports each label on its own:

  n_ref        positives per labelling LLM, averaged (GLM-5.3-Flash, DeepSeek-V4.1-Flash)
  llm_f1       F1 of GLM against DeepSeek on this label: how far the references agree, the ceiling for a model
  model_f1     F1 of the model against each LLM, averaged
  model_recall share of each LLM's positives the model finds, averaged
  train_agreed training excerpts where both LLMs chose the label (when training rows are given)

macro_f1 per field is the mean model_f1 over labels with n_ref >= MIN_SUPPORT, with a 95% bootstrap interval
(1,000 resamples of excerpts); labels with fewer positives are listed in `unmeasured`. llm_macro_f1 is the same mean
for GLM against DeepSeek. Methods are scored on methodology excerpts; other fields on findings and
recommendations. Rows are dicts with `excerpt_id`, `type` and `<field>_<llm>` lists, as in the llm_labels config.

Usage from Python:
  from per_label import per_label_report
  report = per_label_report(preds, rows, fields=("themes", "regions", "countries", "methods"), train_rows=train)
"""

from __future__ import annotations

import warnings
from collections import Counter

import numpy as np

LABELLERS = ("glm", "deepseek")
MIN_SUPPORT = 5  # reference positives (mean of the two LLMs) needed to score a label on its own


def _eligible(rows, field):
    return [r for r in rows if (r["type"] == "methodology") == (field == "methods")]


def _ref(r, field, m) -> set:
    return set(r[f"{field}_{m}"] or [])


def _f1(p: np.ndarray, g: np.ndarray) -> np.ndarray:
    """Per-label F1 x 100 of boolean matrices (excerpts x labels); NaN where neither side has a positive."""
    tp, fp, fn = (p & g).sum(0), (p & ~g).sum(0), (~p & g).sum(0)
    den = 2 * tp + fp + fn
    return np.where(den > 0, 100 * 2 * tp / np.maximum(den, 1), np.nan)


def _model_f1(p, refs) -> np.ndarray:
    """Mean F1 against each LLM; a label one LLM never chose counts 0 against it if the model predicted it."""
    f = np.stack([_f1(p, g) for g in refs])
    return np.where(np.isnan(f).all(0), np.nan, np.nan_to_num(f).mean(0))


def per_label_report(preds: dict, rows: list[dict], fields: tuple[str, ...], train_rows: list[dict] | None = None,
                     n_boot: int = 1000, seed: int = 0) -> dict:
    """preds: excerpt_id -> {field: set of codes}. Returns {field: {macro_f1, macro_ci, llm_macro_f1, labels}}."""
    out = {}
    rng = np.random.default_rng(seed)
    for field in fields:
        rows_f = _eligible(rows, field)
        codes = sorted({c for r in rows_f for m in LABELLERS for c in _ref(r, field, m)}
                       | {c for r in rows_f for c in preds[r["excerpt_id"]].get(field, set())})
        col = {c: i for i, c in enumerate(codes)}

        def matrix(sets):
            x = np.zeros((len(rows_f), len(codes)), dtype=bool)
            for i, s in enumerate(sets):
                x[i, [col[c] for c in s]] = True
            return x

        p = matrix(preds[r["excerpt_id"]].get(field, set()) for r in rows_f)
        refs = [matrix(_ref(r, field, m) for r in rows_f) for m in LABELLERS]
        n_ref = np.mean([g.sum(0) for g in refs], axis=0)
        llm_f1, model_f1 = _f1(*refs), _model_f1(p, refs)
        with np.errstate(all="ignore"), warnings.catch_warnings():
            warnings.simplefilter("ignore", RuntimeWarning)
            recall = np.nanmean([np.where(g.sum(0) > 0, 100 * (p & g).sum(0) / np.maximum(g.sum(0), 1), np.nan)
                                 for g in refs], axis=0) if len(codes) else np.array([])
        train = Counter()
        if train_rows is not None:
            for r in _eligible(train_rows, field):
                train.update(set.intersection(*(_ref(r, field, m) for m in LABELLERS)))
        num = lambda v: None if np.isnan(v) else round(float(v), 1)
        labels = {c: {"n_ref": float(n_ref[i]), "n_pred": int(p[:, i].sum()), "llm_f1": num(llm_f1[i]),
                      "model_f1": num(model_f1[i]), "model_recall": num(recall[i]),
                      **({"train_agreed": train[c]} if train_rows is not None else {})}
                  for c, i in col.items()}
        scored = n_ref >= MIN_SUPPORT
        boots = []
        for _ in range(n_boot):
            idx = rng.integers(0, len(rows_f), len(rows_f))
            b_ref = [g[idx] for g in refs]
            keep = scored & (np.mean([g.sum(0) for g in b_ref], axis=0) > 0)
            if keep.any():
                boots.append(float(np.nanmean(_model_f1(p[idx], b_ref)[keep])))
        out[field] = {
            "n_excerpts": len(rows_f), "n_labels_scored": int(scored.sum()), "min_support": MIN_SUPPORT,
            "unmeasured": sorted(c for c, i in col.items() if not scored[i] and n_ref[i] > 0),
            "macro_f1": num(np.nanmean(model_f1[scored])) if scored.any() else None,
            "macro_ci": [round(x, 1) for x in np.percentile(boots, [2.5, 97.5])] if boots else None,
            "llm_macro_f1": num(np.nanmean(llm_f1[scored])) if scored.any() else None,
            "labels": labels,
        }
    return out

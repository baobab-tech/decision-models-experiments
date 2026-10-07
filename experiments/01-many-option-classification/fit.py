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
from score import FIELDS, score

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "common"))
from country_lookup import country_lookup  # noqa: E402

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


def predict(probs: dict, t: float, tax, sample=None, find=None) -> dict:
    """Labels at one threshold t. With find (country lookup), countries come from the lookup and
    regions = direct region Nouls ∪ regions of looked-up countries (experiment 02's hybrid)."""
    preds = {e: {f: {c for c, p in codes.items() if p >= t} for f, codes in fields.items()} for e, fields in probs.items()}
    if find is None:
        add_regions(preds, tax)
        return preds
    c2r = dict(tax[tax.field == "countries"][["code", "region"]].itertuples(index=False))
    for e, fs in preds.items():
        if "countries" in fs or "regions" in fs:
            fs["countries"] = find(sample.at[e, "input"])
            fs["regions"] = fs.get("regions", set()) | {c2r[c] for c in fs["countries"] if c2r.get(c)}
    return preds


def fit(probs, sample, tax, find=None) -> tuple[float, dict]:
    """One threshold for all fields: the best validation mean (ties go higher)."""
    curve = {t: score(predict(probs, t, tax, sample, find), sample)["mean_field_score"] for t in GRID}
    best = max(curve.values())
    return max(t for t, v in curve.items() if v == best), curve


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
    pv, pt, find = probabilities(val_path), probabilities(test_path), country_lookup()
    metrics, fitted = {}, {}
    for name, f in (("model_countries", None), ("country_lookup", find)):
        t, curve = fit(pv, val, tax, f)
        fitted[name] = {"threshold": t, "validation_curve": curve}
        metrics[name] = {"threshold": t, "fitted": score(predict(pt, t, tax, test, f), test),
                         "at_0.5": score(predict(pt, 0.5, tax, test, f), test)}
    out = HERE / "results" / f"{args.model}-context-thresholds"
    out.mkdir(parents=True, exist_ok=True)
    (out / "thresholds.json").write_text(json.dumps({
        "model": args.model, "date": datetime.now(timezone.utc).isoformat(), "fitted": fitted,
        "objective": "mean micro-F1 vs glm and deepseek on the validation sample; one threshold for all fields",
        "grid": [GRID[0], GRID[-1], 0.05], "ties": "higher threshold",
        "validation_run": val_path.parent.name, "test_run": test_path.parent.name}, indent=1) + "\n")
    (out / "metrics.json").write_text(json.dumps(metrics, indent=2) + "\n")
    for name, m in metrics.items():
        for k in ("at_0.5", "fitted"):
            r = m[k]
            print(f"{args.model} {name:15} {k:6} t={m['threshold'] if k == 'fitted' else 0.5:<4} mean {r['mean_field_score']:5.1f} | "
                  + " ".join(f"{f} {v['micro_f1']:5.1f}" for f, v in r["fields"].items()))


if __name__ == "__main__":
    main()

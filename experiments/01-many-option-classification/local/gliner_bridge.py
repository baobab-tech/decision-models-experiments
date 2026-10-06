"""Bridge from Jev wire-format requests to local GLiNER2.5-Decide, using its native multi-label classification.

Each request becomes one multi-label task over its labels (human label names, with definitions as label
descriptions when the run uses them). Every label's score is returned as the Noul answer, so run.py thresholds
and scores it like any model.

stdin: JSONL {id, state, questions}; stdout: JSONL {id, answers, latency_ms, model_id} or {id, error}.
Run with the GLiNER environment: third_party/gliner/.venv/bin/python local/gliner_bridge.py --device mps
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")

from gliner2 import AutoExtractor  # noqa: E402

MODEL = "fastino/GLiNER2.5-Decide"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="mps")
    ap.add_argument("--revision", default=None)
    args = ap.parse_args()

    kwargs = {"map_location": args.device}
    if args.revision:
        kwargs["revision"] = args.revision
    model = AutoExtractor.from_pretrained(MODEL, **kwargs)

    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        t0 = time.perf_counter()
        try:
            meta = req.get("labels") or {k: {"label": q["instructions"], "description": None}
                                         for k, q in req["questions"].items()}
            name_to_key = {m["label"]: k for k, m in meta.items()}
            labels = {m["label"]: (m.get("description") or m["label"]) for m in meta.values()}
            # cls_threshold 0 returns every label with its score; >= 0.5 equals GLiNER's default selection
            task = {"labels": labels, "multi_label": True, "cls_threshold": 0.0}
            out = model.classify_text(req["state"], {"task": task}, threshold=0.0, include_confidence=True)
            scores = {d["label"]: float(d["confidence"]) for d in out["task"]}
            answers = {key: {"type": "noul", "noul": scores.get(name, 0.0)} for name, key in name_to_key.items()}
            res = {"id": req["id"], "answers": answers, "latency_ms": round((time.perf_counter() - t0) * 1000),
                   "model_id": MODEL}
        except Exception as e:
            res = {"id": req["id"], "error": repr(e)[:500]}
        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

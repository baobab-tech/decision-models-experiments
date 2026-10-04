"""Bridge from Jev wire-format requests to local GLiNER2.5-Decide, using its native multi-label classification.

Each request's Nouls become one multi-label task: labels = question keys, label descriptions = Noul instructions.
The per-label probability is returned as the Noul answer, so run.py thresholds and scores it like any model.

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
            labels = {key: q["instructions"] for key, q in req["questions"].items()}
            task = {"labels": labels, "multi_label": True}
            out = model.classify_text(req["state"], {"task": task}, include_confidence=True)
            probs = out["task"]["probabilities"] if isinstance(out.get("task"), dict) else None
            if probs is None:
                raise ValueError(f"no probabilities in output: {str(out)[:300]}")
            answers = {key: {"type": "noul", "noul": float(probs.get(key, 0.0))} for key in labels}
            res = {"id": req["id"], "answers": answers, "latency_ms": round((time.perf_counter() - t0) * 1000),
                   "model_id": MODEL}
        except Exception as e:
            res = {"id": req["id"], "error": repr(e)[:500]}
        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

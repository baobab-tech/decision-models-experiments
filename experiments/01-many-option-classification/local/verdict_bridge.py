"""Bridge from Jev wire-format requests to local openJev Verdict (rlcd 0.1.0, heman10x/rlcd-modernbert-151m).

Each Noul becomes a Verdict Noul; the answer is P(true) from Verdict's three-way distribution
(true, false, insufficient evidence), so abstention mass counts against the label.

stdin: JSONL {id, state, questions}; stdout: JSONL {id, answers, latency_ms, model_id} or {id, error}.
Run with the Verdict environment: third_party/Verdict-open-jev/.venv/bin/python local/verdict_bridge.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from rlcd import DecisionEngine, Noul

ARTIFACTS = Path(__file__).resolve().parents[3] / "third_party/Verdict-open-jev/artifacts/v2"
BATCH = 24  # Verdict scores at most 24 options plus abstention per pass; Nouls are batched in groups


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--device", default="cpu")
    args = ap.parse_args()
    engine = DecisionEngine(model_name_or_path=str(ARTIFACTS), device=args.device)

    for line in sys.stdin:
        if not line.strip():
            continue
        req = json.loads(line)
        t0 = time.perf_counter()
        try:
            items = list(req["questions"].items())
            answers = {}
            for i in range(0, len(items), BATCH):
                queries = [Noul(id=key, proposition=q["instructions"],
                                semantics="conditional_on_sufficient_evidence_v2") for key, q in items[i:i + BATCH]]
                for r in engine.evaluate(context=req["state"], queries=queries).results:
                    answers[r.id] = {"type": "noul", "noul": float(r.probabilities.get("true", 0.0)),
                                     "p_insufficient": float(r.p_insufficient_evidence)}
            res = {"id": req["id"], "answers": answers, "latency_ms": round((time.perf_counter() - t0) * 1000),
                   "model_id": "heman10x/rlcd-modernbert-151m"}
        except Exception as e:
            res = {"id": req["id"], "error": repr(e)[:500]}
        sys.stdout.write(json.dumps(res) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()

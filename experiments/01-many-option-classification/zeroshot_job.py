# /// script
# requires-python = ">=3.12,<3.14"
# dependencies = ["huggingface_hub>=1.16,<2", "httpx>=0.28"]
# ///
"""Experiment 01: zero-shot runs of the open decision models on an HF Job GPU.

Reads the exported requests (run.py --export: one Noul per label, doc_summary context as state, at most 64
questions per request) from baobabtech/decision-models-zeroshot-runs, answers them with one model, and uploads
<model>/<split>/responses.jsonl and run.json to the same repo. Scoring happens locally with fit.py, as for the
API models. Each model brings its own package via `hf jobs uv run --with`:

  gliner-decide  --with "gliner2[local]==2.0.0"         native multi-label, all labels of a request scored together
  laya           --with "laya==0.3.27"                  Router (checkpoint chosen by language)
  verdict        --with "rlcd @ git+https://github.com/Heman10x-NGU/Verdict-open-jev@30f15564821626ca5c1ad5b2638c4eb7078787dd"
  kev-4b/0.8b    --with "kev[serve] @ git+https://github.com/jaredpalmer/kev@fe64b1274ea7f80d4095866df90666abb03e9cf6"

Usage: hf jobs uv run --flavor a10g-small --namespace baobabtech -s HF_TOKEN --with <package> zeroshot_job.py -- --model laya
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone

import httpx
from huggingface_hub import HfApi, hf_hub_download

REPO = "baobabtech/decision-models-zeroshot-runs"
VERDICT_REPO = "heman10x/rlcd-modernbert-151m"
KEV_RUNS = {"kev-4b": "jaredpalmer/kev-4b@139fdd94", "kev-0.8b": "jaredpalmer/kev-0.8b@9a45d25e"}


def noul(p: float) -> dict:
    return {"type": "noul", "noul": float(p)}


def run_gliner(reqs, device):
    os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    from gliner2 import AutoExtractor
    model = AutoExtractor.from_pretrained("fastino/GLiNER2.5-Decide", map_location=device)
    for req in reqs:
        meta = req["labels"]
        name_to_key = {m["label"]: k for k, m in meta.items()}
        labels = {m["label"]: (m.get("description") or m["label"]) for m in meta.values()}
        # cls_threshold 0 returns every label's score; >= 0.5 equals GLiNER's default selection
        out = model.classify_text(req["state"], {"task": {"labels": labels, "multi_label": True, "cls_threshold": 0.0}},
                                  threshold=0.0, include_confidence=True)
        scores = {d["label"]: float(d["confidence"]) for d in out["task"]}
        yield {key: noul(scores.get(name, 0.0)) for name, key in name_to_key.items()}


def run_laya(reqs, device):
    from laya import Router
    router = Router()
    for req in reqs:
        out = router.predict(req["state"], req["questions"])
        yield {k: noul(a.get("noul", 0.0)) for k, a in out["answers"].items()}


def run_verdict(reqs, device):
    from huggingface_hub import snapshot_download
    from rlcd import DecisionEngine, Noul
    engine = DecisionEngine(model_name_or_path=snapshot_download(VERDICT_REPO), device=device)
    for req in reqs:
        items, answers = list(req["questions"].items()), {}
        for i in range(0, len(items), 24):  # at most 24 options plus abstention per pass
            qs = [Noul(id=k, proposition=q["instructions"], semantics="conditional_on_sufficient_evidence_v2")
                  for k, q in items[i:i + 24]]
            for r in engine.evaluate(context=req["state"], queries=qs).results:
                answers[r.id] = noul(r.probabilities.get("true", 0.0))
        yield answers


KEV_URL = "http://127.0.0.1:8009"


def start_kev(model):
    """kev.serve once per job, shared by both splits."""
    proc = subprocess.Popen([sys.executable, "-m", "kev.serve", "--run", KEV_RUNS[model], "--port", "8009"])
    for _ in range(180):
        try:
            if httpx.get(f"{KEV_URL}/v1/models", timeout=5).status_code == 200:
                return proc
        except httpx.HTTPError:
            pass
        time.sleep(10)
    raise RuntimeError("kev.serve did not start")


def run_kev(reqs, device):
    with httpx.Client(timeout=600) as client:
        for req in reqs:
            r = client.post(f"{KEV_URL}/v1/systemone", json={"model": "kev-latest", "state": req["state"],
                                                             "questions": req["questions"]})
            r.raise_for_status()
            yield {k: noul(a.get("noul", 0.0)) for k, a in r.json()["answers"].items()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=("gliner-decide", "laya", "verdict", "kev-4b", "kev-0.8b"))
    ap.add_argument("--requests-revision", default="main")
    ap.add_argument("--limit", type=int, help="first N requests per split (smoke tests)")
    args = ap.parse_args()

    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    api = HfApi()
    kev = start_kev(args.model) if args.model in KEV_RUNS else None
    for split in ("test", "validation"):
        path = hf_hub_download(REPO, f"requests/{split}.jsonl", repo_type="dataset", revision=args.requests_revision)
        reqs = [json.loads(line) for line in open(path)][: args.limit]
        runner = {"gliner-decide": run_gliner, "laya": run_laya, "verdict": run_verdict}.get(args.model, run_kev)
        gen = runner(reqs, device)
        started, out, t0 = datetime.now(timezone.utc), [], time.perf_counter()
        for req in reqs:
            t = time.perf_counter()
            try:
                answers = next(gen)
                out.append({"id": req["id"], "answers": answers, "latency_ms": round((time.perf_counter() - t) * 1000)})
            except StopIteration:
                break
            except Exception as e:  # keep going; scoring skips errors
                out.append({"id": req["id"], "error": repr(e)[:300]})
        wall = time.perf_counter() - t0
        prefix = f"{args.model}/{split}"
        os.makedirs("out", exist_ok=True)
        with open("out/responses.jsonl", "w") as f:
            f.writelines(json.dumps(r) + "\n" for r in out)
        json.dump({"model": args.model, "split": split, "date": started.isoformat(), "requests": len(reqs),
                   "errors": sum("error" in r for r in out), "wall_s": round(wall, 1), "device": device,
                   "gpu": torch.cuda.get_device_name() if device == "cuda" else None,
                   "job_id": os.environ.get("JOB_ID"), "requests_revision": args.requests_revision},
                  open("out/run.json", "w"), indent=1)
        api.upload_folder(folder_path="out", path_in_repo=prefix, repo_id=REPO, repo_type="dataset",
                          commit_message=f"{prefix}: {len(out)} responses")
        print(f"{prefix}: {len(out)} responses, {sum('error' in r for r in out)} errors, {wall:.0f} s")
    if kev:
        kev.terminate()


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "torch==2.14.1",
#   "transformers==5.19.0",
#   "datasets==5.1.0",
#   "huggingface_hub>=1.16,<2",
#   "numpy",
#   "pycountry==24.6.1",
# ]
# ///
"""Experiment 02: per-excerpt probabilities on validation and test for fine-tuned taggers pushed before
train_encoder.py saved probs.npz. Loads each repo's model.pt, rebuilds the model from its run.json (base revision,
recipe, architecture) and writes results/probs/<repo name>.npz in the same format as probs.npz.

Usage: uv run predict_saved.py [repo ...]   (default: every baobabtech/evaldocs-excerpt-tagger-*-lookup* repo)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import torch
from datasets import load_dataset
from huggingface_hub import HfApi, hf_hub_download
from transformers import AutoTokenizer

from train_encoder import DATASET, Tagger, predict

OUT = Path(__file__).resolve().parent / "results/probs"


def main() -> None:
    api = HfApi()
    repos = sys.argv[1:] or [m.id for m in api.list_models(author="baobabtech", search="evaldocs-excerpt-tagger")
                             if "lookup" in m.id]
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    OUT.mkdir(parents=True, exist_ok=True)
    data = {}
    for repo in repos:
        dest = OUT / f"{repo.split('/')[-1]}.npz"
        files = {f for f in api.list_repo_files(repo)}
        if dest.exists() or "probs.npz" in files:
            print(f"skip {repo}: probabilities exist")
            continue
        run = json.load(open(hf_hub_download(repo, "run.json")))
        labels = json.load(open(hf_hub_download(repo, "labels.json")))["labels"]
        rev = run["dataset_revision"]
        if rev not in data:
            d = load_dataset(DATASET, "llm_labels", revision=rev)
            data[rev] = (list(d["validation"]), list(d["test"]))
        val, test = data[rev]
        rec = {k: (tuple(v) if isinstance(v, list) else v) for k, v in run["recipe"].items()}
        tok = AutoTokenizer.from_pretrained(repo, trust_remote_code=rec["trust_remote_code"])
        model = Tagger(len(labels), run["base"], run["base_revision"], rec["trust_remote_code"], run["arch"])
        model.load_state_dict(torch.load(hf_hub_download(repo, "model.pt"), map_location="cpu"))
        model.to(device)
        go = lambda rows: predict(model, tok, rows, device, run["max_len"], 16, run["arch"], rec["context_first"], rec)
        np.savez_compressed(dest, val=go(val), test=go(test),
                            val_ids=np.array([r["excerpt_id"] for r in val]),
                            test_ids=np.array([r["excerpt_id"] for r in test]))
        print(f"wrote {dest.name}")
        del model
        torch.mps.empty_cache() if device == "mps" else None


if __name__ == "__main__":
    main()

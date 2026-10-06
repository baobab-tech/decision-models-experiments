"""Select extra training excerpts so rare labels get enough examples (experiment 02).

The first training sample (10,000 random excerpts) has a median of 19 agreed positives per method and 1-5 for
several themes and regions. This adds real excerpts from the unlabelled rest of the train split:
  - every remaining methodology excerpt (rare methods are rare everywhere);
  - for each theme and region, up to PER_LABEL findings/recommendations excerpts that the pipeline tagged with it.
The pipeline labels only choose which excerpts to label; GLM-5.3-Flash and DeepSeek-V4.1-Flash label them.
Writes results/labels/train_extra_sample.json.

Usage: uv run select_balanced.py
"""

from __future__ import annotations

import json
from pathlib import Path

from datasets import load_dataset

HERE = Path(__file__).resolve().parent
DATASET = "baobabtech/decision-models-evaluation-docs"
REVISION = "5b5de6f"
PER_LABEL = 300
SEED = 0


def main() -> None:
    ex = load_dataset(DATASET, "excerpts", split="train", revision=REVISION).to_pandas()
    used = set(json.loads((HERE / "results/labels/train_sample.json").read_text())["excerpt_ids"])
    pool = ex[~ex.excerpt_id.isin(used)].sample(frac=1, random_state=SEED)  # shuffled once, so picks are random

    chosen = set(pool[pool.type == "methodology"].excerpt_id)
    findings = pool[pool.type != "methodology"]
    per_label = {}
    for field in ("themes", "regions"):
        for code in sorted({c for v in findings[field] if v is not None for c in v}):
            ids = findings[findings[field].map(lambda v: v is not None and code in v)].excerpt_id[:PER_LABEL]
            per_label[f"{field}:{code}"] = len(ids)
            chosen.update(ids)
    chosen = sorted(chosen)
    types = ex.set_index("excerpt_id").loc[chosen].type.value_counts().to_dict()
    print(f"selected {len(chosen)} excerpts: {types}")
    (HERE / "results/labels/train_extra_sample.json").write_text(json.dumps({
        "dataset_revision": REVISION, "split": "train", "seed": SEED, "per_label": PER_LABEL,
        "rule": "all unlabelled methodology excerpts + up to per_label pipeline-tagged excerpts per theme and region",
        "candidates_per_label": per_label, "type_counts": types, "excerpt_ids": chosen}, indent=1) + "\n")


if __name__ == "__main__":
    main()

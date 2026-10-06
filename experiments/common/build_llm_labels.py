# /// script
# requires-python = ">=3.11"
# dependencies = ["datasets>=3", "pandas", "huggingface_hub"]
# ///
"""Push the `llm_labels` config of baobabtech/decision-models-evaluation-docs: excerpt, its context, and LLM labels.

`input` is the text every labeller saw: the excerpt, then the report's title, first 100 words, and executive
summary and abstract (each cut to 1,500 characters) -- the `doc_summary` context chosen by experiment 01's pilot.

Splits:
  test        the 600 eval_sample excerpts
  validation  the 300-excerpt threshold-fitting sample
  train       the 10,000-excerpt experiment-02 sample
Labels from GLM-5.3-Flash and DeepSeek-V4.1-Flash in every split.
Every row also has the pipeline labels as <field>_pipeline. Label files come from this repo:
experiments/01-many-option-classification/results/labels/ and experiments/02-fine-tuning/results/labels/.

Usage: uv run experiments/common/build_llm_labels.py [--push]
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import sys

import pandas as pd
from datasets import Dataset, DatasetDict, Features, List, Value, load_dataset

sys.path.insert(0, str(Path(__file__).resolve().parent))
from context import load_source, user_prompt  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DATASET = "baobabtech/decision-models-evaluation-docs"
SOURCE_REVISION = "bfaf706"
CONTEXT = "doc_summary"  # chosen by the experiment-01 context pilot
FIELDS = ("themes", "regions", "countries", "methods")
LLMS = ("glm", "deepseek")
SAMPLES = {  # split -> (dataset split, label dir, file suffix, ids file or None for eval_sample)
    "test": ("test", "01-many-option-classification", "", None),
    "validation": ("validation", "01-many-option-classification", "_validation", "validation_sample.json"),
    "train": ("train", "02-fine-tuning", "_train", "train_sample.json"),
}


def labels(dir_: Path, model: str, suffix: str) -> dict | None:
    path = dir_ / f"excerpts_{model}_{CONTEXT}{suffix}.jsonl"
    return {r["excerpt_id"]: r["labels"] for r in map(json.loads, path.open())} if path.exists() else None


def build(split: str, partial: bool = False) -> Dataset:
    source_split, exp, suffix, ids_file = SAMPLES[split]
    dir_ = ROOT / "experiments" / exp / "results/labels"
    df = load_dataset(DATASET, "excerpts", split=source_split, revision=SOURCE_REVISION).to_pandas()
    if ids_file is None:
        df = df[df.eval_sample]
    else:
        ids = set(json.loads((dir_ / ids_file).read_text())["excerpt_ids"])
        df = df[df.excerpt_id.isin(ids)]
    per = {m: labels(dir_, m, suffix) for m in LLMS}
    have = [m for m in LLMS if per[m] is not None]
    assert len(have) == len(LLMS), f"{split}: missing labels from {set(LLMS) - set(have)}"
    for m in have:
        missing = set(df.excerpt_id) - set(per[m])
        if partial:  # smoke tests only: keep excerpts every labeller has done
            df = df[~df.excerpt_id.isin(missing)]
        else:
            assert not missing, f"{split}: {m} has no labels for {len(missing)} excerpts"
    src_ex, src_win, src_doc = load_source(source_split)
    rows = []
    for r in df.sort_values("excerpt_id").itertuples():
        row = {"excerpt_id": r.excerpt_id, "document_id": r.document_id, "type": r.type, "text": r.text,
               "input": user_prompt(src_ex.loc[r.excerpt_id], src_win, src_doc, CONTEXT)}
        for f in FIELDS:
            row[f"{f}_pipeline"] = sorted(getattr(r, f)) if getattr(r, f) is not None else []
            for m in LLMS:
                row[f"{f}_{m}"] = sorted(per[m][r.excerpt_id].get(f, []))
        rows.append(row)
    features = Features({"excerpt_id": Value("string"), "document_id": Value("string"), "type": Value("string"),
                         "text": Value("string"), "input": Value("string"),
                         **{f"{f}_{s}": List(Value("string")) for f in FIELDS
                            for s in ("pipeline", *LLMS)}})
    print(f"{split}: {len(rows)} rows; labellers {have}")
    return Dataset.from_pandas(pd.DataFrame(rows), features=features, preserve_index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--save-dir", type=Path, help="save locally (load with --local-data in train_encoder.py)")
    ap.add_argument("--partial", action="store_true", help="smoke tests: drop excerpts not yet labelled")
    args = ap.parse_args()
    dd = DatasetDict({s: build(s, args.partial) for s in SAMPLES})
    if args.save_dir:
        dd.save_to_disk(str(args.save_dir))
    if args.push:
        dd.push_to_hub(DATASET, config_name="llm_labels", data_dir="llm_labels", private=False)


if __name__ == "__main__":
    main()

# /// script
# requires-python = ">=3.11"
# dependencies = ["datasets>=3", "pandas", "pyarrow", "pycountry", "huggingface_hub"]
# ///
"""Build baobabtech/decision-models-evaluation-docs, the public dataset used by experiments 01 and 02.

Source: baobabtech/evalexplorer-data (private), pinned by REVISION.
Taxonomy: label names and definitions from a local checkout of the labelling pipeline (github.com/baobab-tech/eval-explorer).

Configs pushed to --target:
  documents  first pages (as the classify_codes config truncated them) + silver labels (GLM-5.3-Flash)
             + pipeline labels (`*_pipeline`), train/validation/test
  excerpts   findings, recommendations and methodology excerpts + tags, train/validation/test;
             `eval_sample` marks the fixed 600-excerpt test sample (300 findings, 150 recommendations, 150 methodology, seed 0)
  taxonomy   one row per (field, code): label, definition (document prompt), definition_excerpts (excerpt
             prompt: themes and methods), region (countries only), and whether the code occurs in the
             documents / excerpts gold labels (the label sets the experiments ask over)

Usage:
  uv run experiments/common/build_evaluation_docs_dataset.py --eval-explorer ~/DEV/eval-explorer           # build only
  uv run experiments/common/build_evaluation_docs_dataset.py --eval-explorer ~/DEV/eval-explorer --push    # build and push (public)
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd
import pycountry
from datasets import Dataset, DatasetDict, load_dataset

SOURCE = "baobabtech/evalexplorer-data"
REVISION = "5315eab20c1d61101401a9b4ac80a2a7e3391623"  # adds labels_glm_5_3_flash; checked 2026-10-02
SILVER = "labels_glm_5_3_flash"  # GLM-5.3-Flash relabelling, used as silver labels
TARGET = "baobabtech/decision-models-evaluation-docs"
SPLITS = ("train", "validation", "test")
SAMPLE = {"findings": 300, "recommendations": 150, "methodology": 150}
SEED = 0


def ts_record(source: str, name: str) -> dict[str, str]:
    """Parse `export const NAME: Record<...> = { key: "value", ... };` from a TypeScript file."""
    body = re.search(rf"export const {name}[^=]*=\s*\{{(.*?)\n\}};", source, re.S).group(1)
    return dict(re.findall(r'^\s*"?(\w+)"?:\s*"([^"]*)"', body, re.M))


def prompt_definitions(prompt: str) -> dict[str, dict[str, str]]:
    """Parse "- `code` - description" bullets under each "### field" heading of the pipeline prompt."""
    out: dict[str, dict[str, str]] = {}
    field = None
    for line in prompt.splitlines():
        if heading := re.match(r"### (\w+)", line):
            field = heading.group(1)
        elif field and (bullet := re.match(r"- `(\w+)` - (.+)", line)):
            out.setdefault(field, {})[bullet.group(1)] = bullet.group(2).strip()
    return out


def excerpt_definitions(ee: Path) -> dict[str, dict[str, str]]:
    """Theme and method definitions from the excerpt extract-and-classify prompts (ingestion-pipeline/lib/extract)."""
    ex = ee / "ingestion-pipeline/lib/extract"
    prompts = (ex / "prompts.ts").read_text()
    body = re.search(r"THEME_LABEL_TO_CODE[^=]*=\s*\{(.*?)\n\};", prompts, re.S).group(1)
    label_to_code = dict(re.findall(r"'([^']+)':\s*'(\w+)'", body))
    themes = {label_to_code[t["theme"]]: t["definition"]
              for t in json.loads((ex / "definitions_themes.json").read_text())["themes"]}
    section = prompts.split("## Method Descriptions", 1)[1].split("##", 1)[0]
    methods = dict(re.findall(r"- \\`(\w+)\\` - (.+)", section))
    return {"themes": themes, "methods": methods}


def taxonomy(ee: Path) -> pd.DataFrame:
    tax = (ee / "lib/taxonomy.ts").read_text()
    geo = (ee / "lib/geography.ts").read_text()
    defs = prompt_definitions((ee / "ingestion-pipeline/lib/prompts/document-classification.md").read_text())
    exc_defs = excerpt_definitions(ee)
    labels = {
        "evaluation_approach": ts_record(tax, "EVALUATION_APPROACH_LABELS"),
        "evaluation_type": ts_record(tax, "EVALUATION_TYPE_LABELS"),
        "temporality": ts_record(tax, "TEMPORALITY_LABELS"),
        "themes": ts_record(tax, "THEME_LABELS"),
        "methods": ts_record(tax, "METHOD_LABELS"),
        "regions": ts_record(geo, "REGION_LABELS"),
    }
    rows = [
        {"field": field, "code": code, "label": label, "definition": defs.get(field, {}).get(code),
         "definition_excerpts": exc_defs.get(field, {}).get(code), "region": None}
        for field, codes in labels.items()
        for code, label in codes.items()
    ]
    for code, region in ts_record(geo, "COUNTRY_TO_REGION").items():
        country = pycountry.countries.get(alpha_2=code)
        rows.append({"field": "countries", "code": code, "label": country.name if country else code,
                     "definition": None, "definition_excerpts": None, "region": region})
    return pd.DataFrame(rows)


def _scalar(v):
    """pandas reads null strings as NaN; return None for those."""
    return None if v is None or (isinstance(v, float) and v != v) else v


def _codes(v) -> list[str]:
    return [] if v is None or (isinstance(v, float) and v != v) else list(v)


def documents() -> DatasetDict:
    out = {}
    for split in SPLITS:
        codes = load_dataset(SOURCE, "classify_codes", split=split, revision=REVISION).to_pandas()
        docs = load_dataset(SOURCE, "documents", split=split, revision=REVISION).to_pandas()
        docs = docs.set_index("document_id")
        silver = load_dataset(SOURCE, SILVER, split=split, revision=REVISION).to_pandas().set_index("document_id")
        missing = set(codes.document_id) - set(silver.index)
        assert not missing, f"{len(missing)} {split} documents have no silver label"
        rows = []
        for r in codes.itertuples():
            user = r.prompt[1]["content"]
            text = user.removeprefix("<document>\n").removesuffix("\n</document>")
            pipe = json.loads(r.answer)
            src = docs.loc[r.document_id]
            sil = silver.loc[r.document_id]
            rows.append({
                "document_id": r.document_id,
                "title": src["title"],
                "text": text,
                "n_chars": int(r.n_chars),
                "truncated": bool(r.truncated),
                **{k: _scalar(sil[k]) for k in ("evaluation_approach", "evaluation_type", "temporality")},
                "themes": _codes(sil["themes"]),
                "countries": _codes(sil["countries"]),
                **{f"{k}_pipeline": pipe[k] for k in ("evaluation_approach", "evaluation_type", "temporality")},
                "themes_pipeline": list(pipe["themes"]),
                "countries_pipeline": list(pipe["countries"]),
                "regions_pipeline": list(src["regions"]) if src["regions"] is not None else [],
                "label_source_pipeline": src["label_source"],
            })
        out[split] = Dataset.from_list(rows)
    return DatasetDict(out)


def excerpts() -> DatasetDict:
    out = {}
    cols = ["excerpt_id", "document_id", "type", "section_category", "page", "text",
            "themes", "regions", "countries", "methods"]
    for split in SPLITS:
        df = load_dataset(SOURCE, "excerpts", split=split, revision=REVISION).to_pandas()[cols]
        for c in ("themes", "regions", "countries", "methods"):
            df[c] = df[c].map(lambda v: list(v) if v is not None else [])
        df["eval_sample"] = False
        if split == "test":
            for kind, n in SAMPLE.items():
                idx = df[df["type"] == kind].sample(n=n, random_state=SEED).index
                df.loc[idx, "eval_sample"] = True
        out[split] = Dataset.from_pandas(df.reset_index(drop=True), preserve_index=False)
    return DatasetDict(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval-explorer", type=Path, required=True, help="local eval-explorer checkout (taxonomy source)")
    ap.add_argument("--push", action="store_true")
    args = ap.parse_args()

    docs, exc = documents(), excerpts()
    tax_df = taxonomy(args.eval_explorer.expanduser())

    def seen(dd: DatasetDict, fields: tuple[str, ...]) -> set[tuple[str, str]]:
        out = set()
        for split in dd.values():
            for f in fields:
                for v in split[f]:
                    for code in ([v] if isinstance(v, str) else (v or [])):
                        out.add((f, code))
        return out

    in_docs = seen(docs, ("evaluation_approach", "evaluation_type", "temporality", "themes", "countries",
                          "evaluation_approach_pipeline", "evaluation_type_pipeline", "temporality_pipeline",
                          "themes_pipeline", "countries_pipeline", "regions_pipeline"))
    in_docs = {(f.removesuffix("_pipeline"), c) for f, c in in_docs}
    in_exc = seen(exc, ("themes", "regions", "countries", "methods"))
    tax_df["in_documents"] = [(f, c) in in_docs for f, c in zip(tax_df.field, tax_df.code)]
    tax_df["in_excerpts"] = [(f, c) in in_exc for f, c in zip(tax_df.field, tax_df.code)]
    unknown = (in_docs | in_exc) - set(zip(tax_df.field, tax_df.code))
    print("gold codes missing from taxonomy:", sorted(unknown))
    tax = Dataset.from_pandas(tax_df, preserve_index=False)
    print("codes in documents:", tax_df[tax_df.in_documents].groupby("field").size().to_dict())
    print("codes in excerpts:", tax_df[tax_df.in_excerpts].groupby("field").size().to_dict())
    print("taxonomy:", tax.to_pandas().groupby("field").size().to_dict())
    print("documents:", {k: len(v) for k, v in docs.items()})
    print("excerpts:", {k: len(v) for k, v in exc.items()}, "eval_sample:", sum(exc["test"]["eval_sample"]))

    if args.push:
        docs.push_to_hub(TARGET, config_name="documents", data_dir="documents", private=False)
        exc.push_to_hub(TARGET, config_name="excerpts", data_dir="excerpts", private=False)
        DatasetDict({"train": tax}).push_to_hub(TARGET, config_name="taxonomy", data_dir="taxonomy", private=False)


if __name__ == "__main__":
    main()

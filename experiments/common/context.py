"""Production-style context for excerpt tagging, rebuilt from baobabtech/evalexplorer-data.

Production (eval-explorer ingestion-pipeline, processor-extract.ts + extraction.ts) tags excerpts in one call per
section chunk ("window"), with up to 3 context sections cut to 1,500 characters: "Document Start" (the first
100 words) and the first two other sections in document order. The source data stores the executive summary and
abstract but not section order, so those two stand in for the other context sections.

Variants (experiment 01 context pilot):
  excerpt      the excerpt alone (control)
  doc          + title + Document Start
  doc_summary  + executive summary and abstract (<= 1,500 characters each)
  production   excerpt marked inside its window + Document Start + executive summary and abstract
  summary_doc  doc + summary_doc (the pipeline's post-extraction document summary)
"""

from __future__ import annotations

import pandas as pd
from datasets import load_dataset

SOURCE = "baobabtech/evalexplorer-data"  # private; read only
SOURCE_REVISION = "5315eab20c1d61101401a9b4ac80a2a7e3391623"
CONTEXT_MAX_CHARS = 1500  # production: CONTEXT_MAX_CHARS in processor-shared.ts
VARIANTS = ("excerpt", "doc", "doc_summary", "production", "summary_doc")


def load_source(split: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """(excerpts, windows, documents) for a split, indexed by id."""
    ex = load_dataset(SOURCE, "excerpts", split=split, revision=SOURCE_REVISION).to_pandas().set_index("excerpt_id")
    win = load_dataset(SOURCE, "windows", split=split, revision=SOURCE_REVISION).to_pandas().set_index("window_id")
    doc = load_dataset(SOURCE, "documents", split=split, revision=SOURCE_REVISION).to_pandas().set_index("document_id")
    return ex, win, doc


def _s(x) -> str:
    """pandas gives NaN for missing strings."""
    return x.strip() if isinstance(x, str) else ""


def _cut(text, n=CONTEXT_MAX_CHARS) -> str:
    text = _s(text)
    return text if len(text) <= n else text[:n] + "\n\n[... truncated for context ...]"


def _first_words(text, n=100) -> str:
    return " ".join(_s(text).split()[:n])


def user_prompt(excerpt: pd.Series, windows: pd.DataFrame, docs: pd.DataFrame, variant: str) -> str:
    """User message for one excerpt: the excerpt to classify, then the context blocks of the variant."""
    parts = []
    if excerpt["type"] != "methodology":
        parts.append(f"Excerpt type: {excerpt['type']}")
    parts.append(f"## EXCERPT TO CLASSIFY\n\n{excerpt['text']}")
    if variant == "excerpt":
        return "\n\n".join(parts)
    doc = docs.loc[excerpt["document_id"]]
    if variant == "production":
        w = windows.loc[excerpt["window_id"]]
        a, b = int(excerpt["char_start"]), int(excerpt["char_end"])
        marked = w["text"][:a] + "<<<" + w["text"][a:b] + ">>>" + w["text"][b:]
        parts.append(f"## MAIN SECTION ({w['section_category']}; the excerpt is between <<< and >>>)\n\n{marked}")
    ctx = []
    if variant in ("doc", "doc_summary", "summary_doc"):
        ctx.append(f"### Title\n{_s(doc['title'])}")
    ctx.append(f"### Document Start\n{_first_words(doc['first_pages'])}")
    if variant in ("doc_summary", "production"):
        for name, col in (("Executive Summary", "executive_summary_section"), ("Abstract", "abstract_section")):
            if _s(doc[col]):
                ctx.append(f"### {name}\n{_cut(doc[col])}")
    if variant == "summary_doc" and _s(doc["summary_doc"]):
        ctx.append(f"### Document Summary\n{_s(doc['summary_doc'])}")
    parts.append("## CONTEXT SECTIONS (for understanding only)\n\n" + "\n\n".join(ctx))
    return "\n\n".join(parts)

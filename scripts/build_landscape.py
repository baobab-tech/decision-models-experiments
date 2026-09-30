"""Build docs/landscape.md from Han Xiao's all-about-jev dataset.

Usage:
    curl -sL https://hanxiao.io/all-about-jev/all-methods.jsonl -o data/all-about-jev/all-methods.jsonl
    python3 scripts/build_landscape.py
"""

import collections
import json
import os
import re
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/all-about-jev/all-methods.jsonl"
OUT = ROOT / "docs/landscape.md"

# Model docs we maintain by hand; matched against the entry URL (lower-cased).
OUR_DOCS = {
    "huggingface.co/convaiinnovations/laya": "models/open-reproductions.md",
    "jaredpalmer/kev": "models/kev.md",
    "contrastive-lm/": "models/clm-8b.md",
    "anyjev": "models/anyjev.md",
    "fastino/gliner2.5-decide": "models/gliner-decide.md",
    "tev1": "models/tev1.md",
    "kyr0/bonsai-llama-jev": "models/bonsai-llama-jev.md",
}


APPROACHES = {
    "fine-tune": "Weights of an existing LM updated (full or LoRA) on decision data.",
    "head": "New output head (classifier / pointer) on a pretrained backbone; LM head removed or bypassed.",
    "logits": "Training-free: read next-token logits over answer labels from an unmodified LM.",
    "from-scratch": "Decision model trained from random init.",
    "distill": "Student trained on a teacher's (often Jev's) probability outputs.",
    "modified": "Architecture changed beyond adding a head.",
    "rl": "Trained with reinforcement learning against a scoring rule.",
    "router": "Routes each decision to one of several models.",
    "constrained": "Constrained decoding over the answer set.",
    "diffusion": "Diffusion LM backbone.",
    "undisclosed": "Method not published.",
    "sdk": "Client library, not a model.",
    "": "Not recorded in the dataset.",
}


BACKBONES = [  # (label, substrings in base_model/arch, lower-cased); first match wins
    ("mmBERT", ["mmbert", "laya multilingual", "laya-multilingual"]),
    ("DeBERTa", ["deberta", "gliner"]),
    ("ModernBERT", ["modernbert", "laya"]),
    ("Other BERT", ["bert", "roberta", "electra", "minilm", "ettin"]),
    ("Qwen", ["qwen"]),
    ("Gemma", ["gemma"]),
    ("Llama", ["llama"]),
    ("Bonsai", ["bonsai"]),
    ("LFM", ["lfm", "liquid"]),
    ("Mistral", ["mistral", "ministral"]),
    ("Phi", ["phi-"]),
    ("SmolLM", ["smollm"]),
]


def backbone(r):
    # base_model first; arch prose often mentions other models in comparisons.
    for field in ("base_model", "arch"):
        text = str(r.get(field) or "").lower()
        for label, needles in BACKBONES:
            if any(n in text for n in needles):
                return label
    return "Other / undisclosed"


def size_tier(r):
    m = re.search(r"(\d+(?:\.\d+)?)\s*([MB])", str(r.get("params") or ""), re.I)
    if not m:
        return "unknown"
    n = float(m.group(1)) * (1e-3 if m.group(2).upper() == "M" else 1)
    if n < 0.1:
        return "<100M"
    if n < 0.5:
        return "100–500M"
    if n <= 4.5:
        return "0.5–4B"
    if n <= 14:
        return "7–14B"
    return "20B+"


TIERS = ["<100M", "100–500M", "0.5–4B", "7–14B", "20B+", "unknown"]


def cell(s, n=None):
    s = re.sub(r"\s+", " ", str(s or "")).replace("|", "\\|").strip()
    return s[: n - 1] + "…" if n and len(s) > n else s


def our_doc(r):
    key = r["url"].lower()
    for needle, path in OUR_DOCS.items():
        if needle in key:
            return path
    return ""


def counts_table(counter, header, total):
    lines = [f"| {header} | Entries | Share |", "|---|---:|---:|"]
    for k, v in counter.most_common():
        lines.append(f"| {cell(k) or '(blank)'} | {v} | {v / total:.0%} |")
    return "\n".join(lines)


def main():
    rows = [json.loads(l) for l in SRC.open() if l.strip()]
    models = [r for r in rows if r["category"] == "model"]
    snapshot = time.strftime("%Y-%m-%d", time.localtime(os.path.getmtime(SRC)))

    by_cat = collections.Counter(r["category"] for r in rows)
    approach = collections.Counter(r.get("approach") or "" for r in models)
    family = collections.Counter(r.get("family") or "(blank)" for r in models)
    license_ = collections.Counter(r.get("license") or "(blank)" for r in models)
    qtypes = collections.Counter(r.get("qtypes") or "(blank)" for r in models)
    hw = collections.Counter(r.get("hw") or "(blank)" for r in models)

    # Shortlist: open licence, local, full Choice/Score/Noul coverage or /v1/systemone wire,
    # and a reported metric.
    def shortlisted(r):
        lic = (r.get("license") or "").lower()
        full = "choice" in (r.get("qtypes") or "") and "noul" in (r.get("qtypes") or "")
        wire = "systemone" in (r.get("wire") or "")
        return (
            (lic.startswith("apache") or lic == "mit")
            and r.get("deployment") in ("local", "")
            and (full or wire)
            and r.get("metric")
        )

    short = sorted(filter(shortlisted, models), key=lambda r: r["date"])
    mac = [r for r in models if "MLX" in (r.get("hw") or "") or "llama.cpp" in (r.get("hw") or "")]

    out = []
    w = out.append
    w("# Landscape: the all-about-jev dataset\n")
    w(
        f"Data: [All about Jev](https://hanxiao.io/all-about-jev/) by Han Xiao "
        f"([announcement](https://www.linkedin.com/feed/update/urn:li:ugcPost:7508930228493348865/)). All credit for collecting and curating it goes to him.\n\n"
        f"Generated by `scripts/build_landscape.py` from the dataset's `all-methods.jsonl` (local copy dated {snapshot}; the site's last sweep was 2026-09-27 UTC). "
        f"The dataset records findings as each source reported them; they are not independently verified. "
        f"Re-run the script to refresh. Do not edit by hand.\n"
    )
    w("## Counts\n")
    w(f"{len(rows)} entries; {len(models)} are models.\n")
    w(counts_table(by_cat, "Category", len(rows)) + "\n")
    w("## Models by approach\n")
    lines = ["| Approach | Models | Meaning |", "|---|---:|---|"]
    for k, v in approach.most_common():
        lines.append(f"| {k or '(blank)'} | {v} | {APPROACHES.get(k, '')} |")
    w("\n".join(lines) + "\n")
    w("## Backbone × size\n")
    w("Backbone is inferred by keyword from `base_model` (falling back to `arch`); size from `params` (first number). Mixed-size families count once at their first size.\n")
    grid = collections.Counter((backbone(r), size_tier(r)) for r in models)
    fams = sorted({b for b, _ in grid}, key=lambda b: -sum(v for (bb, _), v in grid.items() if bb == b))
    w("| Backbone | " + " | ".join(TIERS) + " | Total |")
    w("|---|" + "---:|" * (len(TIERS) + 1))
    for b in fams:
        row = [grid.get((b, t), 0) for t in TIERS]
        w(f"| {b} | " + " | ".join(str(x or "") for x in row) + f" | {sum(row)} |")
    w("")
    w("## Models by family (dataset's own grouping)\n")
    w(counts_table(family, "Family", len(models)) + "\n")
    w("## Question types supported\n")
    w(counts_table(qtypes, "qtypes", len(models)) + "\n")
    w("## Licences\n")
    w(counts_table(license_, "Licence", len(models)) + "\n")
    w("## Hardware targets\n")
    w(counts_table(hw, "Hardware", len(models)) + "\n")

    w("## Shortlist for local experiments\n")
    w(
        "Filter: Apache-2.0 or MIT licence, runs locally, supports Choice and Noul or serves `/v1/systemone`, "
        f"and reports a metric. {len(short)} models match. Metrics use different benchmarks and are not comparable across rows.\n"
    )
    w("| Model | Author | Date | Base | Params | Approach | Hardware | Metric | Our doc |")
    w("|---|---|---|---|---|---|---|---|---|")
    for r in short:
        doc = our_doc(r)
        w(
            f"| [{cell(r['name'], 40)}]({r['url']}) | {cell(r['author'], 24)} | {r['date']} | {cell(r.get('base_model'), 40)} "
            f"| {cell(r.get('params'), 12)} | {cell(r.get('approach'))} | {cell(r.get('hw'), 24)} | {cell(r.get('metric'), 70)} "
            f"| {f'[doc]({doc})' if doc else ''} |"
        )
    w("")

    w("## Apple Silicon-ready models\n")
    w(f"Models the dataset tags with MLX / MPS or llama.cpp hardware: {len(mac)}.\n")
    w("| Model | Author | Params | Hardware | Licence | Metric |")
    w("|---|---|---|---|---|---|")
    for r in sorted(mac, key=lambda r: r["date"]):
        w(
            f"| [{cell(r['name'], 40)}]({r['url']}) | {cell(r['author'], 24)} | {cell(r.get('params'), 12)} "
            f"| {cell(r.get('hw'), 30)} | {cell(r.get('license'), 16)} | {cell(r.get('metric'), 70)} |"
        )
    w("")

    w(f"## All {len(models)} models\n")
    w("Sorted by backbone, then size tier, then date.\n")
    w("| Model | Author | Date | Backbone | Base | Params | Approach | Licence | Metric |")
    w("|---|---|---|---|---|---|---|---|---|")
    for r in sorted(models, key=lambda r: (backbone(r), TIERS.index(size_tier(r)), r["date"], r["name"].lower())):
        w(
            f"| [{cell(r['name'], 40)}]({r['url']}) | {cell(r['author'], 24)} | {r['date']} | {backbone(r)} "
            f"| {cell(r.get('base_model'), 40)} | {cell(r.get('params'), 12)} | {cell(r.get('approach'))} "
            f"| {cell(r.get('license'), 16)} | {cell(r.get('metric'), 60)} |"
        )
    w("")
    OUT.write_text("\n".join(out))
    print(f"wrote {OUT.relative_to(ROOT)}: {len(models)} models, {len(short)} shortlisted, {len(mac)} Mac-ready")


if __name__ == "__main__":
    main()

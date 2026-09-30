# 03 Jev vs open models on document tasks

**Status:** done (upstream run by LlamaIndex, not re-run here).

## Credit

This experiment is the work of [LlamaIndex](https://www.llamaindex.ai/): the [`run-llama/jev_vs_oss`](https://github.com/run-llama/jev_vs_oss) repo by Logan Markewich, MIT licence, © 2026 LlamaIndex. We copied it here as-is from commit [`0a3726f`](https://github.com/run-llama/jev_vs_oss/commit/0a3726fabea08cf9766fe04ec25815f0631009be) (2026-09-24), checked 2026-09-30. Their licence is in [LICENSE](LICENSE) and their original README in [UPSTREAM_README.md](UPSTREAM_README.md).

Every number below comes from the executed notebook [jev_vs_open.ipynb](jev_vs_open.ipynb) in that commit. We have not re-run it.

## Question

On five document-pipeline tasks, how does Jev compare with an open decoder, two open encoders and a specialised open tool, on accuracy, latency and cost?

All PDF work (render, native text, OCR) runs through [liteparse](https://github.com/run-llama/liteparse) (pdfium + tesseract), because Jev takes text only.

## Models

| Backend | What it is | Where it ran | How it answers |
|---|---|---|---|
| Jev | `jev-1.13.0` via `typesafe-sdk` ([jev.md](../../docs/models/jev.md)) | TypeSafe API (US) | native Choice |
| Qwen3.5-4B | `Qwen/Qwen3.5-4B`, revision not pinned | Modal, one L4 GPU | SemIf-style: next-token logits over option letters, softmax |
| Laya | `convaiinnovations/laya`, `typed-decisions` checkpoint, `max_len=2048`, `head_max_len=512` ([open-reproductions.md](../../docs/models/open-reproductions.md#laya)) | local Mac, MPS | jev-compatible decision head |
| jeff | [logan-markewich/jeff](https://github.com/logan-markewich/jeff), jev System One API on gliformer-large-v1 | Modal | jev wire format, label scores normalised |
| lingua | n-gram language detector | local CPU | language task only |
| tesseract OSD | `--psm 0` orientation detection | local CPU | orientation task only |
| heuristic | escalate if OCR confidence < 0.85 or < 300 chars | local | triage task only |

The upstream docs give jeff as 400M (README) and 576M (notebook table); [benchmarks.md](../../docs/benchmarks.md) lists 576M.

## Tasks and data

| Task | n | State | Question | Ground truth |
|---|---:|---|---|---|
| Language | 48 | first 1,200 chars of native PDF text | Choice(12) | Wikipedia `20231101` excerpts in 12 languages, rendered to PDF |
| Orientation | 32 | OCR of the page at 0/90/180/270°, 500 chars each | Choice(4) | Wikipedia pages scanned then rotated |
| Classify | 96 | up to 2,500 chars of OCR text | Choice(16), one-line descriptions | RVL-CDIP test scans (6 per class) |
| Split | 82 | last 700 chars of page *n*, first 700 of page *n+1* | Choice(2) per boundary | concatenated Wikipedia articles, 27 true boundaries |
| Triage | 48 | liteparse `is_complex` signals + OCR confidence + excerpt (JSON) | Choice(2): `local_ok` / `upgrade` | degraded, rotated scans; `upgrade` if OCR character error rate > 10% |

Corpora are built by `uv run build-corpus all` with fixed seeds (0; triage 1). Sources: [`wikimedia/wikipedia`](https://huggingface.co/datasets/wikimedia/wikipedia) (CC BY-SA 4.0 per HF card, unverified) and [`chainyo/rvl-cdip`](https://huggingface.co/datasets/chainyo/rvl-cdip) (licence not checked, unverified). Nothing from either is committed here.

## Results

Accuracy, from the notebook's overview table.

| Task | Jev | Qwen3.5-4B | Laya | jeff | Specialised tool |
|---|---:|---:|---:|---:|---:|
| Language (n=48) | 100.0% | 100.0% | 39.6% | 47.9% | lingua 100.0% |
| Orientation (n=32) | 93.8% | 90.6% | 28.1% | 21.9% | tesseract OSD 100.0% |
| Classify (n=96) | 54.2% | 51.0% | 24.0% | 26.0% | — |
| Split (n=82) | 96.3% | 87.8% | 70.7% | 73.2% | — |
| Triage (n=48) | 85.4% | 95.8% | 52.1% | 64.6% | heuristic 93.8% |

Cost in USD per 1,000 decisions. Jev: $0.042 per million input tokens. Qwen3.5-4B: wall seconds × Modal L4 at $0.80/h. Laya, jeff and the tools are counted as $0.

| Task | Jev | Qwen3.5-4B |
|---|---:|---:|
| Language | $0.040 | $0.096 |
| Orientation | $0.054 | $0.389 |
| Classify | $0.042 | $0.116 |
| Split | $0.030 | $0.070 |
| Triage | $0.034 | $0.036 |

Latency p50 / p95 in seconds.

| Task | Jev | Qwen3.5-4B | Laya | jeff | Tool |
|---|---|---|---|---|---|
| Language | 0.13 / 0.25 | 0.17 / 1.74 | 0.11 / 0.17 | 0.39 / 1.42 | lingua 0.0015 / 0.0021 |
| Orientation | 0.24 / 0.31 | 1.75 / 1.88 | 0.20 / 0.24 | 0.42 / 0.63 | OSD 0.55 / 0.57 |
| Classify | 0.14 / 0.26 | 0.26 / 2.00 | 0.14 / 0.21 | 0.32 / 0.64 | — |
| Split | 0.13 / 0.27 | 0.14 / 1.78 | 0.09 / 0.12 | 0.32 / 1.15 | — |
| Triage | 0.16 / 0.37 | 0.16 / 0.20 | 0.12 / 0.17 | 0.35 / 0.64 | heuristic < 0.001 |

Split, boundary detection (27 boundaries):

| Backend | Precision | Recall | F1 |
|---|---:|---:|---:|
| Jev | 0.900 | 1.000 | 0.947 |
| Qwen3.5-4B | 0.947 | 0.667 | 0.783 |
| Laya | 0.548 | 0.630 | 0.586 |
| jeff | 0.632 | 0.444 | 0.522 |

Classify, accuracy when acting only on answers at or above a confidence threshold (coverage / accuracy):

| Threshold | Jev | Qwen3.5-4B | Laya | jeff |
|---|---|---|---|---|
| 0.0 | 100% / 54.2% | 100% / 51.0% | 100% / 24.0% | 100% / 26.0% |
| 0.5 | 83.3% / 62.5% | 74.0% / 63.4% | 32.3% / 41.9% | 0% / — |
| 0.7 | 69.8% / 68.7% | 62.5% / 71.7% | 18.8% / 61.1% | 0% / — |
| 0.9 | 45.8% / 81.8% | 37.5% / 86.1% | 4.2% / 75.0% | 0% / — |

## Findings

- **Specialised tools match or beat every model on the tasks they cover.** lingua ties Jev and Qwen at 100% on language in 1.5 ms. tesseract OSD scores 100% on orientation against Jev's 93.8%. The two-rule heuristic scores 93.8% on triage against Jev's 85.4%.
- **Jev and Qwen3.5-4B read out SemIf-style are close.** Across the five tasks they sit within 10.4 points of each other. Jev leads on four tasks by 0–8.5 points; Qwen leads triage by 10.4 points.
- **Jev costs less per decision than a 4B model on an on-demand L4.** Jev costs $0.030–0.054 per 1,000 decisions; Qwen costs $0.036–0.389, with orientation's four OCR candidates making it the most expensive. Jev's p95 stays ≤ 0.37 s; Qwen's p95 reaches 1.7–2.0 s on four tasks.
- **Jev finds every document boundary.** On split it has recall 1.000 at precision 0.900. Qwen has higher precision (0.947) but misses a third of boundaries.
- **Zero-shot RVL-CDIP from OCR text is hard for all four models.** Jev scores 54.2% and Qwen 51.0% on 16 classes. Jev's confusion matrix sends advertisements and handwritten pages to `file_folder`, which suits pages with little OCR text.
- **Confidence thresholds work for Jev and Qwen on classify.** At ≥ 0.9, Jev keeps 45.8% of pages at 81.8% accuracy; Qwen keeps 37.5% at 86.1%.
- **The two open encoders fall short on these tasks.** Laya and jeff score 22–73%, below Jev and Qwen on every task. On language, jeff sends Turkish and Russian pages to English (7 of 8). On orientation, all 10 of the first jeff errors the notebook lists pick 270°.
- **Encoder confidences need checking before use.** Laya's confidence on the first 10 wrong orientation answers listed is 0.003–0.034, and it logs a warning that its `choice:11+` temperatures were clamped, so confidence for 11+ options is uncalibrated. No jeff answer on classify reaches confidence 0.3; its mean confidence on language is 0.07.

## Limits

- Samples are small: 32–96 decisions per task. A 5-point gap on 48 items is 2–3 decisions.
- One run, no seeds repeated, no confidence intervals.
- Model revisions are not pinned for Qwen3.5-4B, Laya or jeff. Jev reported `jev-1.13.0`.
- Laya's context limits (512–1,024 tokens trained) are below the 2,500-char classify state; upstream raised the budgets to fit.
- Costs count Modal GPU time only for Qwen; they exclude cold starts and idle time, and count local hardware as free.
- Hardware for local backends is an Apple Silicon Mac (MPS, from the notebook output); model and memory not stated.

## Data governance

- Jev: TypeSafe API, United States ([jev.md](../../docs/models/jev.md#data-governance)). Only public data (Wikipedia, RVL-CDIP) was sent.
- Qwen3.5-4B and jeff: Modal, LlamaIndex's account; region not stated.
- Laya, lingua, tesseract: local.

## Running it

See [UPSTREAM_README.md](UPSTREAM_README.md). In short:

```bash
cd experiments/03-jev-vs-open-document-tasks
uv sync
cp .env.example .env                 # add TYPESAFE_API_KEY
uv run build-corpus all              # ~5-10 min, writes ./data (gitignored)
uv run modal deploy modal_app.py     # Qwen3.5-4B on an L4
uv run jupyter lab jev_vs_open.ipynb
```

The notebook expects a jeff server at `JEFF_BASE_URL`; see the upstream README.

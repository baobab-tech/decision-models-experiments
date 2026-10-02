# 01 Many-option classification

**Status:** proposed. Nothing runs until the plan is approved.

## Question

Can zero-shot decision models classify and tag international development evaluation reports as well as an LLM pipeline or a fine-tuned small LLM, at 3 to 250 labels, on ~50-token excerpts and ~2,000-token first pages?

## Data

1,420 public international development evaluation reports with LLM-pipeline labels: [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs) (public); see [common/datasets.md](../common/datasets.md). Test splits only, split by document.

| Task | Input | n | Field | Labels | Type |
|---|---|---:|---|---:|---|
| **A. Document classification** | First pages: median 1,935 tokens, p99 5,267 | 134 docs | `evaluation_approach` | 6 | single |
| | | | `evaluation_type` | 4 | single |
| | | | `temporality` | 3 | single |
| | | | `themes` | 18 | multi, 1–4 |
| | | | `countries` | 54 seen; ~250 ISO codes | multi |
| **B. Excerpt tagging** | Finding, recommendation or methodology excerpt: median 34 words, p90 107 | 600: `eval_sample` (300 findings, 150 recommendations, 150 methodology) | `themes` | 22 | multi, median 2 |
| | | | `regions` | 17 | multi |
| | | | `methods` (methodology only) | 24 | multi |
| | | | `countries` | 121 seen; ~250 ISO codes | multi |

- Labels come from an ingestion pipeline's LLMs (Gemini 2.5 Flash, gpt-oss-120b, Qwen 3 235B) and are treated as gold. 36 document labels were corrected by hand.
- Option counts come from the real taxonomy. `countries` is the 100+ case: ask over the 54 or 121 codes seen, and over all ~250 ISO codes.

## Models

| Model | Where | Why |
|---|---|---|
| [Jev](../../docs/models/jev.md) | TypeSafe API | Reference model; 255 options |
| [Liquid d1](../../docs/models/liquid-d1.md) | Liquid API (`d1:free`) | Vendor-reported Decision Index leader |
| [GLiDE](../../docs/models/glide.md) | Fastino API | 255 options; 40k tokens per question |
| [GLiNER2.5-Decide](../../docs/models/gliner-decide.md) | This Mac | Only model with native multi-label; earlier zero-shot runs used GLiNER2.5 small/base |
| [Kev-4B](../../docs/models/kev.md) | This Mac (MLX) | Open, Jev-compatible, 255 options |
| [Laya](../../docs/models/laya.md) | This Mac | Small encoder; context 512 (en), so task A only after chunking |

## Question formats

- Single-label fields: one Choice.
- Multi-label fields: one Noul per label in one request, thresholded at 0.5. GLiNER2.5-Decide also uses its native multi-label mode.
- `countries`: flat Choice/Noul over all codes vs staged (region first, then countries within it).
- Label names only vs names with one-line definitions (the `definitions` prompt variant from the classify experiments).

## Baselines

- **Earlier Baobab Tech classifier runs on the same test split and metric** (not re-run; results in `baobabtech/evalexplorer-classify-experiments`, private):

  | Model | Zero-shot | After SFT |
  |---|---:|---:|
  | Qwen3.5-4B | 67.1 | 84.7 |
  | Gemma 4 E4B | 72.3 | 83.0 |
  | GLiNER2.5 base | 45.4 | 57.8 |

- **[DeepSeek-V4.1-Flash](https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash)** zero-shot via HF Inference Providers, with the same prompt as the pipeline.
- Embeddings + logistic regression trained on the train split, for task B.

## Judge

The gold labels are LLM output, not truth. On every item where a decision model disagrees with gold, DeepSeek-V4.1-Flash, called via HF Inference Providers, sees the text, the gold labels and the prediction, and decides which is supported.

- Report accuracy against gold, plus a judge-adjusted score.
- Check the judge on 100 items: compare its verdicts with the 36 hand-corrected documents, and with a second judge. [Qwen3.8-Flash-Next](https://huggingface.co/Qwen/Qwen3.8-Flash-Next) is the second judge if a provider serves it. On 2026-10-02 only featherless-ai listed it, and the HF router did not.

## Metrics

From [common/metrics.md](../common/metrics.md):

- **Main score:** `mean_field_score`, the mean of per-field accuracy and F1, so results compare with the earlier runs.
- **Per field:** `accuracy` for single-label fields; `micro_f1` and `macro_f1` for multi-label fields.
- **Calibration:** `ece_15`, `brier`, `coverage_at_5`.
- **Speed and cost:** `latency_p50_ms` and `p95`, `cost_per_1k`, `tokens_per_request`.
- **Judge:** the judge-adjusted score.

## Data governance

- Local models run on this Mac.
- These models send document text to third parties:
  - Jev: US.
  - d1: US. Liquid may use inputs to improve its models.
  - GLiDE: US.
  - DeepSeek-V4.1-Flash: the region depends on the provider. Pin one provider and record it.
- The reports and dataset are public; the maintainer approved sending them to these APIs (2026-10-02).

## What would change a decision

- **Use a decision model as the classifier:** it reaches the SFT models' ~84 `mean_field_score` zero-shot, or within 3 points, at lower latency or cost.
- **Use one for excerpt tagging only:** it matches gold on task B but not task A, which points to input length as the limit.
- **Keep fine-tuned small LLMs:** every decision model stays below the 67–72 zero-shot LLM range.

# 02 Fine-tuning decision models

**Status:** proposed. It runs after [01](../01-many-option-classification/), on the same data and phases: task B (excerpts) first, then task A (documents).

## Question

Does a fine-tuned open decision model reach the LLM range from 01 and match the fine-tuned small LLMs (`mean_field_score` 77–80 against GLM labels), and how many labelled examples does it take to beat its own zero-shot score from 01?

## What we already know

- Earlier Baobab Tech runs fine-tuned generative LLMs and GLiNER2.5 on this exact task (results in `baobabtech/evalexplorer-classify-experiments`, private):

  | Model | Size | Zero-shot vs GLM | Fine-tuned vs GLM | Fine-tuned vs pipeline | Seconds per doc |
  |---|---|---:|---:|---:|---:|
  | Gemma 4 26B-A4B | 26B (4B active) | 72.9 | 80.3 | 84.4 | 1.46 |
  | Qwen3.5-4B | 4B | 66.2 | 77.8 | 84.7 | 1.22 |
  | LFM2.5-350M | 350M | 20.3 | 70.9 | 79.2 | 0.58 |
  | GLiNER2.5 small | 74M | 47.1 | 52.7 | 57.3 | 0.04 |

  Those models were fine-tuned on pipeline labels. The scores are task A only, against single label sets: GLM-5.3-Flash or the pipeline. They are rescored against 01's consensus reference if their predictions are available.

- GLiNER2.5 base and small plateaued at 57–58 after fine-tuning (52–57 against GLM). Approach and type accuracy stayed at 25–60%.
- Jev, d1 and GLiDE cannot be fine-tuned.
- [ModernJEV-Decide-Preview](../../docs/models/modernjev-decide.md#fine-tuning) gives a cost reference: about $5.41 on one A100. It also fell below the majority baseline on a task family it was not trained on.

## Data

- **Evaluation:** against 01's leave-one-out consensus of four LLM label sets (pipeline, GLM-5.3-Flash, DeepSeek-V4.1-Flash, Qwen3.8-Flash-Next), on the same test items, so zero-shot and fine-tuned scores compare directly.
- **Training labels:** pipeline labels by default, since they exist for every train item. One run per model trains on consensus labels (at least 3 of 4 LLMs) for a train sample, to show how much the label source matters:
  - Task B: 10,000 train excerpts labelled by GLM, DeepSeek and Qwen.
  - Task A: all 1,148 train documents labelled by DeepSeek and Qwen; GLM labels already exist.
- Generated labels go through HF Inference Providers billed to `baobabtech` ([common/README.md](../common/README.md#hf-inference-providers)) and are added to the dataset.
- **Task A:** documents, 1,148 train / 138 validation / 134 test.
- **Task B:** excerpts, 157,302 train, sampled down per run.
- Same splits as 01. See [common/datasets.md](../common/datasets.md).

## Models

| Model | Size | Method | Where it trains |
|---|---|---|---|
| [GLiNER2.5-Decide](../../docs/models/gliner-decide.md) | 340M | full and LoRA (`gliner2[train]`) | HF Jobs (CPU-only on this Mac) |
| [openJev Verdict](../../docs/models/rlcd-modernbert.md) or [Laya](../../docs/models/laya.md) | 151M / 421M | full | This Mac (MPS) |
| [Kev-0.8B](../../docs/models/kev.md) | 0.8B | LoRA + pointer head | HF Jobs or this Mac (MLX) |
| Plain ModernBERT-base classifier (control) | 150M | full, one head per field | This Mac (MPS) |

## Variables

- Training examples per label:
  - Task A: 8, 32, 128, all (up to 1,148 docs).
  - Task B: 8, 32, 128, 1,000, all.
- Method: full fine-tune vs LoRA, where both exist.

## Metrics

- The same as 01, including the per-model write-up (fine-tuning, limitations, opportunities, further work), so zero-shot, fine-tuned and SFT-LLM rows sit in one table.
- Training time and cost: record the Job ID, flavor and USD.
- Forgetting: zero-shot accuracy on a held-out field, and on the Decision Index subset each model was trained against, before and after fine-tuning.

## Data governance

- Train on this Mac where possible.
- HF Jobs does not document its region; the data is public, and the maintainer approved using it (2026-10-02).
- Label generation sends public excerpts and documents to HF Inference Providers; record the pinned provider and region.
- Record where each run trained.

## What would change a decision

- **Replace the LLM in ingestion:** a fine-tuned decision model scores within 01's LLM range at under 0.1 s per item, beating the LLMs and SFT LLMs on cost and speed.
- **Keep the SFT LLMs:** decision models plateau near GLiNER2.5's 57–58.

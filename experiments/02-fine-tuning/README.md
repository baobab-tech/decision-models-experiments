# 02 Fine-tuning decision models

**Status:** planned. Plan approved 2026-10-02. It runs after [01](../01-many-option-classification/), on the same data and phases: task B (excerpts) first, then task A (documents).

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

- **Splits:** the same as 01. Task A: documents, 1,148 train / 138 validation / 134 test. Task B: excerpts, 157,302 train, sampled per run. See [common/datasets.md](../common/datasets.md).
- **Evaluation:** against 01's leave-one-out consensus of four LLM label sets (pipeline, GLM-5.3-Flash, DeepSeek-V4.1-Flash, Qwen3.8-Flash-Next), on the same test items, so zero-shot and fine-tuned scores compare directly.
- **Training labels:** settled by a pilot before the main runs.
  - A fixed sample of 10,000 train excerpts gets GLM, DeepSeek and Qwen labels, through HF Inference Providers billed to `baobabtech` ([common/README.md](../common/README.md#hf-inference-providers)).
  - Laya trains twice on the same excerpts: once on pipeline labels, once on consensus labels (at least 3 of 4 LLMs).
  - If the consensus-label run scores at least 2 points higher, consensus labels become the default and are generated for the rest of the training data. Otherwise pipeline labels are the default, since they cover every train item.
  - Task A gets the same treatment in its phase: DeepSeek and Qwen label the 1,148 train documents; GLM labels already exist.

## Models

| Model | Size | Method | Where it trains |
|---|---|---|---|
| [GLiNER2.5-Decide](../../docs/models/gliner-decide.md) | 340M | full and LoRA (`gliner2[train]`) | HF Jobs (CPU-only on this Mac) |
| [Laya](../../docs/models/laya.md) | 421M | full | This Mac (MPS) |
| [openJev Verdict](../../docs/models/rlcd-modernbert.md) | 151M | full | This Mac (MPS) |
| [Kev-0.8B](../../docs/models/kev.md) | 0.8B | LoRA + pointer head | HF Jobs (`a10g-large`) |
| [Kev-4B](../../docs/models/kev.md) | 4B | LoRA + pointer head | HF Jobs (`a10g-large`) |
| Plain ModernBERT-base classifier (control) | 150M | full, one head per field | This Mac (MPS) |

- Every model has a zero-shot score from 01 except the ModernBERT control, which has no zero-shot mode.
- Kev-0.8B against Kev-4B shows the effect of size; Verdict against Laya does the same for encoders.
- Multi-label fields are trained the way 01 asks them: one Noul per label (Kev, Laya, Verdict) or GLiNER2's native multi-label `true_label` list.

## Variables

- Training examples per label:
  - Task A: 8, 32, 128, all (up to 1,148 docs).
  - Task B: 8, 32, 128, 1,000, all.
- Method: full fine-tune vs LoRA, where both exist.
- Seeds: 3 per run at 8, 32 and 128 examples per label, where variance is high; 1 above.
- **Stop rule:** a model gets the task B "all" run only if its 1,000-example run is within 10 points of 01's LLM range. This caps HF Jobs spend on models that have plateaued.

## Metrics

- The same as 01, including the per-model write-up (fine-tuning, limitations, opportunities, further work), so zero-shot, fine-tuned and SFT-LLM rows sit in one table.
- Training time and cost: record the Job ID, flavor and USD.
- Inference speed of each fine-tuned model, in seconds per item, against the 0.1 s target.
- Forgetting: accuracy before and after fine-tuning on a fixed 200-item sample of the [Decision Index 0.2.1](../../docs/benchmarks.md#decision-index).
- Transfer: one extra run per model at 1,000 examples per label leaves `regions` out of training and scores it zero-shot. Main runs train on every field.

## Data governance

- Train on this Mac where possible.
- HF Jobs run with `--namespace baobabtech`, so they bill to the org.
- Fine-tuned weights and adapters are pushed to private `baobabtech` model repos with their run metadata. Publishing them is a separate decision, made after the results are written up.
- HF Jobs does not document its region; the data is public, and the maintainer approved using it (2026-10-02).
- Label generation sends public excerpts and documents to HF Inference Providers; record the pinned provider and region.
- Record where each run trained.

## What would change a decision

- **Replace the LLM in ingestion:** a fine-tuned decision model scores within 01's LLM range at under 0.1 s per item, beating the LLMs and SFT LLMs on cost and speed.
- **Keep the SFT LLMs:** decision models plateau near GLiNER2.5's 57–58.

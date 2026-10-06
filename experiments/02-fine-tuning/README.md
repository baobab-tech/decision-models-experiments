# 02 Fine-tuning decision models

**Status:** planned; the main experiment after 01 (2026-10-06). Task B (excerpts) first.

## Question

What is the smallest model, by compute per excerpt, that reaches 01's LLM range (84.2–85.0 `mean_field_score` against the 3-LLM majority) on excerpt tagging after fine-tuning, and how many labelled examples does it take?

Why: 01 found no zero-shot decision model in the LLM range, and small zero-shot models scored 17–19. A cheap LLM matches decision models on cost and speed, so the case for a small model is compute and environmental impact: a ~150M encoder that reads each excerpt once would use about 1/1,000 of DeepSeek-V4.1-Flash's compute per excerpt ([01 compute table](../01-many-option-classification/README.md#phase-1-compute-per-excerpt)).

## First step

1. Label a fixed sample of 10,000 train excerpts (5,000 findings, 2,500 recommendations, 2,500 methodology, seed 0; ids in `results/labels/train_sample.json`) with GLM-5.3-Flash and DeepSeek-V4.1-Flash, using [label_excerpts.py](../common/label_excerpts.py) and the production taxonomy and definitions (eval-explorer `ingestion-pipeline/lib/extract/`, identical on `main` and `staging`, checked 2026-10-06). Cost: about $3.
   - Training targets are soft: 1 if both LLMs chose the label, 0.5 if one did, 0 if neither. No third labeller.
   - Qwen3.8-Flash-Next was dropped for training labels: featherless-ai allows 2 concurrent requests and Qwen reasons on every excerpt, about 10 excerpts per minute, so ~17 hours for 10,000 (2026-10-06). On 01's test sample, Qwen decides 18% of the majority labels (169 of 953), all of them labels where GLM and DeepSeek disagree; soft targets mark those as uncertain instead.
   - Evaluation is unchanged: 01's 3-LLM majority on the 600 test excerpts, Qwen included.
2. Fine-tune two models on those labels, on this Mac:
   - a plain ModernBERT-base classifier (150M), one sigmoid head per field, reading each excerpt once;
   - GLiNER2.5-Decide (340M), native multi-label.
3. Score on 01's 600 test excerpts; fit thresholds on 01's 300-excerpt validation sample; report compute per excerpt next to the score.
4. One ModernBERT run on pipeline labels for the same 10,000 excerpts shows how much the label source matters. Pipeline labels agree with the LLM majority at 52.8 on test, so they are not the default.

The model list and variables below apply after the first step, if a small model gets within ~10 points of the LLM range.

## What we already know

- Earlier Baobab Tech runs fine-tuned generative LLMs and GLiNER2.5 on this exact task (results in `baobabtech/evalexplorer-classify-experiments`, private):

  | Model | Size | Zero-shot vs GLM | Fine-tuned vs GLM | Fine-tuned vs pipeline | Seconds per doc |
  |---|---|---:|---:|---:|---:|
  | Gemma 4 26B-A4B | 26B (4B active) | 72.9 | 80.3 | 84.4 | 1.46 |
  | Qwen3.5-4B | 4B | 66.2 | 77.8 | 84.7 | 1.22 |
  | LFM2.5-350M | 350M | 20.3 | 70.9 | 79.2 | 0.58 |
  | GLiNER2.5 small | 74M | 47.1 | 52.7 | 57.3 | 0.04 |

  Those models were fine-tuned on pipeline labels. The scores are task A only, against single label sets: GLM-5.3-Flash or the pipeline. They are rescored against 01's majority reference if their predictions are available.

- GLiNER2.5 base and small plateaued at 57–58 after fine-tuning (52–57 against GLM). Approach and type accuracy stayed at 25–60%.
- Jev, d1 and GLiDE cannot be fine-tuned.
- [ModernJEV-Decide-Preview](../../docs/models/modernjev-decide.md#fine-tuning) gives a cost reference: about $5.41 on one A100. It also fell below the majority baseline on a task family it was not trained on.

## Data

- **Splits:** the same as 01. Task A: documents, 1,148 train / 138 validation / 134 test. Task B: excerpts, 157,302 train, sampled per run. See [common/datasets.md](../common/datasets.md).
- **Evaluation:** against 01's reference, the labels chosen by at least 2 of GLM-5.3-Flash, DeepSeek-V4.1-Flash and Qwen3.8-Flash-Next, on the same test items. Training targets come from GLM and DeepSeek only (soft labels; see [First step](#first-step)), so zero-shot and fine-tuned scores compare directly. There is no human gold set, so scores measure agreement with LLMs, not correctness ([01](../01-many-option-classification/README.md#reference-labels)).
- **Training labels:** soft GLM + DeepSeek labels (see [First step](#first-step)). One ModernBERT run on pipeline labels for the same excerpts shows how much the label source matters; pipeline labels agree with the LLM majority at 52.8 on 01's test sample, against 84.2–85.0 between the LLMs.

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

- **Replace the LLM in ingestion:** a fine-tuned small model scores within 01's LLM range at a small fraction of DeepSeek-V4.1-Flash's compute per excerpt.
- **Keep the LLM:** the best fine-tuned small model stays more than ~10 points below the LLM range after 10,000 examples.
- **Keep the SFT LLMs:** decision models plateau near GLiNER2.5's 57–58.

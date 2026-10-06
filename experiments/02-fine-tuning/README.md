# 02 Fine-tuning decision models

**Status:** running. First step done (2026-10-06).

## Question

What is the smallest model, by compute per excerpt, that reaches 01's LLM range on excerpt tagging after fine-tuning, with the context the production pipeline uses, and how many labelled examples does it take?

Why: the case for a small model is compute and environmental impact. A ~150M encoder needs a small fraction of a 10B+-active-parameter LLM's compute per excerpt, if it can match its tags.

## First step

1. Input: `doc+summary`, the context chosen by 01's [context pilot](../01-many-option-classification/README.md#pilot-result) (title, Document Start, executive summary and abstract, then the excerpt), so the model sees what production's tagger sees. Document-level context (title, Document Start, summary) is the same for every excerpt of a report, so a model can encode it once per document.
2. Label a fixed sample of 10,000 train excerpts (5,000 findings, 2,500 recommendations, 2,500 methodology, seed 0; ids in [results/labels/train_sample.json](results/labels/train_sample.json)) with GLM-5.3-Flash and DeepSeek-V4.1-Flash, using production's taxonomy and definitions.
   - Training targets are soft: 1 if both LLMs chose the label, 0.5 if one did, 0 if neither.
   - Evaluation: 01's test excerpts, scored as mean agreement with GLM and DeepSeek.
3. Fine-tune small encoders on those labels as HF Jobs in the `baobabtech` namespace with [train_encoder.py](train_encoder.py), which reads everything from the Hub so others can rerun it. Candidates: encoders released since March 2026 under ~300M parameters with a context window of at least 8,192 tokens, with ModernBERT-base and Ettin as 2025 references; label-conditioned models (GLiClass, GLiNER2.5) in a second round.
   - **Input layout:** `[start] excerpt block [sep] context block [sep]`, excerpt first, so truncation only cuts context. The excerpt and context blocks keep their headings (`## EXCERPT TO CLASSIFY`, `## CONTEXT SECTIONS`) as markers.
   - **Joint model (default):** one pass over excerpt + context; the classifier reads the mean of the excerpt's token vectors only. Those tokens attend to the context, so they carry the report's country and topic, but the context tokens do not dilute the vector the classifier reads. ~540 tokens per excerpt.
   - **Two-tower model:** the same encoder reads the document context once per report and the excerpt on its own; the classifier sees [excerpt vector, context vector, their product]. At ~135 excerpts per report, that is ~90 tokens per excerpt, about 6× less compute. Run with `jhu-clsp/ettin-encoder-150m`.
4. Score on 01's test excerpts; fit one threshold on 01's validation sample; report compute per excerpt next to the score.
5. One run on pipeline labels for the same excerpts shows how much the label source matters.

The model list and variables below apply after the first step, if a small model gets within ~10 points of the LLM range.

## Results

### First step: encoder sweep

Run 2026-10-06 as HF Jobs in `baobabtech` (A10G; bf16; effective batch 32; 5 epochs; learning rate 5e-5; one threshold fitted on 01's validation sample). Training: 9,998 excerpts with soft GLM + DeepSeek labels and the `doc+summary` context (dataset revision `5b5de6f`). Test: 01's 600 excerpts. Score: mean micro-F1 × 100 against GLM and DeepSeek; the LLMs agree with each other at **88.8** (themes 82.4, regions 94.9, countries 89.8, methods 88.1). Per-run metrics: [results/sweep_summary.json](results/sweep_summary.json) and each model repo (`baobabtech/evaldocs-excerpt-tagger-*`, private).

| Model | Params | Mean | Themes | Regions | Countries | Methods | Tokens per excerpt |
|---|---:|---:|---:|---:|---:|---:|---:|
| Ettin-150M, countries from lookup | 149M | **75.3** | **80.6** | 83.7 | 72.3 | 64.4 | 541 |
| Ettin-32M, countries from lookup | 32M | 74.7 | 75.5 | 82.7 | 72.3 | **68.2** | 541 |
| ModernJEV-Decide-Preview | 149M | 73.8 | 74.0 | 89.6 | 71.6 | 60.1 | 541 |
| LFM2.5-Encoder-230M | 230M | 73.5 | 68.5 | 83.5 | **78.4** | 63.7 | 548 |
| mmBERT-small | 141M | 73.4 | 69.8 | **89.7** | 71.5 | 62.7 | 521 |
| Ettin-150M | 149M | 70.9 | 70.3 | 86.4 | 73.2 | 53.7 | 541 |
| ModernBERT-base | 149M | 68.8 | 71.3 | 84.4 | 62.1 | 57.5 | 541 |
| Ettin-150M, two-tower | 150M | 64.6 | 70.3 | 75.9 | 53.7 | 58.4 | **90** |
| F2LLM-v2-80M | 80M | 63.9 | 61.2 | 86.0 | 60.5 | 47.8 | 531 |
| Ettin-32M | 32M | 63.2 | 61.8 | 81.0 | 51.6 | 58.5 | 541 |
| Country lookup alone (01) | — | — | — | 74.7 | 71.6 | — | ~0 |

- **Countries from the lookup, not the model, help every other field.** Without the 198 country outputs, Ettin-150M's themes rise from 70.3 to 80.6 and Ettin-32M's from 61.8 to 75.5. The lookup matches the best fine-tuned country scores (72.3; only LFM2.5 is higher at 78.4).
- **Size matters little in that setup:** Ettin-32M scores 74.7 against Ettin-150M's 75.3 with a fifth of the parameters.
- **Themes and regions approach the LLMs** (best 80.6 vs 82.4, and 89.7 vs 94.9). **Methods are furthest** (best 68.2 vs 88.1); the training sample has ~2,500 methodology excerpts for 24 methods.
- **The two-tower model** reads document context once per report: ~90 tokens per excerpt instead of ~540, for 6.3 points less than the joint Ettin-150M.
- **Not reported as results, pending a check:** gte-modernbert-base (collapsed to no predictions), and harrier-oss-v1-270m, granite-embedding-97m-multilingual-r2 and NeoMME-260M (33–43; no country predictions). The first three are embedding models and NeoMME is multimodal; their training settings were not tuned.

## What we already know

- Earlier Baobab Tech runs fine-tuned generative LLMs and GLiNER2.5 on this exact task (results in `baobabtech/evalexplorer-classify-experiments`, private):

  | Model | Size | Zero-shot vs GLM | Fine-tuned vs GLM | Fine-tuned vs pipeline | Seconds per doc |
  |---|---|---:|---:|---:|---:|
  | Gemma 4 26B-A4B | 26B (4B active) | 72.9 | 80.3 | 84.4 | 1.46 |
  | Qwen3.5-4B | 4B | 66.2 | 77.8 | 84.7 | 1.22 |
  | LFM2.5-350M | 350M | 20.3 | 70.9 | 79.2 | 0.58 |
  | GLiNER2.5 small | 74M | 47.1 | 52.7 | 57.3 | 0.04 |

  Those models were fine-tuned on pipeline labels. The scores are task A only, against single label sets: GLM-5.3-Flash or the pipeline. They are rescored against 01's reference if their predictions are available.

- GLiNER2.5 base and small plateaued at 57–58 after fine-tuning (52–57 against GLM). Approach and type accuracy stayed at 25–60%.
- Jev, d1 and GLiDE cannot be fine-tuned.
- [ModernJEV-Decide-Preview](../../docs/models/modernjev-decide.md#fine-tuning) gives a cost reference: about $5.41 on one A100. It also fell below the majority baseline on a task family it was not trained on.

## Data

- **Splits:** the same as 01. Task A: documents, 1,148 train / 138 validation / 134 test. Task B: excerpts, 157,302 train, sampled per run. See [common/datasets.md](../common/datasets.md).
- **Evaluation:** 01's reference on the same test items: mean agreement with GLM-5.3-Flash and DeepSeek-V4.1-Flash. Training targets come from the same two LLMs (soft labels; see [First step](#first-step)), so zero-shot and fine-tuned scores compare directly. There is no human gold set, so scores measure agreement with LLMs, not correctness ([01](../01-many-option-classification/README.md#reference-labels)).
- **Training labels:** soft GLM + DeepSeek labels (see [First step](#first-step)). One run on pipeline labels for the same excerpts shows how much the label source matters.

## Models

| Model | Size | Method | Where it trains |
|---|---|---|---|
| [GLiNER2.5-Decide](../../docs/models/gliner-decide.md) | 340M | full and LoRA (`gliner2[train]`) | HF Jobs (CPU-only on this Mac) |
| [Laya](../../docs/models/laya.md) | 421M | full | This Mac (MPS) |
| [openJev Verdict](../../docs/models/rlcd-modernbert.md) | 151M | full | This Mac (MPS) |
| [Kev-0.8B](../../docs/models/kev.md) | 0.8B | LoRA + pointer head | HF Jobs (`a10g-large`) |
| [Kev-4B](../../docs/models/kev.md) | 4B | LoRA + pointer head | HF Jobs (`a10g-large`) |
| Plain ModernBERT-base classifier (control) | 150M | full, one head per field | This Mac (MPS) |

- Every decision model has a zero-shot score from 01; plain encoders have no zero-shot mode.
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

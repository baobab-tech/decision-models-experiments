# Experiments

The maintainer picks which experiment runs next (see [AGENTS.md](../AGENTS.md)). Each experiment gets its own `experiments/<nn>-<slug>/README.md` with the full plan before any code is written.

| # | Experiment | Status | Folder |
|---|---|---|---|
| 01 | Many-option classification | proposed | — |
| 02 | Fine-tuning decision models | proposed | — |

Statuses: `proposed` → `planned` (plan written and approved) → `running` → `done`.

## 01 Many-option classification

**Question.** Are decision models worth using for classification with 10+ options, 100+ tags, or document types, on inputs of ~100 and ~2,000 tokens? What should we use instead where they aren't?

**Findings from the research so far:**

| Model | Max options per Choice | Multi-label | Input length |
|---|---|---|---|
| [Jev](models/jev.md#scaling-limits) | 255 (docs: reliable to ~240) | one Noul per label | 64k per request |
| [Liquid d1](models/liquid-d1.md) | not published (≥2) | one Noul per label | 32k |
| [GLiNER2.5-Decide](models/gliner-decide.md#scaling-limits) | no cap in code | native (`multi_label`) | chunks of 384 words for long text |
| [Kev](models/kev.md) | 255 | one Noul per label | trained on states ≤384 tokens; served up to 65k |
| [CLM-8B](models/clm-8b.md) | no cap; option embeddings cached | via `/v1/rank` plus thresholding | 2,048 by default; longer states are truncated silently |
| [AnyJev](models/anyjev.md) | 26 | one Noul per label | base model's context |
| [Bonsai-Llama-Jev](models/bonsai-llama-jev.md) | not published | one Noul per label | 64k, split across slots |

- No vendor publishes accuracy or latency for 10 vs 100+ options.
- No study covers 100+ multi-label tags ([concepts.md](concepts.md)).
- For more than 255 options, vendors recommend running Choice questions in stages: a coarse question first, then a finer one within the chosen group.

**Variables to vary:**

- Number of options: 5, 10, 25, 50, 100, 200+.
- Label type: single-label or multi-label.
- Input length: ~100 tokens or ~2,000 tokens.
- How the question is asked:
  - one Choice
  - one Noul per label
  - staged Choices, coarse then fine
  - label names only vs names with descriptions

**Candidate datasets.** Check each licence before use.

| Dataset | Labels | Type | Typical length | Notes |
|---|---|---|---|---|
| BANKING77 | 77 | single | short | used by AnyJev and CLM-8B reports |
| CLINC150 | 150 (+OOS) | single | short | includes out-of-scope examples, which test abstention |
| DBpedia (L3) | 219 | single, hierarchical | ~50–100 tokens | tests staged Choices on a label hierarchy |
| 20 Newsgroups | 20 | single | long | news-like text of ~2,000 tokens |
| Reuters-21578 (ModApte) | 90 | multi | medium–long | news topic tags |
| Document types | ~10–30 | single | long | report, invoice, contract, …; source TBD (public or synthetic) |

**Baselines:**

- Embeddings plus kNN or logistic regression.
- Zero-shot NLI.
- An open LLM reading answer probabilities directly, both raw and through AnyJev.
- A fine-tuned encoder, where labelled data exists.

**Metrics:**

- Accuracy and macro-F1. For multi-label data, micro- and macro-F1.
- Calibration: ECE and Brier score.
- Share of items that can be decided automatically at a fixed 5% error rate.
- Latency at p50 and p95.
- Cost per 1,000 decisions.
- Tokens per request.

**Data governance.** Local models use this Mac. API models (Jev, d1) get public datasets only.

**What would change a decision.** If a decision model stays within a few points of a fine-tuned encoder at 100+ labels, we would use it for tagging without collecting training data.

## 02 Fine-tuning decision models

**Question.** Which decision models can we fine-tune, and how? How many labelled examples does it take to beat zero-shot, and on what hardware? Background is in [fine-tuning.md](fine-tuning.md).

**Findings from the research so far:**

- Jev and d1 cannot be fine-tuned. They can only be used as teachers to generate labels.
- GLiNER2.5-Decide supports full and LoRA fine-tuning. Training runs on CUDA or CPU only, so on this Mac it trains on CPU.
- Kev, the Qwen-based heads and the Laya family can be fine-tuned. The recipes and hardware needs are in [fine-tuning.md](fine-tuning.md).

**Variables to vary:**

- Model: GLiNER2.5-Decide, Laya, a small Kev or Qwen-head model.
- Method: full fine-tune or LoRA.
- Labelled examples per class: 0, 8, 32, 128, all.
- Where training runs: this Mac (CPU, MPS or MLX) or a cloud GPU (HF Jobs).

**Candidate tasks.** The same datasets as experiment 01, so zero-shot and fine-tuned results can be compared directly.

**Metrics:**

- The same accuracy and calibration metrics as 01.
- Training time and cost.
- Accuracy on data from a different source than the training set.
- Whether other question types degrade after fine-tuning.

**Data governance.** Fine-tune on this Mac or on EU infrastructure. Record where each training run happened.

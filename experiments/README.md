# Experiments

The maintainer picks which experiment runs next; see [AGENTS.md](../AGENTS.md).

| # | Experiment | Status | Question |
|---|---|---|---|
| 01 | [Many-option classification](01-many-option-classification/) | done (phase 1) | Can decision models and small encoders tag and classify international development evaluation reports as well as LLMs, with the context production uses (3–250 labels)? Phase 1: excerpt tagging. |
| 02 | [Fine-tuning small encoders and decision models](02-fine-tuning/) | done | What is the smallest model, by compute per excerpt, that reaches 01's LLM range on excerpt tagging (with production context) after fine-tuning, and with how many labels? |
| 03 | [Jev vs open models on document tasks](03-jev-vs-open-document-tasks/) | done (LlamaIndex) | How do Jev, Qwen3.5-4B, Laya, jeff and specialised tools compare on language, orientation, classification, splitting and parse triage of PDFs? |

Statuses: `proposed` → `planned` (plan approved) → `running` → `done`.

Experiment 03 is [LlamaIndex's `jev_vs_oss`](https://github.com/run-llama/jev_vs_oss) (MIT), copied with credit; its results are theirs.

## The story

For outside readers; each step links to the experiment README with the numbers.

1. **The task.** EvalExplorer's ingestion pipeline uses a large LLM to tag excerpts of evaluation reports with themes (22), regions (17), countries (198) and methods (24), with document context in view. Can a much smaller model do it?
2. **Context decides the answer.** Tagged alone, an excerpt rarely says which country it is about. Adding the report's title, first 100 words and executive summary raises agreement with the pipeline from 44 to 68; adding the whole section lowers it ([01 context pilot](01-many-option-classification/README.md#pilot-result)).
3. **The bar.** No human gold set exists. Two LLMs (GLM-5.3-Flash, DeepSeek-V4.1-Flash) given that context agree at 88.8 micro-F1; a model at that level agrees with each LLM as much as they agree with each other ([01 reference](01-many-option-classification/README.md#reference-labels-result)).
4. **Geography is mostly a lookup.** Matching country names in the excerpt, title and first 100 words scores 71.6 on countries and 74.7 on regions with no model at all ([01 lookup](01-many-option-classification/README.md#country-lookup-baseline)).
5. **Zero-shot decision models** with the same context fall short of the LLMs' 88.8.
   - Jev reaches 72.5 and d1 69.0, with countries from the lookup. Jev beats the pipeline's own labels (67.5) for $0.19 per 600 excerpts.
   - The open decision models score 38–65 (Kev-4B best).
   - Details: [01 zero-shot](01-many-option-classification/README.md#zero-shot-decision-models).
6. **Fine-tuned small encoders get closest.**
   - Trained on 28,664 LLM-labelled excerpts, they score 79.7–81.4.
   - Ettin-32M scores 80.4 with 31M parameters.
   - The top 10 of 12 encoders are within 1.7 points of each other. Training data matters more than the choice of encoder: 66.2 at 1,000 excerpts, 77.0 at 10,000, 80.4 with excerpts added for rare labels.
   - Details: [02 results](02-fine-tuning/README.md#second-step-per-model-recipes-and-balanced-data).
7. **The remaining gap is mostly the taxonomy.**
   - On themes, the best encoders agree with each LLM per label (macro-F1 78) as well as the two LLMs agree with each other (77.5).
   - The weakest labels (science and technology, global partnerships, civil society) are those the LLMs also disagree on.
   - Most methods and small regions are too rare in a 900-excerpt test set to measure.
   - Details: [02 conclusion](02-fine-tuning/README.md#conclusion).
8. **What it means for decision models.** For a fixed, high-volume task with LLM labels to train on, a fine-tuned small general encoder beats zero-shot decision models. The one decision-model backbone fine-tuned here did no better than general encoders. Without training data, zero-shot decision models remain the option (not tested beyond this task).

## Layout

```
experiments/
  README.md                  this index
  common/                    shared across experiments
    README.md                conventions: run metadata, results format
    datasets.md              dataset registry with licences
    metrics.md               metric definitions
  <nn>-<slug>/
    README.md                plan, then results and conclusions
    pyproject.toml           pinned dependencies (added when the experiment starts)
    results/                 metrics and summaries (raw predictions gitignored)
```

- Anything used by two or more experiments goes in `common/`: dataset loaders, clients, metric code and docs.
- Code in an experiment folder is specific to that experiment.
- Background research lives in [../docs/](../docs/README.md). Experiments link to it rather than copying it.

# Experiments

The maintainer picks which experiment runs next; see [AGENTS.md](../AGENTS.md).

| # | Experiment | Status | Question |
|---|---|---|---|
| 01 | [Many-option classification](01-many-option-classification/) | planned | Can decision models and small encoders tag and classify international development evaluation reports as well as LLMs, with the context production uses (3–250 labels)? Phase 1: excerpt tagging, starting with a context pilot. |
| 02 | [Fine-tuning decision models](02-fine-tuning/) | running | What is the smallest model, by compute per excerpt, that reaches 01's LLM range on excerpt tagging (with production context) after fine-tuning, and with how many labels? |
| 03 | [Jev vs open models on document tasks](03-jev-vs-open-document-tasks/) | done (LlamaIndex) | How do Jev, Qwen3.5-4B, Laya, jeff and specialised tools compare on language, orientation, classification, splitting and parse triage of PDFs? |

Statuses: `proposed` → `planned` (plan approved) → `running` → `done`.

Experiment 03 is [LlamaIndex's `jev_vs_oss`](https://github.com/run-llama/jev_vs_oss) (MIT), copied with credit; its results are theirs.

## The story so far

For outside readers; each step links to the experiment README with the numbers.

1. **The task.** EvalExplorer's ingestion pipeline uses a large LLM to tag excerpts of evaluation reports with themes (22), regions (17), countries (198) and methods (24), with document context in view. Can a much smaller model do it?
2. **Context decides the answer.** Tagged alone, an excerpt rarely says which country it is about. Adding the report's title, first 100 words and executive summary raises agreement with the pipeline from 44 to 68; adding the whole section lowers it ([01 context pilot](01-many-option-classification/README.md#pilot-result)).
3. **The bar.** No human gold set exists. Two LLMs (GLM-5.3-Flash, DeepSeek-V4.1-Flash) given that context agree at 88.8 micro-F1; a model at that level agrees with each LLM as much as they agree with each other ([01 reference](01-many-option-classification/README.md#reference-labels-result)).
4. **Geography is mostly a lookup.** Matching country names in the excerpt, title and first 100 words scores 71.6 on countries and 74.7 on regions with no model at all ([01 lookup](01-many-option-classification/README.md#country-lookup-baseline)).
5. **Zero-shot decision models** (Jev, d1, GLiDE, GLiNER2.5-Decide, Kev, Laya, Verdict): to be rerun with the chosen context.
6. **Fine-tuned small encoders** (trained on 10,000 LLM-labelled excerpts) reach 75.3 against the LLMs' 88.8 when countries come from the lookup; a 32M-parameter encoder reaches 74.7. Themes come within 2 points of the LLMs; methods are furthest ([02 results](02-fine-tuning/README.md#first-step-encoder-sweep)).
7. **What to deploy:** after 5 and 6.

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

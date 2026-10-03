# Experiments

The maintainer picks which experiment runs next; see [AGENTS.md](../AGENTS.md).

| # | Experiment | Status | Question |
|---|---|---|---|
| 01 | [Many-option classification](01-many-option-classification/) | planned | Can zero-shot decision models classify and tag international development evaluation reports (3–250 labels, ~50-token excerpts and ~2,000-token first pages) as well as LLMs? Phase 1: excerpt tagging. |
| 02 | [Fine-tuning decision models](02-fine-tuning/) | proposed | Does a fine-tuned decision model reach the LLM range from 01 and match fine-tuned small LLMs (77–80 against GLM labels), and with how many labels? |
| 03 | [Jev vs open models on document tasks](03-jev-vs-open-document-tasks/) | done (LlamaIndex) | How do Jev, Qwen3.5-4B, Laya, jeff and specialised tools compare on language, orientation, classification, splitting and parse triage of PDFs? |

Statuses: `proposed` → `planned` (plan approved) → `running` → `done`.

Experiment 03 is [LlamaIndex's `jev_vs_oss`](https://github.com/run-llama/jev_vs_oss) (MIT), copied with credit; its results are theirs.

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

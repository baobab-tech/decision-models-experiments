# Experiments

The maintainer picks which experiment runs next; see [AGENTS.md](../AGENTS.md).

| # | Experiment | Status | Question |
|---|---|---|---|
| 01 | [Many-option classification](01-many-option-classification/) | proposed | Do decision models hold up at 10–200+ labels, multi-label tags and document types, on ~100 and ~2,000-token inputs? |
| 02 | [Fine-tuning decision models](02-fine-tuning/) | proposed | Which models can we fine-tune, how many labels does it take to beat zero-shot, and on what hardware? |

Statuses: `proposed` → `planned` (plan approved) → `running` → `done`.

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

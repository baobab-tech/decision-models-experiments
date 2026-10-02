# 02 Fine-tuning decision models

**Status:** proposed. Nothing runs until the plan is approved.

## Question

Which decision models can we fine-tune, and how? How many labelled examples does it take to beat zero-shot, and on what hardware? Background is in [fine-tuning.md](../../docs/fine-tuning.md).

## What the research says

- Jev and d1 cannot be fine-tuned. They can only be used as teachers to generate labels.
- GLiNER2.5-Decide supports full and LoRA fine-tuning. Training runs on CUDA or CPU only, so on this Mac it trains on CPU.
- Kev, the Qwen-based heads and the Laya family can be fine-tuned. Recipes and hardware needs are in [fine-tuning.md](../../docs/fine-tuning.md).
- A published cost reference: [ModernJEV-Decide-Preview](../../docs/models/modernjev-decide.md#fine-tuning) trained ModernBERT-base on 60,000 agent decisions in 129.8 min on one A100 (about $5.41 on HF Jobs). It reached 62.18% on 542 tool-selection test cases vs a 22.88% frequency baseline, and fell below the majority baseline on an untrained task family.

## Variables

- Model: GLiNER2.5-Decide, Laya, a small Kev or Qwen-head model.
- Method: full fine-tune or LoRA.
- Labelled examples per class: 0, 8, 32, 128, all.
- Where training runs: this Mac (CPU, MPS or MLX) or a cloud GPU (HF Jobs).

## Data

The same datasets as [01](../01-many-option-classification/), so zero-shot and fine-tuned results can be compared directly. See [common/datasets.md](../common/datasets.md).

## Metrics

- The metrics from [common/metrics.md](../common/metrics.md).
- Training time and cost.
- Accuracy on data from a different source than the training set.
- Whether other question types degrade after fine-tuning.

## Data governance

Fine-tune on this Mac or on EU infrastructure. Record where each training run happened.

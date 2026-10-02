# Laya (Convai Innovations)

| Field | Value |
|---|---|
| Vendor | Convai Innovations (author Nandha Kishor M); Node port by receptron |
| Type | Encoder decision model: probabilities for typed questions (Choice, Score, Noul) in one forward pass, no generated text |
| Backbone | ModernBERT-large (395M) for `laya` and `laya-typed-decisions`; mmBERT-base (307M) for `laya-multilingual`; plus a 2-layer decision head trained from scratch |
| Size | 421M (`laya`, `laya-typed-decisions`); 322M (`laya-multilingual`). Weights 843 MB and 644 MB (safetensors) |
| Licence | Apache-2.0 (weights, PyPI `laya`); MIT (npm `@receptron/laya` code) |
| Run it via | Self-hosted only: `pip install laya` (PyTorch: CUDA, MPS, XPU, CPU), `laya[onnx]`, `laya-serve` (`POST /v1/systemone`), npm `@receptron/laya` (ONNX Runtime, Node 20+). No hosted API; a public demo Space runs on HF ZeroGPU |
| Status | Released 2026-09-18 (HF repo created, PyPI 0.1.0). Runtime `laya` 0.3.23 (2026-10-01); checkpoints last changed 2026-09-24 |

Checked 2026-10-02.

## Overview

Laya takes a `state` (text or JSON) and named typed questions and returns one answer per question, with a probability for every option.
All questions in a call share one encoder forward pass.
Each option is scored at its own `[MASK]` marker, then softmaxed within its question, so the option set is defined per request ([card](https://huggingface.co/convaiinnovations/laya)).
Training uses RLCD: REINFORCE with a group-mean baseline against strictly proper scoring rules (log, spherical, ranked probability score for ordinal questions).
The training data for the two base checkpoints is not listed on the cards or the GitHub README (unverified).

Three checkpoints live in one repo, `convaiinnovations/laya`: English at the root, `multilingual/` and `typed-decisions/` as subfolders. The last two also have their own repos.

| Checkpoint | Encoder | Params | Default context | Use |
|---|---|---|---|---|
| `laya` | ModernBERT-large | 421M | 512 | English |
| `laya-multilingual` | mmBERT-base | 322M | 1,024 (up to 8,192 with `max_len=8192`) | 100+ languages |
| `laya-typed-decisions` | ModernBERT-large | 421M | 1,024 | the four `LocalLLaMA/typed-decisions` workflows |

The `Router` picks a checkpoint from the input script and language before the forward pass (under 0.5 ms).
It never picks `laya-typed-decisions` unless built with `auto_task_detection=True`.
The cards describe Laya as "a fast base to specialise, not a zero-shot decision engine".

| Repo | Revision | Downloads (30 d) | Likes | Created |
|---|---|---:|---:|---|
| [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya) | `55cf4c4` | 0 (no root `config.json`) | 4,915 | 2026-09-18 |
| [`convaiinnovations/laya-multilingual`](https://huggingface.co/convaiinnovations/laya-multilingual) | `e4e9ddf` | 0 | 354 | 2026-09-19 |
| [`convaiinnovations/laya-typed-decisions`](https://huggingface.co/convaiinnovations/laya-typed-decisions) | `1a793eb` | 0 | 141 | 2026-09-18 |
| [`receptron/laya-onnx`](https://huggingface.co/receptron/laya-onnx) (fp32 ONNX of `laya`) | `68f27df` | 0 | 5 | 2026-09-19 |
| npm [`@receptron/laya`](https://www.npmjs.com/package/@receptron/laya) 0.1.2 | n/a | 9,980 (September 2026) | n/a | 2026-09-19 |

HF API and npm registry, read 2026-10-02.

## Schema

`laya-serve` serves `POST /v1/systemone` "on the same … request and response shape as TypeSafe Jev" ([card](https://huggingface.co/convaiinnovations/laya)).
It accepts `criteria` as a list, ignores unknown fields, and returns `422` for a malformed question.
Answers carry `choice` / `score` / `noul` plus `usage` `{input_tokens, output_tokens}` ([GitHub README](https://github.com/NandhaKishorM/laya#self-hosting-http-server-jev-compatible)).

- **Choice:** `criteria` map; returns `choice`, `probabilities`, `confidence`.
- **Score:** ordered level list; returns `score` as the expected level, the distribution and `confidence`. Every level needs a description; a `null` level returns `422`.
- **Noul:** returns `noul` = P(true). Optional `labels` `{"false": …, "true": …}` changes the text the model sees without changing the meaning of the output.
- **Extra fields per request:** `model` (`english` / `multilingual` / `typed-decisions`), `task`, `lang`, `lang_guess`, `min_confidence`, `max_len`, `head_max_len`, and `option_order` per question.
- **Batch:** `POST /v1/systemone/batch` takes a `states` array, up to 64 states, and returns `results` plus `total_usage`.
- **Not sent over HTTP:** hook arguments (`hooks`, `on_predict_start`, …) return `422`.

Differences from Jev (GitHub README):

| Jev | Laya |
|---|---|
| Up to 255 options | Options share a `head_max_len` budget (192 tokens `laya`, 256 others); `laya-serve` rejects more than 100 Choice options with `413` |
| Choice `confidence` = (n·p_max − 1)/(n − 1) | `confidence` = 1 − normalised entropy; `answer_confidence` = probability of the reported answer |
| Hosted, US | Local only |

A threshold set on Jev does not transfer to Laya ([#394](https://github.com/NandhaKishorM/laya/issues/394)).
The npm package matches the Python `RLAgent.system_one` output to four decimals ([receptron README](https://github.com/receptron/laya)).

## Benchmarks

### Author's numbers

From the [card](https://huggingface.co/convaiinnovations/laya) and [GitHub README](https://github.com/NandhaKishorM/laya#benchmarks), on a Tesla T4. Jev figures there are third-party published numbers, not measured by the author.

| Benchmark | `laya` | `laya-multilingual` | `laya-typed-decisions` | Jev 1.13.0 (published) |
|---|---:|---:|---:|---:|
| typed-decisions, 2,000 decisions, accuracy | 0.362 | 0.342 | 0.766 | 0.727 |
| typed-decisions, soft accuracy | 0.332 | 0.326 | 0.471 | 0.580 |
| typed-decisions, Brier | 0.316 | 0.439 | 0.062 | 0.148 |
| typed-decisions, ECE | 0.175 | 0.285 | 0.213 | 0.144 |
| MASSIVE intent, 51 languages, 20 options, macro accuracy | 0.227 | 0.366 | n/r | n/r |
| Languages above 3× random (of 51) | 23 | 45 | n/r | n/r |
| XNLI English / 14 other languages | 0.860 / 0.521 | 0.843 / 0.731 | n/r | n/r |

- Routed Laya against Jev (card): AG News 0.950 vs 0.910; DAIR Emotion 0.595 vs 0.480; Banking77 0.425 (77 labels) vs 0.870 (72 labels).
- ECE 0.081 for `laya` after refitting one temperature per (question type, option count); 0.466 before. `laya-multilingual`: 0.314 → 0.106.
- typed-decisions random baseline 0.318; majority class 0.461; teacher self-agreement 0.735. `laya-typed-decisions` was fine-tuned on that benchmark's 1,200-case train split.
- The README says the `laya-typed-decisions` row "has no committed result file behind it yet".
- Latency, T4: 1 question 39.5 ms (`laya`) and 32.8 ms (`laya-multilingual`); 10 questions 158.6 ms and 72.3 ms; 50 questions 771 ms and 337 ms.

### Third-party boards

| Board | Run | Result | Source |
|---|---|---|---|
| Jev Decision Index 0.2.1 | `laya` (runtime 0.3.11), RTX PRO 6000 | balanced skill 6.04 (Jev 57.91), rank 61 of 70; ECE 0.140; median 5.8 ms; coverage 0.759 | [index.json](https://huggingface.co/spaces/multimodalart/jev-decision-index) (generated 2026-09-28); [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021) |
| JevBench v1.5.4 | `laya` / `laya-multilingual` / `laya-typed-decisions`, local CPU | score 0.0 / 0.0 / 0.0 (ranks 93, 86, 106 of 109); intelligence 0.0 / 2.4 / 0.0 | [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#jevbench-v154-headline-a) |
| typed-decision-bench (kyr0), 22,001 test cases | `laya`, H200 | soft accuracy 46.70%, hard 52.55%, ECE 0.278, p50 36.7 ms (Jev 88.08%, 93.41%, 0.084) | [benchmarks.md](../benchmarks.md#typed-decision-bench-kyr0-275-capabilities) |
| typed-decision-bench (4nt0ineB), 60 MASSIVE intents | Laya router / multilingual | EN_EN 45% / 42%; FR_FR 31% / 35% (Jev 85%, 84%); automatable 0% | [benchmarks.md](../benchmarks.md#typed-decision-bench-4nt0ineb-60-intents-enfr) |
| Fastino fast-decisions, 17 domains | Laya Router | 46.6% (GLiNER2.5-Decide 60.2%, JevK5 57.6%) | [dataset card](https://huggingface.co/datasets/fastino/fast-decisions) |
| decision-models-under-pressure | Laya | 128 options: 39% (Jev 60%); option-order sensitivity 49.4% (Jev 14.6%) | [gazelle93](https://github.com/gazelle93/decision-models-under-pressure), via [benchmarks.md](../benchmarks.md) |

Laya's JevBench 0.0 scores come from the score's gates, not from zero correct answers; the calibration axes read 73.7 (`laya`) and 83.3 (`laya-typed-decisions`).

### Experiment 03 (LlamaIndex document tasks)

[Experiment 03](../../experiments/03-jev-vs-open-document-tasks/README.md) records LlamaIndex's run of `jev_vs_oss` (commit `0a3726f`, 2026-09-24), not re-run here.
It used the `typed-decisions` checkpoint with `max_len=2048` and `head_max_len=512`, on MPS on an Apple Silicon Mac.

| Task | n | Laya | Jev | Qwen3.5-4B (SemIf-style) |
|---|---:|---:|---:|---:|
| Language, Choice(12) | 48 | 39.6% | 100.0% | 100.0% |
| Orientation, Choice(4) | 32 | 28.1% | 93.8% | 90.6% |
| RVL-CDIP classify, Choice(16) | 96 | 24.0% | 54.2% | 51.0% |
| Page split, Choice(2) | 82 | 70.7% | 96.3% | 87.8% |
| Triage, Choice(2) | 48 | 52.1% | 85.4% | 95.8% |

- Laya ranked below Jev and Qwen3.5-4B on all five tasks.
- Laya had the lowest p50 latency of the three models on four tasks and tied Jev on classify (0.14 s); range 0.09–0.20 s.
- Split F1 0.586 (Jev 0.947).
- On classify at confidence ≥ 0.9, Laya kept 4.2% of pages at 75.0% accuracy; Jev kept 45.8% at 81.8%.
- Laya's confidence on the first 10 wrong orientation answers was 0.003–0.034.
- It logged a warning that its `choice:11+` temperatures were clamped. The shipped `rl_agent_config.json` sets `choice:11+` to 0.1006.
- The classify state (2,500 characters) exceeds the 512–1,024 tokens Laya was trained on; upstream raised the budgets to fit.

## Running it

Mac path (M5 Max, 128 GB): PyTorch on MPS through `pip install laya`, ONNX Runtime on CPU through `laya[onnx]` or `@receptron/laya`. A 4,000-token input takes about 1.7 s "on an Apple GPU" (card). Eight English tickets one by one took 2,624 ms on MPS (README).

1. Install into a uv environment ([installation](https://github.com/NandhaKishorM/laya#installation-details)):

```bash
uv venv --python 3.12
uv pip install laya
```

2. Call the Router ([card](https://huggingface.co/convaiinnovations/laya)):

```python
from laya import Router

router = Router()  # downloads a checkpoint on first use
state = "Hi, we were billed twice for March. Please refund the duplicate today or we will cancel our plan."
questions = {
    "department": {"type": "choice", "instructions": "Which department should handle this?",
                   "criteria": {"billing": "invoices, payments, refunds",
                                "technical": "bugs, outages, system errors",
                                "other": "everything else"}},
    "urgency": {"type": "score", "instructions": "How urgent is this?",
                "criteria": ["not urgent", "soon", "blocking"]},
    "churn_risk": {"type": "noul", "instructions": "Does the user threaten to cancel or leave?"},
}
result = router.predict(state, questions)
print(result["answers"]["department"]["choice"], result["routing"]["model"])  # billing english
```

3. Or run the TypeSafe-shaped server on loopback with a key:

```bash
uv pip install "laya[serve]"
LAYA_HOST=127.0.0.1 LAYA_API_KEY=... LAYA_PRELOAD=1 laya-serve   # port 8000
```

4. Node 22, no Python ([receptron README](https://github.com/receptron/laya)):

```ts
import { Laya } from "@receptron/laya";
const laya = await Laya.load({ revision: "68f27df" }); // ~1.7 GB fp32, cached in ~/.cache/receptron-laya
const result = await laya.systemOne(state, questions);
```

Three questions take about 140 ms on an Apple Silicon CPU once warm.

- Set `USE_TF=0` if `laya.load()` hangs; TensorFlow's import can deadlock model construction.
- LangChain's default thread pool "races on MPS, where concurrent torch forwards abort the process"; the integration batches instead (README).
- Routing alone (`laya "text"` with no `--predict`) works offline and downloads nothing.
- Community Apple runtimes: [`tc3oliver/laya-apple`](https://github.com/tc3oliver/laya-apple) (MLX GPU and Neural Engine), listed in the README. Others in the all-about-jev dataset (`laya-mlx`, `laya-coreml`, `laya-mps`, `laya.cpp`) are unverified.

## Scaling limits

- **Options:** keep Choice under about 20 options (card). Options share `head_max_len`: 192 tokens on `laya`, 256 on the others. At 77 options each label gets 3–4 tokens; Banking77 scores 0.425.
- **Hard cap:** `laya-serve` rejects more than 100 Choice options (`MAX_CHOICE_OPTIONS = 100`, `413`). The library returns `422` when options no longer fit the window.
- **More options:** raise `head_max_len` to 512 and `max_len` to 1,024–8,192 per request, shortlist with `laya.predict_shortlist(k=20)`, or split into coarse and fine questions. Issue [#102](https://github.com/NandhaKishorM/laya/issues/102) reports a top-20 shortlist moving BANKING77 from 54.3% to 60.8% (reporter's figures).
- **Context:** 512 tokens (`laya`), 1,024 (`laya-multilingual`, `laya-typed-decisions`). `laya-multilingual` reads up to 8,192 with `max_len=8192`; 16–18 of 20 requests were right up to about 4,000 tokens, and 8–17 of 20 beyond that. The state gets `max_len − head_len − 1` tokens; for 100 options on `laya` that is 100 tokens.
- **Long documents:** `predict_long` slides windows over the state and aggregates.
- **Questions per call:** one forward pass for all questions; 50 questions take 337–771 ms on a T4.
- **Batching:** `predict_batch` and `/v1/systemone/batch` (64 states).
- **Option order:** on five identical options the English checkpoint's per-slot logits run from +1.68 to −1.91 by position alone. Averaging over rotations (`option_order`) cut order-dependent answers from 16.3% to 6.1% on 62 banking intents (README).

## Fine-tuning

- **Kaggle:** [`laya_finetune_typed_decisions_2xT4_kaggle.ipynb`](https://github.com/NandhaKishorM/laya/blob/main/notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb) builds the dataset, trains with RLCD, fits temperatures, evaluates and pushes to the Hub. About 4–5 h for 4 epochs over ~30k questions on 2×T4.
- **Apple Silicon:** [`laya_finetune_typed_decisions_mps.py`](https://github.com/NandhaKishorM/laya/blob/main/notebooks/laya_finetune_typed_decisions_mps.py) trains single-process on MPS with CPU fallback, e.g. `--micro-batch 1 --grad-accum 32` on a 16 GB MacBook. No timing is published.
- Full encoder plus head are trained; gradient checkpointing via `model.head_checkpointing = True`.
- `laya-typed-decisions`: fine-tuned from `laya` on 6,000 decisions, RLCD plus soft cross-entropy against teacher distributions.
- The notebook's calibration samples come from its training items. The README says to evaluate on held-out data before claiming a gain.
- Third-party: [`cklxx/laya-browser`](https://huggingface.co/cklxx/laya-browser) browser-agent head (element top-1 of ~45 from 0.10 to 0.66, one 16 GB GPU); [`stuntd`](https://github.com/bladedevoff/stuntd) trains a head per decision on the frozen encoder (README, unverified).

## Data governance

Not legal advice. Laya has no vendor API; every row below is for self-hosting on your own infrastructure.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; air-gapped once the checkpoint is in the HF cache (`HF_HUB_CACHE`) | [GitHub README](https://github.com/NandhaKishorM/laya#installation-details) |
| Fine-tuning | Yes, on your hardware (CUDA notebook, MPS script) | [GitHub README](https://github.com/NandhaKishorM/laya#fine-tuning) |
| Processing location | Your infrastructure. The public [demo Space](https://huggingface.co/spaces/convaiinnovations/laya-demo) runs on HF ZeroGPU (A10G); its region is not stated | HF API, 2026-10-02 |
| EU processing option | Self-host in the EU. HF Inference Endpoints `eu-west-1` needs a custom handler for the `Router` (see [open-reproductions.md](open-reproductions.md#data-governance)) | |
| Retention / ZDR | No retention by the library. `laya-serve` logging behaviour is not documented (unverified) | |
| Training on inputs | No; inference is local | |
| DPA / GDPR | Not applicable when self-hosted: no processor | |
| Certifications | None (open-source project) | |
| Network exposure | `laya-serve` binds `0.0.0.0` with no auth unless `LAYA_API_KEY` is set | [card](https://huggingface.co/convaiinnovations/laya) |
| Weights licence | Apache-2.0 (all three checkpoints, `cardData`); npm code MIT; ONNX export weights stay Apache-2.0 | HF API; [receptron/laya-onnx](https://huggingface.co/receptron/laya-onnx) |
| Training data | Base checkpoints: not disclosed (unverified). `laya-typed-decisions`: `LocalLLaMA/typed-decisions` train split (Apache-2.0), labelled by an unnamed "roughly 4B-class" teacher | [dataset card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) |

- The repo root executes `rl_common.py` and `rl_agent_api.py` from the checkpoint at load; pin a revision.
- The root repo's `main` has moved (JevBench ran `laya@1c5edc1`; today's `main` is `55cf4c4`).

## Caveats

- Base checkpoints score near chance on typed-decisions zero-shot (0.362, 0.342 vs 0.318 random); the 0.766 needs fine-tuning on that benchmark's train split.
- Every third-party general-decision board puts Laya far below Jev: DI 6.04 vs 57.91, kyr0 46.70% vs 88.08%, 4nt0ineB 45% vs 85%, exp. 03 24.0–70.7% vs 54.2–100%.
- Ships over-confident; refit temperatures on held-out data at the option counts you use. `laya-multilingual` ships with no fitted temperatures. `laya-typed-decisions` inherits `temperature_by_options` from the base and its per-type temperatures were fitted on training items ([#186](https://github.com/NandhaKishorM/laya/issues/186)).
- The English checkpoint fails on non-Latin scripts while staying confident: Khmer 0.000 accuracy at 0.952 confidence. Use the Router.
- `noul` can follow its `false:` / `true:` labels instead of the state ([#156](https://github.com/NandhaKishorM/laya/issues/156)).
- Negated cancellation requests chose `cancel_account` in 4 of 4 cases on `laya` ([#377](https://github.com/NandhaKishorM/laya/issues/377)).
- `action.act_probability` "carries no usable signal yet" (AUROC 0.30; [#185](https://github.com/NandhaKishorM/laya/issues/185)).
- `laya-multilingual` rarely picks the first Score level: 0 of 290 in one run ([#131](https://github.com/NandhaKishorM/laya/issues/131)).
- Score is the weakest primitive: SST-5 0.372 (`laya`), 0.282 (`laya-multilingual`).
- The author's Jev comparisons use third-party Jev numbers with different samples and prompts.

## Sources

- Model cards: [`convaiinnovations/laya`](https://huggingface.co/convaiinnovations/laya/raw/main/README.md), [`laya-multilingual`](https://huggingface.co/convaiinnovations/laya-multilingual/raw/main/README.md), [`laya-typed-decisions`](https://huggingface.co/convaiinnovations/laya-typed-decisions/raw/main/README.md), [`receptron/laya-onnx`](https://huggingface.co/receptron/laya-onnx/raw/main/README.md); [`rl_agent_config.json`](https://huggingface.co/convaiinnovations/laya/raw/main/rl_agent_config.json); [`eval/results.md`](https://huggingface.co/convaiinnovations/laya/raw/main/eval/results.md).
- HF API: `https://huggingface.co/api/models/<repo>` for the four repos above and `api/spaces/convaiinnovations/laya-demo`.
- GitHub: [`NandhaKishorM/laya` README](https://github.com/NandhaKishorM/laya) (runtime 0.3.23) and LICENSE; [`receptron/laya` README](https://github.com/receptron/laya).
- Package registries: [PyPI `laya`](https://pypi.org/project/laya/) (0.3.23, 31 releases since 2026-09-18), [npm `@receptron/laya`](https://registry.npmjs.org/@receptron/laya), [npm downloads API](https://api.npmjs.org/downloads/point/last-month/@receptron/laya).
- Benchmarks: [Decision Index `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index) (generated 2026-09-28), [fastino/fast-decisions](https://huggingface.co/datasets/fastino/fast-decisions), [LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions), [benchmarks.md](../benchmarks.md), [benchmarks-leaderboards.md](../benchmarks-leaderboards.md), [experiment 03](../../experiments/03-jev-vs-open-document-tasks/README.md).

All read 2026-10-02.

# Clef and Clef-flash (Cloudflare)

| Field | Value |
|---|---|
| Vendor | Cloudflare, Inc. (San Francisco); Workers AI team |
| Type | Decision model: probabilities for typed questions (Choice, Score, Noul), no generated text. Text, JSON, image and video input |
| Backbone | Clef: Qwen/Qwen3.8-27B. Clef-flash: Qwen/Qwen3.5-9B. Both with the Qwen vision encoder and a joint schema head |
| Size | Clef: 27,356,728,560 parameters (BF16). Clef-flash: 9,409,813,744 (BF16) |
| Licence | Apache-2.0, open weights, not gated |
| Run it via | Self-host from `Cloudflare/clef` / `Cloudflare/clef-flash` (custom Python loader); Workers AI `@cf/cloudflare/clef` and `@cf/cloudflare/clef-flash` |
| Status | HF repos created 2026-09-30; launch blog 2026-10-01 |

Checked 2026-10-02.

## Overview

Clef takes a `state` and named typed questions and returns a probability for every option of every question in one forward pass ([Clef card](https://huggingface.co/Cloudflare/clef)).
The backbone runs a prefill-only pass; a joint schema head then scores all options of all questions ([blog](https://blog.cloudflare.com/clef-decision-models/)).
The head routes evidence from the state to each option, lets fields cross-attend, and outputs one logit per option.
The card's release head is 4 layers, 2 routing layers, width 1,024, 16 heads (`joint_head_config.json`).
Training froze the backbone and fit the routing head with rank-256 LoRA adapters, using label-smoothed cross-entropy plus a Brier loss on Cloudflare's internal synthetic data ([blog](https://blog.cloudflare.com/clef-decision-models/)).
A second stage, "Reinforcement Learning for Calibrated Decisions (RLCD)", gives partial credit to adjacent ordinal choices and adds a reference penalty.
The published weights are a merged backbone plus `joint_head.safetensors`.
Clef-flash is the 9B variant with the same head design and the same loader code (`joint_schema_model.py` files are byte-identical).
The card states "The Clef API is fully compatible with Jev and SystemOne."

HF metadata, read 2026-10-02 ([API](https://huggingface.co/api/models/Cloudflare/clef)):

| Repo | Revision | Downloads (30 days) | Likes | Last modified |
|---|---|---:|---:|---|
| `Cloudflare/clef` | `2f3de3d` | 824 | 600 | 2026-10-01 |
| `Cloudflare/clef-flash` | `17f0b0a` | 1,303 | 201 | 2026-10-01 |

## Schema

Same structure as TypeSafe: `model` + `state` + `questions` → `answers` + `usage`.
The HF code's `systemone()` takes a `POST /v1/systemone` request body and returns the same response body.
Workers AI takes the same body at its own URL, not at `/v1/systemone` ([Workers AI model page](https://developers.cloudflare.com/workers-ai/models/clef/)).

- **Noul:** returns `noul` (probability of true). Optional `criteria` `{"true": …, "false": …}`.
- **Choice:** `criteria` map of option id to description; returns `choice`, `probabilities`, `confidence`.
- **Score:** `criteria` array, lowest first, indexed from 0; returns `score` (probability-weighted level), `legend`, `probabilities`, `confidence`.
- **Confidence:** the top probability, for both Choice and Score (`systemone_answer` in `joint_schema_model.py`). Jev uses a different Choice formula; re-tune thresholds set for Jev.
- **Images and video:** a Clef extension. HF code takes PIL images and video frame arrays; Workers AI takes up to 4 base64 PNG, JPEG or WebP images, no remote URLs, no video field in the schema.
- `usage.output_tokens` is 0 in the HF code.

Differences between the two entry points:

| Item | HF `systemone()` | Workers AI |
|---|---|---|
| `instructions` | optional; the question id is used when empty | required, non-empty |
| Choice options | no cap in code | 2–255 |
| Score levels | no cap in code | 2–10 |
| Questions | no cap in code | 1–64; ids up to 100 characters |
| `model` | any string, echoed | must be `clef` or `clef-flash` |
| Input window | `max_length` 16,384 tokens by default | 65,536-token context |

Source: [input schema](https://developers.cloudflare.com/workers-ai/models/clef/schema-input.json), [output schema](https://developers.cloudflare.com/workers-ai/models/clef/schema-output.json), [`joint_schema_model.py`](https://huggingface.co/Cloudflare/clef/blob/main/joint_schema_model.py).

## Benchmarks

Decision Index 0.2.1, Cloudflare's own run ([leaderboard data](https://clef-evals.workers-ai-mle.workers.dev/data/leaderboard.json), generated 2026-10-01; marked `self_reported`). HLE and iSarcasmEval were not run (36 of 38 index benchmarks). The public board's `data/index.json` (generated 2026-09-28) has no Clef row, checked 2026-10-02.

| Measure | Clef | Clef-flash | Jev 1.13.0 (board) |
|---|---:|---:|---:|
| Decision Index 0.2.1, balanced skill | 61.21 | 57.07 | 57.91 |
| Tools and Automation (skill) | 81.2 | 82.0 | 75.1 |
| Knowledge and Reasoning (skill) | 51.2 | 50.4 | 51.4 |
| BANKING77 macro-F1 | 94.2 | 90.9 | 79.7 |
| CLINC150+OOS macro-F1 | 97.4 | 66.8 | 89.3 |
| GPQA Diamond accuracy | 48.0 | 51.0 | 78.3 |
| MMLU-Pro accuracy | 65.9 | 65.3 | 82.7 |
| Median / p95 latency (ms) | 209.3 / 238.6 | 38.8 / 122.4 | 524.1 / 536.0 |

- Cloudflare's latency rows are its own; hardware for the Clef rows is not stated. Jev's numbers match the board (RTX PRO 6000 harness, Jev over HTTPS).
- The card lists all 41 per-benchmark scores against Jev, a DiffusionGemma Jev, Kev 9B and Laya ([card](https://huggingface.co/Cloudflare/clef#results)).
- Workflow evals ([Typesafe Evals](https://evals.typesafe.ai/), consensus labels, Cloudflare's run): invoice exact actions Clef 64.7, Clef-flash 57.1, Jev 61.8; customer service 76.3 / 77.0 / 76.0; security incidents 62.9 / 61.7 / 61.7; agent trace observability 68.5 / 69.8 / 71.6.

JevBench v1.5.5 ([board](https://benchmarkheaven.com/jev-models), [aggregate JSON](https://benchmarkheaven.com/api/jevbench/v1.5.5), 109 ranked systems, last measured 2026-10-02, independent run):

| Measure | Clef | Clef-flash | Jev 1.13.0 |
|---|---:|---:|---:|
| JevBench Score (headline A) | 17.0 (#62) | 55.1 (#25) | 72.1 (#3) |
| Intelligence | 67.9 | 53.1 | 72.0 |
| Calibration | 86.7 | 87.6 | 88.0 |
| Speed | 79.9 | 83.6 | 83.8 |
| Cost | 28.1 | 46.8 | 54.7 |
| Capability Score (Intelligence and Calibration) | 77.3 | 70.3 | 80.0 |
| Raw p50 / p95 latency (s) | 0.358 / 0.521 | 0.200 / 0.319 | 0.616 / 0.674 |
| $ per 1,000 decisions (estimate) | 0.249 | 0.059 | 0.032 |

- JevBench ran both models on one H100 80GB pod (US), offline, pinned to the HF revisions above. Self-hosted latency is scored at ×2 + 0.15 s.
- Clef's cost axis (28.1) is below the gate of 50, which pulls its headline down ([benchmarks.md](../benchmarks.md#jevbench)). The Capability view puts it outside the Jev class: cost 7.7× Jev against a 2× cap.
- A price-only scenario at Workers AI list prices scores Clef 29.9 and Clef-flash 59.0. JevBench did not measure Workers AI latency.
- Clef-flash's open-item Intelligence is 58.9 and sealed is 47.3, a gap of 11.5 points; Clef's gap is 0.4.
- Community MLX check on a 2,000-request DI sample (M5 Max): Clef 4-bit 57.02 vs 8-bit 57.96; Clef-flash 4-bit 54.65 vs bf16 55.63 ([mlx-community/clef-4bit](https://huggingface.co/mlx-community/clef-4bit), [clef-flash-4bit](https://huggingface.co/mlx-community/clef-flash-4bit)).

## Running it

**Workers AI (hosted).**

1. Create a Cloudflare account and an API token with Workers AI access. Put `CLOUDFLARE_ACCOUNT_ID` and `CLOUDFLARE_AUTH_TOKEN` in `.env`.
2. Call the model ([model page](https://developers.cloudflare.com/workers-ai/models/clef/)):

```bash
curl https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai/run/@cf/cloudflare/clef \
  -X POST -H "Authorization: Bearer $CLOUDFLARE_AUTH_TOKEN" \
  -d '{"model": "clef",
       "state": "Checkout has been failing for every customer for the last hour.",
       "questions": {
         "urgent": {"type": "noul", "instructions": "Is this support request urgent?"},
         "team": {"type": "choice", "instructions": "Which team should handle this request?",
                  "criteria": {"billing": "Payments, invoices, and refunds", "technical": "Outages, errors, and configuration", "sales": "Plans and upgrades"}},
         "severity": {"type": "score", "instructions": "How severe is the customer impact?",
                      "criteria": ["No impact", "Minor", "Major", "Critical"]}}}'
```

For Clef-flash, use `@cf/cloudflare/clef-flash` and `"model": "clef-flash"`. From a Worker, call `env.AI.run("@cf/cloudflare/clef", {...})`.

- Price: Clef $0.24 per 1M input tokens (21,818 neurons); Clef-flash $0.09 (8,182 neurons). No output price listed ([pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/), updated 2026-10-01).
- Free allocation: 10,000 neurons per day on Free and Paid plans. That is about 458,000 Clef or 1.22M Clef-flash input tokens per day (inferred from the neuron rates).
- A 1,000-token request costs $0.00024 on Clef and $0.00009 on Clef-flash.
- The blog says requests run on Cloudflare GPUs "at the edge". No Workers AI latency figures are published.

**Self-host (PyTorch, CUDA).** The card's tested setup is `torch` 2.11 and `transformers` 5.10.2 on one H200:

```python
import sys
from huggingface_hub import snapshot_download
path = snapshot_download("Cloudflare/clef-flash", revision="17f0b0a")
sys.path.insert(0, path)
from joint_schema_model import load_release_model, systemone
model, processor = load_release_model(path, device="cuda")
print(systemone(model, processor, {"model": "clef-flash", "state": "...", "questions": {...}})["answers"])
```

The loader imports Python from the repo, so pin a revision.

**Mac (M5 Max, 128 GB).**

- **MLX:** `mlx-community/clef-flash-4bit`, `clef-flash-8bit`, `clef-4bit`, `clef-8bit` ship `clef_mlx.py`, which runs the backbone and the joint head (`pip install mlx-vlm huggingface_hub`, no torch). Parity on an M5 Max: top answer agrees on 10/10 text questions and 9/9 image and video questions. Median latency on ~1k-token requests: Clef-flash 4-bit 311 ms; Clef 4-bit 1.03 s ([cards](https://huggingface.co/mlx-community/clef-flash-4bit)). Community conversions, not Cloudflare's.
- **PyTorch MPS:** `load_release_model(path, device="mps")` is not documented by Cloudflare (unverified). BF16 weights are about 55 GB for Clef and 19 GB for Clef-flash, so both fit in 128 GB. Qwen3.5 Gated DeltaNet layers have no MPS kernel in `flash-linear-attention` ([fine-tuning.md](../fine-tuning.md)), so expect a slow fallback (unverified).
- **GGUF / llama.cpp:** `bartowski/Cloudflare_clef-flash-GGUF` and `bartowski/Cloudflare_clef-GGUF` hold the backbone and mmproj only, without `joint_head.safetensors`. `llama-server` then runs a text-generating Qwen, not the decision model. Not a decision path.

## Scaling limits

- **Options:** Workers AI 2–255 per Choice, 2–10 per Score. The HF code sets no cap; each option adds its description tokens to the input.
- **Questions per call:** Workers AI 64. All questions are scored jointly in one pass, so questions can attend to each other.
- **Context:** Workers AI 65,536 tokens. HF code `max_length` 16,384 by default; long `state` is truncated to fit, and a schema longer than `max_length` raises an error.
- **Images:** Workers AI 4 per request, 4 MiB and 16 megapixels each, 8 MiB decoded in total, 13 MiB request body.
- **Rate limits:** the model page lists the task type as Text Generation, whose default is 300 requests per minute ([limits](https://developers.cloudflare.com/workers-ai/platform/limits/)) (inferred).
- **Cost:** a full 65,536-token Clef request costs about $0.016.

## Fine-tuning

- Cloudflare offers fine-tuning of Clef as a hands-on service with its forward-deployed engineer team, through an [interest form](https://www.cloudflare.com/resource/clef-rl-interest) ([blog](https://blog.cloudflare.com/clef-decision-models/)).
- A self-serve RL platform is announced, not shipped: AI Gateway captures traffic as a dataset, Workers AI generates rollouts, Containers host the RL sandbox, a new "Trainer" updates weights, and Workers AI Bring Your Own Model redeploys the result.
- The fine-tuning path stores your requests and responses; the blog's no-storage guarantee excludes it.
- Workers AI LoRA upload allows ranks up to 32 on listed base models ([LoRA docs](https://developers.cloudflare.com/workers-ai/features/fine-tunes/loras/)). Clef is not documented as a LoRA base (unverified).
- Self-hosted training: no training code is published. The weights are Apache-2.0, so you can train your own head or adapters.

## Data governance

Not legal advice. Self-hosted = your infrastructure; nothing leaves your machine. The rows below cover Workers AI.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes, Apache-2.0 weights on HF | [card](https://huggingface.co/Cloudflare/clef) |
| Fine-tuning | Hosted: FDE-led service now, self-serve later. Self-hosted: weights allow it, no recipe published | [blog](https://blog.cloudflare.com/clef-decision-models/) |
| Processing location | Cloudflare GPU data centres; region not selectable. Workers AI is "not compatible" with Regional Services | [DLS compatibility](https://developers.cloudflare.com/data-localization/compatibility/) (updated 2026-07-23) |
| EU processing option | No. Customer Metadata Boundary (logs and analytics) is compatible; inference location is not | same |
| Retention / ZDR | Customer Content is stored only if you use a storage product with Workers AI. Blog: "we don't read, store, or train on your requests or responses (unless you want to use our fine-tuning product)". If you route through AI Gateway, its logging settings apply (unverified) | [Workers AI data usage](https://developers.cloudflare.com/workers-ai/platform/data-usage/) (updated 2026-04-21), [blog](https://blog.cloudflare.com/clef-decision-models/) |
| Training on inputs | No, without explicit consent | [Workers AI data usage](https://developers.cloudflare.com/workers-ai/platform/data-usage/) |
| DPA / GDPR | Cloudflare Customer DPA v6.4 (effective 2026-04-03): EU SCCs (2021/914) and the EU-U.S. Data Privacy Framework | [DPA](https://www.cloudflare.com/cloudflare-customer-dpa/) |
| Certifications | Cloudflare publishes a compliance list; scope for Workers AI not checked (unverified) | [compliance resources](https://www.cloudflare.com/trust-hub/compliance-resources/) |
| Weights licence | Apache-2.0, following the Qwen base models | [card](https://huggingface.co/Cloudflare/clef#license) |

Workers AI has a DPA and does not train on inputs, but offers no EU-only inference. Send only public or synthetic data until the maintainer approves otherwise; for personal data, self-host.

## Caveats

- The Decision Index scores (61.21, 57.07) are Cloudflare's own run on 36 of 38 benchmarks, not a board entry. Fastino reports 64.81 for GLiDE from its own run ([glide.md](glide.md)), so the blog's "currently the leader" claim conflicts with another self-report.
- On JevBench, the only independent board, Clef-flash ranks 25th and Clef 62nd; both rank below Jev 1.13.0 (3rd). Clef's rank comes from its cost estimate, not its accuracy.
- Context differs by source: blog 64k, Workers AI 65,536 tokens, HF code 16,384 by default. Long state is truncated, not rejected.
- The Workers AI data usage page says "Cloudflare neither creates nor trains the AI models made available on Workers AI". That sentence predates Clef, which Cloudflare trained.
- Not documented: training data contents, calibration (ECE) figures, Workers AI latency, MPS support.
- The card's "fully compatible with Jev" claim is not tested here. `instructions` is optional in the HF code and required on Workers AI.

## Sources

- Cloudflare: [launch blog](https://blog.cloudflare.com/clef-decision-models/) (2026-10-01), [Clef evals site](https://clef-evals.workers-ai-mle.workers.dev) and its [`data/leaderboard.json`](https://clef-evals.workers-ai-mle.workers.dev/data/leaderboard.json), Workers AI [clef](https://developers.cloudflare.com/workers-ai/models/clef/) and [clef-flash](https://developers.cloudflare.com/workers-ai/models/clef-flash/) pages with input and output schemas, [pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/), [limits](https://developers.cloudflare.com/workers-ai/platform/limits/), [data usage](https://developers.cloudflare.com/workers-ai/platform/data-usage/), [LoRA docs](https://developers.cloudflare.com/workers-ai/features/fine-tunes/loras/), [DLS compatibility](https://developers.cloudflare.com/data-localization/compatibility/), [Customer DPA](https://www.cloudflare.com/cloudflare-customer-dpa/)
- Hugging Face: [Cloudflare/clef](https://huggingface.co/Cloudflare/clef) and [Cloudflare/clef-flash](https://huggingface.co/Cloudflare/clef-flash) (README, `config.json`, `joint_head_config.json`, `joint_schema_model.py`, HF API); [mlx-community/clef-flash-4bit](https://huggingface.co/mlx-community/clef-flash-4bit), [mlx-community/clef-4bit](https://huggingface.co/mlx-community/clef-4bit), [bartowski/Cloudflare_clef-flash-GGUF](https://huggingface.co/bartowski/Cloudflare_clef-flash-GGUF)
- [JevBench v1.5.5](https://benchmarkheaven.com/jev-models) and [aggregate JSON](https://benchmarkheaven.com/api/jevbench/v1.5.5)
- [Decision Index Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) (`data/index.json` generated 2026-09-28)

All read 2026-10-02.

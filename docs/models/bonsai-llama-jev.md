# Bonsai-Llama-Jev

| | |
|---|---|
| Author | Aron Homberg ([kyr0](https://github.com/kyr0)) |
| Type | Open typed-decision server: llama.cpp fork that reads answer-label logits from a causal LM |
| Backbone | PrismML Ternary-Bonsai-2-27B ([`prism-ml/Ternary-Bonsai-2-27B-gguf`](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf)), a ternary quant of `Qwen/Qwen3.8-27B` (thinking model) |
| Size | GGUF Q2_64, ~7 GB weights, ~10 GB VRAM at 64k context |
| Licence | MIT (code); Apache-2.0 (weights, PrismML; base Qwen3.8-27B also Apache-2.0) |
| Run it via | `make setup && make start` → `http://localhost:54100/v1/systemone` |

Checked 2026-09-30 against the `prism` branch (last push 2026-09-25, 2 stars).

## Overview

- C/C++ server with two endpoints: OpenAI-compatible `/v1/chat/completions` and TypeSafe-compatible `/v1/systemone`.
- `/v1/systemone` generates no text: it normalises the model's scores for each declared label into probabilities.
- Calibration uses separate temperatures for `choice`, `noul` and `score`, loaded from a committed `calibration.json`.
- Both endpoints accept images as base64 data URIs.
- End-to-end tests pass with `typesafe-sdk` 0.7.0 and `@typesafe-ai/sdk` 0.6.0. Method write-up: [kyr0.github.io/Bonsai-Llama-Jev](https://kyr0.github.io/Bonsai-Llama-Jev/).

## Schema

Same wire format as Jev; see [concepts.md](../concepts.md#request-and-response-shape).

```json
{"model": "bonsai-2-27b",
 "state": "My payouts have failed for three days, please help today.",
 "questions": {
   "department":  {"type": "choice", "instructions": "Which team handles this?", "criteria": {"billing": "Payments", "technical": "Bugs"}},
   "urgency":     {"type": "noul", "instructions": "The message is time-sensitive"},
   "frustration": {"type": "score", "instructions": "How frustrated?", "criteria": ["Calm", "Frustrated", "Furious"]}}}
```

```json
{"answers": {
  "department":  {"choice": "technical", "probabilities": {"billing": 0.07, "technical": 0.93}},
  "urgency":     {"noul": 0.99},
  "frustration": {"score": 1.01, "probabilities": {"0": 0.01, "1": 0.96, "2": 0.03}}}}
```

- The README response omits `type` and `confidence`.
- For images, `state` is an object with a `content` array of `text` and `image_url` parts; image tokens count toward `usage.input_tokens`.

## Benchmarks

Self-reported on the author's [typed-decision-bench](https://kyr0.github.io/typed-decision-bench/) ([repo](https://github.com/kyr0/typed-decision-bench)), 2026-09-22, soft accuracy, NVIDIA GPUs:

| Model | Accuracy | p50 / p95 latency (ms) | VRAM at 8k KV |
|---|---:|---:|---|
| Jev-1.13.0 | 88% | 716 / 779 | n/a (API) |
| **Bonsai-2-27B calibrated** | 76.46% | 171 / 448 | 9,242 MB @ Q2_64 |
| openjev-qwen3.5-4b | 74.13% | 1,066 / 1,479 | 12,866 MB @ BF16 |
| spark-X2.5 | 70.97% | 1,057 / 1,784 | 9,813 MB @ BF16 |
| von-1.1 | 48.57% | 38.5 / 46.5 | 3,888 MB @ FP32 |
| laya | 46.70% | 36.7 / 44.4 | 1,426 MB @ FP32 |

- Calibration error: 13% for Bonsai vs 8.4% for Jev-1.13.
- Calibration run: 275 suites, 5,499 calibration and 22,001 held-out cases. Held-out NLL 0.438 → 0.435, Brier 0.2355 → 0.2339, ECE-15 0.0120 → 0.0146; `noul` ECE-15 0.046 → 0.026.

## Running it

The README supports Linux or Mac and reports 46.8 tok/s chat throughput on an M5 Max. Needs ~20 GB disk (model files ~17 GB; 3 of the 4 GGUFs are used).

```sh
git clone https://github.com/kyr0/Bonsai-Llama-Jev && cd Bonsai-Llama-Jev
make setup    # builds the server, downloads the model
make start    # starts on :54100 and runs self-checks
make status   # model, calibration on/off, endpoint URLs
```

Call it with the payload above (`curl http://localhost:54100/v1/systemone -H "Content-Type: application/json" -d @request.json`) or with `TypeSafeClient(base_url="http://localhost:54100")`.

- `make configure-*` targets are NVIDIA-only; Macs use the default build. The PrismML card lists ternary kernels for llama.cpp on CUDA and Metal; the fork's Metal build is not documented in this repo.
- `.env` (from `.env.example`): `PORT`; `BONSAI_API_KEY` (require a key); `BONSAI_CTX` (context); `BONSAI_NP` (parallel slots, default 4, context split across them); `BONSAI_NGL` (`99` all layers on GPU, `0` CPU only); `BONSAI_CALIBRATION` (path or `off`); `BONSAI_GGUF` / `BONSAI_MMPROJ` (other model and its image projector).
- Plain chat needs `"chat_template_kwargs": {"enable_thinking": false}`; `/v1/systemone` does not.

## Scaling limits

- **Options:** no published maximum. Each label needs its own logit readout, so work grows with options and state length; the README says to "shorten the state/question fan-out" when slow.
- **Multi-label:** one `noul` per label, as with Jev.
- **Input length:** up to 64k context in the reference config, split across slots (`BONSAI_CTX` / `BONSAI_NP`).
- **Cost growth:** local compute only. No sampling: sequential requests were bit-identical over 10 repeats; concurrent requests varied by up to ~1e-2.

## Fine-tuning

- Not covered in the README. The documented adaptation is refitting `calibration.json` with typed-decision-bench, required whenever the model, quantisation or prompt template changes.
- `BONSAI_GGUF` can serve another GGUF, including a fine-tuned one.

## Data governance

- Runs locally. After `make setup`, requests stay on the machine unless external services are configured.
- No auth by default; set `BONSAI_API_KEY` before exposing the port.
- Code is MIT. `make setup` runs `scripts/download_models.sh`, which by default fetches [`prism-ml/Ternary-Bonsai-2-27B-gguf`](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf) (revision `b072e1d`, checked 2026-09-30). The card and `NOTICE.txt` give Apache-2.0 and "built from Qwen3.8-27B"; the NOTICE asks for attribution ("Created using Bonsai by Prism ML") on public redistribution.
- Single author, 2 stars as of 2026-09-30. Read the build and download scripts before running `make setup`.

## Caveats

- All benchmark numbers come from the author's own benchmark, not reproduced independently.
- Nothing is published on 100+ options or on `/v1/systemone` Metal performance.
- Provenance: PrismML (`prism-ml` on HF) publishes the weights; `base_model` is `Qwen/Qwen3.8-27B`, "architecture unchanged", quantised to ternary g128 (1.72 bits/weight; PQ2_0 file 7.21 GB, PTQ1_0 5.95 GB) ([`prism-ml/Ternary-Bonsai-2-27B-gguf`](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf) card, checked 2026-09-30).

## Sources

- [kyr0/Bonsai-Llama-Jev](https://github.com/kyr0/Bonsai-Llama-Jev) (README, `prism` branch, fetched 2026-09-30), [method write-up](https://kyr0.github.io/Bonsai-Llama-Jev/)
- [typed-decision-bench](https://kyr0.github.io/typed-decision-bench/), [repo](https://github.com/kyr0/typed-decision-bench), [CALIBRATION.md](https://github.com/kyr0/typed-decision-bench/blob/main/CALIBRATION.md)
- [`prism-ml/Ternary-Bonsai-2-27B-gguf`](https://huggingface.co/prism-ml/Ternary-Bonsai-2-27B-gguf) (card, `NOTICE.txt`, revision `b072e1d`), [`scripts/download_models.sh`](https://github.com/kyr0/Bonsai-Llama-Jev/blob/prism/scripts/download_models.sh)
- [r/LocalLLaMA release thread](https://www.reddit.com/r/LocalLLaMA/comments/1wo6x7e/i_turned_qwen3827b_q2_64_llamacpp_into_a_fully)

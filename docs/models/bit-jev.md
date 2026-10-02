# bit-jev (Zeaulo / jinghao1632)

| Field | Value |
|---|---|
| Vendor | Independent developer: GitHub `Zeaulo`, HF `jinghao1632`, ModelScope `JingHao9616` |
| Type | Decision model: a pointer head scores explicit options for typed questions (Choice, Score, Noul); no generated text |
| Backbone | `microsoft/bitnet-b1.58-2B-4T-bf16` (ternary BitLinear weights), LoRA then full-student distillation from Kev-9B |
| Size | About 2.4B parameters (base, per [microsoft/BitNet](https://github.com/microsoft/BitNet)); `backbone-i2_s.gguf` 1,187,288,192 bytes plus `head.f32` 5,244,948 bytes |
| Licence | **None granted for the weights.** The card says "No standalone open-weights license is granted for this model". Code Apache-2.0; base MIT |
| Run it via | Self-host: `pip install bit-jev` (0.13.13), `BitJev.from_pretrained(device="cpu")`. Prebuilt runners for Windows x64 only; other platforms build from source. Live CPU demo on ModelScope. No paid API |
| Status | HF repo created 2026-09-27; revision `5d2fe7c` (2026-09-30). 2,315 downloads (30 days), 0 likes |

Checked 2026-10-02.

## Overview

bit-jev is a student model that reads hidden states from a 1.58-bit BitNet backbone and scores each option with a pointer head ([card](https://huggingface.co/jinghao1632/bit-jev-2b-distilled/raw/main/README.en.md)).
Readout: `logits_k = dot(Wq h_decide / sqrt(d), Wk h_option_close_k) / temperature`, head dimension 256, temperature 2.35 ([`pointer.json`](https://huggingface.co/jinghao1632/bit-jev-2b-distilled/raw/main/pointer.json)).
Delimiters reuse BitNet's reserved special tokens 128002–128008.
The design follows Kev's interface and pointer head; the repo credits Kev (Apache-2.0) in [`THIRD_PARTY_NOTICES.md`](https://github.com/Zeaulo/bit-jev/blob/main/THIRD_PARTY_NOTICES.md). See [kev.md](kev.md).
The released package is the I2_S GGUF backbone for a native CPU runner built on bitnet.cpp and llama.cpp; BF16 safetensors are not published.

## Schema

Request: `state` + `questions` map, each with `type` (`choice`, `noul`, `score`), `instructions` and `criteria`, as in TypeSafe ([card example](https://huggingface.co/jinghao1632/bit-jev-2b-distilled/raw/main/README.en.md), [`core/bit_jev/api.py`](https://github.com/Zeaulo/bit-jev/blob/main/core/bit_jev/api.py)).

- **Choice:** named options with descriptions; returns the argmax, `probabilities`, `confidence`.
- **Score:** ordered level descriptions; `score` is the expected level (probability-weighted index), with `probabilities` and `confidence`.
- **Noul:** two labels; returns probabilities for both.
- The GGUF API (`BitJev.infer`) returns `answers` and `latency_ms`.
- An HTTP server (`python -m bit_jev.serve`) exposes `POST /v1/systemone` "in kev's shape" and `POST /v1/systemone/separate`. It loads a PyTorch run directory; whether it works with the published GGUF package is not documented (unverified).

TypeSafe-compatible: partial. The request shape matches; the response follows Kev's shape, and confidence formulas are Kev-style, not Jev's.

## Benchmarks

No accuracy result is published. The card: "No auditable held-out report for accuracy, Brier, NLL, or ECE is available, so no such values are claimed."
No row on JevBench v1.5.4, the Decision Index 0.2.1, kyr0, 4nt0ineB or Fastino fast-decisions, checked 2026-10-02 against [`/api/jevbench/v1.5.4`](https://benchmarkheaven.com/api/jevbench/v1.5.4) and the DI [`data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index).

Latency for one fixed request (1 question, 703 input tokens, 77 options), model loading excluded ([`benchmark_case_epyc.json`](https://huggingface.co/jinghao1632/bit-jev-2b-distilled/raw/main/benchmark_case_epyc.json), [`benchmark_case_autodl.json`](https://huggingface.co/jinghao1632/bit-jev-2b-distilled/raw/main/benchmark_case_autodl.json), 2026-09-27 and 2026-09-28):

| Path | Mean time | Runs | Memory |
|---|---:|---:|---:|
| AMD EPYC 9654, 32 threads, I2_S | 1,954 ms | 6 | 1,626 MiB RSS |
| AMD EPYC 9654, 16 threads, I2_S | 3,210 ms | 3 | 1,623 MiB RSS |
| Xeon Gold 6459C, 16 threads, I2_S | 1,972 ms | 3 | 1,625 MiB RSS |
| RTX 5090, FP16 PyTorch (different host) | 86.6 ms | 5 | 4,936 MiB GPU |

The author notes the CPU and GPU rows use different hosts, weight formats and precision, so their ratio is not a hardware speedup.

## Running it

```bash
uv venv --python 3.12 && uv pip install bit-jev==0.13.13
```

```python
from bit_jev.gguf import BitJev

request = {"state": "A customer reports a duplicate charge on the same order.",
           "questions": {"team": {"type": "choice", "instructions": "Which team should handle it?",
                                  "criteria": {"billing": "Payment and refunds", "shipping": "Delivery"}}}}
with BitJev.from_pretrained(device="cpu", threads=8) as model:
    print(model.infer(request)["answers"])
```

- The first call downloads about 1.19 GB from Hugging Face, with ModelScope as fallback.
- Python 3.11 or 3.12 (`requires_python <3.13,>=3.11` on [PyPI](https://pypi.org/project/bit-jev/)). PyPI ships a Windows x64 wheel and an sdist.
- Mac (M5 Max): CPU only, built from source. The runner builds from pinned BitNet and llama.cpp commits with a ReLU² patch; it needs Git, CMake 3.28+ and a C++17 compiler. The project lists macOS arm64 as "not yet tested" ([`core/README.md`](https://github.com/Zeaulo/bit-jev/blob/main/core/README.md)). Upstream bitnet.cpp lists the I2_S kernel for BitNet-b1.58-2B-4T on ARM ([BitNet README](https://github.com/microsoft/BitNet)). No Metal, MLX or MPS inference path is published.
- GPU: Vulkan (prebuilt on Windows) or CUDA (source build).

## Scaling limits

- **Options:** 1 to 255 per question (`MAX_OPTIONS = 255` in `api.py`). The demo page allows 2 to 4.
- **Context:** serving accepts up to 8,192 state tokens plus 8,192 branch tokens (`SERVE_MAX_STATE`, `SERVE_MAX_BRANCH` in `encoding.py`). Training used at most 384 state tokens and 2,048 packed tokens. The backbone `config.json` lists `max_position_embeddings: 4096`. Inputs past 2,048 tokens are out of training distribution (unverified effect).
- **Questions per call:** the native CPU runner "executes one causal row per question and recomputes shared state for multiple questions" (card), so cost grows linearly with questions.
- **Speed:** about 2 s per question for a 703-token, 77-option request on 32 EPYC threads.

## Fine-tuning

- **Code:** public, Apache-2.0, [Zeaulo/bit-jev](https://github.com/Zeaulo/bit-jev) at commit `e3b5b01` (2026-09-30). Scripts `core/scripts/run_train.sh` (LoRA + pointer head), `core/scripts/run_distill.sh` (teacher logits, then distillation), `core/scripts/export_kev_teacher.py`, `core/bit_jev/{train,distill,eval,export_distilled}.py`.
- **Recipe:**
  1. LoRA rank 16 plus pointer head on `microsoft/bitnet-b1.58-2B-4T-bf16`: 2 epochs, LR 5e-5, batch 4 × accumulation 2, BF16, gradient checkpointing ("Kev's exact settings").
  2. Export candidate logits from the teacher `jaredpalmer/kev-9b` (Apache-2.0, revision `db029f0`).
  3. Full-parameter quantization-aware distillation: 3,144 steps, 2 epochs, LR 2e-5, batch 2 × accumulation 4, `adamw8bit`, temperature 2.0, weight 1.0 (card).
  4. Export to I2_S GGUF plus an FP32 head.
- **Data:** the `decision-v7` training partition of [`jaredpalmer/kev-suites`](https://huggingface.co/datasets/jaredpalmer/kev-suites), fetched by `core/scripts/fetch_kev_suites.py`. The kev-suites card has no licence field (HF API, 2026-10-02). The set includes Yelp review records; Yelp's [dataset agreement](https://s3-media3.fl.yelpcdn.com/assets/srv0/engineering_pages/bea5c1e92bf3/assets/vendor/yelp-dataset-agreement.pdf) governs them ([`Yelp/yelp_review_full`](https://huggingface.co/datasets/Yelp/yelp_review_full) licence `other`).
- **Reported hardware and time** (comments in the scripts, AutoDL): LoRA stage "~1-2 h on a 24 GB card"; teacher logits "~1 h"; distillation "~2-4 h" on a "32 GB card". Total about 4–7 h. Cost is not stated.
- **Apple Silicon:** partial. `train.py` accepts `--device mps` and BF16 on MPS (`core/bit_jev/train.py`), untested by the author. Distillation uses bitsandbytes `adamw8bit`, which targets CUDA (MPS support unverified). The Kev-9B teacher export runs in a separate Kev environment.
- **HF Jobs flavor (estimate):** `l40sx1` ($1.80/h, 48 GB) covers all three stages with margin over the author's 32 GB card; 4–7 h is about $7–13. `a10g-small` (24 GB) fits the LoRA stage. Rates from [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing).
- **Commercial use:** not cleared. The weights carry no licence, and the author's request to Yelp for permission had no written reply as of 2026-09-28. Retraining from the public code on data you hold rights to avoids the Yelp question; the base (MIT) and teacher (Apache-2.0) allow commercial use.

## Data governance

Not legal advice. bit-jev has no paid API. Rows cover self-hosting unless they say otherwise.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; CPU runner, air-gapped once the GGUF is cached (offline directories supported) | [GGUF package guide](https://github.com/Zeaulo/bit-jev/blob/main/docs/GGUF_PACKAGE.md) |
| Fine-tuning | Yes, on your hardware; scripts in the repo | `core/scripts/run_train.sh`, `run_distill.sh` |
| Processing location | Your infrastructure. The public demo runs in a free ModelScope CPU Space (2 vCPU); the HF static Space embeds it, so demo input goes to ModelScope | [card](https://huggingface.co/jinghao1632/bit-jev-2b-distilled), `core/README.md` |
| EU processing option | Self-host in the EU. The ModelScope demo region is not documented (unverified) | |
| Retention / ZDR | Local runner: no logging documented. ModelScope demo: not documented; send only public or synthetic data | |
| Training on inputs | No; inference is local | |
| DPA / GDPR | Not applicable when self-hosted: no processor | |
| Certifications | None (open-source project) | |
| Weights licence | None granted. Code Apache-2.0 (GitHub `LICENSE`, PyPI `license_expression`); base `microsoft/bitnet-b1.58-2B-4T-bf16` MIT (revision `2766813`); teacher Kev-9B Apache-2.0 | card, HF API, 2026-10-02 |
| Training-data terms | `decision-v7` from kev-suites (no licence field), including Yelp reviews under Yelp's agreement; permission request unanswered as of 2026-09-28 | card, `THIRD_PARTY_NOTICES.md` |

## Caveats

- No accuracy, calibration or benchmark number exists for this checkpoint.
- The weights have no licence. Treat them as all rights reserved until the author grants one.
- The HF `cardData` has no `license` field. The default `README.md` is the Chinese card; `README.en.md` is the English one.
- Training and serving context limits differ (2,048 vs 16,384 tokens).
- `head.f32` and the GGUF come with SHA-256 hashes in `SHA256SUMS.json`; verify them after download.

## Sources

- HF model: [English card](https://huggingface.co/jinghao1632/bit-jev-2b-distilled/raw/main/README.en.md), [API](https://huggingface.co/api/models/jinghao1632/bit-jev-2b-distilled), `config.json`, `pointer.json`, `SHA256SUMS.json`, `benchmark_case_autodl.json`, `benchmark_case_epyc.json`
- GitHub: [Zeaulo/bit-jev](https://github.com/Zeaulo/bit-jev) at `e3b5b01`: README, LICENSE, `THIRD_PARTY_NOTICES.md`, `core/README.md`, `docs/GGUF_PACKAGE.md`, `core/scripts/{run_train,run_distill}.sh`, `core/scripts/fetch_kev_suites.py`, `core/bit_jev/{api,encoding,train,serve,native_build}.py`
- [PyPI: bit-jev](https://pypi.org/pypi/bit-jev/json) (0.13.13)
- Base and teacher: [`microsoft/bitnet-b1.58-2B-4T-bf16`](https://huggingface.co/microsoft/bitnet-b1.58-2B-4T-bf16), [microsoft/BitNet README](https://github.com/microsoft/BitNet), [`jaredpalmer/kev-9b`](https://huggingface.co/jaredpalmer/kev-9b), [`jaredpalmer/kev-suites`](https://huggingface.co/datasets/jaredpalmer/kev-suites) (API metadata)
- Yelp: [`Yelp/yelp_review_full`](https://huggingface.co/datasets/Yelp/yelp_review_full) card, [dataset agreement](https://s3-media3.fl.yelpcdn.com/assets/srv0/engineering_pages/bea5c1e92bf3/assets/vendor/yelp-dataset-agreement.pdf) (linked, not read)
- Boards: [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4), [Decision Index `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index)
- [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing)

All read 2026-10-02.

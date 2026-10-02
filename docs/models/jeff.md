# jeff (Logan Markewich)

| Field | Value |
|---|---|
| Vendor | Logan Markewich (personal project; author works at LlamaIndex) |
| Type | Self-hosted server for the Jev System One API (`POST /v1/systemone`), backed by an off-the-shelf zero-shot encoder; no weights of its own |
| Backbone | [`knowledgator/gliformer-large-v1`](https://huggingface.co/knowledgator/gliformer-large-v1): DeBERTa encoder, a word-level bidirectional LSTM and GLiFormer task heads |
| Size | 575.6M parameters (GLiFormer card). The jeff README says 400M |
| Licence | Server code MIT. GLiFormer weights and framework Apache-2.0. Both allow commercial use |
| Run it via | `uv run jeff` on your machine (CUDA → MPS → CPU), or `deploy/modal_gpu.py` on your own Modal account. Works with the official `typesafe-sdk` through `TYPESAFE_BASE_URL` |
| Status | Repo at [`34b32f9`](https://github.com/logan-markewich/jeff/commit/34b32f99a727c47b679adde33f4702a001e02979) (2026-09-19). GLiFormer revision `d0a4e53` (created 2026-09-11, last modified 2026-09-18); 1,874 downloads (30 days), 163 likes |

Checked 2026-10-02.

## Overview

jeff wraps GLiFormer-large in a FastAPI server that speaks Jev's wire format ([README](https://github.com/logan-markewich/jeff)).
It answers `choice`, `score` and `noul` questions.
It does not train or fine-tune anything: every answer comes from Knowledgator's released checkpoint plus a fitted temperature of 3.2.
The README calls it "cheaper to self-host, but less accurate than jev on reasoning-heavy tasks."
LlamaIndex used it as one of two open encoders in [experiment 03](../../experiments/03-jev-vs-open-document-tasks/README.md).

**Name clash.** A different project, [firelex/jeff](https://github.com/firelex/jeff) (Hugging Face user `mstrasser`), also calls itself Jeff. That one fine-tunes Qwen3.5 and Gemma 4 decoders and is the subject of the [Developers Digest article](https://www.developersdigest.tech/blog/jeff-jev-compatible-decision-models-2026) "Jeff: Jev-Style Decision Models Trained at Home on One GPU" (2026-09-30). The article does not cover Logan Markewich's jeff. See [Other projects named Jeff](#other-projects-named-jeff).

## Schema

Same path and shape as TypeSafe: `model` + `state` + `questions` → `answers` + `usage` ([API section](https://github.com/logan-markewich/jeff#api-and-compatibility)).

- Auth: `Authorization: Bearer <key>`; keys come from `JEFF_API_KEYS`. With that variable empty, auth is off.
- `model` accepts `jev-latest` and `jev` as aliases (`JEFF_MODEL_ALIASES`).
- Endpoints: `POST /v1/systemone`, `GET /v1/models`, `GET /healthz`, `GET /stats`.
- Errors: `401` bad key, `422` validation or request limit, `429` rate limit (`retry-after-ms`), `529` queue full.
- **Probabilities:** normalised sigmoids, temperature-scaled at 3.2. `score` uses the unscaled distribution, so it matches the weighted mean of the shown probabilities only at `JEFF_TEMPERATURE=1`.
- **Confidence:** `(p_max - 1/n) / (1 - 1/n)`.
- **Question independence:** each `noul` gets its own encoder pass. `choice` and `score` questions share one pass and can affect each other unless `JEFF_ISOLATE=all`.
- **Tokens:** `usage.input_tokens` counts DeBERTa tokens; `output_tokens` is nominal. Counts are not comparable with Jev billing.

TypeSafe-compatible: yes at the wire level. Model behaviour differs as listed above.

## Benchmarks

| Suite | jeff | Jev 1.13.0 | Source |
|---|---:|---:|---|
| Decision Index 0.2.1, balanced skill | 8.04 (#56 of 71); ECE 0.097; median 21.8 ms | 57.91 | [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021); [`data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index) (generated 2026-09-28) |
| JevBench v1.5.4 score | 0.1 (#84); Intelligence 4.4, Calibration 80.3; p50 3.49 s raw on local CPU | 72.1 | [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#jevbench-v154-headline-a) |
| JevBench v1.2.2 score (official, 534 decisions) | 66.9 (#9 of 18); Intelligence 63.9 | 75.3 | [bench/RESULTS.md](https://github.com/logan-markewich/jeff/blob/main/bench/RESULTS.md) |
| JevBench v1.2.2 accuracy, easy / standard / judge / hard | 100 / 76.0 / 61.6 / 37.7% | 100 / 99.0 / 94.5 / 74.1% | same |
| AG News topic accuracy (author's 1,600-item set) | 75.5% | 90.5% | [README](https://github.com/logan-markewich/jeff#benchmarks) |
| Experiment 03, five PDF tasks (32–96 decisions each) | 21.9–73.2% | 54.2–100% | [experiment 03](../../experiments/03-jev-vs-open-document-tasks/README.md#results); [benchmarks.md](../benchmarks.md) |

- JevBench v1.2.2 ran on 4 threads of a Ryzen 5 3600 at jeff commit `6f43d3e`. jeff's rank there came from the Cost axis (#5 of 18); it was #14 on Intelligence.
- JevBench v1.5.4 adds gates to the harmonic mean, which is why the same model falls from 66.9 to 0.1 (see [benchmarks.md](../benchmarks.md#jevbench)).
- Hard-tier calibration (author run, public tiers): ECE 0.22 vs Jev 0.09. Mean top-label confidence 0.54 vs 0.79. The temperature flattens every distribution, so jeff is underconfident where it is right.
- Experiment 03: no jeff answer on 16-class RVL-CDIP reaches confidence 0.3; jeff sends 7 of 8 Turkish and Russian pages to English.
- GLiFormer's own card reports a mean macro-F1 of 75.03 over 13 classification datasets. That is Knowledgator's figure for the base model, not a jeff run.

## Running it

From the [README](https://github.com/logan-markewich/jeff#quickstart); needs `uv` and Python 3.12:

```bash
git clone https://github.com/logan-markewich/jeff && cd jeff
uv sync --extra dev
uv run hf download knowledgator/gliformer-large-v1 --local-dir models/gliformer-large-v1
JEFF_API_KEYS=devkey uv run jeff          # http://localhost:8000
```

```bash
curl http://localhost:8000/v1/systemone \
  -H 'Authorization: Bearer devkey' -H 'Content-Type: application/json' \
  -d '{"state": "The export button crashes in Safari.", "model": "jev-latest",
       "questions": {"severity": {"type": "score", "instructions": "How severe?",
                                  "criteria": ["cosmetic", "degraded", "blocking"]}}}'
```

- **Mac (M5 Max):** the server picks MPS on its own (`JEFF_DEVICE=mps` to force it). The author's M2 Max run at fp32 measured 108 ms p50 on short JevBench items and up to 7 s on 3,000–4,000-token items. An ONNX Runtime CPU path with int8 export also exists (`uv sync --extra onnx`); the README says to prefer MPS on Mac. No MLX or GGUF build.
- **GPU:** Modal L4 recommended for the HTTP API; one container caps at about 50 requests/s behind Modal's ingress. The author estimates about $2.6 per 1M single-question requests on L4 vs about $15.6 on Jev.
- For faster local work, `knowledgator/gliformer-base-v1` with `JEFF_NOUL_MODE=single`.

## Scaling limits

- **Labels:** 64 per question (`JEFF_MAX_LABELS`), adjustable.
- **Questions per call:** 64 (`JEFF_MAX_QUESTIONS`).
- **State:** 20,000 characters (`JEFF_MAX_STATE_CHARS`); more returns `422`. The encoder's own token window is not stated in the GLiFormer card (unverified).
- **Queue:** 256 requests before `529`; batch size 16, 5 ms wait by default.
- **Latency floor:** about 28 ms on A10G and 45 ms on L4 at batch size 1 for a 149-token request. The LSTM after the encoder takes 21% of GPU time.

## Fine-tuning

- **jeff training code: none.** The repo has a temperature-fitting script ([`bench/calibrate.py`](https://github.com/logan-markewich/jeff/blob/main/bench/calibrate.py)) and nothing that updates weights.
- **Base model:** the [GLiFormer framework](https://github.com/Knowledgator/GLiFormer) (Apache-2.0, `19db82a`) has `model.train_model(...)` for fine-tuning a checkpoint on your own labelled records, with options such as `freeze_components=["text_encoder"]` and `train_head_only=True`. To use a tuned checkpoint, point `JEFF_MODEL` at it.
- **Training data of GLiFormer-large:** the card refers to a manuscript for the "multitask training mixtures" and says "full checkpoint-specific training provenance is not recorded". Data licences are not listed.
- **Reported hardware and time:** none for jeff or for GLiFormer-large.
- **Apple Silicon training:** not documented. GLiFormer runs inference on MPS through jeff; `train_model` on MPS is untested (unverified).
- **HF Jobs flavor (estimate):** a 576M encoder fine-tune fits `l4x1` (24 GB, $0.80/h) or `a10g-small` (24 GB, $1.00/h). The optional flash kernels need CUDA, so `t4-small` would run eager attention only. Our estimate from model size, not a measured run ([rates](https://huggingface.co/docs/hub/jobs-pricing)).

## Data governance

Not legal advice. jeff has no hosted API; every row below is for running it on your own infrastructure.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; this is the only way to run it. Offline once the checkpoint is in `models/` | [README](https://github.com/logan-markewich/jeff#quickstart) |
| Fine-tuning | Not in jeff. Possible on the base model through the GLiFormer framework, on your hardware | [GLiFormer README](https://github.com/Knowledgator/GLiFormer#training) |
| Processing location | Your machine, or your own Modal account (region per your Modal settings, unverified) | [`deploy/modal_gpu.py`](https://github.com/logan-markewich/jeff/blob/main/deploy/modal_gpu.py) |
| EU processing option | Self-host in the EU | |
| Retention / ZDR | The server keeps batcher counters in memory (`/stats`). No request logging is documented (unverified) | [README](https://github.com/logan-markewich/jeff#api-and-compatibility) |
| Training on inputs | No; inference only | |
| DPA / GDPR | Not applicable when self-hosted: no processor | |
| Certifications | None (open-source project) | |
| Network exposure | Binds `0.0.0.0:8000`; auth is off unless `JEFF_API_KEYS` is set | [README](https://github.com/logan-markewich/jeff#configuration) |
| Weights licence | Apache-2.0 (`knowledgator/gliformer-large-v1`, `cardData`); server MIT. Commercial use allowed | HF API, 2026-10-02; [LICENSE](https://github.com/logan-markewich/jeff/blob/main/LICENSE) |

## Caveats

- Parameter count: the jeff README and notebook say 400M; the GLiFormer card says 575.6M; the Decision Index records 575,683,963 (estimated). This doc uses the card figure.
- jeff is a wrapper: any accuracy change comes from Knowledgator's checkpoint or from jeff's prompt and temperature settings.
- Experiment 03 did not pin the GLiFormer revision.
- The JevBench v1.2.2 rank of #9 rests on a cost estimate at $0.01 per 1M input tokens, not a bill.
- The repo has had no commits since 2026-09-19.

## Other projects named Jeff

[firelex/jeff](https://github.com/firelex/jeff) (`d0173b4`, read 2026-10-02) is unrelated to this server. Facts from its README and HF API:

- Models: [`mstrasser/Jeff-Qwen3.5-0.8B`](https://huggingface.co/mstrasser/Jeff-Qwen3.5-0.8B) (rev `51552f3`, created 2026-09-28, 1,576 downloads, 18 likes), `Jeff-Qwen3.5-2B` (701 / 14), `Jeff-Gemma4-E2B` (416 / 9), plus nine LoRA adapters added 2026-10-01.
- Licence: code MIT, weights Apache-2.0. It starts from the [AutoJev](https://github.com/denis-pplx/autojev) recipe ([pplx-decider.md](pplx-decider.md)).
- Training code is public (`scripts/train_all.sh`, `jeff-train`). Synthetic data was written by Qwen3.8-Flash-Next on two DGX Sparks; training data is not released, and some sources are CC BY-SA.
- Reported hardware: one RTX PRO 6000. Base training takes about 2 h (0.8B) and 3.5 h (2B), per the Developers Digest article (secondary). Adapters take 0.5–4 h each on one GPU (README).
- Mac: MLX serving on Apple Silicon; the article reports 28 ms per decision on an M4 Max.
- LocalLLaMA typed-decisions card (zero-shot, scored 2026-09-29): Jeff-Qwen3.5-0.8B 0.483, -2B 0.511, Gemma4-E2B 0.561, against Jev 0.727 and the input-blind prior 0.470 ([card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions), rev `d0e2f0c`).

It needs its own model doc.

## Sources

- jeff: [GitHub README](https://github.com/logan-markewich/jeff) (`34b32f9`), [bench/RESULTS.md](https://github.com/logan-markewich/jeff/blob/main/bench/RESULTS.md), [LICENSE](https://github.com/logan-markewich/jeff/blob/main/LICENSE), [`pyproject.toml`](https://github.com/logan-markewich/jeff/blob/main/pyproject.toml)
- GLiFormer: [model card](https://huggingface.co/knowledgator/gliformer-large-v1) and [HF API](https://huggingface.co/api/models/knowledgator/gliformer-large-v1) (`d0a4e53`), [framework README](https://github.com/Knowledgator/GLiFormer) (`19db82a`)
- Boards: [Decision Index Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) (`data/index.json`, generated 2026-09-28), [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4); repo tables in [benchmarks.md](../benchmarks.md) and [benchmarks-leaderboards.md](../benchmarks-leaderboards.md)
- [Experiment 03](../../experiments/03-jev-vs-open-document-tasks/README.md) (LlamaIndex `run-llama/jev_vs_oss` at `0a3726f`)
- Name clash: [firelex/jeff README](https://github.com/firelex/jeff), [HF `mstrasser` models](https://huggingface.co/mstrasser), [LocalLLaMA/typed-decisions card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions), [Developers Digest article](https://www.developersdigest.tech/blog/jeff-jev-compatible-decision-models-2026) (secondary, 2026-09-30)
- HF Jobs rates: [jobs-pricing](https://huggingface.co/docs/hub/jobs-pricing)

All read 2026-10-02.

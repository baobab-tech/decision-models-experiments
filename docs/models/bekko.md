# Bekko System One v0 (hotchpotch)

| Field | Value |
|---|---|
| Vendor | Yuichi Tateno ([@hotchpotch](https://github.com/hotchpotch)), personal project |
| Type | Open-weight encoder decision models: probabilities for Choice, Noul and Score (plus document ranking), no generated text |
| Backbone | Ettin reranker cross-encoders ([`cross-encoder/ettin-reranker-{17m,68m,400m}-v1`](https://huggingface.co/cross-encoder/ettin-reranker-400m-v1), Apache-2.0), ModernBERT-compatible, with a shared-prefix attention layout and task heads |
| Size | 17M (3.9M excluding token embeddings), 68M (42M), 395M (343M) |
| Licence | **None assigned.** Model cards say the licence "remains to be finalized". Training and inference code on GitHub is MIT |
| Run it via | Python `BekkoSentenceTransformer.predict()` (CPU or CUDA, `trust_remote_code`); ONNX in Node.js or the browser (WASM, WebGPU). No HTTP server |
| Status | v0, "experimental". Created 2026-09-29; last modified 2026-09-30. Revisions `b886a1f` (17M), `ab7685f` (68M), `1960df5` (400M). Likes 10 / 1 / 5. HF reports 0 downloads (30 days) for all three; the repos have no root `config.json`, so downloads are not counted |

Checked 2026-10-02.

## Overview

Bekko asks "whether ultra-small models can become capable System One Decision Models" ([400M card](https://huggingface.co/hotchpotch/bekko-system-one-v0-400m)).
The author also built the S1MB benchmark ([github.com/hotchpotch/S1MB](https://github.com/hotchpotch/S1MB)) used for the headline results.
The cards say the models "fall far behind Jev 1.13 on S1MB's benchmarks designed to measure generalization", which is why the release is v0.
The prefix (instructions plus state) is encoded once; each candidate attends to the prefix and to its own tokens, and candidates do not attend to each other.
A browser demo runs the 17M and 68M models on your device ([Space](https://huggingface.co/spaces/hotchpotch/bekko-system-one-in-browser)).
English only.

## Schema

Own JSON call shape with the same three primitives ([card, Decision types](https://huggingface.co/hotchpotch/bekko-system-one-v0-400m#decision-types)). TypeSafe-compatible: **partial**.

- Input: `state_json` plus a list of `decisions`, each with `id`, `type` (`choice`, `noul`, `score`), `instructions_json` and `criteria` entries (`id`, `description_json`, `value`).
- **Choice:** returns `selected_id` and `probabilities` (softmax over candidates).
- **Noul:** criteria IDs `true`/`false` or `yes`/`no`, each with a written meaning; returns `probability_yes`.
- **Score:** each criterion needs an explicit numeric `value`; returns `score` (probability-weighted value), `normalized_score` (0–1), `probabilities`, `values`.
- **Ranking:** `kind="ranking"` with `documents`; returns relative `probabilities` and an `order`.
- Several decisions can share one state in a single input object.
- No `/v1/systemone` endpoint and no `confidence` field. S1MB ships a Bekko adapter ([`adapters/bekko_v0.py`](https://github.com/hotchpotch/S1MB/blob/main/evaluator/src/s1mb/adapters/bekko_v0.py)).

## Benchmarks

**S1MB** (author's benchmark; 137 benchmarks, 14,009 cases, 26,269 judgments; snapshot 2026-09-30). Task Avg is a baseline-adjusted 0–100 score, not accuracy ([card](https://huggingface.co/hotchpotch/bekko-system-one-v0-400m#-evaluation-s1mb), [SCORING.md](https://github.com/hotchpotch/S1MB/blob/main/evaluator/SCORING.md)).

| Model | Task Avg (all 137) | Noul | Choice | Score | Synthetic generalisation (6 benchmarks, 600 cases) |
|---|---:|---:|---:|---:|---:|
| Jev 1.13 | 59.59 | 64.63 | 67.22 | 46.92 | 96.27 |
| bekko-400m | 50.60 | 51.24 | 61.32 | 39.25 | 54.48 |
| bekko-68m | 40.46 | 42.91 | 51.62 | 26.85 | 32.48 |
| bekko-17m | 27.57 | 31.43 | 35.57 | 15.70 | 18.96 |
| von (395M) | 16.21 | 20.15 | 23.99 | 4.48 | 43.19 |
| laya-typed-decisions (421M) | 15.00 | 20.06 | 18.93 | 5.99 | 31.82 |

- We recomputed Task Avg from the published [`viewer-summary.json`](https://huggingface.co/datasets/hotchpotch/s1mb-result) (dataset rev `09cf4c0`, generated 2026-09-30) and got the same values to two decimals.
- Of the 48 models in that file with all 137 benchmarks, bekko-400m ranks 7th, behind Jev and five models of 9B–27B; bekko-68m ranks 21st, next to 4B models such as JevK5 (41.14). (Liquid `d1-free` has 6 benchmarks only.)
- **Training overlap:** the training and evaluation manifests share 77 subset names. The card calls this "task-family exposure, not a count of leaked test examples".
- The six synthetic benchmarks were written and self-reviewed by GPT-6-Astra; no human validation.

**LocalLLaMA typed-decisions** (independent; scored by the card's maintainers on 2026-10-01, CPU on an M3 Max; [card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions), rev `d0e2f0c`). Bekko's training data includes this benchmark's `train` split, so it sits in the card's second (fitted) table.

| Model | Accuracy | KL | Brier | ECE | Latency per case (M3 Max CPU) |
|---|---:|---:|---:|---:|---:|
| bekko-400m | 0.668 | 0.214 | 0.113 | 0.143 | 808 ms |
| bekko-68m | 0.537 | 0.293 | 0.160 | 0.116 | 176 ms |
| bekko-17m | 0.483 | 0.344 | 0.203 | 0.136 | 33 ms |
| Jev 1.13.0 (zero-shot table) | 0.727 | 1.442 | 0.148 | 0.144 | 710 ms |
| laya-typed-decisions (fitted) | 0.766 | – | – | – | – |

No Bekko row on the Decision Index 0.2.1, JevBench v1.5.4, kyr0, 4nt0ineB or Fastino fast-decisions boards in [benchmarks-leaderboards.md](../benchmarks-leaderboards.md) (generated 2026-09-30, before or at release).

**Speed** (author, RTX 5090, compiled SDPA, short four-option Choice, 2026-10-01): single request p50 1.38 ms (17M), 2.69 ms (68M), 5.03 ms (400M). 32-request batch: 9,875 questions/s on 17M. Full S1MB (26,269 judgments): 13.33 s (17M), 34.04 s (68M), 132.97 s (400M) ([release article](https://huggingface.co/blog/hotchpotch/bekko-system-one-v0-release), 2026-09-30).

## Running it

From the [card quickstart](https://huggingface.co/hotchpotch/bekko-system-one-v0-400m#-quickstart):

```bash
pip install 'torch>=2.10,<2.11' 'transformers==5.17.0' 'sentence-transformers==6.1.0' 'safetensors>=0.7' 'tqdm>=4.67'
```

```python
import json
from transformers.dynamic_module_utils import get_class_from_dynamic_module

repo = "hotchpotch/bekko-system-one-v0-400m"
model = get_class_from_dynamic_module("inference_v0.BekkoSentenceTransformer", repo)(
    repo, trust_remote_code=True, device="cpu")
result = model.predict({
    "state_json": json.dumps({"message": "I was charged twice for the same order. Please refund the duplicate payment."}),
    "decisions": [{
        "id": "department", "kind": "judgment", "type": "choice",
        "instructions_json": json.dumps("Which department should handle this request?"),
        "system_prompt": "",
        "criteria": [
            {"id": "billing", "description_json": json.dumps("Payments, charges, and refunds"), "value": None},
            {"id": "technical", "description_json": json.dumps("Technical failures and configuration"), "value": None}],
        "documents": [], "scoring": None}]})
print(result["department"]["selected_id"], result["department"]["probabilities"])
```

- `trust_remote_code=True` runs `inference_v0.py` from the repo. Pin `revision=` to a full commit hash in both calls.
- **Mac (M5 Max):** CPU fp32 works (typed-decisions maintainers ran all three on an M3 Max CPU). ONNX exports run in Node.js 22+ or the browser (WASM, WebGPU). MPS is not documented: the compatibility guide "does not establish macOS, Windows, or MPS support". No MLX or GGUF build.
- **GPU:** CUDA with BF16 autocast; FlashAttention 2 optional (sm80+).

## Scaling limits

- **Context (native inference):** 7,999 tokens, shared between query (cap 7,997) and each candidate (cap 3,800), with adaptive allocation and balanced query truncation.
- **Training and browser limits:** 4,096 query, 2,048 candidate tokens.
- **Options:** no cap found in the card or `inference_v0.py`; cost grows with candidates.
- **Batching:** `batch_size` 128 and `token_budget` 64,000 by default.
- **Generalisation:** the card says strong results on a familiar task do not carry over to arbitrary instructions.

## Fine-tuning

- **Training code:** public, MIT, [hotchpotch/bekko-system-one](https://github.com/hotchpotch/bekko-system-one) (`main` at `0fccbb8`, 2026-10-01; tag `release-v0` → `ab3ec5e`). Recipes for each size, a smoke run, and templates for your own JSONL data (`configs/typed-decisions.yaml`, `configs/reranker.yaml`). Full fine-tuning and LoRA are both supported; soft targets are accepted.
- **Recipe:** full-parameter fine-tune, no LoRA, 8,421,789 judgments, 16,517 updates, batch 512, AdamW, cosine schedule, seed 42. The 400M recipe uses gradient checkpointing.
- **Data:** [`hotchpotch/bekko-system-one-dataset-v0`](https://huggingface.co/datasets/hotchpotch/bekko-system-one-dataset-v0) (rev `5f67e4e`; 153 subsets, 6,589,190 cases). Built from public NLP and retrieval datasets plus synthetic sets, including the `LocalLLaMA/typed-decisions` train split. No aggregate licence. `sources.json` lists per-source terms, among them sources marked "Non-commercial research only" and "Non-commercial use only", plus CC BY-SA sources and some whose licence is marked "unresolved" or "Unknown".
- **Reported hardware and time:** one RTX 5090 (32 GB); training-loop time 2.10 h (17M), 5.57 h (68M), 25.34 h (400M) ([card](https://huggingface.co/hotchpotch/bekko-system-one-v0-400m#training), [release article](https://huggingface.co/blog/hotchpotch/bekko-system-one-v0-release)). No cost given.
- **Apple Silicon training:** no. The lockfile targets Linux x86_64, Python 3.12 and CUDA 13.0, and the release recipes require FlashAttention 2 on one CUDA GPU ([compatibility](https://github.com/hotchpotch/bekko-system-one/blob/main/docs/compatibility.md)).
- **HF Jobs flavor (estimate):** FA2 rules out `t4-small`. 17M and 68M fit `l4x1` (24 GB, $0.80/h) or `a10g-small` ($1.00/h). For 400M, `l40sx1` (48 GB, $1.80/h) or `a100-large` (80 GB, $2.50/h); if throughput is close to the 5090, the 25 h run costs about $45–65. Our estimate, not a measured run ([rates](https://huggingface.co/docs/hub/jobs-pricing)).

## Data governance

Not legal advice. Bekko has no hosted API; every row below is for running it on your own infrastructure.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; offline once weights are cached. The browser app runs inference on your device; "input text is not sent to an inference server" | [GitHub README](https://github.com/hotchpotch/bekko-system-one#browser-app) |
| Fine-tuning | Yes, with the public code, on one CUDA GPU | [training guide](https://github.com/hotchpotch/bekko-system-one/blob/main/docs/training-v0.md) |
| Processing location | Your infrastructure. The demo Space serves model files; inference runs in your browser | [Space](https://huggingface.co/spaces/hotchpotch/bekko-system-one-in-browser) |
| EU processing option | Self-host in the EU | |
| Retention / ZDR | No retention by the library (no server) | |
| Training on inputs | No; inference is local | |
| DPA / GDPR | Not applicable when self-hosted: no processor | |
| Certifications | None (open-source project) | |
| Weights licence | **None.** "This card does not assign a license." Without a licence, no right to use or redistribute the weights is granted, commercial or otherwise. Base Ettin rerankers are Apache-2.0; code is MIT | [card, License](https://huggingface.co/hotchpotch/bekko-system-one-v0-400m#license); HF API `cardData` has no `license` |
| Training data | Mixed per-source licences, some non-commercial | [`sources.json`](https://huggingface.co/datasets/hotchpotch/bekko-system-one-dataset-v0/blob/main/sources.json), [`SOURCES.md`](https://huggingface.co/datasets/hotchpotch/bekko-system-one-dataset-v0/blob/main/SOURCES.md) |

## Caveats

- **Commercial use: not cleared.** No weights licence, and the training data includes non-commercial sources.
- The author built both the model and S1MB, and the training data shares 77 subset names with S1MB.
- `inference_v0.py` executes from the model repo; the RTX 5090 timings pinned older revisions (`2147c3d`, `6eb1bae`, `4aeb85b`) than today's `main`.
- Probabilities are "not guaranteed to be calibrated" (card).
- [scan-2026-10-02.md](../scan-2026-10-02.md) lists Bekko as seen but not documented.

## Sources

- Model cards and HF API: [17M](https://huggingface.co/hotchpotch/bekko-system-one-v0-17m), [68M](https://huggingface.co/hotchpotch/bekko-system-one-v0-68m), [400M](https://huggingface.co/hotchpotch/bekko-system-one-v0-400m); [base Ettin reranker](https://huggingface.co/cross-encoder/ettin-reranker-400m-v1)
- Code: [bekko-system-one README](https://github.com/hotchpotch/bekko-system-one) (`0fccbb8`), [training-v0.md](https://github.com/hotchpotch/bekko-system-one/blob/main/docs/training-v0.md), [compatibility.md](https://github.com/hotchpotch/bekko-system-one/blob/main/docs/compatibility.md), [LICENSE](https://github.com/hotchpotch/bekko-system-one/blob/main/LICENSE)
- [Release article](https://huggingface.co/blog/hotchpotch/bekko-system-one-v0-release) (2026-09-30)
- Data: [bekko-system-one-dataset-v0](https://huggingface.co/datasets/hotchpotch/bekko-system-one-dataset-v0) (`5f67e4e`), `SOURCES.md`, `sources.json`
- S1MB: [GitHub](https://github.com/hotchpotch/S1MB) (`8d44909`), [SCORING.md](https://github.com/hotchpotch/S1MB/blob/main/evaluator/SCORING.md), [results dataset](https://huggingface.co/datasets/hotchpotch/s1mb-result) (`09cf4c0`), [leaderboard](https://huggingface.co/spaces/hotchpotch/S1MB-leaderboard)
- [LocalLLaMA/typed-decisions card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) (`d0e2f0c`)
- HF Jobs rates: [jobs-pricing](https://huggingface.co/docs/hub/jobs-pricing)

All read 2026-10-02.

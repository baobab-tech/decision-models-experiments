# Small "RLCD" language models (LFM2.5, Qwen, Gemma 4)

| Field | Value |
|---|---|
| Vendor | Individual authors on Hugging Face: `notnotsamuel`, `NANI-Nithin` (GGUF), `monotykamary`, `harshatheg`, `anthonym21` (Anthony Maio), `larkooo` (Larkooo). No company behind any of them |
| Type | Six repos. Four are inference engines that score allowed answers with unchanged base weights (parallel constrained decoding, "PCD"). One (`anthonym21/qwen3-0.6b-rlcd-decision`) is a trained decision model. One is a GGUF conversion |
| Backbone | LFM2.5-350M, LFM2.5-2.6B (Liquid AI); Qwen2.5-1.5B-Instruct, Qwen3-0.6B-Base (Alibaba Qwen); Gemma 4 E2B-it (Google) |
| Size | 354M; 2.70B; 1.5B (4-bit MLX, not in the repo); 596M; 5.1B stored parameters in a 3.55 GB 4-bit MLX file ("E2B") |
| Licence | LFM2.5 repos: LFM Open License v1.0 for weights (commercial use only under $10M annual revenue), MIT for code. Qwen and Gemma repos: Apache-2.0 weights, MIT or Apache-2.0 code. See [Data governance](#data-governance) |
| Run it via | Self-hosted only. Python engines in each repo (PyTorch CUDA/MPS, or MLX); GGUF via llama.cpp. No hosted API |
| Status | Community releases, 2026-09-16 to 2026-09-22. All authors call them experimental or research toys |

Checked 2026-10-02.

## Overview

"RLCD" means different things across these six repos.
TypeSafe uses it for Jev's unpublished training method ([concepts](../concepts.md#calibration)).
Four of the repos here did no training at all, and two say so in their own names or cards.

| Repo | Base | What it is | Weights changed? | HF sha | Created | Downloads (30 d) | Likes |
|---|---|---|---|---|---|---:|---:|
| [`notnotsamuel/LFM2.5-350M-RLCD`](https://huggingface.co/notnotsamuel/LFM2.5-350M-RLCD) | `LiquidAI/LFM2.5-350M` @ `9e6c6cc` | PCD engine (`rlcd/engine.py`) plus a byte-for-byte copy of the base weights | No ("training_performed": false) | `deb589d` | 2026-09-16 | 869 | 24 |
| [`NANI-Nithin/LFM2.5-350M-RLCD-GGUF`](https://huggingface.co/NANI-Nithin/LFM2.5-350M-RLCD-GGUF) | the repo above | 29 llama.cpp quants plus BF16, quantized 2026-09-22 with llama.cpp `f3f1a8f`. Language model only; the PCD engine does not run on GGUF | No | `0ef54d7` | 2026-09-22 | 1,487 | 0 |
| [`monotykamary/LFM2.5-2.6B-RLCD`](https://huggingface.co/monotykamary/LFM2.5-2.6B-RLCD) | `LiquidAI/LFM2.5-2.6B` @ `654f946` | PCD engine (`pcd/`) with a `token` and a `sequence` mode, plus a copy of the base weights | No ("No training, LoRA, reinforcement learning, quantization") | `3145545` | 2026-09-16 | 740 | 7 |
| [`harshatheg/Qwen-2.5-1B-RLCD`](https://huggingface.co/harshatheg/Qwen-2.5-1B-RLCD) | `mlx-community/Qwen2.5-1.5B-Instruct-4bit` (loaded at run time) | MLX PCD engine, FastAPI server and web UI. Code only | No weights in the repo | `2af8684` | 2026-09-16 | 0 | 577 |
| [`anthonym21/qwen3-0.6b-rlcd-decision`](https://huggingface.co/anthonym21/qwen3-0.6b-rlcd-decision) | `Qwen/Qwen3-0.6B-Base` | Trained decision model: 100-step SFT warmup, then 500 steps of REINFORCE with reward `c - p_a` (half the Brier-score gradient). LM head removed; 26-letter decision head | Yes (full fine-tune) | `b327ec5` | 2026-09-19 | 1,027 | 4 |
| [`larkooo/gemma-e2b-rlcd`](https://huggingface.co/larkooo/gemma-e2b-rlcd) | `mlx-community/gemma-4-e2b-it-4bit` @ `2387675` (from `google/gemma-4-E2B-it` @ `3e22461`) | MLX PCD engine for text, image, audio and video, plus the unchanged 4-bit checkpoint. An optional trained head scored below the default path and is not shipped | No ("checkpoint_modified": false) | `e099c73` | 2026-09-18 | 337 | 1 |

PCD works the same way in the four engines: prefill the state once, fork the KV cache (and, for LFM2.5, the short-convolution state) per field, score only the allowed answers, and build the JSON in Python.
JSON validity comes from the code, not the model.
`notnotsamuel` writes: "Valid JSON does not mean correct answers."
`anthonym21` credits `harshatheg` for the shared-prefill inference pattern, and `monotykamary` credits `notnotsamuel` for the hybrid-cache design.

### `harshatheg/Qwen-2.5-1B-RLCD` repo facts

- The repo holds 26 files, all code, presets, web assets and two cards. It has no `config.json` and no weight file ([HF API](https://huggingface.co/api/models/harshatheg/Qwen-2.5-1B-RLCD), sha `2af8684`).
- `core/engine_mlx.py` sets `MODEL_ID = "mlx-community/Qwen2.5-1.5B-Instruct-4bit"` and downloads it at run time.
- HF counts downloads from query files such as `config.json` ([HF docs](https://huggingface.co/docs/hub/models-download-stats)). With none in the repo, 0 downloads is expected whatever the use.
- The repo name says 1B; the base is Qwen2.5-1.5B-Instruct.
- The install step clones `https://github.com/your-org/parallel-constrained-decoding.git`, a placeholder URL.
- Likes: 577 on 2026-10-02 ([likers API](https://huggingface.co/api/models/harshatheg/Qwen-2.5-1B-RLCD/likers)). All 577 are user accounts. 367 (64%) use the default avatar. 32 are HF Pro. Account creation dates (from the account IDs) run from 2019-12 to 2026-09; 44 accounts were created in 2026-09, the month of the release. The repo's trending score was 8.
- These numbers alone do not show whether the likes are organic. For comparison, the linked Space [`drinkmoonshine/parallel-constrained-decoding`](https://huggingface.co/spaces/drinkmoonshine/parallel-constrained-decoding) has 34 likes. The author account (Harsha Gundala, created 2025-07-22) has 83 followers.
- The card claims "calibrated field-level confidence scores". The code divides candidate logits by a fixed temperature (default 0.2 or 1.0, depending on the function) before softmax. No calibration result is published.

## Schema

None of the six uses the TypeSafe wire format over HTTP.

| Repo | Input | Types | Output | TypeSafe-compatible |
|---|---|---|---|---|
| LFM2.5-350M | Flat JSON Schema: all properties required, `additionalProperties: false`, each field `boolean` or a string `enum` | boolean, enum | JSON text plus raw candidate log-likelihoods ("not calibrated confidence"); no probabilities | No |
| LFM2.5-2.6B | Same JSON Schema subset; `mode="token"` or `"sequence"` | boolean, enum | `object`, per-field distributions and margins, `calibrated: False` | No |
| Qwen2.5-1.5B (harshatheg) | Own dict: `{"field": {"type": "enum" or "boolean", "choices", "description"}}` | enum (up to 255), boolean | `parsed_json` with `value` and `prob`, plus top choices | No |
| Qwen3-0.6B (anthonym21) | Python: `Decider.ask(state, [ChoiceQ, ScoreQ, NoulQ])` | Choice (2–26), Score (2–26 levels), Noul | `value`, `probs`, `confidence` (top probability), `entropy_confidence`; Score adds `score` = weighted level / (K−1); Noul gives `p_true` | Partial: same three primitives, no HTTP server, different `confidence` and `score` definitions |
| Gemma 4 E2B (larkooo) | Python: `DecisionEngine.system_one(State, {...})` with Jev-style `type` and `criteria`; also a local web UI | Choice, Independent (multi-label), Score, Noul; 2–255 criteria | `answers` with distributions; `confidence` is normalized entropy; `calibration_status: "unvalidated"` | Partial: Jev-style primitives plus multi-label, no `/v1/systemone` endpoint |

## Benchmarks

### Decision Index 0.2.1

Three of the six have rows on the public board ([`data/index-v0.2.1.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index/resolve/main/data/index-v0.2.1.json), generated 2026-09-28; table in [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021)).

| Rank (of 71) | Entrant | Params served | Score | ECE | Median ms (RTX PRO 6000) |
|---:|---|---:|---:|---:|---:|
| 59 | LFM2.5-2.6B-RLCD | 2.7B | 6.76 | 0.255 | 39.3 |
| 67 | Qwen-2.5-1B-RLCD | 1.5B | 3.78 | 0.205 | 43.8 |
| 71 (last) | LFM2.5-350M-RLCD | 354M | 1.38 | 0.568 | 26.7 |
| 1 | Jev 1.13.0 (reference) | n/s | 57.91 | 0.074 | 524.1 |

- LFM2.5-350M-RLCD has the highest ECE on the board, 0.568 ([benchmarks.md](../benchmarks.md)). It is the unchanged LFM2.5-350M base model, so this is the base model's calibration under PCD.
- How the board ran the Qwen-2.5-1B-RLCD entry without weights in the repo is not documented (unverified).
- The Qwen3-0.6B and Gemma 4 E2B repos have no DI, JevBench, kyr0, 4nt0ineB or Fastino fast-decisions row as of 2026-10-02.

### Author-reported

All numbers below are the authors' own, on small or in-distribution sets.

| Repo | Result | Set | Hardware |
|---|---|---|---|
| LFM2.5-350M | Field accuracy 77.8% (PCD) vs 80.6% (autoregressive); 55.27 ms vs 345.36 ms mean (6.25×) | 12 hand-written cases, 3 fields each | M2 Max, FP16, MPS |
| LFM2.5-350M | 28 boolean fields: 393.20 ms vs 3,326.95 ms (8.46×) on M2 Max; 43.76 ms vs 2,586.97 ms on H100; field accuracy 60.7% vs 53.6% | one synthetic input | M2 Max, L40S, H100 |
| LFM2.5-350M | 255-option enum: PCD 3.23× slower than autoregressive on the Mac | one probe | M2 Max |
| LFM2.5-2.6B | Token PCD field accuracy 88.9% on 12 development cases, 72.2% on 6 fresh audit cases, vs 94.4% for autoregressive JSON. Failed both 64- and 255-option probes in token mode | 18 hand-written cases | one L40S, FP16 |
| LFM2.5-2.6B | 56.24 ms vs 557.41 ms (9.9×) on development cases; 106.98 ms vs 4,875.30 ms on 28 fields | same | one L40S |
| Qwen2.5-1.5B (harshatheg) | 68–89 ms vs 380–500 ms (5.6×) on 4-field and 255-option presets; 270 ms vs 1,900 ms (7.0×) on 28 fields. Only "100% schema validity" reported, no accuracy | 4 presets | M4 Max, 128 GB |
| Qwen3-0.6B (anthonym21) | Accuracy 0.807 [0.798, 0.816], ECE 0.021 [0.017, 0.030] (15 bins), Brier 0.268. Warmup it started from: 0.746, ECE 0.022. RLVR (outcome-only reward, lr 4e-6): 0.778, ECE 0.213 | 8,000-row held-out test split of the training mix | RTX 4080 16 GB |
| Qwen3-0.6B (anthonym21) | Two equally cued departments: mean max p 0.593 (ideal 0.5) vs 0.798 for the warmup | 3,000 synthetic tickets with known posteriors | same |
| Gemma 4 E2B (larkooo) | 28-field support triage: 4.41 s vs 15.66 s (3.55×), 15/17 annotated answers both ways; 64-option catalog: 3.27 s vs 2.46 s (0.75×) | 4 demo workloads, 4 runs each | Apple M5 |
| Gemma 4 E2B (larkooo) | Trained head: 23/64 test decisions vs 64/64 for the pretrained Gemma path | 16 synthetic test scenes | Apple Silicon |

The Qwen3-0.6B results are mean [min, max] over 3 runs (seed 0 on the RTX 4080, seeds 1 and 2 on a Colab A100); the export is the seed-0 run.
The author notes RLCD "held, not improved" calibration relative to the warmup, and that everything is in-distribution with prompts of at most 512 tokens.

## Running it

| Repo | Mac path (M5 Max, 128 GB) | Command |
|---|---|---|
| LFM2.5-350M | PyTorch on MPS, documented and measured on M2 Max. GGUF on llama.cpp Metal for plain generation only | `uv venv --python 3.11 .venv && uv pip install -r requirements.txt`; `Engine(device="mps", dtype="float16").constrained(text, schema)` |
| LFM2.5-350M GGUF | llama.cpp Metal | `llama-server -hf NANI-Nithin/LFM2.5-350M-RLCD-GGUF:Q4_K_M` (0.21 GB). No PCD |
| LFM2.5-2.6B | The engine accepts `device="mps"`, but the card documents and measures CUDA only (Mac unverified). Liquid publishes [LFM2.5-2.6B-MLX](https://huggingface.co/LiquidAI/LFM2.5-2.6B-MLX) for plain generation | `GIT_LFS_SKIP_SMUDGE=1 git clone https://huggingface.co/monotykamary/LFM2.5-2.6B-RLCD`, `uv pip install -r requirements-pcd.txt`, `Engine(device="cuda", dtype="float16", attention="sdpa")`. Modal scripts target one L40S |
| Qwen2.5-1.5B (harshatheg) | MLX, Apple Silicon only (macOS 14+) | `pip install -r requirements.txt`; `bash run.sh` (web UI on port 8000) or `run_parallel_generation(context, schema)`; downloads the 4-bit model, about 1.1 GB RAM |
| Qwen3-0.6B (anthonym21) | `Decider.load(path, device=...)` takes a device, default `"cuda"`. `pyproject.toml` pins the PyTorch cu128 index, so `uv sync` on macOS may fail (unverified). CPU or MPS inference untested by the author | `git clone https://github.com/anthony-maio/eve-rlcd && uv sync`; `hf download anthonym21/qwen3-0.6b-rlcd-decision --local-dir qwen3-rlcd-decision`; three questions in 66.1 ms on an RTX 4080 |
| Gemma 4 E2B (larkooo) | MLX, Apple Silicon only; Python 3.12+, ffmpeg for audio and video | `hf download larkooo/gemma-e2b-rlcd --local-dir gemma-e2b-rlcd`, `uv pip install '.[web]'`, `gemma-rlcd-web --model . --port 8787`; about 3.6 GB download |

## Scaling limits

- **LFM2.5-350M:** no cap on enum size in code; large sets "can exhaust memory". Base context 128,000 positions (`config.json`). Fields are scored independently.
- **LFM2.5-2.6B:** defaults of 32 fields, 256 total candidates, 4,096 shared-prompt tokens including the schema, 64 tokens per value. Over-limit requests are rejected.
- **Qwen2.5-1.5B (harshatheg):** up to 255 choices per enum; base context 32,768 tokens (card).
- **Qwen3-0.6B (anthonym21):** 26 options per question (one letter each). State left-truncated to 1,536 tokens, question to 448. Trained and evaluated on prompts of at most 512 tokens; calibration beyond about 500 is unmeasured.
- **Gemma 4 E2B (larkooo):** 32 named fields, 128 primitive decisions, 8,192 input tokens per request (errors, not truncation); 2–255 criteria. Up to 8 images, one audio clip (30 s) and one video (60 s silent, 32 frames).

## Fine-tuning

| Repo | Training code | Data and licence | Reported hardware, time, cost | Trains on Mac | HF Jobs flavor (estimate) |
|---|---|---|---|---|---|
| LFM2.5-350M | None; no training was done | n/a | n/a | n/a | To fine-tune the base yourself: t4-small ($0.40/h, 16 GB) fits a 354M full fine-tune |
| LFM2.5-2.6B | None; no training was done. `lfm25_pcd_modal.py` runs inference and benchmarks on one L40S | n/a | Benchmarks: 94 s and 80 s in-function on one L40S; billed time not stated | n/a | To fine-tune the base: LoRA on l4x1 ($0.80/h, 24 GB); full fine-tune on a100-large ($2.50/h, 80 GB) |
| Qwen2.5-1.5B (harshatheg) | None | n/a | n/a | n/a | n/a |
| Qwen3-0.6B (anthonym21) | Yes: [github.com/anthony-maio/eve-rlcd](https://github.com/anthony-maio/eve-rlcd), MIT, `main` @ `adb9a04`; data release tag `data-v1` @ `b97307a` | 6,400 SFT rows + 32,000 RL rows from Bitext customer support (CDLA-Sharing-1.0), Banking77 (CC-BY-4.0), AG News (licence unknown), MultiNLI (CC-BY-3.0 / CC-BY-SA-3.0 / MIT / other), SST-5 (no licence tag), Yelp reviews (Yelp dataset agreement, licence "other"), BoolQ (CC-BY-SA-3.0), plus synthetic tickets. Built set: [`anthonym21/rlcd-decision-v1`](https://huggingface.co/datasets/anthonym21/rlcd-decision-v1) (tagged CC-BY-4.0) | One RTX 4080 16 GB, Windows 11: warmup 493.8 s, RL 4,233.6 s (about 1.3 h total), peak VRAM 11,413 MB. Seeds 1 and 2 on Colab A100 | No: `train_sft.py` and `train_rl.py` hard-code `device="cuda"` and CUDA autocast | l4x1 ($0.80/h, 24 GB, bf16): about 2–3 h, about $2. t4-small fits 16 GB but lacks bf16 |
| Gemma 4 E2B (larkooo) | Head training only: `scripts/train_head.py` in [github.com/Larkooo/gemma-e2b-rlcd](https://github.com/Larkooo/gemma-e2b-rlcd), MIT, `main` @ `4ae799d`. Backbone frozen; supervised NLL, not RL | Synthetic pilot: 64 / 16 / 16 scenes (`examples/head-pilot/`, MIT) | 600 AdamW updates; time not stated | Yes: MLX on Apple Silicon is the only runtime | None: MLX does not run on HF Jobs (Linux CUDA) |

Liquid documents SFT, LoRA, DPO and GRPO for LFM models through LEAP Finetune, TRL and Unsloth ([docs](https://docs.liquid.ai/lfm/fine-tuning/overview)); none of the LFM2.5 repos here used them.

## Data governance

Not legal advice. All six are self-hosted only: no hosted API, no vendor, no DPA.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes, all six, on your infra | model cards |
| Fine-tuning | Only `anthonym21` publishes training code (CUDA). `larkooo` publishes head training (MLX). The others are inference-only | model cards, GitHub |
| Processing location | Your infra. `harshatheg`'s server binds `0.0.0.0:8000` by default; the `larkooo` UI binds `127.0.0.1:8787` and deletes uploads after each request | READMEs |
| EU processing option | n/a (self-hosted) | |
| Retention / ZDR | n/a. `monotykamary`'s engine discards request caches after each call | card |
| Training on inputs | No | |
| DPA / GDPR | n/a; no hosted service | |
| Certifications | None | |
| Weights licence | See below | |

**Commercial use:**

- **LFM2.5-350M, its GGUF, and LFM2.5-2.6B:** LFM Open License v1.0 ([text](https://huggingface.co/LiquidAI/LFM2.5-350M/blob/9e6c6ccf47cd318696e137d381a7ded8fe4df09f/LICENSE)). Section 5: commercial use is licensed only if you and your affiliates have under $10,000,000 annual revenue ("Threshold"). Above that, commercial use "is not licensed". Qualified non-profits are exempt for non-commercial and research use. Redistribution must include the licence and mark changed files. The engine code is MIT.
- **Qwen3-0.6B (anthonym21):** weights Apache-2.0 (from Qwen3-0.6B-Base), code MIT. Training data includes Yelp reviews under the Yelp dataset agreement and AG News with an unknown licence; check those before commercial use of a retrained model.
- **Gemma 4 E2B (larkooo):** weights Apache-2.0. Google links "Gemma 4 license" to its [Apache 2.0 page](https://ai.google.dev/gemma/apache_2), and `google/gemma-4-E2B-it` is tagged `apache-2.0`. The `mlx-community` conversion card carries the tag `gemma`. Code and synthetic examples MIT.
- **Qwen2.5-1.5B (harshatheg):** repo Apache-2.0, code only. The 4-bit weights it downloads come from `mlx-community` under Qwen2.5-1.5B-Instruct's Apache-2.0 licence (unverified for the mlx-community copy).

## Caveats

- Four of six repos use "RLCD" in the name with no training. Their probabilities are base-model likelihoods. The LFM2.5 cards state this; the `harshatheg` card does not.
- Every author-reported accuracy comes from 12–8,000 items written or assembled by the author. Only the three DI rows are third-party.
- The 577 likes on `harshatheg/Qwen-2.5-1B-RLCD` are the most of any repo here, on a repo with no weights.
- LFM2.5-2.6B always opens `<think>`. The PCD prompt supplies an empty reasoning span, which "is not an officially supported" mode and "can hurt accuracy" (card).
- The LFM2.5-2.6B BF16 path failed the author's hidden-state check; FP16 is the tested precision.
- The Qwen3-0.6B tied embedding means the export "does not make generation physically impossible" (`decision.json`).
- The landscape row for `notnotsamuel/LFM2.5-350M-RLCD` lists "JevBench v1.2 82.62%". That number is not in the repo's card or `results/REPORT.md` (unverified).

## Sources

- HF model cards and API (`/api/models/<repo>`: sha, createdAt, downloads, likes, siblings): [notnotsamuel/LFM2.5-350M-RLCD](https://huggingface.co/notnotsamuel/LFM2.5-350M-RLCD) (README, `RELEASE_MANIFEST.json`, `BASE_MODEL_MANIFEST.json`, `config.json`, `LICENSE`, `LICENSE-CODE`, `results/REPORT.md`, `docs/EXECUTION_NOTES.md`, `docs/IMPLEMENTATION_REVIEW.md`); [NANI-Nithin/LFM2.5-350M-RLCD-GGUF](https://huggingface.co/NANI-Nithin/LFM2.5-350M-RLCD-GGUF); [monotykamary/LFM2.5-2.6B-RLCD](https://huggingface.co/monotykamary/LFM2.5-2.6B-RLCD) (README, `docs/pcd-results.md`, `lfm25_pcd_modal.py`, `pcd/engine.py`); [harshatheg/Qwen-2.5-1B-RLCD](https://huggingface.co/harshatheg/Qwen-2.5-1B-RLCD) (README, `MODEL_CARD.md`, `core/engine_mlx.py`, likers API); [anthonym21/qwen3-0.6b-rlcd-decision](https://huggingface.co/anthonym21/qwen3-0.6b-rlcd-decision); [larkooo/gemma-e2b-rlcd](https://huggingface.co/larkooo/gemma-e2b-rlcd) (README, `docs/training.md`, `model-source.json`, `checkpoint-provenance.json`, `reports/head-pilots/`, `gemma_rlcd/core.py`)
- GitHub: [anthony-maio/eve-rlcd](https://github.com/anthony-maio/eve-rlcd) (README, LICENSE, `pyproject.toml`, `rlcd/train_rl.py`, `rlcd/train_sft.py`, `rlcd/decide.py`; `main` @ `adb9a04`); [Larkooo/gemma-e2b-rlcd](https://github.com/Larkooo/gemma-e2b-rlcd) (LICENSE; `main` @ `4ae799d`)
- HF Space [drinkmoonshine/parallel-constrained-decoding](https://huggingface.co/spaces/drinkmoonshine/parallel-constrained-decoding); HF user overview `harshatheg`
- Dataset licence tags (HF API): `bitext/Bitext-customer-support-llm-chatbot-training-dataset`, `legacy-datasets/banking77`, `fancyzhx/ag_news`, `nyu-mll/multi_nli`, `SetFit/sst5`, `Yelp/yelp_review_full`, `google/boolq`, `anthonym21/rlcd-decision-v1`
- [HF download stats](https://huggingface.co/docs/hub/models-download-stats); [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing)
- Licences: [LFM Open License v1.0](https://huggingface.co/LiquidAI/LFM2.5-350M/blob/9e6c6ccf47cd318696e137d381a7ded8fe4df09f/LICENSE); [Gemma Apache 2.0 page](https://ai.google.dev/gemma/apache_2); `google/gemma-4-E2B-it` HF API
- Liquid AI [fine-tuning overview](https://docs.liquid.ai/lfm/fine-tuning/overview)
- [Decision Index Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) (`data/index-v0.2.1.json` generated 2026-09-28)

All read 2026-10-02.

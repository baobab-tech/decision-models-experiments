# Intern-Decision (InternLM)

| Field | Value |
|---|---|
| Vendor | InternLM (`internlm` on HF and GitHub). The FluidInference Core ML card names Shanghai AI Laboratory (unverified from a primary InternLM source) |
| Type | Decision model: probabilities for typed questions (Choice, Score, Noul) over text and up to 8 images, no generated text |
| Backbone | Qwen3.5 instruct checkpoints (`Qwen/Qwen3.5-0.8B`, `-2B`, `-4B`); language model fine-tuned, vision tower and projector frozen |
| Size | 0.8B: 852,985,920 params; 2B: 2,213,241,664; 4B: 4,539,265,536 (safetensors metadata) |
| Licence | Apache-2.0 (weights and GitHub code); `LICENSE-QWEN` (Apache-2.0) kept in each repo |
| Run it via | Weights only. `DecisionEngine` from each repo's `inference.py` (HF Transformers); GitHub repo with an HTTP server (`POST /v1/decisions`). No hosted API |
| Status | All three created on HF 2026-09-26 (05:35–05:36 UTC). No launch blog or paper found |

Checked 2026-10-02.

## Overview

Intern-Decision takes a `state`, 1–16 named typed questions and optional images, and returns a distribution for every question in one forward pass ([4B card](https://huggingface.co/internlm/Intern-Decision-4B)).
It maps each question's options to single-token symbols `A`–`Z`, `a`–`z`, `0`–`9` (62 symbols).
The prompt ends with a JSON skeleton holding one `<decision>` token per field.
The logit just before each `<decision>` token, restricted to that field's symbols, gives the answer.
A per-checkpoint temperature then rescales the probabilities without changing the argmax.
Training uses the same layout with full-vocabulary cross-entropy; the vision tower and projector stay frozen ([GitHub README](https://github.com/internlm/Intern-Decision)).
Training data, private calibration and validation records are not released; [docs/DATA.md](https://github.com/internlm/Intern-Decision/blob/main/docs/DATA.md) says it "does not disclose the models' training data sources, composition, quantities, or mixing proportions".

| Checkpoint | HF sha | Params | Weights on disk | Temperature | Downloads (30 days) | Likes |
|---|---|---:|---:|---:|---:|---:|
| [Intern-Decision-0.8B](https://huggingface.co/internlm/Intern-Decision-0.8B) | `85a0cc5` | 0.85B | ~1.7 GB | 2.747761 | 1,159 | 26 |
| [Intern-Decision-2B](https://huggingface.co/internlm/Intern-Decision-2B) | `8797836` | 2.21B | ~4.4 GB | 2.100509 | 575 | 15 |
| [Intern-Decision-4B](https://huggingface.co/internlm/Intern-Decision-4B) | `0e5e6aa` | 4.54B | 9.07 GB | 1.992418 | 1,607 | 73 |

Disk sizes for 0.8B and 2B are DI's `trained_bytes`; 4B is the sum of the HF file sizes.

## Schema

Same request as TypeSafe: `state` + `questions` (+ optional `images`) → `model` + `answers` + `usage` ([4B card](https://huggingface.co/internlm/Intern-Decision-4B)).

- **Choice:** `criteria` ordered object of value → description; 1–62 options. Returns `choice`, `probabilities`, `confidence`, `decision`.
- **Score:** `criteria` list (values become `"0"`, `"1"`, …) or object with numeric string keys; 1–62 levels. `score` is the probability-weighted expected value; `confidence` belongs to the most likely level; also `legend`.
- **Noul:** options `no`, then `yes`; optional `criteria` with `no`/`yes` or `false`/`true` keys. `noul` = P(yes).
- `confidence` = maximum calibrated probability. Ties break lexically.
- Extension fields: `backend`, `timing`, `calibration`. `usage.output_tokens` counts scored fields.
- The request `model` field does not switch checkpoints.
- TypeSafe compatibility: yes for the request and response shape, in-process. The GitHub server exposes `POST /v1/decisions` (alias `/v1/jev`), not `/v1/systemone`.
- No multi-label primitive; ask one Noul per label.

## Benchmarks

Decision Index 0.2.1 ([Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) `data/index.json`, generated 2026-09-28; [benchmarks-leaderboards.md](../benchmarks-leaderboards.md)):

| Entrant | Balanced skill (rank of 71) | ECE | Median ms | p95 ms |
|---|---:|---:|---:|---:|
| Jev 1.13.0 | 57.91 (#1) | 0.074 | 524.1 | — |
| Intern-Decision-4B | 37.81 (#28) | 0.028 | 44.2 | 115.4 |
| Intern-Decision-2B | 19.38 (#46) | 0.061 | 33.5 | 58.0 |
| Intern-Decision-0.8B | 11.94 (#52) | 0.025 | 33.7 | 39.2 |

- DI category skill, 4B vs Jev: Knowledge & Reasoning 23.7 vs 51.4; Language Understanding 41.9 vs 62.0; Retrieval & Classification 40.3 vs 55.4; Tools & Automation 55.7 vs 75.1; Arts & Human Taste 26.1 vs 37.7.
- The board ran the torch fallback because `causal-conv1d` was absent; the published latency is from the fast path.
- Intern-Decision is not on JevBench v1.5.4, kyr0, 4nt0ineB or Fastino fast-decisions (checked 2026-10-02).

Self-reported, seven suites ([GitHub README](https://github.com/internlm/Intern-Decision); 10,751 rows, 12,351 decisions; accuracy %; Brier and ECE on JevBench-Hard, 111 items; XTuner backend):

| Model | Easy | Original | Hard | Typed Decision | ToolACE | AG News | WildJailBreak | Average | Brier | ECE |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Jev | 100.00 | 98.61 | 72.07 | 73.35 | 91.29 | 89.57 | 96.29 | 88.74 | 0.358 | 0.095 |
| JevK5 | 100.00 | 97.22 | 73.87 | 64.50 | 80.97 | 89.13 | 90.45 | 85.16 | 0.366 | 0.047 |
| SemIf | 100.00 | 98.61 | 61.26 | 62.80 | 85.16 | 89.22 | 92.53 | 84.23 | 0.498 | 0.112 |
| Intern-Decision-4B | 100.00 | 98.61 | 73.87 | 80.55 | 96.45 | 90.82 | 89.86 | 90.02 | 0.347 | 0.065 |
| Intern-Decision-2B | 100.00 | 84.72 | 63.96 | 79.35 | 96.45 | 89.96 | 78.33 | 84.68 | 0.437 | 0.100 |
| Intern-Decision-0.8B | 97.92 | 80.56 | 52.25 | 77.35 | 94.52 | 88.61 | 64.48 | 79.38 | 0.530 | 0.066 |

- Easy / Original / Hard are the 231 public JevBench items (48 / 72 / 111).
- "Typed Decision" is `LocalLLaMA/typed-decisions` (400 rows, 2,000 decisions). Its card says scores well above 0.735 (teacher self-agreement) "mean a model is learning the teacher's quirks" ([dataset card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions)); 4B reports 80.55%.
- Known-distribution calibration pilot (96 cases, exact reference distributions, bundled in the repo): 4B Brier / ECE 0.628 / 0.213 raw, 0.550 / 0.089 calibrated; Jev 0.595 / 0.130.
- Latency, one RTX 4090, BF16, 289-token request with 3 fields: 0.8B 33.44 ms, 2B 33.15 ms, 4B 44.03 ms median; Jev 106.30 ms (HTTPS).

## Running it

Reference path (Linux, Python 3.12+, CUDA in the docs):

```bash
hf download internlm/Intern-Decision-4B --revision 0e5e6aa7d6d750e2b1504ba11a8136cb58aeb3cd --local-dir intern-decision-4b
cd intern-decision-4b
pip install -r requirements.txt   # torch==2.9.1, torchvision==0.24.1, transformers==5.14.1, Pillow
```

```python
from inference import DecisionEngine
engine = DecisionEngine(device="cuda")   # temperature preset for this size is built in
response = engine.predict({
    "state": "The customer was charged twice and asks for the extra payment back.",
    "questions": {
        "team": {"type": "choice", "instructions": "Which team should handle this request?",
                 "criteria": {"billing": "Payments and refunds", "delivery": "Shipping and delivery"}},
        "urgency": {"type": "score", "instructions": "Rate the priority.", "criteria": ["Low", "Medium", "High"]},
        "refund_requested": {"type": "noul", "instructions": "Is the customer asking for a refund?"}}})
print(response["answers"])
```

- HTTP server and browser demo: clone [the GitHub repo](https://github.com/internlm/Intern-Decision), `export MODEL_CHECKPOINT=...`, `bash scripts/demo.sh`, then `http://127.0.0.1:7860`. Loopback by default, no request-content logging, no auth.
- The HF Space [`internlm/Intern-Decision`](https://huggingface.co/spaces/internlm/Intern-Decision) (0.8B, `cpu-basic`) was paused on 2026-10-02.
- The fast path for Qwen3.5's linear-attention layers needs `flash-linear-attention` and `causal-conv1d` (CUDA); otherwise transformers falls back to plain torch.

Mac paths on the M5 Max, 128 GB (none tested here):

| Path | Repo | Notes |
|---|---|---|
| PyTorch MPS | upstream `inference.py` | `DecisionEngine(device="mps")` is accepted by the code (`torch.device(device)`, CUDA sync only when CUDA), but MPS is not documented; linear attention would run the torch fallback (unverified) |
| Core ML, text only | [`FluidInference/intern-decision-0.8b-coreml`](https://huggingface.co/FluidInference/intern-decision-0.8b-coreml) (`08239aa`) | 0.8B only, from snapshot `85a0cc5`; fp16 and int8 packages for 320–1,024 tokens and up to 16 fields; macOS 14+; Swift runtime in FluidUse. Int8: 2 of 240 answers differ from the reference |
| GGUF + llama.cpp | [`bombdefuser-124/Intern-Decision-4B-GGUF`](https://huggingface.co/bombdefuser-124/Intern-Decision-4B-GGUF) (`0b1dc0b`; FP16, Q8_0, `mmproj-f16`); 0.8B and 2B repos from the same uploader | No decision adapter shipped: you build the prompt and read the restricted symbol logits yourself. Temperature was fitted on BF16 |

## Scaling limits

- **Options:** 62 per Choice or Score (single-token symbols).
- **Questions per call:** 1–16, all in one forward pass.
- **Images:** up to 8 per request; image tokens count toward the length limit.
- **Context:** `max_length` 8,192 tokens by default; longer inputs are rejected, not truncated. The backbone config allows 262,144 positions; DI ran with `max_length` 262144.
- **Batching:** one request per `predict` call.
- **Memory:** BF16 weights about 1.7 GB (0.8B), 4.4 GB (2B), 9.1 GB (4B).

## Fine-tuning

- Supported with your own data: the GitHub repo ships an XTuner training launcher (`scripts/train.sh`, `configs/training/qwen35.py`) for dense Qwen3.5 0.8B, 2B, 4B and 9B ([README](https://github.com/internlm/Intern-Decision#training-on-your-own-data)).
- Tested setup: Linux, CUDA, torch 2.6.0, transformers 4.57.0, flash-attn 2.8.3, XTuner pinned to `fb51bae`, 4 GPUs (`NPROC_PER_NODE=4`).
- Temperature fitting: `src.eval.collect`, `src.eval.fit` (NLL on calibration data only), `src.eval.replay` (checks zero changed decisions).
- No Mac training path.

## Data governance

Not legal advice.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; self-hosted = your infra, air-gapped after download | [4B card](https://huggingface.co/internlm/Intern-Decision-4B) |
| Fine-tuning | Yes, on your hardware with the GitHub training code | [GitHub README](https://github.com/internlm/Intern-Decision) |
| Processing location | Your machine. No hosted API. The demo Space ran on HF (`cpu-basic`) and is paused | [Space API](https://huggingface.co/api/spaces/internlm/Intern-Decision), 2026-10-02 |
| EU processing option | Your choice of hardware. HF Inference Endpoints offer AWS `eu-west-1`; `inference.py` needs a custom handler | [open-reproductions.md](open-reproductions.md#data-governance) |
| Retention / ZDR | Nothing leaves your machine when self-hosted. The demo server deletes uploads after inference and does not log request content | [GitHub README](https://github.com/internlm/Intern-Decision#browser-demo-and-http-api) |
| Training on inputs | No, when self-hosted | |
| DPA / GDPR | No processor, so no DPA needed when self-hosted | |
| Certifications | None | |
| Weights licence | Apache-2.0; derived from Qwen3.5 (Apache-2.0, `LICENSE-QWEN` kept) | [4B card](https://huggingface.co/internlm/Intern-Decision-4B), [Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) |

- The GitHub demo has an optional "external thinking handoff", off by default. When enabled with `LLM_BASE_URL` and `LLM_API_KEY`, request evidence goes to that provider. Leave it off for private data.
- `inference.py` is imported from the downloaded repo; pin the revision and read it first.
- Training data is undisclosed, so its licence and any overlap with DI test sets cannot be checked.

## Caveats

- No blog, paper or technical report found as of 2026-10-02; the GitHub README is the only method description.
- Self-reported average (4B 90.02% vs Jev 88.74%) and DI (4B 37.81 vs Jev 57.91) disagree by a wide margin. The seven self-reported suites are mostly classification and JevBench public items.
- The 4B card lists `Qwen/Qwen3.5-4B` (instruct) as the base and the Space says "instruction-tuned/chat checkpoint"; DI lists `Qwen3.5-4B-Base`.
- Served parameter counts on DI (0.87B, 2.27B, 4.66B) differ from safetensors metadata (0.85B, 2.21B, 4.54B).
- 62-option cap per question.
- The vendor link to Shanghai AI Laboratory comes from a third-party card only.

## Sources

- InternLM HF: [Intern-Decision-0.8B](https://huggingface.co/internlm/Intern-Decision-0.8B), [-2B](https://huggingface.co/internlm/Intern-Decision-2B), [-4B](https://huggingface.co/internlm/Intern-Decision-4B) cards, `inference.py`, `requirements.txt`, `config.json`, `LICENSE`, `LICENSE-QWEN`; HF API for each (`downloads`, `likes`, `sha`, `createdAt`); [collection](https://huggingface.co/collections/internlm/intern-decision); [Space](https://huggingface.co/spaces/internlm/Intern-Decision) README and API
- GitHub [internlm/Intern-Decision](https://github.com/internlm/Intern-Decision): README, `README_zh-CN.md`, `LICENSE`, [docs/DATA.md](https://github.com/internlm/Intern-Decision/blob/main/docs/DATA.md) (read via raw.githubusercontent.com)
- Community builds: [bombdefuser-124/Intern-Decision-4B-GGUF](https://huggingface.co/bombdefuser-124/Intern-Decision-4B-GGUF), [FluidInference/intern-decision-0.8b-coreml](https://huggingface.co/FluidInference/intern-decision-0.8b-coreml)
- Decision Index [Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) `data/index.json` (generated 2026-09-28); [LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions); JevBench [v1.5.4 JSON](https://benchmarkheaven.com/api/jevbench/v1.5.4) (no Intern-Decision row)

All read 2026-10-02.

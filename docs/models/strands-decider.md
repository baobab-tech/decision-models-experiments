# Strands Decider 2B (AWS Strands Labs)

| Field | Value |
|---|---|
| Vendor | Strands Labs, Amazon Web Services. Started as Marc Brooker's personal project "Hobson" |
| Type | Decision model: probabilities for typed questions (Choice, Score, Noul), no generated text. Text only |
| Backbone | Qwen/Qwen3.5-2B-Base, LM head removed, rank-16 LoRA plus a pointer head of about 1M parameters |
| Size | 1.9B parameters (README). The HF repo holds only the adapter and head; the base downloads separately (about 4.5 GB) |
| Licence | Apache-2.0 (code, adapter and head); base model Apache-2.0 |
| Run it via | `pip install strands-decider` (0.1.0); `strands-decider ask` or `strands-decider serve` (`POST /v1/systemone`) on CUDA, MPS or CPU. No hosted API |
| Status | Reference checkpoint v19. HF repo created 2026-09-30; launch blog 2026-10-01 |

Checked 2026-10-02.

## Overview

Strands Decider scores each option of a typed question by comparing the hidden state at the `<answer>` position with the hidden state at the option's last token ([README](https://github.com/strands-labs/strands-decider)).
The pointer head holds no per-option parameters, so the number of options is not capped by the weights.
All three question types come from one masked softmax.
The head runs in fp32; the torso runs in bf16.
Temperatures are fitted per question type on held-out short classification: Noul 0.911, Choice 0.734, Score 1.328 (`hobson_config.json`).
The state is encoded once and its cache is shared across questions; each extra question adds only its own tokens ([inference.md](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md#asking-many-questions-is-nearly-free)).
The design and the v1 to v19 history began as Brooker's "Hobson" ([Brooker, 2026-09-28](https://brooker.co.za/blog/2026/09/28/engineering-system-one.html)); AWS engineers then released it under Strands Labs ([TechCrunch, 2026-10-01](https://techcrunch.com/2026/10/01/amazon-releases-its-own-jev-clone-as-decision-models-flood-the-web/)).
v20 is the latest experiment and did not replace v19 (169 vs 168 of 231 at the 4096 window, inside retrain noise).

HF metadata, read 2026-10-02 ([API](https://huggingface.co/api/models/StrandsAgents/strands-decider-2B-hobson-v19)):

| Repo | Revision | Downloads (30 days) | Likes | Last modified |
|---|---|---:|---:|---|
| `StrandsAgents/strands-decider-2B-hobson-v19` | `bb282d7` | 0 (no root `config.json`, so HF does not count downloads) | 23 | 2026-10-01 |

`StrandsAgents` has no other model repos. PyPI `strands-decider` 0.1.0 was uploaded 2026-10-01 ([PyPI](https://pypi.org/project/strands-decider/)).

## Schema

`strands-decider serve` exposes `POST /v1/systemone`: `state` + `questions` → `answers` + `usage` (+ `latency_ms`). `model` is optional.

- **Noul:** returns `noul` (P(true)). Optional `criteria` `{"true": …, "false": …}`.
- **Choice:** `criteria` map; returns `choice`, `probabilities`, `confidence`.
- **Score:** `criteria` array, lowest first; returns `score` (expected level), the distribution, `confidence`.
- **Confidence:** the top probability rescaled so that an even split gives 0 and certainty gives 1, whatever the option count ([inference.md](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md#ask)). This differs from Jev's formula and from Clef's (top probability).
- `GET /health` returns the model name, checkpoint path, base model, device and temperature.
- JevBench's `typesafe` adapter ran against the server unchanged: 231 of 231 tasks, schema validity 1.000. The README adds: "Compatibility with the Jev API itself is not verified."
- Python: `strands_decider.modeling.StrandsDeciderModel.load("StrandsAgents/strands-decider-2B-hobson-v19")`. The `lora/` folder is a standard PEFT adapter.

## Benchmarks

Strands Decider is not on the JevBench board. The v1.5.5 board (109 ranked systems, read 2026-10-02) has no Strands or Hobson row ([board](https://benchmarkheaven.com/jev-models)). It has no Decision Index row either.

All figures below are the authors' own runs of the public JevBench v1 harness (231 public tasks, commit `1bcc55e`), not board scores:

| Run | Correct | Accuracy | Brier | ECE | Source |
|---|---:|---:|---:|---:|---|
| H100, window 4096 (the HF export) | 167/231 | 0.723 | 0.348 | 0.050 | [HF card](https://huggingface.co/StrandsAgents/strands-decider-2B-hobson-v19), `eval/jevbench-w4096/summary.json` |
| H100, window 3072 | 167/231 | 0.723 | 0.349 | 0.056 | same |
| RTX 3090, window 3072 (pre-registered) | 167/231 | 0.723 | 0.342 | 0.052 | [jevbench.md](https://github.com/strands-labs/strands-decider/blob/main/evaluation/jevbench.md) |
| RTX 3090, window 4096 | 168/231 | 0.727 | 0.342 | 0.051 | same |
| M3 Pro, MPS, window 4096 | 168/231 | 0.727 | 0.342 | 0.049 | [results.md](https://github.com/strands-labs/strands-decider/blob/main/evaluation/results.md#serving-on-a-mac-accuracy-and-latency) |

- Tiers on the repo's split (easy 48, standard 72, hard 111): 1.000 / 0.875 / 0.505.
- Six retrains of the v17 recipe had a standard deviation of 3.2 tasks; the authors treat differences under about 10 tasks as unresolved.
- Against the v1.4.2 board (89 systems, 2026-09-25), 0.723 would rank 50th overall and 3rd of 33 at about 2B. Ahead of it: FlyMy.AI `decision-2b` 0.753 and `system-one-open` 0.732. The blog's "1st of 30" excludes those two and `smalljev` as "just over 2B".
- `decider-2b` (Mapika) uses the same torso. Its board entry is 164/231; its v11 release scores 175/231 on the Strands harness.
- For scale: the v1.4.2 board's public-task accuracy for the leaders is 0.83–0.93 (12B and up) and 0.996 for GPT-6 Luna.
- On the v1.5.5 board, `decider-2b` (same torso) has JevBench Score 45.1 (#32) and Jev 1.13.0 72.1 (#3) ([aggregate JSON](https://benchmarkheaven.com/api/jevbench/v1.5.5)). [benchmarks-leaderboards.md](../benchmarks-leaderboards.md) lists v1.5.4, where `decider-2b` is #30.
- Internal held-out sets (HF card, n per set): short tasks 0.641 (6,000), ContractNLI 0.872 (1,026), MuSiQue 0.884 (1,199), HotpotQA 0.717 (959), boardgame 0.822 (900).
- Calibration claim: on unseen short classification tasks, answers at confidence ≥ 0.9 are right about 95% of the time. On JevBench, all 53 answers at ≥ 0.9 were right.

## Running it

```bash
uv add strands-decider==0.1.0
uv run strands-decider ask StrandsAgents/strands-decider-2B-hobson-v19 --device mps \
  --state "Help! My payouts have been failing for 3 days! " \
  --choice "Which team should handle this?=billing,sales,retail" \
  --noul "Does this convey urgency?" \
  --score "How frustrated is the writer?=calm,frustrated,depressed"
```

Documented output: `noul` 0.829; `choice` → `billing` 0.846 (confidence 0.769); `score` 1.10 (confidence 0.519).

Server, bound to `127.0.0.1` with no authentication:

```bash
uv run strands-decider serve StrandsAgents/strands-decider-2B-hobson-v19 --device mps --port 8000
curl -s localhost:8000/v1/systemone -H 'content-type: application/json' -d '{
  "state": "Help! My payouts have been failing for 3 days!",
  "questions": {"is_urgent": {"type": "noul", "instructions": "Does this convey urgency?"}}}'
```

- **Mac (M5 Max, 128 GB):** PyTorch MPS, bf16. The authors measured an M3 Pro (36 GB) with torch 2.7.1, transformers 5.17.0, peft 0.21.0, Python 3.12 ([inference.md](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md#serving-on-a-mac)). `flash-linear-attention` has no macOS build; the package ships its own MPS kernel for the Gated DeltaNet chunk rule (1.7× faster forward). The `causal_conv1d` fallback costs 32 ms per forward.
- **Mac latency (M3 Pro):** warm median 153 ms under 300 tokens; 234 ms median and 2,628 ms p95 across JevBench. MPS compiles per input length, so a first request of a new length takes 310 ms (under 300 tokens) to 3,836 ms (2,500–5,000 tokens).
- **CUDA latency:** RTX 3090 under WSL2, median 115 ms, p95 299 ms per JevBench question.
- No MLX, GGUF or ONNX build exists.
- **Pin the base:** the loader fetches `Qwen/Qwen3.5-2B-Base` at `main` with no revision. `provenance.json` records `b1485b2` as the inferred training-time revision.

## Scaling limits

- **Options:** no cap from the head; each option adds its tokens to the input.
- **Context:** 4,096-token window (`max_length` in `hobson_config.json`). The question's tokens are reserved first, then the state is truncated to fit. Training rows were at most 3,072 tokens.
- **Questions per call:** no documented maximum. With the shared-prefix cache, 8 questions over a ~2,000-token state took 369 ms and 16 took 445 ms on an RTX 3090 (v14).
- **Concurrency:** "behaviour under concurrent requests is not verified". Local experiments only.
- **Weak spots (authors):** long multi-step documents (hard tier 0.505; `long_policy` 0.368, `temporal_numeric` 0.267); with state and options fixed, a changed question often gets the same answer; Score and Noul transfer poorly to rubrics unlike the training mix.

## Fine-tuning

- The full recipe is open: `training/recipe.sh all` builds the corpora, trains, calibrates and evaluates ([training README](https://github.com/strands-labs/strands-decider/blob/main/training/README.md)).
- Hardware: Linux or WSL2 with NVIDIA GPUs; it needs `flash-linear-attention` (Triton). About 11 hours on one RTX 3090 (24 GiB), or 1 h 10 min on eight H100s with `NGPU=8 FAST=1`. The v19 export trained on a `p5.48xlarge` in 1,685 s (4,204 s for the whole recipe).
- Training on a Mac is not supported; MPS is inference only.
- Objective: one epoch of cross-entropy to gold options, shuffled options, KL to the frozen torso (weight 0.3), and KL replay toward an earlier checkpoint (v14) on multi-step documents ([Brooker](https://brooker.co.za/blog/2026/09/28/engineering-system-one.html), [HF card](https://huggingface.co/StrandsAgents/strands-decider-2B-hobson-v19)).
- Data: 29 public Hub datasets (listed in the card), ContractNLI and MuSiQue from their authors, synthetic rows from open-weight models (Qwen3.5-27B, checked by Qwen3.5-397B per Brooker), and `Qwen/Qwen3.5-4B` output distributions as soft targets. `data/sources.md` lists each source with its revision and licence.
- Recalibrate after training: `strands-decider calibrate` fits the per-type temperatures. The README advises fitting on a sample of your own traffic.

## Data governance

Not legal advice. Open weights only; there is no hosted API. Self-hosted = your infrastructure.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; adapter and head on HF, base from `Qwen/Qwen3.5-2B-Base` | [HF card](https://huggingface.co/StrandsAgents/strands-decider-2B-hobson-v19) |
| Fine-tuning | Yes; full recipe and data inventory in the repo | [GitHub](https://github.com/strands-labs/strands-decider) |
| Processing location | Your machine. The local server binds `127.0.0.1` | [inference.md](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md#serve) |
| EU processing option | n/a (no hosted service) | |
| Retention / ZDR | n/a; the server keeps no request log (unverified) | |
| Training on inputs | n/a | |
| DPA / GDPR | n/a | |
| Certifications | n/a | |
| Weights licence | Apache-2.0. Training sources include Hub datasets tagged CC-BY-SA, `other`, `unknown` or untagged; check a source's terms before redistributing data built from it | [`LICENSE.md`](https://huggingface.co/StrandsAgents/strands-decider-2B-hobson-v19/blob/main/LICENSE.md) |

Local use keeps all data on the Mac. The first run downloads the base model from Hugging Face.

## Caveats

- The JevBench numbers are the authors' runs of the public 231 tasks, not the board's composite. The board adds 720 sealed items, speed and cost. Strands Decider has no board row as of 2026-10-02.
- TechCrunch says Hobson "briefly reached the top spot on the Jevbench ranking" for its size. Brooker's own footnote says "joint first of 30 at 2B or below on the v1.4.2 board" with `decider-2b` v10, from his own harness run.
- Sources disagree on v19's figures: the HF card gives Brier 0.348 and ECE 0.050 (H100, 4096 window); the GitHub README gives 0.342 and 0.052 (RTX 3090, 3072 window). The card reports 167/231 at both windows; the repo reports 168 at 4096.
- The authors ran the JevBench harness on Windows with one disclosed patch (`fcntl` import replaced by a no-op).
- Not documented: maximum questions per request, behaviour under concurrency, multilingual accuracy.
- HF reports 0 downloads because the repo has no root `config.json`; usage is unknown.

## Sources

- Strands: [launch blog](https://strandsagents.com/blog/introducing-strands-decider/) (2026-10-01); GitHub [`strands-labs/strands-decider`](https://github.com/strands-labs/strands-decider) README, [docs/inference.md](https://github.com/strands-labs/strands-decider/blob/main/docs/inference.md), [docs/architecture.md](https://github.com/strands-labs/strands-decider/blob/main/docs/architecture.md), [evaluation/jevbench.md](https://github.com/strands-labs/strands-decider/blob/main/evaluation/jevbench.md), [evaluation/results.md](https://github.com/strands-labs/strands-decider/blob/main/evaluation/results.md), `pyproject.toml`; [PyPI `strands-decider`](https://pypi.org/project/strands-decider/)
- Hugging Face: [StrandsAgents/strands-decider-2B-hobson-v19](https://huggingface.co/StrandsAgents/strands-decider-2B-hobson-v19) (README, `hobson_config.json`, `lora/adapter_config.json`, `provenance.json`, `LICENSE.md`, `eval/jevbench-w4096/summary.json`, `eval/jevbench-w3072/summary.json`, HF API)
- Marc Brooker, [Small Decisions: Engineering a Leading Model](https://brooker.co.za/blog/2026/09/28/engineering-system-one.html) (2026-09-28)
- TechCrunch, [Amazon releases its own Jev clone as decision models flood the web](https://techcrunch.com/2026/10/01/amazon-releases-its-own-jev-clone-as-decision-models-flood-the-web/) (2026-10-01)
- [JevBench v1.5.5 board](https://benchmarkheaven.com/jev-models) and [aggregate JSON](https://benchmarkheaven.com/api/jevbench/v1.5.5)

All read 2026-10-02.

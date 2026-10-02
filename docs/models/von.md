# Von (wfzyx)

| Field | Value |
|---|---|
| Vendor | wfzyx (Victor Hugo Panisa), independent developer |
| Type | Open-weight encoder decision model: probabilities for typed questions (Choice, Score, Noul), no generated text |
| Backbone | `answerdotai/ModernBERT-large` (28 layers, hidden 1,024, 8,192-token context) plus an "Option-Marker" scoring head |
| Size | 395M parameters; `model.safetensors` 1.58 GB and `option_marker.pt` 1.58 GB (FP32) |
| Licence | Apache-2.0 (weights and code) |
| Run it via | `pip install "von-sdk>=1.3.7"`, then `von serve` (`POST /v1/systemone`, TypeSafe wire format); Docker `ghcr.io/wfzyx/von:cpu`; npm `von-sdk` |
| Status | Card version 1.3 (`von-1.3.0`, weights unchanged from 1.2). HF repo created 2026-09-19; revision `498ceba` (updated 2026-10-02); 80,938 downloads (30 days), 53 likes |

Checked 2026-10-02.

## Overview

Von answers Choice, Noul and Score questions over a JSON or text `state` in one encoder pass per question ([model card](https://huggingface.co/wfzyx/von)).
The state, the question and every option are packed into one sequence.
Each option gets a `[MASK]` marker, a small head scores each marker's final hidden state, and a softmax over the markers gives the distribution.
Noul is a two-option Choice over "holds / is false" descriptions or the caller's `criteria`.
Score is a Choice over level descriptions, with the expectation taken over the distribution.
Since version 1.2, each option attends only to the shared premise and its own tokens, so option order does not change the answer: on 111 JevBench hard items × 4 orderings, 1.1 flipped 49.5% of answers and 1.2 flipped none ([card](https://huggingface.co/wfzyx/von)).
Von is English only.
The card lists the old repo id `wfzyx/von-1.0`, which now redirects.

Training (card): ModernBERT-large fine-tuned with listwise softmax cross-entropy plus Brier loss on a ~290k-item decision corpus, then continue-trained on synthetic two-hop and numeric sets.
The corpus mixes IT triage, Banking77 routing, security screening, moderation, sentiment (dair-ai/emotion), triage, and ANLI R1–3 plus WANLI (~15%).
Corpus builders are in [`training/`](https://github.com/wfzyx/von/tree/main/training).
The card states no JevBench item is used for gradient training.
The shipped calibration map was fitted on the 231 public JevBench items.

Version 1.3 adds "chain-of-options": a regex proposer finds dates, durations and amounts in the state, a fixed operator library computes them (`add_duration`, `prorate`, `elapsed_hours` and others), and Von picks among candidate spans ([GitHub README](https://github.com/wfzyx/von)).

## Schema

`von serve` exposes `POST /v1/systemone`, described as "byte-compatible with the TypeSafe specification": `model` + `state` + `questions` → `answers` + `usage` ([GitHub README](https://github.com/wfzyx/von)).
Clients switch from Jev by changing the base URL (`VON_BASE_URL`); `VON_API_KEY` turns on bearer auth.

- **Choice:** `criteria` object; returns `choice`, `probabilities`, `confidence`.
- **Score:** ordered `criteria` array; returns `score` (probability-weighted expected level), `probabilities`, `legend`, `confidence`.
- **Noul:** optional `criteria` `{"true": …, "false": …}`; returns `noul` and `noul_raw`.
- **Choice `confidence`:** `(n × p_max − 1) / (n − 1)`, the formula the code calls TypeSafe's ([`option_marker_backend.py`](https://github.com/wfzyx/von/blob/main/src/von/backends/option_marker_backend.py)).
- **Noul `band` rule (default since 1.3.3):** `noul` is mapped to `0.8 + 0.1 × (p − 0.5)`, mirrored below 0.5, so every answer lands outside JevBench's 0.2–0.8 abstention band. `noul_raw` keeps the calibrated posterior; `--noul-decision raw` returns it as `noul`.
- **Extras:** `usage.input_tokens` is the real token count over every encoder pass; a truncated state carries a `truncation` field and `X-Von-Truncated` header.
- **Python API:** `von.decide`, `von.judge`, `von.rate`, `von.system_one`; TypeScript mirrors it.

## Benchmarks

| Board | Version | Result | Source |
|---|---|---|---|
| JevBench v1.5.4 | "Von (wfzyx, Option-Marker 395M)", evaluator CPU | rank 105 of 106; score 0.0 (Intelligence 0.0, Calibration 83.5, Speed 75.7, Cost 82.7); p50 0.386 s raw | [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#jevbench-v154-headline-a), [API](https://benchmarkheaven.com/api/jevbench/v1.5.4) |
| JevBench v1.4 | 1.2 weights | composite 27.5 (I 34.5, C 75.7, S 70.5, K 77.8); sealed 0.279 | [card](https://huggingface.co/wfzyx/von) |
| typed-decision-bench (kyr0) | Von 1.1, H200, FP32 | soft acc. 48.57%, hard acc. 49.58%, ECE-15 0.372, p50 38.5 ms, 3.8 GB VRAM (Jev 1.13.0: 88.08%) | [benchmarks.md](../benchmarks.md#typed-decision-bench-kyr0-275-capabilities) |
| Decision Index 0.2.1 | none | no row on the board (`data/index.json` generated 2026-09-28) | [DI Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) |

- JevBench v1.5.4 zeroes Von's Intelligence axis: open-half Choice competence 34.4, but sealed-half intelligence −16.6 and open-to-sealed gap 14.7 points ([API](https://benchmarkheaven.com/api/jevbench/v1.5.4), read 2026-10-02).
- The card attributes the zero to the v1.5 Noul abstention rule: nearly every 1.2 Noul answer fell in the 0.2–0.8 band. It reports the `band` rule moves public Noul competence from −76.5 to +18.9; the board row awaits re-measurement (JevBench issue #143, unverified).
- Author-run, not on any board ([card](https://huggingface.co/wfzyx/von), [repo `docs/benchmarks.md`](https://github.com/wfzyx/von/blob/main/docs/benchmarks.md)):
  - Decision Index 0.2.1: 13.74 balanced skill (raw 34.11, coverage 99.96%), p50 32.8 ms on A10G. That would sit above every encoder on the board, where all score below 12 ([model-classes.md](../model-classes.md)).
  - jabr v2 (49 tasks, 869 cases): 72.0% macro, Choice macro 83.0% (Von 1.1); Jev 1.13 96.6%.
  - ViZDoom Defend the Center, 8 seeds zero-shot: 9.00 kills per episode at ~18 ms per decision; Jev 1.13 5.62.
  - Latency under JevBench protocol (1.2): raw p50 0.096 s on 4-vCPU Xeon 8488C (OpenVINO), 0.023 s on A10G ([`results/speed_remeasure.md`](https://github.com/wfzyx/von/blob/main/results/speed_remeasure.md), 2026-09-27).
  - Confidence gate at 0.80 on held-out jabr v2 plus coding-agent probes: Choice keeps 25% of items at 92.4% accuracy (n = 702).
- The card states the calibration map is in-sample on JevBench public (Calibration axis 77.4 in-sample, 67.6 split-half) and "does not carry to other distributions".

## Running it

```bash
uv add von-sdk                      # PyPI von-sdk 1.3.7, Python >= 3.12, uploaded 2026-10-02
uv run von serve --host 127.0.0.1 --port 8000 --device mps
curl -s localhost:8000/v1/systemone -H 'Content-Type: application/json' -d '{
  "model": "von-1.3.0",
  "state": {"error": "Disk volume /var/log at 98% capacity."},
  "questions": {
    "needs_action": {"type": "noul", "instructions": "Does this require operational intervention?"},
    "team": {"type": "choice", "instructions": "Who owns this?",
             "criteria": {"sre": "Infrastructure and capacity", "app": "Application code"}}}}'
```

- **M5 Max:** PyTorch MPS. `--device auto` picks CUDA, then MPS, then OpenVINO, then CPU ([`device.py`](https://github.com/wfzyx/von/blob/main/src/von/device.py)). No MLX, GGUF, ONNX or Core ML build is published. No Apple Silicon latency figure is published.
- The first call downloads ~3.2 GB of weights to `HF_HOME`.
- `von serve` binds `0.0.0.0` by default; pass `--host 127.0.0.1` or set `VON_API_KEY`.
- The Docker image is `linux/amd64` with OpenVINO; a CUDA image builds from the same `Dockerfile` but is not published.
- No hosted API.

## Scaling limits

- **Options:** no cap in the server; all options share one 8,192-token sequence with the state. Training rows use 2–32 options ([`docs/finetune.md`](https://github.com/wfzyx/von/blob/main/docs/finetune.md)).
- **Context:** 8,192 tokens per question. Longer states are middle-truncated (60% head, 40% tail) unless `--on-overflow refuse`, which returns `422`.
- **Questions per call:** no documented maximum. The README says several questions over one state "cost one forward pass", but the backend runs one encoder pass per question (`evaluate` loops over questions, [`option_marker_backend.py`](https://github.com/wfzyx/von/blob/main/src/von/backends/option_marker_backend.py)).
- **Chains:** up to 16 sub-decisions per item (`VON_CHAINS_MAX_CALLS`); hard-tier p50 4.2 s on 4 vCPU, 0.45 s on A10G.
- **Multi-label:** one Noul per label.

## Fine-tuning

Three levels, from [`docs/finetune.md`](https://github.com/wfzyx/von/blob/main/docs/finetune.md):

| Level | Changes | Cost (author) |
|---|---|---|
| `von calibrate labels.jsonl` | temperature map only; never changes an answer | CPU, minutes |
| Continue-train from von-1.2 | head + encoder, your rows plus 10–30k replay rows | 1 GPU, ~1 h (A10G 24 GB) |
| New trunk (e.g. `jhu-clsp/mmBERT-base` for German) | fresh head on another MLM encoder; needs the 290k base corpus | ~1 h on 4×A10G (~$12) |

- Trainer: `training/train_option_marker.py` with `--independent_options --digit_split`; rows are `state`, `question`, 2–32 described `options`, `label`, optional soft `target`.
- On a 38-label coding-agent probe set, a scalar refit (T = 2.15) moved ECE from 0.21 to 0.11 ([card](https://huggingface.co/wfzyx/von)).
- The author reports sealed general benchmarks did not move in 1.4 experiments ([`results/v1.4/`](https://github.com/wfzyx/von/tree/main/results/v1.4)).
- Training on MPS is not documented.

## Data governance

Not legal advice.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; self-hosted = your infra. Runs offline once weights are cached. No telemetry calls found in `src/von` (grep, 2026-10-02) | [GitHub](https://github.com/wfzyx/von) |
| Fine-tuning | Yes, on your hardware (calibrate, continue-train, new trunk) | [`docs/finetune.md`](https://github.com/wfzyx/von/blob/main/docs/finetune.md) |
| Processing location | Wherever you run it | |
| EU processing option | Yes, by self-hosting in the EU | |
| Retention / ZDR | No vendor processing; retention is your server's logging | |
| Training on inputs | No vendor service exists | |
| DPA / GDPR | No processor, so no DPA | |
| Certifications | None | |
| Weights licence | Apache-2.0 (HF `cardData`); base ModernBERT-large Apache-2.0; repo `LICENSE.md` is Apache-2.0 | [HF API](https://huggingface.co/api/models/wfzyx/von) |

- Training data includes public datasets (Banking77, dair-ai/emotion, ANLI, WANLI) and synthetic sets; per-dataset licences are not listed on the card (unverified).
- No hosted API.
- Weights change under the same repo id; pin `revision` (current `498ceba`; card weights SHA `5df8185`).

## Caveats

- Every benchmark above 0 is the author's own run or an older board revision. On the current JevBench (v1.5.4) Von scores 0.0.
- The calibration map is fitted on JevBench public items, so JevBench calibration numbers are partly in-sample.
- Card known gaps: weak on long multi-clause policy and multi-hop temporal or numeric composition (hard tier ~0.37–0.44); `judge` without `criteria` is the weakest path; auth failures, rate limits and tool rejections route to a generic code-error option with high confidence (issue #22).
- The kyr0 run is Von 1.1, before order-invariant scoring; current weights are 1.2.
- The repo cites "Reinforcement Learning with Calibration Distribution for Non-Autoregressive Decision Modeling", arXiv 2503.23303, by DeepMostInnovations (unverified; not checked).
- Size notes differ: the card says 1.5 GB FP32; the GitHub README says ~3 GB is downloaded, which matches the two 1.58 GB files.

## Sources

- [HF model card `wfzyx/von`](https://huggingface.co/wfzyx/von) (revision `498ceba`), [HF API](https://huggingface.co/api/models/wfzyx/von), [`config.json`](https://huggingface.co/wfzyx/von/raw/main/config.json), [`marker_calibration.json`](https://huggingface.co/wfzyx/von/raw/main/marker_calibration.json)
- GitHub [`wfzyx/von`](https://github.com/wfzyx/von) (commit `cd196bb`, 2026-10-02): README, [`docs/finetune.md`](https://github.com/wfzyx/von/blob/main/docs/finetune.md), [`docs/benchmarks.md`](https://github.com/wfzyx/von/blob/main/docs/benchmarks.md), [`results/speed_remeasure.md`](https://github.com/wfzyx/von/blob/main/results/speed_remeasure.md), `src/von/`
- [PyPI `von-sdk`](https://pypi.org/project/von-sdk/) 1.3.7
- [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4)
- [kyr0 typed-decision-bench](https://kyr0.github.io/typed-decision-bench/) (via [benchmarks.md](../benchmarks.md))
- [Decision Index Space `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index) (generated 2026-09-28)

All read 2026-10-02.

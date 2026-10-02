# Jev-Omni (akhilaaa3)

| Field | Value |
|---|---|
| Vendor | Independent author `akhilaaa3` on Hugging Face; no organisation named |
| Type | Decision classifier: one question and 2–256 options in, one probability per option out, no generated text. Text, image, audio and video input |
| Backbone | `google/gemma-4-12B-it`, fine-tuned with two LoRA stages merged, plus a trained 256-way linear decision head (`head.pt`) |
| Size | 11,959,730,224 parameters (BF16 safetensors); `model.safetensors` 23.92 GB |
| Licence | Apache-2.0 (card metadata, "following Gemma 4"); base card links the [Gemma 4 licence](https://ai.google.dev/gemma/docs/gemma_4_license) |
| Run it via | Weights only. Reference loader `load_jev_omni()` (CUDA only); community MLX 4-bit, GGUF and WebGPU builds. No hosted API |
| Status | Created on HF 2026-09-20; last commit 2026-09-25 (`5addda8`). 1,599 downloads (30 days), 342 likes |

Checked 2026-10-02.

## Overview

Jev-Omni takes a `state`, one `question` and a list of `options`, and returns a probability for each option ([model card](https://huggingface.co/akhilaaa3/Jev-Omni)).
It reads the last hidden state of the Gemma 4 text backbone and passes it through a linear head with 256 option slots; slots past the option count are masked ([`jev_omni.py`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/main/jev_omni.py)).
The prompt lists the options as numbers and asks for "only the number of the correct option".
Image, audio and video go through Gemma 4's own vision and audio towers.
Audio is cut to 30 s with `ffmpeg`; video is sampled to 16 frames.
The card says the model is not derived from TypeSafe's Jev and that "nothing in it was trained on Jev output".
The training data is not published.

Training recipe ([`decision_config.json`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/main/decision_config.json)): a first rank-128 adapter, merged, then a rank-512 LoRA on 24,000 examples, 1 epoch, 750 steps, learning rate 1e-5, effective batch 32, seed 3407, 4 GPUs.
Trainable parameters were 2,099,183,872.
The card describes "a 30,000-question fine-tuning run"; the config records 24,000 for the second stage.

## Schema

Own call shape, not the TypeSafe request ([card](https://huggingface.co/akhilaaa3/Jev-Omni)):

```python
classifier.predict(state=..., question=..., options=[...], media=None, modality="text")
# -> {"prediction", "prediction_index", "confidence", "probabilities": {option: p}}
```

- One question per call. Several questions about one state need one call each, and the state is re-encoded each time.
- No `noul`, `choice` or `score` types. A Noul is a `["Yes", "No"]` option list; a Score is an ordered option list with no expected-value output.
- No option descriptions (`criteria`); options are plain strings.
- `confidence` is the top probability.
- `modality` is `text`, `image`, `audio` or `video`; `media` is a local file path.
- TypeSafe compatibility: partial. JevBench wraps it in an adapter that maps all three primitives onto option lists and reports them as "native" ([JevBench JSON](https://benchmarkheaven.com/api/jevbench/v1.5.4)).

## Benchmarks

Third-party boards. Jev 1.13.0 is given for reference.

| Board | Jev-Omni | Jev 1.13.0 | Source |
|---|---:|---:|---|
| JevBench v1.5.4 score (rank) | 71.5 (#6 of 106 ranked); CI95 70.2–72.4 | 72.1 (#3) | [JSON](https://benchmarkheaven.com/api/jevbench/v1.5.4); [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#jevbench-v154-headline-a) |
| JevBench axes: intelligence / calibration / speed / cost | 70.5 / 82.6 / 84.7 / 56.1 | 72.0 / 88.0 / 83.8 / 54.7 | same |
| JevBench p50 latency (raw) | 0.113 s on an evaluator RTX6000 pod | 0.616 s, hosted API | same |
| JevBench cost estimate | $0.029 per 1,000 decisions | $0.032 | same |
| Decision Index 0.2.1 balanced skill (rank) | 40.53 (#21 of 71 rows) | 57.91 (#1) | [DI Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) `data/index.json`, generated 2026-09-28; [benchmarks.md](../benchmarks.md#decision-index) |
| DI ECE (35,088 samples, 32 benchmarks) | 0.161 | 0.074 | same |
| DI median latency | 54.9 ms (p95 627.9 ms), RTX PRO 6000 | 524.1 ms | same |

DI category skill, Jev-Omni vs Jev: Knowledge & Reasoning 25.5 vs 51.4; Language Understanding 50.5 vs 62.0; Retrieval & Classification 35.8 vs 55.4; Tools & Automation 60.8 vs 75.1; Arts & Human Taste 26.1 vs 37.7.
The DI run used the author's `JevOmni.predict` per question with torch 2.14.0 and transformers 5.17.0.
Jev-Omni is not on kyr0, 4nt0ineB or Fastino fast-decisions (checked 2026-10-02).

Self-reported ([card](https://huggingface.co/akhilaaa3/Jev-Omni), merged model):

| Benchmark | Accuracy (group mean) | Micro accuracy |
|---|---:|---:|
| DecisionBench Medium, 80 scenarios / 293 questions | 87.57% | 86.01% |
| JevBench public, 195 groups / 231 decisions | 86.15% | 87.45% |
| MMAU, 1,000 audio questions | — | 63.10% |
| MVBench, 14 tasks / 2,786 video questions | 53.10% | 53.09% |

- DecisionBench Medium ECE: 0.040 (10 bins).
- DecisionBench is the author's own synthetic set ([dataset card](https://huggingface.co/datasets/akhilaaa3/decision-bench), Apache-2.0). On it, Jev 1.13 scores 90.48% on Medium.
- Speed on a warm H200: 83 ms for ~2k-token text, 26 ms image, 31 ms 13-second audio, 504 ms 16-frame video (medians of 20 requests).

Community builds:

- MLX 4-bit: JevBench public 85.90% group mean, 87.88% micro, ECE-10 0.045 raw, 0.031 after temperature scaling (T = 1.115) ([Ruiruiz30 card](https://huggingface.co/Ruiruiz30/Jev-Omni-MLX-4bit)).
- WebGPU int8 in Chrome on an M4 Max: DecisionBench Medium 86.35% browser and fp32 reference, 0 answers changed ([ai-ecoverse card](https://huggingface.co/ai-ecoverse/jev-omni.js)).
- GGUF Q4_K_M: Jev Persian Benchmark Choice 98.75% (237/240), Noul 93.75% (150/160), Score within ±0.5 95.00% (76/80). It matched the fp32 winning option on 3 of 4 verification cases, with a maximum probability difference of 0.210 ([Reza2kn card](https://huggingface.co/Reza2kn/Jev-Omni-Q4_K_M-GGUF)).

## Running it

Reference path (CUDA GPU required; the loader raises an error on any other device):

```bash
pip install -r https://huggingface.co/akhilaaa3/Jev-Omni/resolve/main/requirements.txt  # torch>=2.10, transformers==5.17.0
# ffmpeg is also needed for audio
```

```python
from huggingface_hub import snapshot_download
import sys
path = snapshot_download("akhilaaa3/Jev-Omni", revision="5addda86ddee081a68fb067477ea100c221b8917")
sys.path.insert(0, path)
from jev_omni import load_jev_omni

classifier = load_jev_omni()
print(classifier.predict(state="The meeting starts at 10 AM. It is now 9 AM.",
                         question="Has the meeting started?", options=["Yes", "No"]))
```

The card's "FP32 weights use about 50 GB" predates commit `6028e1f` (2026-09-25), which made the 23.92 GB BF16 checkpoint the repo root.
`verification.json` holds 4 text cases with reference probabilities.

Mac paths on the M5 Max, 128 GB (none tested here):

| Path | Repo | Command | Published Mac result |
|---|---|---|---|
| MLX, 4-bit LM, BF16 vision, FP32 head | [`Ruiruiz30/Jev-Omni-MLX-4bit`](https://huggingface.co/Ruiruiz30/Jev-Omni-MLX-4bit) (`3ec2559`, 825 downloads) | `pip install -r requirements.txt`, then `python -m omni_mlx.classifier --model . --calibration calibration.json --state ... --question ... --options ...` | M4 Mac mini 16 GB: text ~963 ms median, image ~994 ms, peak Metal memory ~7.0 GB. Text and image only |
| GGUF + llama.cpp | [`ngquocvinh/Jev-Omni-GGUF`](https://huggingface.co/ngquocvinh/Jev-Omni-GGUF) (`f07b38e`, 2,010 downloads): Q1_0 2.38 GB to Q8_0 12.67 GB, imatrix; [`Reza2kn/Jev-Omni-Q4_K_M-GGUF`](https://huggingface.co/Reza2kn/Jev-Omni-Q4_K_M-GGUF) (`0991aeb`, 3,536 downloads): Q4_K_M 6.87 GiB | `llama-server -m <gguf> --mmproj mmproj-jev-omni.gguf --embedding --pooling none ...`, then `python jev_omni_gguf_decide.py --head decision-head-f32.npz ...` | None. Reza2kn: "not validated on macOS ... Metal". Plain `llama-cli` does not apply the head |
| ONNX Runtime Web, WebGPU | [`ai-ecoverse/jev-omni.js`](https://huggingface.co/ai-ecoverse/jev-omni.js) (13.58 GB int8) | `loadJevOmni(...)` in Chrome | M4 Max parity table above; text and image only; needs ~16 GB GPU memory |
| PyTorch MPS | upstream | not documented | The loader is CUDA-only; running BF16 on MPS needs a patched loader (unverified) |

- Keep `llama-server` on `127.0.0.1`: the embedding endpoint "exposes internal model states" (Reza2kn).
- The MLX and Reza2kn builds come from upstream revision `c050d51`; ngquocvinh from `5addda8`.

## Scaling limits

- **Options:** 2–256 per question. The card: "Best supported at ≤20 options ... quality above 20 is not established."
- **Questions per call:** 1. DecisionBench measured 2.82× more input tokens on Medium (3.09× on Hard) when a state is split into per-question calls.
- **Context:** `max_position_embeddings` 262,144; long context is "not validated" (ngquocvinh). Sliding window 1,024 tokens on 40 of 48 layers.
- **Media:** audio 30 s; video 16 frames; one media file per call.
- **Memory:** BF16 about 24 GB of weights; MLX 4-bit ~7.0 GB peak; GGUF Q4_K_M 8.77–9.04 GiB VRAM on an RTX 5080 Laptop.

## Fine-tuning

- No training code published. The recipe is in `decision_config.json`; the training set and its licence are not disclosed.
- LoRA on the merged checkpoint with your own data is possible in principle with PEFT on Gemma 4 (unverified; no script).
- Training data on the author's side carries fingerprints only (`train_fingerprint`, `dev_fingerprint`).

## Data governance

Not legal advice.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; self-hosted = your infra. Air-gapped after download, except that the reference loader downloads Gemma 4 multimodal parts if missing | [card](https://huggingface.co/akhilaaa3/Jev-Omni) |
| Fine-tuning | On your hardware; no code from the author | `decision_config.json` |
| Processing location | Your machine. No hosted API from the author | HF author page, 2026-10-02 |
| EU processing option | Your choice of hardware. HF Inference Endpoints offer AWS `eu-west-1`; the custom loader needs a custom handler | [open-reproductions.md](open-reproductions.md#data-governance) |
| Retention / ZDR | Nothing leaves your machine when self-hosted | |
| Training on inputs | No, when self-hosted | |
| DPA / GDPR | No processor, so no DPA needed when self-hosted | |
| Certifications | None | |
| Weights licence | Apache-2.0 metadata; base `gemma-4-12B-it` reports `apache-2.0` and links the Gemma 4 licence. Training-data rights "remain separate" | [card](https://huggingface.co/akhilaaa3/Jev-Omni), [base card](https://huggingface.co/google/gemma-4-12B-it) |

- Custom code: `jev_omni.py` runs from the repo via `sys.path`. Pin the revision and read it first.
- `sha256.json` lists file hashes. ngquocvinh ships `SHA256SUMS.txt`; ai-ecoverse a SHA-256 `manifest.json`.

## Caveats

- Single anonymous author; no paper, blog or GitHub repo.
- Training data undisclosed, so overlap with JevBench public items or DI test sets cannot be checked.
- JevBench rank (#6, 71.5) and DI rank (#21, 40.53) differ by a wide margin; DI ECE 0.161 is 2.2× Jev's.
- The card's FP32 memory figure and "30,000-question" figure do not match the current repo files.
- One question per call: cost and latency scale with question count, unlike Jev and Intern-Decision.
- Quantized builds change probabilities: up to 0.244 absolute (MLX) and 0.210 (Q4_K_M) on 4 test cases.
- The DI Space lists the base as `google/gemma-4-12B`; the card says `gemma-4-12B-it`.

## Sources

- akhilaaa3/Jev-Omni: [model card](https://huggingface.co/akhilaaa3/Jev-Omni), [`config.json`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/main/config.json), [`decision_config.json`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/main/decision_config.json), [`jev_omni.py`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/main/jev_omni.py), [`requirements.txt`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/main/requirements.txt), [`verification.json`](https://huggingface.co/akhilaaa3/Jev-Omni/blob/main/verification.json), [HF API](https://huggingface.co/api/models/akhilaaa3/Jev-Omni) (sha `5addda8`), [commit history](https://huggingface.co/akhilaaa3/Jev-Omni/commits/main)
- [DecisionBench dataset card](https://huggingface.co/datasets/akhilaaa3/decision-bench)
- Community builds: [Ruiruiz30/Jev-Omni-MLX-4bit](https://huggingface.co/Ruiruiz30/Jev-Omni-MLX-4bit) (+ `conversion.json`), [ngquocvinh/Jev-Omni-GGUF](https://huggingface.co/ngquocvinh/Jev-Omni-GGUF) (+ `reproducibility/manifest.md`), [Reza2kn/Jev-Omni-Q4_K_M-GGUF](https://huggingface.co/Reza2kn/Jev-Omni-Q4_K_M-GGUF), [ai-ecoverse/jev-omni.js](https://huggingface.co/ai-ecoverse/jev-omni.js)
- [google/gemma-4-12B-it](https://huggingface.co/google/gemma-4-12B-it) (HF API, sha `707f0a3`)
- JevBench [v1.5.4 JSON](https://benchmarkheaven.com/api/jevbench/v1.5.4); Decision Index [Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) `data/index.json` (generated 2026-09-28)

All read 2026-10-02.

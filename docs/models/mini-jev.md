# mini-Jev (samatv256)

| Field | Value |
|---|---|
| Vendor | Independent developer: HF `samatv256`; v1 source at GitHub `samat2003` |
| Type | Finite-choice decision model: scores each supplied option and returns a probability per option; no generated text |
| Backbone | `Qwen/Qwen3-0.6B` (revision `c1899de`), loaded in 4-bit NF4 |
| Size | Backbone about 0.6B (separate download). This repo: LoRA adapter 1,310,720 parameters plus decision head 1,907,201 parameters (FP32). The HF API's "262,657 params" counts only the legacy v1 head in the root `model.safetensors` |
| Licence | Apache-2.0 (`cardData`, `LICENSE`); base Apache-2.0 |
| Run it via | Self-host: `inference.py` from the repo (`MiniJev.load(".")`). CUDA GPU with BF16 required. No hosted API |
| Status | Created 2026-09-21. Interim checkpoint `step-010626` published 2026-09-29, training planned to 50,000 updates. HF revision `a2003a3` (2026-10-01). 464 downloads (30 days), 19 likes |

Checked 2026-10-02.

## Overview

mini-Jev targets tool and action selection in agent loops: state + question + candidate actions → one probability per candidate ([card](https://huggingface.co/samatv256/mini-Jev/raw/main/README.md)).
Each option is encoded with the state and question as its own branch through the Qwen3-0.6B backbone with a LoRA adapter on the attention projections of layers 20–27 (rank 16, alpha 32, `adapter/adapter_config.json`).
The option tokens are mean-pooled, projected to 256 dimensions, and scored by a 2-layer, 4-head set-attention head, so scoring is permutation equivariant (`config.json`, `inference.py`).
A softmax over the options gives the probabilities.

Two releases share the repo:

| Release | Revision | What it is |
|---|---|---|
| v1 baseline ("ODM Mini v1") | tag `v1-baseline`; the card points to `02acc03` | Frozen Qwen3-0.6B, 262,657-parameter MLP head, trained on 50,000 synthetic examples; root `model.safetensors` + `odm_mini.py` |
| step 10,626 (current) | tag `step-010626`, `main` | LoRA + set head, NF4 backbone; `adapter/`, `decision_head.safetensors`, `inference.py` |

## Schema

Not the TypeSafe wire shape. Python API only:

```python
model.predict(state=..., question="...", question_type="choice",
              answer_options=[{"id": "weather", "type": "tool", "label": "get_weather_forecast",
                               "description": "Look up the weather forecast for a place and date."}, ...])
```

- `question_type` is a free string inserted into the prompt; evaluations used `choice`, `noul` and `score`.
- Each option needs a `label`; `id` is bookkeeping and is not shown to the model. At least 2 options.
- Returns `selected_id`, `selected_label`, `options` (id, label, probability) and `branch_tokens`.
- No `confidence`, Score expected value or Noul probability field; Noul and Score are posed as options.
- No HTTP server ships with step 10,626. The v1 GitHub repo has a FastAPI app for v1 (`src/server/odm_mini_app.py`).

TypeSafe-compatible: no. A wrapper could map Jev requests onto `predict` (unverified).

## Benchmarks

Author's results for step 10,626 ([card](https://huggingface.co/samatv256/mini-Jev/raw/main/README.md), 2026-09-29). Each set has its own denominator.

| Evaluation | Result | Notes |
|---|---:|---|
| [LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) full test | 34.0% (680/2,000) | Choice 27.0%, Noul 52.2%, Score 25.6% |
| BFCL V1 Multiple Function, function-selection adaptation | 96.5% (193/200) | Picks the function from 2–4 definitions; not an official BFCL score |
| Strict held-out Choice slice | 65.6% (63/96) | Selected, bucket-balanced slice |
| Own OOD typed decisions | 72.0% (36/50) | Small synthetic check |
| Held-out slice with 17+ candidates | 4/17 | Large option sets are weak |

v1 baseline ([card at `02acc03`](https://huggingface.co/samatv256/mini-Jev/raw/02acc03cc28ec0b99705a8459ea987274fa7987f/README.md)): synthetic semantic Choice 72.97%, stress Choice 67.64%, counterfactual pair consistency 67.12%; on 243 decisions from 75 real agent trajectories, action accuracy 27.98%. Latency 76–85 ms on an NVIDIA GH200 (BF16, shared-prefix KV cache, 256–1,024 state tokens, 3–16 candidates).

- For scale: on typed-decisions, Decider 1 reports 0.768, Jev 1.13.0 0.727 and Liquid d1 0.742 accuracy ([decider-1.md](decider-1.md#benchmarks)). mini-Jev's 34.0% is the author's run of the same 2,000-decision test.
- No row on JevBench v1.5.4, the Decision Index 0.2.1, kyr0, 4nt0ineB or Fastino fast-decisions, checked 2026-10-02 against [`/api/jevbench/v1.5.4`](https://benchmarkheaven.com/api/jevbench/v1.5.4) and the DI [`data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index).
- The DI row "mini-jev Qwen3-4B" (20.98, [benchmarks-leaderboards.md](../benchmarks-leaderboards.md)) is a different project with a Qwen3-4B base, likely [r-ms/mini-jev](https://github.com/r-ms/mini-jev) (unverified). It is not this model.

## Running it

```bash
hf download samatv256/mini-Jev --revision step-010626 --local-dir mini-jev
cd mini-jev && uv venv && uv pip install -r requirements.txt
uv run python -c "from inference import MiniJev; m = MiniJev.load('.'); print(m.predict(state={'user_goal': 'Weather in Paris tomorrow'}, question='Which option should be selected?', question_type='choice', answer_options=[{'label': 'get_weather_forecast'}, {'label': 'send_email'}])['selected_label'])"
```

- `requirements.txt` pins torch 2.14.0, transformers 5.17.0, peft 0.21.0, bitsandbytes 0.50.2, safetensors 0.8.0, accelerate 1.15.0.
- `MiniJev.__init__` raises `"this 4-bit BF16 release requires a CUDA GPU"` on anything else.
- Mac (M5 Max): no supported path for step 10,626. Loading Qwen3-0.6B unquantized on MPS and applying the adapter with peft would need loader changes, and the adapter was trained against an NF4 base (unverified effect). The v1 baseline (`odm_mini.py`) runs on CPU in FP32; its loader picks CUDA or CPU.

## Scaling limits

- **Context:** 8,192 tokens per branch (state + question + one option); state is truncated to fit (`inference.py`).
- **Options:** no coded cap; minimum 2. One forward pass per option, so cost grows linearly with options. Accuracy drops on large sets (4/17 at 17+ candidates).
- **Questions per call:** one.
- **Calibration:** "its probabilities have not been calibrated for arbitrary domains" (card).

## Fine-tuning

- **Code:**
  - v1 baseline: public, Apache-2.0, [samat2003/mini-Jev](https://github.com/samat2003/mini-Jev) at commit `7cd917b` (2026-09-20). The repo README links the HF model. Scripts `scripts/train_odm_mini_head.py`, `scripts/cache_odm_mini.py`, data generators `src/data/v2/`, `scripts/bootstrap_gh200.sh`. Head-only training with grouped cross-entropy on cached backbone features.
  - step 10,626 (LoRA + set head + NF4): no training code found. The GitHub repo's last commit predates it (searched GitHub 2026-10-02).
- **Data:**
  - v1: 50,000 synthetic decision examples from the repo's generators. The v1 card says it was "NOT trained on Jev Decisions v1".
  - step 10,626: "draws in part on" [`samatv256/jev-decisions-v1`](https://huggingface.co/datasets/samatv256/jev-decisions-v1) (CC BY 4.0, revision `c12aadf`). That set derives from four NVIDIA datasets (Nemotron-SFT-Agentic-v2, two Nemotron-RL agentic sets, Open-SWE-Traces), all CC BY 4.0, with per-repository SPDX licences in Open-SWE-Traces ([SOURCE_LICENSES.md](https://huggingface.co/datasets/samatv256/jev-decisions-v1/blob/main/SOURCE_LICENSES.md)). The other sources are not named. BFCL items were used for evaluation.
- **Reported hardware and time:** v1 trained and was timed on an NVIDIA GH200 (`SHARED_STATE_ARCHITECTURE.md`, v1 card). Training time and cost are not stated for either release.
- **Apple Silicon:** v1 head training could run on CPU (the trainer picks CUDA or CPU); feature caching runs the full backbone. Step 10,626 uses bitsandbytes NF4 with CUDA autocast; not on Mac.
- **HF Jobs flavor (estimate):** QLoRA on a 0.6B backbone with BF16 compute fits in 24 GB: `l4x1` ($0.80/h). `t4-small` lacks BF16. Time unknown. Rates from [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing).
- **Commercial use:** Apache-2.0 weights on an Apache-2.0 base. CC BY 4.0 training data requires attribution; no non-commercial terms found.

## Data governance

Not legal advice. mini-Jev has no vendor API; every row below is for self-hosting on your own infrastructure.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; air-gapped once Qwen3-0.6B and the repo are cached | [card](https://huggingface.co/samatv256/mini-Jev) |
| Fine-tuning | v1 head: yes, code public. Step 10,626: no training code | [samat2003/mini-Jev](https://github.com/samat2003/mini-Jev) |
| Processing location | Your infrastructure (CUDA GPU) | |
| EU processing option | Self-host in the EU | |
| Retention / ZDR | No logging in `inference.py` | `inference.py` |
| Training on inputs | No; inference is local | |
| DPA / GDPR | Not applicable when self-hosted: no processor | |
| Certifications | None (open-source project) | |
| Weights licence | Apache-2.0; base `Qwen/Qwen3-0.6B` Apache-2.0 | HF API, `LICENSE`, 2026-10-02 |
| Training-data terms | Partly CC BY 4.0 (jev-decisions-v1, attribution required); remaining sources undisclosed | card |

## Caveats

- Interim checkpoint: 10,626 of 50,000 planned updates. Results will change, and `main` may move; pin `step-010626`.
- General typed decisions are weak: 34.0% on typed-decisions; the card calls them "a weakness".
- The 96.5% BFCL figure is function-name selection from 2–4 candidates, not BFCL's argument-generation task.
- The card says the previous revision is `02acc03`; the `v1-baseline` tag points to `b5339dd`. The `step-010626` tag points to `ee47ab8`, which is not among the 5 commits the HF API lists for `main`.
- The repo name and tags on the Hub ("mini-Jev") collide with several unrelated GitHub projects called mini-jev.

## Sources

- HF model: [card](https://huggingface.co/samatv256/mini-Jev/raw/main/README.md), [v1 card at `02acc03`](https://huggingface.co/samatv256/mini-Jev/raw/02acc03cc28ec0b99705a8459ea987274fa7987f/README.md), [API](https://huggingface.co/api/models/samatv256/mini-Jev), `/refs`, `/commits/main`, `config.json`, `adapter/adapter_config.json`, `requirements.txt`, `inference.py`, `odm_mini.py`, safetensors headers for `decision_head.safetensors` and `adapter/adapter_model.safetensors`
- GitHub: [samat2003/mini-Jev](https://github.com/samat2003/mini-Jev) at `7cd917b`: README, LICENSE, `SHARED_STATE_ARCHITECTURE.md`, `src/training/odm_mini_head.py`, `scripts/`
- Data: [`samatv256/jev-decisions-v1`](https://huggingface.co/datasets/samatv256/jev-decisions-v1) (API, `SOURCE_LICENSES.md`), [LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions)
- Base: [`Qwen/Qwen3-0.6B`](https://huggingface.co/Qwen/Qwen3-0.6B) (API metadata)
- Boards: [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4), [Decision Index `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index), [benchmarks-leaderboards.md](../benchmarks-leaderboards.md)
- [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing)

All read 2026-10-02.

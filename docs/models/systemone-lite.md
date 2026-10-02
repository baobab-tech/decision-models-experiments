# systemone-lite (dwidlee / fritzprix)

| Field | Value |
|---|---|
| Vendor | Independent developer: HF user `dwidlee`, GitHub `fritzprix`. "Not affiliated with TypeSafe AI or Jev" (card) |
| Type | Decision model: probabilities for typed questions (Choice, Score, Noul) by option-restricted next-token scoring; no generated text |
| Backbone | `Qwen/Qwen2.5-0.5B-Instruct`, full fine-tune ("cold SFT") |
| Size | 494,032,768 parameters, BF16 (`model.safetensors` 988 MB) |
| Licence | Weights Apache-2.0 (`cardData`); code MIT; base Apache-2.0 |
| Run it via | Self-host: `systemone-lite` FastAPI server (`POST /v1/systemone`) or the Python client, from [fritzprix/systemone-lite](https://github.com/fritzprix/systemone-lite). No hosted API |
| Status | Repo created 2026-09-19. Current weights `action-v2-qwen`, published 2026-09-26. HF revision `4214f92`. 1,851 downloads (30 days), 0 likes |

Checked 2026-10-02.

## Overview

systemone-lite is a local System One implementation on a 0.5B model.
It takes a `state` and named closed questions and returns one answer per question.
It scores the answer tokens for the given options in one forward pass per question; it never writes JSON ([GitHub README](https://github.com/fritzprix/systemone-lite)).
Questions about the same `state` share a KV-cached prefix (`src/systemone_lite/infer.py`).
The HF repo is a stable name: "New training runs overwrite these weights" ([card](https://huggingface.co/dwidlee/systemone-lite-0.5b)). Pin the revision.
The author lists it for "demos / local experiments, not a production decision service".

## Schema

Same request shape as TypeSafe: `model` + `state` + `questions` → `answers` + `usage` ([`schema.py`](https://github.com/fritzprix/systemone-lite/blob/main/src/systemone_lite/schema.py), [`openapi/systemone.yaml`](https://github.com/fritzprix/systemone-lite/blob/main/openapi/systemone.yaml)).

- `state`: string, object or array. Objects are rendered as indented JSON.
- `questions` must be a map; unknown fields return a validation error (`extra="forbid"`).
- **Noul:** `instructions`, optional `criteria` `{"true": …, "false": …}`; scores the tokens `yes` and `no`; returns `noul`.
- **Choice:** `criteria` map of key → description (description may be `null`); returns `choice`, `probabilities`, `confidence`.
- **Score:** `criteria` array of 2 to 10 levels, lowest first; scores the level indexes `0`…`n-1`; returns `score` (float), `legend`, `probabilities`, `confidence`.
- `confidence` = (p_max − 1/n) / (1 − 1/n), clipped to [0, 1] ([`confidence.py`](https://github.com/fritzprix/systemone-lite/blob/main/src/systemone_lite/confidence.py)). Jev uses a different formula.
- A multi-token option key is scored by its first token only, with a logged warning (`infer.py`). Two keys that share a first token would get the same score (unverified).
- `usage.output_tokens` is 0.

TypeSafe-compatible: partial. The wire shape matches; `confidence` and the Score value differ, and the README says it is "not a cloud drop-in".

## Benchmarks

All numbers are the author's own, local, single run, 2026-09-26 ([card](https://huggingface.co/dwidlee/systemone-lite-0.5b), [postmortem](https://github.com/fritzprix/systemone-lite/blob/main/docs/NOTE_ACTION_V2_QWEN_POSTMORTEM.md), [`benchmarks/jevbench_action_v2_qwen.json`](https://github.com/fritzprix/systemone-lite/blob/main/benchmarks/jevbench_action_v2_qwen.json)).

| Measure | Result | n |
|---|---:|---:|
| JevBench public items, accuracy (T = 1.0) | 50.65% (117/231) | 231 |
| JevBench public items, ECE | 0.245 | 231 |
| JevBench public items, mean Brier | 0.733 | 231 |
| JevBench public items, p50 latency | 13.1 ms (in-process) | 231 |
| Own `phase2` held-out `test` | 61.55% (2,893/4,700) | 4,700 |
| Prior Hub weights `spatial_v2_s1`, JevBench public accuracy / ECE | 49.78% / 0.307 | 231 |

- Uniform random on the JevBench public set is about 32% (author).
- The author puts the standard error at about ±3 points for n = 231, so the change from 49.78% to 50.65% is noise.
- Per gym on `test`: game2048 34.6%, sokoban 38.2%, chess 42.0%, gridworld 45.6%, connect4 47.0%, ticket and resource allocation 98–100%.
- Latency hardware: RTX 3060 (README).
- No row on JevBench v1.5.4, the Decision Index 0.2.1, kyr0, 4nt0ineB or Fastino fast-decisions, checked 2026-10-02 against [`/api/jevbench/v1.5.4`](https://benchmarkheaven.com/api/jevbench/v1.5.4) and the DI [`data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index). The README says a JevBench submission is queued ([jevbench#107](https://github.com/fstandhartinger/jevbench/issues/107), unverified).
- The repo's `jevbench_unofficial_rank_estimate.json` gives hypothetical board ranks for older runs. It renormalizes axes and borrows a cost estimate, so it is not a JevBench score.

## Running it

```bash
git clone https://github.com/fritzprix/systemone-lite.git && cd systemone-lite
uv venv && uv pip install -e ".[dev]"
uv run systemone-lite --model dwidlee/systemone-lite-0.5b --port 8000
curl -s http://127.0.0.1:8000/v1/systemone -H 'Content-Type: application/json' \
  -d '{"state": "My card was charged twice.",
       "questions": {
         "needs_review": {"type": "noul", "instructions": "Does this need a human agent?"},
         "route": {"type": "choice", "instructions": "Route to a team",
                   "criteria": {"billing": "charges", "technical": "bugs", "other": null}},
         "urgency": {"type": "score", "instructions": "Urgency", "criteria": ["low", "medium", "high"]}}}'
```

- Mac (M5 Max): PyTorch MPS. `infer.py` picks CUDA, then MPS, then CPU, and loads FP32 on anything but CUDA. The author has not published Mac timings.
- No GGUF, MLX or ONNX export is published. The server needs raw next-token logits, so a llama.cpp or MLX port would need new serving code (unverified).
- Dependencies are lower bounds only (`torch>=2.4`, `transformers>=4.46`); pin them for experiments.

## Scaling limits

- **Context:** 4,096 tokens per prompt (`MAX_LENGTH` in `infer.py`); longer input is truncated, not rejected. The base model supports 32,768 (`config.json`).
- **Options:** Score 2 to 10 levels. Choice has no coded cap; training used "option caps ≤8" for chess and small sets elsewhere.
- **Questions per call:** no cap; one forward pass per question over the shared prefix.
- **Calibration:** the card says "Calibration is mediocre" (ECE 0.245 on 231 items).
- **Tasks:** spatial planning (2048, sokoban, chess) "remains far from solved" (card).

## Fine-tuning

- **Code:** public, MIT, [fritzprix/systemone-lite](https://github.com/fritzprix/systemone-lite) at commit `fc6fbe3` (2026-09-26). Trainer `scripts/chess_finetune.py`; data builders `scripts/build_phase2_distill.py` and `src/systemone_lite/synth/`; Colab notebook `notebooks/phase2_spatial_training_colab.ipynb`.
- **Method:** full-parameter SFT with cross-entropy on the answer token. Published run: 10,000 optimizer steps, LR 1e-5 cosine, warmup 500, batch 4 × gradient accumulation 4, stratified by gym (postmortem). `best_val_meta.json` on the Hub: step 10,000, validation accuracy 0.649.
- **Data:** [`dwidlee/systemone-lite-phase2`](https://huggingface.co/datasets/dwidlee/systemone-lite-phase2) (Apache-2.0, revision `3e283cb`): 240,800 train and 4,700 test rows, 0.00% train∩test overlap by the author's audit. Rows are synthetic gyms (connect4, 2048, gridworld, sokoban, chess, cellular automata, ticket routing, resource allocation, debate judging, word games) plus cloze items from WikiText-2. Chess labels come from Stockfish or a heuristic (`scripts/chess_distill_dataset.py`). A second dataset, [`dwidlee/systemone-lite-general`](https://huggingface.co/datasets/dwidlee/systemone-lite-general), is MIT.
- **Data licence note:** WikiText-2 is CC BY-SA 3.0, which sits under the Apache-2.0 label on the dataset card (licence of WikiText-2 not re-checked here, unverified).
- **Reported hardware and time:** the Colab notebook targets a T4 16 GB: "all 204 800 rows ≈ 51 200 steps @ batch 4 (~8–10h)". Inference numbers are from an RTX 3060 12 GB. Hardware and wall time for the published run are not stated.
- **Apple Silicon:** not supported as written. The trainer selects CUDA or CPU only (`device = "cuda" if torch.cuda.is_available() else "cpu"`). CPU training of 0.5B on the M5 Max is possible but slow; an MPS patch is a small code change (unverified).
- **HF Jobs flavor (estimate):** `t4-small` ($0.40/h, 16 GB) matches the author's Colab target. The published run is 160,000 examples (10,000 steps × 16), about 40,000 micro-batches of 4, or about 6–8 h on a T4 by the notebook's rate: about $2.40–3.20. `l4x1` ($0.80/h, 24 GB, BF16) should be faster. Rates from [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing).
- **Commercial use:** Apache-2.0 weights on an Apache-2.0 base; no non-commercial terms found. Check WikiText-2 share-alike terms for the data.

## Data governance

Not legal advice. systemone-lite has no vendor API; every row below is for self-hosting on your own infrastructure.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; air-gapped once weights are cached | [GitHub README](https://github.com/fritzprix/systemone-lite) |
| Fine-tuning | Yes, on your hardware; full-parameter trainer in the repo | `scripts/chess_finetune.py` |
| Processing location | Your infrastructure | |
| EU processing option | Self-host in the EU | |
| Retention / ZDR | The FastAPI server has no documented request logging (unverified) | `src/systemone_lite/api.py` |
| Training on inputs | No; inference is local | |
| DPA / GDPR | Not applicable when self-hosted: no processor | |
| Certifications | None (open-source project) | |
| Weights licence | Apache-2.0 (`cardData`); base `Qwen/Qwen2.5-0.5B-Instruct` Apache-2.0 (revision `7ae5576`); code MIT | HF API, GitHub `LICENSE`, 2026-10-02 |
| Training-data terms | Synthetic gyms, Stockfish labels, WikiText-2 cloze; dataset cards Apache-2.0 and MIT | [phase2 card](https://huggingface.co/datasets/dwidlee/systemone-lite-phase2) |

## Caveats

- Single maintainer; all results are self-reported and unofficial.
- `main` is overwritten in place by new runs. `train_meta.json` on the Hub (10,800 steps, 4 gyms) does not match the card's run (10,000 steps, 11 gyms) and looks left over from an earlier run.
- `generation_config.json` sets sampling defaults (temperature 0.7); the scoring server does not sample, so they do not apply.
- The training data is mostly games and synthetic routing; general decision skill is weak (50.65% on JevBench public items against 32% random).
- The JevBench figure uses the 231 public items only, which other open models have overfit; it is not a sealed-set result.

## Sources

- HF model: [card](https://huggingface.co/dwidlee/systemone-lite-0.5b/raw/main/README.md), [API](https://huggingface.co/api/models/dwidlee/systemone-lite-0.5b), `config.json`, `train_meta.json`, `best_val_meta.json`, `generation_config.json`
- HF datasets: [`dwidlee/systemone-lite-phase2`](https://huggingface.co/datasets/dwidlee/systemone-lite-phase2), [`dwidlee/systemone-lite-general`](https://huggingface.co/datasets/dwidlee/systemone-lite-general) (API metadata)
- GitHub: [fritzprix/systemone-lite](https://github.com/fritzprix/systemone-lite) at `fc6fbe3`: README, LICENSE, `pyproject.toml`, `src/systemone_lite/{schema,infer,prompt,confidence}.py`, `scripts/chess_finetune.py`, `scripts/chess_distill_dataset.py`, the Colab notebook, `docs/NOTE_ACTION_V2_QWEN_POSTMORTEM.md`, `benchmarks/jevbench_action_v2_qwen.json`
- Base: [`Qwen/Qwen2.5-0.5B-Instruct`](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct) (API metadata)
- Boards: [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4), [Decision Index `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index), [benchmarks-leaderboards.md](../benchmarks-leaderboards.md)
- [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing)

All read 2026-10-02.

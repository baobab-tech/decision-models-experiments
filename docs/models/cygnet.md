# Cygnet (blockbrain)

| Field | Value |
|---|---|
| Vendor | blockbrain (GitHub org `blockbrain-ai`; LICENSE copyright "Nood Co (github.com/blockbrain-ai) and contributors") |
| Type | Recipe, not a trained model: frozen LLM with a one-token option-letter readout and one calibration temperature. Returns probabilities for Choice, Score, Noul |
| Backbone | `google/gemma-4-12B-it`, revision `707f0a3`, unmodified |
| Size | 11,959,730,224 parameters (BF16, ~22.3 GiB) |
| Licence | Shim and docs MIT; weights Apache-2.0 with the [Gemma 4 licence](https://ai.google.dev/gemma/docs/gemma_4_license) and [Gemma Prohibited Use Policy](https://ai.google.dev/gemma/prohibited_use_policy) |
| Run it via | [`blockbrain-ai/cygnet-recipe`](https://github.com/blockbrain-ai/cygnet-recipe): `vllm serve` (vLLM 0.30.0) plus `shim/decision_server.py` on `POST /v1/systemone`. Mac: [Ollaya](https://github.com/ollaya-dev/ollaya) `ollaya run cygnet` (Q8_0 GGUF) |
| Status | First commit 2026-09-24; HEAD `3cf591c` (2026-09-29, decision server merged); 25 stars. No hosted API |

Checked 2026-10-02.

## Overview

Cygnet answers typed decision requests with stock `gemma-4-12B-it`, no fine-tuning ([README](https://github.com/blockbrain-ai/cygnet-recipe)).
For each question the shim sends one chat request with the state, the instructions and the options lettered A, B, C…, and asks for one letter.
vLLM masks the answer position to the option letters (`structured_outputs.choice`) and returns the top 20 log-probabilities.
The shim sums probability over every token that decodes to each letter (Gemma 4 has duplicate letter tokens), renormalises, and applies temperature T = 3.4.
Cost is input tokens plus one output token per decision.
The readout idea comes from [NInfer](https://github.com/igorls/ninfer) (Apache-2.0); the shim code is blockbrain's ([CREDITS.md](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/CREDITS.md)).
It is the JevBench submission in [issue #71](https://github.com/fstandhartinger/jevbench/issues/71).

Two servers ship in `shim/`:

- `cygnet_shim.py`: the file every benchmark figure was measured with; standard library only; up to 26 options.
- `decision_server.py`: same readout for applications; answers every named question, up to 255 options, optional API key. On 231 JevBench public items it gives the same probabilities as the benchmark shim.

The calibration temperature was fitted by negative log-likelihood on 241 items blockbrain generated; JevBench public items were not used for the fit. A 121/120 split of those items (T = 3.1) lowered held-out ECE from 0.140 to 0.101 ([README](https://github.com/blockbrain-ai/cygnet-recipe#how-the-readout-works), [PROVENANCE.md](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/PROVENANCE.md)).

## Schema

`decision_server.py` follows TypeSafe's path and shape: `POST /v1/systemone`, `GET /v1/models`; `state` + named `questions` → `answers` + `usage` ([README, Serving applications](https://github.com/blockbrain-ai/cygnet-recipe#serving-applications)). TypeSafe clients need only the base URL changed.

- **Noul:** `criteria` optional; options always shown "false" first. Returns `noul` (probability of yes).
- **Choice:** up to 255 options; descriptions may be text, JSON or `null`. Returns `choice`, `probabilities`, `confidence`.
- **Score:** up to 10 levels. Returns `score` (probability-weighted level, a float as in Jev), `legend`, level-keyed `probabilities`, `confidence`.
- `confidence` is (K·p_max − 1)/(K − 1) over K options or levels.
- `usage`: `input_tokens`, `output_tokens`.
- Auth: `Authorization: Bearer` when `CYGNET_API_KEY` is set; without a key it listens only on localhost unless `CYGNET_ALLOW_NO_KEY=1`.
- Errors: `{"error": "<message>"}`; `422` for an unknown type, over 255 options or 10 levels, or over the context limit; `502` for other vLLM failures.
- No multi-label primitive; ask one Noul per label.

## Benchmarks

JevBench v1.5.5 (headline A, current board), 1,624 decisions (904 open, 720 sealed), run by the evaluator on an RTX PRO 6000 in an offline container ([`api/jevbench/v1.5.5`](https://benchmarkheaven.com/api/jevbench/v1.5.5), read 2026-10-02). Scores are unchanged from v1.5.4 ([leaderboards](../benchmarks-leaderboards.md#jevbench-v154-headline-a)); v1.5.5 adds Clef, Clef Flash and Interfaze Lev.

| Measure | Cygnet | Winnow-12B Q8 | Jev 1.13.0 |
|---|---:|---:|---:|
| Rank (A) of 109 | 1 | 2 | 3 |
| JevBench score | 73.7 | 73.2 | 72.1 |
| 95% CI (A) | 72.4–74.5 | 72.0–74.0 | 71.0–72.6 |
| Intelligence | 71.1 | 74.4 | 72.0 |
| Calibration | 87.0 | 84.1 | 88.0 |
| Speed | 91.0 | 86.1 | 83.8 |
| Cost | 56.4 | 56.6 | 54.7 |
| $/1,000 decisions | 0.0283 est. | 0.0281 est. | 0.0323 est. |
| p50 latency, raw | 0.040 s | 0.095 s | 0.616 s |

- The Cygnet and Winnow-12B intervals overlap; [benchmarks.md](../benchmarks.md#jevbench) calls them a statistical tie. Under headline B Cygnet ranks 2nd (73.2).
- Cygnet's Intelligence is below Jev's (71.1 vs 72.0) and Winnow's; it leads on Speed. Open-set Noul is its weakest type (57.9 vs Choice 82.9, Score 76.6).
- Cost is a base-model hosted price estimate ($0.028 per 1,000 decisions), not a bill. The README's mean input is 704 tokens per decision.
- Decision Index 0.2.1: no row (index generated 2026-09-28, per [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021)).

Author runs ([README](https://github.com/blockbrain-ai/cygnet-recipe#measured-jevbenchs-public-set), JevBench CLI commit `2fa63fa`, `--adapter typesafe`, 231 public items):

| Setup | Correct | easy / standard / hard | p50 / p95 latency (serial) |
|---|---|---|---|
| RTX A6000 48 GB, revision not recorded | 203/231 (87.9%) | 48/48 · 70/72 · 85/111 | 0.066 / 0.072 s |
| L40S 48 GB, revision `707f0a3` | 203/231 (87.9%) | 48/48 · 70/72 · 85/111 | 0.050 / 0.052 s |
| RTX A6000, revision `707f0a3` | 204/231 | 48/48 · 70/72 · 86/111 | not reported |

One item (`hard-sol-a-multi_hop-07`) is a near-tie that GPU batch order can flip.

Decision server on one H100 NVL ([README](https://github.com/blockbrain-ai/cygnet-recipe#serving-applications)):

- BANKING77, 400 test messages, 20 intents each: 87.00% grouped vs 86.50% single pass. All 77 intents: 73.50%. CLINC150, all 150 intents: 91.25%.
- ECE at T = 3.4 vs T = 1: 0.067 vs 0.249 on 77 intents; 0.171 vs 0.074 on 150. The temperature is "not established" for grouped reads.
- 20 options: 0.062 s p50 for one client; 38.5 requests/s at 0.209 s p50 for 8 clients. 77 options (5 passes): 0.193 s p50.

No kyr0, 4nt0ineB or Fastino fast-decisions row as of 2026-10-02 (repo benchmark pages).

## Running it

CUDA, as measured (one RTX A6000 or L40S, 48 GB; other cards not measured):

```bash
pip install vllm==0.30.0      # or docker vllm/vllm-openai:v0.30.0
vllm serve google/gemma-4-12B-it --revision 707f0a3b8a3c7ad586ed01e27eafbad8a27dd0f7 \
  --served-model-name cygnet --host 127.0.0.1 --port 8890 \
  --max-model-len 16384 --gpu-memory-utilization 0.90

git clone https://github.com/blockbrain-ai/cygnet-recipe && cd cygnet-recipe
SHIM_VLLM=http://127.0.0.1:8890/v1/chat/completions SHIM_MODEL=cygnet SHIM_TEMPERATURE=3.4 CYGNET_PORT=8010 \
  python3 shim/decision_server.py

curl -s http://127.0.0.1:8010/v1/systemone -H 'Content-Type: application/json' -d '{"state": "warm-up",
  "questions": {"decision": {"type": "noul", "instructions": "Is this a warm-up?",
  "criteria": {"true": "yes", "false": "no"}}}}'
```

Tests without a GPU: `python3 shim/test_shim.py`, `python3 shim/test_decision_server.py`.

**On an M5 Max (128 GB):** use Ollaya, which documents macOS on Apple silicon and runs GGUF models on llama.cpp with Metal ([Ollaya README](https://github.com/ollaya-dev/ollaya)):

```bash
curl -fsSL https://ollaya.dev/install.sh | sh
ollaya run cygnet          # pulls gemma-4-12B-it-Q8_0.gguf, 12.67 GB, sha256-checked
```

- The [`ollaya-dev/cygnet`](https://huggingface.co/ollaya-dev/cygnet) package (revision `18a9e58`, created 2026-09-30; 0 downloads, 0 likes) holds only `decision.json` and `calibration.json` (T = 3.4); weights come from [`ggml-org/gemma-4-12B-it-GGUF`](https://huggingface.co/ggml-org/gemma-4-12B-it-GGUF) at `e3e6817`. It pins cygnet-recipe commit `3cf591c`.
- It runs Q8_0, not the BF16 that JevBench measured. Its parity check (502 questions, every decision the same as stock llama-server b11146) ran on an RTX 4090, not a Mac. The `decision.json` caps options at 20.
- On any llama.cpp backend, keep thinking off (`chat_template_kwargs: {"enable_thinking": false}`). With thinking on, a reported run dropped the easy tier from 48/48 to 42/48 ([issue #1](https://github.com/blockbrain-ai/cygnet-recipe/issues/1)). Ollaya's template inserts an empty thought channel.
- Running `decision_server.py` against llama-server or vllm-metal on a Mac is undocumented; it relies on vLLM's `structured_outputs.choice` and top-20 log-probabilities (unverified elsewhere).

## Scaling limits

- **Options:** benchmark shim 26 (422 above). Decision server 255: up to 20 per pass, then groups of 13 to 20 (`CYGNET_GROUP_SIZE`) and a final pass over group winners, `ceil(K / 20) + 1` passes. Score up to 10 levels. Ollaya package 20.
- **Context:** 16,384 tokens as served (`--max-model-len`); longer inputs return 422. The shim refuses to run (503) if the server reports under 4,096. Larger windows are untested by the author.
- **Questions per call:** no documented maximum; each question is its own pass, run concurrently, `CYGNET_MAX_PARALLEL` 8 vLLM requests in flight.
- **Body:** 16 MiB (`CYGNET_MAX_BODY`).
- **Input:** text and JSON state only in the recipe; JSON state is rendered with `json.dumps(..., indent=1)`. Image input is not documented.
- **Cost:** each question bills its own state tokens; 255 options take 14 passes.

## Fine-tuning

- None: the weights stay frozen.
- The only fitted parameter is the temperature. `calibration/fit.py` reproduces T = 3.4 from `calibration/items.jsonl` and `calibration/letters-reads.jsonl`; you can refit it on your own labelled items (`SHIM_TEMPERATURE`).
- To change the model's behaviour, fine-tune Gemma-4-12B-it separately; [Winnow-12B](open-reproductions.md#winnow) and [Jev-Omni](open-reproductions.md#other-gemma-based) are fine-tuned Gemma-4-12B decision models.

## Data governance

Not legal advice. Cygnet has no hosted API. Self-hosted means your infrastructure: the shim makes no network calls other than to the local vLLM server ([README, Disclosures](https://github.com/blockbrain-ai/cygnet-recipe#disclosures)).

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; only way to run it | [README](https://github.com/blockbrain-ai/cygnet-recipe) |
| Fine-tuning | No weights trained; temperature refit only | [README](https://github.com/blockbrain-ai/cygnet-recipe#how-the-readout-works) |
| Processing location | Your hardware | |
| EU processing option | Your choice of hardware | |
| Retention / ZDR | Your logs only; the decision server documents no request logging (unverified) | [`shim/decision_server.py`](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/shim/decision_server.py) |
| Training on inputs | No vendor in the loop | |
| DPA / GDPR | No processor, so no DPA. Weights download from Hugging Face once | |
| Certifications | n/a | |
| Weights licence | Gemma 4: `apache-2.0` in HF metadata, linked to the Gemma 4 licence, plus the Gemma Prohibited Use Policy. Shim MIT | [HF API](https://huggingface.co/api/models/google/gemma-4-12B-it), [NOTICE.md](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/NOTICE.md) |

Use restriction: NOTICE.md says the Gemma Prohibited Use Policy "bars using Gemma or its derivatives to make automated decisions in domains that affect material or individual rights", and that deploying Cygnet "for decisions of that kind is outside what the policy allows". Check the policy before using it for credit, hiring, insurance, housing or similar decisions.

Calibration data: 241 items blockbrain generated; none shares a state with a JevBench public item ([PROVENANCE.md](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/PROVENANCE.md)). No other training data is involved.

## Caveats

- Cygnet is a prompt and readout over a public model. Any frozen instruct model can be wrapped the same way; the result depends on Gemma-4-12B-it.
- Its JevBench lead over Winnow-12B and Jev sits inside overlapping 95% intervals; Intelligence alone is below both.
- The A6000 run did not record the weights revision.
- The calibration temperature was fitted on single-pass reads; on grouped reads (over 20 options) it raised ECE on CLINC150.
- The Mac path (Ollaya, Q8_0, Metal) has no published accuracy or latency figures.
- The org is `blockbrain-ai`; the copyright holder is "Nood Co" and the merge author is `nood-co1`. The relation between the names is not stated (unverified).

## Sources

- [`blockbrain-ai/cygnet-recipe`](https://github.com/blockbrain-ai/cygnet-recipe): README, [NOTICE.md](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/NOTICE.md), [CREDITS.md](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/CREDITS.md), [PROVENANCE.md](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/PROVENANCE.md), [LICENSE](https://github.com/blockbrain-ai/cygnet-recipe/blob/main/LICENSE), [commits](https://github.com/blockbrain-ai/cygnet-recipe/commits/main)
- JevBench: [v1.5.5 API](https://benchmarkheaven.com/api/jevbench/v1.5.5), [board](https://benchmarkheaven.com/jev-models), [bench request #71](https://github.com/fstandhartinger/jevbench/issues/71)
- HF: [`google/gemma-4-12B-it`](https://huggingface.co/google/gemma-4-12B-it) ([API](https://huggingface.co/api/models/google/gemma-4-12B-it): sha `707f0a3`), [`ollaya-dev/cygnet`](https://huggingface.co/ollaya-dev/cygnet) (README, `12b/decision.json`, `12b/calibration.json`), [`ggml-org/gemma-4-12B-it-GGUF`](https://huggingface.co/ggml-org/gemma-4-12B-it-GGUF)
- [Ollaya README](https://github.com/ollaya-dev/ollaya)
- Google: [Gemma 4 licence](https://ai.google.dev/gemma/docs/gemma_4_license), [Prohibited Use Policy](https://ai.google.dev/gemma/prohibited_use_policy) (linked from NOTICE.md; not re-read)

All read 2026-10-02.

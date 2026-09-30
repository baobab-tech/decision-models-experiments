# Kev

| | |
|---|---|
| Vendor | Jared Palmer (individual project, GitHub `jaredpalmer`); built with Devin per the README |
| Type | Decoder with the LM head replaced by a pointer head. 0.8B–9B: rank-16 LoRA + head on a frozen base. Kev-27B v2: full-weight fine-tune + head |
| Backbone | Qwen3.5-0.8B/4B/9B-Base; Qwen3.8-27B for Kev-27B |
| Size | 0.8B, 4B, 9B, 27B (base parameters). Kev-27B v2 bf16 weights: 51 GB |
| Licence | Apache-2.0: code, adapters, heads, and the Qwen bases (per their HF cards) |
| Run it via | `kev.serve` from the GitHub repo; MLX on Apple Silicon for 0.8B–9B |

Checked 2026-09-30. Nothing was run locally; no weights were downloaded.

## Overview

- Code: [`jaredpalmer/kev`](https://github.com/jaredpalmer/kev) (created 2026-09-17, last push 2026-09-30, 8,041 stars). Weights: HF collection [`jaredpalmer/kev`](https://huggingface.co/collections/jaredpalmer/kev-6aad9d0ea49f2589665e07cd) and GitHub release `kev-family` with SHA-256 checksums. Browser demo: [HF Space `jaredpalmer/kev`](https://huggingface.co/spaces/jaredpalmer/kev) (Kev-4B, Kev-0.8B). [HN 49783999](https://news.ycombinator.com/item?id=49783999): 462 points, about 2026-09-21.
- Input is serialised as `<state> …` then, per question, `<q> instructions <opt> … </opt> … <decide>`. The pointer head scores each `</opt>` hidden state against the `<decide>` hidden state; a softmax gives the probabilities. Design source: Archer Hume, ["Jev's Architecture Unmasked"](https://archerhume.com/posts/jevs-architecture-unmasked).
- Qwen3.5/3.8 Gated DeltaNet layers ignore attention masks, so each question runs as its own row over a cached state. On attention-only bases (Qwen3) one masked sequence gives identical probabilities. Joint vs separate questions agree within 4e-6 (fp32).
- Training: cross-entropy on the correct answer; adapter and head trained together; base frozen (0.8B–9B). The README states no Jev outputs were used.
- Calibration: one temperature per checkpoint, applied at load; it never changes the argmax. 9B 2.30, 4B 2.41, 0.8B 2.35, fitted on their in-distribution dev sets; Kev-27B 1.32, fitted on held-out datasets it never trained on (`v1-lora`: 1.38). `KEV_TEMPERATURE=1.0` returns raw probabilities. `python -m kev.calibrate` fits a workload temperature (Kev-4B card: WANLI ECE 0.166 → 0.052, T 3.91); `scripts/calibrate_checkpoint.py` gives an out-of-fold estimate.

## Schema

`POST /v1/systemone` in TypeSafe's wire format; the README states the TypeSafe Python SDK (`typesafe_sdk`, installed by `uv sync --extra serve`) works unchanged. README example:

```bash
curl -s localhost:8009/v1/systemone -H 'content-type: application/json' -d '{
  "state": "Shoes arrived two weeks late and in the wrong size. Also I see two charges on my card.",
  "model": "kev-latest",
  "questions": {
    "department":  {"type": "choice", "instructions": "Which team should handle this?",
                    "criteria": {"returns": "Exchanges, refunds, wrong or damaged items",
                                 "shipping": "Delivery status, delays, lost packages",
                                 "billing": "Charges, invoices, payment problems"}},
    "escalate":    {"type": "noul",  "instructions": "Does this need urgent human attention?"},
    "frustration": {"type": "score", "instructions": "How frustrated is the customer?",
                    "criteria": ["Calm", "Frustrated", "Very angry"]}}}'
```

Response (Kev-4B, bf16, Apple M5): `department` returns 0.47 / shipping 0.28 / billing 0.25, confidence 0.21; `escalate` 0.93; `frustration` 1.44; `latency_ms` 495.

Differences from [../concepts.md](../concepts.md#typed-question-format):

- Choice takes 1–255 options (1 option gives confidence 1). Score takes 1–255 levels (Jev: 2–10).
- Choice confidence `(p_max − 1/K) / (1 − 1/K)`; Score confidence `max(0, 1 − E|level − mode| / D)`. The README attributes both to TypeSafe's reference adapter `system-one-adapter` 0.2.1.
- `usage.output_tokens` counts tokens in the serialised answers. Invalid requests return `422`; responses carry `x-typesafe-request-id`.
- Object/array `state` is converted to labelled text; delimiter-like strings are escaped.
- Extra routes: `GET /v1/models` (cards plus loaded checkpoint, backend, precision); `POST /v1/systemone/permute` (one Choice under `n_perm` option orders, 1–64, default 6); `POST /v1/systemone/separate` (one forward pass per question).
- Env vars: `KEV_TEMPERATURE`; `KEV_DATE_FACTS=1` (appends day counts between date pairs); `KEV_DTYPE=fp32` (exact evaluation path; bf16 default); `KEV_API_KEY` (bearer auth). Binds `127.0.0.1`; unauthenticated unless `KEV_API_KEY` is set.

## Benchmarks

Author's numbers; cells are development / test. "New sources" = `transfer-v4`, 764 records (QNLI, SciQ, PAWS, MMLU, Emotion, TweetEval, held-out policies and rules). Jev ran on development sets only. README and card numbers are checked in CI against committed reports (`docs/claims.json`, `scripts/verify_claims.py`).

| Model | Acc., new sources | Acc., trained sources | Brier, new sources | Runs on (README) |
|---|---|---|---|---|
| Kev-0.8B | 0.648 / 0.697 | 0.827 / 0.838 | 0.481 / 0.416 | Any Apple Silicon Mac, L4 |
| Kev-4B | 0.817 / 0.838 | 0.873 / 0.865 | 0.269 / 0.242 | 32 GB Mac, L40S, H100 |
| Kev-9B | 0.822 / 0.852 | 0.872 / 0.874 | 0.286 / 0.237 | 32 GB Mac, L40S, H100 |
| Kev-27B (v2) | 0.851 / 0.889 | 0.865 / 0.866 | 0.225 / 0.156 | B200, H200, H100 80 GB |
| Jev (hosted) | 0.857 / – | 0.845 / – | 0.211 / – | TypeSafe API |

- Kev-27B v2 (card): transfer-v4 test 0.8887, served Brier 0.154 (v1 0.8963 / 0.160). Breadth index, 14 held-out datasets: v2 52.3, v1 50.2, Jev 54.0, AutoJev-27B 50.0. CUAD long contracts: v2 0.874 vs v1 0.890 (ECE 0.053 vs 0.007).
- Calibration on new sources (Kev-9B): ECE 0.106 → 0.042 with the temperature; confident errors (wrong at p ≥ 0.9) 8.7% → 4.0% (Jev 3.7%). Coverage at 5% error: Kev 0.45–0.57, Jev 0.70.
- Knowledge: MMLU Kev-9B 0.74, Kev-27B 0.90, Jev 0.90; MMLU-Pro Kev-9B 0.52, Kev-27B 0.675, Jev 0.840.
- Jev Decision Index 0.2.1 (balanced skill, 2026-09-28): Kev-9B 38.48, Kev-4B 34.64, Kev-0.8B 14.60; Jev 1.13.0 57.91.
- External suites, Kev-9B vs Jev: SemIf 144 decisions 0.917 vs 0.965; WANLI-256 0.703 vs 0.758; TypeSafe-102 agreement / distance 0.809 / 0.226 vs 0.891 / 0.125 (89 rows within 8,192 tokens). Unknowable records answered at ≥ 0.9 confidence: 0% vs 9%. `KEV_DATE_FACTS=1` on deadline questions: 0.80 → 0.90 (Jev 0.93).
- Serving latency (README, median of 20, new text / same text again): 6 questions short text: 0.8B (L4) 22.7 / 16.1 ms, 4B (H100) 18.1 / 12.9, 9B (H100) 24.0 / 16.6, 27B (H100, measured on v1) 75.0 / 52.0, 27B v2 (H200) 67.2 / 50.0. 5 questions on 2,200 tokens: 108.6 / 32.3, 89.4 / 22.5, 88.5 / 26.4, 277.5 / 79.3 ms. Req/s at 64 clients: 62.8, 100.8, 79.5, 28.9.
- Apple M5 32 GB, MLX, 5 questions on ~270 tokens: Kev-0.8B 149 ms new / 28 ms cached; Kev-4B 721 / 136 ms.

Independent: [local-jev-bench](https://github.com/tak-bro/local-jev-bench), M3 Max 36 GB, MLX, 2026-09-30:

| Model | English 30 | BANKING77-20† | transfer-v4 | typed-decisions | NSMC (ko) | KLUE-YNAT (ko) | Order flip (B77-20) |
|---|---|---|---|---|---|---|---|
| Kev-9B | 90% | 89% | 81% | 72% | 86% | 73% | 10% |
| Kev-4B | 89% | 89% | 80% | 67% | 83% | 74% | 8% |
| Kev-0.8B | 75% | 88% | 65% | 46% | 80% | 63% | 8% |

- † BANKING77 is in Kev's training data. Kev-4B reproduced its card on transfer-v4: 534/656 (81.4%) vs 0.817. First-call p50: 0.8B 28–58 ms, 4B 159–307 ms, 9B 297–546 ms; on typed-decisions' long states 152 / 859 / 1,552 ms.

## Running it

M5 Max 128 GB: Kev-0.8B, 4B and 9B have a Mac path. Kev-27B "needs an 80 GB GPU and has no Mac path". Requires Python 3.12 or 3.13 and uv (`.python-version` selects 3.13; torch has no 3.14 wheels).

```bash
git clone https://github.com/jaredpalmer/kev.git && cd kev
uv sync --extra serve        # installs MLX on Apple Silicon; the server uses it automatically
uv run --extra serve python -m kev.serve --run jaredpalmer/kev-4b --port 8009
```

Minimal example: the `curl` request under [Schema](#schema), or with the SDK: `TypeSafeClient(api_key="local", base_url="http://127.0.0.1:8009", model="kev-latest").system_one(state=..., questions={"billing": Noul(instructions="Is this about billing?")})`, read `response.nouls["billing"].noul`.

- First run downloads the adapter and Qwen base into the HF cache; pre-fetch with `hf download jaredpalmer/kev-4b` and `hf download Qwen/Qwen3.5-4B-Base` (standard `hf` usage, not in the README). `--run` also takes a local directory or a Hub revision (`jaredpalmer/kev-4b@qwen3`).
- Macs serve in bf16: probabilities differ from fp32 by up to about 0.05; the top answer changes on about one question in 300. `KEV_DTYPE=fp32` gives the exact path. Memory: Kev-4B server 2.7 GB RSS after startup on M3 Max (local-jev-bench). Kev-9B needs about 17 GB GPU memory (README, CUDA).
- The Kev-4B card says DeltaNet has no MPS implementation and recommends `kev-4b@qwen3` on Apple Silicon; the README says `uv sync --extra serve` installs MLX on Apple Silicon and the server uses it automatically. No Ollama path. Playground: `cd playground && npm install && npm run dev -- -p 3001` (Node 20.9+).

| Repo | Base | Library | Last modified | Downloads | Commit |
|---|---|---|---|---:|---|
| [`kev-0.8b`](https://huggingface.co/jaredpalmer/kev-0.8b) | Qwen3.5-0.8B-Base | peft | 2026-09-24 | 9,814 | `9a45d25e` |
| [`kev-4b`](https://huggingface.co/jaredpalmer/kev-4b) | Qwen3.5-4B-Base | peft | 2026-09-24 | 13,170 | `139fdd94` |
| [`kev-9b`](https://huggingface.co/jaredpalmer/kev-9b) | Qwen3.5-9B-Base | peft | 2026-09-21 | 3,162 | `2629c06a` |
| [`kev-27b`](https://huggingface.co/jaredpalmer/kev-27b) | Qwen3.8-27B | transformers | 2026-09-30 | 518 | `0d7f9b49` |

- Adapter repos hold `adapter_model.safetensors`, `head.pt` (pointer head + temperature), tokenizer, `provenance.json`, `training_config.json`, `train.log`.
- Kev-27B `main` is v2 (2026-09-30): full-weight SFT of Qwen3.8-27B (revision `1d4bf0f2`) on a private 145,840-record corpus, blended 0.85 × SFT + 0.15 × v1. v1 (LoRA, T 1.38) is at tag `v1-lora`. Latest commit `0d7f9b49` (2026-09-30) changed only the card; weights unchanged since `28be62e9`. Older versions are Hub tags (`kev-4b@qwen3`, `@v7-base`, `@night2-du-release`, `@r8-documents-release`). Qwen3 generation: `kev-0.6b`, `kev-4b@qwen3`, `kev-8b`. Prototype: `kev-0.5b` (Qwen2.5-0.5B).

## Scaling limits

- **Options:** Choice 1–255, Score 1–255. Each option adds `<opt> … </opt>` tokens to its row. Rows pack into a 16,384-token budget per forward pass (cached state counted once per question); memory does not grow with question count. No accuracy or latency curve for 10 → 100+ options is published; latency is expected to grow with option tokens (inference, unverified). Above 255: cascade Choice questions.
- **Multi-label:** none. Use one `noul` per label; questions are isolated. 100 Nouls cost 100 short rows plus one state pass on hybrid bases (inference from the README).
- **Input length:** 0.8B–9B trained on states ≤ 384 tokens (≤ 1,024 with one question); Kev-27B v2 on states ≤ 32,768. Serving accepts states ≤ 65,536 tokens plus 8,192 per question. TypeSafe-102 was scored under an 8,192-token context, which rejected 13 of 102 documents. Kev-9B: 0.92 correct inside 384 tokens, 0.75–0.79 beyond. Kev-27B v1 on questions buried in 1k–6k tokens: 0.833 vs Kev-9B 0.556. No Mac latency at ~2,000 tokens is published.

## Fine-tuning

LoRA + head from a released checkpoint (`--init_from`), locally or on Modal. Data: JSONL, one API-shaped request per line with a `label` per question (`choice`: option name; `noul`: `true`/`false`; `score`: level index from 0). Keep 10–20% for evaluation.

```bash
uv run python -m kev.train --data train.jsonl --base Qwen/Qwen3.5-4B-Base --init_from jaredpalmer/kev-4b \
    --epochs 2 --lr 2e-5 --batch 1 --accum 8 --dtype bf16 --checkpointing 1 --device cuda --out runs/mine
uv run python -m kev.benchmark --run runs/mine --data heldout.jsonl --out runs/mine-eval
```

- `--base` must match the checkpoint; the trainer checks base, revision, LoRA rank and head size. `--batch 1 --accum 8` bf16 fits 0.8B on a 4 GB GPU.
- Mac: one job at a time; the README calls the Qwen3.5 Mac path "slow". Whether `--device mps` is the flag is not stated (unverified).
- Without `--init_from`, one user's 836-record run scored 0.33 vs 0.83 with it.
- Reported gains: support workload (3 questions, 1,050 generated records, 15 min on H100) 67.7% → 73.6%, automatable share at 5% error 34% → 48%; 5,219 CFPB complaints, one epoch, 0.804 → 0.904. At 400 records the gain was within noise.
- Coding-agent path: `npx skills add jaredpalmer/kev@kev-finetune`; runs on Modal, about $1 per Kev-4B run on H100.

## Data governance

- **Self-host / air-gap:** yes. Weights on HF and in the GitHub release with SHA-256 checksums. Once base and adapter are cached, `kev.serve` makes no documented outbound calls. `HF_HUB_OFFLINE=1` operation is not documented (unverified).
- **Licences:** code, adapters, heads Apache-2.0; bases Qwen3.5-0.8B/4B/9B-Base and Qwen3.8-27B Apache-2.0 (HF metadata). Training datasets keep their own licences (per card: BANKING77, BoolQ, AG News, MultiNLI, SST-5, Yelp Review Full, TREC, DBpedia-14, Amazon Reviews, IMDB; about 35 sources for Kev-27B); not reviewed here. The TypeSafe SDK (`typesafe-sdk` 0.7.2) is MIT (PyPI).
- **Hosted options:** HF Space: input goes to Hugging Face; region, retention and logging not documented publicly as of 2026-09-30; send only public or synthetic data. Modal (`kev_serve.py`): the user's own Modal account on an L40S; region, retention and DPA follow the user's Modal contract; scales to zero, about 35 s cold start. No vendor API; no training on inputs unless the user trains.
- **Provenance and trust:** single maintainer, built with Devin. Kev-27B starts from Qwen's post-trained release (training data unknown to the author); v2 trained on a private corpus (`sft-v2-r22`, 145,840 records). `head.pt` files are PyTorch pickles; verify release checksums. `kev.jev` benchmark tooling calls Jev through Vercel AI Gateway; the server does not use it.

## Caveats

- Kev-27B `main` changed to v2 on 2026-09-30; pin a revision. v2 was chosen after its test partitions had been read for a previous round (card: weakens the confirmation).
- The Kev-4B card's "no MPS implementation" note conflicts with the README's MLX path. Calibration is one in-distribution temperature; coverage at 5% error is below Jev.
- Option order changes 8–10% of answers on BANKING77-20. Accuracy drops beyond 384 tokens for 0.8B–9B. Knowledge-heavy questions trail Jev.

## Sources

- [GitHub: jaredpalmer/kev](https://github.com/jaredpalmer/kev) (README, 2026-09-30) and [GitHub API metadata](https://api.github.com/repos/jaredpalmer/kev)
- HF model cards and API: [kev-0.8b](https://huggingface.co/jaredpalmer/kev-0.8b), [kev-4b](https://huggingface.co/jaredpalmer/kev-4b), [kev-9b](https://huggingface.co/jaredpalmer/kev-9b), [kev-27b](https://huggingface.co/jaredpalmer/kev-27b) (v2 card), [api/models/jaredpalmer/kev-4b](https://huggingface.co/api/models/jaredpalmer/kev-4b)
- [HF Space: jaredpalmer/kev](https://huggingface.co/spaces/jaredpalmer/kev); [eval suites dataset](https://huggingface.co/datasets/jaredpalmer/kev-suites)
- [Hacker News 49783999](https://news.ycombinator.com/item?id=49783999)
- [GitHub: tak-bro/local-jev-bench](https://github.com/tak-bro/local-jev-bench) (MIT; results 2026-09-30, M3 Max 36 GB)
- [Archer Hume, Jev's Architecture Unmasked](https://archerhume.com/posts/jevs-architecture-unmasked)
- Qwen base licences: [Qwen3.5-4B-Base](https://huggingface.co/Qwen/Qwen3.5-4B-Base), [Qwen3.8-27B](https://huggingface.co/Qwen/Qwen3.8-27B)
- [Jev Decision Index `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index) (0.2.1, generated 2026-09-28); [PyPI: typesafe-sdk](https://pypi.org/project/typesafe-sdk/)
- [TypeSafe API docs](https://docs.typesafe.ai/api)

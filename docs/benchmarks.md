# Benchmarks for decision models

Survey date: 2026-09-30. Every score is copied from the linked source; none was re-run here. "Jev" means TypeSafe AI's hosted Jev 1.13.0. Full tables: [benchmarks-leaderboards.md](benchmarks-leaderboards.md). Entries marked "(AaJ)" come from Han Xiao's [All about Jev](https://hanxiao.io/all-about-jev/) dataset (local copy `data/all-about-jev/all-methods.jsonl`, 2026-09-30).

| Benchmark | Maintainer | Items | Headline metric | Current | Systems |
|---|---|---|---|---|---:|
| [JevBench](#jevbench) | Benchmark Heaven (F. Standhartinger) | 1,624 per system (904 open, 720 sealed) | 4-axis harmonic mean | v1.5.4 | 106 ranked |
| [typed-decision-bench (kyr0)](#typed-decision-bench-kyr0-275-capabilities) | Aron Homberg (kyr0) | 27,598 cases, 275 suites | macro soft accuracy | 2026-09-23 | 7 runs |
| [typed-decision-bench (4nt0ineB)](#typed-decision-bench-4nt0ineb-60-intents-enfr) | 4nt0ineB | 500 MASSIVE commands × 3 language conditions, plus French government data | hard accuracy | 2026-09-30 | 14 models |
| [Decision Index](#decision-index) | multimodalart (apolinario) | 120,340 requests, 38 benchmarks | chance-corrected balanced skill | 0.2.1 | 71 |
| [S1Bench](#s1bench) | Bespoke Labs suite | 3,880 items, 13 subsets | macro accuracy | — | card-reported |
| [Fastino fast-decisions](#fastino-fast-decisions) | Fastino | 5,100 held-out rows, 17 domains | exact-match accuracy | — | 7 |

## JevBench

Repo [`fstandhartinger/jevbench`](https://github.com/fstandhartinger/jevbench) (MIT); live board [benchmarkheaven.com/jev-models](https://benchmarkheaven.com/jev-models); aggregate JSON [`/api/jevbench/v1.5.4`](https://benchmarkheaven.com/api/jevbench/v1.5.4). All read 2026-09-30. The repo README still headlines v1.4.2.2; the live board runs v1.5.4 under the method frozen 2026-09-25 ([`docs/METHOD-v1.5.md`](https://github.com/fstandhartinger/jevbench/blob/main/docs/METHOD-v1.5.md)).

- **Task:** state plus a bounded rubric in, a typed answer (ideally a distribution over options) out.
- **Axes (0–100):** Intelligence (chance-corrected accuracy), Calibration (ECE plus fidelity to gold distributions; label-only systems get 0), Speed (100 at 0.1 s, −20 per 10× slower, mean of p50 and p95), Cost (100 at $0.001 per 1,000 decisions, −30 per 10×).
- **Latency adjustment:** self-hosted and demo endpoints are scored at ×2 + 0.15 s ("an assumption, not a measurement"); production APIs are not adjusted. Latency is measured from a server in Germany.
- **Cost unit:** dollars per 1,000 decisions, not per 1,000 tokens. Most open rows carry an estimate from the base model's hosted list price.
- **Tiers (v1.2 item set, 534 decisions):** easy 72, standard 96, judge 146, hard 220.
- **Public vs sealed (v1.4):** 231 public items (72 original, 48 easy, 111 hard) in [`datasets/public/`](https://github.com/fstandhartinger/jevbench/tree/main/datasets/public); 308 sealed items, aggregates only.
- **Public vs sealed (v1.5):** 601 of 904 open items published; 720 sealed items drawn per release from a 2,805-item pool.

| Version | Items per system | Score | Main changes |
|---|---|---|---|
| v1.1 (2026-09-19) | 314 | mean of Capability, Speed, Cost | easy tier added; calibration reported, not scored |
| v1.2 | 534 | geometric mean of 4 axes | 220-item hard tier (111 public, 109 held out); Calibration becomes an axis |
| v1.3.0 | 534 | geometric mean, ×(I/50)² below 50 Intelligence | Intelligence chance-corrected per tier |
| v1.4 → v1.4.2.2 (2026-09-27) | 842 (534 + 308 sealed) | harmonic mean | sealed = 20% of Intelligence; public−sealed gap >25 pp cuts Intelligence; Speed and Cost gated below 50 |
| v1.5 → v1.5.4 (live) | 1,624 | harmonic mean, equal axes ("headline A") | sealed = 50% of Intelligence; tiers 10/20/30/40; Choice, Noul and Score weighted equally; per-item chance; penalty for gap more than 8 points above the field median (5.19); paired-bootstrap ties |

**Run it yourself** ([README "Reproduce"](https://github.com/fstandhartinger/jevbench#reproduce), Python 3.10+):

```sh
python -m jevbench.cli run --tasks datasets/public/original.jsonl \
  --adapter typesafe --model jev-latest --key-env TYPESAFE_API_KEY \
  --price-in-per-m 0.042 --price-out-per-m 0 \
  --results RUN/results.jsonl --raw-dir RUN/raw \
  --ledger RUN/ledger.jsonl --cap-usd 15 --manifest RUN/manifest.json

python -m jevbench.cli summarize --tasks datasets/public/original.jsonl \
  --results RUN/results.jsonl --public-export RUN/summary.json
```

Other adapters: `systemone_list`, `gradio_space`, `local_openjev`, `openai_compat`. A self-run covers public items only and is not an official entry.

**Leaderboard, v1.5.4 top 10** (all 109 rows: [benchmarks-leaderboards.md](benchmarks-leaderboards.md#jevbench-v154-headline-a)):

| # | System | Size | Score | Intel. | Calib. | Speed | Cost | $/1k | Run |
|---:|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | Cygnet (frozen Gemma-4-12B-it) | 12B | 73.7 | 71.1 | 87.0 | 91.0 | 56.4 | 0.028 est. | local GPU |
| 2 | Winnow-12B Q8 | 12B | 73.2 | 74.4 | 84.1 | 86.1 | 56.6 | 0.028 est. | local GPU |
| 3 | Jev 1.13.0 | undisclosed | 72.1 | 72.0 | 88.0 | 83.8 | 54.7 | 0.032 est. | hosted API |
| 4 | JevK5 v0.3 | 4B | 71.9 | 56.3 | 88.3 | 93.6 | 63.1 | 0.017 est. | local GPU |
| 5 | Plumb-4B (JevK5 v0.2 + LoRA) | 4B | 71.6 | 55.8 | 87.4 | 93.5 | 63.1 | 0.017 est. | local GPU |
| 6 | Jev-Omni (Gemma-4-12B merged) | 12B | 71.5 | 70.5 | 82.6 | 84.7 | 56.1 | 0.029 est. | local GPU |
| 7 | decider-4b v2 | 4B | 71.3 | 55.8 | 85.6 | 90.9 | 64.5 | 0.015 est. | local GPU |
| 8 | Decision 4B v1.2 (FlyMyJev) | 4B | 70.8 | 53.7 | 88.6 | 93.5 | 63.1 | 0.017 est. | local GPU |
| 9 | Imajev-4B | 4B | 70.4 | 53.5 | 88.1 | 91.1 | 63.3 | 0.017 est. | local GPU |
| 10 | Decision 4B v1.1 (FlyMyJev) | 4B | 70.4 | 53.1 | 87.3 | 93.5 | 63.1 | 0.017 est. | local GPU |

- Unranked: classifier.dev fast tier 74.7 (honorable mention; it serves Jev).
- Previous top five, v1.4.2.2 (2026-09-27): Imajev-4B 67.37, Plumb-4B 65.84, decider-4b v2 64.13, Jev 63.29, JevK5 v0.2.0 62.04 ([README](https://github.com/fstandhartinger/jevbench#v1422-imajev-4b-leads-plumb-4b-is-2-current)).

## typed-decision-bench (kyr0, 275 capabilities)

Repo [`kyr0/typed-decision-bench`](https://github.com/kyr0/typed-decision-bench); results [kyr0.github.io/typed-decision-bench](https://kyr0.github.io/typed-decision-bench/) (last updated 2026-09-23); paper [/paper/](https://kyr0.github.io/typed-decision-bench/paper/). Not in the AaJ dataset.

- **Items:** 275 suites, 27,598 synthetic cases (choice 18,140, noul 7,250, score 2,208), generated with GPT-6 Astra and frozen as literal `POST /v1/systemone` requests.
- **Splits:** `test` 22,001 scored; `calibrate` 5,499 used only to fit temperatures; `train`.
- **Headline metric:** macro soft accuracy, the probability mass on the gold label, averaged over suites. Hard accuracy, NLL, Brier, ECE (15 bins) and p50/p95 latency are also reported.
- **Calibration method:** qtype-stratified temperature scaling. One temperature per question type (`choice`/`noul`/`score`) is fitted on `calibrate` and saved as `calibration.json`; argmax never changes. The repo has no `CALIBRATION.md` (404 on 2026-09-30); the method is in the README "Calibration" section and the paper.
- **Hardware:** all runs on one NVIDIA H200 NVL.
- **Run:** `make setup`, set `TYPESAFE_MODEL` / `TYPESAFE_API_KEY` / `TYPESAFE_BASE_URL` in `.env`, then `make eval` (score, metrics, comparison) and `make calibrate`.

| Run | Backbone | Soft acc. | Hard acc. | ECE-15 | p50 ms | p95 ms | VRAM (8k KV) | Precision |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Jev 1.13.0 | closed | 88.08% | 93.41% | 0.084 | 716.4 | 778.8 | hosted | — |
| Bonsai 2 27B, calibrated (kyr0) | Qwen3.8-27B ternary (PrismML) | 76.46% | 83.30% | 0.130 | 170.9 | 448.0 | 9.0 GB | Q2_64 |
| Bonsai 2 27B, calibration init (kyr0) | same | 76.29% | 83.30% | 0.134 | 165.0 | 362.0 | 9.0 GB | Q2_64 |
| openjev-qwen3.5-4b (fastjev) | Qwen3.5-4B | 74.13% | 79.12% | 0.143 | 1,066.1 | 1,478.9 | 12.6 GB | BF16 |
| Winzling-Spark-X2.5-4B (kyr0) | not stated | 70.97% | 71.42% | 0.249 | 1,056.6 | 1,783.5 | 9.6 GB | BF16 |
| Von 1.1 | not stated (395M) | 48.57% | 49.58% | 0.372 | 38.5 | 46.5 | 3.8 GB | FP32 |
| Laya | ModernBERT-large | 46.70% | 52.55% | 0.278 | 36.7 | 44.4 | 1.4 GB | FP32 |

Source: [`docs/model_summary.csv`](https://kyr0.github.io/typed-decision-bench/model_summary.csv) and [`models.json`](https://github.com/kyr0/typed-decision-bench/blob/main/models.json), read 2026-09-30. Three of the seven runs are the author's own models.

## typed-decision-bench (4nt0ineB, 60 intents, EN/FR)

Repo [`4nt0ineB/typed-decision-bench`](https://github.com/4nt0ineB/typed-decision-bench) (MIT code), README updated 2026-09-30. A separate project from kyr0's, with the same name. All models are used zero-shot with hand-written criteria.

- **MASSIVE intents:** 500 commands, one of 60 intents (also 18 scenarios), in three conditions: `EN_EN`, `FR_EN` (French command, English criteria), `FR_FR`.
- **French written questions:** 1,439 Assemblée nationale questions routed to one of 36 ministries, plus 500 reply-matching items.
- **Other tests:** record counting in long texts; a redacted French loan offer (17 questions × 20 runs).
- **Automatable:** the largest share one threshold lets through with at most 5% wrong.
- **Run:** `.venv/bin/python bench/run.py --model qwen3.5-4b --task massive_scenario --sample 100`, then `bench/report.py` ([docs/setup.md](https://github.com/4nt0ineB/typed-decision-bench/blob/main/docs/setup.md)).

| Model | 60 intents `EN_EN` | `FR_EN` | `FR_FR` | At 0.90: passes / right | Automatable | Routing (addressee removed) |
|---|---:|---:|---:|---|---:|---:|
| Jev 1.13.0 | 85% | 83% | 84% | 73% / 94% | 70% | 66.4% |
| Kev-27B | 84% | 80% | 81% | 42% / 98% | 69% | 66.0% |
| GPT-4o mini | 81% | 74% | 75% | 90% / 82% | 5% | 56.4% |
| Qwen3.5 9B | 80% | 71% | 74% | 18% / 98% | 44% | 48.8% |
| Qwen3.5 4B | 80% | 70% | 74% | 31% / 96% | 38% | — |
| Kev-9B | 76% | 73% | 74% | 15% / 99% | 40% | 61.8% |
| Open-Jev 9B | 74% | 71% | 68% | 12% / 96% | 25% | not run |
| Open-Jev 2B | 69% | 65% | 64% | 0% / — | 19% | — |
| Laya router | 45% | 31% | 31% | 59% / 46% | 0% | — |
| Laya multilingual | 42% | 36% | 35% | 26% / 69% | 0% | not run |

Source: [README](https://github.com/4nt0ineB/typed-decision-bench#readme) and [docs/massive-bench.md](https://github.com/4nt0ineB/typed-decision-bench/blob/main/docs/massive-bench.md), read 2026-09-30. Mistral Nemo, MiniCPM5 2B, Qwen3.5 2B and 0.8B score 53% or less on `EN_EN` (same doc). A fine-tuned XLM-R reference scores 89 / 81 / 81. Jev ECE: 0.07 EN, 0.06 FR (massive-bench.md). Kev-9B routing: [docs/written-questions-bench.md](https://github.com/4nt0ineB/typed-decision-bench/blob/main/docs/written-questions-bench.md). Jev $0.08–0.10 per 1,000 calls; median 269 ms per short command from France.

## Decision Index

Space [`multimodalart/jev-decision-index`](https://huggingface.co/spaces/multimodalart/jev-decision-index) (`data/index.json` generated 2026-09-28T00:39Z, read 2026-09-30); kit [`apolinario/decision-index`](https://github.com/apolinario/decision-index) (MIT).

- **Scope:** open reproductions of Jev on a frozen suite, plus Jev via its API. 0.2.1 has 120,340 requests (119,898 scoreable), 43 benchmarks on the board, 38 in the index.
- **Hardware:** open models on one RTX PRO 6000 (96 GB); latency is CUDA-synchronized request time without HTTP. Jev runs over HTTPS.
- **Scoring:** each benchmark `(score − chance)/(1 − chance)`, clipped to 0–1, times coverage. Areas: Knowledge 25.8%, Language 25.8%, Retrieval 20.0%, Tools 18.3%, Arts 10%; gold ★ benchmarks ×1.2 inside an area.
- **Calibration:** ECE and Brier over 32 benchmarks on a 1-in-6 request sample; not part of the score.
- **Rules:** native prompts and readout per engine; no prompt tuning, option pruning, retraining or correctness-based retry.

| Edition | Generated | Requests | Index benchmarks | Jev, balanced skill | Top open entrant, balanced skill |
|---|---|---:|---:|---:|---|
| 0.1 | 2026-09-22 | 132,422 | 19 | 46.26 | Jevfire 40.86 |
| 0.2 | 2026-09-27 | 121,057 | 40 | 51.67 | Decider chat · Gemma-4-31B 51.93 |
| 0.2.1 | 2026-09-28 | 120,340 | 38 (reweighted areas) | 57.91 | Surogate Rune 26B-A4B v3 57.44 |

Balanced raw accuracy in 0.1: Jev 59.51, Jevfire 55.74. Source: `data/index-v0.1.json`, `index-v2.json`, `index-v0.2.1.json`.

**Leaderboard, 0.2.1 top 10** (all 71 rows: [benchmarks-leaderboards.md](benchmarks-leaderboards.md#decision-index-021)):

| # | Entrant | Base | Score | ECE | Median ms |
|---:|---|---|---:|---:|---:|
| 1 | Jev 1.13.0 | closed | 57.91 | 0.074 | 524.1 |
| 2 | Surogate Rune 26B-A4B v3 | gemma-4-26B-A4B-it | 57.44 | 0.120 | 120.5 |
| 3 | Decider chat · Gemma-4-31B | gemma-4-31B | 57.33 | 0.047 | 108.5 |
| 4 | AutoJev-27B | Qwen3.8-27B | 56.40 | 0.018 | 101.4 |
| 5 | simple-jev · Qwen3.8-27B | Qwen3.8-27B | 55.74 | 0.113 | 373.0 |
| 6 | Jebadiah 27B | Qwen3.8-27B | 54.67 | 0.014 | 110.4 |
| 7 | Eikos-27B (FP8) | Qwen3.8-27B | 53.13 | 0.057 | 129.7 |
| 8 | reflex 27B (FP8, wide choice) | Qwen3.8-27B | 52.16 | 0.024 | 108.3 |
| 9 | Decider chat · Qwen3.6-27B | Qwen3.6-27B | 51.35 | 0.021 | 83.6 |
| 10 | Winnow-12B (Q8_0) | gemma-4-12B | 50.02 | 0.168 | 72.5 |

Jev has the top score among the 71 board rows. Liquid reports d1 at 58.9 against Jev 57.9 on 0.2.1 from its own run of the suite; d1 has no board row ([vendor-reported results](benchmarks-leaderboards.md#vendor-reported-results-on-the-same-suite)). Other self-reported 0.2.1 scores, not on the board: Darwin-27B-JEV 61.17 ([PR #15](https://github.com/apolinario/decision-index/pull/15)); `autotrust/JEV-Gemma4-26B-A4B` 58.05 (card); Eikos-27B author rerun 55.46 (AaJ).

## S1Bench

- 13 subsets, 3,880 items, pinned by [`bespokelabsai/nimble`](https://github.com/bespokelabsai/nimble) manifests: vitaminc-dev, massive-en-US, massive-de-DE, boolq, squad2, paws, multinli, civil_comments, aegis2, helpsteer2, summeval-relevance, summeval-consistency, pubmedqa.
- Macro accuracy: Jev 0.761, `interfaze-ai/lev` 0.689 ([lev card](https://huggingface.co/interfaze-ai/lev), 2026-09-25); macro / micro: Jev 0.760 / 0.773, Nimble-9B 0.748 / 0.759, decider-2b v11 0.706 / 0.711 ([decider-2b card](https://huggingface.co/Mapika/decider-2b), 2026-09-24); decider-4b v2.1 0.756, decider-35b-a3b 0.774 (same card, macro).
- Majority-class baselines beat lev and Jev on civil_comments and the three 5-level rating subsets (lev card).

## Fastino fast-decisions

- [`fastino/fast-decisions`](https://huggingface.co/datasets/fastino/fast-decisions) (Apache-2.0): 17 domains; public dev split 1,700 rows; held-out test 5,100 rows, unreleased. Exact-match accuracy.
- Held-out averages (dataset card and [GLiNER2.5-Decide card](https://huggingface.co/fastino/GLiNER2.5-Decide)): GLiNER2.5-Decide (340M) 60.2%; GLiNER2.5-Decide-1B 59.6% (the dataset card labels this row "GLiNER2 XL (1B)"); JevK5 57.6%; GLiNER2.5-multi-Decide (287M) 56.7%; SemIf (Qwen3.5-4B) 56.4%; GLiFormer large-v1 49.0%; Laya Router 46.6%.
- Jev is not in the table. The suite's author also makes the top model.

## Other evaluations

| Evaluation | Measures | Reported numbers | Source |
|---|---|---|---|
| decision-models-under-pressure | 1,000 items; accuracy as options grow 2→256; option-order sensitivity | 128 options: Jev 60%, gliclass 41%, Laya 39%; order sensitivity Jev 14.6%, Laya 49.4% | [gazelle93](https://github.com/gazelle93/decision-models-under-pressure) |
| typed-decisions (LocalLLaMA) | 400 test cases, 2,000 decisions, four workflows, teacher labels (teacher self-agreement 0.735) | Card board, 2026-09-30: meraGPT Decider 1 0.768; Liquid d1 0.742 (measured 2026-09-30 via Liquid's API); Jev 0.727. Laya card: laya-typed-decisions 0.766; ce-1024 0.7885 (AaJ) | [dataset card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions); Laya card |
| Typed Decision Leaderboard | AUC | Jev 0.7350; ZTC 27B 0.7289; open-jev 4B 0.6101; Laya 421M 0.5144 (AaJ) | [mayafree Space](https://huggingface.co/spaces/mayafree/typed-decision-leaderboard) |
| Open JevBench, model-agnostic | Choice/Score/Noul across LLMs and encoders | gpt-oss-20b 88.4; Open-Jev-9B 82.3; NeoHorse-Jev-4B 77.6 (AaJ) | [model-collapse/jev-bench](https://github.com/model-collapse/jev-bench) |
| decisionbench | Banking77, 154 messages | Jev 79.9% at $0.07/1k, p50 0.26 s; Claude Opus 5.5 83.8% at $13.68/1k (AaJ) | [stas4000/decisionbench](https://github.com/stas4000/decisionbench) |
| jev_vs_oss (LlamaIndex) | 5 PDF tasks via liteparse, 32–96 decisions each; accuracy, latency, cost | Jev / Qwen3.5-4B (SemIf-style) / Laya / jeff: language 100 / 100 / 40 / 48%; orientation 94 / 91 / 28 / 22%; RVL-CDIP 16-class 54 / 51 / 24 / 26%; split 96 / 88 / 71 / 73%; triage 85 / 96 / 52 / 65%. lingua 100%, tesseract OSD 100%, heuristic triage 94% | [run-llama/jev_vs_oss](https://github.com/run-llama/jev_vs_oss); [experiment 03](../experiments/03-jev-vs-open-document-tasks/) |

## Reading the leaderboards across models

One row per model on at least two benchmarks. Scores are not comparable across columns: each benchmark has its own items, metric and scale. DI = Decision Index 0.2.1 balanced skill; JB = JevBench v1.5.4 score; kyr0 = macro soft accuracy; 4nt = 60 intents `EN_EN`; Fast = fast-decisions held-out; S1 = S1Bench macro. Params are served parameters from DI `index.json` where listed.

| Model | Params | Backbone | Class | DI | JB | kyr0 | 4nt | Fast | S1 |
|---|---|---|---|---:|---:|---:|---:|---:|---:|
| Jev 1.13.0 | undisclosed | closed | hosted API | 57.91 | 72.1 | 88.1 | 85 | — | 0.76 |
| Liquid d1 ³ | undisclosed | closed | hosted API | 58.9 (vendor run) | — | — | — | — | — |
| Surogate Rune 26B-A4B v3 | 25.8B | Gemma 4 26B-A4B | large | 57.44 | 66.5 | — | — | — | — |
| AutoJev-27B | 27.8B | Qwen3.8-27B | large | 56.40 | 19.5 | — | — | — | — |
| Eikos-27B | 27.8B | Qwen3.8-27B | large | 53.13 | 18.5 | — | — | — | — |
| reflex 27B ¹ | 27.8B | Qwen3.8-27B | large | 52.16 | 13.2 | — | — | — | — |
| decider-35b-a3b | 36.0B | Qwen3.5-35B-A3B | large | 47.11 | 27.5 | — | — | — | 0.774 |
| djev | 25.8B | DiffusionGemma 26B-A4B | large | 40.28 | 64.2 | — | — | — | — |
| Bonsai 2 27B ² | ~27B | Qwen3.8-27B ternary (PrismML) | large | — | 15.8 | 76.5 | — | — | — |
| Winnow-12B Q8 | 12.0B | Gemma 4 12B | mid | 50.02 | 73.2 | — | — | — | — |
| Jev-Omni | 12.0B | Gemma 4 12B | mid | 40.53 | 71.5 | — | — | — | — |
| Bespoke Nimble 9B ¹ | 9.7B | Qwen3.5-9B | mid | 39.57 | 31.8 | — | — | — | 0.748 |
| Kev-9B | 9.7B | Qwen3.5-9B | mid | 38.48 | — | — | 76 | — | — |
| Open-Jev 9B (Zefan Cai) | ~9.7B | Qwen3.5-9B | mid | — | 24.4 | — | 74 | — | — |
| CLM-8B ¹ | 8.2B | Qwen3-8B | mid | 7.40 | 1.5 | — | — | — | — |
| Hopper ¹ | 4.7B | Qwen3.5-4B | small | 40.77 | 67.5 | — | — | — | — |
| decider-4b ¹ | 4.7B | Qwen3.5-4B | small | 40.70 | 71.3 | — | — | — | 0.756 |
| JevK5 ¹ | 4.7B | Qwen3.5-4B | small | 38.81 | 58.1 | — | — | 57.6 | — |
| lev (interfaze) | 4.7B | Qwen3.5-4B | small | 38.54 | — | — | — | — | 0.689 |
| Kev-4B | 4.7B | Qwen3.5-4B | small | 34.64 | 38.1 | — | — | — | — |
| metask-jev-4b | 4.7B | Qwen3.5-4B | small | 26.89 | 67.5 | — | — | — | — |
| SemIf (OpenJev Qwen3.5-4B) ² | 4.7B | Qwen3.5-4B | small | 25.94 | 68.7 | 74.1 | — | 56.4 | — |
| decider-2b | 2.3B | Qwen3.5-2B | small | 28.97 | 45.1 | — | — | — | 0.706 |
| Open-Jev 2B (Zefan Cai) | ~2.3B | Qwen3.5-2B | small | — | 9.1 | — | 69 | — | — |
| Bosun v3.1 0.6B | 0.6B | Qwen3-0.6B | small | 14.32 | 2.5 | — | — | — | — |
| jeff | 576M | GLiFormer-large | tiny encoder (576M) | 8.04 | 0.1 | — | — | — | — |
| GLiNER2.5-Decide | 486M (card: 340M) | GLiNER2 large | tiny encoder | 11.21 | — | — | — | 60.2 | — |
| Laya | 421M | ModernBERT-large | tiny encoder | 6.04 | 0.0 | 46.7 | — | — | — |
| Von ¹ | 395M | not stated | tiny encoder | — | 0.0 | 48.6 | — | — | — |
| Laya multilingual | ~307M | mmBERT-base | tiny encoder | — | 0.0 | — | 42 | — | — |
| Laya router | n/s | not stated | tiny encoder | — | — | — | 45 | 46.6 | — |
| GLiNER2.5 multi | 287M | GLiNER2 | tiny encoder | 4.26 | 2.7 | — | — | — | — |
| openJev Verdict | 151M | ModernBERT-base | tiny encoder | 1.87 | 0.0 | — | — | — | — |

¹ Versions differ between boards: DI reflex is "FP8, wide choice"; DI Nimble is v2; CLM is v0.1 on DI and `clm-latest` on JB; DI Hopper is (G) 1.2; DI Decider 4B vs JB decider-4b v2 vs S1 v2.1; DI JevK5 vs JB JevK5 v0.2.0 (JB v0.3 scores 71.9); JB Von vs kyr0 Von 1.1.
² Same weights, different runtimes (unverified match): JB "Bev / Bonsai 27B" vs kyr0 Bonsai-Llama-Jev; JB SemIf vs kyr0 `openjev-qwen3.5-4b` (fastjev).
³ d1 has no row on any board in this table. The DI figure is Liquid's own run of the 0.2.1 suite ([KuCoin](https://www.kucoin.com/news/flash/liquid-ai-s-d1-decision-model-surpasses-jev-in-hugging-face-evaluation)); Jev scores 57.9 in that run. On the LocalLLaMA typed-decisions card d1 scores 0.742 against Jev 0.727.

Observations (sources as in the sections above):

- **No independent board ranks d1 against Jev on the Decision Index.** Jev's 57.91 is the top board row; Liquid's own run puts d1 at 58.9 and Jev at 57.9. On LocalLLaMA typed-decisions, whose card lists meraGPT Decider 1 first (meraGPT's submission says its team built the benchmark), d1 scores 0.742 and Jev 0.727.
- **Accuracy rises with size on accuracy-only boards.** On DI 0.2.1, the twelve best open entrants are all 12B or larger; the best 4B (JPT-4B) scores 43.04, the best sub-1B decoder (JPT-0.8B) 19.22, and every encoder and GLiNER model scores below 12. kyr0 orders the same way: Jev 88.1, 27B 76.5, 4B 71.0–74.1, ~400M encoders 46.7–48.6.
- **JevBench's composite reverses that order for 27B models.** AutoJev-27B and Eikos-27B reach JB Intelligence 72.8 and 75.1 (Jev 72.0) but score 19.5 and 18.5: their estimated $0.23–0.24 per 1,000 decisions puts the Cost axis at 29.4 and 28.7, under the 50 gate. AutoJev-27B is 4th on DI (Jev included) and 52nd on JB. 4B rebuilds hold 10 of JB's top 15 places, with Intelligence 49.9–62.1 and Cost 57.7–64.5.
- **Calibration does not track size.** DI's five lowest ECEs are Jebadiah 27B 0.014, Xor 35B-A3B 0.015, AutoJev-27B 0.018, Decider chat · Qwen3.6-27B 0.021 and Decider 35B-A3B 0.023; Intern-Decision-0.8B has 0.025, JevK5 4B 0.027 and Winnow-12B 0.168. Three of DI's four highest are under 500M: LFM2.5-350M-RLCD 0.568, Julia-1 (mmBERT-small) 0.420, GLiNER 2.5 base 0.367; the fourth is openvons Qwen3-4B, 0.371. On kyr0: Von 1.1 0.372, Laya 0.278.
- **Confidence thresholds differ in meaning per model.** On 4nt0ineB's 60 intents, answers at ≥0.90 are right 94% of the time for Jev, 98% for Kev-27B, 82% for GPT-4o mini and 69% for Laya multilingual. kyr0's temperature fit moved Bonsai 27B's ECE from 0.134 to 0.130.
- **Latency follows the runtime more than the parameter count.** On one H200, kyr0 measured 36.7–38.5 ms p50 for encoders, 171 ms for a Q2 27B on llama.cpp, and 1,057–1,066 ms for two BF16 4B models. On DI's RTX PRO 6000, Decider 2B runs at 8.1 ms, six of the eight 27B entrants at 84–130 ms, and Jev at 524 ms over HTTPS.
- **Tiny models fall down on general decisions and win narrow ones.** Every encoder, classifier or reranker under 600M has JB Intelligence ≤22.5 and a JB score ≤8.4 (best: GLiNER2 large). Laya reads at most about 770 tokens (4nt0ineB) and scores 42% on English intents. GLiNER2.5-Decide tops Fastino's own 17-domain suite at 60.2% and scores 11.21 on DI.
- **Public sets get overfit.** Gavel-Decide 4B scored 79.34% on the 213 public items it trained on and 3 of 18 on items it never saw (AaJ). In JevBench v1.4.2.2, Imajev-4B scored 86.1% public and 37.0% sealed (gap 49.1 pp). v1.5 penalizes a chance-corrected gap more than 8 points above the field median; v1.5.4's largest gaps are kev 0.6B 27.0, openJev Verdict 26.7 and kev 0.5B 25.7.
- **General LLMs top Intelligence and lose the composite.** GPT-6 Luna scores JB Intelligence 95.3–96.2 and a JB score of 38.8–40.5 at $0.11 per 1,000 decisions and ~1.6 s p50.

## Self-reported results

One row per model documented in [models/](models/). "Claim" is the vendor's or author's own number, taken from the model doc's Benchmarks section and checked against the cited card or launch post on 2026-09-30. "Own" = a suite the claimant built; "public" = a suite someone else built. Gap = claim minus independent result, only where both use the same benchmark and metric. Exp. 03 = LlamaIndex's [jev_vs_oss](../experiments/03-jev-vs-open-document-tasks/) run (five PDF tasks, 32–96 decisions each).

| Model | Claim | Run by | Benchmark source | Independent result | Gap |
|---|---|---|---|---|---|
| Jev 1.13.0 ([doc](models/jev.md)) | 193.6× faster, 444.6× cheaper than LLMs on TypeSafe workflow evals | vendor | own (labels = mean of GPT-6 Astra and Claude Fable 5.1) | DI 57.91 (top board row); JB 72.1 (#3); exp. 03: 54.2–100% on five tasks, Qwen3.5-4B 51.0–100% | — |
| Liquid d1 ([doc](models/liquid-d1.md)) | DI 0.2.1 58.9 vs Jev 57.9 | vendor | public (DI) | no DI row; typed-decisions card 0.742 vs Jev 0.727 | — |
| meraGPT Decider 1 ([doc](models/decider-1.md)) | typed-decisions 0.768 vs Jev 0.727 | vendor | typed-decisions; meraGPT's submission says its team built it, the card calls it independent | none | — |
| OpenAI Decisions API ([doc](models/openai-decisions-api.md)) | ~150 ms per decision vs 1.6 s for GPT-6 Luna | vendor | no benchmark named | Every: ~230 ms, 76/78 vs Jev 73/78 (computer-use steps) | −80 ms |
| Upstage Solar Decide ([doc](models/solar-decide.md)) | none published | — | — | zero-shot-ie-bench 95.8% vs Jev 93.8% (48 questions) | — |
| Respan Span-01 ([doc](models/span-01.md)) | behavior F1 84.3 vs Jev 71.5; production F1 0.806 vs Jev 0.716 | vendor | own | zero-shot-ie-bench 85.4% vs Jev 93.8% | — |
| Together Tev1-4B ([doc](models/tev1.md)) | 880/1,000 (88.0%) on Together's development set, "not an independent benchmark" | vendor | own | DI 29.24 at 69% coverage | — |
| GLiNER2.5-Decide ([doc](models/gliner-decide.md)) | fast-decisions 60.2% vs JevK5 57.6% | vendor | own (Fastino) | DI 11.21 | — |
| Bonsai-Llama-Jev ([doc](models/bonsai-llama-jev.md)) | kyr0 soft accuracy 76.46% vs Jev 88.08% | author | own (kyr0) | JB "Bev / Bonsai 27B" 15.8 (unverified match) | — |
| Kev ([doc](models/kev.md)) | Kev-4B transfer-v4 0.817 dev / 0.838 test; Kev-9B 0.822 / 0.852 | author | own | local-jev-bench Kev-4B 81.4% (534/656); DI Kev-4B 34.64, Kev-9B 38.48 | +0.3 pp (Kev-4B dev) |
| CLM-8B ([doc](models/clm-8b.md)) | BFCL v4 95.2% vs Jev 99.2%, "on par with Jev" | vendor | public (BFCL) | local-jev-bench BANKING77-20 20%; DI 7.40; JB 1.5 | — |
| AnyJev ([doc](models/anyjev.md)) | Qwen3-8B BANKING77-20: L0 0.803, raw 0.747 | vendor | public (BANKING77) | local-jev-bench 241/300 (80.3%), raw 224/300 (74.7%) | 0.0 pp |
| Laya ([doc](models/open-reproductions.md#laya)) | typed-decisions 0.766 (`laya-typed-decisions`) vs Jev 0.727 | author | public (typed-decisions) | DI 6.04; kyr0 46.70%; JB 0.0; exp. 03 (`typed-decisions` checkpoint): 24.0–70.7% vs Jev 54.2–100% | — |
| open-jev-deberta-v3-large | in-domain 0.854, OOD 0.690 | author | own | JB 0.0 (Intelligence 0.0) | — |
| Julia-1 | Choice 71.33%, Noul 80.67%, Score 68.88% | author | own | DI 5.54 | — |
| JevK5 | JevBench v1.4 #2 of 76, 62.04 vs Jev 63.29 | author | public (JB) | JB v1.4.2.2 v0.2.0 62.04 (#5); JB v1.5.4 v0.3 71.9 (#4); DI 38.81; fast-decisions 57.6% | 0.00 |
| Jev-Style-2B v3 | JevBench v1.4.1 public items 73.6% vs Jev 86.6% (self-run) | author | public (JB items) | not on JB or DI | — |
| decider | decider-4b v2.1 Bespoke suite 0.756; decider-2b v11 0.706; decider-2b regression set 0.802 / 0.752 | author | public (S1Bench); own (regression set) | JB decider-4b v2 71.3 (#7); DI Decider 4B 40.70, 2B 28.97 | — |
| Tiny-Jev | none | — | — | none | — |
| OpenThai-SystemOne | S1Bench macro 74.3 vs Nimble-9B 74.8, Jev 76.0 | author | public (S1Bench) | not on DI | — |
| AgentJev-0.6B | coding completion 57.8%, AUROC 0.589 | author | own | none | — |
| autotrust JEV-27B / JEV-Gemma4 | JEV-27B six-benchmark mean 84.07 vs Jev 83.85; JEV-Gemma4 DI 0.2.1 58.05 vs Jev 57.91 | author | mixed; public (DI) | not on DI | — |
| AutoJev-27B | own test set 84.60% vs Jev 82.79% | author | own | DI 56.40 (#4, Jev included); JB 19.5 (Intelligence 72.8) | — |
| Winnow-12B | JevBench public subset 198/231, "matches Jev" | author | public (JB items) | JB Q8 73.2 (#2); DI 50.02 | — |
| VTX-JEV-1 | 73.10% on 3,000 held-out cases (LF4) | author | own | none | — |
| lev | S1Bench macro 0.689 vs Jev 0.761 | author | public (S1Bench) | DI 38.54 | — |
| NeoHorse-Jev-4B | six-group mean 77.70 | author | mixed (author's runs) | DI 36.75 | — |
| Eikos-27B | DI 0.2.1 rerun 55.46 (AaJ) | author | public (DI) | DI 53.13 | +2.33 |
| OpenJev 27B (`openjev/openjev`) | 84.0% vs Jev 85.4% on a 10,000-question set (AaJ) | author | own | none | — |

Sources: model docs linked above; cards on huggingface.co for each named repo; [KuCoin](https://www.kucoin.com/news/flash/liquid-ai-s-d1-decision-model-surpasses-jev-in-hugging-face-evaluation) (d1); [typed-decisions card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions); [local-jev-bench](https://github.com/tak-bro/local-jev-bench); boards as in the sections above. All read 2026-09-30.

- **Own suites put the claimant first.** Decider 1, GLiNER2.5-Decide, Span-01 and AutoJev-27B each put their model above Jev (or JevK5) on a suite they built. Bonsai is the exception: 76.46% against Jev's 88.08% on its author's bench.
- **Where the same benchmark was re-run, the gaps are small.** AnyJev reproduced exactly on BANKING77-20 (241/300); Kev-4B's transfer-v4 dev claim is 0.3 pp above the local re-run; JevK5's 62.04 matches the JevBench board; Eikos-27B's rerun is 2.33 points above its DI board row.
- **Own-suite leaders rank low on public boards.** GLiNER2.5-Decide (60.2% on its own suite) scores 11.21 on DI; Tev1-4B (88.0% on its development set) 29.24; AutoJev-27B (84.60% vs Jev 82.79%) is 4th on DI and 52nd on JevBench.
- **Third-party runs against Jev split both ways.** Span-01 trails Jev on zero-shot-ie-bench (85.4% vs 93.8%) after leading it on Respan's suites; Solar Decide leads Jev there (95.8% vs 93.8%); in exp. 03, Jev leads Laya and jeff on all five tasks and ties or leads Qwen3.5-4B on four (Qwen leads triage, 95.8% vs 85.4%).

## Caveats

- **Self-reported results.** kyr0 and 4nt0ineB run every model themselves; three of kyr0's seven runs are the author's own models. Fastino authored its suite and tops it. S1Bench and many AaJ numbers come from model cards. JevBench and DI run submissions on evaluator hardware, but most JevBench costs are estimates.
- **Public-set contamination.** JevBench publishes 601 of 904 open items (v1.5) and published 231 in v1.4; submitters can train on them. MASSIVE has been public since 2022. DI rebuilds public benchmarks. kyr0's cases are public on GitHub.
- **Different metrics.** DI is chance-corrected skill; JevBench a harmonic mean of four axes; kyr0 soft accuracy (Jev: 88.1% soft vs 93.4% hard); 4nt0ineB, Fastino and S1Bench hard accuracy. A 0 on JevBench means an axis fell below a gate, not zero correct answers.
- **Hardware and network in latency.** kyr0: one H200 NVL. DI: one RTX PRO 6000, no HTTP. JevBench: serial requests from Germany, ×2 + 0.15 s for self-hosted and demo endpoints. 4nt0ineB: hosted calls from France, open models in-process on H100, A100 or an M3 laptop. Jev latency always includes the network.
- **Versions and runtimes.** The same name can mean a different checkpoint, quantization or server on each board (footnotes above).

## Sources

- JevBench: [repo](https://github.com/fstandhartinger/jevbench) README, CHANGELOG, `docs/METHOD-v1.5*.md`, `results/v1.4.2.2/jevbench-v1.4.2.2-results.json`; [board](https://benchmarkheaven.com/jev-models) and [v1.5.4 JSON](https://benchmarkheaven.com/api/jevbench/v1.5.4). Read 2026-09-30.
- kyr0: [repo](https://github.com/kyr0/typed-decision-bench) README, `models.json`; [results page](https://kyr0.github.io/typed-decision-bench/), `model_summary.csv`, `summary.json`; [paper](https://kyr0.github.io/typed-decision-bench/paper/). Read 2026-09-30.
- 4nt0ineB: [repo](https://github.com/4nt0ineB/typed-decision-bench) README, `docs/massive-bench.md`, `docs/setup.md`. Read 2026-09-30.
- Decision Index: [Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) `data/index.json`, `index-v2.json`, `index-v0.1.json`, `methodology.json`. Read 2026-09-30.
- Liquid d1: [KuCoin](https://www.kucoin.com/news/flash/liquid-ai-s-d1-decision-model-surpasses-jev-in-hugging-face-evaluation) (Liquid's own DI run), [Liquid launch thread](https://threadreaderapp.com/thread/2105003472332693869.html); no d1 entry found on JevBench, kyr0, 4nt0ineB, the DI Space or the seawolf2357/decision-index fork, or Artificial Analysis. Read 2026-09-30.
- Model and dataset cards: `LocalLLaMA/typed-decisions`, `fastino/fast-decisions`, `fastino/GLiNER2.5-Decide`, `interfaze-ai/lev`, `Mapika/decider-2b`, `TokenRhythm/NeoHorse-Jev-4B`, `convaiinnovations/laya`, `autotrust/JEV-Gemma4-26B-A4B`.
- Han Xiao, [All about Jev](https://hanxiao.io/all-about-jev/) dataset, local copy 2026-09-30, `category == "benchmark"` (215 entries) and `"model"` entries; not independently verified. More benchmarks: [landscape.md](landscape.md).

# Full leaderboards

Companion to [benchmarks.md](benchmarks.md). Generated 2026-09-30 from the published result files; no row was re-run.

## JevBench v1.5.4 (headline A)

Source: [`benchmarkheaven.com/api/jevbench/v1.5.4`](https://benchmarkheaven.com/api/jevbench/v1.5.4), read 2026-09-30. 106 ranked of 109 listed systems.

- Score: equal-weight harmonic mean of the four 0–100 axes, with gates (see [benchmarks.md](benchmarks.md#jevbench)).
- Size: parsed from the system name or its base model; n/s = not stated.
- $/1k decisions: "est." = the base model's hosted list price times measured tokens, not a bill.
- p50: raw serial latency before JevBench's ×2 + 0.15 s adjustment for self-hosted and demo endpoints.
- Run: where JevBench ran it. Local = evaluator-owned GPU or CPU; hosted = vendor or author endpoint.

| # | System | Size | Score | Intel. | Calib. | Speed | Cost | $/1k decisions | p50 s (raw) | Run |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Cygnet (blockbrain, frozen Gemma-4-12B-it) | 12B | 73.7 | 71.1 | 87.0 | 91.0 | 56.4 | 0.0283 est. | 0.040 | local GPU |
| 2 | Winnow-12B Q8 | 12B | 73.2 | 74.4 | 84.1 | 86.1 | 56.6 | 0.0281 est. | 0.095 | local GPU |
| 3 | Jev 1.13.0 (TypeSafe AI) | undisclosed | 72.1 | 72.0 | 88.0 | 83.8 | 54.7 | 0.0323 est. | 0.616 | hosted API |
| 4 | JevK5 v0.3 (4B) | 4B | 71.9 | 56.3 | 88.3 | 93.6 | 63.1 | 0.0170 est. | 0.016 | local GPU |
| 5 | Plumb-4B (crh225, JevK5 v0.2 + LoRA) | 4B | 71.6 | 55.8 | 87.4 | 93.5 | 63.1 | 0.0170 est. | 0.017 | local GPU |
| 6 | Jev-Omni (akhilaaa3, Gemma-4-12B merged) | 12B | 71.5 | 70.5 | 82.6 | 84.7 | 56.1 | 0.0292 est. | 0.113 | local GPU |
| 7 | decider-4b v2 (Mapika) | 4B | 71.3 | 55.8 | 85.6 | 90.9 | 64.5 | 0.0152 est. | 0.026 | local GPU |
| 8 | Decision 4B v1.2 (FlyMyJev, Qwen3.5-4B + LoRA) | 4B | 70.8 | 53.7 | 88.6 | 93.5 | 63.1 | 0.0170 est. | 0.016 | local GPU |
| 9 | Imajev-4B (RTX 5090) | 4B | 70.4 | 53.5 | 88.1 | 91.1 | 63.3 | 0.0168 est. | 0.042 | local GPU |
| 10 | Decision 4B v1.1 (FlyMyJev, Qwen3.5-4B + LoRA) | 4B | 70.4 | 53.1 | 87.3 | 93.5 | 63.1 | 0.0170 est. | 0.016 | local GPU |
| 11 | Manchego v2.1 | n/s | 68.8 | 51.2 | 84.9 | 88.6 | 64.3 | 0.0155 est. | 0.084 | local GPU |
| 12 | SemIf, formerly OpenJev (Qwen3.5-4B, TheoLeeCJ) | 4B | 68.7 | 51.3 | 84.0 | 90.9 | 63.1 | 0.0170 est. | 0.039 | local GPU |
| 13 | spark-s1-4b-v6 (Open Spark Jev, abhishek085) | 4B | 68.2 | 62.1 | 69.7 | 85.5 | 60.4 | 0.0209 est. | 0.128 | local GPU |
| 14 | metask-jev-4b | 4B | 67.5 | 53.5 | 82.7 | 89.5 | 57.7 | 0.0256 est. | 0.068 | local GPU |
| 15 | Hopper | 4B | 67.5 | 49.9 | 87.9 | 87.2 | 62.3 | 0.0181 est. | 0.122 | local GPU |
| 16 | Malkuth-4B (newfull5, Kev post-train) | 4B | 66.8 | 54.5 | 83.2 | 86.2 | 55.8 | 0.0297 est. | 0.146 | local GPU |
| 17 | Surogate Rune 26B-A4B v3 (RTX PRO 6000) | 26B-A4B | 66.5 | 69.7 | 88.3 | 86.0 | 49.0 | 0.0502 est. | 0.100 | local GPU |
| 18 | reflex 4B (kshetrajna12) | 4B | 65.2 | 51.5 | 86.8 | 68.8 | 63.1 | 0.0169 est. | 1.358 | local GPU |
| 19 | jev-local (Qwen3.5-9B) | 9B | 65.2 | 56.3 | 77.8 | 73.0 | 58.9 | 0.0235 est. | 0.397 | local GPU |
| 20 | djev (Maisa, diffusion-gemma) | 26B-A4B | 64.2 | 72.3 | 80.4 | 91.0 | 48.2 | 0.0532 est. | 0.050 | local GPU |
| 21 | Raw Qwen3 4B Instruct 2507 direct logits | 4B | 62.1 | 54.1 | 52.9 | 89.2 | 63.4 | 0.0166 est. | 0.056 | local GPU |
| 22 | jqv (Qwen3-32B zero-shot) | 32B | 60.8 | 49.1 | 86.8 | 83.4 | 51.2 | 0.0424 est. | 0.078 | local GPU |
| 23 | JevK5 v0.2.0 | 4B | 58.1 | 46.7 | 84.9 | 90.9 | 63.1 | 0.0170 est. | 0.033 | local GPU |
| 24 | Qwen3.5-9B Jev-like data-mix v2 | 9B | 53.0 | 60.4 | 80.9 | 82.0 | 45.7 | 0.0646 est. | 0.215 | local GPU |
| 25 | Standard One 8B (Standard Thinking) | 8B | 47.8 | 59.6 | 83.2 | 92.5 | 43.3 | 0.0777 est. | 0.027 | local GPU |
| 26 | NInfer Qwen3.8-Flash-Next mixed | n/s | 47.5 | 67.2 | 88.5 | 88.6 | 42.5 | 0.0823 est. | 0.080 | local GPU |
| 27 | Instinct Dual 4B | 4B | 47.0 | 43.1 | 88.3 | 82.0 | 60.2 | 0.0212 est. | 0.253 | hosted (author endpoint) |
| 28 | swanOne (blockbrain, Qwen3.8-Flash-Next NVFP4) | n/s | 46.6 | 71.2 | 87.1 | 84.7 | 42.2 | 0.0848 est. | 0.209 | local GPU |
| 29 | Raw Qwen3 8B direct logits | 8B | 45.2 | 51.1 | 49.2 | 86.8 | 45.5 | 0.0654 est. | 0.091 | local GPU |
| 30 | decider-2b (Mapika) | 2B | 45.1 | 42.3 | 71.5 | 94.4 | 64.9 | 0.0148 est. | 0.014 | local GPU |
| 31 | system-one (Qwen3-8B, Sean Goedecke) | 8B | 44.1 | 50.5 | 49.4 | 90.9 | 45.0 | 0.0683 est. | 0.038 | local GPU |
| 32 | system-one-open (Gemma 4 E2B LoRA on an L4) | E2B | 42.4 | 41.6 | 71.6 | 78.3 | 68.3 | 0.0114 est. | 0.575 | hosted (author endpoint) |
| 33 | Autoloops – Gemma 4 31B IT | 31B | 40.5 | 76.7 | 85.8 | 83.9 | 39.6 | 0.1032 | 0.607 | hosted API |
| 34 | GPT-6 Luna (low reasoning effort) | undisclosed | 40.5 | 95.3 | 94.9 | 73.2 | 39.1 | 0.1075 est. | 1.580 | hosted API |
| 35 | GPT-6 Luna (default medium reasoning effort) | undisclosed | 38.8 | 96.2 | 95.6 | 73.2 | 38.3 | 0.1138 est. | 1.555 | hosted API |
| 36 | JevOne | n/s | 38.2 | 54.1 | 84.9 | 90.4 | 39.8 | 0.1012 est. | 0.058 | local GPU |
| 37 | kev 4B (research preview) | 4B | 38.1 | 39.9 | 67.6 | 85.5 | 65.8 | 0.0138 est. | 0.172 | local GPU |
| 38 | kev 8B (research preview) | 8B | 34.2 | 48.3 | 71.0 | 84.1 | 40.4 | 0.0968 est. | 0.181 | local GPU |
| 39 | open-alternative-jev (Qwen3.5-4B, IkerMoel) | 4B | 33.6 | 37.4 | 76.9 | 91.3 | 63.3 | 0.0168 est. | 0.036 | local GPU |
| 40 | Bespoke Nimble 9B (Bespoke Labs) | 9B | 31.8 | 63.7 | 77.2 | 83.0 | 36.8 | 0.1283 est. | 0.198 | local GPU |
| 41 | Malkuth-2B (newfull5, Kev post-train) | 2B | 29.9 | 35.5 | 75.2 | 91.8 | 65.6 | 0.0141 est. | 0.041 | local GPU |
| 42 | openjev-sglang (Qwen3.6-35B-A3B on SGLang) | 35B-A3B | 29.0 | 58.6 | 82.9 | 78.1 | 35.6 | 0.1398 est. | 0.598 | hosted (author endpoint) |
| 43 | decider-35b-a3b (Mapika) | 35B-A3B | 27.5 | 60.5 | 82.0 | 91.0 | 34.4 | 0.1539 est. | 0.045 | local GPU |
| 44 | local-jev Qwen3.5-4B | 4B | 25.8 | 33.7 | 82.4 | 83.7 | 59.3 | 0.0228 est. | 0.138 | local GPU |
| 45 | Nemotron Diffusion 8B (pst2154, optimized vLLM) | 8B | 25.7 | 33.8 | 76.2 | 93.7 | 55.5 | 0.0305 est. | 0.019 | local GPU |
| 46 | Open-Jev 9B (Zefan Cai) | 9B | 24.4 | 63.8 | 81.5 | 73.6 | 33.1 | 0.1704 est. | 0.563 | local GPU |
| 47 | Decision 2B (FlyMy.AI, v59) | 2B | 22.5 | 31.3 | 86.2 | 90.4 | 66.4 | 0.0132 est. | 0.075 | local GPU |
| 48 | GPT-5.6 Luna (low reasoning effort) | undisclosed | 22.4 | 94.3 | 94.7 | 74.1 | 30.7 | 0.2047 | 1.321 | hosted API |
| 49 | typecastlm (Mikhail Gribov, Qwen3.5-4B computed head) | 4B | 21.8 | 31.2 | 76.7 | 92.0 | 64.0 | 0.0159 est. | 0.038 | local GPU |
| 50 | JEV Qwen3.5-9B Base NVFP4 | 9B | 20.1 | 32.2 | 80.9 | 93.5 | 47.6 | 0.0558 est. | 0.020 | local GPU |
| 51 | Gemini 3.1 Flash-Lite | undisclosed | 19.6 | 77.6 | 74.7 | 80.1 | 29.8 | 0.2194 | 0.863 | hosted API |
| 52 | AutoJev-27B (denis-pplx, Qwen3.8-27B) | 27B | 19.5 | 72.8 | 87.7 | 87.6 | 29.4 | 0.2262 est. | 0.101 | local GPU |
| 53 | AutoJev-27B (RTX PRO 6000) | 27B | 19.5 | 72.8 | 86.7 | 87.1 | 29.4 | 0.2262 est. | 0.088 | local GPU |
| 54 | NInfer Qwen3.8-27B NVFP4 | 27B | 18.7 | 65.5 | 85.9 | 89.9 | 29.1 | 0.2305 est. | 0.049 | local GPU |
| 55 | Eikos-27B (caiovicentino1, Qwen3.8-27B) | 27B | 18.5 | 75.1 | 86.3 | 87.6 | 28.7 | 0.2382 est. | 0.102 | local GPU |
| 56 | NInfer Qwen3.8-27B NVFP4 (T=1.5) | 27B | 18.5 | 61.1 | 86.5 | 89.9 | 29.1 | 0.2305 est. | 0.049 | local GPU |
| 57 | Instinct (ZooWork, Qwen3.8-27B) | 27B | 18.3 | 62.7 | 85.0 | 81.7 | 29.2 | 0.2298 est. | 0.260 | hosted (author endpoint) |
| 58 | OpenJev (thinking, BF16) | 26B-A4B | 17.9 | 84.2 | 83.1 | 73.9 | 28.5 | 0.2415 est. | 0.706 | local GPU |
| 59 | djev (thinking) | 26B-A4B | 17.4 | 77.3 | 95.7 | 72.3 | 28.1 | 0.2487 est. | 0.666 | local GPU |
| 60 | LitJev (Qwen3.8-27B) | 27B | 16.3 | 58.3 | 84.5 | 68.2 | 28.4 | 0.2444 est. | 1.459 | local GPU |
| 61 | Bev / Bonsai 27B | 27B | 15.8 | 53.1 | 77.7 | 72.7 | 28.2 | 0.2468 est. | 1.020 | local GPU |
| 62 | Raw Phi-4 mini direct logits | 3.8B | 15.2 | 27.6 | 71.4 | 89.2 | 53.2 | 0.0363 est. | 0.065 | local GPU |
| 63 | OpenSourceJev (Qwen3.5-4B Q4_K_M, native llama.cpp) | 4B | 13.2 | 25.8 | 76.0 | 72.5 | 69.1 | 0.0107 est. | 0.620 | local GPU |
| 64 | reflex-27b (Qwen3.8-27B) | 27B | 13.2 | 62.8 | 85.9 | 69.2 | 25.8 | 0.2973 est. | 1.299 | local GPU |
| 65 | Open-Jev 2B (Zefan Cai) | 2B | 9.1 | 33.6 | 73.6 | 75.8 | 33.1 | 0.1704 est. | 0.429 | local GPU |
| 66 | GLiNER2 large (Fastino) | 486M | 8.4 | 22.5 | 42.4 | 64.8 | 77.6 | 0.0056 est. | 0.865 | local CPU |
| 67 | Qwen3-Reranker-4B | 4B | 7.1 | 21.0 | 76.3 | 79.6 | 48.4 | 0.0525 est. | 0.181 | local GPU |
| 68 | DeepSeek V4.1 Flash (thinking default) | undisclosed | 6.6 | 93.7 | 96.9 | 69.4 | 19.1 | 0.4976 est. | 1.776 | hosted API |
| 69 | SimpleJev (Qwen3.5-0.8B, CPU) | 0.8B | 4.0 | 16.7 | 46.7 | 59.1 | 70.3 | 0.0098 est. | 3.610 | local CPU |
| 70 | SimpleJev Qwen3.8-27B | 27B | 3.4 | 72.8 | 87.2 | 74.9 | 14.9 | 0.6868 est. | 0.840 | hosted (author endpoint) |
| 71 | decision-machine-1 (milliseconds.ai) | undisclosed | 3.2 | 14.8 | 81.2 | 92.8 | 56.3 | 0.0286 est. | 0.180 | hosted API |
| 72 | GLiNER2.5 multi (Fastino, 287M) | 287M | 2.7 | 14.0 | 58.0 | 66.6 | 86.6 | 0.0028 est. | 0.610 | local CPU |
| 73 | Bosun v3.1 0.6B | 0.6B | 2.5 | 13.6 | 65.2 | 61.8 | 77.5 | 0.0056 est. | 1.944 | local CPU |
| 74 | GLiNER2 (Fastino, gliner2.5-base) | 194M | 2.3 | 13.5 | 35.6 | 70.3 | 86.6 | 0.0028 est. | 0.424 | local CPU |
| 75 | Deem 0.8B v1 | 0.8B | 2.1 | 13.0 | 38.9 | 84.3 | 80.3 | 0.0045 est. | 0.176 | local GPU |
| 76 | JevAct (einptein, jev1-2b-v2) | 2B | 1.5 | 11.2 | 62.5 | 76.4 | 68.6 | 0.0112 est. | 0.401 | hosted (author endpoint) |
| 77 | CLM-8B (Contrastive-LM, clm-latest) | 8B | 1.5 | 11.4 | 48.5 | 93.3 | 50.5 | 0.0447 est. | 0.017 | local GPU |
| 78 | kev 0.6B (research preview) | 0.6B | 1.3 | 10.3 | 67.7 | 87.2 | 80.1 | 0.0046 est. | 0.136 | local GPU |
| 79 | Raw Qwen3 0.6B direct logits | 0.6B | 1.1 | 10.6 | 21.5 | 90.4 | 77.6 | 0.0056 est. | 0.063 | local GPU |
| 80 | GLiNER2.5 small (Fastino, 74M) | 74M | 0.9 | 9.2 | 55.9 | 77.4 | 86.6 | 0.0028 est. | 0.161 | local CPU |
| 81 | Raw Qwen3 1.7B direct logits | 1.7B | 0.9 | 9.7 | 21.6 | 90.2 | 68.5 | 0.0112 est. | 0.066 | local GPU |
| 82 | Mirror | n/s | 0.2 | 5.6 | 43.2 | 63.6 | 89.3 | 0.0023 est. | 2.214 | local CPU |
| 83 | ZeroEntropy zerank-2 | n/s | 0.1 | 4.8 | 81.7 | 80.3 | 48.4 | 0.0525 est. | 0.161 | local GPU |
| 84 | jeff (Logan Markewich, GLiFormer 400M) | 400M | 0.1 | 4.4 | 80.3 | 55.8 | 81.1 | 0.0043 est. | 3.494 | local CPU |
| 85 | smalljev semantic-v9 | 2B | 0.1 | 3.7 | 73.1 | 86.5 | 60.8 | 0.0203 est. | 0.150 | local GPU |
| 86 | Laya multilingual | 307M | 0.0 | 2.4 | 43.6 | 73.7 | 82.2 | 0.0039 est. | 0.443 | local CPU |
| 87 | OpenDecision (ModernBERT-large zero-shot) | 395M | 0.0 | 2.1 | 72.5 | 86.6 | 79.1 | 0.0050 est. | 0.073 | local GPU |
| 88 | BAAI bge-reranker-v2-m3 | 568M | 0.0 | 0.0 | 83.3 | 90.5 | 59.3 | 0.0227 est. | 0.029 | local GPU |
| 89 | Certo v1 (AltSlate Labs) | n/s | 0.0 | 0.0 | 87.5 | 91.4 | 96.9 | 0.0013 est. | 0.057 | local GPU |
| 90 | Decision Fast (FlyMy.AI, v53a) | n/s | 0.0 | 0.0 | 76.1 | 91.4 | 80.1 | 0.0046 est. | 0.058 | local GPU |
| 91 | Alibaba GTE Reranker ModernBERT-base | 149M | 0.0 | 0.0 | 75.2 | 91.5 | 69.3 | 0.0106 est. | 0.031 | local GPU |
| 92 | kev 0.5B | 0.5B | 0.0 | 0.0 | 65.0 | 88.5 | 80.1 | 0.0046 est. | 0.104 | local GPU |
| 93 | Laya (Convai Innovations, ModernBERT-large 421M) | 421M | 0.0 | 0.0 | 73.7 | 73.9 | 84.9 | 0.0032 est. | 0.668 | local CPU |
| 94 | lev-350m (Franck Verrot, LFM2.5-350M) | 350M | 0.0 | 0.0 | 77.7 | 93.6 | 80.0 | 0.0046 est. | 0.022 | local GPU |
| 95 | Qwen3.5-0.8B Decision Model (Mourad Ghafiri) | 0.8B | 0.0 | 0.0 | 73.6 | 71.8 | 79.5 | 0.0048 est. | 0.579 | local CPU |
| 96 | Mixedbread mxbai-rerank-base-v2 | 0.5B | 0.0 | 0.0 | 86.6 | 89.3 | 60.3 | 0.0210 est. | 0.042 | local GPU |
| 97 | Needle 3 (Cactus, 2-bit, local CPU) | n/s | 0.0 | 0.0 | 0.0 | 34.1 | 61.6 | 0.0191 est. | 67.682 | local CPU |
| 98 | Needle 3, options as tools (post-hoc adapter mode) | n/s | 0.0 | 0.0 | 0.0 | 41.0 | 61.6 | 0.0191 est. | 29.005 | local CPU |
| 99 | open-jev-deberta-v3-large (local CPU) | 435M | 0.0 | 0.0 | 77.1 | 68.3 | 77.6 | 0.0056 est. | 1.391 | local CPU |
| 100 | Open Jev JSON Canvas (JoshuaSP) | n/s | 0.0 | 77.1 | 0.0 | 85.6 | 49.3 | 0.0490 est. | 0.143 | local GPU |
| 101 | openJev Verdict (heman10x, ModernBERT-base 151M) | 151M | 0.0 | 0.0 | 52.2 | 83.9 | 86.6 | 0.0028 est. | 0.126 | local CPU |
| 102 | openJev Verdict 1.4 | 151M | 0.0 | 0.0 | 80.3 | 80.6 | 86.6 | 0.0028 est. | 0.310 | local CPU |
| 103 | Qwen3.8 27B (Chutes TEE) | 27B | 0.0 | 95.6 | 98.1 | 56.8 | 0.0 | 2.1784 est. | 6.489 | hosted API |
| 104 | verdict-small (Manavarya09, multilingual-e5-small 118M) | 118M | 0.0 | 0.0 | 59.5 | 82.1 | 100.0 | 0.0009 est. | 0.034 | local CPU |
| 105 | Von (wfzyx, Option-Marker 395M) | 395M | 0.0 | 0.0 | 83.5 | 75.7 | 82.7 | 0.0038 est. | 0.386 | local CPU |
| 106 | Laya typed-decisions | n/s | 0.0 | 0.0 | 83.3 | 63.4 | 82.5 | 0.0038 est. | 1.584 | local CPU |
| – | classifier.dev (fast tier) (honorable mention) | undisclosed (Jev) | 74.7 | 75.8 | 89.2 | 82.0 | 58.9 | 0.0235 est. | 0.518 | hosted API |
| – | SimpleJev Qwen3.6-35B-A3B (partial) | 35B-A3B | 0.0 | 0.0 | 78.5 | 75.2 | 35.1 | 0.1451 est. | 0.830 | hosted (author endpoint) |
| – | Decision-4B (Eval Engine / Chromia) (unranked) | 4B |  |  |  |  |  | 0.0137 est. | 0.042 | local GPU |

## Decision Index 0.2.1

Source: [`multimodalart/jev-decision-index` `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index), generated 2026-09-28T00:39Z, read 2026-09-30. 71 rows including Jev.

- Score: balanced skill (headline). ECE: calibration sample over 32 benchmarks.
- Median ms: open models are CUDA-synchronized request time on one RTX PRO 6000 without HTTP; Jev is an HTTPS round trip.

| # | Entrant | Params (served) | Base | Score | ECE | Median ms |
|---:|---|---:|---|---:|---:|---:|
| 1 | Jev 1.13.0 (hosted) | n/s | closed | 57.91 | 0.074 | 524.1 |
| 2 | Surogate Rune 26B-A4B v3 | 25.8B | gemma-4-26B-A4B-it | 57.44 | 0.120 | 120.5 |
| 3 | Decider chat · Gemma-4-31B | 32.7B | gemma-4-31B | 57.33 | 0.047 | 108.5 |
| 4 | AutoJev-27B | 27.8B | Qwen3.8-27B | 56.40 | 0.018 | 101.4 |
| 5 | simple-jev · Qwen3.8-27B (featherless) | 27.8B | Qwen3.8-27B | 55.74 | 0.113 | 373.0 |
| 6 | frontier-infra Jebadiah 27B | 27.8B | Qwen3.8-27B | 54.67 | 0.014 | 110.4 |
| 7 | Eikos-27B-FP8 Qwen3.8-27B LoRA | 27.8B | Qwen3.8-27B | 53.13 | 0.057 | 129.7 |
| 8 | reflex Qwen3.8-27B-FP8 (wide choice) | 27.8B | Qwen3.8-27B | 52.16 | 0.024 | 108.3 |
| 9 | Decider chat · Qwen3.6-27B | 27.8B | Qwen3.6-27B | 51.35 | 0.021 | 83.6 |
| 10 | Winnow-12B | 12.0B | gemma-4-12B | 50.02 | 0.168 | 72.5 |
| 11 | JoshuaSP diffgemma | 25.8B | diffusiongemma-26B-A4B-it | 49.47 | 0.215 | 260.4 |
| 12 | Jevfire Qwen3.8-27B | 27.8B | Qwen3.8-27B | 49.37 | 0.052 | 89.6 |
| 13 | Decider 35B-A3B | 36.0B | Qwen3.5-35B-A3B-Base | 47.11 | 0.023 | 101.4 |
| 14 | JPT-9B Qwen3.5-9B LoRA | 9.7B | Qwen3.5-9B-Base | 46.89 | 0.077 | 148.6 |
| 15 | Decision 1.0 Lux 9B | 9.7B | Qwen3.5-9B-Base | 43.49 | 0.076 | 51.0 |
| 16 | JPT-4B Qwen3.5-4B LoRA | 4.7B | Qwen3.5-4B-Base | 43.04 | 0.079 | 139.1 |
| 17 | Jet v6.2 Qwen3.5-4B LoRA | 4.7B | Qwen3.5-4B-Base | 42.60 | 0.141 | 46.8 |
| 18 | Xor Qwen3.6-35B-A3B | 36.0B | Qwen3.6-35B-A3B | 41.48 | 0.015 | 139.9 |
| 19 | Hopper (G) 1.2 Qwen3.5-4B LoRA | 4.7B | Qwen3.5-4B-Base | 40.77 | 0.093 | 23.3 |
| 20 | Decider 4B | 4.7B | Qwen3.5-4B-Base | 40.70 | 0.084 | 12.6 |
| 21 | Jev-Omni | 12.0B | gemma-4-12B | 40.53 | 0.161 | 54.9 |
| 22 | djev diffgemma | 25.8B | diffusiongemma-26B-A4B-it | 40.28 | 0.212 | 84.4 |
| 23 | Winnow-E4B | 8.0B | gemma-4-E4B | 39.89 | 0.058 | 45.0 |
| 24 | Bespoke Nimble 9B v2 | 9.7B | Qwen3.5-9B-Base | 39.57 | 0.024 | 77.3 |
| 25 | JevK5 Qwen3.5-4B LoRA | 4.7B | Qwen3.5-4B-Base | 38.81 | 0.027 | 22.0 |
| 26 | Interfaze lev Qwen3.5-4B LoRA | 4.7B | Qwen3.5-4B-Base | 38.54 | 0.064 | 70.8 |
| 27 | Kev 9B | 9.7B | Qwen3.5-9B-Base | 38.48 | 0.138 | 51.4 |
| 28 | InternLM Intern-Decision Qwen3.5-4B | 4.7B | Qwen3.5-4B-Base | 37.81 | 0.028 | 44.2 |
| 29 | razorback16 diffgemma | 25.8B | diffusiongemma-26B-A4B-it | 37.25 | 0.232 | 37.7 |
| 30 | TokenRhythm NeoHorse-Jev-4B | 4.7B | Qwen3.5-4B-Base | 36.75 | 0.104 | 49.0 |
| 31 | Solomon v1.1 | 27.8B | Qwen3.8-27B | 36.43 | 0.081 | 223.9 |
| 32 | Kev 4B | 4.7B | Qwen3.5-4B-Base | 34.64 | 0.176 | 52.1 |
| 33 | Decision 1.0 Nox | 4.7B | Qwen3.5-4B-Base | 34.36 | 0.140 | 53.2 |
| 34 | Jobe Qwen3.5-4B | 4.7B | Qwen3.5-4B-Base | 32.35 | 0.123 | 53.5 |
| 35 | mmastrac diffgemma | 25.8B | diffusiongemma-26B-A4B-it | 32.24 | 0.202 | 126.7 |
| 36 | open-jev (pngwn) | 4.7B | Qwen3.5-4B-Base | 29.91 | 0.059 | 112.3 |
| 37 | Together Tev1 Qwen3.5-4B | 4.7B | Qwen3.5-4B-Base | 29.24 | 0.104 | 35.8 |
| 38 | Decider 2B | 2.3B | Qwen3.5-2B-Base | 28.97 | 0.077 | 8.1 |
| 39 | openvons Qwen3-4B | 4.0B | Qwen3-4B-Instruct-2507 | 28.42 | 0.371 | 21.2 |
| 40 | FLock this-that 1.2 | 1.9B | decider-2b | 28.14 | 0.198 | 44.3 |
| 41 | Metask-Jev-4B | 4.7B | Qwen3.5-4B-Base | 26.89 | 0.103 | 57.3 |
| 42 | SemIf Qwen3.5-4B Base | 4.7B | Qwen3.5-4B-Base | 25.94 | 0.099 | 113.1 |
| 43 | Decision 1.0 Sol | 2.3B | Qwen3.5-2B-Base | 25.32 | 0.115 | 38.1 |
| 44 | mini-jev Qwen3-4B | 4.0B | Qwen3-4B-Instruct-2507 | 20.98 | 0.346 | 66.9 |
| 45 | Bosun v3.1 1.7B LoRA | 1.7B | Qwen3-1.7B-Base | 20.10 | 0.130 | 40.3 |
| 46 | InternLM Intern-Decision Qwen3.5-2B | 2.3B | Qwen3.5-2B-Base | 19.38 | 0.061 | 33.5 |
| 47 | JPT-0.8B Qwen3.5-0.8B LoRA | 873M | Qwen3.5-0.8B-Base | 19.22 | 0.069 | 117.5 |
| 48 | Decision 1.0 Eos 0.8B | 873M | Qwen3.5-0.8B-Base | 18.41 | 0.083 | 39.7 |
| 49 | Kev 0.8B | 873M | Qwen3.5-0.8B-Base | 14.60 | 0.074 | 41.6 |
| 50 | Bosun v3.1 0.6B LoRA | 596M | Qwen3-0.6B-Base | 14.32 | 0.142 | 38.7 |
| 51 | Together Tev1 Qwen3.5-0.8B | 873M | Qwen3.5-0.8B-Base | 12.85 | 0.126 | 28.5 |
| 52 | InternLM Intern-Decision Qwen3.5-0.8B | 873M | Qwen3.5-0.8B-Base | 11.94 | 0.025 | 33.7 |
| 53 | MoJev Qwen3.5-0.8B | 873M | Qwen3.5-0.8B-Base | 11.69 | 0.125 | 46.4 |
| 54 | GLiNER2.5-Decide | 486M | gliner2-large-v1 | 11.21 | 0.088 | 23.3 |
| 55 | MoganAI Lavoir ModernBERT-large | 396M | ModernBERT-large | 8.69 | 0.149 | 20.0 |
| 56 | jeff GLiFormer-large | 576M | gliformer-large-v1 | 8.04 | 0.097 | 21.8 |
| 57 | CLM-v0.1-8B Qwen3-8B heads | 8.2B | Qwen3-8B-Base | 7.40 | 0.323 | 46.8 |
| 58 | GLiNER 2.5 base | 194M | s | 6.76 | 0.367 | 14.1 |
| 59 | LFM2.5-2.6B-RLCD | 2.7B | LFM2.5-2.6B-Base | 6.76 | 0.255 | 39.3 |
| 60 | Decision 1.0 Kai | 308M | mmBERT-base | 6.52 | 0.185 | 30.4 |
| 61 | Laya | 421M | s | 6.04 | 0.140 | 5.8 |
| 62 | Supersonic Labs Julia 1 | 141M | mmBERT-small | 5.54 | 0.420 | 5.8 |
| 63 | system-one-gemma | 268M | gemma-3-270m | 5.07 | 0.239 | 31.9 |
| 64 | Decision 1.0 Lex | 308M | mmBERT-base | 4.54 | 0.169 | 29.8 |
| 65 | GLiNER 2.5 multilingual | 287M | s | 4.26 | 0.254 | 14.0 |
| 66 | GLiNER 2.5 small | 74M | s | 3.82 | 0.161 | 13.6 |
| 67 | Qwen-2.5-1B-RLCD | 1.5B | Qwen2.5-1.5B | 3.78 | 0.205 | 43.8 |
| 68 | Lumma-Fev-0.6B | 649M | Lumma-0.6B-Base | 2.97 | 0.236 | 21.3 |
| 69 | Verdict | 151M | gliclass-modern-base-v2.0 | 1.87 | 0.154 | 11.4 |
| 70 | Lumma-Fev-0.1B | 153M | Nandi-Mini-150M | 1.78 | 0.157 | 20.9 |
| 71 | LFM2.5-350M-RLCD | 354M | s | 1.38 | 0.568 | 26.7 |

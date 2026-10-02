# Model classes

Survey date: 2026-09-30. Research only: nothing was run. Counts come from Han Xiao's [All about Jev](https://hanxiao.io/all-about-jev/) dataset (`category == "model"`, 255 entries, local copy 2026-09-30); all credit for the collection goes to him. Scores are copied from [benchmarks.md](benchmarks.md) and the model docs; cross-board caveats are in [benchmarks.md#reading-the-leaderboards-across-models](benchmarks.md#reading-the-leaderboards-across-models).

"DI" = Jev Decision Index 0.2.1 balanced skill (Jev 1.13.0 = 57.91; open models on one RTX PRO 6000). Rows marked (inference) follow from architecture, not measurement.

## Family × size

Backbone is assigned by keyword from `base_model` (the `scripts/build_landscape.py` rules, plus manual fixes for 9 derivatives and Byrne-Jev); size from the first number in `params`. Mixed-size families count once.

| Family | <100M | 100–500M | 0.5–4B | 7–14B | 20–35B | >35B | unknown | Total | Examples |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| BERT-family encoders | 11 | 63 | 2 | | | | 11 | 87 | open-jev-base 28M, [Laya](models/open-reproductions.md#laya) 421M, [GLiNER2.5-Decide](models/gliner-decide.md) 340M |
| ↳ ModernBERT | 2 | 35 | 2 | | | | 8 | 47 | Laya (en), Von 395M, certo 421M |
| ↳ mmBERT | 2 | 17 | | | | | 2 | 21 | Laya multilingual 322M, open-jev-base 28M, Julia-1 144M |
| ↳ DeBERTa-v3 | 2 | 6 | | | | | 1 | 9 | GLiNER2.5-Decide, [open-jev-deberta-v3-large](models/open-reproductions.md#open-jev-deberta-v3-large) 434M, RLCD NLI 400M |
| ↳ other BERT (DistilBERT, MiniLM, Ettin) | 5 | 5 | | | | | | 10 | Nano-Jev 22.7M, System One Mini 69.3M, OpenDecider-nano 400M |
| Qwen decoders | | | 98 | 12 | 15 | 1 | 3 | 129 | [Kev](models/kev.md), JevK5, [decider](models/open-reproductions.md#decider), [CLM-8B](models/clm-8b.md), JEV-9B/27B, AutoJev-27B |
| Gemma decoders | | 3 | 3 | 2 | 1 | | 1 | 10 | Jev-Omni 12B, jevify Gemma 4 26B-A4B, system-one-270m |
| Other open backbones | 6 | 6 | 10 | 2 | 2 | 1 | 2 | 29 | MiniCPM5-2B (4), Llama (3), LFM2.5 (2), Bielik-Minitron-7B, Byrne-Jev 79M (SpikeWhale), nanodiff-350m (diffusion) |
| Training-free wrappers | — | — | — | — | — | — | — | 17 tagged `logits` | [AnyJev](models/anyjev.md) (listed as a runtime), [Bonsai-Llama-Jev](models/bonsai-llama-jev.md) |
| Hosted APIs | — | — | — | — | — | — | — | 0 | [Jev](models/jev.md), [d1](models/liquid-d1.md), [Decider 1](models/decider-1.md), [Solar Decide](models/solar-decide.md), [Tev1](models/tev1.md), Span-01, OpenAI Decisions |

- Qwen bases by version: Qwen3.5 60, Qwen3 30, Qwen3.8 15, Qwen2.5 11, Qwen3.6 1, unclear 12.
- Winnow-E4B/12B, Surogate Rune 26B-A4B and JEV-Gemma4-26B-A4B are Gemma models on DI but not in the dataset's model category.
- The dataset lists hosted APIs as apps or official entries, not models.

## Properties by family

| Family / tier | Readout | DI 0.2.1 | DI ECE | DI median latency (GPU) | Input limit | Options | Fine-tune | Licence pattern | Data location |
|---|---|---:|---:|---:|---|---|---|---|---|
| BERT <100M | head on encoder | GLiNER 2.5 small 3.8 | 0.161 | 13.6 ms | 512–8K (base) | per model | full, cheap | Apache/MIT | local |
| BERT 100–500M | option-marker or span head | 1.9–11.2 | 0.088–0.420 | 5.8–30 ms | Laya 512 (en), 1,024–8,192 (multi); open-jev-deberta 512; GLiNER chunks of 384 words | Laya: <~20 advised; GLiNER: no cap, schema tokens | full or LoRA; T4-class GPU | 70 of 87 Apache/MIT | local |
| Qwen 0.5–4B | LoRA + pointer head, or option-letter logits | 11.7–43.0 | 0.026–0.198 | 8–139 ms | Kev trained ≤384, served 65K; decider 32K | 2–255 | LoRA on one A10G/H100; Kev on MPS | 100 of 129 Qwen Apache/MIT; 6 NC | local |
| Qwen 7–14B | head, letter logits, or contrastive (CLM) | 38.5–46.9; CLM-8B 7.4 | 0.024–0.323 | 47–149 ms | CLM 2,048 (silent truncation) | CLM: no cap, cached | LoRA on L40S | Apache | local |
| Qwen 20–35B | LoRA + head, full SFT, logits | 36.4–56.4 | 0.014–0.081 | 101–224 ms | JEV-27B 1,024 at serving | JEV: 2–16 | LoRA/SFT on A100-H200 | Apache; OpenJev 27B CC-BY-NC | local |
| Gemma 4B–31B | letter logits (Winnow), fine-tune | 39.9–57.4 | 0.058–0.168 | 45–121 ms | Winnow served at 8,192 | — | LoRA | Apache or Gemma | local |
| Other open | mixed | 1.4–6.8 (4 entrants) | 0.157–0.568 | 21–39 ms | — | — | per model | 23 of 29 Apache/MIT | local |
| Training-free wrappers | next-token logits over labels | 55.7–57.3 (inference techniques) | 0.047–0.113 | 108–373 ms | base model context | AnyJev 2–26 | none needed; AnyJev L1/L2 fit 100–500 labels | base model's | local |
| Hosted APIs | undisclosed | Jev 57.91; Tev1 29.24; d1 58.9, GLiDE 64.81 (vendors' own runs, not on the board) | Jev 0.074 | Jev 524 ms (HTTPS) | Jev 64K; d1 32K; GLiDE 40K; Decider 1 4,096; Solar 512K | Jev 255; GLiDE 255; Solar 26; Tev1 24; Decider 1 10 | none (Tev1 weights open) | proprietary | vendor cloud, US for Jev and d1 |

DI rows: [benchmarks.md](benchmarks-leaderboards.md#decision-index-021). "Inference techniques" = `Decider chat · Gemma-4-31B` (57.33) and `simple-jev · Qwen3.8-27B` (55.74), both logit readouts with no released weights. Open-model rows exclude inference techniques; ranges come from the DI Space `data/index.json` (generated 2026-09-28T00:39Z, checked 2026-09-30). Tev1's 29.24 is on the board. Liquid AI reports d1 at 58.9 and Jev at 57.9 from its own run of the suite ([KuCoin/BlockBeats](https://www.kucoin.com/news/flash/liquid-ai-s-d1-decision-model-surpasses-jev-in-hugging-face-evaluation), 2026-09-29); the board data predates d1's 2026-09-29 release and has no d1 row ([liquid-d1.md](models/liquid-d1.md#benchmarks)).

## BERT-family encoders

- **How it works.** State and options go through one encoder pass; a head scores each option marker (Laya, open-jev-deberta) or each label span (GLiNER). No decoding ([concepts.md](concepts.md#architectures)).
- **Zero-shot.** Every encoder on DI 0.2.1 scores below 12. typed-decision-bench (kyr0): Laya 46.70%, Von 48.57%, Jev 88% ([bonsai-llama-jev.md](models/bonsai-llama-jev.md#benchmarks)). Base Laya 0.362 on typed-decisions (random 0.318).
- **Fine-tuned.** Laya-typed-decisions 0.766 vs Jev 0.727; browser element choice 0.10 → 0.66 top-1 ([fine-tuning.md](fine-tuning.md#when-fine-tuning-beats-zero-shot-published-evidence)). open-jev-deberta: 0.854 in domain, 0.690 on unseen question types.
- **Vendor suite.** GLiNER2.5-Decide 60.2% on Fastino's fast-decisions, ahead of JevK5 57.6% (Fastino authored the suite).
- **Many options.** At 128 candidates Laya 39% vs Jev 60%; Laya flips on option order 49.4% vs Jev 14.6% (decision-models-under-pressure, [benchmarks.md](benchmarks.md#other-evaluations)). Laya on BANKING77 (77 options): 0.425.
- **Calibration.** Laya ships over-confident; ECE 0.081 after temperature refit ([open-reproductions.md](models/open-reproductions.md#laya)).
- **On an M5 Max.** Laya: ~140 ms for three questions on Apple CPU via ONNX (npm README); ~32 ms median on an M5 Pro via MPS (third party, unverified). Weights 0.8–1.9 GB. GLiNER: no Mac figures; 167 ms p50 on a 48-vCPU Xeon at 64 tokens. open-jev-deberta: 1.8 s for 4 questions on M1 Max CPU.
- **<100M tier.** On DI, only GLiNER 2.5 small (74M served parameters) at 3.82; no entrant on JevBench or typed-decision-bench (as of 2026-09-30).
- **Choose when:** labelled data exists, the label set is fixed, CPU or browser deployment is required, or latency must stay under ~50 ms.

## Qwen-based decoders

- **How it works.** LoRA + pointer head on a frozen base (Kev 0.8B–9B, JEV; Kev-27B v2 is a full-weight SFT), full or LoRA fine-tune read at option-letter logits (decider, JevK5, AutoJev), or frozen encoder + contrastive heads (CLM-8B) ([fine-tuning.md](fine-tuning.md#architectures-and-what-gets-trained)).
- **0.5–4B.** DI 11.7 (MoJev, 0.8B) to 43.0 (JPT-4B). On JevBench v1.5.4 the Qwen3.5-4B derivatives JevK5 v0.3 (71.9) and Plumb-4B (71.6) rank 4th and 5th, behind Jev 72.1 ([live board](https://benchmarkheaven.com/jev-models), checked 2026-09-30); JevBench weights speed and cost as axes.
- **7–14B.** DI JPT-9B 46.89, Kev 9B 38.48. CLM-8B scores 7.40 on DI and 20% on BANKING77-20 in an independent Mac run; its strength is cached action scoring (0.6 ms revisited states) ([clm-8b.md](models/clm-8b.md#benchmarks)).
- **20–35B.** DI AutoJev-27B 56.40, Jebadiah 54.67, Eikos 53.13, Decider 35B-A3B 47.11, Solomon 36.43. JEV-27B: six-benchmark mean 84.07 vs Jev 83.85 (AutoTrust's runs). Bonsai-2-27B (PrismML ternary quant of Qwen3.8-27B) is in the wrapper section.
- **Size effects.** Long input: Kev-27B 0.833 vs Kev-9B 0.556 on questions buried in 1k–6k tokens. Knowledge: MMLU-Pro Kev-9B 0.52 vs Jev 0.84 ([kev.md](models/kev.md#benchmarks)). Kev-9B accuracy falls from 0.92 (≤384 tokens) to 0.75–0.79 on longer documents.
- **Many options.** decider on CLINC 151-way: 0.88 with all labels vs 0.98 with 10 sampled.
- **On an M5 Max.** Kev-0.8B 149 ms new / 28 ms cached, Kev-4B 721 / 136 ms (M5 32 GB, MLX, 5 questions, ~270 tokens). Kev-9B first-call p50 297–546 ms on M3 Max. JevK5 GGUF ~0.6 s per decision on M1 Pro. Qwen3.5 Gated DeltaNet layers have no MPS kernels. 27B bf16 (~54 GB) fits in 128 GB, but JEV-27B, AutoJev-27B and Kev-27B document no Mac path; OpenJev 27B ships a 16.5 GB Q4_K_M GGUF.
- **Choose when:** you need Jev-like zero-shot quality locally (4B for throughput, 27B for accuracy and long input), or plan to fine-tune with a documented recipe (Kev, decider).

## Gemma-based decoders

- DI: Surogate Rune 26B-A4B 57.44 (second overall), Winnow-12B 50.02, Jev-Omni 40.53, Winnow-E4B 39.89. JEV-Gemma4-26B-A4B self-reports 58.05 (not on the board).
- JevBench v1.5.4: Cygnet (frozen Gemma-4-12B-it) 73.7 and Winnow-12B Q8 73.2 rank first and second, a statistical tie, ahead of Jev 72.1.
- Diffusion variants on diffusiongemma-26B-A4B: JoshuaSP 49.47, djev 40.28 (ECE 0.21).
- ECE runs higher than the best Qwen entrants: Winnow-12B 0.168, Jev-Omni 0.161 vs Jebadiah 0.014.
- Winnow ships GGUF only with an `apple-silicon` server profile; no Mac timings are published ([open-reproductions.md](models/open-reproductions.md#winnow)). Jev-Omni lists MLX/MPS, ONNX and WebGPU in the dataset.
- **Choose when:** a Gemma licence is acceptable and you want an MoE model (26B-A4B) with DI near Jev.

## Other open backbones

- MiniCPM5-2B (4 entries), Llama (3), LFM2.5 (2), Bielik-Minitron-7B, Nemotron 3.5 30B-A3B, SpikeWhale (Byrne-Jev 79M), a 350M diffusion LM, and 5 from-scratch models (smallest 3.1M).
- DI scores: LFM2.5-2.6B-RLCD 6.76, Lumma-Fev-0.6B 2.97, Lumma-Fev-0.1B 1.78, LFM2.5-350M-RLCD 1.38.
- Language-specific bases: Bielik (Polish), LFM2.5-1.2B-JP (Japanese), Mankei-1B (German).
- **Choose when:** a language or licence requirement rules out Qwen and Gemma. Expect to benchmark it yourself.

## Training-free wrappers

- **How it works.** Read next-token logits over option labels from an unmodified LLM, then correct position bias and calibrate ([anyjev.md](models/anyjev.md)).
- AnyJev on Qwen3-8B, BANKING77-20: accuracy 0.747 raw → 0.807 with L1; ECE 0.240 → 0.095; auto-decidable at ≤5% error 7.7% → 52.0%. L2 heads on Qwen3-4B to 32B: 0.786–0.799 on typed-decisions (Jev 0.727).
- The top two DI inference techniques reach 55.74–57.33, within 2.2 points of Jev.
- Bonsai-Llama-Jev (Bonsai-2-27B ternary, Q2_64): 76.46% on typed-decision-bench (kyr0), p50 171 ms on NVIDIA, ~10 GB VRAM at 64K; calibration error 13% vs Jev 8.4%.
- **Costs.** AnyJev L0 runs K prefills per K-option Choice; first-call p50 on an M3 Max reached 7,860 ms on 20-way BANKING77. Choice caps at 26 options.
- **On an M5 Max.** Any MLX or vllm-metal model works; Qwen3-8B reserved ~20 GB on vllm-metal. Bonsai: ~17 GB of files, 46.8 tok/s chat on an M5 Max.
- **Choose when:** you already run an open LLM, have no labelled data, and have ≤26 options. L1/L2 need 100–500 labels.

## Hosted APIs

| API | Options | Context | Price per 1M input | Fine-tune | Notes |
|---|---|---|---|---|---|
| [Jev 1.13](models/jev.md) | 255 | 64K | $0.042 | no | DI 57.91; ECE 0.032–0.096 on classification (AI/ML API) |
| [d1](models/liquid-d1.md) | ≥2, max n/d | 32K | free tier; paid n/d | no | DI 58.9 (Liquid's own run, not on the board); policy permits training on inputs |
| [GLiDE](models/glide.md) | 255 | 40K per question | $0.30 | no | DI 0.2.1 64.81 (Fastino's own run, not on the board); reasons further when unsure |
| [Decider 1](models/decider-1.md) | 10 | 4,096 | $0.03 | no | typed-decisions 0.768 (vendor) |
| [Solar Decide](models/solar-decide.md) | 26 | 512K | $0.10 | no | 35B-A3B MoE; beta |
| [Tev1](models/tev1.md) | 24, one question | 32,768 (Together serverless) | $0.042 | open Qwen3.5-4B weights | returns a letter, no distribution |

- Span-01 answers Noul questions only ([span-01.md](models/span-01.md)). OpenAI Decisions is undocumented ([openai-decisions-api.md](models/openai-decisions-api.md)).
- Jev and d1 process in the US; retention, DPA and EU terms are in [data-governance.md](data-governance.md).
- **Choose when:** data may leave your infrastructure, you want top zero-shot quality with no GPU, and 250–750 ms per call is acceptable.

## Choosing a class

| Condition | Class | Evidence |
|---|---|---|
| ≤10 options, no labels | Hosted API or Qwen 4B–27B | DI gap Qwen 4B vs 27B: ~43 vs ~56 |
| 10–255 options | Jev, decider, Kev | cap 255; decider loses 10 points at 151 labels |
| 100+ labels, single choice | cascade Choices; or a fine-tuned encoder | 22M encoder + LR 93.2% vs Jev 79.2–80.1% on BANKING77 ([concepts.md](concepts.md#published-comparisons-on-many-class-tasks)) |
| 100+ tags, multi-label | GLiNER (native `multi_label`) or one Noul per label | no published study |
| ~100-token inputs | any class | all within training lengths |
| ~2,000-token inputs | Qwen 27B, hosted API, or GLiNER chunking | Laya en 512; JEV 1,024; CLM 2,048 truncates |
| <50 ms per decision | encoder or Qwen ≤4B on GPU | DI median 5.8–30 ms (encoders), 8–139 ms (≤4B) |
| EU / data must stay local | any open class on your infra | [data-governance.md](data-governance.md) |
| Labelled data (≥ a few hundred) | fine-tune an encoder or Kev/decider from a decision checkpoint | 400 Kev records: gain inside noise |
| CPU only | BERT encoders; JevK5/decider GGUF | GLiNER 167 ms on 48-vCPU; JevK5 ~0.6 s on M1 Pro |

## Open questions for experiments

Mapped to [experiments](../experiments/README.md). None has a published answer as of 2026-09-30.

| Class | Question | Experiment |
|---|---|---|
| BERT encoders | Accuracy vs option count (5→200) and order sensitivity after fine-tuning | 01, 02 |
| BERT encoders | Labels per class needed to pass zero-shot Qwen-4B (0/8/32/128) | 02 |
| BERT <100M | Any shared-board score above GLiNER 2.5 small's DI 3.82 | 01 |
| Qwen 0.5–4B | M5 Max latency with MLX vs GGUF at ~2,000 tokens | 01 |
| Qwen 0.5–4B | Choice vs 100 Nouls on the same tag set | 01 |
| Qwen 27B | Whether a 27B head runs on MLX at usable latency | 01 |
| Gemma | Calibration after refitting temperatures on our data | 01 |
| Wrappers | AnyJev L2 vs Kev-4B at matched label budgets | 01, 02 |
| Hosted APIs | ECE and coverage at 5% error on public datasets at 10/77/150 options | 01 |

## Sources

- Han Xiao, All about Jev dataset, [hanxiao.io/all-about-jev](https://hanxiao.io/all-about-jev/), `data/all-about-jev/all-methods.jsonl` (local copy 2026-09-30); counts computed with `scripts/build_landscape.py` backbone rules plus manual overrides. Entries are not independently verified.
- [benchmarks.md](benchmarks.md): Decision Index 0.2.1, fast-decisions, decision-models-under-pressure.
- [DI Space `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index) (generated 2026-09-28T00:39Z) and [JevBench v1.5.4 live board](https://benchmarkheaven.com/jev-models), fetched 2026-09-30.
- [typed-decision-bench (kyr0)](https://kyr0.github.io/typed-decision-bench/), via [bonsai-llama-jev.md](models/bonsai-llama-jev.md); the page did not render for this survey.
- Model docs: [jev.md](models/jev.md), [liquid-d1.md](models/liquid-d1.md), [decider-1.md](models/decider-1.md), [solar-decide.md](models/solar-decide.md), [tev1.md](models/tev1.md), [gliner-decide.md](models/gliner-decide.md), [kev.md](models/kev.md), [clm-8b.md](models/clm-8b.md), [anyjev.md](models/anyjev.md), [bonsai-llama-jev.md](models/bonsai-llama-jev.md), [open-reproductions.md](models/open-reproductions.md).
- [concepts.md](concepts.md), [fine-tuning.md](fine-tuning.md), [data-governance.md](data-governance.md), [landscape.md](landscape.md).

# Docs

Research checked 2026-09-30. Models in this field changed weekly in September 2026, so check the "Checked" date at the top of each model doc.

## Start here

| Doc | Contents |
|---|---|
| [concepts.md](concepts.md) | System One vs System Two, the `state` + typed-questions format (Choice / Score / Noul), calibration, many-label classification, timeline |
| [quickstart.md](quickstart.md) | Fastest way to run each model locally or via API; one client for all Jev-compatible endpoints |
| [model-classes.md](model-classes.md) | Model classes by backbone family (BERT encoders, Qwen, Gemma, other, wrappers, hosted) and size |
| [benchmarks.md](benchmarks.md) | Decision Index, JevBench, both typed-decision-benches, S1Bench, Fastino fast-decisions; cross-benchmark table. Full tables in [benchmarks-leaderboards.md](benchmarks-leaderboards.md) |
| [fine-tuning.md](fine-tuning.md) | Which models can be fine-tuned, how, and on what hardware |
| [data-governance.md](data-governance.md) | Self-hosting, fine-tuning rights, EU processing, retention and DPA for each deployment option |
| [landscape.md](landscape.md) | All 255 models in Han Xiao's [All about Jev](https://hanxiao.io/all-about-jev/) dataset (generated) |
| [../experiments/](../experiments/README.md) | Experiment index, plans and results |

## Model docs by backbone

| Backbone | Model | Weights | Runs on this Mac |
|---|---|---|---|
| Closed | [Jev](models/jev.md) (TypeSafe AI) | API only | No |
| Closed | [Liquid d1](models/liquid-d1.md) | API only | No |
| Closed | [Decider 1](models/decider-1.md) (meraGPT) | API only | No |
| Closed | [Solar Decide](models/solar-decide.md) (Upstage) | API only | No |
| Closed | [Span-01](models/span-01.md) (Respan) | API only | No |
| Closed | [OpenAI Decisions API](models/openai-decisions-api.md) | API only | No |
| DeBERTa | [GLiNER2.5-Decide](models/gliner-decide.md) (Fastino) | Apache-2.0 | Yes (CPU; MPS unverified) |
| BERT-family (ModernBERT, mmBERT, DeBERTa) | [Laya, open-jev-deberta and others](models/open-reproductions.md#bert-family-encoders) | Apache-2.0 | Yes |
| Qwen3.5 / Qwen3.8 | [Kev](models/kev.md) (0.8B–27B) | Apache-2.0 | 0.8B–9B via MLX |
| Qwen3-8B | [CLM-8B](models/clm-8b.md) (Contrastive-LM) | Apache-2.0 | Via vllm-metal (third-party recipe) |
| Qwen3.5-4B | [Tev1](models/tev1.md) (Together AI) | Public; licence pending | GGUF via llama.cpp |
| Qwen (various) | [JevK5, Jev-Style, decider, autotrust JEV and others](models/open-reproductions.md#qwen-based) | Mostly Apache-2.0 | Mostly |
| Gemma | [Winnow, Jev-Omni](models/open-reproductions.md#gemma-based) | See doc | See doc |
| Qwen3.8-27B (Ternary Bonsai 2, PrismML) | [Bonsai-Llama-Jev](models/bonsai-llama-jev.md) (kyr0) | MIT code; Apache-2.0 weights | Yes (llama.cpp) |
| Any open LLM | [AnyJev](models/anyjev.md) (Nokia) | Apache-2.0 library | HF backend (MPS unverified) |

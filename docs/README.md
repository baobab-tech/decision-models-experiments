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
| [scan-2026-10-02.md](scan-2026-10-02.md) | New releases (Clef, pplx-decider, Strands Decider, GLiDE and others) and the most-downloaded and most-liked decision repos, 2026-10-02 |
| [landscape.md](landscape.md) | All 255 models in Han Xiao's [All about Jev](https://hanxiao.io/all-about-jev/) dataset (generated) |
| [../experiments/](../experiments/README.md) | Experiment index, plans and results |

## Model docs by backbone

| Backbone | Model | Weights | Runs on this Mac |
|---|---|---|---|
| Closed | [Jev](models/jev.md) (TypeSafe AI) | API only | No |
| Closed | [Liquid d1](models/liquid-d1.md) | API only | No |
| Closed | [GLiDE](models/glide.md) (Fastino) | API only | No |
| Closed | [Decider 1](models/decider-1.md) (meraGPT) | API only | No |
| Closed | [Solar Decide](models/solar-decide.md) (Upstage) | API only | No |
| Closed | [Span-01](models/span-01.md) (Respan) | API only | No |
| Closed | [OpenAI Decisions API](models/openai-decisions-api.md) | API only | No |
| Qwen3.8-27B / Qwen3.5-9B | [Clef, Clef-flash](models/clef.md) (Cloudflare); also Workers AI | Apache-2.0 | MLX 4-bit and 8-bit builds |
| Qwen3.8-27B | [pplx-decider-v1-27b](models/pplx-decider.md) (Perplexity; same weights as AutoJev-27B); also Perplexity API | Apache-2.0 | No documented path |
| Qwen3.5-2B | [Strands Decider](models/strands-decider.md) (AWS Strands Labs) | Apache-2.0 | Yes (MPS) |
| DeBERTa | [GLiNER2.5-Decide](models/gliner-decide.md) (Fastino) | Apache-2.0 | Yes (CPU; MPS unverified) |
| ModernBERT / mmBERT | [Laya](models/laya.md) (Convai) | Apache-2.0 | Yes (MPS, ONNX) |
| ModernBERT-large | [Von](models/von.md) (wfzyx) | Apache-2.0 | Yes (MPS) |
| ModernBERT-base | [openJev Verdict](models/rlcd-modernbert.md) (heman10x) | Apache-2.0 | Yes (CPU, ONNX) |
| ModernBERT-base | [ModernJEV-Decide-Preview](models/modernjev-decide.md) (Maziyar Panahi) | Apache-2.0 | Yes (CPU) |
| BERT-family (other) | [open-jev-deberta, Julia-1 and others](models/open-reproductions.md#bert-family-encoders) | Apache-2.0 | Yes |
| Qwen3.5 / Gemma 4 | [decider](models/decider.md) (Mapika; unrelated to Decider 1) | Apache-2.0 | Yes (MPS, GGUF) |
| Qwen3.5 | [JevK5](models/jevk5.md) (alibiserikbay) | Apache-2.0 | GGUF via llama.cpp Metal |
| Qwen3.5 | [Intern-Decision](models/intern-decision.md) (InternLM) | Apache-2.0 | MPS untested; Core ML 0.8B |
| Qwen3.5 / Qwen3.8 / Gemma 4 | [autotrust JEV / GEV](models/autotrust-jev.md) | Apache-2.0 | No documented path |
| Qwen3.5 / Qwen3.8 | [Kev](models/kev.md) (0.8B–27B) | Apache-2.0 | 0.8B–9B via MLX |
| Qwen3-8B | [CLM-8B](models/clm-8b.md) (Contrastive-LM) | Apache-2.0 | Via vllm-metal (third-party recipe) |
| Qwen3.5-4B | [Tev1](models/tev1.md) (Together AI) | Public; licence pending | GGUF via llama.cpp |
| Qwen (various) | [Jev-Style, OpenThai-SystemOne and others](models/open-reproductions.md#qwen-based) | Mostly Apache-2.0 | Mostly |
| Gemma-4-12B | [Jev-Omni](models/jev-omni.md) (akhilaaa3) | Apache-2.0 (Gemma 4 terms) | MLX 4-bit (community) |
| Gemma-4-12B, unmodified | [Cygnet](models/cygnet.md) (blockbrain; recipe, no new weights) | MIT shim; Gemma 4 | Yes (Ollaya, GGUF Metal) |
| Gemma | [Winnow and others](models/open-reproductions.md#gemma-based) | See doc | See doc |
| Qwen3.8-27B (Ternary Bonsai 2, PrismML) | [Bonsai-Llama-Jev](models/bonsai-llama-jev.md) (kyr0) | MIT code; Apache-2.0 weights | Yes (llama.cpp) |
| Any open LLM | [AnyJev](models/anyjev.md) (Nokia) | Apache-2.0 library | HF backend (MPS unverified) |

New releases and download counts: [scan-2026-10-02.md](scan-2026-10-02.md).

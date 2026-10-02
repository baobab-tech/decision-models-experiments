# Getting started with decision models

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Docs checked](https://img.shields.io/badge/docs%20checked-2026--09--30-informational)](docs/README.md)
[![Status](https://img.shields.io/badge/status-research%20phase-lightgrey)](experiments/README.md)

Guides, run instructions and open experiments for **System One decision models**: Jev, Liquid d1, GLiDE, GLiNER2.5-Decide, Kev, Laya and 250+ open models on Hugging Face.

This repo is maintained by [Baobab Tech](https://github.com/baobab-tech). Baobab Tech is not affiliated with any model, vendor, benchmark or dataset listed here. Each model, name, benchmark and dataset belongs to its authors, and each doc links to the original source. What this repo adds is the docs, experiment plans and results.

## What a decision model does

You send a piece of text (the `state`) and typed questions. You get back a probability for every possible answer, from one forward pass with no generated text.

```json
{
  "state": "My payouts have failed for three days, please help today.",
  "questions": {
    "department": {"type": "choice", "instructions": "Which team handles this?",
                   "criteria": {"billing": "Payments", "technical": "Bugs"}},
    "urgent":     {"type": "noul",   "instructions": "The message is time-sensitive"},
    "frustration":{"type": "score",  "instructions": "How frustrated?",
                   "criteria": ["Calm", "Frustrated", "Furious"]}
  }
}
```

```json
{"answers": {
  "department":  {"choice": "technical", "probabilities": {"billing": 0.07, "technical": 0.93}},
  "urgent":      {"noul": 0.99},
  "frustration": {"score": 1.01, "probabilities": {"0": 0.01, "1": 0.96, "2": 0.03}}
}}
```

| Type | Answers |
|---|---|
| **Choice** | one of up to 255 options |
| **Score** | a level on a 2–10 point scale |
| **Noul** | yes / no, as a probability |

The same request works against Jev, Liquid d1, Kev, Laya (`laya-serve`), Bonsai-Llama-Jev, Decider 1 and Solar Decide. More in [concepts](docs/concepts.md).

## Start here

1. [Concepts](docs/concepts.md): the format, calibration, and how many-label classification works.
2. [Quickstart](docs/quickstart.md): run a model on a Mac or through an API, with one client for every compatible endpoint.
3. [Model classes](docs/model-classes.md): how a 300M BERT encoder, a 4B Qwen head and a 27B model differ.
4. [Benchmarks](docs/benchmarks.md): Decision Index, JevBench, typed-decision-bench, S1Bench.
5. [Data governance](docs/data-governance.md): who can self-host, fine-tune, or process in the EU.

## Models

| Model | Backbone | Weights | Runs locally | Doc |
|---|---|---|---|---|
| Jev (TypeSafe AI) | closed | API only | no | [jev](docs/models/jev.md) |
| Liquid d1 | closed | API only | no | [liquid-d1](docs/models/liquid-d1.md) |
| GLiDE (Fastino) | closed | API only | no | [glide](docs/models/glide.md) |
| Decider 1 (meraGPT), Solar Decide (Upstage), Span-01 (Respan), OpenAI Decisions | closed | API only | no | [models/](docs/models/) |
| GLiNER2.5-Decide (Fastino) | DeBERTa-v3-large, 340M per card | Apache-2.0 | yes, CPU | [gliner-decide](docs/models/gliner-decide.md) |
| Clef, Clef-flash (Cloudflare) | Qwen3.8-27B / Qwen3.5-9B | Apache-2.0; also Workers AI | MLX builds | [clef](docs/models/clef.md) |
| pplx-decider-v1-27b (Perplexity) | Qwen3.8-27B; same weights as AutoJev-27B | Apache-2.0; also Perplexity API | no documented path | [pplx-decider](docs/models/pplx-decider.md) |
| Strands Decider (AWS Strands Labs) | Qwen3.5-2B | Apache-2.0 | yes, MPS or MLX | [strands-decider](docs/models/strands-decider.md) |
| Laya, Von, openJev Verdict, ModernJEV-Decide | ModernBERT / mmBERT | Apache-2.0 | yes | [laya](docs/models/laya.md), [von](docs/models/von.md), [verdict](docs/models/rlcd-modernbert.md), [modernjev](docs/models/modernjev-decide.md) |
| Small fine-tunable models: jeff, bekko, Decision-Jef, Yway, systemone-lite, mini-Jev, bit-jev, small RLCD LMs | GLiFormer / Ettin / mmBERT / XLM-R / Qwen / BitNet / LFM | mixed; bekko and bit-jev unlicensed | mostly | [fine-tuning table](docs/fine-tuning.md#small-open-models-you-can-fine-tune--25b) |
| Other BERT-family encoders | DeBERTa / mmBERT | Apache-2.0 | yes | [open models](docs/models/open-reproductions.md#bert-family-encoders) |
| Kev (0.8B–27B) | Qwen3.5 / Qwen3.8 | Apache-2.0 | 0.8B–9B via MLX | [kev](docs/models/kev.md) |
| decider (Mapika), JevK5, Intern-Decision, autotrust JEV | Qwen3.5 / Qwen3.8 / Gemma 4 | Apache-2.0 | decider and JevK5 yes | [decider](docs/models/decider.md), [jevk5](docs/models/jevk5.md), [intern-decision](docs/models/intern-decision.md), [autotrust-jev](docs/models/autotrust-jev.md) |
| Jev-Omni, Cygnet | Gemma-4-12B | Apache-2.0 (Gemma 4 terms); Cygnet ships no weights | community MLX / GGUF | [jev-omni](docs/models/jev-omni.md), [cygnet](docs/models/cygnet.md) |
| Jev-Style and other Qwen models | Qwen | mostly Apache-2.0 | mostly | [open models](docs/models/open-reproductions.md#qwen-based) |
| CLM-8B (Contrastive-LM) | Qwen3-8B | Apache-2.0 | via vllm-metal | [clm-8b](docs/models/clm-8b.md) |
| Tev1 (Together AI) | Qwen3.5-4B | public, licence pending | GGUF | [tev1](docs/models/tev1.md) |
| Bonsai-Llama-Jev | Qwen3.8-27B, ternary (PrismML Bonsai 2) | MIT code, Apache-2.0 weights | yes, llama.cpp | [bonsai-llama-jev](docs/models/bonsai-llama-jev.md) |
| AnyJev (Nokia) | any open LLM | Apache-2.0 | yes | [anyjev](docs/models/anyjev.md) |

New releases and download counts as of 2026-10-02: [scan](docs/scan-2026-10-02.md). All 255 models in Han Xiao's [All about Jev](https://hanxiao.io/all-about-jev/) dataset are in [landscape](docs/landscape.md), grouped by backbone and size.

## Findings so far

These come from published sources; we haven't run anything yet.

- On Decision Index 0.2.1, Liquid AI reports d1 at 58.9 and Jev 1.13 at 57.9 from its own run of the suite ([KuCoin/BlockBeats](https://www.kucoin.com/news/flash/liquid-ai-s-d1-decision-model-surpasses-jev-in-hugging-face-evaluation), 2026-09-29). The public board, generated 2026-09-28 before d1's release, lists Jev first at 57.91 and has no d1 row ([Space](https://huggingface.co/spaces/multimodalart/jev-decision-index), checked 2026-09-30). Every BERT-family encoder scores below 12 ([benchmarks](docs/benchmarks.md#reading-the-leaderboards-across-models)).
- On JevBench v1.5.4, which also scores speed and cost, two open Gemma-4-12B models (Cygnet 73.7, Winnow-12B Q8 73.2) lead Jev 1.13 (72.1) in a statistical tie, and 4B models follow within 0.5 points ([live board](https://benchmarkheaven.com/jev-models), checked 2026-09-30).
- Choice is capped at 255 options on Jev and Kev, and at 26 on AnyJev. No vendor publishes accuracy for 100+ options ([experiment 01](experiments/01-many-option-classification/)).
- Multi-label tagging means one Noul per label on every Jev-compatible API. Only GLiNER2.5-Decide has a native multi-label mode.
- Jev and d1 process data in the US and cannot be fine-tuned. Open models can run and train on your own hardware ([data governance](docs/data-governance.md)).

## Experiments

| # | Experiment | Status |
|---|---|---|
| 01 | [Many-option classification](experiments/01-many-option-classification/): 10–200+ labels, tags, document types; ~100 vs ~2,000-token inputs | proposed |
| 02 | [Fine-tuning](experiments/02-fine-tuning/): which models, how, and how many labels it takes to beat zero-shot | proposed |
| 03 | [Jev vs open models on document tasks](experiments/03-jev-vs-open-document-tasks/): language, orientation, RVL-CDIP classes, bundle splitting and parse triage on PDFs; by [LlamaIndex](https://github.com/run-llama/jev_vs_oss) | done |

Each experiment starts as a written plan. Results, code and run metadata are published in its folder ([index](experiments/README.md)).

<details>
<summary>Repository layout</summary>

```
docs/
  README.md                   docs index
  concepts.md                 format, calibration, many-label classification
  quickstart.md               run each model locally or via API
  model-classes.md            models by backbone family and size
  benchmarks.md               benchmarks and cross-benchmark table
  benchmarks-leaderboards.md  full leaderboard tables
  fine-tuning.md              fine-tuning options by backbone
  data-governance.md          governance comparison across models
  landscape.md                all 255 dataset models (generated)
  models/                     one doc per model or family
experiments/
  README.md                   index and status
  common/                     shared datasets, metrics, conventions, code
  <nn>-<slug>/                one folder per experiment
scripts/                      doc generators
data/                         external datasets (raw files gitignored)
```

</details>

## Contributing

Issues and pull requests are welcome, especially corrections to the model docs (with a source link) and new open decision models. Contributor and agent conventions are in [AGENTS.md](AGENTS.md).

## Credits

[docs/landscape.md](docs/landscape.md) is generated from [All about Jev](https://hanxiao.io/all-about-jev/), a dataset compiled and curated by Han Xiao ([announcement](https://www.linkedin.com/feed/update/urn:li:ugcPost:7508930228493348865/)).

## License

[MIT](LICENSE)

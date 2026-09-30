# Getting started with decision models

Guides, run instructions and open experiments for System One decision models (Jev, GLiNER2.5-Decide, Liquid d1, and open Hugging Face models), from [Baobab Tech](https://github.com/baobab-tech).

A decision model takes a piece of text (the *state*) and a set of typed questions, and returns a calibrated probability for every answer in one forward pass. It generates no text. Question types:

- **Choice**: pick one option from a list.
- **Score**: pick a level on a 2–10 scale.
- **Noul**: yes / no.

We test when these models can replace an LLM or a fine-tuned classifier in real pipelines, and publish the results, code and notes as we go.

## Models under study

| Model | Vendor | Weights | Self-host / fine-tune | Notes |
|---|---|---|---|---|
| Jev | TypeSafe AI | API only | No / No | Early access since 2026-09-15; 64k context; see [docs/models/jev.md](docs/models/jev.md) |
| GLiNER2.5-Decide | Fastino | Open, Apache 2.0 | Yes / Yes | 340M-parameter DeBERTa-v3 encoder; runs on CPU |
| d1 | Liquid AI | API only | No / No | Released 2026-09-29; billed for input tokens only |
| Bonsai-Llama-Jev | kyr0 (community) | Open, MIT code | Yes / calibration only | llama.cpp server on Bonsai-2-27B; see [docs/models/bonsai-llama-jev.md](docs/models/bonsai-llama-jev.md) |
| Open Jev-style models | Various (Hugging Face) | Open | Yes / varies by model | See [docs/models/open-reproductions.md](docs/models/open-reproductions.md); 255 community models are catalogued in [docs/landscape.md](docs/landscape.md) |

API-only models process your text on the vendor's cloud. Where the data goes, how long it is kept, whether the vendor trains on it, and whether it can be processed in the EU are covered in the "Data governance" section of each model doc. [docs/data-governance.md](docs/data-governance.md) has the side-by-side comparison.

## Questions we plan to test

1. **Many-option classification.** Do decision models hold up with 10+ options, 100+ tags (e.g. news topics), or document-type labels, on inputs of ~100 and ~2,000 tokens? Baselines: embeddings + kNN, fine-tuned classifiers, and LLMs.
2. **Fine-tuning.** Which models can be fine-tuned, how, and when fine-tuning beats zero-shot.

Each experiment gets a written plan before any code runs. Status is tracked in [docs/experiments.md](docs/experiments.md).

## Repository layout

```
docs/
  README.md            index and model comparison
  concepts.md          System One models, typed questions, calibration
  landscape.md         all 255 models in the all-about-jev dataset (generated)
  quickstart.md        fastest way to run each model (Mac or API)
  model-classes.md     models by backbone family and size
  benchmarks.md        Decision Index, JevBench, typed-decision-bench and others
  benchmarks-leaderboards.md  full leaderboard tables
  fine-tuning.md       fine-tuning options across models
  data-governance.md   cross-model governance matrix (details live in each model doc)
  experiments.md       planned and completed experiments
  models/              one file per model or model family
experiments/           one folder per experiment (added as we run them)
scripts/               doc generators (e.g. build_landscape.py)
data/                  external datasets; raw files gitignored, fetch steps in each README
```

## Running the models

Open-weight models run locally; this work uses an Apple Silicon Mac (M5 Max, 128 GB). The API models need a key from the vendor or from Vercel AI Gateway. Setup steps for each model are in [docs/quickstart.md](docs/quickstart.md).

## Status

Research phase. The docs reflect sources checked on 2026-09-30. No experiments have run yet.

## Contributing

Issues and pull requests are welcome, especially corrections to the model docs and new open decision models to add.

## Credits

- [docs/landscape.md](docs/landscape.md) is generated from [All about Jev](https://hanxiao.io/all-about-jev/), a dataset compiled and curated by Han Xiao ([announcement](https://www.linkedin.com/feed/update/urn:li:ugcPost:7508930228493348865/)).

## License

[MIT](LICENSE)

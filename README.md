# jev-experiments

Open experiments with System One decision models, run by [Baobab Tech](https://github.com/baobab-tech).

A decision model takes a piece of text (the *state*) and a set of typed questions, and returns a calibrated probability for every answer in one forward pass. It generates no text. Question types:

- **Choice**: pick one option from a list.
- **Score**: pick a level on a 2–10 scale.
- **Noul**: yes / no.

We test when these models can replace an LLM or a fine-tuned classifier in real pipelines, and publish the results, code and notes as we go.

## Models under study

| Model | Vendor | Weights | Notes |
|---|---|---|---|
| Jev | TypeSafe AI (unverified) | see [docs/models/jev.md](docs/models/jev.md) | Reference implementation of the typed-question format |
| GLiNER2.5-Decide | Fastino | Open, Apache 2.0 | 340M-parameter DeBERTa-v3 encoder; runs on CPU |
| d1 | Liquid AI | API only | Released 2026-09-29; billed for input tokens only |
| Open Jev-style models | Various (Hugging Face) | Open | See [docs/models/open-reproductions.md](docs/models/open-reproductions.md) |

## Questions we plan to test

1. **Many-option classification.** Do decision models hold up with 10+ options, 100+ tags (e.g. news topics), or document-type labels, on inputs of ~100 and ~2,000 tokens? Baselines: embeddings + kNN, fine-tuned classifiers, and LLMs.
2. **Fine-tuning.** Which models can be fine-tuned, how, and when fine-tuning beats zero-shot.

Each experiment gets a written plan before any code runs. Status is tracked in [docs/experiments.md](docs/experiments.md).

## Repository layout

```
docs/
  README.md            index and model comparison
  concepts.md          System One models, typed questions, calibration
  quickstart.md        fastest way to run each model (Mac or API)
  benchmarks.md        Decision Index and other published evals
  fine-tuning.md       fine-tuning options across models
  experiments.md       planned and completed experiments
  models/              one file per model or model family
experiments/           one folder per experiment (added as we run them)
```

## Running the models

Open-weight models run locally; this work uses an Apple Silicon Mac (M5 Max, 128 GB). The API models need a key from the vendor or from Vercel AI Gateway. Setup steps for each model are in [docs/quickstart.md](docs/quickstart.md).

## Status

Research phase. The docs are being written; no experiments have run yet.

## Contributing

Issues and pull requests are welcome, especially corrections to the model docs and new open decision models to add.

## License

[MIT](LICENSE)

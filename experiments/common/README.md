# Common

Shared docs and code for all experiments. No shared code exists yet; it's added when the first experiment starts.

| File | Contents |
|---|---|
| [datasets.md](datasets.md) | Candidate datasets: labels, type, length, licence, source |
| [metrics.md](metrics.md) | Definitions of every metric we report |

## Planned shared code

Written only when an approved experiment needs it:

- **Dataset loaders:** these return `(text, labels, split)` with a fixed seed and record the dataset version.
- **Decision client:** one interface over the TypeSafe `/v1/systemone` format (Jev, d1, Kev, Bonsai-Llama-Jev, Decider 1, Solar Decide) and over native APIs (GLiNER2, AnyJev, CLM). See [../../docs/quickstart.md](../../docs/quickstart.md).
- **Metrics:** implementations of [metrics.md](metrics.md).

## Run metadata

Every run writes `results/<run-id>/run.json` with:

- `experiment`, `run_id`, `date` (UTC)
- `model`, plus its `revision` (HF commit hash) or `api_version`
- `where`: `local`, `api` or `gateway`, plus `region` for API and gateway runs
- `hardware` (e.g. `M5 Max 128 GB, MLX`) and `dtype` or quantisation
- `dataset`, `dataset_version`, `split`, `n`, `seed`
- `question_format`: `choice`, `noul-per-label` or `staged-choice`, plus label text or descriptions
- `metrics`: keys as defined in [metrics.md](metrics.md)

Raw predictions (`predictions.jsonl`) are gitignored if they contain dataset text whose licence forbids redistribution.

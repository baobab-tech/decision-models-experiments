# Common

Shared docs and code for all experiments. No shared code exists yet; it's added when the first experiment starts.

| File | Contents |
|---|---|
| [datasets.md](datasets.md) | Candidate datasets: labels, type, length, licence, source |
| [metrics.md](metrics.md) | Definitions of every metric we report |
| [prompts/excerpt-tagging.md](prompts/excerpt-tagging.md) | Classify-only LLM prompts for relabelling task B excerpts |

## Planned shared code

Written only when an approved experiment needs it:

- **Dataset loaders:** these return `(text, labels, split)` with a fixed seed and record the dataset version.
- **Decision client:** one interface over the TypeSafe `/v1/systemone` format (Jev, d1, Kev, Bonsai-Llama-Jev, Decider 1, Solar Decide) and over native APIs (GLiNER2, AnyJev, CLM). See [../../docs/quickstart.md](../../docs/quickstart.md).
- **Metrics:** implementations of [metrics.md](metrics.md).

## HF Inference Providers

- Call `https://router.huggingface.co/v1` with `HF_TOKEN` and the header `X-HF-Bill-To: baobabtech`, so usage bills to the Baobab Tech org.
- Pin the provider with a model suffix, e.g. `Qwen/Qwen3.8-Flash-Next:featherless-ai`, and record it in `run.json`.

```python
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
    default_headers={"X-HF-Bill-To": "baobabtech"},
)
```

## Run metadata

Every run writes `results/<run-id>/run.json` with:

- `experiment`, `run_id`, `date` (UTC)
- `model`, plus its `revision` (HF commit hash) or `api_version`
- `where`: `local`, `api`, `gateway` or `hf-inference-providers`, plus `provider` and `region` for remote runs
- `hardware` (e.g. `M5 Max 128 GB, MLX`) and `dtype` or quantisation
- `dataset`, `dataset_version`, `split`, `n`, `seed`
- `question_format`: `choice`, `noul-per-label` or `staged-choice`, plus label text or descriptions
- `metrics`: keys as defined in [metrics.md](metrics.md)

Raw predictions (`predictions.jsonl`) are gitignored if they contain dataset text whose licence forbids redistribution.

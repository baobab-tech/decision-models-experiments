# AGENTS.md

Instructions for coding agents (Claude Code, Codex, Cursor, etc.) working in this repo.

## Project

A public repo run by Baobab Tech. It records experiments with System One decision models (Jev, GLiNER2.5-Decide, Liquid d1, and open Hugging Face models). Everything committed here is published, so write for outside readers.

## Where things are

- [docs/README.md](docs/README.md): docs index and model comparison table. Start here.
- [docs/concepts.md](docs/concepts.md): terminology (state, Choice / Score / Noul, calibration).
- [docs/quickstart.md](docs/quickstart.md): how to run each model locally or through its API.
- [docs/models/](docs/models/): one file per model or model family.
- [docs/benchmarks.md](docs/benchmarks.md), [docs/fine-tuning.md](docs/fine-tuning.md): published evals and fine-tuning options.
- [docs/experiments.md](docs/experiments.md): experiment list and status.
- `experiments/<nn>-<slug>/`: code and results for one experiment.

## How we work

1. **The maintainer picks the experiments.** Don't start an experiment, download model weights, or scaffold experiment code unless the maintainer asks for that specific experiment. You may propose experiments by adding them to `docs/experiments.md` with status `proposed`.
2. **Write the plan first.** Each experiment starts as a written plan in `experiments/<nn>-<slug>/README.md`: question, models, datasets, baselines, metrics, and the result that would change a decision. The code comes after the plan.
3. **Results go in the docs.** When an experiment finishes, write the results and conclusions in its README. Update its status in `docs/experiments.md`, and update model docs if a finding changes them.
4. **Cite sources.** Model docs cover a fast-moving field (most releases date from September 2026). Link every claim to a primary source, and mark anything you couldn't check as `(unverified)`. Record the date you checked it.
5. **Make runs reproducible.** Pin dependencies. Record hardware, model revision (HF commit hash or API model version), seeds, and dataset version with every result.

## Environment

- Hardware: Apple Silicon (M5 Max, 128 GB). Use MPS or MLX where the model supports it; fall back to CPU.
- Python: manage with `uv` (`uv init`, `uv add`, `uv run`). One `pyproject.toml` per experiment, so dependencies stay isolated.
- Node 22 is available for TypeScript clients (e.g. ONNX Runtime, AI SDK).
- Hugging Face: `hf` CLI. Model weights go in the HF cache, never in the repo.
- Secrets: API keys (e.g. `LIQUID_API_KEY`, `AI_GATEWAY_API_KEY`, `HF_TOKEN`) go in `.env`, which is gitignored. Never commit keys or print them in logs or docs.

## Writing style

Applies to docs, READMEs, comments and commit messages.

- Lead with the fact.
- No hype or verdict words: *powerful, interesting, key, elegant*.
- No sentences about the document itself: *this section explains…*
- One fact per sentence, stated once.
- Headings are labels.
- Give numbers with units, sample sizes and dates.

## Don't commit

- Model weights, large datasets or caches: link to them or add a download script instead.
- Credentials or `.env` files.
- Unlicensed data. Check each dataset's license and note it in the experiment README.

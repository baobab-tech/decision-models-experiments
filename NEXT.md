# NEXT

Current state and next steps. Keep this short: delete items when done, add new ones as they come up. Last updated 2026-10-04.

## State

- Docs: model docs, benchmarks, governance and landscape fact-checked on 2026-09-30 and 2026-10-02.
- Dataset: [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs) is public.
  - Built by `experiments/common/build_evaluation_docs_dataset.py` from `evalexplorer-data` at `5315eab`; `fcd40f8` added `definition_excerpts` to `taxonomy`; `5017706` adds the LLM label columns and `<field>_majority` for `eval_sample`.
  - Default labels are silver (GLM-5.3-Flash); the `*_pipeline` columns hold the pipeline labels.
- HF collection: [Decision models experiments](https://huggingface.co/collections/baobabtech/decision-models-experiments-6ac0461f242cbc19f87d4854), 32 items.
- Experiment 01 is `planned` (approved 2026-10-02): phase 1 is task B, scored against the majority of three LLMs (no human gold set). Reference labels for the 600 test excerpts generated 2026-10-03: LLMs agree at 84.2–85.0; pipeline at 52.8. 02 is `planned` (approved 2026-10-02). 03 is LlamaIndex's, done.

## Next

1. **Before 01 phase 1 runs:**
   - `.env` has `HF_TOKEN`, `AI_GATEWAY_API_KEY` (Jev, d1) and `FASTINO_API_KEY` (GLiDE). Jev and d1 smoke-tested through the gateway on 2026-10-04.
   - Check featherless-ai's processing region and retention (Qwen3.8-Flash-Next) for the data governance section.
   - Runner and scorer written (`run.py`, `score.py`, `gateway/evaluate.mjs`). Jev 71.0, GLiDE 52.4, d1 39.5 at p ≥ 0.5 (2026-10-04); LLM range 84.2–85.0.
   - Thresholds: d1 and GLiDE over-tag at 0.5. Fit per-model thresholds on held-out labels: label ~300 validation excerpts with the three LLMs (~$0.50), fit there, re-score the test set.
   - Local models, as of 2026-10-04 (all in gitignored `third_party/`):
     - Kev cloned at `fe64b12`; `uv sync --extra serve` done. Server: `cd third_party/kev && uv run --extra serve python -m kev.serve --run jaredpalmer/kev-4b@139fdd94 --port 8009` (Kev-0.8B: `jaredpalmer/kev-0.8b@9a45d25e`, port 8010). Kev-4B 9-excerpt smoke test passed (~1.1 s per request); the full run was interrupted. Re-run: `cd experiments/01-many-option-classification && uv run run.py --model kev-4b --concurrency 4`.
     - Laya 0.3.27 in `third_party/laya/.venv`; server not started. Add `LAYA_API_KEY` to `.env`, then `LAYA_HOST=127.0.0.1 LAYA_PRELOAD=1 third_party/laya/.venv/bin/laya-serve` (port 8000).
     - GLiNER2 2.0.0 in `third_party/gliner/.venv`; bridge `local/gliner_bridge.py` (native multi-label) written, first test was downloading the model. Still to do: a `gliner` backend in `run.py` that pipes requests through the bridge, like the gateway bridge.
     - openJev Verdict: not installed (the auto-mode classifier blocked the clone; the maintainer has since approved installing it). Clone `Heman10x-NGU/Verdict-open-jev` into `third_party/`, `uv pip install -e .`, run `scripts/download_artifacts.py`, then write a bridge like GLiNER's. Max 24 options per question; Nouls are fine.
2. **Dataset viewer:** check that it renders for `decision-models-evaluation-docs`. If it still fails, open a discussion on the repo.
3. **Baselines:** decide whether to publish the earlier classifier leaderboard. The 01/02 baselines cite `evalexplorer-classify-experiments`, which is private.
4. **Experiment 02:** `planned` (approved 2026-10-02); runs after 01 phase 1, starting with the training-label pilot.

## Don't touch

- `baobabtech/evalexplorer-data` and `baobabtech/evalexplorer-classify-experiments`: another agent owns them, including the GLM labels. Read only.

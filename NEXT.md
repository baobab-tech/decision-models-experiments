# NEXT

Current state and next steps. Keep this short: delete items when done, add new ones as they come up. Last updated 2026-10-02.

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
   - Local models (Kev-4B, Kev-0.8B, Laya, GLiNER2.5-Decide, Verdict): installing them was blocked by the auto-mode permission classifier (third-party code). The maintainer needs to allow it or install them.
2. **Dataset viewer:** check that it renders for `decision-models-evaluation-docs`. If it still fails, open a discussion on the repo.
3. **Baselines:** decide whether to publish the earlier classifier leaderboard. The 01/02 baselines cite `evalexplorer-classify-experiments`, which is private.
4. **Experiment 02:** `planned` (approved 2026-10-02); runs after 01 phase 1, starting with the training-label pilot.

## Don't touch

- `baobabtech/evalexplorer-data` and `baobabtech/evalexplorer-classify-experiments`: another agent owns them, including the GLM labels. Read only.

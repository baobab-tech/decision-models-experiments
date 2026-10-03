# NEXT

Current state and next steps. Keep this short: delete items when done, add new ones as they come up. Last updated 2026-10-02.

## State

- Docs: model docs, benchmarks, governance and landscape fact-checked on 2026-09-30 and 2026-10-02.
- Dataset: [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs) is public.
  - Built by `experiments/common/build_evaluation_docs_dataset.py` from `evalexplorer-data` at `5315eab`.
  - Default labels are silver (GLM-5.3-Flash); the `*_pipeline` columns hold the pipeline labels.
- HF collection: [Decision models experiments](https://huggingface.co/collections/baobabtech/decision-models-experiments-6ac0461f242cbc19f87d4854), 32 items.
- Experiment 01 is `planned` (approved 2026-10-02): phase 1 is task B, scored against a four-LLM consensus. 02 is `planned` (approved 2026-10-02). 03 is LlamaIndex's, done.

## Next

1. **Before 01 phase 1 runs:**
   - `.env` has `HF_TOKEN`, `AI_GATEWAY_API_KEY` (Jev, d1) and `FASTINO_API_KEY` (GLiDE). Smoke-test `typesafe-ai/jev` and `liquid/d1` through the gateway with synthetic text before the run.
   - Pin providers for GLM-5.3-Flash and DeepSeek-V4.1-Flash (deepinfra: $0.20 / $0.60 per million input/output tokens for DeepSeek). Qwen3.8-Flash-Next is featherless-ai only; check its region and retention.
   - Generate GLM, DeepSeek and Qwen labels for the 600 task B excerpts, and add them to the dataset as `*_glm`, `*_deepseek`, `*_qwen` columns.
2. **Dataset viewer:** check that it renders for `decision-models-evaluation-docs`. If it still fails, open a discussion on the repo.
3. **Baselines:** decide whether to publish the earlier classifier leaderboard. The 01/02 baselines cite `evalexplorer-classify-experiments`, which is private.
4. **Experiment 02:** `planned` (approved 2026-10-02); runs after 01 phase 1, starting with the training-label pilot.

## Don't touch

- `baobabtech/evalexplorer-data` and `baobabtech/evalexplorer-classify-experiments`: another agent owns them, including the GLM labels. Read only.

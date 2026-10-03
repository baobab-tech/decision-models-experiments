# NEXT

Current state and next steps. Keep this short: delete items when done, add new ones as they come up. Last updated 2026-10-02.

## State

- Docs: model docs, benchmarks, governance and landscape fact-checked on 2026-09-30 and 2026-10-02.
- Dataset: [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs) is public.
  - Built by `experiments/common/build_evaluation_docs_dataset.py` from `evalexplorer-data` at `5315eab`.
  - Default labels are silver (GLM-5.3-Flash); the `*_pipeline` columns hold the pipeline labels.
- HF collection: [Decision models experiments](https://huggingface.co/collections/baobabtech/decision-models-experiments-6ac0461f242cbc19f87d4854), 32 items.
- Experiments 01 and 02 are `proposed` with written plans. 03 is LlamaIndex's, done.

## Next

1. **Maintainer:** approve the experiment 01 plan, then set it to `planned`. Nothing runs before that.
2. **Before 01 runs:**
   - Confirm API keys in `.env`: `TYPESAFE_API_KEY` (Jev early access), `LIQUID_API_KEY`, Fastino key for GLiDE, `HF_TOKEN`.
   - Pin a DeepSeek-V4.1-Flash provider; deepinfra is cheapest at $0.20 / $0.60 per million input/output tokens with structured output.
   - Decide the second judge. Qwen3.8-Flash-Next was not on the HF router on 2026-10-02.
3. **Dataset viewer:** check that it renders for `decision-models-evaluation-docs`. If it still fails, open a discussion on the repo.
4. **Baselines:** decide whether to publish the earlier classifier leaderboard. The 01/02 baselines cite `evalexplorer-classify-experiments`, which is private.
5. **Collection:** add models from experiment 02 when they exist.

## Don't touch

- `baobabtech/evalexplorer-data` and `baobabtech/evalexplorer-classify-experiments`: another agent owns them, including the GLM labels. Read only.

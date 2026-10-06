# NEXT

Current state and next steps. Keep this short: delete items when done, add new ones as they come up. Last updated 2026-10-06.

## State

- Docs: model docs, benchmarks, governance and landscape fact-checked on 2026-09-30 and 2026-10-02.
- Dataset: [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs) is public.
  - Built by `experiments/common/build_evaluation_docs_dataset.py` from `evalexplorer-data` at `5315eab`; current revision `bfaf706` (`taxonomy` has `definition_excerpts`; no LLM label columns yet).
  - Default labels are silver (GLM-5.3-Flash); the `*_pipeline` columns hold the pipeline labels.
- HF collection: [Decision models experiments](https://huggingface.co/collections/baobabtech/decision-models-experiments-6ac0461f242cbc19f87d4854), 32 items.
- Experiments 01 and 02 re-planned 2026-10-06 around production's context: excerpts are tagged with their section and document context, as in eval-explorer's ingestion. Excerpt-only runs were removed.
- 03 is LlamaIndex's, done.

## Next

1. **01 context pilot:** done 2026-10-06; chosen input `doc+summary` (title + Document Start + executive summary/abstract + excerpt): LLM agreement 90.2, pipeline agreement 68–69, +440 tokens.
2. **01 reference labels:** done 2026-10-06 with GLM + DeepSeek (Qwen dropped: too slow on featherless-ai). LLM range 88.8 on test; pipeline 67.5. Publish with the `llm_labels` config.
3. **01 zero-shot runs:** decision models with the chosen context (`run.py` needs context in `state`).
4. **02 first step:** label 10,000 train excerpts (GLM + DeepSeek, soft targets) with the chosen context; publish as the `llm_labels` config; sweep small encoders as HF Jobs (`train_encoder.py`).
5. **Taxonomy:** production theme definitions overlap (cash transfers, renewable energy, refugees, mediation, technology transfer each under 2–3 themes; Growth lists only trade terms; Conflict reads as humanitarian practice), and the prompt says 1–3 themes while the zod schema says 1–4. Raise with the taxonomy owner; experiments keep production's version.
6. **Dataset viewer:** check that it renders for `decision-models-evaluation-docs`.
7. **Baselines:** decide whether to publish the earlier classifier leaderboard; `evalexplorer-classify-experiments` is private.

## Don't touch

- `baobabtech/evalexplorer-data` and `baobabtech/evalexplorer-classify-experiments`: another agent owns them, including the GLM labels. Read only.

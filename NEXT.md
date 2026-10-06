# NEXT

Current state and next steps. Keep this short: delete items when done, add new ones as they come up. Last updated 2026-10-06.

## State

- Docs: model docs, benchmarks, governance and landscape fact-checked on 2026-09-30 and 2026-10-02.
- Dataset: [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs) is public.
  - Built by `experiments/common/build_evaluation_docs_dataset.py` from `evalexplorer-data` at `5315eab`; `fcd40f8` added `definition_excerpts` to `taxonomy`; `5017706` adds the LLM label columns and `<field>_majority` for `eval_sample`.
  - Default labels are silver (GLM-5.3-Flash); the `*_pipeline` columns hold the pipeline labels.
- HF collection: [Decision models experiments](https://huggingface.co/collections/baobabtech/decision-models-experiments-6ac0461f242cbc19f87d4854), 32 items.
- Experiment 01 phase 1 done (2026-10-06): no zero-shot decision model reaches the LLM range (84.2–85.0). Jev 71.0, GLiDE 52.4, d1 39.5, GLiNER2.5-Decide 19.1, Laya 17.5 at p ≥ 0.5. Threshold fitting lifts d1 and GLiDE by 6–17 points. Phase 2 not run.
- Experiment 02 is the main experiment: smallest fine-tuned model, by compute per excerpt, that reaches the LLM range. 03 is LlamaIndex's, done.

## Next

1. **Experiment 02, first step** ([plan](experiments/02-fine-tuning/README.md#first-step)):
   - Labelling 10,000 train excerpts with GLM and DeepSeek (started 2026-10-06, detached processes; resume with `uv run experiments/common/label_excerpts.py --model glm --split train`). Qwen dropped for training labels (~17 h on featherless-ai); targets are soft (1 / 0.5 / 0).
   - Fine-tune ModernBERT-base (one sigmoid head per field) and GLiNER2.5-Decide on the soft labels; score on 01's test sample (3-LLM majority); report compute per excerpt.
2. **Taxonomy:** production theme definitions overlap (cash transfers, renewable energy, refugees, mediation, technology transfer each under 2–3 themes; Growth lists only trade terms; Conflict reads as humanitarian practice), and the prompt says 1–3 themes while the zod schema says 1–4. Raise with the taxonomy owner; experiments keep production's version.
3. **Experiment 01 leftovers (optional):** Kev-4B, Kev-0.8B and Verdict zero-shot runs did not finish (2-hour background limit while sharing the Mac). Re-run one at a time if wanted; make `run.py` save responses as it goes first. Servers and environments are in `third_party/` (gitignored).
4. **Dataset:** add the 300 validation-sample LLM labels (`results/labels/excerpts_*_validation.jsonl`) to `decision-models-evaluation-docs`, and the 10,000 train labels when they exist.
5. **Dataset viewer:** check that it renders for `decision-models-evaluation-docs`. If it still fails, open a discussion on the repo.
6. **Baselines:** decide whether to publish the earlier classifier leaderboard; `evalexplorer-classify-experiments` is private.

## Don't touch

- `baobabtech/evalexplorer-data` and `baobabtech/evalexplorer-classify-experiments`: another agent owns them, including the GLM labels. Read only.

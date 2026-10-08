# NEXT

Current state and next steps. Keep this short: delete items when done, add new ones as they come up. Last updated 2026-10-08.

## State

This repo is closed as a decision-models study:
- **01 (zero-shot decision models, excerpt tagging):** done.
- **02 (fine-tuned small encoders and a decision-model backbone):** done.

Conclusions are in each README, in the root README "Findings so far", and in `experiments/README.md` "The story".

EvalExplorer production work moved to the `eval-explorer-fine-tune` repo (private):
- The excerpt-extraction plan (04) was copied to `eval-explorer-fine-tune/04-excerpt-extraction/`. An agent in that repo merges it.
- New EvalExplorer experiments go there, not here.

## Open items

1. **Country-lookup donor bug.** It's documented as a limitation in the 02 conclusion and not fixed. The proposed rule: keep a lookup country only if the excerpt names it, or if its region is outside northern, southern and western Europe, northern America, and Australia/NZ. Test result: countries 72.3 → 78.4. If adopted, change `common/country_lookup.py` and the copy in `train_encoder.py`, then re-score 01 (`fit.py`) and 02 (`score_per_label.py`).
2. **Hand over to the EvalExplorer repo** (these are findings about production, not about decision models):
   - Taxonomy note for the owner:
     - Theme definitions overlap: cash transfers, renewable energy, refugees, mediation and technology transfer each appear under 2–3 themes. Growth lists only trade. Conflict reads as humanitarian practice.
     - Per-label LLM agreement backs this: science_technology F1 6, global_partnerships 36, multilateral 40.
     - The prompt says 1–3 themes; the zod schema allows 1–4.
     - The document-level theme list has `international_finance`; the excerpt list does not.
     - The region list includes `antarctica`, which the repair prompt treats as invalid.
   - Production facts found in code (2026-10-08):
     - Excerpt extraction defaults to `gemini-2.5-flash` (`MODEL` env), not gpt-oss-120b.
     - Methodology excerpts are not checked against the source.
     - No character offsets are stored.
   - Reusable code from this repo: `experiments/common/per_label.py` (per-label F1, LLM-vs-LLM agreement, macro with bootstrap CI), `02-fine-tuning/train_encoder.py`, `predict_saved.py`, `score_per_label.py`.
3. **Housekeeping:**
   - Dataset viewer for `decision-models-evaluation-docs`.
   - Decide whether to publish the fine-tuned tagger repos (`baobabtech/evaldocs-excerpt-tagger-*`, private).
   - Decide on publishing the earlier classifier leaderboard (`evalexplorer-classify-experiments`, private).

## Key files

- `experiments/01-many-option-classification/`: `README.md` (plan + results), `run.py`, `score.py`, `fit.py` (one threshold; with and without lookup), `zeroshot_job.py` (HF Job for local models), `gateway/evaluate.mjs` (Jev/d1).
- `experiments/02-fine-tuning/`:
  - `README.md`
  - `train_encoder.py` (HF Jobs uv script; saves `probs.npz` from 2026-10-08)
  - `sweep.sh` (`REV=... [TIMEOUT=6h] ./sweep.sh`)
  - `predict_saved.py`, `score_per_label.py`, `plot_learning_curve.py`, `select_balanced.py`
  - `results/` (`sweep_summary.json` for sweep 1, `sweep2_summary.json`, `per_label/`, `learning_curve.png`; `probs/` is gitignored)
- `experiments/common/`: `label_excerpts.py`, `context.py`, `country_lookup.py`, `per_label.py`, `build_llm_labels.py`, `prompts/excerpt-tagging.md`.

## Operational notes

- **HF tokens:** the `HF_TOKEN` in `.env` cannot see baobabtech private repos or create jobs there. Don't source `.env` before `hf` or Hub calls; the CLI login works.
- **HF Jobs:** `hf jobs uv run --flavor a10g-small --namespace baobabtech --secrets HF_TOKEN --detach ...`. Job label values may only contain `[a-zA-Z0-9_-]`. The job ID is in the `Job started with ID:` line.
- **transformers 5.x** loads checkpoints in their stored dtype. `train_encoder.py` forces fp32 weights.
- `.env` has `HF_TOKEN`, `AI_GATEWAY_API_KEY`, `FASTINO_API_KEY` and `LAYA_API_KEY`. Never print them.
- **Costs** (approx.): LLM labels ~$20; Jev/d1 runs ~$5; GLiDE $4.64; HF Jobs a few dollars per sweep.

## Leave out of published docs

Internal iteration: the excerpt-only round, Qwen3.8-Flash-Next, job failures (OOM, label errors, bf16), per-field threshold experiments.

## Don't touch

- `baobabtech/evalexplorer-data` and `baobabtech/evalexplorer-classify-experiments`: another agent owns them. Read only.

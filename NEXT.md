# NEXT

Current state and next steps. Keep this short: delete items when done, add new ones as they come up. Last updated 2026-10-08.

## Goal

Can a small model tag evaluation-report excerpts as well as the LLM in EvalExplorer's ingestion, at a fraction of the compute? Fields: themes (22), regions (17), countries (198), methods (24). We judge on accuracy **and** compute per excerpt (environmental impact). The publishable story outline is in `experiments/README.md` ("The story so far").

## Method, as settled

- **Input = production context** (`doc_summary`): excerpt, then the report's title, first 100 words, and executive summary and abstract (each cut to 1,500 characters). Chosen by a 50-excerpt pilot (01 README, "Pilot result"). Built by `experiments/common/context.py` from `baobabtech/evalexplorer-data` (private, read only).
- **Reference = two LLMs**, GLM-5.3-Flash and DeepSeek-V4.1-Flash (HF Inference Providers on deepinfra, billed to `baobabtech`). No human gold set. Score = mean micro-F1 against each LLM; **LLM range = 88.8** on test (GLM vs DeepSeek). Pipeline labels score 67.5.
- **Taxonomy and definitions = production's** (eval-explorer `ingestion-pipeline/lib/extract/`, same on `main` and `staging`).
- **Countries:** a country-name lookup (`experiments/common/country_lookup.py`; copy inside `train_encoder.py`) scores 71.6 countries / 74.7 regions with no model. Models tag themes, regions and methods; countries come from the lookup ("hybrid").
- **Data:** public dataset `baobabtech/decision-models-evaluation-docs`, config `llm_labels`, revision `e191ae3`: test 600, validation 300, train 28,664 (9,998 random + 18,666 balanced, column `sample`). All real excerpts, LLM-labelled; no synthetic text.

## Results so far

- **01 zero-shot (with context, threshold fitted on validation, lookup countries):** Jev 72.5, d1 69.0. GLiDE skipped (~$40 with context).
- **02 sweep 1** (5 epochs, lr 5e-5 for all, random 10k data; `experiments/02-fine-tuning/results/sweep_summary.json`): best Ettin-150M + lookup 75.3, Ettin-32M + lookup 74.7. Dropping the country outputs raised themes from 70 to 81. These numbers are in the 02 README.

## Do next

1. **Collect sweep 2** (per-model recipes, fp32 weights, lookup countries, random + balanced data; job ids in `experiments/02-fine-tuning/results/jobs_sweep2.tsv`). All completed except NeoMME and harrier, which hit the 3 h job timeout after epoch 8 (validation 78.3 and 78.5). Read `metrics.json` from each private repo `baobabtech/evaldocs-excerpt-tagger-<encoder>-llm-nocountries-lookup[...]`, e.g.:
   ```python
   from huggingface_hub import HfApi, hf_hub_download
   repos = [m.id for m in HfApi().list_models(author="baobabtech", search="evaldocs-excerpt-tagger")]
   ```
   Note: sweep 2's Ettin lookup repos overwrote sweep 1's (old numbers kept in `sweep_summary.json`).
2. **Rerun NeoMME and harrier** with `--timeout 6h` (edit `sweep.sh` `run()` or launch the two lines by hand; `REV=e191ae3f5665781f5e1a1ca9a68d035c1868a2b4`).
3. **Learning curve:** Ettin-32M on 1,000 / 2,500 / 5,000 / 10,000 random excerpts plus the full run on random + balanced are done; plot score vs training size (the answer to "how much data").
4. **Score the zero-shot open models:** responses for GLiNER2.5-Decide, Laya, Verdict, Kev-0.8B and Kev-4B are in the private dataset `baobabtech/decision-models-zeroshot-runs` (`<model>/<split>/responses.jsonl`). Download each into `experiments/01-many-option-classification/results/raw/<model>-definitions-excerpts-<YYYYMMDDTHHMM>/responses.jsonl` (test) and `<model>-definitions-excerpts-val-<...>/responses.jsonl` (validation), then `cd experiments/01-many-option-classification && uv run fit.py --model <model>`. Add a row per model to the 01 README "Zero-shot decision models" table.
5. **Write up:** 02 README results for sweep 2 (table with params, tokens per excerpt, mean, per-field), the learning curve, and update `experiments/README.md` story steps 5–7 (what to deploy). Keep internal iteration out (see below).
6. **Two-tower + lookup:** two-tower Ettin-150M in sweep 2 is done; compare with joint (sweep 1 gap was 6.3 points for ~6× less compute per excerpt).
7. **Taxonomy note for the owner:** production theme definitions overlap (cash transfers, renewable energy, refugees, mediation, technology transfer under 2–3 themes; Growth lists only trade; Conflict reads as humanitarian practice); prompt says 1–3 themes, zod schema says 1–4.
8. Housekeeping: dataset viewer for `decision-models-evaluation-docs`; decide on publishing the earlier classifier leaderboard (`evalexplorer-classify-experiments`, private).

## Key files

- `experiments/01-many-option-classification/`: `README.md` (plan + results), `run.py` (decision-model runner; `--export` writes requests), `score.py`, `fit.py` (one threshold; with and without lookup), `zeroshot_job.py` (HF Job for local models), `context_pilot.py`, `gateway/evaluate.mjs` (Jev/d1 via Vercel AI Gateway), `results/labels/` (LLM label records).
- `experiments/02-fine-tuning/`: `README.md`, `train_encoder.py` (HF Jobs uv script; `RECIPES` per model; `--exclude-fields countries --country-lookup`; `--arch two_tower`; `--train-sample`, `--limit-train`), `sweep.sh` (sweep 2; `REV=... ./sweep.sh`), `select_balanced.py`, `results/`.
- `experiments/common/`: `label_excerpts.py` (LLM labelling; `--split test|validation|train|train_extra`), `context.py`, `country_lookup.py`, `build_llm_labels.py` (publishes `llm_labels`), `prompts/excerpt-tagging.md`.
- `third_party/` (gitignored): local installs of Kev, Laya, GLiNER2, Verdict. Not needed now that local models run as HF Jobs.

## Operational notes

- HF Jobs: `hf jobs uv run --flavor a10g-small --namespace baobabtech --secrets HF_TOKEN --detach ...`; job label values only `[a-zA-Z0-9_-]`. 230–270M encoders on the full data need > 3 h.
- transformers 5.x loads checkpoints in their stored dtype; `train_encoder.py` forces fp32 weights (bf16/fp16 checkpoints otherwise fail to train).
- Background waits: never `pgrep -f` a pattern that appears in the waiting command itself; check files or job status instead. zsh does not split unquoted variables; use `bash -c` for loops over ids.
- `.env` has `HF_TOKEN`, `AI_GATEWAY_API_KEY`, `FASTINO_API_KEY`, `LAYA_API_KEY`. Never print them.
- Costs so far (approx.): LLM labels ~$20; Jev/d1 runs ~$5; GLiDE (excerpt-only, removed) $4.64; HF Jobs a few dollars per sweep.

## Leave out of published docs

Internal iteration: the excerpt-only round, Qwen3.8-Flash-Next (too slow on featherless-ai), job failures (OOM, label errors, bf16), per-field threshold experiments. Keep method details as one-liners.

## Don't touch

- `baobabtech/evalexplorer-data` and `baobabtech/evalexplorer-classify-experiments`: another agent owns them, including the GLM labels. Read only.

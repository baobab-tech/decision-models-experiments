# 01 Many-option classification

**Status:** planned. Plan approved 2026-10-02; phase 1 (task B) runs first.

## Question

Can zero-shot decision models classify and tag international development evaluation reports as well as LLMs, at 3 to 250 labels, on ~50-token excerpts and ~2,000-token first pages?

## What it informs

- **Ingestion:** whether a decision model can replace the LLM step that classifies and tags reports in the EvalExplorer ingestion pipeline, at lower cost or latency.
- **Public write-up:** a benchmark of decision models on a real many-option task, for outside readers.
- Each phase also records, per model: what fine-tuning would take, limitations, opportunities and further work (see [Write-up](#write-up)).

## Phases

1. **Task B, excerpt tagging.** Excerpts are short, so every model fits, including Laya (512-token context). Cheap and fast to run.
2. **Task A, document classification.** Planned after phase 1 results are written up; the maintainer decides whether it runs.

## Data

1,420 public international development evaluation reports: [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs) (public); see [common/datasets.md](../common/datasets.md). Test splits only, split by document.

| Task | Input | n | Field | Labels | Type |
|---|---|---|---|---:|---|
| **B. Excerpt tagging** (phase 1) | Finding, recommendation or methodology excerpt: median 34 words, p90 107 | 600: `eval_sample` (300 findings, 150 recommendations, 150 methodology) | `themes` (findings, recommendations) | 22 | multi, median 2 |
| | | | `regions` (findings, recommendations) | 17 | multi |
| | | | `methods` (methodology only) | 24 | multi |
| | | | `countries` (findings, recommendations) | 121 seen; ~250 ISO codes | multi |
| **A. Document classification** (phase 2) | First pages: median 1,935 tokens, p99 5,267 | 134 docs | `evaluation_approach` | 6 | single |
| | | | `evaluation_type` | 4 | single |
| | | | `temporality` | 3 | single |
| | | | `themes` | 18 | multi, 1–4 |
| | | | `countries` | 54 seen; ~250 ISO codes | multi |

Option counts come from the real taxonomy. `countries` is the 100+ case: ask over the codes seen, and over all ~250 ISO codes.

## Reference labels

There is no human gold set. No person labelled the test items, and no decision model is checked against human answers. The reference is the agreement of three LLMs, so every score here measures **agreement with LLMs, not correctness**. A decision model that beats the LLMs on a label they all get wrong scores lower, not higher. The only human check is the 36 hand-corrected documents in task A.

| Label set | Input | Task B (excerpts) | Task A (documents) |
|---|---|---|---|
| GLM-5.3-Flash | excerpt alone | generated 2026-10-03 | in dataset (default columns) |
| DeepSeek-V4.1-Flash | excerpt alone | generated 2026-10-03 | to generate |
| Qwen3.8-Flash-Next | excerpt alone | generated 2026-10-03 | to generate |
| Pipeline (gpt-oss-120b; fallbacks Gemini 2.5 Flash, Qwen 3 235B) | whole section, tagged while extracting | in dataset | in dataset (`*_pipeline`; 36 corrected by hand) |

- The reference sets are GLM, DeepSeek and Qwen. They see the same input as the decision models.
- The pipeline is not a reference. It saw the whole section, and on task B it agrees with the other three at 51.8–54.0 against their 83.5–85.1 with each other ([results](#phase-1-reference-labels)). Its scores are reported as a separate comparison.
- Generated sets use classify-only prompts rebuilt from the pipeline's extract-and-classify prompts ([common/prompts/excerpt-tagging.md](../common/prompts/excerpt-tagging.md)), temperature 0, through HF Inference Providers billed to `baobabtech` ([common/README.md](../common/README.md#hf-inference-providers)), with the provider pinned: GLM and DeepSeek on deepinfra, Qwen on featherless-ai.
- Qwen3.8-Flash-Next is a reasoning model. It returned empty `content` with `response_format: json_schema` (2 of 2 calls, 2026-10-02), so the JSON format goes in the prompt, and `max_tokens` is 16,384.
- The generated sets are in the dataset as `<field>_glm`, `<field>_deepseek`, `<field>_qwen`, with the reference as `<field>_majority` (revision `5017706`). Per-call records: [results/labels/](results/labels/).

Scoring:

- **Reference:** labels chosen by at least 2 of the 3 LLMs. For a single-label field with no majority, the item is excluded from that field.
- **LLM range:** each LLM's mean agreement with the other two. A decision model is also scored against each LLM separately and averaged, so its score compares directly with the range.
- Decision models get both scores: against the majority reference (headline), and the mean against each LLM (for the range).
- Scores against the pipeline labels are reported too, for comparison with the earlier classifier runs.

## Models

| Model | Where | Why |
|---|---|---|
| [Jev](../../docs/models/jev.md) | Vercel AI Gateway (`typesafe-ai/jev`) | Reference model; 255 options |
| [Liquid d1](../../docs/models/liquid-d1.md) | Vercel AI Gateway (`liquid/d1`) | Vendor-reported Decision Index leader |
| [GLiDE](../../docs/models/glide.md) | Fastino API | 255 options; 40k tokens per question |
| [GLiNER2.5-Decide](../../docs/models/gliner-decide.md) | This Mac | Only model with native multi-label; earlier zero-shot runs used GLiNER2.5 small/base |
| [Kev-4B](../../docs/models/kev.md) | This Mac (MLX) | Open, Jev-compatible, 255 options |
| [Kev-0.8B](../../docs/models/kev.md) | This Mac (MLX) | Zero-shot score for 02's size comparison |
| [openJev Verdict](../../docs/models/rlcd-modernbert.md) | This Mac (MPS) | Zero-shot score for 02; 151M encoder; max 24 options, so Noul-per-label only for fields above 24 |
| [Laya](../../docs/models/laya.md) | This Mac | Small encoder; context 512 (en), so task A only after chunking |

- Jev and d1 use `AI_GATEWAY_API_KEY`. The gateway documents only the AI SDK `experimental_evaluate` path (TypeScript), so their client is Node 22.
- GLiNER2.5-Decide, Kev and Laya have no HF Inference Providers mapping (checked 2026-10-02), so they run locally, as does Verdict.

## Question formats

- Single-label fields: one Choice.
- Multi-label fields: one Noul per label in one request, thresholded at 0.5. GLiNER2.5-Decide also uses its native multi-label mode.
- `countries`: flat Choice/Noul over all codes vs staged (region first, then countries within it).
- Label names only vs names with one-line definitions (the `definitions` prompt variant from the classify experiments).

## Null answers (phase 2)

`evaluation_approach`, `evaluation_type` and `temporality` can be `null`. A Choice always returns one of its options, so `null` comes from one of two methods, and we test both:

1. **Threshold:** the field is `null` when the top option's probability is below a threshold *t*.
2. **Gate:** a Noul asks whether the report states the field (e.g. "The report states its evaluation approach"). The field is `null` when the Noul is below a threshold *g*; otherwise the Choice answer is used.

Calibrating the thresholds:

- *t* and *g* are fitted per model and per field on the validation split (138 documents), then frozen for the test split.
- The objective is field accuracy with `null` counted as its own class.
- Grid: 0.05 to 0.95 in steps of 0.05. Ties go to the higher threshold, which gives fewer `null`s.
- Reported for each field:
  - the fitted threshold
  - the `null` precision and recall on test
  - the accuracy curve across thresholds on validation, so we can see whether a plateau or a sharp peak drove the choice
- 138 validation documents give a coarse fit, especially for rare `null`s, so the 95% bootstrap interval of the test accuracy is reported. If the interval is wide, the fit is repeated with 5-fold cross-validation over train + validation.
- A third run with no `null` handling, where the Choice is always taken, shows what each method adds.

## Baselines

- **The three reference LLMs**, as the LLM range above.
- **The pipeline labels**, scored against the majority reference.
- **Embeddings + logistic regression** trained on the train split, for task B.
- **Earlier Baobab Tech classifier runs** on the task A test split (phase 2; not re-run; results in `baobabtech/evalexplorer-classify-experiments`, private):

  | Model | Zero-shot vs GLM | After SFT vs GLM | After SFT vs pipeline |
  |---|---:|---:|---:|
  | Gemma 4 26B-A4B | 72.9 | 80.3 | 84.4 |
  | Qwen3.5-4B | 66.2 | 77.8 | 84.7 |
  | Gemma 4 E4B | 72.1 | 76.8 | 83.0 |
  | GLiNER2.5 base | 45.2 | 57.2 | 58.4 |

  The SFT models were trained on pipeline labels. Pipeline and GLM agree at 76.2 on test.

## Metrics

From [common/metrics.md](../common/metrics.md):

- **Main score:** `mean_field_score`, the mean of per-field accuracy and F1.
- **Per field:** `accuracy` for single-label fields; `micro_f1` and `macro_f1` for multi-label fields.
- **Calibration:** `ece_15`, `brier`, `coverage_at_5`.
- **Speed and cost:** `latency_p50_ms` and `p95`, `cost_per_1k`, `tokens_per_request`. LLM labelling cost and latency are recorded too, as the ingestion comparison.

## Results

### Phase 1: reference labels

Run 2026-10-03 on the 600 `eval_sample` excerpts, dataset revision `fcd40f8`. Fields: `themes`, `regions` and `countries` on 450 findings and recommendations; `methods` on 150 methodology excerpts. Scores are micro-F1 × 100; the mean is over the four fields.

LLM range (each LLM's mean agreement with the other two):

| LLM | Provider | Themes | Regions | Countries | Methods | Mean |
|---|---|---:|---:|---:|---:|---:|
| GLM-5.3-Flash | deepinfra | 79.7 | 85.6 | 86.7 | 84.9 | 84.2 |
| DeepSeek-V4.1-Flash | deepinfra | 80.9 | 85.1 | 89.2 | 82.0 | 84.3 |
| Qwen3.8-Flash-Next | featherless-ai | 81.2 | 86.3 | 87.9 | 84.5 | 85.0 |

Pipeline labels against the majority reference: themes 67.3, regions 44.3, countries 45.6, methods 54.2; mean 52.8.

Labels per excerpt:

| | Themes | Regions | Countries | Methods |
|---|---:|---:|---:|---:|
| Pipeline | 2.37 | 0.60 | 0.68 | 1.06 |
| GLM / DeepSeek / Qwen | 1.36 / 1.62 / 1.62 | 0.24 / 0.20 / 0.21 | 0.30 / 0.24 / 0.25 | 0.55 / 0.43 / 0.55 |
| Majority reference | 1.48 | 0.21 | 0.25 | 0.51 |

- All three LLMs agree on 75% of the majority's theme and method labels, 82% of region labels and 88% of country labels.
- The pipeline tags 2–3 times more regions and countries. In a 9-excerpt pilot, 3 of its 6 country tags on findings and recommendations named a country absent from the excerpt (Tanzania, Syria, Pakistan), which fits its section-level input.
- Calls: 600 per model, no errors or truncations after retries. GLM 0.86M tokens (p50 3.8 s); DeepSeek 0.84M (p50 1.4 s); Qwen 1.09M, including 216k reasoning tokens (p50 7 s; up to 6,906 output tokens).
- Two codes outside the label lists were dropped: one DeepSeek, one Qwen.

## Write-up

Results go in this README per phase. Besides scores, each phase records per model:

- **Fine-tuning:** whether it can be fine-tuned (open weights, vendor service or neither), the data format, the hardware and time it would take, and what experiment [02](../02-fine-tuning/) should test.
- **Limitations:** option and context caps, multi-label handling, failure modes seen in errors.
- **Opportunities:** fields or excerpt types where it matches the LLMs.
- **Further work:** follow-up experiments, added to [../README.md](../README.md) as `proposed`.

## Data governance

- Local models run on this Mac.
- These models send document text to third parties:
  - Jev via Vercel AI Gateway: served by `digitalocean`; no ZDR; no training on inputs (`has_no_training: true`); no EU region.
  - d1 via Vercel AI Gateway: served by `liquid`; no ZDR; Liquid's terms let it use inputs to improve its models; no EU region.
  - GLiDE: Fastino API, US.
  - GLM-5.3-Flash, DeepSeek-V4.1-Flash and Qwen3.8-Flash-Next via HF Inference Providers: the region depends on the provider; record the pinned provider and its region.
- The reports and dataset are public; the maintainer approved sending them to these APIs (2026-10-02).

## What would change a decision

- **Replace the LLM in ingestion:** on both tasks, a decision model scores within the LLM range, or within 3 points of its lowest score, at lower cost or latency.
- **Use one for excerpt tagging only:** it reaches the LLM range on task B but not task A, which points to input length as the limit.
- **Keep LLMs, try fine-tuning:** every decision model stays below the LLM range; experiment 02 tests whether fine-tuning closes the gap.

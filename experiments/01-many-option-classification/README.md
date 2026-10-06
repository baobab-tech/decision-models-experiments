# 01 Many-option classification

**Status:** running. Context pilot and reference labels done (2026-10-06); model runs next.

## Question

Can decision models and small encoders tag and classify international development evaluation reports as well as LLMs, with the context the production ingestion pipeline uses, at 3 to 250 labels?

## What it informs

- **Ingestion:** whether a smaller model can replace the LLM step that tags excerpts and classifies reports in the EvalExplorer ingestion pipeline, at a fraction of the compute per item.
- **Public write-up:** a benchmark of decision models on a real many-option task.
- Each phase records, per model: what fine-tuning would take, limitations, opportunities and further work (see [Write-up](#write-up)).

## Phases

1. **Task B, excerpt tagging.** Starts with a [context pilot](#context-pilot).
2. **Task A, document classification.** After phase 1 is written up; the maintainer decides whether it runs.

## Input: what production sees

Excerpts are tagged in context. In production ([eval-explorer](https://github.com/baobab-tech/eval-explorer) `ingestion-pipeline/lib/extract/extraction.ts` and `processor-extract.ts`, identical on `main` and `staging`, checked 2026-10-06), one LLM call per section chunk extracts and tags excerpts. The call sees:

- **Main section:** the section chunk ("window") the excerpt comes from, under its section heading. Windows: median 7,481 characters, p90 12,736.
- **Context sections**, up to 3, each cut to 1,500 characters: "Document Start" (the report's first 100 words, usually the title page), then the first two other sections in document order (often Abstract, Executive Summary or Introduction).

The source data, [`baobabtech/evalexplorer-data`](https://huggingface.co/datasets/baobabtech/evalexplorer-data) revision `5315eab`, has the pieces to rebuild it:

- the excerpt's window (`excerpts.window_id` → `windows.text`), with the excerpt located by its character offsets;
- `documents.title` and `first_pages`;
- `executive_summary_section` (45% of documents) and `abstract_section` (39%). Production takes the first two sections in document order, which the source data does not store; these two are the closest available;
- `summary_doc`, a 300–500-word summary the pipeline writes after extraction (100% of documents). Production's tagging call does not see it.

## Context pilot

Which context gives the best tags for the least input? Run on 50 random test excerpts (seed 0; findings, recommendations and methodology in proportion) before labelling the full samples.

| Variant | Input | Approx. tokens |
|---|---|---:|
| `excerpt` | the excerpt alone (control) | ~60 |
| `doc` | excerpt + title + Document Start (first 100 words) | ~250 |
| `doc+summary` | `doc` + executive summary or abstract (≤ 1,500 characters) | ~650 |
| `production` | excerpt marked inside its window + Document Start + executive summary and abstract (≤ 1,500 characters each) | ~2,500 |
| `summary_doc` | `doc` + `summary_doc` | ~900 |

- Labellers: GLM-5.3-Flash and DeepSeek-V4.1-Flash.
- Reported per variant: agreement between the two LLMs, agreement of each with the pipeline labels (production's own tags, made with section context), labels per excerpt, and input tokens.
- A sample of disagreements is read by hand to see which variant gets geography and themes right.
- The chosen variant must also work for a small encoder or classifier: one input sequence of context plus the marked excerpt, with outputs that tag only the excerpt. It has to fit the encoder's window (at least 8,192 tokens; DeBERTa-v3 (512) and NeoBERT (4,096) are excluded) at an acceptable compute per excerpt. Document-level blocks are the same for every excerpt of a report, so they can be encoded once per document; the window is not.
- The variant with the best agreement per input token, within those limits, becomes the input for the reference labels, the decision models and the training data in [02](../02-fine-tuning/).

### Pilot result

Run 2026-10-06 on 50 random test excerpts (seed 0: 25 findings, 10 recommendations, 15 methodology; [context_pilot.py](context_pilot.py), [summary](results/context_pilot/summary.json)). Micro-F1 × 100, mean over fields. Input tokens include the ~1,350-token system prompt.

| Variant | Input tokens | GLM vs DeepSeek | vs pipeline (GLM / DeepSeek) | Countries per excerpt (GLM) |
|---|---:|---:|---:|---:|
| `excerpt` | 1,351 | 86.1 | 44.3 / 44.5 | 0.29 |
| `doc` | 1,532 | 87.0 | 67.3 / 68.5 | 0.83 |
| **`doc+summary`** | **1,787** | **90.2** | **67.8 / 69.3** | 0.83 |
| `production` | 3,608 | 74.2 | 64.3 / 62.3 | 1.06 |
| `summary_doc` | 2,127 | 87.0 | 58.9 / 56.2 | 1.43 |

- Document context drives agreement with the pipeline: title and Document Start alone raise it from 44 to 68. Countries and regions are mostly a property of the report.
- The whole section window lowers LLM agreement, mostly on countries (68.8): sections list many countries, and the two LLMs tag different subsets. In 6 hand-read cases, `doc+summary` gave both LLMs the same countries where `production` gave 0–7 different ones.
- **Chosen input: `doc+summary`** (title, Document Start, executive summary and abstract cut to 1,500 characters each, then the excerpt). It adds ~440 tokens of document-level context that every excerpt of a report shares.
- 50 excerpts (15 methodology) give noisy per-field numbers; the ranking is clear.

## Data

1,420 public international development evaluation reports: [`baobabtech/decision-models-evaluation-docs`](https://huggingface.co/datasets/baobabtech/decision-models-evaluation-docs); see [common/datasets.md](../common/datasets.md). Split by document.

| Task | Unit | n (test) | Field | Labels | Type |
|---|---|---|---|---:|---|
| **B. Excerpt tagging** (phase 1) | Finding, recommendation or methodology excerpt (median 34 words) in its context | 600: `eval_sample` (300 findings, 150 recommendations, 150 methodology) | `themes` (findings, recommendations) | 22 | multi |
| | | | `regions` (findings, recommendations) | 17 | multi |
| | | | `countries` (findings, recommendations) | 198 seen in excerpts; 250 ISO codes | multi |
| | | | `methods` (methodology) | 24 | multi |
| **A. Document classification** (phase 2) | First pages: median 1,935 tokens | 134 docs | `evaluation_approach` | 6 | single |
| | | | `evaluation_type` | 4 | single |
| | | | `temporality` | 3 | single |
| | | | `themes` | 18 | multi |
| | | | `countries` | 54 seen; ~250 ISO codes | multi |

- A 300-excerpt validation sample (150 findings, 75 recommendations, 75 methodology, seed 0; [results/labels/validation_sample.json](results/labels/validation_sample.json)) is used to fit thresholds.
- Labels, names and definitions are production's: `ingestion-pipeline/lib/extract/prompts.ts` and `definitions_themes.json` ([prompts](../common/prompts/excerpt-tagging.md)).

## Reference labels

No human gold set exists beyond 36 hand-corrected documents (task A). The reference is two LLMs' labels, so scores measure **agreement with LLMs, not correctness**.

- GLM-5.3-Flash and DeepSeek-V4.1-Flash tag each test and validation excerpt with the pilot's chosen context and production's classification rules ([prompts](../common/prompts/excerpt-tagging.md)), temperature 0, through HF Inference Providers on deepinfra, billed to `baobabtech` ([common/README.md](../common/README.md#hf-inference-providers)).
- **Score:** a model's mean micro-F1 against GLM and against DeepSeek.
- **LLM range:** GLM's agreement with DeepSeek. A model at that level agrees with each LLM as much as they agree with each other.
- **Pipeline labels** (gpt-oss-120b, fallbacks Gemini 2.5 Flash and Qwen 3 235B; in the dataset) are scored the same way, as a third tagger.

### Reference labels: result

Run 2026-10-06 with the `doc+summary` context ([labels](results/labels/)); GLM-5.3-Flash and DeepSeek-V4.1-Flash on deepinfra. Micro-F1 × 100.

| | Themes | Regions | Countries | Methods | Mean |
|---|---:|---:|---:|---:|---:|
| LLM range: GLM vs DeepSeek, test (600) | 82.4 | 94.9 | 89.8 | 88.1 | **88.8** |
| LLM range: GLM vs DeepSeek, validation (300) | 81.3 | 92.8 | 88.9 | 81.6 | 86.1 |
| Pipeline vs the two LLMs, test | 67.5 | 77.1 | 73.6 | 52.0 | 67.5 |

Labels per excerpt on test (GLM / DeepSeek / pipeline): themes 1.84 / 2.09 / 2.37; regions 0.78 / 0.74 / 0.60; countries 0.97 / 0.90 / 0.68; methods 0.84 / 0.78 / 1.06.

### Country lookup baseline

Countries and regions are mostly a lookup. A country-name lookup (pycountry names plus common variants; regions from the taxonomy's country → region map), with no model, scored against the two LLMs on test (2026-10-06):

| Text searched | Countries | Regions | Countries per excerpt |
|---|---:|---:|---:|
| Excerpt only | 27.8 | 24.3 | 0.15 |
| Excerpt + title + Document Start | 71.6 | 74.7 | 0.97 |
| Excerpt + all context (+ summaries) | 69.7 | 69.6 | 1.53 |
| LLM range (GLM vs DeepSeek) | 89.8 | 94.9 | 0.90–0.97 |

The gap to the LLMs is which mentioned countries count (author affiliations, donors and comparison countries are mentioned but not "substantively discussed") and region names with no country ("Sub-Saharan Africa"). Geography is lookup plus a filter; themes and methods need a model.

## Models

| Model | Where | Size |
|---|---|---|
| [Jev](../../docs/models/jev.md) | Vercel AI Gateway (`typesafe-ai/jev`, pinned to provider `typesafe-ai`) | n/d |
| [Liquid d1](../../docs/models/liquid-d1.md) | Vercel AI Gateway (`liquid/d1`) | n/d |
| [GLiDE](../../docs/models/glide.md) | Fastino API | n/d |
| [GLiNER2.5-Decide](../../docs/models/gliner-decide.md) | This Mac | 340M |
| [Kev-4B](../../docs/models/kev.md), Kev-0.8B | This Mac (MLX) | 4B, 0.8B |
| [openJev Verdict](../../docs/models/rlcd-modernbert.md) | This Mac | 151M |
| [Laya](../../docs/models/laya.md) | This Mac | 421M |

- Zero-shot, one Noul per label, with the chosen context as `state`.
- Clients: [run.py](run.py) builds requests and [score.py](score.py) scores them; [gateway/evaluate.mjs](gateway/evaluate.mjs) bridges Jev-format requests to the Vercel AI Gateway; [local/](local/) bridges GLiNER2 and Verdict. Requests are split into chunks of at most 128 questions (d1's limit) or 64 (Laya's).
- Regions: direct region Nouls ∪ regions of predicted countries (taxonomy country → region map).

## Metrics

From [common/metrics.md](../common/metrics.md):

- **Main score:** `mean_field_score`, micro-F1 per field against the reference, averaged over fields.
- **Per field:** `micro_f1`, `macro_f1`, labels per item.
- **Compute per item:** estimated as 2 × active parameters × tokens processed, next to measured tokens, latency and cost.
- Thresholds: one per model, fitted on the validation sample (grid 0.05–0.95; ties go higher), and at 0.5.

## Null answers (phase 2)

`evaluation_approach`, `evaluation_type` and `temporality` can be `null`. A Choice always returns one of its options, so `null` comes from a threshold on the top probability or from a gate Noul ("The report states its evaluation approach"). Both are fitted on the 138 validation documents and reported with `null` precision and recall.

## Write-up

Results go in this README per phase, with, per model: fine-tuning options, limitations, opportunities and further work (added to [../README.md](../README.md) as `proposed`).

## Data governance

- Local models run on this Mac.
- Text sent to third parties:
  - Jev via Vercel AI Gateway, pinned to `typesafe-ai` (TypeSafe: no training on inputs, US); no ZDR; no EU region.
  - d1 via Vercel AI Gateway, served by `liquid`; no ZDR; Liquid's terms let it use inputs to improve its models.
  - GLiDE: Fastino API, US; `/v1/systemone` rejects `store: false`.
  - GLM and DeepSeek via HF Inference Providers on deepinfra.
- The reports are public; the maintainer approved sending them to these APIs (2026-10-02).

## What would change a decision

- **Replace the LLM in ingestion:** a model scores within the LLM range at a fraction of the LLM's compute per item.
- **Fine-tune instead:** no zero-shot model reaches the range; experiment [02](../02-fine-tuning/) tests fine-tuned small models on the same input.

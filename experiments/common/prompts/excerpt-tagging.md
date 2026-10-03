# Excerpt tagging prompts

Classify-only prompts for relabelling task B excerpts with GLM-5.3-Flash, DeepSeek-V4.1-Flash and Qwen3.8-Flash-Next (experiments [01](../../01-many-option-classification/) and [02](../../02-fine-tuning/)).

## Source

- The pipeline had no separate tagging prompt. It extracted and tagged excerpts in one call per document section: `EXTRACT_AND_CLASSIFY_FINDINGS_PROMPT` and `EXTRACT_AND_CLASSIFY_METHODOLOGY_PROMPT` in `ingestion-pipeline/lib/extract/prompts.ts` of [baobab-tech/eval-explorer](https://github.com/baobab-tech/eval-explorer), commit `6ae90f7` (2026-07-29).
- Pipeline model: `openai/gpt-oss-120b`, with fallbacks `google/gemini-2.5-flash` and `alibaba/qwen-3-235b`, via Vercel AI Gateway (`ingestion-pipeline/lib/config.ts`).
- The prompts below keep the pipeline's taxonomy text and classification rules word for word, and drop the extraction instructions.

## Differences from the pipeline

- **Input:** the excerpt alone, the same input the decision models get. The pipeline saw the whole section plus context sections, so its labels can include countries or regions named only in that context.
- **Output:** tags for one given excerpt. The JSON format is in the prompt, because Qwen3.8-Flash-Next returned empty `content` with `response_format: json_schema`.
- **Label lists and definitions** come from the dataset's `taxonomy` config (`definition_excerpts` for themes and methods), filtered to `in_excerpts`, so every model is asked over the same codes.

## Findings and recommendations

Fields: `themes`, `regions`, `countries`. `{themes}` is one line per code, formatted as in the pipeline: ``- `code` (Label): definition``. `{regions}` is the comma-separated, backticked region codes.

System:

````
You are an expert evaluator classifying excerpts from evaluation documents.

## Task

Classify the excerpt below by themes, regions and countries.

## Themes (select 1 to 3 maximum per excerpt)

{themes}

## Geography

### Regions
{regions}

### Countries
Use ISO 3166-1 alpha-2 codes (2-letter codes). Examples: GB, KE, US, IN, BD

## Classification Rules

1. Assign 1 to 3 themes per excerpt based on content
2. Include regions and countries substantively discussed (not passing mentions)
3. Leave arrays empty if cannot be determined

## Output Format

Return only a JSON object:
```json
{"themes": ["theme_code"], "regions": ["region_code"], "countries": ["XX"]}
```
````

User:

```
Excerpt type: {type}

<excerpt>
{text}
</excerpt>
```

## Methodology

Field: `methods`. `{methods}` is one line per code: ``- `code` - description``.

System:

````
You are an expert evaluator classifying methodology excerpts from evaluation documents.

## Task

Classify the methodology excerpt below with the research methods used.

## Methods (select all that apply per excerpt)

{methods}

## Classification Rules

1. Assign all relevant methods mentioned in each excerpt
2. Leave array empty if no specific methods can be identified

## Output Format

Return only a JSON object:
```json
{"methods": ["method_code"]}
```
````

User:

```
<excerpt>
{text}
</excerpt>
```

## Call settings

- Temperature 0. `max_tokens` 1,000 for the reasoning models.
- Parse the first JSON object in `content`. Drop codes not in the label list and record how many were dropped.
- HF Inference Providers, billed to `baobabtech` ([../README.md](../README.md#hf-inference-providers)); pin and record the provider.

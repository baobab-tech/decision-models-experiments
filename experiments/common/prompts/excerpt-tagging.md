# Excerpt tagging prompts

Classify-only prompts for relabelling task B excerpts with GLM-5.3-Flash and DeepSeek-V4.1-Flash (experiments [01](../../01-many-option-classification/) and [02](../../02-fine-tuning/)).

## Source

- The pipeline had no separate tagging prompt. It extracted and tagged excerpts in one call per document section: `EXTRACT_AND_CLASSIFY_FINDINGS_PROMPT` and `EXTRACT_AND_CLASSIFY_METHODOLOGY_PROMPT` in `ingestion-pipeline/lib/extract/prompts.ts` of [baobab-tech/eval-explorer](https://github.com/baobab-tech/eval-explorer), commit `6ae90f7` (2026-07-29).
- Pipeline model: `openai/gpt-oss-120b`, with fallbacks `google/gemini-2.5-flash` and `alibaba/qwen-3-235b`, via Vercel AI Gateway (`ingestion-pipeline/lib/config.ts`).
- The prompts below keep the pipeline's taxonomy text and classification rules word for word, and drop the extraction instructions.
- The theme definitions (`definitions_themes.json`) and `prompts.ts` are identical on eval-explorer `main`, `staging` and `6ae90f7` (checked 2026-10-06), so these are the production definitions. The zod schema (`schemas.ts`) takes its enums from `prompts.ts`; its `themes` description says "1-4 relevant theme codes" while the prompt says 1 to 3. These prompts follow the prompt text.

## Differences from the pipeline

- **Input:** the excerpt to classify, plus context blocks in production's layout: its main section (the window, with the excerpt marked) and context sections (Document Start, executive summary, abstract). Which blocks are included is the variant under test in 01's [context pilot](../../01-many-option-classification/README.md#context-pilot). The task line says to use the context for understanding, as production's "use context for understanding only" does.
- **Output:** tags for one given excerpt. The JSON format is in the prompt rather than a `response_format` schema, which not every provider supports.
- **Label lists and definitions** come from the dataset's `taxonomy` config (`definition_excerpts` for themes and methods), filtered to `in_excerpts`, so every model is asked over the same codes.

## Findings and recommendations

Fields: `themes`, `regions`, `countries`. `{themes}` is one line per code, formatted as in the pipeline: ``- `code` (Label): definition``. `{regions}` is the comma-separated, backticked region codes.

System:

````
You are an expert evaluator classifying excerpts from evaluation documents.

## Task

Classify the excerpt below by themes, regions and countries. Use the main section and context sections for understanding, e.g. which country or programme the excerpt refers to.

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

## EXCERPT TO CLASSIFY

{text}

## MAIN SECTION ({section_category}; the excerpt is between <<< and >>>)

{window_with_marked_excerpt}

## CONTEXT SECTIONS (for understanding only)

### Document Start
{first_100_words}

### Executive Summary
{executive_summary_1500_chars}

### Abstract
{abstract_1500_chars}
```

Blocks absent from a variant, or empty for a document, are left out.

## Methodology

Field: `methods`. `{methods}` is one line per code: ``- `code` - description``.

System:

````
You are an expert evaluator classifying methodology excerpts from evaluation documents.

## Task

Classify the methodology excerpt below with the research methods used. Use the main section and context sections for understanding.

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
## EXCERPT TO CLASSIFY

{text}

## MAIN SECTION ({section_category}; the excerpt is between <<< and >>>)

{window_with_marked_excerpt}

## CONTEXT SECTIONS (for understanding only)

### Document Start
{first_100_words}

### Executive Summary
{executive_summary_1500_chars}

### Abstract
{abstract_1500_chars}
```

Blocks absent from a variant, or empty for a document, are left out.

## Call settings

- Temperature 0. `max_tokens` 16,384, so reasoning never truncates; billing is per token used.
- Parse the first JSON object in `content`. Drop codes not in the label list and record how many were dropped.
- HF Inference Providers, billed to `baobabtech` ([../README.md](../README.md#hf-inference-providers)); pin and record the provider.

# 01 Many-option classification

**Status:** proposed. Nothing runs until the plan is approved.

## Question

Are decision models worth using for classification with 10+ options, 100+ tags, or document types, on inputs of ~100 and ~2,000 tokens? Where they fall short, what should we use instead?

## What the research says

| Model | Max options per Choice | Multi-label | Input length |
|---|---|---|---|
| [Jev](../../docs/models/jev.md#scaling-limits) | 255 (docs: reliable to ~240) | one Noul per label | 64k per request |
| [Liquid d1](../../docs/models/liquid-d1.md#scaling-limits) | not published (≥2) | one Noul per label | 32k |
| [GLiNER2.5-Decide](../../docs/models/gliner-decide.md#scaling-limits) | no cap in code | native (`multi_label`) | chunks of 384 words for long text |
| [Kev](../../docs/models/kev.md#scaling-limits) | 255 | one Noul per label | trained on states ≤384 tokens; served up to 65k |
| [CLM-8B](../../docs/models/clm-8b.md#scaling-limits) | no cap; option embeddings cached | via `/v1/rank` plus thresholding | 2,048 by default; longer states are truncated silently |
| [AnyJev](../../docs/models/anyjev.md#scaling-limits) | 26 | one Noul per label | base model's context |
| [Bonsai-Llama-Jev](../../docs/models/bonsai-llama-jev.md#scaling-limits) | not published | one Noul per label | 64k, split across slots |

- No vendor publishes accuracy or latency for 10 vs 100+ options.
- No study covers 100+ multi-label tags ([concepts.md](../../docs/concepts.md)).
- For more than 255 options, vendors recommend running Choice questions in stages: a coarse question first, then a finer one within the chosen group.

## Variables

- Number of options: 5, 10, 25, 50, 100, 200+.
- Label type: single-label or multi-label.
- Input length: ~100 tokens or ~2,000 tokens.
- How the question is asked:
  - one Choice
  - one Noul per label
  - staged Choices, coarse then fine
  - label names only vs names with descriptions

## Data

BANKING77, CLINC150, DBpedia L3, 20 Newsgroups, Reuters-21578 and a document-types set. Licences and sources are in [common/datasets.md](../common/datasets.md).

## Baselines

- Embeddings plus kNN or logistic regression.
- Zero-shot NLI.
- An open LLM reading answer probabilities directly, both raw and through AnyJev.
- A fine-tuned encoder, where labelled data exists.

## Metrics

Defined in [common/metrics.md](../common/metrics.md):

- `accuracy`, `macro_f1`, and `micro_f1` for multi-label
- `ece_15`, `brier`
- `coverage_at_5`
- `latency_p50_ms` / `p95`
- `cost_per_1k`, `tokens_per_request`

## Data governance

Local models run on this Mac. API models (Jev, d1) get public datasets only.

## What would change a decision

If a decision model stays within a few points of a fine-tuned encoder at 100+ labels, we would use it for tagging without collecting training data.

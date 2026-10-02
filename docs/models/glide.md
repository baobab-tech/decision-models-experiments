# GLiDE (Fastino)

| Field | Value |
|---|---|
| Vendor | Fastino Labs (Fastino, Inc., San Francisco) |
| Type | Decision model with adaptive reasoning: probabilities for typed questions (Choice, Score, Noul), no generated text |
| Backbone | Not disclosed |
| Size | Not disclosed. Catalog: "Served on one B200" |
| Licence | Hosted API only; no weights published. The API catalog lists `"license": "Apache-2.0"` (see [Caveats](#caveats)) |
| Run it via | `POST https://api.fastino.ai/v1/systemone`, model `fastino/GLiDE` |
| Status | Released 2026-09-30 (blog); press release 2026-10-01. Catalog `tier: "research"` |

Checked 2026-10-02.

## Overview

GLiDE stands for Generalized Lightweight Decision Engine.
It takes a `state` and named typed questions and returns one answer per question, with probabilities for every option.
It makes a fast first pass, then reasons further when the leading answer is uncertain and folds that reasoning into the final probabilities ([blog](https://fastino.ai/blog/introducing-glide-the-first-thinking-decision-model)).
Fastino reports that "roughly two-thirds of requests were resolved on the fast path" in its testing ([press release](https://www.prnewswire.com/news-releases/fastino-labs-releases-glide-the-first-thinking-decision-model-leading-the-decision-indexs-top-model-by-6-9-points-302896638.html)).
Reasoning tokens appear as `usage.output_tokens` and are not billed.
It is text-only (`supports_image_input: false`).
It is unrelated to Fastino's open-weight [GLiNER2.5-Decide](gliner-decide.md), which uses the `gliner2` schema.

## Schema

Same structure as TypeSafe: `model` + `state` + `questions` → `answers` + `usage` ([GLiDE reference](https://docs.fastino.ai/concepts/decision-models)).

- Auth: `X-API-Key: $FASTINO_API_KEY`; `Authorization: Bearer` also accepted. Keys start `fast_sk_`.
- `model` is required; omitting it returns `422`. The response echoes `glide`.
- `instructions` must be a non-empty string on every question. Unknown top-level fields return `422`.
- **Noul:** optional `criteria` `{"true": …, "false": …}`; returns `noul` and `confidence` = `|2 × noul − 1|`.
- **Choice:** `criteria` object of up to 255 options; returns `choice`, `probabilities`, `confidence` = top-1 minus top-2 probability.
- **Score:** ordered array of up to 255 levels; returns `score` (integer index of the most probable level), `expected_level` (probability-weighted level), `probabilities`, `legend`, `confidence` = top-1 minus top-2.
- No multi-label primitive; ask one question per label.

Differences from Jev ([migration guide](https://docs.fastino.ai/inference/systemone#migrating-from-typesafe)):

| Jev | GLiDE |
|---|---|
| Score `score` is a weighted float | `expected_level` is the weighted float; `score` is the winning index |
| Choice `confidence` formula n/d | top-1 minus top-2 margin |
| TypeSafe SDK | plain HTTP; no Fastino SDK documented |
| Retry `429`, `529` | Retry `425` (model warming, ~60 s), `429`, `503` |

Fastino says the integration "is not a drop-in replacement" and asks users to re-tune confidence thresholds set for Jev.

## Benchmarks

All numbers are Fastino's own run of the Decision Index 0.2.1 scorer ([blog](https://fastino.ai/blog/introducing-glide-the-first-thinking-decision-model), 2026-09-30). GLiDE has no row on the public board; the blog says 0.2.1 submissions are paused. The board's `data/index.json` (generated 2026-09-28) has no GLiDE row, checked 2026-10-02.

| Measure | GLiDE | Jev 1.13.0 (board) |
|---|---:|---:|
| Decision Index 0.2.1, balanced skill | 64.81 | 57.91 |
| Tools and Automation (skill) | 83.5 | 75.1 |
| Knowledge and Reasoning (skill) | 62.9 | 51.4 |
| CRUXEval accuracy | 92.6% | 73.0% |
| CLadder accuracy | 88.7% | 72.6% |

- Fastino reports GLiDE ahead of Jev in all five areas and on 31 of 38 benchmarks. Scores for the other three areas and 34 benchmarks are not in the blog.
- No calibration (ECE), latency or cost-per-decision figures are published.
- No third-party results as of 2026-10-02.

## Running it

1. Create an account at [agent.fastino.ai](https://agent.fastino.ai/) and a key under [API keys](https://agent.fastino.ai/api-keys). Put `FASTINO_API_KEY` in `.env`.
2. Call the endpoint ([GLiDE inference](https://docs.fastino.ai/inference/systemone)):

```bash
curl --max-time 300 -s https://api.fastino.ai/v1/systemone \
  -H "X-API-Key: $FASTINO_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "fastino/GLiDE",
       "state": "Refund request: the receipt is attached, the purchase was 10 days ago, and refunds are allowed within 30 days.",
       "questions": {
         "department": {"type": "choice", "instructions": "Which team should handle this request?",
                        "criteria": {"billing": "Payment or charge disputes", "returns": "Refund or return requests", "shipping": "Delivery or shipping issues"}},
         "urgency": {"type": "score", "instructions": "How urgent is this request?",
                     "criteria": ["low urgency, can wait", "medium urgency, handle soon", "high urgency, handle immediately"]}}}'
```

Documented answers: `department` → `returns` (0.9996, confidence 0.9993); `urgency` → `score` 0, `expected_level` 0.276; usage 743 input, 252 output tokens.

- Price: $0.30 per 1M input tokens; output $0 ([pricing](https://docs.fastino.ai/pricing), [catalog](https://api.fastino.ai/v1/base-models)). That is about 7× Jev's $0.042.
- Docs advise a read timeout of at least 300 s. A cold model returns `425 model_warming`.

## Scaling limits

- **Options:** 255 per Choice or Score.
- **Context:** 40,000 tokens per rendered question (`state` plus that question); oversized requests are rejected, not truncated. Thinking tokens share the window.
- **Questions per call:** no documented maximum. Each question is a separate internal pass, so `usage.input_tokens` sums across questions and can exceed 40,000.
- **Batching:** one `state` per request; no streaming.
- **Rate limits:** no number published; `429` with `Retry-After`.
- **Cost:** each question bills its own pass, so a 10,000-token state asked 5 questions bills about 50,000 tokens ($0.015) (inferred from the `usage` note, unverified).

## Fine-tuning

- Not offered: `supports_training: false` in the catalog, and "GLiDE does not currently support fine-tuned deployment IDs".
- Fastino's hosted training jobs cover GLiNER models only ([pricing](https://docs.fastino.ai/pricing)).

## Data governance

Not legal advice. The hosted API is shared with GLiNER2.5-Decide, so the account-level terms in [gliner-decide.md](gliner-decide.md#data-governance) apply.

| Item | Status | Evidence |
|---|---|---|
| Self-host | No; no weights published | [HF `fastino` models](https://huggingface.co/fastino), 2026-10-02 |
| Fine-tuning | No | [catalog](https://api.fastino.ai/v1/base-models) |
| Processing location | US on AWS; all 15 listed subprocessors are in the US, including OpenAI, Anthropic, Modal and Azure for "AI/ML services" | [Trust & Safety](https://docs.fastino.ai/trust-safety) (subprocessors updated 2026-07-30) |
| EU processing option | n/d | |
| Retention / ZDR | Inputs and outputs "retained indefinitely" by default; `store: false` gives zero retention "for eligible use cases". Catalog: `supports_zdr: true` | [Trust & Safety](https://docs.fastino.ai/trust-safety) |
| Training on inputs | Yes by default ("Sometimes, by default"); Enterprise can opt out in Settings. The terms say Pro and above (see gliner-decide.md) | [Trust & Safety](https://docs.fastino.ai/trust-safety) |
| DPA / GDPR | "At this time, we do not offer a Data Processing Addendum (DPA)" | [Trust & Safety](https://docs.fastino.ai/trust-safety) |
| Certifications | SOC 2 Type II and ISO 27001 in progress; first audit expected November 2026 | [Trust & Safety](https://docs.fastino.ai/trust-safety) |
| Weights licence | No weights distributed; catalog field says Apache-2.0 | [catalog](https://api.fastino.ai/v1/base-models) |

Which requests, if any, reach the AI/ML subprocessors is undocumented. Send only public or synthetic data until a DPA exists.

## Caveats

- The only benchmark is Fastino's own run of a public suite; it is not on the board.
- Not documented: architecture, size, training method, calibration, latency, rate limits, EU processing.
- The catalog lists the licence as Apache-2.0 while no weights are published; the field may describe a future release or be a catalog default (unverified).
- Release date: the blog is dated 2026-09-30 and the press release 2026-10-01.

## Sources

- Fastino: [launch blog](https://fastino.ai/blog/introducing-glide-the-first-thinking-decision-model) (2026-09-30), [GLiDE concept page](https://docs.fastino.ai/concepts/glide), [GLiDE reference](https://docs.fastino.ai/concepts/decision-models), [GLiDE inference](https://docs.fastino.ai/inference/systemone), [Choice](https://docs.fastino.ai/concepts/glide-choice), [Score](https://docs.fastino.ai/concepts/glide-score), [Noul](https://docs.fastino.ai/concepts/glide-noul), [pricing](https://docs.fastino.ai/pricing), [Trust & Safety](https://docs.fastino.ai/trust-safety), [llms.txt](https://docs.fastino.ai/llms.txt), [base-model catalog](https://api.fastino.ai/v1/base-models), [OpenAPI](https://docs.fastino.ai/openapi.json)
- [Press release](https://www.prnewswire.com/news-releases/fastino-labs-releases-glide-the-first-thinking-decision-model-leading-the-decision-indexs-top-model-by-6-9-points-302896638.html) (PR Newswire, 2026-10-01)
- [Decision Index Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) (`data/index.json` generated 2026-09-28)

All read 2026-10-02.

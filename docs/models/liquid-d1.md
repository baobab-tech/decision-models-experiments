# Liquid AI d1

| | |
|---|---|
| Vendor | Liquid AI |
| Type | Decision model: calibrated probabilities over fixed outcomes, zero output tokens |
| Backbone | Not disclosed |
| Size | Not disclosed |
| Licence | Proprietary, hosted API only; no weights |
| Run it via | Liquid API (`POST https://api.liquid.ai/decisions/v1/systemone`, model `d1:free`) or Vercel AI Gateway (`liquid/d1`, AI SDK `experimental_evaluate`) |

Checked 2026-09-30. Released 2026-09-29.

## Overview

- TypeSafe-compatible System One API: `state` plus typed `questions` in, one answer per question out. `usage.output_tokens` is always `0`.
- Clients are the TypeSafe SDKs (`typesafe-sdk`, `@typesafe-ai/sdk`) pointed at `https://api.liquid.ai`.
- Liquid's docs target classification, routing, moderation, triage, reranking and safety checks, and send writing, dialogue, reasoning, summarisation and code to a language model.
- Liquid documents migrating from LLM structured-output classification to d1 in its [decision model guide](https://docs.liquid.ai/guides/decision-model-guide).
- The only cookbook example is `examples/road-decider/` in [Liquid4All/cookbook](https://github.com/Liquid4All/cookbook).

## Schema

Same wire format as Jev; see [concepts.md](../concepts.md#request-and-response-shape). Examples from [Liquid docs](https://docs.liquid.ai/lfm/models/decision-models).

```json
{"model": "d1:free",
 "state": "I have been waiting over three weeks for my order and nobody has responded to my emails.",
 "questions": {"is_complaint": {"type": "noul", "instructions": "Is this message a complaint from the customer?"}}}
```

```json
{"model": "d1:free",
 "answers": {"is_complaint": {"type": "noul", "noul": 0.999}},
 "usage": {"input_tokens": 84, "output_tokens": 0}}
```

- Documented examples pass JSON state as a string (`json.dumps(ticket)`); Noul examples use only `instructions`.
- `confidence` is not the top probability: a Choice with `engineering: 0.80, frontend: 0.18` reports `confidence: 0.74`. The formula is not documented.
- A Choice with fewer than two options returns HTTP 422 ([perch PR #230](https://github.com/lakeday-org/perch/pull/230)).
- The AI SDK path renames fields:

| Liquid API | AI SDK `experimental_evaluate` |
|---|---|
| `type: "noul"`, answer `noul` | `type: "boolean"`, answer `probability`; optional `true`/`false` criteria |
| Choice / Score `criteria` | nonempty option map / at least two ordered levels; `probabilities` optional |
| `confidence` | `result.providerMetadata?.typesafe?.confidence` |

## Benchmarks

| Benchmark | d1 | Jev 1.13 | Source |
|---|---|---|---|
| Decision Index 0.2.1 (composite) | 58.9 | 57.9 | Liquid's own run of the suite, reported by [KuCoin](https://www.kucoin.com/news/flash/liquid-ai-s-d1-decision-model-surpasses-jev-in-hugging-face-evaluation), 2026-09-30 |

- By area, d1 leads on arts and human judgment, language understanding, and retrieval and classification. It is slightly behind Jev on tools and 8 points behind on knowledge and reasoning.
- The Jev figure matches the public board: Jev 1.13 scores 57.91 on Decision Index 0.2.1 in the [DI Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) (`data/index-v0.2.1.json`, 38 index benchmarks, 120,340 requests).
- d1 has no row on the public board. Its data files (`index-v0.2.1.json`, 70 entrants plus Jev, generated 2026-09-28T00:39Z) predate d1's 2026-09-29 release (checked 2026-09-30).
- [Liquid's launch thread](https://threadreaderapp.com/thread/2105003472332693869.html) calls d1 "the first model to outperform Jev" on the index.
- Liquid publishes no per-benchmark scores and no latency numbers. [DataNorth](https://datanorth.ai/news/liquid-ai-releases-d1) notes the index ranks open-weight models and d1 has no weights.

## Running it

No weights exist (no `d1` under `LiquidAI` or `Liquid4All` on HF; no GGUF, MLX or ONNX), so it cannot run locally. Easiest path: curl against the Liquid API.

1. At [console.liquid.ai](https://console.liquid.ai), Dashboard > API Keys > create a key (prefix `liquid_`) and export it as `LIQUID_API_KEY`.
2. Call the endpoint:

```bash
curl -s https://api.liquid.ai/decisions/v1/systemone \
  -H "Authorization: Bearer $LIQUID_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "d1:free", "state": "I have been waiting over three weeks for my order.",
       "questions": {"is_complaint": {"type": "noul", "instructions": "Is this message a complaint from the customer?"}}}'
```

- SDKs: `TypeSafeClient(api_key=..., base_url="https://api.liquid.ai").system_one(model="d1:free", ...)` in Python; `new TypeSafeClient({apiKey, baseURL: "https://api.liquid.ai"}).systemOne(...)` in TS.
- Vercel AI Gateway: `experimental_evaluate({model: 'liquid/d1', ...})` from `ai`, auth via `AI_GATEWAY_API_KEY` or `VERCEL_OIDC_TOKEN` (`vercel link && vercel env pull`). AI SDK 7.0.105+ is required for Jev; the minimum for d1 is not stated (unverified). Only the AI SDK path is documented, not a raw HTTP or `/v1/chat/completions` route.
- OpenRouter support is planned, no date.

| Pricing and limits | Value |
|---|---|
| Billing | Input tokens only |
| Free tier | `d1:free`; quotas undocumented |
| Paid pricing / paid model id | Not documented; [liquid.ai/pricing](https://www.liquid.ai/pricing) covers open LFM licensing only |
| AI Gateway price | $0 input and output for `liquid/d1` ([`/v1/models`](https://ai-gateway.vercel.sh/v1/models)); whether this draws on the `d1:free` quota is undocumented |
| Context | 32,000 tokens ([Vercel](https://vercel.com/ai-gateway/models/d1), [gateway endpoints](https://ai-gateway.vercel.sh/v1/models/liquid/d1/endpoints), DataNorth) |
| Rate limits, regions | Not documented |

## Scaling limits

- **Options:** minimum 2; maximum undocumented. Compatible providers publish their own caps, not stated to apply to d1: Telnyx 2–64 options, 2–64 levels, 1–64 questions; LLM Gateway (Jev 1.13) 255 options, 2–10 levels, 600 requests/minute per organisation.
- **Questions per request:** a search summary claims "1–16 questions, up to 62 options" without a traceable source (unverified). perch PR #230 ran 100 questions in one call.
- **Multi-label:** no multi-select mode (Telnyx's compatible API states the same). Use one `noul` per label; Choice probabilities sum to about 1 and cannot be thresholded independently.
- **Input length:** 32k tokens for state and questions. perch ran a ~20k-token state with 100 questions and 8 parallel calls on `d1:free` (no latency reported). No accuracy or latency data by input length.
- **Cost growth:** whether `instructions` and `criteria` count as input tokens is undocumented. LLM Gateway says "Question text counts as input on every call" for Jev (unverified for d1). Under that model 100 one-line options cost about 10× the question tokens of 10, re-billed every call with no caching discount; a 2,000-token state costs ~20× a 100-token one.
- **Latency:** described as predictable (no decoding loop); no numbers vs option count. An unrelated model (integrallis "Harriet", Qwen3.5-4B) reports O(1) latency in options (not evidence for d1).

## Fine-tuning

- d1 is not fine-tunable ([MarkTechPost](https://www.marktechpost.com/2026/09/29/liquid-ai-releases-d1-a-decision-model-that-returns-calibrated-probabilities-with-zero-output-tokens/), DataNorth). No custom or enterprise variant is documented.
- Liquid's open LFM2 / LFM2.5 models support SFT, LoRA, DPO and GRPO via LEAP Finetune, TRL and Unsloth ([docs](https://docs.liquid.ai/lfm/fine-tuning/overview)). They are free for commercial use under $10M revenue.
- No System One-style recipe exists for LFM2.5; a fine-tune would be a generative classifier with logprob-derived probabilities.
- [`Mapika/decider-2b`](https://huggingface.co/Mapika/decider-2b) (Apache 2.0, Qwen3.5-2B-Base, not Liquid) is an open reproduction: 2–255 options, 32k context, a `/v1/systemone` server said to work with `typesafe-sdk` (unverified; not tested).

## Data governance

Not legal advice.

| Field | Liquid API (`api.liquid.ai`) | Vercel AI Gateway (`liquid/d1`) |
|---|---|---|
| Processing location | US, "and possibly other countries" ([privacy policy](https://www.liquid.ai/privacy-policy)). Cloud provider undocumented. | Gateway in any Vercel region on AWS, Azure, GCP ([DPA](https://vercel.com/legal/dpa)); inference routed to `liquid` only. |
| EU region | Undocumented. US transfers "may" rely on standard clauses. | No: no `regions` in [`/v1/models`](https://ai-gateway.vercel.sh/v1/models), so EU `inferenceRegion` fails ([Regional Inference](https://vercel.com/docs/ai-gateway/security-and-compliance/regional-inference)). |
| Retention | "As long as necessary". Terms §3.3.4: inputs and outputs usable "in perpetuity for our internal business purposes" ([terms](https://www.liquid.ai/terms-conditions)). No ZDR. | Vercel logs metadata only ([FAQ](https://vercel.com/docs/ai-gateway/faq)). `"zdr": "none"` and `has_zdr: false` ([endpoints](https://ai-gateway.vercel.sh/v1/models/liquid/d1/endpoints)); Liquid absent from the [ZDR list](https://vercel.com/docs/ai-gateway/security-and-compliance/zdr). `zeroDataRetention: true` fails with `no_providers_available` (unverified). |
| Trains on inputs | Permitted: inputs and outputs used for "enhancing AI models"; users asked not to submit personal data. | Vercel does not ([docs](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training)). `"no_training": "none"` and `has_no_training: false`, so Liquid's terms apply. |
| DPA / GDPR | Referenced, no public link. Requests: legal@liquid.ai. | Vercel DPA (2021 SCCs, UK IDTA); covers Vercel only. |
| Certifications | Access-gated [trust center](https://trust.liquid.ai/) hosted on Vanta; contents not public. | Vercel SOC 2 Type 2, ISO 27001:2013 ([security](https://vercel.com/security)). |
| Subprocessors | Undocumented. | Vercel's via its DPA. |
| Self-host / fine-tuning | No / no. Open LFMs run on-prem but are not d1. | No / no. |
| Weights licence | Proprietary; none distributed. | Same. |

- The gateway adds Vercel's controls but does not change what Liquid does with the request.
- Liquid's privacy policy (2025-07-14) and terms (2024-09-23) do not mention d1.

## Caveats

- Paid pricing, rate limits, quotas, size and architecture are undocumented.
- The only benchmark figures come from Liquid's own run of the Decision Index; no independent run exists.
- Code is not portable between the Liquid API (`noul` / `.noul`) and AI SDK (`boolean` / `.probability`) without renaming.

## Sources

- Liquid: [Decision Models](https://docs.liquid.ai/lfm/models/decision-models), [Decision Model Guide](https://docs.liquid.ai/guides/decision-model-guide), [fine-tuning](https://docs.liquid.ai/lfm/fine-tuning/overview), [pricing](https://www.liquid.ai/pricing), [cookbook](https://github.com/Liquid4All/cookbook), [HF models](https://huggingface.co/LiquidAI/models)
- Vercel / AI SDK: [d1 model page](https://vercel.com/ai-gateway/models/d1), [`evaluate` reference](https://ai-sdk.dev/docs/reference/ai-sdk-core/evaluate), [Evaluation](https://ai-sdk.dev/docs/ai-sdk-core/evaluation), [Jev + AI SDK guide](https://vercel.com/kb/guide/typesafe-jev-and-ai-sdk)
- News: [MarkTechPost](https://www.marktechpost.com/2026/09/29/liquid-ai-releases-d1-a-decision-model-that-returns-calibrated-probabilities-with-zero-output-tokens/), [KuCoin](https://www.kucoin.com/news/flash/liquid-ai-s-d1-decision-model-surpasses-jev-in-hugging-face-evaluation), [DataNorth](https://datanorth.ai/news/liquid-ai-releases-d1), [Decision Index Space](https://huggingface.co/spaces/multimodalart/jev-decision-index)
- Limits: [perch PR #230](https://github.com/lakeday-org/perch/pull/230), [Telnyx](https://developers.telnyx.com/api-reference/decision-models/evaluate-decision-models-typesafe-compatible.md), [LLM Gateway](https://llmgateway.io/changelog/system-one-typed-decisions), [integrallis PR #216](https://github.com/integrallis/models/pull/216), [Mapika/decider-2b](https://huggingface.co/Mapika/decider-2b)
- Governance: [privacy policy](https://www.liquid.ai/privacy-policy), [terms](https://www.liquid.ai/terms-conditions), [trust center](https://trust.liquid.ai/), [Vercel security and compliance](https://vercel.com/docs/ai-gateway/security-and-compliance), [ZDR](https://vercel.com/docs/ai-gateway/security-and-compliance/zdr), [prompt training](https://vercel.com/docs/ai-gateway/security-and-compliance/disallow-prompt-training), [Regional Inference](https://vercel.com/docs/ai-gateway/security-and-compliance/regional-inference), [FAQ](https://vercel.com/docs/ai-gateway/faq), [`/v1/models`](https://ai-gateway.vercel.sh/v1/models), [`liquid/d1` endpoints](https://ai-gateway.vercel.sh/v1/models/liquid/d1/endpoints), [DPA](https://vercel.com/legal/dpa), [security](https://vercel.com/security)

# Upstage Solar Decide

| Field | Value |
|---|---|
| Vendor | Upstage (Republic of Korea) |
| Type | Decision model: probabilities for typed questions (Choice, Score, Noul) |
| Backbone | Solar Mini 4 (mixture-of-experts; targets Korean, English, Japanese) |
| Size | 35B parameters, 3B active per token |
| Licence | Proprietary; hosted API only |
| Run it via | `POST https://api.upstage.ai/v1/systemone`, model `solar-decide`; OpenRouter, model `upstage/solar-decide` |
| Status | Beta (Upstage Console 2026-09-22; OpenRouter 2026-09-28) |

Checked 2026-09-30.

## Overview

Solar Decide takes a `state` (string or JSON) and a map of typed `questions`, and returns one typed answer per question, using Jev's `/v1/systemone` request format.
Upstage runs one forward pass per question and does not bill output tokens.
The context window is 524,288 tokens (512K).
Upstage's own model page (`console.upstage.ai/docs/models/solar-decide`) returned "could not be found" on 2026-09-30; details come from the API reference, systemonemodels.org and OpenRouter.

## Schema

Same path, request fields, primitives and answer fields as TypeSafe. Auth: `Authorization: Bearer $UPSTAGE_API_KEY`.

- Choice: 2–26 options; more returns HTTP 422 (decisions are read from single-token labels A–Z).
- Score: `criteria` array, lowest first.
- Noul: `instructions` only.
- Choice `confidence` (0.983124 in the documented example) is lower than the top probability (0.997405); the formula is not published.
- The documented example returns `usage.output_tokens: 4`, though output is billed at $0.
- TypeSafe SDKs with `base_url="https://api.upstage.ai"`: not documented (unverified).
- OpenRouter exposes `/api/v1/systemone` and `/api/alpha/decisions`; Solar Decide on those paths is unverified.

## Benchmarks

| Benchmark | Solar Decide | Jev 1.13 | Source |
|---|---|---|---|
| zero-shot-ie-bench spectrum pool (48 questions) | 95.8% (46/48), 0.308 s/question | 93.8% | [PR #17](https://github.com/umstek/zero-shot-ie-bench/pull/17) |
| zero-shot-ie-bench multilingual (54 texts, 9 languages) | 100%, 0.885 s/text | n/d | same |
| "JevBench" | 87.0%, median 0.14 s | 86.1%, 0.30 s | didcodexreset.com (unverified) |

PR #17 ran through OpenRouter's default route on "small samples from one person's test set".
Upstage has published no benchmarks.

## Running it

1. Create an API key on the [Upstage Console](https://console.upstage.ai) and `export UPSTAGE_API_KEY=...`.
2. Call the endpoint (from the [API reference](https://console.upstage.ai/api/systemone)):

```bash
curl -X POST https://api.upstage.ai/v1/systemone \
  -H "Authorization: Bearer $UPSTAGE_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "solar-decide",
       "state": "Customer ticket #4821: My package never arrived and I want my money back. I have been waiting three weeks and nobody has replied to my emails.",
       "questions": {
         "intent": {"type": "choice", "instructions": "Classify what the customer is asking for.",
                    "criteria": {"refund": "The customer wants money back.", "track": "The customer wants the delivery status of an order.", "other": "Anything else."}},
         "urgency": {"type": "score", "instructions": "Rate how urgently this ticket needs a reply.",
                     "criteria": ["No action needed", "Can wait a week", "Needs attention today", "Escalate immediately"]},
         "is_angry": {"type": "noul", "instructions": "Is the customer angry?"}}}'
```

Documented answers: `intent` → `refund` (0.997405), `urgency` → 2.846517, `is_angry` → 0.99883; 670 input tokens.

Alternative: OpenRouter with `OPENROUTER_API_KEY`; one of its two Upstage endpoints is tagged `upstage/zdr`.

Price: $0.10 per 1M input tokens list; OpenRouter shows $0.05 (50% discount); output free.

## Scaling limits

- **Options:** 26 per Choice. Score level cap and questions-per-call cap are not published.
- **Context:** 512K tokens; a full 512K state costs about $0.05 per call at list price.
- **Multi-label:** one Noul per label in the same call.
- **100+ options:** ≥4 Choice questions of ≤26 options (distributions normalised within each group), or a coarse-to-fine hierarchy.
- **Rate limits:** Tier 0: 100 requests and 250,000 tokens per minute; Tier 4: 8,000 requests and 3,000,000 tokens per minute (systemonemodels.org, unverified).
- **Latency:** not published; one forward pass per question suggests it grows with question count (inferred).

## Data governance

| Item | Status | Evidence |
|---|---|---|
| Self-host | Upstage sells on-premises deployments of its models; Solar Decide on-prem n/d | [Upstage on-premises](https://upstage.ai/pricing/on-premises) |
| Fine-tuning | n/d | |
| Processing location | Not stated; overseas transfers to AWS, Azure, OpenAI, Google, Stripe (all US) | [privacy policy](https://www.upstage.ai/privacy-policy) |
| EU processing option | n/d | |
| Retention / ZDR | Stored "solely to the extent necessary"; async results 30 days; sync n/d. ZDR endpoint via OpenRouter | [terms](https://www.upstage.ai/terms-of-service), [OpenRouter endpoints](https://openrouter.ai/api/v1/models/upstage/solar-decide/endpoints) |
| Training on inputs | Paid: no. Free services (excluding promotional trials) may be used "(including training)" | [terms, Article 22](https://www.upstage.ai/terms-of-service) |
| DPA / GDPR | No DPA; Korea PIPA; overseas transfer can be refused, which "may result in restrictions" | [privacy policy](https://www.upstage.ai/privacy-policy) |
| Certifications | SOC 2, HIPAA, ISO 27001/27701 in search summaries (unverified) | |
| Governing law | Republic of Korea; US customers: arbitration under California law | [terms, Article 28](https://www.upstage.ai/terms-of-service) |

## Caveats

- Beta services "may be modified or discontinued… without prior notice" (terms, Article 10).
- Not documented: Score level cap, questions per call, latency, `confidence` formula, fine-tuning, EU processing.
- The "JevBench" comparison has no traceable primary source.

## Sources

- Upstage: [API reference](https://console.upstage.ai/api/systemone), [model page (not resolving)](https://console.upstage.ai/docs/models/solar-decide), [Solar Mini 4](https://console.upstage.ai/docs/models/solar-mini-4), [rate limits](https://console.upstage.ai/docs/guides/rate-limits), [changelog](https://console.upstage.ai/docs/resources/changelog), [terms](https://www.upstage.ai/terms-of-service), [privacy policy](https://www.upstage.ai/privacy-policy), [on-premises](https://upstage.ai/pricing/on-premises)
- OpenRouter: [upstage/solar-decide](https://openrouter.ai/upstage/solar-decide), [endpoints](https://openrouter.ai/api/v1/models/upstage/solar-decide/endpoints), [Jev guide](https://openrouter.ai/docs/guides/community/jev)
- [systemonemodels.org: Solar Decide](https://systemonemodels.org/models/solar-decide/)
- [umstek/zero-shot-ie-bench PR #17](https://github.com/umstek/zero-shot-ie-bench/pull/17)
- [didcodexreset.com: Solar Decide on OpenRouter](https://didcodexreset.com/news/98eea98c1cb3457b9564532a.html)

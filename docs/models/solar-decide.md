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
Upstage's [model page](https://console.upstage.ai/docs/models/solar-decide) lists release 2026-09-22 (beta), $0.10 per 1M input and cached tokens, and free output tokens.

## Schema

Same path, request fields, primitives and answer fields as TypeSafe. Auth: `Authorization: Bearer $UPSTAGE_API_KEY`.

- Choice: 2–26 options; more returns HTTP 422 (decisions are read from single-token labels A–Z).
- Score: `criteria` array, lowest first.
- Noul: `instructions` only.
- Choice `confidence` (0.983124 in the documented example) is lower than the top probability (0.997405). The API reference defines it as how concentrated the probabilities are; the formula is not published.
- The API reference states one output token per question, not billed; its three-question example returns `usage.output_tokens: 4`.
- TypeSafe SDKs with `base_url="https://api.upstage.ai"`: not documented (unverified).
- OpenRouter exposes `/api/v1/systemone` and `/api/alpha/decisions`. PR #17 below called Solar Decide through `/api/v1/systemone`; `/api/alpha/decisions` with Solar Decide is unverified.

## Benchmarks

| Benchmark | Solar Decide | Jev | Source |
|---|---|---|---|
| zero-shot-ie-bench spectrum pool (48 questions) | 95.8% (46/48), 0.308 s/question | 93.8% (cloud, via TypeSafe) | [PR #17](https://github.com/umstek/zero-shot-ie-bench/pull/17) |
| zero-shot-ie-bench multilingual (54 texts, 9 languages) | 100%, 0.885 s/text | 100% | same; [README](https://github.com/umstek/zero-shot-ie-bench#multilingual-benchmark-9-languages-no-english) |
| "JevBench" | 87.0%, median 0.14 s | 86.1% (Jev 1.13), 0.30 s | didcodexreset.com, attributed to OpenRouter (unverified) |

PR #17 (merged 2026-09-29) ran through OpenRouter's default, non-ZDR route; the spectrum pool is 48 sentiment and topic questions.
The JevBench figures appear neither on OpenRouter's model page nor on [jevbench.dev](https://jevbench.dev/), which ranks game wins (checked 2026-09-30).
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

Price: $0.10 per 1M input tokens list ([model page](https://console.upstage.ai/docs/models/solar-decide)); output free. OpenRouter shows $0.05 with a 0.5 discount. Upstage runs a 50% Solar Mini 4 promotion through 2026-10-22 (UTC); whether it covers Solar Decide on the Upstage Console is not stated.

## Scaling limits

- **Options:** 26 per Choice. Score level cap and questions-per-call cap are not published.
- **Context:** 512K tokens; a full 512K state costs about $0.05 per call at list price.
- **Multi-label:** one Noul per label in the same call.
- **100+ options:** ≥4 Choice questions of ≤26 options (distributions normalised within each group), or a coarse-to-fine hierarchy.
- **Rate limits:** shared with Solar Mini 4. Tier 0: 100 requests and 250,000 tokens per minute; Tier 4: 8,000 requests and 3,000,000 tokens per minute; legacy tiers: 100 requests and 50,000 tokens per minute ([rate limits](https://console.upstage.ai/docs/guides/rate-limits)).
- **Latency:** not published; one forward pass per question suggests it grows with question count (inferred).

## Data governance

| Item | Status | Evidence |
|---|---|---|
| Self-host | Upstage sells on-premises deployments of its models; Solar Decide on-prem n/d | [Upstage on-prem](https://www.upstage.ai/pricing/on-prem) |
| Fine-tuning | n/d | |
| Processing location | Not stated for Solar Decide. Model-inference subprocessors in Korea (NAVER Cloud, VESSL AI, Elice) and the US (RunPod, Azure, OpenAI); storage and operations on AWS, Azure, Google (US) | [privacy policy](https://www.upstage.ai/privacy-policy) (revised 2026-09-15) |
| EU processing option | n/d | |
| Retention / ZDR | Model page: "API input data is not stored, unless required for service delivery". Terms: not stored except "solely to the extent necessary" for the service. Async API results 30 days. ZDR endpoint via OpenRouter | [model page](https://console.upstage.ai/docs/models/solar-decide), [terms, Article 22](https://www.upstage.ai/terms-of-service), [privacy policy](https://www.upstage.ai/privacy-policy), [OpenRouter endpoints](https://openrouter.ai/api/v1/models/upstage/solar-decide/endpoints) |
| Training on inputs | Paid: no, unless separately consented. Free services (excluding promotional trials) may be used "(including training)". Model page: API input is not used for training | [terms, Article 22](https://www.upstage.ai/terms-of-service), [model page](https://console.upstage.ai/docs/models/solar-decide) |
| DPA / GDPR | No published DPA. Korea PIPA, plus EU/UK supplementary provisions: Upstage is controller; transfers rely on the EU adequacy decision for Korea and SCCs. Overseas transfer can be refused, which "may result in restrictions" | [privacy policy](https://www.upstage.ai/privacy-policy) (revised 2026-09-15) |
| Certifications | SOC 2, HIPAA, ISO 27001/27701, as stated by Upstage; reports not reviewed | [Upstage on-prem](https://www.upstage.ai/pricing/on-prem) |
| Governing law | Republic of Korea; US customers: arbitration under California law | [terms, Article 28](https://www.upstage.ai/terms-of-service) (effective 2026-09-21) |

## Caveats

- Beta services "may be modified or discontinued… without prior notice" (terms, Article 12-2).
- Not documented: Score level cap, questions per call, latency, `confidence` formula, fine-tuning, EU processing.
- The "JevBench" comparison has no traceable primary source.

## Sources

- Upstage: [API reference](https://console.upstage.ai/api/systemone), [model page](https://console.upstage.ai/docs/models/solar-decide), [Solar Mini 4](https://console.upstage.ai/docs/models/solar-mini-4), [rate limits](https://console.upstage.ai/docs/guides/rate-limits), [changelog](https://console.upstage.ai/docs/resources/changelog), [terms](https://www.upstage.ai/terms-of-service), [privacy policy](https://www.upstage.ai/privacy-policy), [on-prem](https://www.upstage.ai/pricing/on-prem)
- OpenRouter: [upstage/solar-decide](https://openrouter.ai/upstage/solar-decide), [endpoints](https://openrouter.ai/api/v1/models/upstage/solar-decide/endpoints), [Jev guide](https://openrouter.ai/docs/guides/community/jev)
- [systemonemodels.org: Solar Decide](https://systemonemodels.org/models/solar-decide/)
- [umstek/zero-shot-ie-bench PR #17](https://github.com/umstek/zero-shot-ie-bench/pull/17)
- [jevbench.dev](https://jevbench.dev/)
- [didcodexreset.com: Solar Decide on OpenRouter](https://didcodexreset.com/news/98eea98c1cb3457b9564532a.html)

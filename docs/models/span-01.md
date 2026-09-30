# Respan Span-01

| Field | Value |
|---|---|
| Vendor | Respan (Keywords AI Inc., California) |
| Type | Behaviour classifier for conversation traces: per behaviour, P(present), P(absent), P(not observable) |
| Backbone | Not disclosed |
| Size | Not disclosed |
| Licence | Proprietary; hosted API only |
| Run it via | `POST https://api.respan.ai/api/v1/scores`, models `span-01-free` (default) / `span-01-pro`; OpenRouter `respan/span-01`, `respan/span-01-lite` |
| Status | GA (2026-09-24) |

Checked 2026-09-30.

## Overview

Span-01 reads a conversation span (prior messages plus one target turn) and a list of plain-language behaviour definitions.
For each behaviour it returns `p_present`, `p_absent` and `p_not_observable`, which "sum to about 1".
Respan says to treat `p_not_observable` as unknown, not absent.
All behaviours are scored in one forward pass.
Training: "general classification reasoning with RLAIF", then specialisation for behaviour detection.
Tiers: Span-01 Lite (`span-01-free`), free with a daily cap resetting 00:00 UTC; Span-01 (`span-01-pro`), paid.

## Schema

Auth: `Authorization: Bearer $RESPAN_API_KEY`.

| Field | Required | Notes |
|---|---|---|
| `span` | yes | `input`: list of `{role, content}`; `output`: one `{role, content}` to classify |
| `behaviors` | yes | list of `{id, definition}`; `definition` ≥ 3 characters |
| `model` | no | default `span-01-free` |
| `respan_params` | no | logging metadata, e.g. `customer_identifier` |

Response: `{"model", "results": [{"id", "p_present", "p_absent", "p_not_observable"}], "usage": {"input_tokens"}}`.
Errors: 400 bad request, 402 no credits (Pro), 403 key/access, 413 span too large, 422 validation, 424/503/504 scorer unreachable or timeout, 429 rate limit.

TypeSafe compatibility: none (different path, `span` for `state`, `behaviors` list for `questions`, `results` list for `answers`).
Each behaviour maps to a Noul via `p_present`; an adapter must decide whether to fold `p_not_observable` into "no" or renormalise.
Choice and Score are not supported.

## Benchmarks

The [launch post](https://www.respan.ai/blog/introducing-span-1) (2026-09-24, checked 2026-09-30) reports two benchmarks; both F1 figures come from it.

- **Behavior benchmark**, nine models, overall F1: Span-01 84.3, GPT-6 Luna 81.5, Jev 1.13.0 71.5. "Overall is the unweighted mean of English and multilingual F1." Span-01 Lite is said to beat Jev and Sonnet 5; its score is not printed in the page text.
- **Production behavior benchmark**, seven domains, overall F1: Span-01 0.806, GPT-6 Sol 0.885, Sonnet 5 0.719, Jev 0.716. How the overall is aggregated from the domains is not stated. Per-domain scores:

| Domain | Span-01 | Jev | Sonnet 5 | GPT-6 Sol |
|---|---|---|---|---|
| Jailbreak and prompt injection | 0.779 | 0.752 | 0.709 | 0.878 |
| Safety and refusals | 0.803 | 0.751 | 0.785 | 0.911 |
| Privacy and secrets | 1.000 | 0.948 | 0.901 | 0.935 |
| Hallucination and grounding | 0.796 | 0.673 | 0.756 | 0.903 |
| Agent/tool reliability | 0.845 | 0.691 | 0.677 | 0.861 |
| Task following | 0.702 | 0.671 | 0.621 | 0.821 |
| Response quality | 0.771 | 0.691 | 0.722 | 0.956 |
| Overall | 0.806 | 0.716 | 0.719 | 0.885 |

- systemonemodels.org repeats both figures and adds Lite 0.761 (unverified; not in the launch post text).
- zero-shot-ie-bench (sentiment/topic): Span-01 85.4%, Lite 79.2%, Jev 93.8% (systemonemodels.org).
- No calibration metric published.

## Running it

1. Create a Respan account, `export RESPAN_API_KEY=...`.
2. Call the free tier ([quickstart](https://www.respan.ai/docs/documentation/span-01/quickstart)):

```bash
curl https://api.respan.ai/api/v1/scores \
  -H "Authorization: Bearer $RESPAN_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "span-01-free",
       "span": {"input": [{"role": "user", "content": "Please connect me to a person."}],
                "output": {"role": "assistant", "content": "I will connect you to our support team."}},
       "behaviors": [{"id": "escalation", "definition": "the user wants a human/agent/representative, or the assistant says a human handoff is needed (not mere frustration or wanting a better answer)."}]}'
```

Price: `span-01-pro` $0.02 per 1M input tokens; `span-01-free` free with an unpublished daily cap; output free.
The OpenRouter call shape for Span-01 is not documented.

## Scaling limits

- **Behaviours per request:** "no per-request cap"; multi-label is native.
- **Context / span size:** not published; oversized spans return 413. OpenRouter lists `context_length: 0`.
- **Cost:** 100 one-line definitions (~2,000 tokens) plus a 2,000-token trace cost about $0.00008 on Pro, assuming definitions are billed as input (unverified).
- **Rate limits:** not published for Pro.

## Data governance

| Item | Status | Evidence |
|---|---|---|
| Self-host | Platform offers AWS/GCP/Azure, on-prem and VPC deployment; Span-01 not stated | [Respan enterprise](https://respan.ai/solutions/enterprise) |
| Fine-tuning | n/d | |
| Processing location | Not stated; AI providers named: Anthropic, Google Cloud AI, OpenAI | [privacy policy](https://respan.ai/legal/privacy-policy) |
| EU processing option | "EU data residency available upon request" (search summary; trust center returned 403, unverified) | [enterprise](https://respan.ai/solutions/enterprise), [trust center](https://trustcenter.respan.ai/) |
| Retention / ZDR | Kept while the account exists; custom retention on enterprise contracts; no ZDR mode for Span-01 | [privacy policy](https://respan.ai/legal/privacy-policy) |
| Training on inputs | n/d | [privacy policy](https://respan.ai/legal/privacy-policy) |
| DPA / GDPR | GDPR/UK GDPR rights covered; DPA and BAA "on request" (search summary); `respan.ai/legal/dpa` "Not Found" | [privacy policy](https://respan.ai/legal/privacy-policy) |
| Certifications | SOC 2 Type II, HIPAA (BAA), ISO 27001, "GDPR ready" (platform-wide) | [enterprise](https://respan.ai/solutions/enterprise) |

## Caveats

- Not documented: model size, context length, span-size limit, Lite daily cap, Pro rate limits, training on inputs.
- Span-01's 84.3 (behavior benchmark) and 0.806 (production behavior benchmark) are different Respan benchmarks, both vendor-run on Respan data.
- The only external result is on sentiment/topic, outside Span-01's target domain.
- Organisation enablement may be needed before calls succeed (systemonemodels.org, unverified).

## Sources

- Respan: [launch blog (2026-09-24)](https://www.respan.ai/blog/introducing-span-1), [concept](https://www.respan.ai/docs/documentation/span-01/concept), [quickstart](https://www.respan.ai/docs/documentation/span-01/quickstart), [API reference](https://www.respan.ai/docs/apis/respan-models/score-span-behaviors), [privacy policy](https://respan.ai/legal/privacy-policy), [terms](https://respan.ai/legal/terms-of-use), [enterprise](https://respan.ai/solutions/enterprise), [trust center](https://trustcenter.respan.ai/)
- OpenRouter: [respan/span-01](https://openrouter.ai/respan/span-01), [respan/span-01-lite](https://openrouter.ai/respan/span-01-lite), [endpoints](https://openrouter.ai/api/v1/models/respan/span-01/endpoints)
- [systemonemodels.org: Span-01](https://systemonemodels.org/models/span-01/)
- [umstek/zero-shot-ie-bench](https://github.com/umstek/zero-shot-ie-bench)

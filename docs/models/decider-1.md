# meraGPT Decider 1

| Field | Value |
|---|---|
| Vendor | meraGPT (trading name of Okyasoft Pte Ltd, Singapore) |
| Type | Decision model: probabilities for typed questions (Choice, Score, Noul), no generated text |
| Backbone | Not disclosed |
| Size | Not disclosed |
| Licence | Proprietary; hosted API only |
| Run it via | `POST https://meragpt.com/v1/systemone`, model `sd-1` (alias `state-decider-1`); TypeSafe SDKs with base URL `https://meragpt.com` (unverified) |
| Status | GA (2026-09-22) |

Checked 2026-09-30.

## Overview

Decider 1 takes a JSON `state` and a map of typed `questions`, and returns one typed answer per question.
It is text-only.
systemonemodels.org records it as unrelated to the open `Mapika/decider-*` models.
meraGPT's guidance: "Batch questions, not items" (several questions about one item per call; one call per item).

## Schema

Same path and shape as TypeSafe: `model` + `state` + `questions` → `answers` + `usage`. Auth: `Authorization: Bearer $MERAGPT_API_KEY`.

- Choice: 2–10 labels; returns `choice`, `probabilities`, `confidence`.
- Score: 2–10 levels (`criteria` array, lowest first); returns `score`, `probabilities`, `confidence`, `legend`.
- Noul: `instructions` only; returns `noul`.
- The envelope adds `id`, `object`, `usage.cost_usd` and `balance_usd`.

In the documented example, Choice `confidence` equals the top probability (0.8969) and Score `confidence` equals the top level probability (0.4393); Score `score` is the probability-weighted mean level (2.1852).
Liquid d1 computes Choice `confidence` differently.

## Benchmarks

meraGPT's own evaluation on `LocalLLaMA/typed-decisions` (400 test cases, 2,000 decisions):

| Metric | Decider 1 | Jev 1.13.0 |
|---|---|---|
| Accuracy (all) | 0.768 | 0.727 |
| Noul / Choice / Score accuracy | 0.840 / 0.733 / 0.739 | n/d |
| KL divergence from reference | 0.096 | 1.442 |
| Brier score | 0.052 | 0.148 |
| ECE | 0.180 (binning not stated) | n/d |

Labels come from a teacher model; meraGPT notes "scores well above 0.735 mean a model is learning the teacher's quirks".
No third-party results.

## Running it

1. Sign up at https://meragpt.com ($1 free credit; prepaid from $10) and `export MERAGPT_API_KEY=...`.
2. Call the endpoint ([support-triage cookbook](https://meragpt.com/docs/cookbooks/support-triage)):

```bash
curl https://meragpt.com/v1/systemone \
  -H "Authorization: Bearer $MERAGPT_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "sd-1",
       "state": {"channel": "email", "messages": [{"from": "customer", "text": "Hi, the export button has been greyed out since yesterday'\''s update and I have a board meeting at 3pm where I need this report. Can someone look at it now?"}]},
       "questions": {
         "team": {"type": "choice", "instructions": "Which team should handle this?",
                  "criteria": {"billing": "Charges, invoices, payments and refunds.", "technical": "The product is not working as expected.", "account": "Login, plan changes and access."}},
         "urgency": {"type": "score", "instructions": "How urgent is this?",
                     "criteria": ["Can wait a week", "Within a few days", "Today", "Immediately"]},
         "refund_requested": {"type": "noul", "instructions": "Is the customer asking for money back?"}}}'
```

Documented answers: `team` → `technical` (0.8969), `urgency` → 2.1852, `refund_requested` → 0.0975.
Price: $0.03 per 1M input tokens; output not billed.
The playground allows 10 signed-out runs per day per IP.
Launch-post latency: p50 about 526 ms end to end.

## Scaling limits

- **Options:** 10 per Choice, 10 levels per Score.
- **Questions per call:** up to 64.
- **Context:** 4,096 tokens for state plus questions; more returns `400 input_too_long`.
- **Multi-label:** one Noul per label in the same call.
- **100+ options:** ≥10 Choice questions of ≤10 labels (distributions not comparable across groups), or a two-call coarse-to-fine hierarchy. 100 options at ~20 tokens each use ~2,000 of the 4,096 tokens.
- **Rate limits:** no number published; saturation returns `429` with `Retry-After`.
- **Cost:** a full 4,096-token request costs about $0.00012.

## Data governance

| Item | Status | Evidence |
|---|---|---|
| Self-host | No | [systemonemodels.org](https://systemonemodels.org/models/meragpt-decider-1/) |
| Fine-tuning | n/d | |
| Processing location | Not stated; "including the United States". Subprocessors: Vercel, Neon, Stripe, Google, unnamed model hosts | [privacy policy](https://meragpt.com/privacy) |
| EU processing option | n/d | |
| Retention / ZDR | Request text "held in memory only… never written to our database or our logs"; usage records kept for billing | [privacy policy](https://meragpt.com/privacy), [terms](https://meragpt.com/terms) |
| Training on inputs | No ("We do not train on it") | [terms](https://meragpt.com/terms) |
| DPA / GDPR | No DPA; transfers rely on "standard contractual clauses" | [privacy policy](https://meragpt.com/privacy) |
| Certifications | n/d | |
| Legal entity / law | Okyasoft Pte Ltd; Singapore law | [terms](https://meragpt.com/terms) |

## Caveats

- Not documented: model size, architecture, training method, processing regions, certifications, fine-tuning.
- The only benchmark is meraGPT's own, on a teacher-labelled dataset.
- The 10-option cap and 4,096-token context are the tightest among TypeSafe-compatible APIs.

## Sources

- meraGPT: [System One API docs](https://meragpt.com/docs/systemone), [cookbooks](https://meragpt.com/docs/cookbooks), [errors](https://meragpt.com/docs/errors), [model page](https://meragpt.com/models/state-decider-1), [launch blog](https://meragpt.com/blog/introducing-decider-1), [terms](https://meragpt.com/terms), [privacy policy](https://meragpt.com/privacy)
- [HF: LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions)
- [systemonemodels.org: Decider 1](https://systemonemodels.org/models/meragpt-decider-1/)

# Jev (TypeSafe AI)

| | |
|---|---|
| Vendor | TypeSafe AI (typesafe.ai), founder Diogo Almeida |
| Type | "System One" typed decision model: state + typed questions in, probabilities out; no text generation |
| Backbone | Not disclosed; the launch post describes a new architecture with a parallel sampler |
| Size | Not disclosed (no parameter count, architecture paper or training-compute figure) |
| Licence | Proprietary, closed weights; hosted API only (early access) |
| Run it via | `POST https://api.typesafe.ai/v1/systemone`, Python `typesafe-sdk`, JS/TS `@typesafe-ai/sdk` |

Checked 2026-09-30.

## Overview

- Launched in early access on 2026-09-15 ([launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev)). TypeSafe raised a $40M seed led by DCVC (secondary sources only).
- Trained with "Reinforcement Learning for Calibrated Decisions" (RLCD). Each question is evaluated in parallel and in isolation against the same state.
- Input is text only: string, JSON object or array. English is the primary language; others (including CJK) work with lower accuracy.
- Official domains: `typesafe.ai`, `docs.typesafe.ai`, `console.typesafe.ai`, `api.typesafe.ai`; GitHub org `typesafe-ai`.
- `jevmodel.net` and `thejevai.com` (linked from third-party HF blog posts) are not TypeSafe domains. Their endpoints, the model string `typesafe/jev-1.13` and the "Starter $10 / Pro $100 / Enterprise $1,000" plans are unofficial (unverified).

## Schema

Reference wire format; see [concepts.md](../concepts.md#request-and-response-shape) for field rules and errors. Examples are a composite of the [API reference](https://docs.typesafe.ai/api.md)'s per-type examples; values illustrative.

```json
{"model": "jev-latest",
 "state": "Help! My payouts have been failing for 3 days.",
 "questions": {
   "is_urgent":  {"type": "noul", "instructions": "Does this convey urgency?"},
   "department": {"type": "choice", "instructions": "Which team should handle this?",
                  "criteria": {"billing": "Payments, invoicing, refunds", "technical": "Bugs, outages, integrations"}},
   "frustration": {"type": "score", "instructions": "How frustrated is the customer?",
                   "criteria": ["Calm", "Frustrated", "Very angry"]}}}
```

```json
{"model": "jev-1.13.0",
 "answers": {
   "is_urgent":  {"type": "noul", "noul": 0.95},
   "department": {"type": "choice", "choice": "billing", "probabilities": {"billing": 0.88, "technical": 0.12}, "confidence": 0.81},
   "frustration": {"type": "score", "score": 1.05, "legend": {"0": "Calm", "1": "Frustrated", "2": "Very angry"},
                   "probabilities": {"0": 0.0, "1": 0.95, "2": 0.05}, "confidence": 0.92}},
 "usage": {"input_tokens": 304, "output_tokens": 18}}
```

- Model IDs: `jev-1.13.0` (current), `jev-latest` and `jev-preview` (both → `jev-1.13.0`). `jev-1.12` appears in cookbooks dated 2026-08-12; whether it is still served is undocumented. Aliases move on release, so pin a version when tuning thresholds.
- Question keys are not sent to the model. An `instructions` object can hold reference data that the question names in backticks.
- `confidence` is computed from the distribution (flatter → lower); the formula is not published.
- `elapsedMs`, listed by a third-party HF post, is not in the API reference (unverified).
- `GET /v1/models` returns `{"models": [{"name", "description", "release_date"}]}` (aliases only). No batch, streaming or fine-tuning endpoints are documented.

## Benchmarks

| Source | Result |
|---|---|
| TypeSafe workflow evals ([homepage](https://typesafe.ai)) | 193.6x faster, 444.6x cheaper than LLMs; example $0.000081 / 0.114 s vs $0.013880 / 8.566 s |
| Dashboard via [orcarouter.ai](https://www.orcarouter.ai/blog/jev-typesafe-system-one-what-we-know) | 711 cases, 4 workflows: Jev 67.8% agreement vs 74.1% best comparator (security 61.7/66.2, agent traces 71.6/76.6, invoices 61.8/79.1, customer service 76.0/78.3) (unverified) |
| [AutoTrust](https://huggingface.co/blog/autotrust/autotrustjev-27b-fast-calibrated-decisions-and-ful) (not affiliated) | Mean 83.85 over six benchmarks: JevBench 87.18, Kev 85.52, OpenJev text 72.96, Nimble 91.84, VitaminC 78.46, MASSIVE-en 87.14; its open JEV-27B scores 84.07 (unverified) |

- TypeSafe's reference labels are the average of GPT-6 Astra and Claude Fable 5.1 predictions, not ground truth; TypeSafe notes a bias toward those models and calls the speed/cost ratios "on the higher end".
- The HF "Decision Index" ([dataset](https://huggingface.co/datasets/autotrust/jev-decision-index-results)) is AutoTrust's board of its own open models, not a TypeSafe product.
- Community harnesses: [4esv/jev-eval](https://github.com/4esv/jev-eval), [dhruvmehra/jevbench](https://github.com/dhruvmehra/jevbench), [fstandhartinger/jevbench](https://github.com/fstandhartinger/jevbench).

## Running it

API only. Local runs on Apple Silicon are impossible: no weights, GGUF, MLX or ollama build exists, and Hub/ollama models named "Jev" are third-party. For local Jev-style models see [open-reproductions.md](./open-reproductions.md).

| Item | Value ([Models](https://docs.typesafe.ai/models)) |
|---|---|
| Price | $0.042 per million input tokens; output free. No free tier documented |
| Rate limits | 100K tokens/s, 40 requests/s (adjusted dynamically; higher on enterprise) |
| Context | 64k tokens per request; 32k for state + longest single question |
| Latency | 70–500 ms end-to-end (vendor claim; service hosted on the US West Coast) |

Get early access at [console.typesafe.ai](https://console.typesafe.ai/) (waitlist possible), export a key as `TYPESAFE_API_KEY`, then `uv run jev_min.py`:

```python
# /// script
# dependencies = ["typesafe-sdk"]
# ///
from typesafe_sdk import Choice, Noul, TypeSafeClient

with TypeSafeClient() as client:  # reads TYPESAFE_API_KEY, defaults to jev-latest
    r = client.system_one(
        state="I've been trying to connect my Stripe account for 3 days and it keeps failing. Please help ASAP.",
        questions={
            "department": Choice(instructions="Which team should handle this",
                                 criteria={"billing": "Payment issues", "technical": "Bugs or integration problems"}),
            "is_urgent": Noul(instructions="The message conveys urgency"),
        },
    )
print(r.answers["department"].choice, r.answers["is_urgent"].noul, r.usage)
```

- SDKs: Python ≥ 3.10 [`typesafe-sdk`](https://github.com/typesafe-ai/typesafe-sdk-python) (`[http2]` extra available; sync and async clients); Node ≥ 20 [`@typesafe-ai/sdk`](https://github.com/typesafe-ai/typesafe-sdk-js) (v0.6.0). Both retry 429/529 with backoff.
- Agent skill: `claude plugin marketplace add typesafe-ai/skills && claude plugin install typesafe@typesafe-ai`, or `npx skills add typesafe-ai/skills --skill typesafe-ai`.
- Vercel AI Gateway serves it as `typesafe-ai/jev` via AI SDK `experimental_evaluate` (≥ 7.0.105). Its example uses type `"boolean"` instead of `"noul"`; the mapping is not in TypeSafe docs.

## Scaling limits

- **Options:** hard limit 255 per Choice. A cookbook says it "works reliably up to roughly 240". High-cardinality Choices use an internal two-stage process that causes "occasional slowdown". Past 255, docs chain two passes or run hierarchical beam search over nested Choices.
- Docs recommend sending the full option list plus an `other` option. No accuracy, latency or cost curve for 10 vs 100+ options is published.
- **Multi-label:** no multi-select type. Use one Noul per label in one request and threshold in code. Choice probabilities are relative and Noul probabilities absolute, so thresholds do not transfer between them ([jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13)).
- **Questions per request:** no documented maximum beyond the 64k context. Parallel questions "barely change the response time". Batching 13 questions (jev-1.12): $0.000497 / 0.27 s in one call vs $0.006090 / 2.71 s in 13 calls, same answers.
- **Input length:** 64k per request, 32k for state + longest question. Accuracy drops as irrelevant content grows ("context rot"); filter in code or add a relevance Noul. No published 100- vs 2,000-token comparison.
- **Cost growth:** input tokens only. Each option adds its key and description tokens; 2,000 extra state tokens cost about $0.00008.

## Fine-tuning

- Not offered. The same weights serve every account ([Models](https://docs.typesafe.ai/models)).
- Customisation is per request: content in `state`, rules in `instructions`/`criteria`, and decomposition into atomic questions.
- TypeSafe suggests training a downstream model (e.g. CatBoost) on Jev's probabilities (AutoResearch cookbook).
- For trainable Jev-style models see [open-reproductions.md](./open-reproductions.md).

## Data governance

Not legal advice.

| Field | Jev API (`api.typesafe.ai`) |
|---|---|
| Processing location | United States ([privacy policy](https://typesafe.ai/legal/privacy-policy), effective 2025-11-19). AWS hosts live-request data; Modal processes prompts without storing them ([trust center](https://trust.typesafe.ai/)). |
| EU region | None as of 2026-09-30. EU data moves to the US under SCCs Module 2 ([DPA](https://typesafe.ai/legal/data-processing)). |
| Retention | DPA: "as long as necessary". ZDR for enterprise via sales@typesafe.ai ([Legal](https://docs.typesafe.ai/legal)). Default prompt retention undocumented. |
| Trains on inputs | No: TypeSafe "will not train or fine tune any … models on Input" (privacy policy). |
| DPA / GDPR | Public DPA (2026-04-24): SCCs, UK Addendum, 72-hour breach notice, 15-day subprocessor notice. |
| Certifications | SOC 2 Type II (2026, on request). ISO 27001 undocumented. |
| Subprocessors | AWS, Modal, Slack, Google Workspace (all USA). |
| Self-host / fine-tuning | No / no. |
| Weights licence | Proprietary; no weights distributed. |

Via Vercel AI Gateway (`typesafe-ai/jev`):

- No ZDR as of 2026-09-30. The gateway routes `typesafe-ai/jev` through one provider, `digitalocean`, with `"has_zdr": false` and `"has_no_training": true` ([`/v1/models/typesafe-ai/jev/endpoints`](https://ai-gateway.vercel.sh/v1/models/typesafe-ai/jev/endpoints)); [`/v1/models`](https://ai-gateway.vercel.sh/v1/models) matches with `"zdr": "none"`, `"no_training": "all"` and no `regions` field. The [ZDR page](https://vercel.com/docs/ai-gateway/security-and-compliance/zdr) (updated 2026-09-22) lists TypeSafe AI as a ZDR provider, and the [2026-09-16 changelog](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway) says Jev supports ZDR, but TypeSafe is not the serving provider. Per the ZDR page, a `zeroDataRetention: true` request fails with `no_providers_available` when no ZDR provider serves the model (not tested).
- Without `regions`, EU pinning via `inferenceRegion` is unavailable ([Regional Inference](https://vercel.com/docs/ai-gateway/security-and-compliance/regional-inference)).

## Caveats

- Closed model with early-access keys; rate limits change without notice during the capacity ramp.
- Text only: PDFs need a parse or OCR step first. On LlamaIndex's five PDF tasks (32–96 decisions each, jev-1.13.0, run 2026-09-24), free specialised tools matched or beat Jev: lingua 100% vs 100% on language, tesseract OSD 100% vs 93.8% on orientation, a two-rule heuristic 93.8% vs 85.4% on parse triage ([experiment 03](../../experiments/03-jev-vs-open-document-tasks/)).
- Noul answers carry no `confidence`. Calibration holds across groups of predictions, not for single answers.
- Documented jev-1.13 weak spots: literal reading, counting and arithmetic, date comparison, multi-hop indirection, large irrelevant state, injected state content, instructions contradicting criteria, and inconsistent related questions (a Noul and its negation summed to 1.19).
- Open questions: `confidence` formula, max questions per request, free tier, `jev-1.12` availability, accuracy vs option count and state length.

## Sources

- TypeSafe: [launch post](https://typesafe.ai/blog/introducing-system-one-models-and-jev), [homepage](https://typesafe.ai), [llms.txt](https://docs.typesafe.ai/llms.txt), [API](https://docs.typesafe.ai/api), [quickstart](https://docs.typesafe.ai/introduction/quickstart), [Models](https://docs.typesafe.ai/models), [System One](https://docs.typesafe.ai/concepts/system-one), [State](https://docs.typesafe.ai/concepts/state), [Confidence](https://docs.typesafe.ai/confidence)
- Primitives and cookbooks: [Choice](https://docs.typesafe.ai/primitives/choice), [Score](https://docs.typesafe.ai/primitives/score), [Noul](https://docs.typesafe.ai/primitives/noul), [Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13), [parallel questions](https://docs.typesafe.ai/cookbooks/parallel_questions), [classification using confidence](https://docs.typesafe.ai/cookbooks/classification_using_confidence), [line-by-line search](https://docs.typesafe.ai/cookbooks/semantic_find), [Python SDK](https://docs.typesafe.ai/sdk/python), [JavaScript SDK](https://docs.typesafe.ai/sdk/javascript), [agent skill](https://docs.typesafe.ai/agent-skill)
- Legal: [Legal](https://docs.typesafe.ai/legal), [DPA](https://typesafe.ai/legal/data-processing), [privacy policy](https://typesafe.ai/legal/privacy-policy), [MCA](https://typesafe.ai/legal/mca), [trust center](https://trust.typesafe.ai/)
- Vercel: [changelog 2026-09-16](https://vercel.com/changelog/typesafe-ai-jev-now-available-on-ai-gateway), [ZDR](https://vercel.com/docs/ai-gateway/security-and-compliance/zdr), [Regional Inference](https://vercel.com/docs/ai-gateway/security-and-compliance/regional-inference), [`/v1/models`](https://ai-gateway.vercel.sh/v1/models)
- Third-party: [AutoTrust JEV-27B blog](https://huggingface.co/blog/autotrust/autotrustjev-27b-fast-calibrated-decisions-and-ful), [Decision Index dataset](https://huggingface.co/datasets/autotrust/jev-decision-index-results), [orcarouter.ai](https://www.orcarouter.ai/blog/jev-typesafe-system-one-what-we-know), [systemonemodels.org](https://systemonemodels.org); unofficial: [HF blog (paidaxccc)](https://huggingface.co/blog/paidaxccc/jev-system-one-model-a-practical-guide-to-typed-ai), [HF blog (sora-2)](https://huggingface.co/blog/sora-2/what-is-jev-ai-a-practical-guide-to-system-one-and)

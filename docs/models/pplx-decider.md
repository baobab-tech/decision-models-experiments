# pplx-decider-v1-27b (Perplexity)

| Field | Value |
|---|---|
| Vendor | Perplexity AI, Inc. (San Francisco) |
| Type | Decision model: probabilities for typed questions (Choice, Score, Noul), no generated text. Text and image input |
| Backbone | Qwen3.8-27B (revision `1d4bf0f`), LM head replaced by a 255-option decision readout |
| Size | 26,085,330,160 parameters (BF16, 48.6 GiB in 11 shards) |
| Licence | Weights Apache-2.0; `source/` training and serving code MIT |
| Run it via | Hosted: `POST https://api.perplexity.ai/v1/decisions`, model `pplx-decider-v1-27b`. Open weights: [`perplexity-ai/pplx-decider-v1-27b`](https://huggingface.co/perplexity-ai/pplx-decider-v1-27b) with `inference.py` on a CUDA GPU |
| Status | Released 2026-10-01 (HF repo created 2026-10-01T21:24Z; [@perplexitydevs](https://x.com/perplexitydevs/status/2105725598882832414) launch post the same day). HF revision `5117a6c`; 165 downloads (30-day), 46 likes |

Checked 2026-10-02.

## Overview

pplx-decider-v1-27b is Perplexity's open-weight decision model and the only model behind its Decisions API.
It takes a `state` (text, JSON or images) and named questions, and returns one typed answer per question ([quickstart](https://docs.perplexity.ai/docs/decisions/quickstart)).
The full-weight SFT replaced the language-generation output layer with a 255-option readout; a scalar temperature fitted on a separate split is stored in `decision_config.json` ([NOTICE](https://huggingface.co/perplexity-ai/pplx-decider-v1-27b/blob/main/NOTICE)).
Perplexity's own cookbook pairs it with the Agent API: the Decisions API makes the first call on each ticket and only escalations go to an LLM ([cookbook](https://docs.perplexity.ai/docs/cookbook/examples/decisions-api-ticket-triage/README)).

### Same weights as AutoJev-27B

The released weights are byte-identical to [AutoJev-27B](open-reproductions.md#autojev-27b) (`denis-pplx/autojev-27b`, revision `6f5b557`, published 2026-09-19). Evidence, read 2026-10-02 from the HF tree API:

- All 11 safetensors shards, `readout.safetensors`, `config.json`, `decision_config.json`, `model.safetensors.index.json`, the tokenizer files, `processor_config.json` and `chat_template.jinja` have the same LFS sha256 or git oid in both repos.
- Both `decision_config.json` files record run `sft-curated-02`, step 200, git commit `ad4345c` and temperature 2.2076.
- The pplx repo's `NOTICE` still reads "AutoJev 27B curated SFT checkpoint".
- The `source/src/autojev/` package is identical file for file; only `source/README.md` and the top-level README differ, and pplx adds `inference.py`.
- The `denis-pplx` HF account belongs to Denis Yarats and is a member of the verified `perplexity-ai` org ([HF profile](https://huggingface.co/denis-pplx)). His role at Perplexity is not stated on either card (unverified).

Treat the two repos as one model. AutoJev-27B results apply to pplx-decider-v1-27b, and the other way round, for the open weights. Whether the hosted API serves exactly these weights is not stated (unverified); the card says its scores "were measured through the Perplexity API".

## Schema

Same body shape as TypeSafe: `model` + `state` + `questions` → `model` + `answers` + `usage` ([API reference](https://docs.perplexity.ai/api-reference/decisions-post)). The path differs, so it is not a drop-in TypeSafe endpoint.

- Path `POST /v1/decisions`, not `/v1/systemone`. A trailing slash returns `404`.
- Auth `Authorization: Bearer $PERPLEXITY_API_KEY`; an `x-api-key` header is ignored and returns `401`. Any Perplexity API key works.
- `model` is required; a missing or unknown model returns `400`. Unknown top-level fields return `400`.
- **Noul:** `instructions`, `criteria` `{"true", "false"}`, or both; neither returns `400`. Returns `noul` (probability of yes) and no `confidence`.
- **Choice:** `criteria` object of 1 to 255 options; a `null` description means "use the name". Returns `choice`, `probabilities`, `confidence`.
- **Score:** ordered `criteria` array of up to 10 levels. Returns `score` (probability-weighted mean level, a float as in Jev), `legend`, `probabilities`, `confidence`.
- Images: OpenAI-style `image_url` parts with base64 PNG, JPEG or WebP data URLs inside a `state` array. HTTP image URLs return `400`.
- No multi-label primitive; ask one Noul per label.

`confidence` in the documented example:

- Choice: 0.9255 with top probability 0.9503 over 3 options, which is (K·p_max − 1)/(K − 1). The open code in `source/src/autojev/model.py` uses the same formula.
- Score: 0.7839, equal to 1 − Σ p_i·|i − best| (inferred from the example). The open code divides that distance by a uniform baseline and would give 0.676 for the same probabilities, so hosted and local Score `confidence` differ (inferred, unverified).

Perplexity says identical requests "occasionally" differ "in the second decimal place".

## Benchmarks

Vendor card, 11 benchmarks, 7,210 samples (sample count from [KuCoin news](https://www.kucoin.com/news/flash/perplexity-open-sources-27b-decision-model-outperforms-jev-in-official-tests), unverified), measured through the Perplexity API ([model card](https://huggingface.co/perplexity-ai/pplx-decider-v1-27b)):

| Benchmark | Jev | Qwen3.8-27B | pplx-decider-v1-27b |
|---|---:|---:|---:|
| WinoGrande | 90.70% | 73.10% | 83.30% |
| FinancialPhraseBank | 76.98% | 75.68% | 84.18% |
| RAGTruth | 77.27% | 61.53% | 88.80% |
| JudgeBench | 78.57% | 68.86% | 78.29% |
| BBH | 94.27% | 72.80% | 82.80% |
| JevBench public hard | 73.27% | 72.28% | 70.30% |
| TabFact | 89.80% | 78.60% | 90.60% |
| ContractNLI | 77.45% | 80.78% | 80.78% |
| Circa | 84.60% | 87.00% | 89.20% |
| Belebele | 95.00% | 93.20% | 94.00% |
| TruthfulQA binary | 92.00% | 82.80% | 85.40% |
| Overall | 84.51% | 74.76% | 85.71% |

Jev leads on 6 of 11 rows. The card gives no ECE, Brier, sample size per row or Jev version.

Third-party results for the same weights (as AutoJev-27B):

| Board | Result | Source |
|---|---|---|
| Decision Index 0.2.1 | 56.40 balanced skill, #4 of 71 rows (Jev 57.91); ECE 0.018; median 101.4 ms on one RTX PRO 6000 | [benchmarks.md](../benchmarks.md#decision-index), [leaderboards](../benchmarks-leaderboards.md#decision-index-021) |
| JevBench v1.5.5 (headline A) | 19.5, rank 54 of 109; Intelligence 72.8 (Jev 72.0), Calibration 87.7; Cost axis 29.4 at an estimated $0.226 per 1,000 decisions | [`api/jevbench/v1.5.5`](https://benchmarkheaven.com/api/jevbench/v1.5.5), read 2026-10-02 |
| AutoJev own test set | 84.60% vs Jev 82.79%; ECE 0.0428 vs 0.0527 | [AutoJev card](https://huggingface.co/denis-pplx/autojev-27b) |

The JevBench Cost axis uses a hosted base-model price estimate, not Perplexity's $0.04 per 1M input tokens. No JevBench row runs the Perplexity API as of 2026-10-02.

## Running it

Hosted API ([quickstart](https://docs.perplexity.ai/docs/decisions/quickstart)):

1. Create a key at [console.perplexity.ai](https://console.perplexity.ai/project/keys) and put `PERPLEXITY_API_KEY` in `.env`.
2. Call the endpoint:

```bash
curl -X POST https://api.perplexity.ai/v1/decisions \
  -H "Authorization: Bearer $PERPLEXITY_API_KEY" -H "Content-Type: application/json" \
  -d '{"model": "pplx-decider-v1-27b",
       "state": {"title": "Battery died after two weeks",
                 "review": "The headphones sound great, but the battery stopped charging after two weeks."},
       "questions": {
         "defect": {"type": "noul", "instructions": "Does the review report a product defect?"},
         "sentiment": {"type": "choice", "instructions": "What is the overall sentiment of the review?",
                       "criteria": {"positive": "Mostly satisfied", "mixed": "Praise and complaints in one review", "negative": "Mostly dissatisfied"}},
         "severity": {"type": "score", "instructions": "How severe is the reported problem?",
                      "criteria": ["Cosmetic", "Inconvenient", "Product unusable"]}}}'
```

Documented answers: `defect` 0.942; `sentiment` → `mixed` (0.950); `severity` 1.784; usage 367 input, 3 output tokens.

- Price: $0.04 per 1M input tokens; output free; no per-request fee ([pricing](https://docs.perplexity.ai/docs/getting-started/pricing)). The documented request costs about $0.0000147.
- Latency (Perplexity's tests, 2026-09-30): under 2 s for a few hundred input tokens; 5 s at ~90,000; 14 s at ~190,000; 23 s just under the limit.

Open weights ([model card](https://huggingface.co/perplexity-ai/pplx-decider-v1-27b)):

```bash
uvx --from huggingface-hub hf download perplexity-ai/pplx-decider-v1-27b inference.py --local-dir .
uv run inference.py            # text example; add --image screenshot.png for an image
```

`inference.py` pins `torch==2.14.0`, `transformers==5.17.0` and downloads 48.6 GiB on first run. The card asks for "a CUDA GPU with room for approximately 49 GiB of weights plus working memory". The AutoJev route (`uv run autojev-serve`) also serves `POST /v1/systemone` locally; see [open-reproductions.md](open-reproductions.md#autojev-27b).

**On an M5 Max (128 GB):** no documented path. `inference.py` defaults to `--device cuda`. `DecisionModel` loads BF16 only on CUDA and float32 elsewhere (`model.py`, line 154), so `--device mps` or `cpu` would hold about 97 GiB of weights (inferred from the code, not run). Qwen3.5-family Gated DeltaNet layers have no MPS kernels ([model-classes.md](../model-classes.md)). No MLX or GGUF conversion that keeps the readout head exists as of 2026-10-02. Use the hosted API for this Mac.

## Scaling limits

Hosted ([request limits](https://docs.perplexity.ai/docs/decisions/quickstart#request-limits)):

- **Options:** 1 to 255 per Choice; up to 10 levels per Score.
- **Questions per call:** 1 to 128.
- **Context:** under 262,144 input tokens per request, counting `state`, images and every question. `config.json` sets `max_position_embeddings` 262,144. The launch post says "250k".
- **Body:** 32 MiB (`413` above).
- **Images:** at most 2,048 tiles of 32 × 32 px per image (1440 × 1440 fits; 1600 × 1310 does not). An oversized image waits about a minute and returns `504`, not `400`. About 1,000 input tokens per megapixel.
- **Rate limits:** 10 requests per second per organization on every plan, plus a token limit for bursts; `429` with `Retry-After`.
- **Cost:** a 100,000-token state costs $0.004 per request.

Local (open code): `prepare()` rejects a question branch over 8,192 tokens by default, with no truncation (`model.py`, line 180). Options are capped at 255.

## Fine-tuning

- Hosted: not offered. No fine-tuning or custom-model option is documented for the Decisions API.
- Open weights: the training code ships in `source/` (`bash configs/train.sh --help`; `configs/training.json`). The curated 73,000-example corpus is not bundled ([AutoJev card](https://huggingface.co/denis-pplx/autojev-27b)). The original run used one H200, full-weight SFT, 286 updates; the release is checkpoint 200 ([fine-tuning.md](../fine-tuning.md)).

## Data governance

Not legal advice.

Open weights: self-hosted means your infrastructure. No data leaves it, no processor is involved, so no DPA is needed.

Hosted Decisions API:

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes, open weights (CUDA GPU with ~49 GiB free) | [model card](https://huggingface.co/perplexity-ai/pplx-decider-v1-27b) |
| Fine-tuning | Open weights only; not on the API | [model card](https://huggingface.co/perplexity-ai/pplx-decider-v1-27b), [quickstart](https://docs.perplexity.ai/docs/decisions/quickstart) |
| Processing location | "Amazon Web Services in North America" | [API FAQ](https://docs.perplexity.ai/docs/resources/faq) |
| EU processing option | n/d | |
| Retention / ZDR | "We do not retain any query data sent through the API"; "zero day retention of user prompt data" by default. The Privacy & Security page states its Zero Data Retention Policy for "the Chat Completions API" and does not name the Decisions API. Billing metadata (tokens, model, timestamps, key) is kept | [API FAQ](https://docs.perplexity.ai/docs/resources/faq), [Privacy & Security](https://docs.perplexity.ai/docs/resources/privacy-security) |
| Training on inputs | No. API terms §2.3.3: Perplexity will not use Customer Content to train, retrain or fine-tune any generative AI model. DPA: personal data "will not be used" to train Perplexity's LLMs | [API terms](https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service) (updated 2026-01-23), [DPA](https://www.perplexity.ai/hub/legal/dpa) |
| DPA / GDPR | DPA incorporated by reference in the API terms (§6.1). EU SCCs Module 2 and 3 plus the UK Addendum; Irish supervisory authority, Irish law and courts for the SCCs. Personal data deleted within 30 days after service ends. Subprocessors at [trust.perplexity.ai/subprocessors](https://trust.perplexity.ai/subprocessors), including Amazon and Microsoft | [DPA](https://www.perplexity.ai/hub/legal/dpa) |
| Certifications | SOC 2 Type II; 2025 HIPAA gap assessment; CAIQlite. Protected health information needs a signed BAA (API terms §6.2) | [Privacy & Security](https://docs.perplexity.ai/docs/resources/privacy-security), [Trust Center](https://trust.perplexity.ai/) |
| Weights licence | Apache-2.0 (weights); MIT (`source/`). Base Qwen3.8-27B is Apache-2.0 | [NOTICE](https://huggingface.co/perplexity-ai/pplx-decider-v1-27b/blob/main/NOTICE) |
| Legal entity / law | Perplexity AI, Inc.; California law, San Francisco courts | [API terms](https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service) |

The API terms define the Services as the "Sonar by Perplexity and/or Agentic Research" APIs; whether they also cover the Decisions API is not stated (unverified). The terms and DPA were read through a scraper that returned the Spanish rendering; the DPA showed "last updated 8 July 2025", while a third-party tracker reports DPA edits in August 2026 ([ConductAtlas](https://conductatlas.com/platform/perplexity-ai/perplexity-data-processing-addendum/)), so the date may be stale (unverified).

Training-data provenance: the AutoJev card does not publish the 73,000 training examples or say whether they include TypeSafe Jev outputs. Compliance with TypeSafe's output-use terms is unverified.

## Caveats

- pplx-decider-v1-27b and AutoJev-27B are the same weights under two names; avoid counting them twice in comparisons.
- The 11-benchmark card is a vendor run through the vendor's API. The AutoJev own-set numbers (84.60%) are a different suite from the pplx card (85.71%).
- No calibration figure is published for the hosted API; DI's ECE of 0.018 is for the open weights.
- Hosted and local Score `confidence` appear to use different formulas (see [Schema](#schema)).
- Context: the docs say "under 262,144" input tokens; the launch post says "250k"; the local code defaults to 8,192 per question.
- [explainx.ai](https://explainx.ai/blog/perplexity-pplx-decider-decisions-api-2026) (secondary) was not used for any fact here.

## Sources

- Perplexity docs: [Decisions API quickstart](https://docs.perplexity.ai/docs/decisions/quickstart), [Answer questions reference (OpenAPI)](https://docs.perplexity.ai/api-reference/decisions-post), [pricing](https://docs.perplexity.ai/docs/getting-started/pricing), [ticket-triage cookbook](https://docs.perplexity.ai/docs/cookbook/examples/decisions-api-ticket-triage/README), [Privacy & Security](https://docs.perplexity.ai/docs/resources/privacy-security), [FAQ](https://docs.perplexity.ai/docs/resources/faq), [llms.txt](https://docs.perplexity.ai/llms.txt)
- Perplexity legal: [API terms of service](https://www.perplexity.ai/hub/legal/perplexity-api-terms-of-service), [DPA](https://www.perplexity.ai/hub/legal/dpa), [Trust Center](https://trust.perplexity.ai/)
- [@perplexitydevs launch post](https://x.com/perplexitydevs/status/2105725598882832414) (2026-10-01)
- HF: [`perplexity-ai/pplx-decider-v1-27b`](https://huggingface.co/perplexity-ai/pplx-decider-v1-27b) (README, NOTICE, `config.json`, `decision_config.json`, `release-manifest.json`, `inference.py`, `source/src/autojev/model.py`; [API](https://huggingface.co/api/models/perplexity-ai/pplx-decider-v1-27b)), [`denis-pplx/autojev-27b`](https://huggingface.co/denis-pplx/autojev-27b) (README, NOTICE, `decision_config.json`, tree), [`denis-pplx` profile](https://huggingface.co/denis-pplx)
- [JevBench v1.5.5 API](https://benchmarkheaven.com/api/jevbench/v1.5.5); Decision Index rows via [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021)
- Secondary: [KuCoin news](https://www.kucoin.com/news/flash/perplexity-open-sources-27b-decision-model-outperforms-jev-in-official-tests) (sample count only)

All read 2026-10-02.

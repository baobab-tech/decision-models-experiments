# OpenAI Decisions API

| Field | Value |
|---|---|
| Vendor | OpenAI |
| Type | Decision endpoint: picks one answer from a developer-supplied list; Choice confirmed, Score/Noul unconfirmed |
| Backbone | Specialised GPT-6 Luna, "the cheapest model in the GPT-6 family" |
| Size | Not disclosed |
| Licence | Proprietary; hosted API only |
| Run it via | OpenAI API, selected customers; endpoint not documented |
| Status | Limited preview (announced at DevDay, 2026-09-29) |

Checked 2026-09-30.

## Overview

Developers define a question with a fixed list of answers and pass context as text or images; the API returns one answer from the list.
The Decoder quotes the use cases as "classify content, route requests, or decide an agent's next step".
Pasqualepillitteri.it and The New Stack report a confidence score; OrcaRouter says confidence is not documented in the preview.
OpenAI promised broad availability "in the coming days" (The Decoder).
`developers.openai.com/api/docs/guides/decisions` returned 404, and the GPT-6 Luna model page lists no Decisions endpoint.

## Benchmarks

No OpenAI numbers. Early third-party results ([Every](https://every.to/vibe-check/vibe-check-openai-devday-2026), 2026-09-29):

| Test | Decisions API | Jev |
|---|---|---|
| Text-only computer-use steps (Jack Cheng) | 76/78, ~230 ms | 73/78, ~500 ms |
| Conversation-thread classification (Kieran Klaassen) | accuracy tied, median 309 ms | median 161 ms |

OpenAI claims ~150 ms per decision vs 1.6 s for a standard GPT-6 Luna call (The Decoder); not reproduced.

## Running it

Hosted only. Access requires an OpenAI account enrolled in the preview; there is no public enrolment page.

## Data governance

OpenAI's general API terms; whether each applies to the Decisions preview is not stated.

| Item | Status (OpenAI API in general) | Evidence |
|---|---|---|
| Self-host | No | |
| Fine-tuning | n/d | |
| Processing location | Data residency in 10 regions incl. US and Europe; Decisions not listed | [OpenAI: Your data](https://developers.openai.com/api/docs/guides/your-data) |
| EU processing option | GPT-6 Luna: EU residency on Standard, Flex, Batch (10% premium); n/d for Decisions | [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna) |
| Retention / ZDR | Abuse-monitoring logs "up to 30 days"; Decisions not on the ZDR-eligible list | [OpenAI: Your data](https://developers.openai.com/api/docs/guides/your-data) |
| Training on inputs | No, unless you opt in | [OpenAI: Your data](https://developers.openai.com/api/docs/guides/your-data) |
| DPA / GDPR | DPA offered for API customers | [OpenAI DPA](https://openai.com/policies/data-processing-addendum/) |
| Certifications | SOC 2 Type 2 on the trust portal (not re-checked, unverified) | [trust portal](https://trust.openai.com/) |

## Caveats

- Not documented: endpoint path, request/response schema, auth, price, rate limits, answer-count limit, context window, multi-label, calibration, ZDR and residency for this endpoint.
- Reference price: GPT-6 Luna on the regular API is $0.10 per 1M input and $0.50 per 1M output tokens.
- All facts come from DevDay coverage and systemonemodels.org; OpenAI's DevDay recap returned 403.

## Sources

- OpenAI: [DevDay 2026 recap](https://openai.com/index/devday-2026-recap/) (403), [GPT-6 Luna](https://developers.openai.com/api/docs/models/gpt-6-luna), [Your data](https://developers.openai.com/api/docs/guides/your-data), [DPA](https://openai.com/policies/data-processing-addendum/), [trust portal](https://trust.openai.com/)
- [systemonemodels.org: OpenAI Decisions API](https://systemonemodels.org/models/openai-decisions-api/)
- [The Decoder](https://the-decoder.com/openai-expands-codex-and-its-api-at-devday-with-security-scans-a-decisions-api-and-ultrafast/)
- [The New Stack](https://thenewstack.io/openai-decision-api-luna/)
- [Every: Vibe Check, DevDay 2026](https://every.to/vibe-check/vibe-check-openai-devday-2026)
- [OrcaRouter](https://www.orcarouter.ai/blog/openai-decisions-api-gpt-6-luna)
- [Pasquale Pillitteri](https://pasqualepillitteri.it/en/news/19372/openai-decisions-api-jev)

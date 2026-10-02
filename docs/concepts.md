# Concepts

Terminology for System One decision models. Sources checked 2026-09-30. Most releases date from September 2026; most claims come from vendors or secondary coverage.

## Definition

A System One model reads a piece of content (the *state*) and answers typed questions about it with probabilities, in a single forward pass, without generating text ([glossary](https://systemonemodels.org/glossary/system-one-model)).

- Each question gets a typed answer (an option, a score or a yes-probability) plus the distribution behind it.
- Application code reads the answers and owns all control flow and side effects ([How to build](https://systemonemodels.org/guides/how-to-build-with-system-one-models/)).
- Output tokens are zero or unbilled: Jev charges $0.042 per 1M input tokens with free output ([Jev pricing](https://systemonemodels.org/guides/jev-speed-and-pricing/)); Liquid d1 returns `usage.output_tokens = 0`.
- "System Two" is a contrast term, not a product: an LLM that reasons, plans or writes text. In Jev-Mem, a System Two LLM writes the final answer and a System One controller makes the frequent structured choices ([Jev-Mem](https://huggingface.co/papers/2609.23986)).
- The pair comes from Kahneman's *Thinking, Fast and Slow* (2011) via Bengio's NeurIPS 2019 keynote. TypeSafe AI coined "System One model" as a product category at Jev's launch ([Latent Space](https://www.latent.space/p/jev)).

## Typed-question format

A request carries one `state` and a map of named `questions`, all answered against the same state in one call ([Choice, Score and Noul](https://systemonemodels.org/guides/choice-score-noul/), [TypeSafe API docs](https://docs.typesafe.ai/api)).

| Type | Answers | Limits (Jev) | Returned fields |
|---|---|---|---|
| Choice | one option from a set you define | up to 255 options | `choice`, `confidence`, `probabilities` |
| Score | a position on ordered levels | 2–10 levels | `score` (probability-weighted mean level index), `confidence`, `legend`, `probabilities` |
| Noul | a yes/no question | — | `noul`: probability of yes |

- A Score with probabilities `{0: 0.0, 1: 0.7, 2: 0.3}` is 1.3; it can land between levels.
- Noul has no `confidence`; values near 0.5 mean yes and no are about equally likely.
- "Noul" is called "Noulli" (from Bernoulli) in the launch podcast ([Latent Space](https://www.latent.space/p/jev)); TypeSafe's docs do not explain the name ([glossary: Noul](https://systemonemodels.org/glossary/noul)).

### Request and response shape

`POST https://api.typesafe.ai/v1/systemone`, bearer auth. OpenAPI document `https://api.typesafe.ai/openapi.json` (version 0.2.0), paraphrased from [jevwiki](https://jevwiki.ai/wiki/reference/openapi-schemas.md).

```json
{"model": "jev-1.13.0",
 "state": "Customer: my parcel arrived broken, I want my money back.",
 "questions": {
   "department": {"type": "choice", "instructions": "Which team should handle this ticket?", "criteria": {"returns": "Refunds, returns, damaged goods", "shipping": "Delivery delays and tracking", "billing": "Charges and invoices"}},
   "urgency": {"type": "score", "instructions": "How urgent is this ticket?", "criteria": ["Can wait a week", "Handle today", "Handle now"]},
   "wants_refund": {"type": "noul", "instructions": "The customer asks for a refund.", "criteria": {"true": "Explicit refund request", "false": "No refund request"}}}}
```

```json
{"model": "jev-1.13.0",
 "answers": {
   "department": {"type": "choice", "choice": "returns", "confidence": 1.0, "probabilities": {"returns": 1.0, "shipping": 0.0, "billing": 0.0}},
   "urgency": {"type": "score", "score": 1.3, "confidence": 0.54, "legend": {"0": "Can wait a week", "1": "Handle today", "2": "Handle now"}, "probabilities": {"0": 0.0, "1": 0.7, "2": 0.3}},
   "wants_refund": {"type": "noul", "noul": 0.99}},
 "usage": {"input_tokens": 0, "output_tokens": 0}}
```

Answer objects are from [Choice, Score and Noul](https://systemonemodels.org/guides/choice-score-noul/) with labels matched to the request; `usage` values are placeholders.

- `state`: string, object or array. `questions`: at least one.
- Choice `criteria`: object, option → description. Score `criteria`: array of levels, lowest first (the 2–10 limit is in prose, not the schema). Noul `criteria`: optional `true` / `false` object.
- `instructions`: optional; can reference fields of a JSON state with backticks.
- Errors: 401 invalid key, 422 validation failure, 429/529 rate-limited or overloaded.
- Versions: `jev-latest` alias or pinned (`jev-1.13.0`). Jev's context is 64K tokens per request, of which state plus the longest single question can use at most 32K ([TypeSafe models page](https://docs.typesafe.ai/models)). This explains the 32K figure in [longjev](https://github.com/avshalomd/longjev).
- [NoulXP](https://github.com/systemonemodels/noulxp) (Apache-2.0, spec 0.2, formerly OpenDXP) is an open standard whose HTTP binding reuses this path and shape; it also covers packaging, calibration and MCP serving. It is not affiliated with TypeSafe.

### Vendor differences

| Model | Vendor | Question types | Endpoint / wire format | Status | Weights |
|---|---|---|---|---|---|
| [Jev 1.13](models/jev.md) | TypeSafe AI | Choice, Score, Noul | `POST https://api.typesafe.ai/v1/systemone` (reference) | early access | closed |
| [d1](models/liquid-d1.md) | Liquid AI | Choice, Score, Noul | `POST https://api.liquid.ai/decisions/v1/systemone`, model `d1:free`; TypeSafe-compatible | released 2026-09-29 | closed |
| [GLiDE](models/glide.md) | Fastino | Choice, Score, Noul | `POST https://api.fastino.ai/v1/systemone`, model `fastino/GLiDE`; same structure, not a drop-in (auth header, Score fields); 255 options, 40K tokens per question | released 2026-09-30 | closed |
| [Decider 1](models/decider-1.md) | meraGPT | Choice, Score, Noul | `POST https://meragpt.com/v1/systemone`; TypeSafe-compatible, 10 options, 4,096-token context | GA | closed |
| [Solar Decide](models/solar-decide.md) | Upstage | Choice, Score, Noul | `POST https://api.upstage.ai/v1/systemone`; also OpenRouter `upstage/solar-decide`; 26 options, 512K context | beta | closed |
| [Tev1](models/tev1.md) | Together AI | Choice only (one letter, no distribution) | Together chat completions, model `together/Tev1-4B-experimental`; not TypeSafe-compatible | early access | public, ungated HF weights (licence "being finalized"); community GGUF |
| [Span-01](models/span-01.md) | Respan | Noul-like: present / absent / not observable per behaviour | `POST https://api.respan.ai/api/v1/scores`; not TypeSafe-compatible | GA | closed |
| [OpenAI Decisions API](models/openai-decisions-api.md) | OpenAI | Choice (others unconfirmed) | undocumented | limited preview | closed |
| [GLiNER2.5-Decide](models/gliner-decide.md) | Fastino | Choice, Score, Noul equivalents; multi-label | own `gliner2` schema; hosted `https://api.fastino.ai` | released | Apache-2.0 |
| [Kev](models/kev.md) | Jared Palmer | Choice, Score, Noul | TypeSafe-compatible local server (`kev.serve`) | released | Apache-2.0 |
| [CLM-8B](models/clm-8b.md) | Contrastive-LM | Choice, Score, Noul | TypeSafe requests replay through the CLM client | released | Apache-2.0 |
| [Laya](models/open-reproductions.md#laya) | Convai Innovations | Choice, Score, Noul | TypeSafe-shaped (`laya-serve`) | released | Apache-2.0 |
| [AnyJev](models/anyjev.md) | Nokia | choice, boolean, score | own Python API | released | Apache-2.0 library |
| [Bonsai-Llama-Jev](models/bonsai-llama-jev.md) | Aron Homberg | Choice, Score, Noul | local `/v1/systemone` server | released | MIT code; Apache-2.0 weights |

## Calibration

A model is calibrated when its stated probabilities match observed frequencies: of answers given at 0.8, about 80% are correct.

- **Expected Calibration Error (ECE).** Bin predictions by confidence; average the gap between mean confidence and accuracy per bin, weighted by bin size. Depends on the binning, so report it.
- **Brier score.** Mean squared difference between the predicted probability vector and the one-hot outcome; penalises miscalibration and wrong answers.
- **Reliability diagram.** Confidence bins against accuracy; a calibrated model lies on the diagonal.
- **Coverage at fixed error.** Share of traffic that can be auto-decided below a target error. AnyJev on Qwen3-8B, BANKING77: 7.7% → 52% at 5% error.

How vendors calibrate:

- **Jev:** RLCD ("Reinforcement Learning for Calibrated Decisions") on synthetic data; unpublished. `confidence` is computed from the distribution; formula unpublished ([Jev architecture](https://systemonemodels.org/guides/jev-architecture/)).
- **Laya:** RL against strictly proper scoring rules, also called RLCD.
- **Kev:** one temperature per checkpoint: Kev-27B 1.32 (v2, `main` since 2026-09-30; v1 1.38), 9B 2.30, 4B 2.41, 0.8B 2.35. Kev-9B ECE on new sources 0.106 → 0.042 ([jaredpalmer/kev](https://github.com/jaredpalmer/kev)).
- **AnyJev:** batch calibration (divide out the running mean prediction at 0.75 strength after 8 items), optional temperature scaling. Qwen3-8B on BANKING77: ECE 0.240 → 0.095.

Measured calibration of Jev: AI/ML API (900 examples) found ECE 0.032–0.096 on classification and 0.284 on a rating task ([aimlapi.com](https://aimlapi.com/blog/what-is-jev)). MindStudio found 88% mean confidence against about 80% accuracy on BANKING77; temperature scaling cut the error by about two thirds ([mindstudio.ai](https://www.mindstudio.ai/blog/jev-vs-classic-classifiers-benchmark)). No cross-vendor calibration benchmark exists.

### Thresholds and abstention

- The application owns the thresholds. Starting points: confidence below 0.5 is uncertain; require 0.9 before destructive actions ([How to build](https://systemonemodels.org/guides/how-to-build-with-system-one-models/)).
- Three-band Noul: block above 0.8, allow below 0.2, review between.
- Abstention routes to a fallback: a System Two LLM, a human queue or a default. AI/ML API escalated low-confidence Jev answers to Claude Opus 5.5 and matched its accuracy at 38–45% of its cost.
- Fit thresholds on held-out data from your distribution. The Decision Index scores abstentions as wrong.
- Keep arithmetic, date comparisons, consistency checks and hostile-input screening in application code.

```python
a = resp["answers"]
if a["wants_refund"]["noul"] > 0.9 and a["department"]["choice"] == "returns":
    issue_refund()            # destructive: high bar
elif a["department"]["confidence"] < 0.5:
    escalate_to_llm_or_human()
else:
    route(a["department"]["choice"])
```

## Architectures

Backbone families (BERT-family encoders, Qwen and Gemma decoders, training-free wrappers, hosted APIs), their readouts, sizes and trade-offs are in [model-classes.md](model-classes.md).
Jev's architecture is not public; TypeSafe has disclosed a single query per request, typed distributions, RLCD on synthetic data and text-only input.
A single non-autoregressive pass removes test-time computation, so these models cannot "think longer" on harder inputs.

## Use cases

Routing and tool dispatch (Choice); ticket triage (Choice + Score + Noul); moderation and guardrails (per-policy Nouls); confidence-gated tool-call approval; agent memory control (Jev-Mem: LLM-as-judge 0.777 vs 0.700 on LoCoMo); reranking, RAG filtering and structured extraction ([examples](https://systemonemodels.org/examples)).

## Comparison with classic zero-shot classifiers

NLI zero-shot (`facebook/bart-large-mnli`) runs one pass per label and returns uncalibrated entailment softmax. LLM logprob readouts carry position and tokenisation bias and bill output tokens. Embedding + logistic regression and fine-tuned encoders need labelled data and retraining for new labels.
System One models add calibration-trained probabilities, several mixed-type questions per call, and instructions at request time ([Is Jev just a zero-shot classifier?](https://systemonemodels.org/guides/is-jev-just-a-classifier/)).
A fair baseline set: NLI zero-shot, GLiNER2.5-Decide, an open LLM with logprobs (raw and through AnyJev), embedding + logistic regression, and a fine-tuned encoder. Report accuracy, ECE, Brier, coverage at fixed error, p50/p95 latency and cost per 1K decisions.

## Many-label classification

### Single-choice vs multi-label

- **One Choice** gives a softmax over all options, assuming exactly one label applies; up to 255 options on Jev.
- **Many Nouls**, one per label, give independent yes-probabilities for labels that can co-occur ([opentweet.io](https://opentweet.io/jev/choice-score-noul)).
- **Hybrid.** A Choice over a coarse taxonomy, then Nouls to confirm the leaf or add tags.
- **Above 255 options.** A Choice over groups, then a Choice inside the winning group; one request per level ([opentweet.io](https://opentweet.io/jev/classification)).
- GLiNER2.5-Decide supports multi-label and cross-answer rules natively.
- Add an "other" option when the set may be incomplete.

### Effect of option count and input length

Rows marked (inference) follow from the architecture, not measurement.

| Architecture | More options | Longer input | Cost |
|---|---|---|---|
| Jev (API) | option text adds input tokens; 77-class intent routing trailed flagship LLMs by about 7 points | 375 ms at 1K tokens, 734 ms at 32K (attributed to [longjev](https://github.com/avshalomd/longjev); not in its README or results, unverified); accuracy drops with irrelevant detail | input only; ~260 overhead tokens per request |
| Encoder (GLiNER2.5-Decide, Laya) | options share the encoder context (inference) | Laya 512 tokens (en), 1,024 (mmBERT); 2,000-token documents need chunking | local; quadratic attention cost (inference) |
| Decoder + pointer head (Kev) | each option adds prompt tokens | Qwen base context; hybrid DeltaNet checkpoints need one pass per question | local |
| Decoder logprobs (AnyJev) | L0 cyclic shifts: passes scale with option count (inference) | decoder context | local; vLLM prefix caching helps |
| Contrastive (CLM-8B) | action embeddings cached; one dot product per option | state encoded once | local; cached scoring 0.6 ms on RTX 4090 |

### Published comparisons on many-class tasks

| Task (classes) | System One result | Baselines | Source |
|---|---|---|---|
| BANKING77 (77), zero-shot | Jev 79.2–80.1% | 22M encoder + LR 93.2%; NLI 66.7% / 48.8% | [mindstudio.ai](https://www.mindstudio.ai/blog/jev-vs-classic-classifiers-benchmark) |
| BANKING77 (77), 24 retrieved examples in state | Jev 92.40% (n=3,080; $0.44) | fine-tuned BERT 93.66% | [simonmesmith](https://github.com/simonmesmith/jev-banking77-experiment) |
| SST-2, AG News, Emotion, BANKING77, mean | Jev 79.3%, 381 ms | ModernBERT cross-encoder 78.7%; bi-encoder 69.9% at 15.7 ms | [dylantom2012](https://huggingface.co/blog/dylantom2012/i-benchmarked-jev-against-open-cpu-only-stacks-it) |
| CLINC150 (150) | Jev 87% | gpt-5.4-nano 80%; GPT-5.6 Terra 92% | search summary (unverified) |
| Fast Decisions (17 datasets) | GLiNER2.5-Decide 60.2% (card; blog 60.1%) | JevK5 57.6%, Laya 46.6% (vendor suite) | [Fastino blog](https://fastino.ai/blog/gliner-2-5-decide-open-weight-decision-model) |
| KLUE-YNAT (7), Korean | Kev / Winnow 73–74%; AnyJev 75–76% | — | [local-jev-bench](https://github.com/tak-bro/local-jev-bench) |

A supervised encoder beat zero-shot Jev by about 13 points on BANKING77; retrieved labelled examples in the state closed most of the gap.
No published study covers 100+ multi-label tags, Choice vs many-Noul formulations, or accuracy as a function of option count. Leaderboards (Decision Index, JevBench) are in [benchmarks.md](benchmarks.md).

## Timeline

| Date | Event |
|---|---|
| 2011 / 2019-12 | Kahneman, *Thinking, Fast and Slow* / Bengio's System 1–2 NeurIPS keynote |
| 2025-07-24 | GLiNER2 paper |
| 2026-09-15 | TypeSafe AI launches Jev |
| 2026-09-18 | Convai releases Laya |
| 2026-09-21 | Jev-Mem on arXiv; Kev on Hacker News |
| 2026-09-22 | meraGPT Decider 1; Upstage Solar Decide (beta); Decision Index 0.1 posted; GPT-6 Luna (base of OpenAI's Decisions API) |
| 2026-09-23 | Together AI Tev1; CLM-8B; Nokia AnyJev |
| 2026-09-24 | Fastino GLiNER2.5-Decide; Respan Span-01 |
| 2026-09-26 | Decision Index 0.2.1 |
| 2026-09-29 | Liquid AI d1; OpenAI Decisions API (limited preview) |
| 2026-09-30 | Kev-27B `main` becomes v2; Fastino GLiDE (blog; press release 2026-10-01) |

## Glossary

- **State.** The content the questions are about: ticket, document, transcript or JSON object.
- **Question.** A named, typed prompt about the state: Choice, Score or Noul.
- **Criteria.** The options (Choice), ordered levels (Score) or true/false definitions (Noul).
- **Confidence.** A 0–1 statistic computed from an answer's distribution; not returned for Noul.
- **Calibration.** Agreement between stated probability and observed frequency.
- **RLCD.** Reinforcement Learning for Calibrated Decisions; TypeSafe's unpublished method. Convai uses the name for RL against proper scoring rules.
- **Abstention.** Declining to act on an answer below a threshold and routing it elsewhere.

## Sources

- systemonemodels.org: [models](https://systemonemodels.org/models), [glossary](https://systemonemodels.org/glossary/), [Choice, Score and Noul](https://systemonemodels.org/guides/choice-score-noul/), [How to build](https://systemonemodels.org/guides/how-to-build-with-system-one-models/), [Is Jev just a zero-shot classifier?](https://systemonemodels.org/guides/is-jev-just-a-classifier/), [Jev architecture](https://systemonemodels.org/guides/jev-architecture/), [examples](https://systemonemodels.org/examples)
- TypeSafe [API docs](https://docs.typesafe.ai/api); [jevwiki OpenAPI reference](https://jevwiki.ai/wiki/reference/openapi-schemas.md); [Latent Space podcast](https://www.latent.space/p/jev); [NoulXP](https://github.com/systemonemodels/noulxp); [Jev-Mem](https://huggingface.co/papers/2609.23986); [jaredpalmer/kev](https://github.com/jaredpalmer/kev); MarkTechPost on [d1](https://www.marktechpost.com/2026/09/29/liquid-ai-releases-d1-a-decision-model-that-returns-calibrated-probabilities-with-zero-output-tokens/) and [AnyJev](https://www.marktechpost.com/2026/09/23/nokia-open-sources-anyjev-a-training-free-layer-that-turns-any-open-llm-into-a-calibrated-decision-model/)
- Evaluations: [AI/ML API](https://aimlapi.com/blog/what-is-jev), [MindStudio](https://www.mindstudio.ai/blog/jev-vs-classic-classifiers-benchmark), [simonmesmith](https://github.com/simonmesmith/jev-banking77-experiment), [dylantom2012](https://huggingface.co/blog/dylantom2012/i-benchmarked-jev-against-open-cpu-only-stacks-it), [local-jev-bench](https://github.com/tak-bro/local-jev-bench), [longjev](https://github.com/avshalomd/longjev), [opentweet.io](https://opentweet.io/jev/classification)
- Timeline (checked 2026-09-30): [GLiNER2 on arXiv](https://arxiv.org/abs/2507.18546), [Kev on HN](https://news.ycombinator.com/item?id=49783999), [Decision Index Space commits](https://huggingface.co/spaces/multimodalart/jev-decision-index/commits/main), GPT-6 Luna creation date on [OpenRouter](https://openrouter.ai/openai/gpt-6-luna) and [Vercel AI Gateway](https://ai-gateway.vercel.sh/v1/models), [Kev-27B commits](https://huggingface.co/jaredpalmer/kev-27b/commits/main)
- Vendor-specific claims: the model docs in [models/](models/).

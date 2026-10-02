# Decision-Jef-0.1 (BarraHome / bet0x)

| Field | Value |
|---|---|
| Vendor | Hugging Face user `BarraHome`, GitHub `bet0x`; LICENSE names "Decision-Jef contributors" |
| Type | Open-weight encoder decision model: probabilities for Choice, Score and Noul over options supplied at runtime, no generated text |
| Backbone | [`jhu-clsp/mmBERT-base`](https://huggingface.co/jhu-clsp/mmBERT-base) (ModernBERT, 22 layers, hidden 768, 256k-token vocabulary), full fine-tune plus a small query/option projection head (`proj_dim` 256) |
| Size | 307,336,448 parameters (F32 safetensors, HF API) |
| Licence | MIT, weights and code. Base model MIT. Commercial use allowed by the licence; see training-data caveat |
| Run it via | `pip install decision-jef` (PyPI 0.8.1, 2026-09-24): Python `Decider.decide(...)`, or `decision-jef-serve` for a local `POST /v1/systemone` |
| Status | Created 2026-09-21 (21:42 UTC); last modified 2026-09-24. Revision `b0ebfbd`. 459 downloads (30 days), 2 likes. GitHub [`26fa12e`](https://github.com/bet0x/decision-jef/commit/26fa12ea777b844f1864a0e8b6fd242855f447a4) (2026-09-24) |

Checked 2026-10-02.

## Overview

Decision-Jef answers several questions about one state in a single forward pass ([card](https://huggingface.co/BarraHome/Decision-Jef-0.1)).
The answer space is built from the options in the request; there is no fixed label head.
The state is encoded once; each question block attends to the state and to itself, and position IDs restart after the state for every question.
The card says adding a question does not change another question's answer: four packing layouts agree "to every digit reported" in fp32 across all 2,000 benchmark decisions.
Releases 0.5–0.8.1 (2026-09-23 to 2026-09-24) added training on game-agent states (Doom, Flappy Bird, Snake) and four third-party demo rule sets.
The 0.8.1 weights trade 0.50 points of benchmark accuracy for Flappy Bird; the 0.8.0 weights (78.00) stay at revision `5a015f6c`.
No relation to TypeSafe, OpenJev, or the [jeff](jeff.md) server.

## Schema

Two interfaces ([card, Usage](https://huggingface.co/BarraHome/Decision-Jef-0.1#usage)):

- **Python:** `d.decide(state, {"id": Question(type, instructions, criteria)})` returns per-question `choice`, `p("true")`, `confidence` and `probabilities`. `d.to_wire(answers)` gives a Jev-style JSON body. Plain dicts raise `TypeError`.
- **HTTP:** `decision-jef-serve` serves `POST /v1/systemone` on `127.0.0.1:8088` and returns `{"answers": {...}}`, each with `latency_ms`. `GET /health` returns `{"status": "ok"}`. `--token` enables Bearer auth; without it, any key is accepted.

| Type | `criteria` | Answer |
|---|---|---|
| `choice` | ordered map of key → description, 2 to 255 | `choice`, `probabilities` |
| `noul` | optional `false` / `true` descriptions ("supply it") | `noul` probability |
| `score` | ordered array of 2 to 10 level descriptions | probability-weighted `score`, `legend` |

Differences from Jev's validation: the server answers a one-option `choice` itself (probability 1, `"forced": true`) instead of returning `422`, and it flattens structured `instructions` or `state` objects to text.
Requests are serialised behind a lock (no concurrent forward passes).
TypeSafe-compatible: yes for the path and body, per the card; the card shows two Doom agents switched by a one-line URL change.

## Benchmarks

**LocalLLaMA typed-decisions** test split (2,000 decisions: 600 choice, 600 noul, 800 score), author's run, raw probabilities, single measurement ([card, Results](https://huggingface.co/BarraHome/Decision-Jef-0.1#results)):

| Model | Global | Choice | Noul | Score |
|---|---:|---:|---:|---:|
| Decision-1.0-Lex (`llm-semantic-router`) | 78.15 | 74.00 | 84.67 | 76.38 |
| **Decision-Jef-0.1 (0.8.1)** | 77.50 | 75.70 | 84.30 | 73.90 |
| Laya typed-decisions | 76.60 | 73.33 | 85.67 | 72.25 |
| Jev | 72.70 | n/p | n/p | n/p |

| Metric | Decision-Jef | Laya | Jev |
|---|---:|---:|---:|
| ECE, 10 bins | 0.011 | 0.213 | 0.144 |
| Brier, summed over classes | 0.112 | 0.061 (per-class convention) | 0.148 |
| Score MAE | 0.273 | 0.242 | 0.391 |

- The dataset card's own boards ([LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions), rev `d0e2f0c`) list Jev 1.13.0 at 0.727 and laya-typed-decisions at 0.766 (fitted on `train`). Decision-Jef has no row there, so its 77.50 is unchecked.
- Whether Decision-Jef's training data includes the typed-decisions `train` split is not stated. The card's comparison set (Lex, Laya) are fitted models. Scores above the 0.735 teacher self-agreement mean "learning the teacher's quirks", per the dataset card.
- Option order: the benchmark puts the gold answer third 39.7% of the time. Permuting options moves global accuracy from 77.55 to 77.60; the answer changes on 5.3% of 1,800 permutations.
- Option-count sweep (author, banking intents): 0.915 at 5 options, 0.770 at 20, 0.625 at 65. The card says Jev "is reported at 0.870" at 65 (source not given, unverified).
- New state formats: on Doom agent states the 0.4.0 weights scored 37.4% with constant high-confidence answers; after 20,000 rule-labelled examples, 99.7% on 3,194 held-out decisions.
- No row on Decision Index 0.2.1, JevBench v1.5.4, S1MB, kyr0, 4nt0ineB or Fastino fast-decisions as of 2026-10-02 ([benchmarks-leaderboards.md](../benchmarks-leaderboards.md); [S1MB results](https://huggingface.co/datasets/hotchpotch/s1mb-result)). [landscape.md](../landscape.md) records "77.30 global" from an earlier release.

## Running it

From the [card](https://huggingface.co/BarraHome/Decision-Jef-0.1#usage):

```bash
pip install decision-jef
decision-jef-serve            # 127.0.0.1:8088, weights from the Hub
```

```python
from decision_jef import Decider, Question, email

d = Decider.from_pretrained("BarraHome/Decision-Jef-0.1")
state = email.as_state("user@acme.com", "Duplicate charge on invoice #4411",
    "We were billed twice for March. Please refund the duplicate today or we will cancel our plan.")
answers = d.decide(state, {
    "department": Question("choice", "Which department should handle this?", {
        "billing": "invoices, payments, refunds", "technical": "bugs, outages, system errors",
        "sales": "pricing, new contracts", "other": "everything else"}),
    "churn_risk": Question("noul", "Does the user threaten to leave?", {
        "false": "The user makes no threat to stop using the service.",
        "true": "The user threatens to cancel, churn or leave."}),
})
```

Documented answers: `department` → `billing` (0.9997); `churn_risk` → 0.988.

- **Latency** (author, H100 NVL, fp32, median of 30): 11.69 ms for one question, 12.13 ms for four. bf16 "roughly halves these numbers". Batch 64 at 1,024 tokens: 5.36 ms per decision.
- **Mac (M5 Max):** CPU fp32 through the package. `device="auto"` picks CUDA or CPU only ([`infer.py`](https://github.com/bet0x/decision-jef/blob/main/decision_jef/infer.py)); passing `device="mps"` is undocumented (unverified). The encoder also loads as a plain `ModernBertModel` in Transformers. No ONNX, MLX or GGUF build.
- `model.safetensors` only; no pickle and no remote code.
- **Noul descriptions matter:** with no `false`/`true` text, noul accuracy drops from 83.83 to 66.17; templated text ("No. <question>.") gives 65.33.

## Scaling limits

- **Context:** 1,024 tokens per packed sequence (`max_len`, default); long states are truncated with questions reserved first. The backbone supports 8,192 positions.
- **Options:** 255 per Choice; 2–10 Score levels. The card advises `shortlist_decide(..., k=16)` above about 20 options.
- **Questions per call:** no cap found; all share the 1,024-token window.
- **Concurrency:** one request at a time per server process.
- **Language:** trained and measured on English only; multilingual use "untested".

## Fine-tuning

- **Training code: not public.** The GitHub repo and PyPI package hold inference, packing, the server and `verify.py`, but no training script ([repo](https://github.com/bet0x/decision-jef), `26fa12e`).
- **Data (card):** part of the corpus is [`tasksource/tasksource-jev-typed-decisions`](https://huggingface.co/datasets/tasksource/tasksource-jev-typed-decisions) (`license: other`; draws on 571 upstream sources). The card says the per-source licence review "has **not** been done for this release". The rest is project-generated data and [`tasksource/procedural-typed-decisions`](https://huggingface.co/datasets/tasksource/procedural-typed-decisions) (formerly `procedural-jev`, Apache-2.0, procedurally generated).
- **Reported hardware, time, cost:** none.
- **Apple Silicon training:** no code to run.
- **HF Jobs flavor (estimate):** none applies until code is released. A custom fine-tune of a 307M fp32 encoder at 1,024 tokens would fit `l4x1` (24 GB, $0.80/h) or `a10g-small` ($1.00/h). Our estimate, not a measured run ([rates](https://huggingface.co/docs/hub/jobs-pricing)).
- The shipped `temperatures.json` raises ECE from 0.011 to 0.017; the card says to refit on your own data or leave it off.

## Data governance

Not legal advice. Decision-Jef has no hosted API; every row below is for running it on your own infrastructure.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; offline once weights are cached (`--weights` accepts a local directory) | [card](https://huggingface.co/BarraHome/Decision-Jef-0.1#serving-an-existing-jev-client) |
| Fine-tuning | No public training code | [repo](https://github.com/bet0x/decision-jef) |
| Processing location | Your infrastructure. `inference: false` on the card (no HF inference widget) | HF API, 2026-10-02 |
| EU processing option | Self-host in the EU | |
| Retention / ZDR | The server logs one line per request unless `--quiet`; contents not documented (unverified) | [card](https://huggingface.co/BarraHome/Decision-Jef-0.1#serving-an-existing-jev-client) |
| Training on inputs | No; inference is local | |
| DPA / GDPR | Not applicable when self-hosted: no processor | |
| Certifications | None (open-source project) | |
| Network exposure | Binds `127.0.0.1` by default; any bearer value is accepted unless `--token` is set | [card](https://huggingface.co/BarraHome/Decision-Jef-0.1#serving-an-existing-jev-client) |
| Weights licence | MIT (`cardData`, LICENSE). Base `jhu-clsp/mmBERT-base` MIT | HF API, 2026-10-02 |
| Training data | Partly `license: other` with no per-source review; the card asks users to "say so downstream" where data licensing matters | [card, License and provenance](https://huggingface.co/BarraHome/Decision-Jef-0.1#license-and-provenance) |

## Caveats

- **Commercial use:** the MIT licence allows it, and the card is tagged `commercial-use`. The card itself says the training data is unreviewed for licences; treat it as unreviewed.
- All benchmark numbers are the author's own single runs.
- The card states "A state format this model has not seen produces a constant answer with high confidence"; its 0.011 ECE is in-distribution only.
- The escalation head was removed; `with_escalation=True` returns `None`.
- Date conflict: [landscape.md](../landscape.md) lists 2026-09-22; the HF API `createdAt` is 2026-09-21T21:42Z.

## Sources

- [Model card](https://huggingface.co/BarraHome/Decision-Jef-0.1) and [HF API](https://huggingface.co/api/models/BarraHome/Decision-Jef-0.1) (`b0ebfbd`), [`config.json`](https://huggingface.co/BarraHome/Decision-Jef-0.1/blob/main/config.json)
- [GitHub bet0x/decision-jef](https://github.com/bet0x/decision-jef) (`26fa12e`): README, `decision_jef/infer.py`, `decision_jef/wire.py`, `decision_jef/serve.py`, LICENSE
- [PyPI decision-jef](https://pypi.org/project/decision-jef/) (0.8.1)
- [jhu-clsp/mmBERT-base](https://huggingface.co/jhu-clsp/mmBERT-base); [tasksource-jev-typed-decisions](https://huggingface.co/datasets/tasksource/tasksource-jev-typed-decisions); [procedural-typed-decisions](https://huggingface.co/datasets/tasksource/procedural-typed-decisions)
- [LocalLLaMA/typed-decisions card](https://huggingface.co/datasets/LocalLLaMA/typed-decisions) (`d0e2f0c`); [S1MB results dataset](https://huggingface.co/datasets/hotchpotch/s1mb-result) (`09cf4c0`)
- HF Jobs rates: [jobs-pricing](https://huggingface.co/docs/hub/jobs-pricing)

All read 2026-10-02.

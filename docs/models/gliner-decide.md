# GLiNER2.5-Decide (Fastino)

| | |
|---|---|
| Vendor | Fastino Labs (fastino.ai) |
| Type | Encoder-only classification ("decision") model; no generated tokens |
| Backbone | `microsoft/deberta-v3-large` (24 layers, hidden 1024); `base_model` `fastino/gliner2-large-v1`; `span` head (`SpanExtractor`) |
| Size | 340M parameters per card; `model.safetensors` 1.95 GB fp32 |
| Licence | Apache 2.0 (weights, `gliner2` package, `fast-decisions` dataset) |
| Run it via | `uv pip install "gliner2[local]"`, then `AutoExtractor.from_pretrained("fastino/GLiNER2.5-Decide")`; hosted at `https://api.fastino.ai` |

Checked 2026-09-30. Not run locally; no weights downloaded.

## Overview

- HF repo [`fastino/GLiNER2.5-Decide`](https://huggingface.co/fastino/GLiNER2.5-Decide), released 2026-09-24, last modified 2026-09-28; 34,664 downloads at check time. English only. Siblings: [`GLiNER2.5-multi-Decide`](https://huggingface.co/fastino/GLiNER2.5-multi-Decide) (287M, multilingual) and [`GLiNER2.5-Decide-1B`](https://huggingface.co/fastino/GLiNER2.5-Decide-1B).
- Scope per card: intent, routing, sentiment, document type, handoff, agent completion, moderation, severity, urgency, spam, yes/no over a passage, ordinal scores. It does not reason, explain or answer open questions.
- Adds multi-label questions and cross-question rules decoded jointly, which Jev lacks.
- Framework paper: [GLiNER2, arXiv:2507.18546](https://arxiv.org/abs/2507.18546).

## Schema

Own Python API (`gliner2` 2.0.0), not the `/v1/systemone` wire format. Read from the package source and tutorials. Request (typed questions with a rule, tutorial 14; untested with this checkpoint):

```python
from gliner2.classification import Classifier, ClassificationSchema, constraints as C
clf = Classifier.from_pretrained("fastino/GLiNER2.5-Decide")
schema = (ClassificationSchema()
    .single("intent", ["refund_request", "cancel_subscription", "login_problem", "other"])     # Choice
    .ordinal("urgency", ["0", "1", "2", "3", "4", "5"])                                        # Score
    .single("wants_human", ["yes", "no"], instruction="Is the customer asking for a human agent?")  # Noul
    .constrain(C.implies(("wants_human", "yes"), C.min_level("urgency", "3"))))
r = clf.classify("Third time asking about my refund. Get me a person now.", schema)
```

Response (`ClassificationResult`): `r.value("intent")`, `r.selected(...)`, `r.confidence(...)`, `r.probabilities("urgency")` → `{"0": p, ..., "5": p}`, `r.feasible`, `r.violations`, `r.to_dict()`.

| Shared type ([concepts.md](../concepts.md#typed-question-format)) | Decide equivalent | Difference |
|---|---|---|
| Choice | `.single(name, labels)`; labels may be `{label: description}` | No 255-option cap; bounded by the encoder window |
| Score | `.ordinal(name, levels)` | Returns one level; compute Σ level·p from `.probabilities()` for a fractional score |
| Noul | `.single(name, ["yes", "no"], instruction=...)` | Read P(yes) from `.probabilities(name)["yes"]` |
| (none) | `.multi(name, labels, min_labels=0)` and constraints | Multi-label and cross-question rules |

- `.task(...)` kwargs: `min_labels, max_labels, ordered, threshold, candidate_threshold, activation ("auto"|"sigmoid"|"softmax"), temperature, default, instruction, examples`.
- Constraints: `C.implies`, `iff`, `excludes`, `not_`, `all_of`, `any_of`, `exactly_one_of`; `at_least`, `at_most`, `exactly`; `at_level`, `min_level`, `max_level`, `between_level`; `any_selected`, `any_other_selected`. Conditions are `(task, label)` tuples; `C.implies` also accepts a nested constraint (per `_expr` in `constraints.py`; the tutorial shows only tuples).
- Unsatisfiable schemas raise `SchemaError`; infeasible assignments raise or report `InfeasibleError`. Decoders: `"auto" | "independent" | "exact" | "beam"`. Tutorials use `fastino/gliner2.5-multi-v1`. `Classifier.from_pretrained` loads via `AutoExtractor`, so it should accept this span checkpoint (unverified).
- Simpler path: `classify_text(text, {"intent": [...], "urgency": [...]})` scores independent heads in one pass and returns `{"intent": "request", ...}`. It takes `{"labels", "multi_label", "cls_threshold"}` or `{"labels", "prompt"}` dicts and enforces no cross-task rules.

## Benchmarks

[`fastino/fast-decisions`](https://huggingface.co/datasets/fastino/fast-decisions) (Fastino-built, Apache 2.0): 17 English domains, 300 test rows each (5,100), exact-match accuracy, same labels for every model.

| Model | Avg exact match |
|---|---:|
| GLiNER2.5-Decide (340M) | 60.2% |
| GLiNER2.5-Decide-1B | 59.6% |
| JevK5 (presumably Jev, unverified) | 57.6% |
| GLiNER2.5-multi-Decide (287M) | 56.7% |
| SemIf (Qwen3.5-4B) | 56.4% |
| GLiFormer large-v1 | 49.0% |
| Laya Router | 46.6% |

- Source: model and dataset cards. The [blog](https://fastino.ai/blog/gliner-2-5-decide-open-weight-decision-model) and MarkTechPost report 60.1% and 57.5%; the dataset card labels the 59.6% row "GLiNER2 XL (1B)".
- Decide led 9 of 17 domains; support intent 75.3%, banking intent 64.3%. No independent replication found. Blog latency, batch 1, two heads, 15 labels, p50 at 64 / 1,024 tokens: 48-vCPU Xeon 8581C 167.3 ms / —; T4 43.6 / —; L4 43.4 / 131.4; V100 38.3 / 75.6; A100 47.3 / 52.6 ms. No Apple Silicon numbers.

## Running it

Local on Apple Silicon. The card's bare `pip install gliner2` installs only the API client; local inference needs the `[local]` extra (torch, transformers <5, safetensors, peft). Python ≥ 3.10.

```bash
uv venv --python 3.10 .venv && source .venv/bin/activate
uv pip install "gliner2[local]==2.0.0"
hf download fastino/GLiNER2.5-Decide   # optional prefetch, ~1.95 GB
```

```python
import os; os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
from gliner2 import AutoExtractor
model = AutoExtractor.from_pretrained("fastino/GLiNER2.5-Decide")  # map_location="mps" for GPU (unverified)
print(model.classify_text(
    "Subject: Protocol update — action required today\n\nPlease confirm the new retention rule is applied before Friday's audit.",
    {"intent": ["fyi", "request", "approval", "complaint"], "urgency": ["low", "normal", "high", "critical"],
     "route": ["support", "billing", "legal", "security"]}))
# card's "potential output": {"intent": "request", "urgency": "high", "route": "legal"}
```

- `map_location` calls `model.to(...)`; the package has no MPS-specific inference code. CPU is supported. Other load options: `quantize=True`, `compile=True`, `word_splitter=...`.
- Hosted API: `https://api.fastino.ai` (override with `GLINER2_API_BASE_URL`); keys at agent.fastino.ai. Auth header `X-API-Key: $FASTINO_API_KEY` per `SKILL.md`, but the 2.0.0 client reads `PIONEER_API_KEY`.
- API operations (`SKILL.md`): `GET /v1/models`, `POST /v1/chat/completions`, dataset upload, `POST /v1/training-jobs`, checkpoint deploy ([OpenAPI](https://docs.fastino.ai/openapi.json)). `from gliner2 import API` mirrors `classify_text`; it takes no model argument, so which model serves a call is undocumented (unverified). Decide pricing is unpublished. models.dev lists a different model, `gliner2.5-base-v1`, at $0.03 per million input tokens (unverified).

## Scaling limits

- **Options:** no cap in the inference code; the training sampler caps at `max_num_labels = 1000`. Labels are serialised into the same encoder sequence as the text, so every label costs tokens and attention is quadratic in total length.
- A 100-label head adds a few hundred subword tokens, more with descriptions (estimate, unverified). No published curve beyond 15 labels. Workaround: a coarse head, then the chosen branch's sub-labels.
- **Multi-label:** supported via `.multi(...)` with `min_labels`/`max_labels` and `C.at_most`/`C.at_least`, or `classify_text` with `multi_label: True, cls_threshold: 0.4`.
- **Input length:** `max_position_embeddings: 512` with relative attention, so longer inputs run without error; training length is undocumented (unverified). Fastino's latency table runs 1,024 tokens. `classify_text(max_len=N)` truncates to the first N whitespace words.
  Long inputs: `classify_text_long(...)` or `Classifier.classify_long(text, schema, chunk_size=384, chunk_overlap=64, aggregate="max")`, counted in whitespace words; constrained runs aggregate logits then decode once.
- **Cost growth:** ~100 tokens is one pass (~170 ms on the Xeon). ~2,000 tokens is 5–6 chunks at the defaults, and latency scales with chunk count; single-pass at 2,000 is untested (unverified).

## Fine-tuning

Full or LoRA, locally with `uv pip install "gliner2[train]==2.0.0"` or hosted via `POST /v1/training-jobs`.

```jsonl
{"input": "My card PIN is locked.", "output": {"classifications": [{"task": "intent", "labels": ["card_pin_change", "card_lost", "balance_inquiry"], "true_label": ["card_pin_change"]}]}}
```

```python
from gliner2.training.trainer import ExtractorTrainer, TrainingConfig  # model loaded as in Running it
lora = TrainingConfig(output_dir="./decide_lora", use_lora=True, lora_r=16, lora_alpha=32, lora_dropout=0.1,
                      lora_target_modules=["encoder"], save_adapter_only=True, task_lr=5e-4, num_epochs=10, batch_size=16)
ExtractorTrainer(model, lora).train(train_data="train.jsonl", eval_data="val.jsonl")  # load: model.load_adapter("./decide_lora/final")
```

- Optional fields: `multi_label`, `prompt`, `examples`, `label_descriptions`. `TrainingDataset` validates JSONL without torch.
- Tutorial full fine-tune defaults: 15 epochs, batch 16, encoder LR 1e-5 (range 1e-6 to 5e-5), task LR 5e-4 (1e-4 to 1e-3), cosine, early stopping. It calls LoRA "often comparable" and suggests 100–1,000+ examples per domain.
- The trainer picks CUDA or CPU; no MPS branch, and fp16/bf16 are off on CPU. LoRA with small batches is the practical local option (estimate, unverified). No published training times.
- `SKILL.md`: test the base model first, run a small pilot, compare LoRA vs full, keep an untouched test split.

## Data governance

Not legal advice.

| Field | Self-hosted weights | Fastino hosted API (`api.fastino.ai`) |
|---|---|---|
| Processing location | Your hardware. | US on AWS ([Trust & Safety](https://docs.fastino.ai/trust-safety)). |
| EU region | Yes, if hosted in the EU. | None as of 2026-09-30; all subprocessors are US. |
| Retention | You control it; inference runs in-process. | Inputs and outputs "retained indefinitely" by default. `store: false` per request gives zero retention "for eligible use cases"; team-wide ZDR may disable some models ([privacy policy](https://agent.fastino.ai/privacy)). |
| Trains on inputs | No. | Yes by default; opt-out for enterprise only. Inference data also trains your own task models regardless. ZDR data is never used. |
| DPA / GDPR | Not applicable. | "At this time, we do not offer a Data Processing Addendum (DPA)". Requests: security@fastino.ai. |
| Certifications | Not applicable. | SOC 2 Type II and ISO 27001 in progress; first audit expected November 2026. |
| Subprocessors | None. | AWS, Anthropic, Intercom, OpenAI, Twilio (SendGrid), Amplitude, Vercel, Supabase, Modal, Microsoft Azure, Datadog, Sentry, Stripe, Attio, Linear; all US; list dated 2026-07-30. |
| Self-host / air-gap | Yes: download once, load from a local path (air-gap untested). | No. |
| Fine-tuning | Yes, full or LoRA (see [Fine-tuning](#fine-tuning)). | Yes, `POST /v1/training-jobs`; `GET /v1/training-jobs/{job_id}/download` exists. Data and checkpoints stored until deleted. |
| Weights licence | Apache-2.0 for Decide, multi-Decide and Decide-1B ([HF API](https://huggingface.co/api/models/fastino/GLiNER2.5-Decide)); keep licence and NOTICE. | Same weights; API under Fastino's [terms](https://agent.fastino.ai/terms). |

- The privacy policy (Fastino, Inc., effective 2026-08-06) routes prompts to "upstream inference providers", including OpenAI and Anthropic. Which requests reach them is undocumented. For EU personal data, self-hosting is the only option with EU-only processing and no vendor training.

## Caveats

- Parameter count: 340M (card, blog), 355M (fastino.ai/models); the 1.95 GB fp32 file implies ~486M stored values, and DeBERTa-v3-large is ~435M with embeddings. 340M may exclude embeddings (unverified).
- MPS inference and `Classifier` with this span checkpoint are untested. Card outputs are labelled "potential results". Label-count and long-input accuracy scaling are unmeasured.

## Sources

- Model: [HF card](https://huggingface.co/fastino/GLiNER2.5-Decide) (README, SKILL.md, configs), [HF API](https://huggingface.co/api/models/fastino/GLiNER2.5-Decide), [fast-decisions](https://huggingface.co/datasets/fastino/fast-decisions), [blog](https://fastino.ai/blog/gliner-2-5-decide-open-weight-decision-model), [models page](https://fastino.ai/models), [X launch post](https://x.com/fastinoAI/status/2103188985292157353)
- Code: [fastino-ai/GLiNER2](https://github.com/fastino-ai/GLiNER2), [PyPI gliner2 2.0.0](https://pypi.org/project/gliner2/) (sdist: `auto.py`, `inference/runtime.py`, `classification/*`, `processor.py`, `models/loading.py`, `training/trainer.py`, `api_client.py`; tutorials 8, 9, 10, 12, 14), [arXiv:2507.18546](https://arxiv.org/abs/2507.18546)
- Coverage: [MarkTechPost 2026-09-24](https://www.marktechpost.com/2026/09/24/fastino-releases-gliner2-5-decide-a-340m-open-weight-decision-model-that-runs-on-cpu/), [systemonemodels.org launch page](https://systemonemodels.org/examples/tools/gliner-2-5-decide-launch/), glossary [Noul](https://systemonemodels.org/glossary/noul/), [Score](https://systemonemodels.org/glossary/score/), [opentweet.io](https://opentweet.io/jev/choice-score-noul), [models.dev PR #8312](https://github.com/anomalyco/models.dev/pull/8312)
- Governance: [Trust & Safety](https://docs.fastino.ai/trust-safety), [privacy policy](https://agent.fastino.ai/privacy), [terms](https://agent.fastino.ai/terms), [OpenAPI](https://docs.fastino.ai/openapi.json), [Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)

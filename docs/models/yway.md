# Yway (Burmese System One model)

| Field | Value |
|---|---|
| Vendor | Aung Thu Hein (`aungthuhein-dev` on Hugging Face), independent research |
| Type | Decision model for Burmese (Myanmar) text: probabilities for typed questions (Choice, Score, Noul), no generated text |
| Backbone | `FacebookAI/xlm-roberta-base` encoder with Laya's two-layer decision head |
| Size | 293,012,998 parameters stored in F16 (HF API); the report gives 278M for the encoder. 586 MB `model.safetensors` |
| Licence | HF tag `other` (`mit-cc-by-sa-gemma-terms`): code and encoder MIT; Burmese Wikipedia training text CC BY-SA 4.0; part of the training data made with Gemma 3 under the Gemma Terms of Use |
| Run it via | Self-hosted only: `laya.Agent` (PyPI `laya==0.3.22`) or the bundled `serve.py` (`POST /v1/systemone`). No public API |
| Status | First release; repo created 2026-10-01, last commit 2026-10-02. Technical report is a non-peer-reviewed preprint |

Checked 2026-10-02.

## Overview

Yway (ရွေး, "choose") answers typed questions about Burmese text in one encoder pass per question.
It reuses Laya's `DecisionModel` and training loop and swaps Laya's mmBERT encoder for XLM-RoBERTa-base ([report](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/resolve/main/report.pdf), §4).
XLM-R tokenizes Burmese at 2.93 characters per token against 1.28 for mmBERT, measured on 200 Burmese Wikipedia passages.
A median passage needs 338 XLM-R tokens against 781 mmBERT tokens.
All training data comes from Burmese Wikipedia (dump of 2026-09-01, 37,159 articles after removing bot-made pages) and Gemma 3 outputs.
The repo ships 30 question presets in `presets.json` with the trained Burmese wordings; the card says the model "is sensitive to question wording".

| Repo | HF sha | Created | Downloads (30 d) | Likes |
|---|---|---|---:|---:|
| [`aungthuhein-dev/yway-system1-xlmr`](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr) | `7249a12` | 2026-10-01 | 0 | 0 |

The repo has no root `config.json` (the encoder config sits in `encoder/`), so HF's download counter may stay at 0 regardless of use ([HF docs](https://huggingface.co/docs/hub/models-download-stats)).
The model has no row in [landscape.md](../landscape.md); [scan-2026-10-02.md](../scan-2026-10-02.md) lists it as not documented.

## Schema

Jev wire format, served by `serve.py` ([card](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr)):

- `POST /v1/systemone` with `{"state", "questions"}` returns `{"model", "answers", "usage"}`.
- `POST /v1/systemone/batch` takes `{"states": [...], "questions"}`.
- `GET /v1/presets` returns the 30 presets. `GET /health` returns model and device.
- A question is a full Jev definition (`type`, `instructions`, `criteria`) or a preset name string, for example `"topic": "topic"`. Preset names are a Yway extension.
- Types: `choice`, `noul` (P(true)), `score` (ordered levels). No multi-label type.
- Optional auth: set `YWAY_API_KEY` and send `X-Yway-Key`. This header differs from TypeSafe's.
- TypeSafe-compatible: yes for the request and response shape (unverified against the TypeSafe SDK). The `confidence` formula is Laya's.

## Benchmarks

No third-party results. Yway has no row on Decision Index 0.2.1, JevBench, kyr0, 4nt0ineB or Fastino fast-decisions as of 2026-10-02.

### Author's test split

Held-out Wikipedia articles and question wordings not seen in training (card; [round 3 report](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/blob/main/reports/round3.md)).

| Decision | Type | Accuracy | ECE |
|---|---|---:|---:|
| Question type (8) | choice | 0.994 | 0.006 |
| "Does this question ask about X?" (8) | noul | 0.992 | 0.010 |
| Passage answers question | noul | 0.916 | 0.015 |
| Topic (12 categories) | choice | 0.858 | 0.114 |
| Passage relevance (0–2) | score | 0.855 | 0.034 |
| Answer correct according to passage | noul | 0.803 | 0.013 |
| Register, formal vs spoken (held out of training) | choice | 0.512 (chance 0.5) | n/d |

- Answer checker on 2,000 real Gemma 3 12B answers: at P(correct) ≥ 0.5 it keeps 68% of correct answers and catches 81% of wrong ones. Shown-answer quality rises from 0.438 to 0.681.
- Answers with one changed number are judged right only 45% of the time.
- Few-shot: adding 300 labelled `register` examples (plus 3× replay, 3 epochs) took it from 0.527 to 0.989, with old-task mean accuracy 0.876 ([round 2](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/blob/main/reports/round2.md)).
- A plain fine-tuned XLM-R-base classifier scored 0.896 on 12-topic classification against 0.845–0.858 for Yway's `topic` question. The report explains the gap by truncation: at 512 tokens the 12 Burmese option descriptions leave about 550 characters for the text.

### Author's comparison with Jev and Laya

600 Burmese test decisions (100 per task, seed 2026) from Yway's own test split, sent one request at a time with Burmese instructions ([benchmark note](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/resolve/main/benchmark.pdf), October 2026). Accuracy with 95% bootstrap intervals; ECE with 10 bins.

| Task | Yway | Jev (`jev-latest`, zero-shot) | Laya multilingual (zero-shot) | ECE Yway / Jev / Laya |
|---|---:|---:|---:|---|
| Topic (12) | 0.87 (0.80–0.93) | 0.79 (0.71–0.86) | 0.15 | 0.105 / 0.127 / 0.694 |
| Question type (8) | 0.99 (0.97–1.00) | 0.90 (0.84–0.95) | 0.12 | 0.008 / 0.043 / 0.360 |
| Passage answers question | 0.91 (0.85–0.96) | 0.95 (0.90–0.99) | 0.42 | 0.043 / 0.067 / 0.457 |
| Passage relevance (0–2) | 0.83 (0.75–0.90) | 0.89 (0.82–0.95) | 0.39 | 0.056 / 0.073 / 0.249 |
| Answer correct (real Gemma 3 12B answers) | 0.76 (0.68–0.84) | 0.78 (0.70–0.86) | 0.46 | 0.048 / 0.106 / 0.452 |
| Mean of these 5 | 0.872 | 0.862 | 0.308 | |
| Register, formal vs spoken (no system trained on it) | 0.45 (0.35–0.55) | 0.97 (0.93–1.00) | 0.55 | 0.268 / 0.079 / 0.110 |
| Mean of all 6 | 0.802 | 0.880 | 0.348 | |

Latency per question, one request at a time:

| System and place | Median ms | p90 ms | Batched questions/s |
|---|---:|---:|---:|
| Yway, H200 MIG slice (3g.71gb) | 6.0 | 58.5 | 627 (batch 8) |
| Laya multilingual, same slice | 62.8 | 66.0 | 200 (batch 32) |
| Jev API from the author's HPC cluster (with network) | 274.8 | 326.2 | n/a |
| Yway, 4 CPU threads | 421.6 | 573.6 | 1.8 |
| Yway, Railway CPU container (with network) | 697.3 | 922.3 | n/a |

- Jev cost $0.031 for the 600 questions, about 1,200 input tokens per question at $0.042 per 1M ($0.05 per 1,000 questions).
- With English instructions, Yway's 6-task mean drops from 0.802 to 0.765; Jev's from 0.880 to 0.867.
- The author notes a "home advantage": items, labels and judge are the same ones that produced Yway's training data. At 100 items per task, intervals are about ±0.07, so only the question-type and register gaps are clear.
- CPU and Railway timings used 180 items (30 per task).
- Data governance of that run: Burmese Wikipedia-derived text (public, CC BY-SA 4.0) went to TypeSafe's API (`api.typesafe.ai`); the serving region is not stated.

## Running it

```bash
python -m venv .venv && source .venv/bin/activate
python -m pip install "laya==0.3.22" "transformers>=4.48,<5" huggingface_hub sentencepiece torch
```

```python
import json, laya
from huggingface_hub import hf_hub_download, snapshot_download
repo = "aungthuhein-dev/yway-system1-xlmr"
model_dir = snapshot_download(repo)
presets = json.load(open(hf_hub_download(repo, "presets.json"), encoding="utf-8"))
agent = laya.Agent(model_dir, device="cpu")
result = agent.predict({"text": "မာရသွန်ပြေးပွဲသည် ၁၈၉၆ ခုနှစ် အိုလံပစ် အားကစားပြိုင်ပွဲတွင် စတင် ပါဝင်ခဲ့သည်။"},
                       {"topic": presets["topic"], "is_sports": presets["topic_is.sports"]})
```

HTTP server: `pip install fastapi uvicorn`, `hf download aungthuhein-dev/yway-system1-xlmr --local-dir yway`, `python yway/serve.py` (binds `0.0.0.0:8000` by default; set `YWAY_HOST=127.0.0.1` for local only).

Mac path (M5 Max, 128 GB): CPU works as documented. `laya` supports MPS ([laya.md](laya.md)), so `laya.Agent(model_dir, device="mps")` should work (unverified for Yway). `serve.py` auto-detects only CUDA or CPU; set `YWAY_DEVICE=mps` to try MPS (unverified). The author's public demo runs on a CPU container on Railway behind a Vercel function (report §6).

## Scaling limits

- **Context:** 512 tokens; longer inputs are truncated from the end. The answer checker places the answer before the passage for this reason.
- **Per request (`serve.py`):** 32 questions, 64 states per batch, 20,000 characters of serialized state.
- **Options:** no documented maximum; the head reads one `[MASK]` per option inside the 512-token window (`head_max_len` 336 in `rl_agent_config.json`).
- **Language and domain:** Burmese only; trained mainly on Wikipedia. News, social media and spoken Burmese are untested.
- **New decisions:** no zero-shot transfer; about 300 labelled examples are needed.

## Fine-tuning

- **Training code:** not public. The round reports quote "the Yway training code (not part of this repository)". The method is Laya's training loop (`laya` 0.3.22), which is open ([NandhaKishorM/laya](https://github.com/NandhaKishorM/laya), Apache-2.0).
- **Method:** REINFORCE against the group mean over four noisy copies of the logits (σ 0.4 to 0.1), rewarded with log, spherical and ranked-probability scores, plus soft cross-entropy. AdamW at 2.5·10⁻⁵ (encoder) and 10⁻⁴ (head), 64 sequences per update, 2 epochs per round, bf16. One temperature per type fitted on validation: 1.360, 1.664, 1.596 (`rl_agent_config.json`).
- **Data:** 60,000 training cases built from [`aungthuhein-dev/burmese-wiki-qa`](https://huggingface.co/datasets/aungthuhein-dev/burmese-wiki-qa) (251,642 pairs generated by Gemma 3 27B, CC-BY-SA-4.0, sha `18be8fb`) and [`aungthuhein-dev/burmese-wiki-topics`](https://huggingface.co/datasets/aungthuhein-dev/burmese-wiki-topics) (CC-BY-SA-4.0, sha `da9c86a`). Round 3 adds 22,000 Gemma 3 12B answers graded by Gemma 3 27B; that set's publication is not documented (unverified).
- **Hardware and time:** one NVIDIA H200 MIG slice (3g, 71 GB) (report §4.3). `rl_agent_config.json` records 15,987 updates, 4 epochs completed and 4.97 h for the released checker. Adding a new decision took "a few minutes on one GPU slice". Cost is not stated.
- **Mac training:** not documented for Yway. Laya ships an MPS training script ([laya.md](laya.md#fine-tuning)); running it with an XLM-R encoder is untested (unverified).
- **HF Jobs flavor (estimate):** l40sx1 ($1.80/h, 48 GB) fits a 278M encoder at 512 tokens and batch 64 in bf16. At about 5 h, a full retrain costs about $9. A few-shot add-on run would cost well under $1. a10g-small (24 GB) may need gradient accumulation.

## Data governance

Not legal advice. Self-hosted only; no vendor service.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes, on your infra (CPU, or CUDA GPU) | card |
| Fine-tuning | Yes, with Laya's open training loop on your infra; Yway's own scripts are not public | card, round reports |
| Processing location | Your infra | |
| EU processing option | n/a (self-hosted) | |
| Retention / ZDR | n/a. `serve.py` keeps no request log in code (unverified beyond a read of the file) | `serve.py` |
| Training on inputs | No | |
| DPA / GDPR | n/a; no hosted service | |
| Certifications | None | |
| Weights licence | `other`: MIT (code, XLM-R encoder) + CC BY-SA 4.0 (Wikipedia text) + Gemma Terms of Use (generated questions, answers and grades) | card, report §8 |

**Commercial use:** no non-commercial clause appears in any of the three licences.
Two points need review before commercial use.
CC BY-SA 4.0 requires attribution and ShareAlike for adapted material; whether trained weights are adapted material is not settled (unverified).
The Gemma Terms of Use (last modified 2026-04-01) define "Model Derivatives" to include a model trained on synthetic Gemma outputs "in order to cause that model to perform similarly to Gemma" ([terms](https://ai.google.dev/gemma/terms), §1.1(e)). If Yway counts as one, Gemma's use restrictions and prohibited-use policy pass through to it (unverified).

## Caveats

- All results are the author's, on the author's split; the Jev comparison uses 100 items per task.
- Labels come from machines: Gemma 3 27B wrote the Q&A pairs and graded the checker data; topic labels come from Wikipedia categories. No native-speaker check at scale (report §7).
- The parameter count differs between the report (278M) and the stored weights (293M, HF API).
- The card's install line pins `transformers<5`; current `laya` releases may move past 0.3.22.
- Not yet compared: Laya's mmBERT encoder trained on the same 32-task data (report §7).

## Sources

- HF: [model card](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr) (sha `7249a12`), [HF API](https://huggingface.co/api/models/aungthuhein-dev/yway-system1-xlmr), `serve.py`, `presets.json`, `rl_agent_config.json`, `encoder/config.json`, [reports/round1.md](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/blob/main/reports/round1.md), [round2.md](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/blob/main/reports/round2.md), [round3.md](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/blob/main/reports/round3.md)
- Technical report: [report.pdf](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/resolve/main/report.pdf); Zenodo [10.5281/zenodo.23094628](https://doi.org/10.5281/zenodo.23094628) (version 1.0, published 2026-10-02, record licence CC-BY-4.0); [benchmark.pdf](https://huggingface.co/aungthuhein-dev/yway-system1-xlmr/resolve/main/benchmark.pdf) (benchmark note, 6 pages)
- Datasets: [`aungthuhein-dev/burmese-wiki-qa`](https://huggingface.co/datasets/aungthuhein-dev/burmese-wiki-qa) card and API; [`aungthuhein-dev/burmese-wiki-topics`](https://huggingface.co/datasets/aungthuhein-dev/burmese-wiki-topics) API
- [Gemma Terms of Use](https://ai.google.dev/gemma/terms); [HF download stats](https://huggingface.co/docs/hub/models-download-stats); [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing)
- Laya: [laya.md](laya.md) (checked 2026-10-02)

All read 2026-10-02.

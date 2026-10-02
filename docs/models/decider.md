# decider (Mapika)

| Field | Value |
|---|---|
| Vendor | Mark Marosi (HF and GitHub user `Mapika`); independent project, "not affiliated with or endorsed by TypeSafe AI" ([README](https://github.com/Mapika/decider)) |
| Type | Decoder read as a decision model: option-letter logits at one answer slot per question, softmax over the options, divided by a fitted temperature. No generated text |
| Backbone | Qwen3.5-0.8B / 2B / 4B / 35B-A3B-Base; Gemma-4-12B-it (decider-12b); stock Gemma-4-31B-it and Qwen3.6-27B (`decider-chat-*`) |
| Size | 0.75B to 34.7B (3B active); see [Repositories](#repositories) |
| Licence | Apache-2.0 for weights (HF `cardData`) and code; Qwen3.5, Qwen3.6 and Gemma 4 bases are Apache-2.0 |
| Run it via | `pip install decider-ai` (1.8.1, 2026-09-30): `Decider(...)` in Python, or `decider.serve` with `POST /v1/systemone`. GGUF through llama-cpp-python. Large stock models through `decider.serve_vllm`. No hosted API |
| Status | decider-2b v11 (2026-09-24), decider-4b v2.1, decider-12b v2 (2026-09-29), decider-35b-a3b v1, `decider-chat-*` (2026-09-29) |

Checked 2026-10-02. No weights were downloaded and nothing was run.

## Overview

- decider is unrelated to meraGPT's hosted [Decider 1](decider-1.md) (`state-decider-1`).
- One request holds a `state` and typed questions; one forward pass returns a distribution per question ([decider-2b card](https://huggingface.co/Mapika/decider-2b)).
- The prompt is `Context: …`, then per question the lettered options and an answer slot `Answer k: (`. The hidden state at each slot is projected onto the option-letter rows of the LM head.
- Training data: about 95 public decision datasets, agent trajectories (AgentGym), Mind2Web, game states and questions labelled by a local Qwen3.5-27B teacher. The README states "Nothing was distilled from Jev."
- decider-2b history: supervised stages v1 to v8; v10 adds 384 steps of calibration-aware RL on live MiniWoB++ tasks and exact games; v11 adds a merged rank-64 LoRA trained on 42,749 rows. v10 and v8 stay under Hub tags.
- decider-4b v2.1: one supervised pass over "mixture v2" (742M tokens), then a merged rank-64 LoRA on 29,325 rows. No RL stage. v2 and v1 stay under tags.
- decider-12b v2: Gemma-4-12B-it with a merged rank-32 LoRA trained on 6,000 generated state-tracking decisions and 4,000 replayed rows. v1 (stock weights) stays under tag `v1`.
- decider-35b-a3b v1: the supervised recipe with routed experts frozen and the Muon optimizer. The README plans a retrain because its FP32 master-weight setting cost knowledge accuracy in later runs.
- `decider-chat-gemma4-31b` and `decider-chat-qwen3.6-27b` hold unchanged stock weights plus a `decider_config.json`. Only the readout and temperature are added.
- decider-2b-vision uses v5 text weights inside the Qwen3.5-2B vision-language model. A 256×240 frame costs 64 visual tokens. The README says it "is retraining".

### Repositories

HF API, read 2026-10-02. Downloads are the rolling 30-day counter.

| Repo | Version | Base | Params (safetensors) | Weights | Created | Revision | Downloads | Likes |
|---|---|---|---:|---|---|---|---:|---:|
| [decider-0.8b](https://huggingface.co/Mapika/decider-0.8b) | one epoch | Qwen3.5-0.8B-Base | 752,393,024 | 1.4 GB bf16 | 2026-09-19 | `a0a01d6` | 13,442 | 6 |
| [decider-2b](https://huggingface.co/Mapika/decider-2b) | v11 | Qwen3.5-2B-Base | 1,881,825,088 | 3.8 GB bf16 | 2026-09-16 | `533964d` | 275,828 | 97 |
| [decider-4b](https://huggingface.co/Mapika/decider-4b) | v2.1 | Qwen3.5-4B-Base | 4,205,751,296 | 8.4 GB bf16 | 2026-09-22 | `eb5fbdf` | 22,724 | 14 |
| [decider-12b](https://huggingface.co/Mapika/decider-12b) | v2 | gemma-4-12B-it (rev `707f0a3b`) + LoRA r32 | 11,959,730,224 | 24 GB bf16 | 2026-09-29 | `8ac1efa` | 108 | 3 |
| [decider-35b-a3b](https://huggingface.co/Mapika/decider-35b-a3b) | v1 | Qwen3.5-35B-A3B-Base | 34,660,610,688 (3B active) | 65 GB bf16 | 2026-09-20 | `91470e6` | 1,384 | 9 |
| [decider-35b-a3b-nvfp4](https://huggingface.co/Mapika/decider-35b-a3b-nvfp4) | v1 | the 35B in NVFP4 (ModelOpt 0.46.1) | | 19.6 GB | 2026-09-20 | `798555c` | 788 | 7 |
| [decider-2b-vision](https://huggingface.co/Mapika/decider-2b-vision) | v5 text | Qwen3.5-2B vision-language | 2,213,241,664 | 4.1 GB bf16 | 2026-09-16 | `863e290` | 3,705 | 32 |
| [decider-chat-gemma4-31b](https://huggingface.co/Mapika/decider-chat-gemma4-31b) | stock | gemma-4-31B-it (rev `842da379`) | 31,273,088,876 | 62.5 GB bf16 | 2026-09-29 | `22975cb` | 323 | 1 |
| [decider-chat-qwen3.6-27b](https://huggingface.co/Mapika/decider-chat-qwen3.6-27b) | stock | Qwen3.6-27B (rev `6a9e13bd`) | | 55.6 GB bf16 | 2026-09-29 | `f18c938` | 23 | 0 |
| [decider-4b-GGUF](https://huggingface.co/Mapika/decider-4b-GGUF) | v2.1 | decider-4b | | Q4_K_M 2.7 GB, Q8_0 4.5 GB, BF16 8.4 GB | 2026-09-27 | `b79f09d` | 2,523 | 1 |
| [decider-2b-GGUF](https://huggingface.co/Mapika/decider-2b-GGUF) | v11 | decider-2b | | Q4_K_M 1.3 GB, Q8_0 2.0 GB, BF16 3.8 GB | 2026-09-27 | `ff2e5e6` | 1,499 | 0 |
| [decider-2b-coherent](https://huggingface.co/Mapika/decider-2b-coherent) | v1.1 | add-on over decider-2b `533964d` | 9.5M (add-on) | 38 MB | 2026-09-27 | `516f5ca` | 24 | 0 |

- decider-2b has the highest 30-day download count of any decision-model repo found in the HF searches for this doc (2026-10-02). `autotrust/JEV-27B-VL` is next at 179,237 ([autotrust-jev.md](autotrust-jev.md)).
- decider-2b-coherent returns one joint distribution over several questions about one state; it targets BookieBench-style probability questions.
- Third-party conversions (not author-documented): `mradermacher/decider-35b-a3b-GGUF`, `mradermacher/decider-2b-vision-GGUF`, `SirSahOl/decider-2b-chat-mlx-*`, `midium-ai/decider-2b-dwq-4bit`, `midium-ai/decider-4b-dwq-4bit`, `litert-community/decider-2b-vision-LiteRT`, `tielmane/decider-12b-NPU-LPBQ-X-Elite` (Snapdragon NPU port, linked from the README).

## Schema

TypeSafe-compatible: yes. `d.system_one(state, questions)` and `POST /v1/systemone` take Jev's request shape. The README says TypeSafe's SDKs "work unchanged with `TYPESAFE_BASE_URL=http://localhost:8000`".

- **Choice:** 2 to 255 options in `criteria` (name to description, JSON value or `null`). Options beyond 10 use one label token each: A–J, then K–Z and two-letter tokens. Returns `choice`, `probabilities`, `confidence` = `(n·p_max − 1)/(n − 1)` (TypeSafe's formula, since decider-ai 1.3.0), `x_p_max` = top probability, and `certainty` = 1 minus normalised entropy.
- **Score:** 2 to 10 described levels (README). Each level is judged in its own row without its number, then normalised (`"isolated": false` restores listwise scoring). Returns `score` (expected level), `probabilities`, `legend`, `confidence`, `level_fit` and `fit_mass`.
- **Noul:** returns `noul` = P(yes); no `confidence`. `instructions` may be omitted if `criteria` describe true and false.
- `state` may be a string, object or array. `instructions` and option descriptions may be any JSON value. Question ids are never shown to the model.
- Each question runs in its own row by default, so adding or reordering questions does not change other answers. `independent=False` packs questions into one row: about half the latency on short states, and reversing question order changes up to 12% of answers.
- `decide()` and `POST /decide` are a plain form (`question`, `options`). Their `confidence` is still the top probability. `abstain_below=t` returns `None` under threshold `t`.
- `d.schema(questions)` caches a questions-first prefix: 1.2× to 2.4× faster per request and up to 19× per batch, for about 1.5 points accuracy on fixed label sets and 5 points on per-example options. v11 does not mark itself as schema-first trained, so the server leaves the cache off unless `DECIDER_SCHEMA_CACHE=1`.
- Temperatures live in `decider_config.json`: `temperature`, `temperature_by_type` (decider-ai ≥ 1.4.0), and `temperature_by_options` T(n) = max(min, a + b ln n) (≥ 1.8.0, used by `decider-chat-gemma4-31b`). decider-ai 1.3.0 and earlier ignore the maps; argmax answers are unchanged.

## Benchmarks

### Public boards

Decision Index 0.2.1 board: `data/index.json` generated 2026-09-28T00:39Z, still current on 2026-10-02. Ranks count Jev's row, as in [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021). The README counts 70 entrants without Jev, so its ranks are one lower.

| Entry | DI 0.2.1 | Rank (of 71) | ECE | Median ms (RTX PRO 6000) |
|---|---:|---:|---:|---:|
| Jev 1.13.0 (hosted) | 57.91 | 1 | 0.074 | 524.1 (HTTPS) |
| Decider chat · Gemma-4-31B | 57.33 | 3 | 0.047 | 108.5 |
| Decider chat · Qwen3.6-27B | 51.35 | 9 | 0.021 | 83.6 |
| Decider 35B-A3B (NVFP4, per README) | 47.11 | 13 | 0.023 | 101.4 |
| Decider 4B | 40.70 | 20 | 0.084 | 12.6 |
| Decider 2B | 28.97 | 38 | 0.077 | 8.1 |

- The README's per-area panel puts decider-35b-a3b within 0.03 of Jev on language, retrieval, tools and arts, and 0.18 behind on knowledge (0.51 vs 0.69; GPQA, GSM8K, CRUXEval, MMLU).
- `FLock this-that 1.2`, a decider-2b derivative, scores 28.14 ([benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021)).

JevBench v1.5.4 ([API](https://benchmarkheaven.com/api/jevbench/v1.5.4), 106 ranked; ranks re-read 2026-10-02):

| System | Rank | Score | Intelligence | Calibration | Speed | Cost |
|---|---:|---:|---:|---:|---:|---:|
| Jev 1.13.0 | 3 | 72.1 | 72.0 | 88.0 | 83.8 | 54.7 |
| decider-4b v2 | 7 | 71.3 | 55.8 | 85.6 | 90.9 | 64.5 |
| decider-2b | 30 | 45.1 | 42.3 | 71.5 | 94.4 | 64.9 |
| decider-35b-a3b | 43 | 27.5 | 60.5 | 82.0 | 91.0 | 34.4 |

- decider-35b-a3b is gated by the Cost axis: JevBench prices it at the base model's hosted price (README).
- decider-12b is submitted ([jevbench #155](https://github.com/fstandhartinger/jevbench/issues/155)) and absent from v1.5.4 on 2026-10-02.
- No decider row on typed-decision-bench (kyr0), typed-decision-bench (4nt0ineB) or Fastino fast-decisions ([benchmarks.md](../benchmarks.md)).

### Author-reported

From the model cards and README (single runs unless stated):

| Model | Regression set in-task / held-out acc. | JevBench public hard tier (111 items) | Bespoke public suite, macro | Hard-tier ECE |
|---|---|---:|---:|---:|
| decider-0.8b | 0.776 / 0.707 (single-run protocol; 2B 0.809 / 0.739) | n/d | n/d | n/d |
| decider-2b v11 | 0.802 / 0.752 | 0.577 | 0.706 | 0.175 |
| decider-4b v2.1 | 0.831 / 0.784 | 0.649 | 0.756 | 0.18 |
| decider-12b v2 (v1) | not measured | 0.712 (0.730) | n/d | 0.147 (0.098) |
| decider-35b-a3b v1 | 0.855 / 0.810 | 0.676 | 0.774 | 0.15 |
| Jev 1.13.0 | n/d | 0.730 | 0.760 (Bespoke's report) | n/d |

- decider-2b v11 against v10 on the same rows: held-out generated families 0.429 vs 0.324; held-out document questions 0.753 vs 0.646; human-labelled public sets 0.781 vs 0.803; greedy bag-draw play 46.9% vs 57.8%.
- v11 failed its own pre-registered release rule: ECE 0.156 on held-out generated families against a 0.08 limit. The author released it "on a decision made after reading the full comparison".
- GGUF quality (regression set, held-out): 4B Q4_K_M 0.783 and Q8_0 0.783 vs bf16 0.784; 2B Q8_0 0.752 and Q4_K_M 0.747 vs 0.752. Measured on the CUDA build only.
- decider-2b-vision: Visual7W 0.89; Breakout 41 from pixels.
- Speed, decider-2b v10 on one B300 (230-token states, 3 questions): 3.2 ms p50 single request with CUDA graphs; 2,181 decisions/s through the HTTP server at 64 clients.

## Running it

```bash
uv add decider-ai                         # 1.8.1; extras: serve, train, games, gguf, metal
```

```python
from decider.infer import Decider
d = Decider("Mapika/decider-2b")          # CUDA, else MPS (float16), else CPU (float32)
d.system_one({"ticket": "I was charged twice for order A-104. Please refund the duplicate."},
             {"refund_requested": {"type": "noul", "instructions": "Does the ticket request a refund?"},
              "department": {"type": "choice", "instructions": "Which team should handle this?",
                             "criteria": {"billing": "Charges, invoices", "returns": "Exchanges and returns", "other": None}}})
```

HTTP: `scripts/serve.sh Mapika/decider-2b 8000` (from the GitHub clone) listens on 127.0.0.1. `DECIDER_HOST=0.0.0.0` opens it with no authentication. Over-limit requests get `413`; an overloaded server returns `503`.

### Mac (M5 Max, 128 GB)

| Path | Models | Status |
|---|---|---|
| PyTorch MPS, float16 | 0.8B, 2B, 2B vision | Documented. M1 Pro median 133 ms per request with the MPS patch (171 ms without). MASSIVE Scenario accuracy 0.7553 vs 0.756 bf16 (1,500 rows). Merged 2026-09-22 |
| PyTorch MPS, bf16 | 35B-A3B | User report (issue #6) on an M5 Max 128 GB, macOS 26.5: loads in about 60 s with `Decider(path, device="mps", dtype=torch.bfloat16, use_graphs=False)`; reproduced the card's JevBench public counts; 0.23–0.5 s per decision with the MPS MoE patch (decider-ai ≥ 1.1.4). `flash-linear-attention` does not install; install decider-ai with `--no-deps` |
| `decider-ai[metal]` | dense models | Optional MLX/Metal kernel (README); no Mac numbers published |
| GGUF, llama.cpp Metal | 2B v11, 4B v2.1 | `CMAKE_ARGS="-DGGML_METAL=on" pip install "decider-ai[gguf]"`, then `Decider("Mapika/decider-4b-GGUF", gguf_file="decider-4b-v2.1-Q4_K_M.gguf")`. The Metal build was not run over the regression set |
| CPU | all | float32 since 1.7.1 |
| not documented | 4B v2.1 on MPS ("not checked on v2.1"), 12B, `decider-chat-*` | The 31B bf16 weights (62.5 GB) fit in 128 GB; no Mac run reported (unverified) |

- The GGUF files are not chat models. `llama-cli`, `llama-server`, Ollama and LM Studio give a text model; answers come only from the option-letter logits through `Decider` or `decide_gguf.py`.
- Qwen3.5 bases need `flash-linear-attention` (Triton) for speed on CUDA; without it the model runs "several times slower" (decider-2b card). Triton does not run on Mac.

## Scaling limits

- **Options:** 255 per Choice; 10 levels per Score.
- **Context:** 32k tokens for the state plus questions, all sizes (README model table).
- **Questions per call:** no documented maximum. Each question and each Score level is its own row, so compute grows with questions × levels.
- **Many labels:** training sub-sampled to ≤ 10 options per example. CLINC 151-way scores 0.88 with the full set vs 0.98 with 10 sampled options; DBpedia level 2 with 70 labels has ECE 0.14 (decider-2b card).
- **Long JSON arrays:** picking a record by position scores 0.51 with 64 records vs 0.70 with one.
- **GGUF batching:** packing rows into one llama.cpp decode moves probabilities by up to 0.16 at Q4_K_M; `Decider` scores one row per decode.
- **Long shared prefixes:** decider-ai 1.8.1 bounds the shared-prefix forward; a 32-document, ~26k-token retrieval request peaked at 68.5 GB (README, 2026-09-30).
- **Memory:** 2B about 4 GB, 4B 8.4 GB, 35B 65 GB in bf16 (19.6 GB NVFP4, Blackwell only).

## Fine-tuning

- `scripts/train.sh full` builds the public mixture and runs one supervised epoch from Qwen3.5-2B-Base: 1.47M examples, 455M tokens, 5.3 h on a GH200. It matched v9 on the 94-task set (in-task 0.809 vs 0.812).
- `scripts/train.sh delta runs/<model>` continues an existing checkpoint on new formats plus replay.
- `python -m decider.calibrate records.jsonl` fits per-type temperatures by NLL from temperature-1 answers.
- Not in the package: the RL stage (needs a separate research repo, live Chrome and MiniWoB++), the mixture-v2 builders (the public 60% is reproducible), and the LoRA trainer used for v11 and v2.1.
- Training ran on CUDA (GH200, B300). Training on Mac is not documented.
- Replay toward the previous checkpoint's distribution (KL(p_prev ‖ p_model)) limited regressions in v11 and v2.1 ([fine-tuning.md](../fine-tuning.md)).

## Data governance

Not legal advice. All weights are open; there is no vendor API.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes. Self-hosted means your infrastructure; weights and code are public | [HF `Mapika`](https://huggingface.co/Mapika), [GitHub](https://github.com/Mapika/decider) |
| Fine-tuning | Yes, with the published supervised recipe; RL and LoRA stages not packaged | README |
| Processing location | Your infrastructure. The HF Space [`hugging-apps/decider-2b-vision-demo`](https://huggingface.co/spaces/hugging-apps/decider-2b-vision-demo) sends input to Hugging Face | README |
| EU processing option | Yes, on your own EU infrastructure | |
| Retention / ZDR | Your control. No telemetry is documented (unverified) | |
| Training on inputs | No vendor receives inputs | |
| DPA / GDPR | Not needed for self-hosting; no processor | |
| Certifications | n/a | |
| Weights licence | Apache-2.0 (HF `cardData`, not gated). Bases: Qwen3.5 and Qwen3.6 Apache-2.0; Gemma 4 Apache-2.0 ([Gemma 4 licence page](https://ai.google.dev/gemma/docs/gemma_4_license)) | HF API, 2026-10-02 |

- Training data: about 95 public datasets plus labels from local Qwen3.5-27B and Qwen3.6-27B teachers. Per-dataset licences were not reviewed here.
- The server has no authentication. Keep the default 127.0.0.1 bind or put a proxy in front.
- Model repos ship a `decider/` Python inference subset. The documented path imports the `decider-ai` package from PyPI; neither path is reviewed here.
- `main` changes between versions (decider-2b v10 to v11, decider-12b v1 to v2). Pin a `revision`.

## Caveats

- All accuracy and calibration numbers outside DI and JevBench are the author's own.
- The DI score is set mostly by the base model. Two stock models read through the decider readout outscore the trained 35B, 4B and 2B (README).
- Calibration is weak on hard items: hard-tier ECE 0.15–0.18 for the trained models.
- Rules written into a question are not followed at 2B ("a paragraph of rules 0.24" vs "a one-sentence question 0.67" on the form-filling probe).
- English only.
- decider-2b v11 and decider-4b v2.1 each regress on some sets against their previous versions; the cards list when to keep the older tag.
- `decider-12b` v2 is lower than v1 on the JevBench hard tier (79 vs 81 of 111) and less calibrated there.
- decider-2b-vision is on v5 text weights.

## Sources

- [GitHub: Mapika/decider](https://github.com/Mapika/decider) README (What's new to 2026-09-30, Standing read by the author 2026-09-29)
- HF model cards: [decider-0.8b](https://huggingface.co/Mapika/decider-0.8b), [decider-2b](https://huggingface.co/Mapika/decider-2b), [decider-4b](https://huggingface.co/Mapika/decider-4b), [decider-12b](https://huggingface.co/Mapika/decider-12b), [decider-35b-a3b](https://huggingface.co/Mapika/decider-35b-a3b), [decider-35b-a3b-nvfp4](https://huggingface.co/Mapika/decider-35b-a3b-nvfp4), [decider-2b-vision](https://huggingface.co/Mapika/decider-2b-vision), [decider-chat-gemma4-31b](https://huggingface.co/Mapika/decider-chat-gemma4-31b), [decider-chat-qwen3.6-27b](https://huggingface.co/Mapika/decider-chat-qwen3.6-27b), [decider-4b-GGUF](https://huggingface.co/Mapika/decider-4b-GGUF), [decider-2b-GGUF](https://huggingface.co/Mapika/decider-2b-GGUF), [decider-2b-coherent](https://huggingface.co/Mapika/decider-2b-coherent)
- HF API: [`api/models?author=Mapika`](https://huggingface.co/api/models?author=Mapika) and `api/models/Mapika/<repo>` (sha, downloads, likes, safetensors totals)
- [PyPI: decider-ai](https://pypi.org/project/decider-ai/) (1.8.1, uploaded 2026-09-30)
- [Decision Index Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) `data/index.json` (generated 2026-09-28)
- [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4)
- [Gemma 4 licence page](https://ai.google.dev/gemma/docs/gemma_4_license)

All read 2026-10-02.

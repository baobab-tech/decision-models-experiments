# AnyJev

| | |
|---|---|
| Vendor | Nokia applied research (GitHub `nokia-applied-research`). Authors: Jiamu Zhang, Tianze Yang, Liang Wu (Nokia, Sunnyvale, CA); Yucheng Shi (Tencent Hunyuan) |
| Type | Training-free Python library over any open decoder LLM: reads next-token logits over option labels (raw/L0/L1) or fits a closed-form head on a hidden state (L2). No model of its own |
| Backbone | Any open decoder LLM; headline tables use Qwen3-1.7B to Qwen3-32B |
| Size | Library only; shipped L2 heads 1.8–4.4 MB per model |
| Licence | Apache-2.0 (code, `anyjev` package, heads). Base model licence applies separately (Qwen3: Apache-2.0) |
| Run it via | `pip install "anyjev[hf]"`, then `Decider(HFBackend(...))` or `Decider(VLLMBackend(...))`. No HTTP server |

Checked 2026-09-30. Nothing was run locally; no weights were downloaded.

## Overview

- Code: [`nokia-applied-research/AnyJev`](https://github.com/nokia-applied-research/AnyJev) (created 2026-09-21, last push 2026-09-28, 985 stars; README in English and Simplified Chinese). No paper; a technical report is on the roadmap. Not affiliated with TypeSafe or Jev (README).
- PyPI [`anyjev`](https://pypi.org/project/anyjev/): 0.0.1/0.0.2 (2026-09-21), 0.1.0 (09-26), 0.2.0 (09-28); Python ≥ 3.10; core dependency `numpy`; extra `hf`: `torch>=2.3`, `transformers>=4.53`; extra `bench`: `datasets`, `scikit-learn`.
- No HF model repo. Heads ship in `anyjev-heads/` for Qwen3-1.7B, 4B, 8B, 30B-A3B-Instruct-2507, 32B. Announced 2026-09-23 ([MarkTechPost](https://www.marktechpost.com/2026/09/23/nokia-open-sources-anyjev-a-training-free-layer-that-turns-any-open-llm-into-a-calibrated-decision-model/)).
- Levels; every `Decision` carries a `level`, and `require="L1"` etc. refuses weaker answers:

| Level | Needs | Does |
|---|---|---|
| `raw` | nothing | Softmax over label tokens, options in given order. README: "Do not ship it." |
| `L0` | nothing | Cyclic-shift marginalisation (every option in every position; geometric mean in log space) + label-prior correction |
| `L1` | 100–500 labels/question | Temperature scaling on L0 |
| `L2` | 100–300 labels/question | Closed-form head (shrunk LDA or ridge) on the hidden state at ~⅔ depth; one prompt per state |
| `auto` | — | L2 where a head routes, else L1, else L0 |

- L0 (`docs/levels.md`): default prior is batch calibration (Zhou et al., 2024), strength 0.75, from a running per-question mean after 8 items (`min_prior_n`); none before that. The prior accumulates across calls (local-jev-bench restarts its adapter per run). Opt-in `prior="content_free"` (Zhao et al., 2021). Noul reads "Yes or No" and "No or Yes"; Score bins are never permuted. `canonical_order=True` (opt-in in 0.2) makes any listing of an option set give identical probabilities. `adaptive_shifts=True` reads rotations until a log-odds margin clears a threshold certified by `calibrate_adaptive(q, states, target=0.01)` on unlabelled states; README says opt-in in 0.2.0, CHANGELOG says "now the default".
- L2 (`docs/jev_mode.md`): `fit_head(q, states, labels)` is one forward plus a closed-form solve, seconds on CPU; `observe(q, state, label)` solves at 30 labels, re-solving at 60, 120, …. A reworded question drops Qwen3-8B from 0.767 to 0.646–0.701; recentring on 30 unlabelled states recovers 0.742–0.749 (`adapt="routed"`, default). Needs hidden states (transformers backend or vLLM embed server); log-prob-only backends stop at L1. Heads are per (model, question).

## Schema

Python library, no wire format. Example (README, `docs/jev_mode.md`):

```python
from anyjev import Decider, Question
from anyjev.backends.hf import HFBackend

dec = Decider(HFBackend("Qwen/Qwen3-4B"))
dec.load_artifacts("anyjev-heads/Qwen__Qwen3-4B.json")     # shipped heads for the typed questions
q = Question.choice("What should happen next?", ["resolve", "escalate", "wait", "refund"], name="action")
d = dec.decide(ticket_text, [q], level="L2", require="L2")["action"]
d.probs, d.argmax, d.diagnostics["blocks_executed"]
```

| Constructor | Limits | Result fields |
|---|---|---|
| `Question.choice(text, options, name=)` | 2–26 unique options (letter readout, `MAX_OPTIONS = 26`) | `probs`, `distribution`, `argmax`, `answer`, `confidence`, `level`, `diagnostics` |
| `Question.noul(text, name=)` | Yes/No | `p_true` |
| `Question.score(text, bins=5, scale=(0,1))` or `levels=[...]` | 2–10 bins or levels | `value` (bin centres or probability-weighted level index) |

Differences from [../concepts.md](../concepts.md#typed-question-format):

- Choice capped at 26 until a span readout ships (roadmap); no separate option-description field. `confidence` formula not checked (unverified).
- `decide(state, questions, level=, require=)` returns a `DecisionSet` keyed by name; `decide_batch` runs many states.
- No `/v1/systemone` server. The roadmap lists a Jev-compatible server (`POST /v1/decisions`, conformance suite) as open. MarkTechPost's "Jev-compatible interface" means the typed-question semantics (inference). local-jev-bench's `serve/anyjev_server.py` wraps AnyJev in `/v1/systemone` (`model`: `anyjev-raw` or `anyjev-l0`).
- Backends: `HFBackend` (transformers), `VLLMBackend` (HTTP `/v1/completions`, `/v1/embeddings`), `fake`. Tested models: Qwen3, OLMo, Granite, Phi, Mistral (MarkTechPost); `docs/results_small_models.md` adds SmolLM2-1.7B, Qwen2.5-7B, OLMo-2-7B, Granite-3.3-8B, Phi-4-mini, Mistral-7B-v0.3.

## Benchmarks

Vendor, Qwen3-8B, BANKING77 20-way, 300 test items:

| | raw | L0 | L1 |
|---|---:|---:|---:|
| Labels | none | none | 100–500 |
| Flips when options reversed | 0.230 | 0.073 | 0.077 |
| Accuracy | 0.747 | 0.803 | 0.807 |
| ECE | 0.240 | 0.184 | 0.095 |
| Auto-decidable at ≤ 5% error | 7.7% | 46.3% | 52.0% |

L2 on `LocalLLaMA/typed-decisions` (20 questions × 300 fit labels, 2,000 held-out decisions):

| Model | L0 | L2 | Block read | L2 cost vs one forward |
|---|---:|---:|---|---:|
| Qwen3-1.7B | 0.494 | 0.730 | 18 / 28 | 0.70× |
| Qwen3-4B | 0.564 | 0.786 | 24 / 36 | 0.69× |
| Qwen3-8B | 0.647 | 0.771 | 24 / 36 | 0.68× |
| Qwen3-30B-A3B | 0.630 | 0.799 | 40 / 48 | — |
| Qwen3-32B | 0.700 | 0.798 | 52 / 64 | 0.84× |

- Reference: Jev (published by others) 0.727; Laya fine-tuned 421M (measured) 0.768. Pooled L2 ECE 0.03–0.05. Qwen3-8B L2 by label count: 20 → 0.654, 50 → 0.707 (ECE 0.11), 100 → 0.740, 300 → 0.772 (ECE 0.03).
- typed-decisions gold is one teacher LLM's soft label; a fresh teacher sample agrees 0.735 of the time. Rotation budget: 7.2 of 18 rotations at a certified 1% target; 2.2× decisions/s on vLLM, 2.3–2.7× on transformers; accuracy 0.703 vs 0.697 (Qwen2.5-7B, massive_route).
- Latency, H100: L0 ~0.25 s per decision at batch 32, K = 20 (MarkTechPost). L2 shipped heads (batch 16, 300–400-token states): 1.7B 5.9 ms, 4B 10.5 ms, 8B 14.5 ms.
- README numbers regenerate from committed JSON (`bash scripts/regen_docs.sh`). Coverage at 5% risk is high-variance at n = 300 (README).

Independent: [local-jev-bench](https://github.com/tak-bro/local-jev-bench), M3 Max 36 GB, Qwen3-8B on vllm-metal, AnyJev 0.1.0:

| Set | raw | L0 | Kev-4B |
|---|---:|---:|---:|
| English 30 items | 82% | 81% | 89% |
| BANKING77-20 | 75% | 80% | 89% (in Kev's training data) |
| transfer-v4 (764) | 75% | 75% | 80% |
| typed-decisions (2,000) | 61% | 63% | 67% |
| NSMC / KLUE-YNAT (ko) | 81% / 76% | 80% / 75% | 83% / 74% |

- Reproduced README BANKING77-20: flips 68/300 → 22/300, accuracy 224/300 → 241/300 (paired p = 0.005).
- typed-decisions distributions far from gold: KL 3.78 (raw) / 2.81 (L0), ECE 0.35 / 0.31. First-call p50: raw 204–1,508 ms; L0 391–2,554 ms, 7,860 ms on 20-way BANKING77.

## Running it

```bash
uv add "anyjev[hf]"                          # vendor: pip install "anyjev[hf]"
hf download Qwen/Qwen3-8B                    # standard hf usage
python -m demo.jev_mode --backend fake       # no-GPU check (README)
```

- `HFBackend(model_name, device="cuda", dtype="bfloat16")` defaults to CUDA; `device="mps"` follows the same `.to(device)` path (unverified on Apple Silicon; not documented by the vendor). The backend avoids `device_map` because it "segfaults outright" on Apple Silicon (issue #5).
- L2 works only on this backend or a vLLM embed server. `load_artifacts` needs the question layout to match a shipped question; a new question needs L0 or its own head. No MLX or Ollama backend (Ollama does not expose per-label logprobs or hidden states; inference).
- End-to-end measurement: `python -m anyjev.pipeline Qwen/Qwen2.5-7B-Instruct --labels-from banking20`.
- vLLM route (README, CUDA): `python -m anyjev.truncate Qwen/Qwen2.5-7B-Instruct 18 ./qwen-b18` keeps ~⅔ of blocks, then `vllm serve ./qwen-b18 --task embed --override-pooler-config '{"pooling_type":"LAST","normalize":false,"softmax":false}'`. Zero-label L0: `Decider(VLLMBackend("http://localhost:8000", "./qwen-b18"), adaptive_shifts=True)`, `calibrate_adaptive(route, unlabelled_tickets, target=0.01)`, `decide_batch(tickets, route)`.
- Mac vLLM recipe (local-jev-bench; vllm-metal 0.30.0, AnyJev 0.1.0, raw/L0 only): `brew tap vllm-project/vllm-metal https://github.com/vllm-project/vllm-metal` (the tap needs the URL), `brew install vllm-project/vllm-metal/vllm-metal`, then `VLLM_ENABLE_V1_MULTIPROCESSING=0 GLOO_SOCKET_IFNAME=lo0 VLLM_HOST_IP=127.0.0.1 vllm serve "$model" --served-model-name "$name" --max-model-len 4096 --gpu-memory-utilization 0.7 --host 127.0.0.1 --port "$port"`.
  - vllm-metal 0.30.0 reports logprobs before the `allowed_token_ids` filter, so a label can drop out of the top K; the adapter requests each label by id (`logprob_token_ids`).
  - The vLLM backend imports `transformers` only for the tokenizer; no torch on the client. Qwen3-8B reserved about 20 GB at 0.7 on a 36 GB machine.

## Scaling limits

- **Options:** 2–26 per Choice; cascade for 100+. L0 costs K prefills sharing the state prefix (prefix caching on vLLM); Noul 2, Score 1; L1 the same as L0. `adaptive_shifts` reads about 5–7 of 18–20 rotations at a 1% target. L2 is one prompt per state stopped at ~⅔ depth, independent of K apart from option tokens. L2 heads above 8 options use the canonical listing; random listings cost 6–18 points at K = 20.
- **Multi-label:** none; one `Question.noul` per label. L2 Nouls on the same state batch into one call and can share the state's prefix KV.
- **Input length:** bounded by the base model and `--max-model-len`; AnyJev sets no limit (not documented as of 2026-09-30). L2 per decision, H100 batched: 110 tokens Qwen3-4B 5.2 ms vs 32B 34.1 ms; ~1,000 tokens 29.9 vs 194.6 ms. ~2,000 tokens: not measured; L0 multiplies the options-section prefill by the rotation count. Accuracy vs length not documented as of 2026-09-30.

## Fine-tuning

- No weight updates. L1: `calibrate(q, states, labels)` fits a temperature on 100–500 labels, stored as JSON keyed by (model, question hash). L2: `fit_head` on 100–300 labels, or `observe()` online from 30. `export_artifacts()` / `load_artifacts()` persist heads, adaptation statistics and optionally observations. Loading an artifact from a different model raises an error. A head fit on a truncated checkpoint must be served by that checkpoint.
- Closed-form distillation: Qwen3-1.7B 0.730 → 0.760 using Qwen3-32B-labelled synthetic states.

## Data governance

- **Self-host / air-gap:** yes. Runs against a local transformers model or local vLLM; no documented outbound calls once the base model is cached. `--backend fake` needs no download.
- **Licences:** code, package and heads Apache-2.0. The base LLM's licence governs weights (Qwen3 Apache-2.0; Phi, Granite, OLMo, Mistral their own). Benchmark datasets (`THIRD_PARTY.md`): BANKING77 CC-BY-4.0, MASSIVE CC-BY-4.0, CLINC150 CC-BY-3.0, deepset/prompt-injections Apache-2.0, LocalLLaMA/typed-decisions Apache-2.0, 20 Newsgroups see card.
- **Hosted option:** none. No vendor API; no region, retention, DPA or training-on-inputs terms apply.
- **Data kept by the library:** the L0 batch prior is a running mean in process memory. `export_artifacts(include_observations=True)` writes labelled states to disk; treat those files as input data.
- **Provenance and trust:** Nokia research code, one co-author at Tencent Hunyuan. Shipped heads were fit on typed-decisions (one teacher LLM's labels). Heads are JSON (base64 float32), not pickles. CHANGELOG 0.2.0 removed an internal `handoff/` directory.

## Caveats

- Choice capped at 26 options; no TypeSafe wire server (third-party adapter only). README and CHANGELOG disagree on the `adaptive_shifts` default in 0.2.0.
- L0 on many options is slow on a Mac: 7.9 s p50 for 20-way (full cycle, 0.1.0).
- The batch prior hurts when one label dominates traffic (`docs/when_l0_helps.md`). L1/L2 need labels per question; heads do not transfer across questions or models.
- Headline tables are Qwen only; each decision is scored in isolation, not in an agent loop (README).

## Sources

- [GitHub: nokia-applied-research/AnyJev](https://github.com/nokia-applied-research/AnyJev) (README, `docs/levels.md`, `docs/jev_mode.md`, `docs/results_small_models.md`, `anyjev/question.py`, `anyjev/result.py`, `anyjev/backends/hf.py`, `anyjev/truncate.py`, `ROADMAP.md`, `CHANGELOG.md`, `THIRD_PARTY.md`)
- [PyPI: anyjev](https://pypi.org/project/anyjev/)
- [MarkTechPost, 2026-09-23](https://www.marktechpost.com/2026/09/23/nokia-open-sources-anyjev-a-training-free-layer-that-turns-any-open-llm-into-a-calibrated-decision-model/)
- [GitHub: tak-bro/local-jev-bench](https://github.com/tak-bro/local-jev-bench) (README, `scripts/serve-llm.sh`, `scripts/serve-anyjev.sh`)
- [HF dataset: LocalLLaMA/typed-decisions](https://huggingface.co/datasets/LocalLLaMA/typed-decisions)
- Methods: [Zhao et al. 2021, arXiv:2102.09690](https://arxiv.org/abs/2102.09690); [Zhou et al. 2024, arXiv:2309.17249](https://arxiv.org/abs/2309.17249); [Zheng et al. 2024, arXiv:2309.03882](https://arxiv.org/abs/2309.03882); [Guo et al. 2017, arXiv:1706.04599](https://arxiv.org/abs/1706.04599)
- [HF: Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B)

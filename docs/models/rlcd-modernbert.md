# openJev Verdict (`heman10x/rlcd-modernbert-151m`)

| Field | Value |
|---|---|
| Vendor | Hemant (heman10x, GitHub `Heman10x-NGU`), independent developer |
| Type | Open-weight encoder decision model: Choice, Score and Noul with an explicit abstention slot, no generated text |
| Backbone | `knowledgator/gliclass-modern-base-v2.0` (GLiClass uni-encoder over `answerdotai/ModernBERT-base`, hidden 768), fully fine-tuned |
| Size | 151,378,177 parameters; `model.safetensors` 606 MB (FP32), `model.onnx` 606 MB, `model_fp16.onnx` 304 MB |
| Licence | Apache-2.0 (weights and code) |
| Run it via | `rlcd` Python package from [GitHub](https://github.com/Heman10x-NGU/Verdict-open-jev) (`DecisionEngine`); ONNX Runtime; in-browser WebGPU/WASM demo |
| Status | HF repo created 2026-09-17, last updated 2026-09-20; revision `8af2496`; 28,516 downloads (30 days), 37 likes. Inference engine "v1.4" (2026-09-20) on unchanged weights |

Checked 2026-10-02.

## Overview

The model is named "OpenJev (Verdict)" on its card; the HF repo id is `rlcd-modernbert-151m` ([model card](https://huggingface.co/heman10x/rlcd-modernbert-151m)).
Boards list it as "openJev Verdict" (JevBench) and "Verdict" (Decision Index).
Context and candidate labels are joined with `[TEXT]` and `[LABEL]` tokens and scored in one bidirectional pass; a softmax over up to 25 slots gives the distribution ([GitHub README](https://github.com/Heman10x-NGU/Verdict-open-jev)).
One slot is always `__insufficient_evidence__`, so every question can abstain.
Since engine v1.4, each option is rendered as `It is {description}` to match GLiClass's NLI-style pretraining.

Training ([`train_manifest.json`](https://huggingface.co/heman10x/rlcd-modernbert-151m/raw/main/train_manifest.json), [`scripts/train.py`](https://github.com/Heman10x-NGU/Verdict-open-jev/blob/main/scripts/train.py)):

- Loss: cross-entropy + 1.0 × Brier, then L-BFGS temperature scaling. The card calls this RLCD, but the trainer is supervised; no reinforcement-learning step appears in the code.
- Data: 2,300 Banking77 training rows (`data/real_banking_train.jsonl`) with 5 candidates plus abstention by default. Calibration and test slices add CLINC150 out-of-scope queries and synthetic rows.
- Run: 3 epochs, batch 8, effective batch 32, seed 42, on Apple MPS, 646 s total; epoch 2 selected by validation NLL (val accuracy 0.916).
- The README notes training contexts are under 71 tokens.

A second, separate model, "openJev-verdict-2.0", lives in [`Heman10x-NGU/openJev-verdict-2.0`](https://github.com/Heman10x-NGU/openJev-verdict-2.0) with Git LFS weights; `heman10x/openJev-verdict-2.0` is not public on HF (API returned 401, 2026-10-02).

## Schema

Own Python API, not the TypeSafe wire format; no HTTP server ships with the repo ([`core/primitives.py`](https://github.com/Heman10x-NGU/Verdict-open-jev/blob/main/core/primitives.py)).

- **Call:** `DecisionEngine().evaluate(context=..., queries=[...])`.
- **Choice:** `question` + 2–24 `Option(id, description)`; returns `selected_id`, `selected_probability`, probabilities, `confidence`, `p_abstain`.
- **Score:** `question` + 2–24 ordered `levels`; returns `selected_level_id`, `selected_value`, probabilities.
- **Noul:** proposition with three outcomes, `true`, `false`, `__insufficient_evidence__`; returns `p_true_given_sufficient_evidence`.
- **DAG mode:** a query can name parent fields; their answers are appended as `[STATE] field=value` and the child runs in a second pass.
- Partial TypeSafe compatibility: same three types, different field names, and an extra abstention outcome. JevBench and the Decision Index ran it through author-supplied adapters.

## Benchmarks

| Board | Version | Result | Source |
|---|---|---|---|
| JevBench v1.5.4 | "openJev Verdict", evaluator CPU | rank 101 of 106; score 0.0 (Intelligence 0.0, Calibration 52.2, Speed 83.9, Cost 86.6); p50 0.126 s raw | [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#jevbench-v154-headline-a), [API](https://benchmarkheaven.com/api/jevbench/v1.5.4) |
| JevBench v1.5.4 | "openJev Verdict 1.4" (same weights, fixed engine) | rank 102; score 0.0 (Calibration 80.3, Speed 80.6, Cost 86.6); p50 0.310 s raw | same |
| Decision Index 0.2.1 | engine `verdict-8af2496e` | 1.87 balanced skill (raw 12.94), ECE 0.154, median 11.4 ms on RTX PRO 6000, coverage 30.7% | [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021), [`data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index/resolve/main/data/index.json) |

- On the Decision Index, 46.6% of requests were answered with the model's own abstain option and 12.2% were unsupported because they had more than 24 options. Both count as wrong.
- JevBench v1.5.4 intelligence: open half 12.6, sealed half −14.1 (first row); −14.7 and −18.3 for the 1.4 row ([API](https://benchmarkheaven.com/api/jevbench/v1.5.4), read 2026-10-02).
- Author's own results ([GitHub README](https://github.com/Heman10x-NGU/Verdict-open-jev)):
  - Banking77 held-out test (1,000 cases, K = 5): top-1 95.0% (95% CI 93.6–96.2%), Brier 0.0785, ECE-10 3.35% calibrated; out-of-scope abstention recall 97.5%, precision 89.45%.
  - Cardinality: K = 9 91.0%, K = 17 78.0%, K = 25 72.0% (100 cases each).
  - TypeSafe public evals (337 cases): 48.07%; Jev 90.80%.
  - JevBench public, 231 items, engine 1.0 → 1.4: easy 85.4% → 87.5%, standard 62.5% → 69.4%, hard 36.9% unchanged; hard-tier ECE 0.298 → 0.118.
  - Abstention does not generalize: missing-option recall 75.5% falls to 18.0% with hard-negative siblings (K = 9) and 23.5% with paraphrased prompts.
- `LocalLLaMA/typed-decisions` (2,000 decisions): the author's v2 repo lists "Verdict 1.0 Baseline" at 26.10% top-1 and ECE 0.4209 ([`openJev-verdict-2.0` README](https://github.com/Heman10x-NGU/openJev-verdict-2.0)). The 66.10% row in the main README is a TF-IDF + logistic-regression baseline, not this model.
- Not on kyr0 typed-decision-bench, 4nt0ineB or Fastino fast-decisions as of 2026-10-02.

## Running it

```bash
git clone https://github.com/Heman10x-NGU/Verdict-open-jev.git && cd Verdict-open-jev
uv venv && uv pip install -e .          # package "rlcd" 0.1.0, Python >= 3.10
uv run python scripts/download_artifacts.py
```

```python
from rlcd import DecisionEngine, Choice, Option
engine = DecisionEngine()                 # device="cpu" default
q = Choice(id="intent", question="What is the primary customer inquiry?",
           options=[Option(id="card_lost", description="Reporting a lost or stolen card"),
                    Option(id="pin_reset", description="Requesting a PIN reminder or reset")])
r = engine.evaluate(context="I lost my wallet and need to stop my debit card.", queries=[q])
```

- The card's quickstart omits `id`, which `Choice` requires (`Field(min_length=1)`); pass one.
- **M5 Max:** PyTorch CPU (default) or ONNX Runtime CPU. `DecisionEngine(device="mps")` should work since the model trained on MPS, but MPS inference is not documented (unverified). Browser: `webgpu-demo/` runs ONNX Runtime Web on WebGPU with a WASM fallback. No MLX, GGUF or Core ML build.
- Author latency: p50 35.58 ms, p95 39.81 ms at K = 5 (WASM single-thread proxy). DI median 11.4 ms on an RTX PRO 6000.
- FP16 ONNX matches FP32 test accuracy (94.50% both, author).
- No hosted API.

## Scaling limits

- **Options:** 24 plus the abstention slot (25 logits, `max_num_classes: 25`); 26 or more raises `CapacityError`. Accuracy falls from 96% at K = 5 to 72% at K = 25 (author).
- **Context:** engine `max_length` 512 tokens since v1.4 (was 1,024); the tokenizer truncates silently. The backbone supports 8,192. Training contexts were under 71 tokens.
- **Questions per call:** one padded batch, one row per question; no documented maximum.
- **Multi-label:** one Noul per label.

## Fine-tuning

- `scripts/train.py`: defaults `--device mps`, 3 epochs, batch 8, grad-accum 4, base `knowledgator/gliclass-modern-base-v2.0`; rows in `openjev-jsonl-v1` format.
- `scripts/train_calibrator.py` refits per-K temperatures; `export/export_onnx.py` exports ONNX (opset 17).
- The shipped run took 646 s on Apple MPS ([`train_manifest.json`](https://huggingface.co/heman10x/rlcd-modernbert-151m/raw/main/train_manifest.json)), so an M5 Max can retrain it.

## Data governance

Not legal advice.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; self-hosted = your infra. Runs offline once artifacts are downloaded | [GitHub](https://github.com/Heman10x-NGU/Verdict-open-jev) |
| Fine-tuning | Yes, on your hardware, including Apple MPS | [`scripts/train.py`](https://github.com/Heman10x-NGU/Verdict-open-jev/blob/main/scripts/train.py) |
| Processing location | Wherever you run it; the WebGPU demo runs in the browser | |
| EU processing option | Yes, by self-hosting in the EU | |
| Retention / ZDR | No vendor processing | |
| Training on inputs | No vendor service exists | |
| DPA / GDPR | No processor, so no DPA | |
| Certifications | None | |
| Weights licence | Apache-2.0 (HF `cardData`, repo `LICENSE`); base GLiClass Apache-2.0 | [HF API](https://huggingface.co/api/models/heman10x/rlcd-modernbert-151m), [base API](https://huggingface.co/api/models/knowledgator/gliclass-modern-base-v2.0) |

- Training and evaluation data: Banking77 (CC-BY-4.0, [card](https://huggingface.co/datasets/PolyAI/banking77)), CLINC150 OOS (CC-BY-3.0, [card](https://huggingface.co/datasets/clinc/clinc_oos)); both require attribution. The repo commits these rows under `data/`.
- No hosted API.
- `bundle_manifest.json` records SHA-256 for `model.safetensors` and `model.onnx`.

## Caveats

- In-domain results are Banking77 only. Out of domain the model scores 0.0 on JevBench, 1.87 on the Decision Index and 48.07% on TypeSafe's public evals.
- Temperature values disagree: the card says T = 1.0716, the README table 1.4265, and the shipped `calibrator.json` 2.8039 with per-K values from 1.51 to 5.01 (fitted 2026-09-20).
- The card's "RLCD" label describes CE + Brier supervised training; TypeSafe's RLCD method is unpublished ([concepts.md](../concepts.md)).
- JevBench's first Verdict row points at a different repo (`openJev-verdict-2.0`) than the HF card.
- The DI 12.2% unsupported share comes from the 24-option cap.

## Sources

- [HF model card `heman10x/rlcd-modernbert-151m`](https://huggingface.co/heman10x/rlcd-modernbert-151m) (revision `8af2496`), [HF API](https://huggingface.co/api/models/heman10x/rlcd-modernbert-151m), [`config.json`](https://huggingface.co/heman10x/rlcd-modernbert-151m/raw/main/config.json), [`train_manifest.json`](https://huggingface.co/heman10x/rlcd-modernbert-151m/raw/main/train_manifest.json), [`calibrator.json`](https://huggingface.co/heman10x/rlcd-modernbert-151m/raw/main/calibrator.json), [`bundle_manifest.json`](https://huggingface.co/heman10x/rlcd-modernbert-151m/raw/main/bundle_manifest.json)
- GitHub [`Heman10x-NGU/Verdict-open-jev`](https://github.com/Heman10x-NGU/Verdict-open-jev) (commit `30f1556`, 2026-09-20): README, `core/`, `scripts/`, `data/`
- GitHub [`Heman10x-NGU/openJev-verdict-2.0`](https://github.com/Heman10x-NGU/openJev-verdict-2.0) (commit `bff2856`, 2026-09-20)
- [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4)
- [Decision Index Space `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index) (generated 2026-09-28)
- Dataset cards: [PolyAI/banking77](https://huggingface.co/datasets/PolyAI/banking77), [clinc/clinc_oos](https://huggingface.co/datasets/clinc/clinc_oos)

All read 2026-10-02.

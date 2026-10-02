# autotrust JEV and GEV

| Field | Value |
|---|---|
| Vendor | AutoTrust AI (HF org [`autotrust`](https://huggingface.co/autotrust)); independent, "not affiliated with, endorsed by, or a product of TypeSafe AI" (cards) |
| Type | Frozen decoder (System 2) plus a System 1 block: LoRA adapter and a 24-slot fp32 decision head on the last-token hidden state. One prefill pass per decision, no generated text. GEV-26B-Decide adds opt-in adaptive thinking |
| Backbone | Qwen3.5-9B (JEV-9B); Qwen3.8-27B (JEV-27B, JEV-27B-VL); gemma-4-26B-A4B-it (JEV-Gemma4-26B-A4B, GEV-26B-Decide) |
| Size | 8.95B, 26.9B, 27.8B (with vision tower), 25.8B (≈ 4B active per token); see [Repositories](#repositories) |
| Licence | Apache-2.0 (adapter, head, calibration files; bases Apache-2.0) |
| Run it via | vLLM with the bundled `serve_decide.py` (`POST /v1/decide`), or `transformers` + `peft` (cards use `device_map="cuda"`). No hosted API |
| Status | JEV-9B 2026-09-23; JEV-27B 2026-09-25 (updated 2026-10-02); JEV-Gemma4-26B-A4B 2026-09-29; JEV-27B-VL 2026-09-30; GEV-26B-Decide 2026-10-02 |

Checked 2026-10-02. No weights were downloaded and nothing was run.

## Overview

- AutoTrust calls the method "Blocks of Experts": the backbone stays bit-identical to the upstream release and serves as System 2. System 1 is a small trained block routed per request ([JEV-27B card](https://huggingface.co/autotrust/JEV-27B)).
- The System 1 block is a LoRA (r=16, α=32) on the decoder projections plus a 24-slot head initialised from `lm_head` rows. JEV-27B trains 108.9M parameters (0.4% of the backbone); JEV-9B trains 40.2M.
- System 1 is distilled from TypeSafe Jev 1.13. The corpus `SargeDev/jev-distill-corpus-v3` (Apache-2.0, 740,957 rows) holds 498,010 rows of Jev 1.13 output distributions collected "via OpenRouter", 94,801 Open-Jev rows with programmatic labels (CC0), and 148,154 placeholder rows.
- Loss: KL(target ‖ model) over active slots plus 0.5 × ranked probability score for `score`. 30% of `choice` rows have their options permuted.
- In vLLM the head is re-expressed as an `lm_head` LoRA where only the 24 verbalizer rows change. A decision is a one-token completion constrained to the option tokens. Chat requests use the untouched `lm_head`, and both share a batch.
- Merging the LoRA into the backbone dropped JEV-9B's HumanEval from 70.7% to 61.6%; keeping it separate leaves System 2 byte-identical to the base ([blog](https://huggingface.co/blog/autotrust/autotrustjev-27b-fast-calibrated-decisions-and-ful), 2026-09-27).
- JEV-27B-VL is JEV-27B's adapter and head on Qwen3.8-27B with its vision tower. On 1,000 text decisions its mean probability difference from JEV-27B is 0.010. The head was trained on text only, so image decisions are zero-shot.
- GEV-26B-Decide is JEV-Gemma4-26B-A4B renamed: "the weights are the same" (GEV card). It adds `serve_decide.py`, a vLLM patch and adaptive thinking. The old repo is still online at `603bfed`.
- Adaptive thinking (GEV, `thinking: "auto"`): if System 1's top option is below 0.8, Gemma-4 thinking mode reasons over the same question, and the final distribution is p = ½ p1 + ½ p2.
- AutoTrust's earlier `autotrust/GLM-5.3-*-GGUF-DGX-Spark` repos are unrelated quantizations.
- Not to be confused with AutoJev-27B (`denis-pplx/autojev-27b`), an unrelated full fine-tune (JEV-27B card).

### Repositories

HF API, read 2026-10-02. Downloads are the rolling 30-day counter.

| Repo | Base | Params (safetensors) | Created | Last modified | Revision | Downloads | Likes |
|---|---|---:|---|---|---|---:|---:|
| [JEV-9B](https://huggingface.co/autotrust/JEV-9B) | Qwen3.5-9B | 8,953,803,264 | 2026-09-23 | 2026-09-26 | `4ab5dfb` | 3,182 | 18 |
| [JEV-27B](https://huggingface.co/autotrust/JEV-27B) | Qwen3.8-27B | 26,895,998,464 | 2026-09-25 | 2026-10-02 | `51740a8` | 1,012 | 23 |
| [JEV-27B-VL](https://huggingface.co/autotrust/JEV-27B-VL) | Qwen3.8-27B (with vision) | 27,781,427,952 | 2026-09-30 | 2026-10-02 | `d835ee0` | 179,237 | 49 |
| [JEV-Gemma4-26B-A4B](https://huggingface.co/autotrust/JEV-Gemma4-26B-A4B) | gemma-4-26B-A4B-it | 25,805,936,206 | 2026-09-29 | 2026-09-29 | `603bfed` | 469 | 0 |
| [GEV-26B-Decide](https://huggingface.co/autotrust/GEV-26B-Decide) | gemma-4-26B-A4B-it | 25,805,936,206 | 2026-10-02 | 2026-10-02 | `e6f052c` | 0 | 0 |

- Weights on disk: JEV-9B backbone 17.9 GB plus a 154 MB adapter; JEV-27B 53.8 GB plus a 416 MB adapter (cards).
- JEV-27B-VL reached 179,237 downloads within three days of creation; JEV-27B has 1,012. The cause is not documented (unverified).
- Third-party GGUFs: `prithivMLmods/JEV-27B-GGUF` (796 downloads), `prithivMLmods/JEV-9B-GGUF` (1,532), `mradermacher/JEV-9B-GGUF` (651). Their file lists hold only `.gguf` files and a README, with no adapter, head or calibration (HF API, 2026-10-02). Because the root safetensors are bit-identical to the base, these files should behave as the base Qwen model, not System 1 (inferred).
- Demos and applied-task code: [GitHub yuhai-china/JEV-27B-DEMO](https://github.com/yuhai-china/JEV-27B-DEMO) (linked from the cards; not reviewed).

## Schema

TypeSafe-compatible: partial. Same three primitives, own call shape, one question per request.

`POST /v1/decide` (added 2026-10-01 to JEV-27B and JEV-27B-VL; in GEV from creation):

```json
{"kind": "choice", "state": "Customer: my card was charged twice for one coffee.",
 "question": "Which team should handle this?", "options": ["billing", "shipping", "tech support"]}
```

Documented response (JEV-27B-VL card): `"probabilities": [0.9969, 0.0000, 0.0031]`, `"choice": "billing"`, `"adaptation": "native"`, `"protocol": "jev27-bare-v1"`.

- **noul:** options fixed to `["false", "true"]`. No `criteria`.
- **score:** fixed 0–5 scale (`"0"`…`"5"`). No level descriptions.
- **choice:** 2–256 strings through the server. Labels A–P (16) are the trained ones. JEV-27B and -VL label options 17–256 with Q–Z and single-token two-letter labels in one pass (`adaptation: "wide-labels"`). GEV reads more than 16 options in groups of 16 and then a final round (`strategy: "tournament"`, default; `"single"` and `"permute"` exist).
- The `transformers` path and JEV-9B read 2–16 options.
- `state`: a string, JSON object, or (JEV-27B-VL, GEV) a list mixing text and `{"image": "https://…" | "data:…"}` parts.
- GEV only, for `noul` and `choice`: `thinking` (`"off"` default, `"auto"`, `"on"`), `threshold` (0.8), `think_budget`, `return_reasoning`, `debug`. The response adds `thinking.used`, `think_tokens`, `think_seconds`.
- Prompt template `bare-v1`: `[kind] … [state] … [question] … [options] A) … [decision]:`. Gemma models get a `<bos>` prefix and a soft cap of 30 on head logits.
- Temperatures per kind in `calibration.json`. JEV-27B: noul 1.014, choice 1.016, score 1.004. GEV ships a second table, `calibration_gold.json` (noul 1.214, choice 1.098, score 1.000), "when you gate automatic actions on confidence".
- To call `/v1/completions` yourself, pass `top_k: 0` and `top_p: 1.0`. The generation configs set `top_k` 20 (Qwen) or 64 (Gemma), which vLLM applies as request defaults and which would truncate the probabilities.
- No `instructions`/`criteria` fields, no multi-question requests, no `/v1/systemone` route. A TypeSafe SDK client needs an adapter.

## Benchmarks

### Public boards

- Decision Index 0.2.1: no autotrust row on the board. `data/index.json` (generated 2026-09-28) was re-checked 2026-10-02.
- JevBench v1.5.4: no autotrust row (re-checked 2026-10-02).
- The blog lists both submissions under "What's next".

### Self-scored Decision Index 0.2.1

AutoTrust ran the full suite and scored it with the kit's `score --edition 0.2.1`. Results are in [`autotrust/jev-decision-index-results`](https://huggingface.co/datasets/autotrust/jev-decision-index-results).

| Model | Balanced skill | Balanced raw | Breadth skill | K&R | Language | Retrieval | Tools | Arts |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| GEV-26B-Decide, adaptive thinking on K&R only | 62.48 | 70.66 | 62.00 | 0.602 | 0.636 | 0.679 | 0.697 | 0.415 |
| JEV-Gemma4-26B-A4B / GEV, System 1 (150,317 scored requests) | 58.05 | 67.35 | 56.98 | 0.430 | 0.636 | 0.679 | 0.697 | 0.415 |
| JEV-27B, System 1 | 53.30 | 64.32 | 52.21 | | | | | |
| Jev 1.13.0 (board) | 57.91 | | | | | | | |

- The 62.48 run would not qualify for the board: adaptive thinking misses the 1,000 ms median-latency limit on Knowledge & Reasoning (GEV card).
- Thinking raises GPQA Diamond accuracy from 42.9% to 78.6%, MMLU-Pro from 65.0% to 84.6%, and BBH from 75.0% to 92.0%. HLE stays near chance (8.4% to 17.8%; chance 16.4%).
- The Gemma cards disclose training on the training splits of datasets whose test splits the index uses, including BANKING77 and CLINC150.
- [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#vendor-reported-results-on-the-same-suite) lists the 58.05 row; the 62.48 and 53.30 rows are new as of 2026-10-02.

### Author-run comparisons with Jev 1.13

Six public decision benchmarks, AutoTrust's full runs of JEV-27B and hosted Jev 1.13 (2026-09-26/27). Other open rows are copied from the NeoHorse-Jev-4B card.

| Model | JevBench (public 231) | Kev | OpenJev text | Nimble | VitaminC | MASSIVE-en | Mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| JEV-27B | 88.70 | 83.75 | 73.89 | 92.91 | 77.46 | 87.71 | 84.07 |
| Jev 1.13, hosted | 87.18 | 85.52 | 72.96 | 91.84 | 78.46 | 87.14 | 83.85 |

Distillation fidelity on the held-out `test_set_30k` (25,376 rows labelled with Jev's own distributions, same 53 domains as training):

| Metric | JEV-9B | JEV-27B |
|---|---:|---:|
| Mean KL from Jev 1.13 | ≈ 0.019 | ≈ 0.017 |
| noul AUROC | 0.994 | 0.995 |
| ECE | 0.0007 | 0.0009 |
| KL to programmatic labels, unseen task families | 0.234 | 0.104 |
| HumanEval pass@1, System 2 (= base) | 70.7% | 78.0% |

[decision-models-under-pressure](https://github.com/gazelle93/decision-models-under-pressure) (human gold labels, 800 items; Jev's row published by the benchmark author, JEV rows re-run by AutoTrust):

| Options | 2 | 4 | 8 | 16 | Answers changed by option order (16 options) |
|---|---:|---:|---:|---:|---:|
| Jev 1.13 | 0.890 | 0.801 | 0.782 | 0.769 | 7.0% |
| JEV-27B | 0.876 | 0.784 | 0.767 | 0.740 | 7.4% |
| JEV-9B | 0.868 | 0.774 | 0.735 | 0.694 | 11.5% |

### Other author results

- Many options, zero-shot, 400 utterances per row: JEV-27B CLINC150 with all 150 intents 89.5% (names) and 93.8% (one-line descriptions); ECE 0.079 and 0.034. GEV with the tournament: CLINC150 95.5%, BANKING77 (77) 81.5%, 255 merged intents 89.0% / 75.2%.
- GEV adaptive thinking on 1,754 questions from six public sets outside the index: 73.3% (System 1) to 83.4% (adaptive), thinking on 47.8% of questions. ECE 0.035 both ways.
- Images: VL-RewardBench (1,247 pairs) JEV-27B-VL 78.3%, GEV 78.4%. MicroLens (200 users, covers only) AUC 0.727 vs item-based collaborative filtering 0.728 ([VL blog](https://huggingface.co/blog/autotrust/autotrustjev-27b-vl-a-decision-model-that-learned), 2026-09-30).
- Speed, one B200: JEV-27B 137 ms median per single decision and 4.2 ms batched (128); JEV-9B ≈ 90 ms and 2.5 ms; GEV System 1 45 ms and 257 decisions/s at 64 clients. JEV-27B on one H100 80 GB at bf16: ≈ 100 decisions/s (blog). These exclude network time.

## Running it

```bash
hf download autotrust/JEV-27B --local-dir JEV-27B         # ~54 GB
bash JEV-27B/serve.sh                                      # vLLM on :8000; one GPU with ≥ 80 GB
```

- `serve_decide.py` is the vLLM OpenAI server plus `POST /v1/decide`. It needs the vLLM development build from September 2026 (`logprob_token_ids`). The blog's plain `vllm serve` recipe pins vLLM 0.30.0 with `--max-model-len 4096`.
- JEV-27B-VL: `--max-num-seqs 8` is required. Above 8 sequences vLLM's LoRA path for this model class "returns wrong System 1 probabilities".
- GEV: needs `patches/vllm-gemma4-lm-head-lora.patch` (LoRA on Gemma-4's tied `lm_head`). `MTP=1 bash serve.sh` adds Google's 0.9 GB draft model, which speeds thinking 1.8–1.9× and halves System 1 throughput at 64 clients.
- `transformers` + `peft`: load the base, merge `adapter/` in memory, apply `head.safetensors` and `calibration.json` (code in each card).

### Mac (M5 Max, 128 GB)

No Mac path is documented for any autotrust model.

| Path | Status |
|---|---|
| vLLM `serve_decide.py` | CUDA build; not available on Mac |
| `transformers` + `peft` on MPS | Not documented. Change `device_map="cuda"` to `"mps"` (unverified). Memory fits: JEV-27B bf16 53.8 GB, GEV 25.8B params ≈ 52 GB bf16 (inferred) |
| Qwen3.5/3.8 bases on MPS | Training used `flash-linear-attention`, which is Triton-only. The Kev-4B card says "The DeltaNet kernels have no MPS implementation" ([fine-tuning.md](../fine-tuning.md)), so JEV-9B/27B would run on the slow PyTorch fallback (unverified) |
| Gemma-4-26B-A4B on MPS | No DeltaNet layers; the MoE path through `transformers` on MPS is untested (unverified) |
| GGUF / llama.cpp Metal | The third-party GGUFs lack the System 1 block. A GGUF build would need the head and per-kind temperatures applied outside llama.cpp |
| MLX | No conversion found (HF search, 2026-10-02) |

## Scaling limits

- **Options:** 2–256 per `choice` through the server; 2–16 on the `transformers` path and JEV-9B. `noul` and `score` take only their canonical options.
- **Questions per call:** one. Several questions about one state need several requests; vLLM prefix caching (`--enable-prefix-caching`) reuses the shared state.
- **Context:** 262,144 tokens with `--max-model-len 262144`. JEV-27B-VL got 20 of 20 single-fact decisions right at every length tested up to 250K tokens (28.7 s at 250K on one B200). GEV was tested to 128K. KV cache ≈ 65 KB per token (27B), so 256K needs ≈ 17 GB on top of 52 GB of weights. The cards advise `--max-model-len 131072` on an 80 GB GPU.
- **Original reference server:** truncates states over 1,024 tokens (60% head, 40% tail) unless the limit is raised (JEV-9B and JEV-27B cards).
- **Wide choices:** a 150-option question takes a median 1.4 s with names (≈ 790 tokens) and 2.6 s with descriptions (≈ 3,100 tokens). Above 128 options the server reads in two passes.
- **Thinking cost (GEV):** median 13.4 s and 90th percentile 33 s per request over the K&R benchmarks at ≈ 250 tokens/s (7.7 s median with speculative decoding).
- **Option order:** about 7% of 16-option answers change with order alone (JEV-27B); 11.5% (JEV-9B).

## Fine-tuning

- The recipe is described in the cards: LoRA r=16, α=32, dropout 0.05; AdamW, head lr 2e-4, LoRA lr 1e-4; 128 rows per step; JEV-27B 5,000 steps (0.98 epoch, ≈ 9.2 B200-hours, peak 79 GB); JEV-9B 4,750 steps (≈ 3 B200-hours).
- No training code is published. The corpus is public (Apache-2.0).
- Because the backbone is frozen and unmerged, a new adapter and head can be trained beside the shipped one without touching System 2 (inferred from the file layout).
- No Mac training path ([fine-tuning.md](../fine-tuning.md)).

## Data governance

Not legal advice. All weights are open; there is no vendor API.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes. Self-hosted means your infrastructure | HF repos above |
| Fine-tuning | Possible; recipe described, no training code | cards |
| Processing location | Your infrastructure. Image `state` parts given as `https://` URLs are fetched by your server | JEV-27B-VL card |
| EU processing option | Yes, on your own EU infrastructure | |
| Retention / ZDR | Your control | |
| Training on inputs | No vendor receives inputs | |
| DPA / GDPR | Not needed for self-hosting; no processor | |
| Certifications | n/a | |
| Weights licence | Apache-2.0, not gated (HF `cardData`). Qwen3.5-9B and Qwen3.8-27B Apache-2.0; Gemma 4 Apache-2.0 ([licence page](https://ai.google.dev/gemma/docs/gemma_4_license)) | HF API, 2026-10-02 |

- Provenance: System 1 copies TypeSafe Jev 1.13 output distributions collected via OpenRouter. Whether that use complies with TypeSafe's output-use terms is unverified ([TypeSafe MCA](https://typesafe.ai/legal/mca), as in [open-reproductions.md](open-reproductions.md#data-governance)).
- `serve_decide.py` runs the vLLM OpenAI server; access control follows vLLM's flags (for example `--api-key`; not checked on the development build).
- Live demos in JEV-27B-DEMO send input to whoever hosts them; send only public or synthetic data.
- JEV-27B and JEV-27B-VL changed on 2026-10-01/02 under the same name. Pin a `revision`.

## Caveats

- Every number except the board absences is AutoTrust's own run. No autotrust model is on DI or JevBench as of 2026-10-02.
- "Indistinguishable from Jev by KL" holds on the 53 training domains. No Jev-labelled out-of-domain set exists (cards).
- The student inherits the teacher's errors. The cards cite a poker spot where Jev shoves at 0.62 and JEV-27B at 0.63.
- System 2 does not know what System 1 decided and was not trained to agree with it.
- Image calibration and choices beyond 16 options are measured on one dataset each.
- GEV adaptive thinking lowers BANKING77 macro-F1 (88.0 to 85.0) and does not help retrieval or chess.
- The `yuri_v1` placeholder stream teaches nothing about memory relevance; the models output ≈ 0.5 there by design.
- English-centric.

## Sources

- HF model cards: [JEV-9B](https://huggingface.co/autotrust/JEV-9B), [JEV-27B](https://huggingface.co/autotrust/JEV-27B), [JEV-27B-VL](https://huggingface.co/autotrust/JEV-27B-VL), [JEV-Gemma4-26B-A4B](https://huggingface.co/autotrust/JEV-Gemma4-26B-A4B), [GEV-26B-Decide](https://huggingface.co/autotrust/GEV-26B-Decide)
- HF API: [`api/models?author=autotrust`](https://huggingface.co/api/models?author=autotrust) and `api/models/autotrust/<repo>` (sha, downloads, likes, safetensors totals, siblings)
- AutoTrust blogs: [autotrust/JEV-27B: fast, calibrated decisions and full reasoning from one open model](https://huggingface.co/blog/autotrust/autotrustjev-27b-fast-calibrated-decisions-and-ful) (2026-09-27, edited 2026-09-30); [autotrust/JEV-27B-VL: a decision model that learned to see](https://huggingface.co/blog/autotrust/autotrustjev-27b-vl-a-decision-model-that-learned) (2026-09-30)
- Dataset: [SargeDev/jev-distill-corpus-v3](https://huggingface.co/datasets/SargeDev/jev-distill-corpus-v3) (Apache-2.0, `fc99c63`); results [autotrust/jev-decision-index-results](https://huggingface.co/datasets/autotrust/jev-decision-index-results)
- Third-party GGUF file lists: [prithivMLmods/JEV-27B-GGUF](https://huggingface.co/prithivMLmods/JEV-27B-GGUF), [prithivMLmods/JEV-9B-GGUF](https://huggingface.co/prithivMLmods/JEV-9B-GGUF), [mradermacher/JEV-9B-GGUF](https://huggingface.co/mradermacher/JEV-9B-GGUF)
- [Decision Index Space](https://huggingface.co/spaces/multimodalart/jev-decision-index) `data/index.json` (generated 2026-09-28); [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4)
- [Gemma 4 licence page](https://ai.google.dev/gemma/docs/gemma_4_license)

All read 2026-10-02.

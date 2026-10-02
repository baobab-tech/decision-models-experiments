# Open Jev-style models

Checked 2026-09-30. No weights were downloaded and nothing was run; every command is quoted from the card or README it cites. Target machine: Apple M5 Max, 128 GB.

- Jev's request shape (one `state`, named `choice` / `score` / `noul` questions) is in [../concepts.md](../concepts.md#typed-question-format). **Schema:** "yes" = accepts that shape or a documented `POST /v1/systemone`; "partial" = same three primitives through its own call shape.
- Downloads = HF API `downloads` (rolling 30 days, read 2026-09-30); repos without a root `config.json` report 0. "DI" = balanced-skill score on Jev Decision Index 0.2.1 (Jev 1.13.0 = 57.91; [../benchmarks.md](../benchmarks.md)).
- **Own docs (checked 2026-10-02):** [Laya](laya.md), [JevK5](jevk5.md), [decider](decider.md), [autotrust JEV / GEV](autotrust-jev.md), [pplx-decider (= AutoJev-27B)](pplx-decider.md), [Jev-Omni](jev-omni.md), [Intern-Decision](intern-decision.md), [Von](von.md), [openJev Verdict](rlcd-modernbert.md), [Cygnet](cygnet.md), [Clef](clef.md), [Strands Decider](strands-decider.md), [ModernJEV-Decide-Preview](modernjev-decide.md). Where a section below and an own doc disagree, the own doc is newer.
- The long tail (255 models in Han Xiao's all-about-jev dataset) is in [../landscape.md](../landscape.md). Entries marked "(all-about-jev)" come from that dataset and were not checked.

## Comparison

| Model | Backbone | Params | Licence | Schema | Max options / input | Mac path |
|---|---|---|---|---|---|---|
| [Laya](#laya) | ModernBERT-large; mmBERT-base (multilingual) | 421M / 322M | Apache-2.0; npm MIT | yes | < ~20 advised / 512 (en), 1,024–8,192 (ml) | `pip install laya` (MPS) or `@receptron/laya` (ONNX, Node) |
| [open-jev-deberta](#open-jev-deberta-v3-large) | DeBERTa-v3-large | 434M | Apache-2.0 | partial | 255 / 512 | Python CPU fp32; Transformers.js (ONNX) |
| [Julia-1](#julia-1) | mmBERT-small | 144M | Apache-2.0 | yes | 2–20 / 8,192 | `pip install -e`, `device="cpu"` |
| GLiNER2.5-Decide | DeBERTa-v3-large | 340M | Apache-2.0 | partial (multi-label) | unlimited / not stated | [gliner-decide.md](gliner-decide.md) |
| [JevK5](jevk5.md) | Qwen3.5-4B (also 2B, 9B) | 4.2B | Apache-2.0 | yes (`jevk5-serve`) | any (knockout) / 16,384 | `llama-server` (Metal) |
| [Jev-Style](#jev-style) | Qwen3.5-2B / 0.8B | ~2B / 0.75B | Apache-2.0 | yes | 26 / 25,600 tested | `pip install "jev-style[mlx]"` |
| [decider](#decider) | Qwen3.5 Base; Gemma-4-12B-it (12b) | 0.8B–35B-A3B | Apache-2.0 | yes | 2–255 / 32k | `pip install decider-ai` (MPS, dense models) or `decider-ai[gguf]`, Metal build |
| [Tiny-Jev](#tiny-jev) | Qwen3-0.6B | 596M | Apache-2.0 | partial | not stated / 4,096 per question | transformers `.to("mps")` |
| [OpenThai-SystemOne](#openthai-systemone) | Qwen3.5-0.8B-Base | 753M | Apache-2.0 | yes | 255 / 64k | `pip install openthai-systemone` (MPS) |
| [AgentJev](#agentjev-06b) | Qwen3-0.6B | 598M | Apache-2.0 | partial | not stated / 2,048 | Python server; Mac not documented |
| [JEV-9B / 27B](autotrust-jev.md) | Qwen3.5-9B / Qwen3.8-27B | 9.0B / 26.9B | Apache-2.0 | partial | 2–256 / up to 256K on vLLM (server since 2026-10-01); 2–16 / 1,024 on JEV-9B and the reference server | none in card |
| [AutoJev-27B = pplx-decider](pplx-decider.md) | Qwen3.8-27B | 26.1B | Apache-2.0; code MIT | yes | not stated | ~49 GiB GPU; Mac not documented |
| Kev | Qwen3.5 / Qwen3.8 | 0.8B–27B | Apache-2.0 | yes | 255 / 65,536 | MLX, automatic: [kev.md](kev.md) |
| CLM-8B | Qwen3-8B (frozen encoder) | 8B | Apache-2.0 | yes | no cap found / 2,048 | vllm-metal: [clm-8b.md](clm-8b.md) |
| AnyJev | any open LLM (Qwen3 in tables) | library | Apache-2.0 | partial | 26 / base model | [anyjev.md](anyjev.md) |
| [Winnow](#winnow) | gemma-4-E4B-it / 12B-it | ~8B / 12B | Apache-2.0 | yes | not stated / 64K tested | `winnow-inference --profile apple-silicon` |
| [JEV-Gemma4](#autotrust-jev) | gemma-4-26B-A4B-it | 25.8B (4B active) | Apache-2.0 | partial | 2–16 / 1,024 | none in card |
| [VTX-JEV-1](#vtx-jev-1) | vtx-embed-7M | 12.66M (card) | Apache-2.0 | partial | 255 / not stated | `inference.py` on CPU |
| Bonsai-Llama-Jev | Bonsai-2-27B (GGUF Q2_64, ~7 GB) | 27B | MIT code; Apache-2.0 weights (PrismML) | yes | [bonsai-llama-jev.md](bonsai-llama-jev.md) | llama.cpp fork |
| Liquid d1 | — | — | commercial API | — | — | hosted: [liquid-d1.md](liquid-d1.md) |

Backbone not stated or unclear: NeoHorse-Jev-4B ([Other](#other)). Intern-Decision-4B (Qwen3.5-4B) and `surogate/rune-26b-a4b` (gemma-4-26B-A4B-it) are also under [Other](#other).

Ranking for this Mac (documented Apple Silicon path, no CUDA needed, published accuracy):

1. JevK5-GGUF: M1 Pro Metal ~0.6 s/decision, 230/231 agreement with bf16; JevBench v1.4 62.04 (Jev 63.29); DI 38.81.
2. Kev-4B / Kev-9B: MLX automatic; M5 timings published.
3. Jev-Style-2B v3 MLX: native MLX; JevBench v1.4.1 public 73.6% (self-run).
4. decider-4b-GGUF: Metal build flag in card; DI 40.70; Metal build not run over the author's regression set.
5. Laya (MPS) or `@receptron/laya` (Node 22): ~140 ms for three questions on CPU; zero-shot DI 6.04, typed-decisions 0.362.
6. Winnow-E4B: `apple-silicon` profile, no Mac measurements; DI 39.89 (Q8_0).
7. open-jev-deberta: CPU fp32 on M1 Max 1.8 s for 4 questions; trained on three public domains.

The 27B models (JEV-27B, AutoJev-27B, Solomon, Jebadiah) fit in 128 GB at bf16, but no card documents an MPS or MLX path for the decision head.

## BERT-family encoders

### Laya

Full doc: [laya.md](laya.md), checked 2026-10-02.

- **Repos:** `convaiinnovations/laya` (English root; `multilingual/`, `typed-decisions/` subfolders); ONNX `receptron/laya-onnx` (fp32, `laya.onnx` + 1.69 GB `.data`), `killkli/open-jev-laya-multilingual-onnx` (third-party, fp32 + fp16 647 MB, 271 downloads). npm `@receptron/laya` 0.1.2 (MIT, 661 stars); PyPI `laya` (`github.com/NandhaKishorM/laya`). Author: Convai Innovations; Node port by receptron. Downloads 0 (no root `config.json`), 4,635 likes.
- **Schema:** `laya-serve` exposes `POST /v1/systemone` "on the same … request and response shape as TypeSafe Jev"; npm output matches `RLAgent.system_one` to four decimals. Options share `head_max_len` (192 en / 256 ml); Banking77 (77 options) scores 0.425. Input 512 (en); multilingual 1,024 default, `max_len=8192`.
- **Benchmarks (card):** typed-decisions (2,000): `laya` 0.362, `laya-multilingual` 0.342, `laya-typed-decisions` 0.766, Jev 1.13.0 0.727. AG News 0.950; DAIR Emotion 0.595; ECE 0.081 after temperature refit. DI 6.04. Fastino fast-decisions (Laya Router) 46.6%. JEV-27B card six-group mean: 58.24.
- **Known issues:** `noul` can follow its `false:`/`true:` labels instead of the state (#156); `act_probability` "carries no usable signal yet" (#185); over-confident until temperatures are refit. `typed-decisions` warns that its `choice:11+` temperatures are clamped and uncalibrated. On LlamaIndex's PDF tasks (budgets raised to 2,048/512) it scored 24.0–70.7%, below Jev and Qwen3.5-4B on all five ([experiment 03](../../experiments/03-jev-vs-open-document-tasks/)).
- **Fine-tuning:** `notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb` (RLCD, 4 epochs over ~30k questions, 4–5 h on 2×T4).
- **Mac:** `pip install laya`; `from laya import Router; router = Router()` (downloads on first use; `preload=True` loads all three). CLI `--device cuda|cpu|mps`; 8 English tickets one-by-one 2,624 ms (MPS). Node 22: `npm install @receptron/laya`; `const laya = await Laya.load()`; ~1.7 GB fp32 to `~/.cache/receptron-laya`; ~140 ms for three questions on Apple Silicon CPU once warm.
- **Other Apple runtimes (all-about-jev):** `aac6fef/laya-mlx` (unverified; 843 MB fp16, 63/63 argmax matches vs MPS fp32) via `mizorewww/laya-mlx` (`pip install laya-mlx`, 6,654 stars); `mizorewww/laya-coreml` (Neural Engine); `afshinm/laya-mps` (~32 ms median, ~2.1 GiB, M5 Pro, 260/260 matches across memory profiles); `lkarlslund/laya.cpp` (macOS arm64 Core ML; `brew install cmake ninja icu4c nlohmann-json`); `ollaya-dev/ollaya` (Ollama-style daemon on 11435 serving Laya, decider 2B/0.8B, Kev 0.8B as ONNX with `/v1/systemone`; quoted install is a CUDA Docker image); `chaoliangUNSW/MacJev-322M-4K-Laya` (4K context, no details).

### open-jev-deberta-v3-large

- **Repos:** `com-kotobalabs/open-jev-deberta-v3-large` (2,770 downloads); ONNX `onnx-community/open-jev-deberta-v3-large-ONNX` (fp32, fp16, q4, q4f16; 600). Code `github.com/kotoba-lang/typed-decisions`. Author: Kotoba Labs Inc. (as Mithril). Encoder + 3-layer head (`head.safetensors`).
- **Schema:** `decide(state, [{"type", "instructions", "options"}])`; `choice` ≤ 255, `score` 2–10. Input 512 total, state cut to 256. No multi-label.
- **Benchmarks (card, public gold):** in-domain 0.854 (ECE 0.022); OOD 0.690 (ECE 0.035); banking77 0.916; boolq 0.879. Trained on banking77, SST-5, BoolQ only; "not comparable" to TypeSafe's numbers.
- **Fine-tuning:** corpus builder and training in `kotoba-lang/typed-decisions`; 18,000 states, 1 epoch, one H100, 229 s.
- **Mac:** `pip install git+https://github.com/kotoba-lang/typed-decisions` (plus `torch transformers safetensors huggingface_hub sentencepiece protobuf`); `OpenJev.from_pretrained("com-kotobalabs/open-jev-deberta-v3-large")` from `typed_decisions.open_jev`. CPU fp32 on M1 Max: 1.8 s for 4 questions. ONNX: Transformers.js with `{ dtype: "fp16", device: "webgpu" }`.

### Julia-1

- **Repo:** `SupersonicLabs/Julia-1` (2,201 downloads); PyTorch package; card mentions WebGPU/ONNX.
- **Schema:** `state` + `questions` with `type`/`instructions`/`criteria`. 2–20 options, each ≤ 48 tokens; 8,192 tokens combined.
- **Benchmarks:** card Choice 71.33%, Noul 80.67%, Score 68.88%. DI 5.54.
- **Mac:** `snapshot_download('SupersonicLabs/Julia-1', local_dir='Julia-1')`, `pip install -e ./Julia-1`, then `load_model("Julia-1", device="cpu", strict_encoding=True, max_length=8192, head_length=512)` from `julia`. MLX port (all-about-jev): `zm2231/julia-mlx` (`pip install julia-mlx`), M4 Pro 6.62 ms vs 34.15 ms reference, logits within 0.00115.

### Other encoders

- `mobarmg/jev-schema-scorer-deberta-v3-large` (MIT, 546 downloads), `argos1111/modernbert-ja-310m-jev` (Japanese, CC-BY-SA-4.0): not evaluated. `HIT-TMG/JevEmbed-*`: embeddings.

## Qwen-based

### JevK5

Full doc: [jevk5.md](jevk5.md), checked 2026-10-02.

- **Repos:** `alibiserikbay/JevK5` (4B, 8.4 GB bf16; 8,047 downloads), `-9B`, `-2B`, `-Lite` (DeBERTa-v3-large, 434M), `-GGUF` (Q8_0 4.48 GB, Q5_K_M 3.07 GB, Q4_K_M 2.71 GB; 7,582). Runtime `github.com/allebee/jevk5`. Answer read from next-token log-probs of option letters.
- **Schema:** `decide(state, {"type", "instructions", "criteria"})`. Runtime 0.3.0 answers > 16 options with a second `knockout_temperature` pass; the stdlib client handles ≤ 16. Multi-label not documented.
- **Benchmarks:** JevBench v1.4 #2 of 76 (62.04; Jev 63.29) per card; v1.4.2 leaderboard lists v0.2.0 at 62.04 (#5). DI 38.81. Fastino fast-decisions 57.6%. Card JevBench public (231), v0.3 4B bf16: easy 1.000, standard 0.944, hard 0.784.
- **Training:** 17,408 teacher questions (incl. 14,138 written by GPT-6 Luna via OpenAI's API, "generated under OpenAI's terms") + 30,052 public train-split items; no training command in card.
- **Mac:** `llama-server --hf-repo alibiserikbay/JevK5-GGUF --hf-file jevk5-4b-v0.3-Q8_0.gguf -c 8192 -ngl 99`, then `pip install --no-deps "jevk5 @ git+https://github.com/allebee/jevk5@v0.3.3"` and `JevK5GGUF(temperature=1.22, knockout_temperature=0.93).decide(state, {...})`. ~0.6 s per short decision (4B Q8_0, M1 Pro Metal). Only `llama-server` tested; Ollama / LM Studio log-prob support not checked.

### Jev-Style

- **Repos:** `chaoliangUNSW/Jev-Style-2B-Decision-v3-MLX` (bf16 and 8-bit 2.00 GB; 181 downloads), `-2B-Decision-v3`, `-v3-GGUF`, `Jev-Style-0.8B-Decision-v3` (+ GGUF, MLX; 752,393,024 params; 404), v1 `Jev-Style-Qwen3.5-2B-Decision-GGUF` (8,293), v2. Package `jev-style` (`github.com/lawrence3699/jev-style`).
- **Schema:** `jev-style serve` exposes `/v1/systemone`; helpers `choice`, `noul`, score. "Up to 26 options (20 when probabilities are read through a server's `top_logprobs`)" (v1 card).
- **Benchmarks (self-run):** JevBench v1.4.1 public 231: 73.6% (Jev 86.6%). Not on DI.
- **Mac timing:** M1 Max MLX bf16, 24,501-token state: first question 15.5 s, next 0.15 s. v1: 76 ms per decision.
- **Constraint:** runtime pins `mlx-lm` 0.31.3 and patches Qwen3.5 `GatedDeltaNet.__call__`. Fine-tuning: v1 describes LoRA r=16 on all linear layers with log-score loss; no script.
- **Mac:** `pip install "jev-style[mlx]"`; `jev-style serve --release 2b --precision 8bit` (bf16 default; `http://127.0.0.1:8765`), or `JevStyle.from_pretrained("chaoliangUNSW/Jev-Style-2B-Decision-v3-MLX", precision="8bit").decide(state, {"billing": noul(...), "tone": choice(...)})`.

### decider

Full doc: [decider.md](decider.md), checked 2026-10-02.

- **Repos:** `Mapika/decider-0.8b` (752M; 12,860 downloads), `-2b` (v11, 1,881,825,088; 255,088, most in this survey), `-4b` (v2.1, 4,205,751,296; 18,425), `-4b-GGUF` (Q4_K_M 2.7 GB, Q8_0 4.5 GB, BF16 8.4 GB; 1,227), `-35b-a3b` (34.7B, 3B active), `-35b-a3b-nvfp4`, `-2b-vision`, `-12b` (v2: Gemma-4-12B-it + merged rank-32 LoRA, 11,959,730,224; 46), `-2b-GGUF`; stock-model readouts `decider-chat-gemma4-31b`, `decider-chat-qwen3.6-27b`. Code `github.com/Mapika/decider`, package `decider-ai`. Readout: option-letter logits over options ÷ fitted temperature.
- **Schema:** `d.system_one(state, questions)` and `decider.serve` (`POST /v1/systemone`); "the official `typesafe-sdk` works against it unchanged with `TYPESAFE_BASE_URL`". 2–255 options (> 10 use one label token each); CLINC 151-way 0.88 vs 0.98 with 10 sampled. Input "up to 32k tokens with the questions".
- **Benchmarks:** DI: 4b 40.70, 2b (FP8) 28.97, 35b-a3b (NVFP4) 47.11. JevBench v1.5.2 (99 ranked systems, per README): 4b v2 71.3 (#7; Jev 1.13.0 72.1, #3). decider-2b regression set 0.802 in-task / 0.752 held-out; JevBench hard 0.577.
- **Fine-tuning:** `scripts/train.sh full` reproduces the supervised stages; v11 added rank-64 LoRA.
- **Mac:** `pip install "decider-ai[gguf]"` with `CMAKE_ARGS="-DGGML_METAL=on"`; `Decider("Mapika/decider-4b-GGUF", gguf_file="decider-4b-v2.1-Q4_K_M.gguf").decide(state, [{"question", "options"}])` from `decider.infer`. Plain `llama-cli`/`llama-server`/Ollama/LM Studio give a text model; answers must come from option-letter logits. CPU and Metal builds were not run over the regression set. decider-2b needs `flash-linear-attention` (Triton) for speed ("several times slower" without, decider-2b card). The README documents MPS for the dense models (0.8B, 2B, 2B vision; merged 2026-09-22): `Decider("Mapika/decider-2b")` picks CUDA, else MPS (float16), else CPU; M1 Pro median 133 ms per request; MASSIVE Scenario accuracy 0.7553 vs 0.756 bf16. `pip install "decider-ai[metal]"` adds an optional MLX/Metal kernel; third-party MLX conversions (`SirSahOl/decider-2b-chat-mlx-*`, `midium-ai/decider-2b-dwq-4bit`) are not author-documented.

### Tiny-Jev

- **Repos:** `lostargon/Tiny-Jev` (595,778,561 params, 999 downloads), `lostargon/Tiny-Jev-1.7B`. LoRA merged, marker-token scalar head; custom code (`modeling_tiny_jev.py`, `trust_remote_code=True`).
- **Schema:** `model.choice(...)`, `model.noul(...)`, score methods; fan-out over one state. 4,096 tokens per question, state truncated head+tail. Synthetic rule- or code-labelled data (~100k states). Fine-tuning not documented; no DI or JevBench entry.
- **Mac:** `AutoModel.from_pretrained("lostargon/Tiny-Jev", trust_remote_code=True).eval().to("mps")` (per card).

### OpenThai-SystemOne

- **Repo:** `iapp/OpenThai-SystemOne` (iApp Technology; 752,674,883 params; 9,363 downloads); continued pre-training on ~5B Thai tokens; custom code (`modeling.py`, `auto_map`). Siblings: GGUF, MLX 4bit/8bit/bf16/mxfp4/nvfp4, FP8, GPTQ, bnb, ONNX (`imtk`), CoreAI (`mlboydaisuke`).
- **Schema:** `Choice`/`Score`/`Noul` and a `/v1/systemone` server. 255 options (slot 255 = abstain); 64k tokens per request. Card compares with Bespoke-Nimble-9B on a 13-subset suite and Thai held-out sets; not on DI. Fine-tuning not documented (changelog describes continued fine-tuning).
- **Mac:** `pip install openthai-systemone`; `OPENTHAI_SYSTEMONE_MODEL=iapp/OpenThai-SystemOne uvicorn openthai_systemone.server:app --port 8000`. 3-question Thai ticket (166 tokens): 154 ms on M3 Max (MPS).

### AgentJev-0.6B

- **Repo:** `aimeigaoshou/agent-jev` (598,418,689 params; 912 downloads); code `github.com/malevrigns/agent-jev`. LM head removed; permutation-equivariant candidate head; safetensors FP32 2.39 GB + `temperatures.json`. "This file is the coding-completion checkpoint": P(work is finished).
- **Schema:** `decide_boolean`, `decide_choice`, `score`; 2,048 tokens, longer refused; no multi-label. Card: coding completion 57.8%, AUROC 0.589; invoice teacher agreement 87.2%. RLCD training in GitHub repo (unverified).
- **Run:** clone, `pip install -r requirements.txt huggingface_hub safetensors`, wrap with `torch.save({"state_dict": load_file(src)}, "agentjev.pt")`, then `python -m jev_service.server --checkpoint agentjev.pt --model-path Qwen/Qwen3-0.6B --temperatures temperatures.json --port 8149`. Binds `127.0.0.1`. Mac device selection not documented.

### autotrust JEV

Full doc: [autotrust-jev.md](autotrust-jev.md), checked 2026-10-02.

- **Repos:** `autotrust/JEV-9B` (8,953,803,264; 813 downloads), `JEV-27B` (26,895,998,464; 438), `JEV-Gemma4-26B-A4B` (25,805,936,206, 4B active; 95; Gemma-based). Third-party GGUF: `mradermacher/JEV-9B-GGUF`, `prithivMLmods/JEV-27B-GGUF`, `prithivMLmods/JEV-9B-GGUF`. Blog: `huggingface.co/blog/autotrust/autotrustjev-27b-fast-calibrated-decisions-and-ful`.
- **Architecture:** frozen base bit-identical to upstream (System 2); System 1 = LoRA (27B: 108.9M params) + 24-slot fp32 head on the last-token hidden state. Files: base safetensors, `adapter/`, `adapter_vllm/`, `head.safetensors`, `calibration.json`.
- **Schema:** template `[kind] … [state] … [question] … [options] … [decision]:`; `noul` must be `["false","true"]`, `score` `"0".."5"`, `choice` 2–16. 1,024 tokens at serving (state truncated 60% head / 40% tail) unless raised. No multi-label. Recipe described; no training code.
- **Benchmarks (27B card):** mean KL to Jev 1.13 ≈ 0.017 on 25,376 rows; noul AUROC 0.995; ECE 0.0009; six-benchmark mean 84.07 vs Jev 83.85 (own runs). Not on DI. JEV-Gemma4 self-reports DI 58.05 (not on the board as of 2026-09-28).
- **Run:** vLLM (`vllm serve JEV-27B … --enable-lora …`) or transformers + peft with `device_map="cuda"`; no MPS/MLX path. A GGUF from the root weights lacks the System 1 adapter and head (unverified for the third-party repos).

### AutoJev-27B

Same weight files (identical hashes) as Perplexity's `perplexity-ai/pplx-decider-v1-27b`, released 2026-10-01 with a hosted API. Full doc: [pplx-decider.md](pplx-decider.md). Count it once.

- **Repo:** `denis-pplx/autojev-27b` (26,085,330,160 params; 1,025 downloads); code `github.com/denis-pplx/autojev` (MIT). Full-weight SFT on 73,000 examples, one H200.
- **Schema:** `POST /v1/systemone` (`choice`/`noul`/`score`, optional images); auth via `AUTOJEV_API_KEY`. DI 56.40 (#3 open entrant); own test set 84.60% vs Jev 82.79%.
- **Run:** `uv sync --frozen --python 3.12`, `uv run hf download denis-pplx/autojev-27b --local-dir checkpoints/selected`, `AUTOJEV_CHECKPOINT=checkpoints/selected uv run autojev-serve`. Needs "a GPU with space for approximately 49 GiB of BF16 weights"; Mac not mentioned. Fine-tuning: `bash configs/train.sh --help`; corpus not bundled.

### Other Qwen-based

- `interfaze-ai/lev`: Qwen3.5-4B LoRA; `pip install "lev[serve] @ git+https://github.com/Abhinavexists/lev#subdirectory=packages/lev"`, `lev serve --checkpoint interfaze-ai/lev --host 0.0.0.0 --port 8000`; Jev-compatible server; DI 38.54; 480 downloads; Mac not documented.
- `DoccyHealth/Solomon`: Qwen3.8-27B LoRA + heads; document QA with evidence spans; multi-label `candidates` under `noul`; `POST /v1/decide`; `mlx/` package "has not been updated for v1.1", "experimental"; DI 36.43; no fine-tuning.
- `AlexWortega/openjev`: MIT; Qwen3.5 0.8B/2B/4B NLI cross-encoders (`AutoModelForSequenceClassification`); `OpenJev.from_pretrained(..., device="cuda")`; 107 GB repo; 0 downloads, 627 likes.
- `ZefanCai/Open-Jev-2B`, `-9B`, `-27B-v1.1`: PEFT adapters on Qwen3.5/3.8 (Apache-2.0 metadata); site reports 27B v1.1 197/231 on public JevBench; 0 downloads; loading not verified.
- `pngwn/system-one-qwen3.5-4b-scorer` / `-v2b`: Qwen3.5-4B-Base LoRA + scalar head; CC-BY-NC-4.0; DI 29.91 (v2b).
- Mac paths (all-about-jev): `bnsd55/jevmlx` (MIT; `pip install git+https://github.com/bnsd55/jevmlx`; `jevmlx decide` / `serve` over stock instruct models, default Qwen2.5-7B-Instruct-4bit; M1+, Python ≥ 3.12). `jnaina/jev-like-on-mac`: Banking77, Kev-4B (bf16, MPS) 85.1%, ECE 0.27; DiffusionGemma 26B-A4B MLX 4-bit 71.4%.

## Gemma-based

### Winnow

- **Repos:** `EldanRing/Winnow-E4B` (16,142 downloads), `Winnow-12B` (19,571). LoRA r=32 merged (no script). GGUF only: E4B Q8_0 8.01 GB; 12B Q8_0 12.67 GB, BF16 23.83 GB; optional vision projector. Server `github.com/EldanRing/winnow-inference` (llama.cpp-based, MIT).
- **Schema:** `/v1/systemone` plus `/v1/chat/completions`; 64K context tested. DI: 12B (Q8_0) 50.02, E4B (Q8_0) 39.89.
- **Mac:** `git clone …/winnow-inference && git checkout 77d1458 && python3 scripts/build.py`, then `python3 scripts/serve.py --model models/Winnow-E4B/gguf/Winnow-E4B-Q8_0.gguf --alias Winnow-E4B --text-only --context 8192 --decision-parallel 4 --chat-parallel 1 --cache q8_0 --memory exclusive --profile apple-silicon`. Published speed and memory are from a 5070 Ti. The `sha256sum` step needs coreutils. The QUICKSTART's "while this model repository is private" is stale; public as of 2026-09-30.

### Other Gemma-based

- JEV-Gemma4-26B-A4B: see [autotrust JEV](#autotrust-jev).
- `akhilaaa3/Jev-Omni`: Gemma-4-12B, 12.0B, multimodal incl. audio; `state`/`question`/`options`; `pip install -r https://huggingface.co/akhilaaa3/Jev-Omni/resolve/main/requirements.txt`, `load_jev_omni()`; `head.pt`; DI 40.53; 1,599 downloads (2026-10-02); community MLX 4-bit, GGUF and WebGPU builds. Full doc: [jev-omni.md](jev-omni.md).

## Other

### VTX-JEV-1

- **Repo:** `VTXAI/VTX-JEV-1` (created 2026-09-24; 51 downloads). Card says 12.66M params; safetensors metadata 7,133,398 stored elements (LF4 4-bit, 8.0 MB). Dequantized `VTXAI/vtx-embed-7M` embedding table, non-autoregressive; 2 epochs on `SargeDev/jev-distill-corpus-v3` (655,806 rows). Custom code, no ONNX.
- **Schema:** `JevClient.system_one(state, questions={name: Noul|Choice|Score})`; 255 options, 2–10 levels; no multi-label. Card: 3,000 held-out cases, LF4 73.10% (FP32 72.63%), Brier 0.0758. Training and LF4 code in `training/`.
- **Mac:** CPU ("CPU and CUDA support"): clone, then `from inference import JevClient; JevClient.from_pretrained("VTXAI/VTX-JEV-1")`.

### Others

- `TokenRhythm/NeoHorse-Jev-4B`: ~4B + pointer head, multimodal; partial schema; vLLM/SGLang scripts with `CUDA_VISIBLE_DEVICES=0`; DI 36.75; six-group mean 77.70 (own); 2,202 downloads.
- `internlm/Intern-Decision-4B`: Qwen3.5-4B (`base_model`), 4.5B; schema yes; `pip install -r requirements.txt`, `DecisionEngine(device="cuda")`; 1–16 questions, ≤ 62 options; DI 37.81; XTuner training code in the GitHub repo. Full doc: [intern-decision.md](intern-decision.md).
- `surogate/rune-26b-a4b-GGUF`: gemma-4-26B-A4B-it (`base_model`), 25.8B; DI 57.44 (highest open entrant); gated (automatic approval), so the card is not readable without accepting; files are 11 safetensors shards, not GGUF.
- `openjev/openjev` (OpenJev 27B, all-about-jev): CC-BY-NC-4.0; 16.5 GB Q4_K_M GGUF; lists MLX/MPS hardware; 10,000-question set 84.0% vs Jev 85.4%.
- Further DI entrants: `frontier-infra/jebadiah-27b` 54.67; `caiovicentino1/Eikos-27B-FP8` (MIT) 53.13; `kirp/jpt-9b` / `jpt-4b` (CC-BY-NC-4.0) 46.89 / 43.04; `llm-semantic-router/Decision-1.0-*` (Lux-9B) 43.49; `michaljach/jet` 42.60; `juspay/xor` (35B-A3B) 41.48; `HopitAI/hopper-g` (licence "other") 40.77; `bespokelabs/Bespoke-Nimble-9B-v2` 39.57; `togethercomputer/Tev1-4B-experimental` (no licence metadata) 29.24; `wayfind/metask-jev-4b-policy-mix` 26.89; `Hanno-Labs/bosun-v3.1-*` (custom code) 20.10 / 14.32; `moganai/lavoir` (CC-BY-NC-4.0) 8.69; `monotykamary/LFM2.5-2.6B-RLCD` 6.76.
- Jev-Mem (paper, no weights): Yi Li, Bingzhe Li, Dongming Jiang (UT Dallas), arXiv 2609.23986; code `github.com/libingzheren/Jev-Mem` (MIT), Space `libingzheren/Jev-Mem`. Hosted Jev by default, or Laya locally (`pip install '.[laya]'`; `'.[mlx]'` on Apple Silicon); `noul`/`choice`/scores for memory decisions. LoCoMo (GPT-4o-mini answerer): judge 0.777 vs 0.700 (MAGMA); build 158 s vs 1,044 s (Nemori); query 0.93 s vs 1.47 s.

## Data governance

- **Self-hosting:** every model above except Liquid d1 and hosted Jev runs locally, air-gapped once downloaded, with fine-tuning on your hardware; no processor, so no DPA. `laya-serve` binds `0.0.0.0` with no auth unless `LAYA_API_KEY` is set; AgentJev binds `127.0.0.1`; AutoJev auth via `AUTOJEV_API_KEY`.
- **Licences (HF `cardData`, 2026-09-30):** `autotrust/JEV-9B`, `JEV-27B`, `JEV-27B-VL`, `JEV-Gemma4-26B-A4B` and `Mapika/decider-0.8b`, `-2b`, `-4b`, `-12b`, `-35b-a3b`: Apache-2.0, not gated. Bases Qwen3.5-9B, Qwen3.8-27B, Qwen3.5-35B-A3B-Base, gemma-4-26B-A4B-it, gemma-4-12B-it report `apache-2.0`; Gemma cards link the [Gemma 4 licence](https://ai.google.dev/gemma/docs/gemma_4_license). Non-commercial (CC-BY-NC-4.0): `pngwn/system-one-*`, `kirp/jpt-*`, `moganai/lavoir`, `openjev/openjev`. Share-alike: `argos1111/modernbert-ja-310m-jev` (CC-BY-SA-4.0). DeBERTa-v3 base: MIT.
- **Training-data provenance:** JEV-9B/27B/Gemma4 and VTX-JEV-1 train on `SargeDev/jev-distill-corpus-v3` (Apache-2.0), mainly TypeSafe Jev 1.13 output distributions. JevK5 v0.3 includes GPT-6 Luna outputs. Compliance with TypeSafe's output-use terms is unverified ([TypeSafe MCA](https://typesafe.ai/legal/mca)). open-jev-deberta uses public gold labels only. JevK5, Jev-Style and JEV-Gemma4 cards disclose training on train splits of datasets whose test splits the Decision Index uses.
- **HF Inference Endpoints:** regions ([provider API](https://api.endpoints.huggingface.cloud/v2/provider)) AWS `eu-west-1` (the only EU region), `us-east-1`, `us-east-2`, `us-west-2`; Azure `eastus`; GCP `us-east4`. HF "does not store customer data in terms of payloads or tokens"; logs kept 30 days; SOC 2 Type 2; GDPR DPA via Enterprise; PrivateLink on AWS and Azure ([security](https://huggingface.co/docs/inference-endpoints/security)); no statement on training on inputs. Custom-code repos (VTX, Tiny-Jev, OpenThai, Laya `Router`) need a custom handler or container.
- **HF storage and jobs:** EU storage regions on Team/Enterprise, otherwise US ([storage regions](https://huggingface.co/docs/hub/storage-regions)). Jobs execution region not documented as of 2026-09-30, no region parameter ([Jobs guide](https://huggingface.co/docs/huggingface_hub/guides/jobs)). Servers in the US; Hugging Face SAS is the EU establishment, supervised by the CNIL ([privacy policy](https://huggingface.co/privacy)).
- **Integrity:** `SHA256SUMS` from JevK5, decider-4b-GGUF and Winnow (plus a release manifest); Solomon `MANIFEST.json` (sha256); Jev-Style's runtime checks a sha256 `manifest.json`. Pin a `revision`: decider-2b, JevK5 and Kev replace weights under the same name and keep older versions as tags. Custom-code repos execute Python at load (`trust_remote_code=True` or `sys.path` imports).

| Low-trust repo | Flag |
|---|---|
| `surogate/rune-26b-a4b-GGUF` | gated; card not public; files are safetensors |
| `VTXAI/VTX-JEV-1` | 51 downloads; created 2026-09-24; custom code; param count mismatch (card 12.66M, safetensors 7.13M) |
| `AlexWortega/openjev` | custom loader; 107 GB mixed repo; download counter 0 |
| `ZefanCai/Open-Jev-*` | download counter 0; loader not documented |
| `DoccyHealth/Solomon` | MLX package pinned to an older release, experimental |
| `lostargon/Tiny-Jev`, `iapp/OpenThai-SystemOne`, `Hanno-Labs/bosun-*` | `trust_remote_code` custom architectures |
| `prithivMLmods/JEV-27B-GGUF`, `mradermacher/JEV-9B-GGUF` | third-party; likely lack the System 1 adapter/head (unverified) |
| `killkli/open-jev-laya-multilingual-onnx` | "Decision probabilities have not been separately recalibrated" |
| `alibiserikbay/JevK5` v0.3 | GPT-6 Luna outputs under OpenAI terms |
| `kirp/jpt-*`, `pngwn/*`, `moganai/lavoir` | CC-BY-NC-4.0 |
| `togethercomputer/Tev1-*`, `HopitAI/hopper-g` | licence missing or "other" |

## Sources

- Hugging Face API, `https://huggingface.co/api/models?search=jev|decide|system-one` and `https://huggingface.co/api/models/<id>`, read 2026-09-30.
- Model cards: `huggingface.co/alibiserikbay/JevK5`, `/alibiserikbay/JevK5-GGUF`, `/convaiinnovations/laya`, `/receptron/laya-onnx`, `/killkli/open-jev-laya-multilingual-onnx`, `/chaoliangUNSW/Jev-Style-2B-Decision-v3-MLX`, `/chaoliangUNSW/Jev-Style-Qwen3.5-2B-Decision-GGUF`, `/Mapika/decider-2b`, `/Mapika/decider-4b-GGUF`, `/com-kotobalabs/open-jev-deberta-v3-large`, `/onnx-community/open-jev-deberta-v3-large-ONNX`, `/lostargon/Tiny-Jev`, `/iapp/OpenThai-SystemOne`, `/VTXAI/VTX-JEV-1`, `/SupersonicLabs/Julia-1`, `/EldanRing/Winnow-12B`, `/EldanRing/Winnow-E4B` (+ `docs/QUICKSTART.md`), `/aimeigaoshou/agent-jev`, `/autotrust/JEV-9B`, `/autotrust/JEV-27B`, `/autotrust/JEV-Gemma4-26B-A4B`, `/denis-pplx/autojev-27b`, `/interfaze-ai/lev`, `/TokenRhythm/NeoHorse-Jev-4B`, `/internlm/Intern-Decision-4B`, `/akhilaaa3/Jev-Omni`, `/DoccyHealth/Solomon`, `/AlexWortega/openjev`, `/pngwn/system-one-qwen3.5-4b-scorer`, `/fastino/GLiNER2.5-Decide`, `/prithivMLmods/JEV-27B-GGUF`, `/mradermacher/JEV-9B-GGUF`.
- GitHub READMEs: `github.com/receptron/laya`, `github.com/NandhaKishorM/laya`, `github.com/jaredpalmer/kev`, `github.com/libingzheren/Jev-Mem`.
- npm registry: `registry.npmjs.org/@receptron/laya`.
- Paper page: `huggingface.co/papers/2609.23986`.
- Jev Decision Index: `huggingface.co/spaces/multimodalart/jev-decision-index` (`data/index.json`, 0.2.1, generated 2026-09-28).
- `systemonemodels.org` (API schema definitions, model catalog).
- `aiweekly.co/alerts/aac6fef-ports-laya-decision-encoder-to-mlx-for-apple-silicon` (Laya MLX port).
- `artiverse.ca/nokias-anyjev-brings-fast-reliable-ai-decisions-to-open-llms/` (AnyJev).
- Open-Jev site: `zefan-cai.github.io/open-jev/`.
- Han Xiao, all-about-jev dataset (`data/all-about-jev/all-methods.jsonl`, local copy 2026-09-30; `hanxiao.io/all-about-jev/`), for entries marked "(all-about-jev)".
- Governance: `huggingface.co/docs/inference-endpoints/security`, `api.endpoints.huggingface.cloud/v2/provider`, `huggingface.co/docs/hub/storage-regions`, `huggingface.co/privacy`, `typesafe.ai/legal/mca` (via `data/all-about-jev/.gov-notes-open-models.md`).
- HF Inference Endpoints FAQ: `huggingface.co/docs/inference-endpoints/faq`; HF Jobs guide: `huggingface.co/docs/huggingface_hub/guides/jobs`.

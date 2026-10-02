# JevK5 (alibiserikbay)

| Field | Value |
|---|---|
| Vendor | Independent author `alibiserikbay` on HF; runtime at `github.com/allebee/jevk5`. Not affiliated with TypeSafe AI |
| Type | Decoder decision model: a softmax over the answer letters' next-token logits for Choice, Score and Noul questions, one temperature, zero generated tokens |
| Backbone | Qwen3.5-4B (JevK5), Qwen3.5-9B (JevK5-9B), Qwen3.5-2B (JevK5-2B), each with a merged rank-16 LoRA. JevK5-Lite: DeBERTa-v3-large classifier |
| Size | 4.21B (4B), 8.95B (9B), 1.88B (2B), 434M safetensors (Lite; card 437M). bf16 weights 8.4 GB, 17.9 GB, 3.8 GB |
| Licence | Apache-2.0 (weights and runtime). Training data includes GPT-6 Luna outputs "generated under OpenAI's terms" |
| Run it via | Self-hosted only: `jevk5` runtime from GitHub (CUDA), `jevk5-serve` (`POST /v1/systemone`), or GGUF on `llama-server` (Metal, CPU, other GPUs) with the `JevK5GGUF` client |
| Status | 4B v0.3 and 9B v0.3.3 current (2026-09-25); 2B is v0.2; Lite is `preview-1` |

Checked 2026-10-02.

## Overview

JevK5 reads a state and one typed question and returns a probability for every option.
The readout follows SemIf (TheoLeeCJ/SemIf, MIT): options get letters A–P, and the model's next-token logits over those letters are softmaxed and divided by a fitted temperature ([card](https://huggingface.co/alibiserikbay/JevK5)).
Questions with more than 16 options run as a knockout tournament (see [Scaling limits](#scaling-limits)).
Generic `generate()` examples on the Hub do not perform this readout.

v0.3 trained on 47,460 rows for one epoch: 17,408 teacher questions and 30,052 items from the train splits of 26 public datasets.
3,270 teacher questions came from Qwen3.6-27B (self-hosted); 14,138 came from GPT-6 Luna through OpenAI's API.
A teacher question was kept only when two independent answers both matched the intended one.
The card states that no JevBench item and no Jev output was used for training, tuning or selection.

| Repo | Model | Revision (`main`) | Tags | Downloads (30 d) | Likes | Created |
|---|---|---|---|---:|---:|---|
| [`alibiserikbay/JevK5`](https://huggingface.co/alibiserikbay/JevK5) | 4B v0.3 | `c4f7fdb` | `v0.2` `ea4804e`, `v0.3` `41a82c1` | 9,194 | 17 | 2026-09-22 |
| [`alibiserikbay/JevK5-9B`](https://huggingface.co/alibiserikbay/JevK5-9B) | 9B v0.3.3 | `d6521a1` | `v0.3` `19a3a36`, `v0.3.3` `d6521a1` | 898 | 1 | 2026-09-25 |
| [`alibiserikbay/JevK5-2B`](https://huggingface.co/alibiserikbay/JevK5-2B) | 2B v0.2 | `7922d1f` | none | 634 | 1 | 2026-09-23 |
| [`alibiserikbay/JevK5-Lite`](https://huggingface.co/alibiserikbay/JevK5-Lite) | DeBERTa-v3-large, preview-1 | `315ee21` | `preview-1` `315ee21` | 76 | 0 | 2026-09-25 |
| [`alibiserikbay/JevK5-GGUF`](https://huggingface.co/alibiserikbay/JevK5-GGUF) | 10 GGUF files | `ec67b0b` | none | 10,072 | 1 | 2026-09-23 |

HF API, read 2026-10-02. `jevk5` is not on PyPI (404); install from a Git tag.

## Schema

`jevk5-serve` "answers TypeSafe-style `/v1/systemone` requests" ([card](https://huggingface.co/alibiserikbay/JevK5); [runtime README](https://github.com/allebee/jevk5)).
In Python, `JevK5.decide(state, question)` takes one question dict.

- **Noul:** optional `criteria` `{"true": …, "false": …}`; returns `noul` = P(true) and `confidence`.
- **Choice:** `criteria` as `{key: description}` or a list of keys; returns `choice`, `probabilities`, `confidence`.
- **Score:** `criteria` as a list of level descriptions, lowest first.
- **Per question:** "Each question is evaluated separately; the server serializes requests on one GPU."
- **Multi-label:** not documented for the decoders. JevK5-Lite has its own `classify()` call with multi-label heads (sigmoid per label).
- **Not documented:** the `confidence` formula, the `usage` block, and error codes. Treat compatibility with TypeSafe clients as unverified until tested.

## Benchmarks

### Third-party boards

| Board | Run | Result | Source |
|---|---|---|---|
| JevBench v1.5.4 (106 ranked) | JevK5 v0.3 (4B), local GPU | #4, score 71.9 (Jev 72.1, #3); intelligence 56.3 (Jev 72.0), calibration 88.3, speed 93.6, cost 63.1; p50 0.016 s raw | [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#jevbench-v154-headline-a) (read 2026-09-30) |
| JevBench v1.5.4 | JevK5 v0.2.0 | #23, 58.1 | same |
| JevBench v1.5.4 | Plumb-4B (crh225, JevK5 v0.2 + LoRA) | #5, 71.6 | same |
| JevBench v1.4 | JevK5 v0.2 | #2 of 76, 62.04 (Jev 63.29); 308 sealed decisions 33.1% (Jev 36.7%) | [runtime README](https://github.com/allebee/jevk5); [benchmarks.md](../benchmarks.md#jevbench) |
| JevBench v1.4.2.2 (2026-09-27) | JevK5 v0.2.0 | #5, 62.04 | [JevBench README](https://github.com/fstandhartinger/jevbench) |
| Jev Decision Index 0.2.1 | "JevK5 Qwen3.5-4B LoRA" (v0.2 weights, runtime 0.2.2 with knockout), RTX PRO 6000 | balanced skill 38.81 (Jev 57.91), rank 25 of 70; ECE 0.027; median 22.0 ms, p95 226.3 ms; coverage 0.76 | [index.json](https://huggingface.co/spaces/multimodalart/jev-decision-index) (generated 2026-09-28); [benchmarks-leaderboards.md](../benchmarks-leaderboards.md#decision-index-021) |
| Fastino fast-decisions, 17 domains × 300 | "JevK5" (version not stated) | 57.6% (GLiNER2.5-Decide 60.2%, SemIf Qwen3.5-4B 56.4%, Laya Router 46.6%) | [dataset card](https://huggingface.co/datasets/fastino/fast-decisions) |

- DI area skills for JevK5: Knowledge 0.235, Language 0.433, Retrieval 0.462, Tools 0.521, Arts 0.278 (index.json).
- The card cites a separate DI rerun at 36.31, 15th of 49 ([discussion #13](https://huggingface.co/spaces/multimodalart/jev-decision-index/discussions/13)); the 0.2.1 board row reads 38.81.
- v0.3, JevK5-9B and JevK5-Lite have no DI row as of the 2026-09-28 index. The GGUF card says they are submitted.
- The JevBench calibration axis (88.3) is the highest in the v1.5.4 top 10 after Decision 4B v1.2 (88.6).

### Author's numbers

JevBench v1.2's 231 public items through JevBench's own runner (`jevk5_direct` adapter). The author's runs, not official results ([cards](https://huggingface.co/alibiserikbay/JevK5-GGUF)).

| Model | Easy (48) | Standard (72) | Hard, public half (111) | Hard-tier ECE |
|---|---:|---:|---:|---:|
| Untrained Qwen3.5-4B, same prompt | 1.000 | 0.986 | 0.613 | 0.117 |
| JevK5 v0.2 (4B) | 1.000 | 0.958 | 0.739 | 0.066 |
| JevK5 v0.3 (4B) | 1.000 | 0.944 | 0.784 | 0.054 |
| JevK5-9B v0.3.3 | 1.000 | 0.958 | 0.775 | 0.071 |
| JevK5-2B v0.2 | 1.000 | 0.806 | 0.604 | 0.071 |
| JevK5-Lite preview-1 (CPU) | 0.958 | 0.750 | 0.405 | 0.269 |

- v0.3 against v0.2 on the hard tier: 10 items fixed, 5 broken (McNemar p = 0.30).
- Held-out "index proxy" (the author's estimate over 16 DI train-split sources, 40 rows each, about ±0.15 per source): v0.2 0.620, v0.3 0.731, 9B v0.3.3 0.794.
- bev-decision-150K test sample (4,723 questions): v0.3 0.663, 9B v0.3.3 0.698; Score is the weakest type (0.409, 0.482).
- H100 latency, batch 1, CUDA graphs: 4B p50 13.2 ms on easy/standard items, 30 ms on 1–4k-token hard items; 9B 16 ms and 42 ms; 2B about 9 ms.

More than 16 options, 500 train-split items per set, every option offered ([card](https://huggingface.co/alibiserikbay/JevK5-9B)):

| Set | Options | Passes | 4B v0.3 accuracy / ECE | 9B v0.3.3 accuracy / ECE |
|---|---:|---:|---:|---:|
| MASSIVE en-US (temperature fitting set) | 60 | 5 | 0.738 / 0.045 | 0.814 / 0.031 |
| BANKING77 | 77 | 6 | 0.652 / 0.044 | 0.754 / 0.055 |
| CLINC150 with out-of-scope | 151 | 11 | 0.700 / 0.056 | 0.804 / 0.060 |

CLINC150 out-of-scope recall: 0.27 (4B v0.3), 0.59 (9B v0.3.3).

JevK5-Lite against GLiNER2.5-Decide ([Lite card](https://huggingface.co/alibiserikbay/JevK5-Lite)): mean macro-F1 over seven public sets 0.629 vs 0.643; lower top-label ECE on all six single-label sets; fast-decisions dev head accuracy 0.587 vs 0.637.

### Related: experiment 03

[Experiment 03](../../experiments/03-jev-vs-open-document-tasks/README.md) ran untrained `Qwen/Qwen3.5-4B` with a SemIf-style letter readout: JevK5's base and readout without its LoRA or temperature. It scored within 10.4 points of Jev on five document tasks (language 100%, orientation 90.6%, RVL-CDIP 51.0%, split 87.8%, triage 95.8%). JevK5 itself was not run there.

## Running it

Mac path (M5 Max, 128 GB): GGUF on `llama-server` with Metal. The transformers runtime is documented for CUDA only ("Needs a CUDA GPU with ~9 GB for bf16"); MPS is not documented. Every GGUF file (largest 9.53 GB) fits in memory.

1. Start llama.cpp's server ([GGUF card](https://huggingface.co/alibiserikbay/JevK5-GGUF)):

```bash
llama-server --hf-repo alibiserikbay/JevK5-GGUF --hf-file jevk5-4b-v0.3-Q8_0.gguf -c 8192 -ngl 99
```

2. Install the standard-library client and pass the file's own temperatures:

```bash
uv pip install --no-deps "jevk5 @ git+https://github.com/allebee/jevk5@v0.3.3"
```

```python
from jevk5 import JevK5GGUF

model = JevK5GGUF(temperature=1.22, knockout_temperature=0.93)   # jevk5-4b-v0.3-*.gguf
model.decide("Order #7120 shows delivered to No. 17; the customer lives at No. 71.",
             {"type": "choice", "instructions": "What happened to the parcel?",
              "criteria": ["delivered", "misdelivered", "unknown"]})
```

| File | Size | Same answer as bf16 (231) | `temperature` / `knockout_temperature` |
|---|---:|---:|---|
| `jevk5-4b-v0.3-Q8_0.gguf` | 4.48 GB | 229 | 1.22 / 0.93 |
| `jevk5-4b-v0.3-Q5_K_M.gguf` | 3.07 GB | 224 | 1.22 / 0.93 |
| `jevk5-4b-v0.3-Q4_K_M.gguf` | 2.71 GB | 221 | 1.22 / 0.93 |
| `jevk5-9b-v0.3.3-Q8_0.gguf` | 9.53 GB | 229 | 1.316 / 1.05 |
| `jevk5-9b-v0.3.3-Q5_K_M.gguf` | 6.47 GB | 228 | 1.316 / 1.05 |
| `jevk5-2b-v0.2-Q8_0.gguf` | 2.01 GB | 226 | 1.42 / 0.77 |

- `JevK5GGUF()` with no arguments uses v0.2's values (1.532 / 0.77); pass the file's own.
- Speed: the 4B Q8_0 takes about 0.6 s per short decision (~170 tokens) on an M1 Pro with Metal. M5 timings are not published.
- Only `llama-server` is tested. Ollama and LM Studio may not expose the letter log-probabilities the readout needs (not checked by the author).
- Verify files against `SHA256SUMS` in the repo.
- On CUDA: `pip install "jevk5[fast] @ git+https://github.com/allebee/jevk5@v0.3.0"`, then `JevK5("alibiserikbay/JevK5")` or `jevk5-serve --model alibiserikbay/JevK5 --port 8090`.
- JevK5-Lite runs on CPU: `pip install "jevk5[lite] @ git+https://github.com/allebee/jevk5@v0.3.1"`, then `JevK5Lite.from_pretrained("alibiserikbay/JevK5-Lite", threads=16)`. bf16 needs AMX or AVX512-BF16 to be fast; use the fp32 default on a Mac.

## Scaling limits

- **Options:** 16 per pass (letters A–P). More options use a knockout tournament: groups of up to 16 in order, then a final of 16 with each group's leaders, so n options take ceil(n/16) + 1 passes. A second temperature (`knockout_temperature`, runtime 0.3.0+) recalibrates the combined result; it never changes the answer. 151 options took 11 passes and 199 ms p50 on an H100 (v0.2).
- **Standalone client:** the card's stdlib snippet handles up to 16 options; `JevK5GGUF` handles more.
- **Context:** inputs over 16,384 tokens are refused, not cut. Training inputs were up to 2,048 tokens. The documented `llama-server` command sets `-c 8192`.
- **Questions per call:** one forward pass per question; the server serialises requests on one GPU.
- **JevK5-Lite:** text cut to 512 tokens, labels first; long label lists extend past 512 tokens (DeBERTa relative positions). All 77 BANKING77 labels fit.
- **Language:** English only.

## Fine-tuning

- Training code in the runtime repo: [`training/teacher.py`](https://github.com/allebee/jevk5/blob/main/training/teacher.py) (teacher data) and [`training/lora.py`](https://github.com/allebee/jevk5/blob/main/training/lora.py) (LoRA).
- Recipe: LoRA rank 16 on attention projections, cross-entropy on the option-letter logits, learning rate 3e-5, inputs up to 2,048 tokens, 1 epoch (4B) or 1.5 epochs (9B v0.3.3). Distribution-valued answers train against the distribution.
- Calibration: one temperature fitted on 362 held-out teacher questions from three unseen domains (4B ECE 0.050 → 0.035). Per-type temperatures and option-order averaging were tested and rejected.
- Training hardware and time are not stated. MPS training is not documented.
- Third-party: Plumb-4B (crh225) is a further LoRA on JevK5 v0.2 and scores 71.6 on JevBench v1.5.4.

## Data governance

Not legal advice. JevK5 has no vendor API; every row below is for self-hosting on your own infrastructure.

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; air-gapped once weights are cached | [runtime README](https://github.com/allebee/jevk5) |
| Fine-tuning | Yes, on your hardware (LoRA scripts in the repo) | same |
| Processing location | Your infrastructure | |
| EU processing option | Self-host in the EU. HF Inference Endpoints `eu-west-1` would need a custom container for the letter readout (unverified) | [open-reproductions.md](open-reproductions.md#data-governance) |
| Retention / ZDR | No retention by the runtime documented or expected; `jevk5-serve` logging is not documented (unverified) | |
| Training on inputs | No; inference is local | |
| DPA / GDPR | Not applicable when self-hosted: no processor | |
| Certifications | None (open-source project) | |
| Weights licence | Apache-2.0 for all five repos (`cardData`); bases Qwen3.5 Apache-2.0; Lite base DeBERTa-v3-large MIT | HF API, 2026-10-02 |
| Training-data terms | 14,138 teacher questions (4B, 9B) and 20,822 Lite documents written by GPT-6 Luna via OpenAI's API, "subject to OpenAI's terms". Replay sets include CC BY-SA 3.0/4.0 (ARC, HoVer, SGD, BoolQ, DBpedia-14) and CDLA-Sharing 1.0 (Bitext, Lite only) | [4B card](https://huggingface.co/alibiserikbay/JevK5), [Lite card](https://huggingface.co/alibiserikbay/JevK5-Lite) |

- Two development variants trained on ANLI (CC BY-NC 4.0), NLI4CT (no licence) or RACE (non-commercial) are not released.
- The 2B is v0.2: its training data includes 940 MMLU-Pro test items; the author's 4B v0.2 scored 5.5 points higher on those than on unseen MMLU-Pro items (CHANGELOG, per the 2B card).
- Declared DI overlap: train splits of 15 DI benchmarks (ARC, OpenBookQA, CommonsenseQA, GSM8K, WinoGrande, HellaSwag, BANKING77, CLINC150, SGD, Amazon ESCI, When2Call, iSarcasmEval, RAGTruth, HoVer, New Yorker caption contest), deduplicated against test and validation text by exact match and shared 8-word sequences. 53 v0.2 Qwen-written questions share an 8-gram with ContractNLI or SGD test or dev text and were kept.
- `main` is replaced in place across versions; pin a tag or commit (`v0.3`, `v0.3.3`, `preview-1`).

## Caveats

- On JevBench v1.5.4, JevK5 v0.3's intelligence axis is 56.3 against Jev's 72.0; its overall rank comes from speed (93.6) and cost (63.1).
- v0.2 dropped to 33.1% on JevBench v1.4's sealed decisions; v0.3 has no sealed-set result.
- The author's held-out checks use small slices: 40 rows per index source, 64 hand-written items, one seed per setting.
- Dates and numbers stay the weakest JevBench family (0.47 on the hard tier, 4B and 9B).
- More than 16 options got worse from v0.2 to v0.3 on MASSIVE (0.754 → 0.738) and BANKING77 (0.690 → 0.652).
- JevK5-Lite is a preview; its calibration holds on some sets and not others (fast-decisions ECE 0.255).
- Real-world workflow performance against Jev has not been measured (card).
- The DI lists the base as `Qwen/Qwen3.5-4B-Base`; the card's `base_model` is `Qwen/Qwen3.5-4B`.

## Sources

- Model cards: [`alibiserikbay/JevK5`](https://huggingface.co/alibiserikbay/JevK5/raw/main/README.md), [`JevK5-9B`](https://huggingface.co/alibiserikbay/JevK5-9B/raw/main/README.md), [`JevK5-2B`](https://huggingface.co/alibiserikbay/JevK5-2B/raw/main/README.md), [`JevK5-Lite`](https://huggingface.co/alibiserikbay/JevK5-Lite/raw/main/README.md), [`JevK5-GGUF`](https://huggingface.co/alibiserikbay/JevK5-GGUF/raw/main/README.md); `jevk5_config.json` and `config.json` in the 4B, 9B and 2B repos.
- HF API: `https://huggingface.co/api/models/<repo>` and `/refs` for the five repos.
- GitHub: [`allebee/jevk5` README](https://github.com/allebee/jevk5) and LICENSE; [JevBench README](https://github.com/fstandhartinger/jevbench).
- PyPI: `https://pypi.org/pypi/jevk5/json` (404).
- Benchmarks: [Decision Index `data/index.json`](https://huggingface.co/spaces/multimodalart/jev-decision-index) (generated 2026-09-28), [JevBench v1.5.4 API](https://benchmarkheaven.com/api/jevbench/v1.5.4), [fastino/fast-decisions](https://huggingface.co/datasets/fastino/fast-decisions), [benchmarks.md](../benchmarks.md), [benchmarks-leaderboards.md](../benchmarks-leaderboards.md), [experiment 03](../../experiments/03-jev-vs-open-document-tasks/README.md).

All read 2026-10-02.

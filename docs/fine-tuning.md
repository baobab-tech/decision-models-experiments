# Fine-tuning decision models

Survey date: 2026-09-30. Research only: no training was run and no weights were downloaded. Commands and numbers are quoted from the cited cards and READMEs. "n/d" = not documented.

## Architectures and what gets trained

| Readout | Trained parts | Examples |
|---|---|---|
| Encoder + option-marker head (softmax within each question) | full encoder + head | Laya, open-jev-deberta-v3-large, Julia-1, VTX-JEV-1 |
| Cross-encoder, one scalar score per (state, option) pair | full encoder + head | ModernJEV-Decide-Preview |
| GLiNER2 span/classification heads | encoder + task heads, or LoRA on both | GLiNER2.5-Decide |
| Decoder + option-letter logits, divided by a fitted temperature | full weights or merged LoRA | decider, JevK5, Jev-Style, Winnow, AutoJev-27B, Tev1 |
| Decoder + LoRA + separate linear/pointer head | LoRA adapter + head; base frozen | Kev, autotrust JEV-9B/27B, pngwn scorer, Tiny-Jev, AgentJev, Solomon |
| Decoder as sequence classifier over (premise, hypothesis) | full or LoRA | `AlexWortega/openjev` |
| Frozen encoder + contrastive heads | heads only | CLM-8B |

Backbone families and sizes are compared in [model-classes.md](model-classes.md).

## BERT-family encoders

| Model (backbone) | Method | Data format | Hardware | Mac feasibility |
|---|---|---|---|---|
| GLiNER2.5-Decide (DeBERTa-v3-large, 340M) | full, or LoRA (`use_lora=True, lora_r=8, lora_alpha=16.0, lora_targets=["encoder", "all_task_heads"]`; adapters ~2–10 MB, 2–3× faster). Hosted: Fastino API fine-tuning | GLiNER2 JSONL; `true_label` is a list (multi-label allowed) | n/d | MPS training n/d |
| Laya (ModernBERT-large 421M; mmBERT-base 322M) | full encoder + head; RLCD (proper-scoring-rule rewards, GRPO-style), per-type temperatures fitted after | built by the notebook from typed-decision cases; teacher distributions or gold labels | Kaggle 2×T4, "roughly 4-5 hours for 4 epochs over ~30k questions"; browser-agent example on one 16 GB GPU | inference on MPS documented; training on MPS n/d |
| open-jev-deberta-v3-large (DeBERTa-v3-large) | full fine-tune, CE + Brier, question augmentation p=0.7 | corpus builder in `kotoba-lang/typed-decisions` (banking77, SST-5, BoolQ) | one H100, 1 epoch, 18,000 states, 229 s (~$0.25) | n/d |
| [ModernJEV-Decide-Preview](models/modernjev-decide.md#fine-tuning) (ModernBERT-base, 150M) | full encoder + scalar head; softmax CE over candidate scores, gold + up to 3 negatives | `MaziyarPanahi/AgentToolDecisions-180K` (60,000 of 171,056 train rows) | one A100 80GB on HF Jobs: 129.8 min training ≈ $5.41, full job ≈ $6.58 (runtime estimate); a 6,000-row replay ran from one HuggingChat ML Intern message | CPU inference documented; training n/d |

- GLiNER2: `pip install gliner2[train]`, then `ExtractorTrainer(AutoExtractor.from_pretrained("fastino/gliner2-base-v1"), TrainingConfig(output_dir="./output", num_epochs=10)).train(train_data="train.jsonl")`. Starting from `fastino/GLiNER2.5-Decide` with this trainer is not shown (unverified).
- Laya notebook: `notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb` in `NandhaKishorM/laya`; uses gradient checkpointing (`model.head_checkpointing = True`). README: "The notebook's calibration samples come from its training items; evaluate on separate held-out data before claiming an improvement." Browser-agent example: `docs/finetune_browser_agent.md`, weights at `cklxx/laya-browser`.

## Qwen-based decoders

Qwen3.5 mixes Gated DeltaNet (linear attention) and attention layers. The Kev-4B card states "The DeltaNet kernels have no MPS implementation"; the Kev README says its Mac training path "works but is slow for Qwen3.5 bases". The decider-2b card lists `flash-linear-attention` (Triton) as a requirement ("several times slower" without it). Qwen3 is attention-only.

| Model (backbone) | Method | Data format | Hardware | Mac feasibility |
|---|---|---|---|---|
| [Kev](models/kev.md#fine-tuning) (Qwen3.5-0.8B/4B/9B-Base) | LoRA r16 on attention, MLP and DeltaNet projections + pointer head; `--init_from` a released checkpoint | JSONL, one API request per line with `label` per question (`choice`: option name; `noul`: `true`/`false`; `score`: level index from 0) | `--batch 1 --accum 8` bf16 fits 0.8B on a 4 GB GPU; Modal skill, ~$1 per Kev-4B run on H100 | documented: one job at a time; "slow for Qwen3.5 bases" (README) |
| decider (Mapika; Qwen3.5) | earlier stages: full fine-tune, CE on ~95 public datasets, ≤10 options per example. v11: LoRA r64, α128, merged; lr 1e-4, 1,676 steps × 65,536 tokens, 42,749 rows; replay rows via KL(p_v10 ‖ p_model) | registry and generators in `Mapika/decider` (`decider/data/mixture.py`) | CUDA; `scripts/train.sh full` | MPS inference documented for dense models; training on Mac n/d |
| autotrust JEV-9B / 27B | LoRA + 24-slot linear head on a frozen base; 27B 108.9M trained parameters, 9B 40.2M | `SargeDev/jev-distill-corpus-v3` (655k+ rows, mostly Jev 1.13 distributions), KL loss | 27B ≈9.2 B200-hours; 9B ≈3 | no Mac path; training code not in cards |
| AutoJev-27B | full-weight SFT, 73,000 examples, 286 updates | corpus not bundled | one H200 | no Mac path |
| Jev-Style v1 (Qwen3.5-2B) | LoRA r16 on all linear layers, log-score loss, custom chunk-parallel DeltaNet forward | n/d | n/d | MLX inference documented (`mlx-lm==0.31.3`, patched `GatedDeltaNet.__call__`) |
| JevK5 v0.3 | teacher questions kept only when two independent answers agree + public train-split replay | n/d | n/d | n/d |
| [Tev1](models/tev1.md) (Qwen3.5-4B) | LoRA r8, 1 epoch, lr 5e-5 | 37,840 examples from 8 sources; builders in `togethercomputer/tev1` | Together fine-tuning, ~$17, ~25 min | n/d |
| AgentJev (Qwen3-0.6B) | supervised + RLCD on executed coding pairs | n/d | n/d | n/d |
| [CLM-8B](models/clm-8b.md#fine-tuning) (Qwen3-8B, frozen) | heads only; InfoNCE or soft CE | (state, action) traces, or `LocalLLaMA/typed-decisions` | CUDA (`--gpu`); hardware and time n/d | n/d |

## Other backbones

| Model (backbone) | Method | Data format | Hardware | Mac feasibility |
|---|---|---|---|---|
| Winnow-E4B / 12B (Gemma 4) | LoRA r32, α64, merged in FP32, then GGUF | n/d | n/d | n/d |
| LFM2.5-2.6B-RLCD (LFM2.5) | full fine-tune | in repo (not reviewed) | Modal (`lfm25_pcd_modal.py`) | n/d |
| VTX-JEV-1 (7M embedding model) | full fine-tune, then LF4 4-bit quantization | 655,806 rows, 2 epochs; `training/` in the repo | timings on T4 | n/d |

Liquid AI documents SFT/DPO for LFM2 with TRL + PEFT (QLoRA, then merge). `notnotsamuel/LFM2.5-350M-RLCD` scores 1.38 and LFM2.5-2.6B-RLCD 6.76 on DI 0.2.1.

## Converting a Jev-shaped request to GLiNER2 rows

Map each `choice` to a task with `labels` = option keys, each `noul` to a two-label task, and each `score` to an ordinal task with string-digit labels (the `fastino/fast-decisions` shape adds `"multi_label": bool`). Neither project documents this mapping.

```jsonl
{"input": "This movie is absolutely fantastic! I loved every minute of it.", "output": {"classifications": [{"task": "sentiment", "labels": ["positive", "negative", "neutral"], "true_label": ["positive"]}]}}
```

## Hardware

- **Apple Silicon (M5 Max, 128 GB).** Unified memory holds bf16 weights of every model here, including 27B (~54 GB) and 35B-A3B (~65–69 GB). The constraints are missing MPS kernels (DeltaNet) and CUDA-only scripts. `mlx_lm.lora` on a Qwen3.5 base is general MLX tooling that no decision-model author documents.
- **Hugging Face Jobs.** Billed per minute while a Job is Starting or Running; default timeout 30 minutes; region selection not documented. See [Training on Hugging Face Jobs](#training-on-hugging-face-jobs).

| Flavor | GPU | $/h | Fits (from cards) |
|---|---|---:|---|
| `t4-small` / `t4-medium` | 1× T4 16 GB | 0.40 / 0.60 | Laya targets 2×T4 (no 2×T4 flavor) |
| `a10g-small` / `a10g-large` | 1× A10G 24 GB | 1.00 / 1.50 | Kev-0.8B/4B LoRA; GLiNER2; open-jev-deberta |
| `a10g-largex2` | 2× A10G | 3.00 | closest to Laya's 2×T4 |
| `l40sx1` | 1× L40S 48 GB | 1.80 | Kev-9B LoRA |
| `a100-large` | 1× A100 80 GB | 2.50 | 27B LoRA |
| `h200` | 1× H200 141 GB | 5.00 | AutoJev-27B full SFT |
| `rtx-pro-6000` | 1× RTX PRO 6000 96 GB | 2.75 | Decision Index evaluation GPU |

## Training on Hugging Face Jobs

From the [Train Models on Jobs](https://huggingface.co/docs/hub/jobs-training) guide, [Configuration](https://huggingface.co/docs/hub/jobs-configuration) and [Pricing](https://huggingface.co/docs/hub/jobs-pricing), read 2026-10-02.

### How a Job is built

- **One file:** a uv script with a PEP 723 header, run with `hf jobs uv run train.py`. The header can carry its own launch config in a `[tool.hf-jobs]` table (`flavor`, `timeout`, `secrets`, `env`, `volumes`, `labels`, `namespace`); flags still win.
- **A project folder** (local imports, `pyproject.toml`): `hf jobs uv run` uploads only the script, so mount the folder with `-v ./proj:/code` and copy it to a writable path inside the container. Experiments here keep one `pyproject.toml` each, so this is the form they need.
- **A library image** (TRL, Axolotl): `hf jobs run <image> -- <command>`. Pin the tag.
- **Token:** Jobs get none by default. `-s HF_TOKEN` forwards it; other keys travel the same way (`--secrets-file .env.secrets`). Secrets are encrypted server side.
- **`--` separates `hf` flags from script arguments.** Without it, a script flag named `--timeout` or `--token` goes to `hf`.
- **Output:** the container disk is discarded at the end. Push the model (`--push_to_hub`, or `hub_model_id`), and for runs over an hour write checkpoints to a mounted bucket: `-v hf://buckets/<user>/checkpoints:/ckpt`. Create a private repo first with `hf repos create <name> --private`; a fine-grained token needs write and create access, or the run trains to the end and fails on upload.
- **Agent loop:** `-d` returns the Job ID; `hf jobs logs -f`, `hf jobs stats`, `hf jobs wait` (non-zero exit on failure) and `hf jobs inspect` cover monitoring. `hf skills add` installs an `hf` CLI skill for Claude Code, Codex and Cursor ([Jobs examples](https://huggingface.co/docs/hub/jobs-examples#coding-agent-skills)).

### Checks before a long run

1. Smoke-test with a step cap on a small flavor: proves install, data load, memory fit and push.
2. Check disk: weights, data and checkpoints share the flavor's ephemeral storage (50 GB on `t4-small`, 110 GB on `a10g-small`, 1,000 GB on `a100-large`).
3. Estimate time from the smoke test's `train_steps_per_second` and total steps; set `--timeout` above it.
4. On `x2`/`x4` flavors, launch one process per GPU (`accelerate launch`); plain `python train.py` uses one.
5. Pin script URLs to a commit and images to a tag, so a rerun gets the same software. This is also what [AGENTS.md](../AGENTS.md) asks for.

### Decision models on Jobs

| Model | Trainer | Suggested flavor | Measured or estimated cost |
|---|---|---|---|
| [ModernJEV-Decide-Preview](models/modernjev-decide.md#fine-tuning) (150M) | own `recipe/train.py` | `a100-large` (used) | 129.8 min ≈ $5.41 training, ≈ $6.58 job (author, runtime estimate) |
| [GLiNER2.5-Decide](models/gliner-decide.md#fine-tuning) (340M) | `gliner2[train]` `ExtractorTrainer` | `a10g-small` | no published time (estimate: under 1 h for 1,000 examples, unverified) |
| [open-jev-deberta](models/open-reproductions.md#open-jev-deberta-v3-large) (434M) | `kotoba-lang/typed-decisions` | `a10g-small`; author used one H100 | 229 s on H100 for 18,000 states (author); ≈ $0.32 at the `h200` rate (estimate) |
| [Laya](models/laya.md) (421M) | Kaggle notebook, RLCD | `a10g-largex2` (no 2×T4 flavor) | 4–5 h on 2×T4 (author); ≈ $12–15 on `a10g-largex2` (estimate; likely faster) |
| [Kev](models/kev.md#fine-tuning) 0.8B / 4B | `kev` LoRA + pointer head | `a10g-large` / `l40sx1` | Kev-4B: 15 min on H100 for 1,050 records (author) |
| Qwen 0.5B–2B with TRL | TRL `sft.py` from its URL | `a10g-small` | HF guide: Qwen2-0.5B SFT, 100 steps ≈ 6 min |

The TRL and Transformers example scripts already carry PEP 723 headers and run from their GitHub URL. GLiNER2, Kev, Laya and the ModernJEV recipe need a one-file wrapper or a mounted project.

### Template for a GLiNER2 LoRA run (untested)

```python
# /// script
# requires-python = ">=3.11"
# dependencies = ["gliner2[train]==2.0.0", "huggingface_hub>=1.0"]
#
# [tool.hf-jobs]
# flavor  = "a10g-small"
# timeout = "1h"
# secrets = ["HF_TOKEN"]
# ///
import sys
from huggingface_hub import hf_hub_download, upload_folder
from gliner2 import AutoExtractor
from gliner2.training.trainer import ExtractorTrainer, TrainingConfig

data_repo, out_repo = sys.argv[1], sys.argv[2]          # a private dataset repo and a private model repo
train = hf_hub_download(data_repo, "train.jsonl", repo_type="dataset")
val = hf_hub_download(data_repo, "val.jsonl", repo_type="dataset")
model = AutoExtractor.from_pretrained("fastino/GLiNER2.5-Decide")   # pin a revision before a real run
cfg = TrainingConfig(output_dir="/tmp/out", use_lora=True, lora_r=16, lora_alpha=32,
                     lora_target_modules=["encoder"], save_adapter_only=True, num_epochs=10, batch_size=16)
ExtractorTrainer(model, cfg).train(train_data=train, eval_data=val)
upload_folder(repo_id=out_repo, folder_path="/tmp/out/final")
```

Launch: `hf jobs uv run train_gliner.py -- <user>/decide-train-data <user>/decide-lora`. Data format: [Converting a Jev-shaped request to GLiNER2 rows](#converting-a-jev-shaped-request-to-gliner2-rows).

### Data governance on Jobs

- Region: not documented, so treat a Job as processing outside the EU unless Hugging Face confirms otherwise.
- `-v ./dir:/path` uploads the local folder to a private `jobs-artifacts` bucket in your namespace.
- Training data reaches a Job through a Hub repo, a bucket, a mounted folder (uploaded to `jobs-artifacts`) or a URL the script downloads. The first three store it on Hugging Face.
- Rule for this repo: send only public or synthetic data to Jobs unless the maintainer approves otherwise (same as API-only models). Record the flavor, Job ID and cost with each result.

## When fine-tuning beats zero-shot (published evidence)

| Source | Zero-shot | Fine-tuned | Notes |
|---|---|---|---|
| Laya typed-decisions (2,000 decisions) | 0.362 (en), 0.342 (multilingual); random 0.318, majority 0.461 | 0.766 | "Laya is a fast base to specialise, not a zero-shot decision engine." |
| Laya browser-agent element choice (~45 candidates) | 0.10 top-1 | 0.66 top-1; task success 0% → 62% | one 16 GB GPU |
| Kev-4B, 1,050 generated support records | 67.7% | 73.6%; automatable at 5% error 34% → 48% | 15 min on H100 |
| Kev-4B, 5,219 consumer-finance complaints | 0.804 | 0.904 | one epoch; "Gains like these are in distribution" |
| Kev, 400 records | — | gain "inside the noise" | README |
| Kev `--init_from` vs from base (836 decisions) | — | 0.33 from base; 0.83 with `--init_from` (0.88 on the new domain) | README |
| open-jev-deberta | OOD questions 0.690 | in-domain question types 0.854 | same states |
| decider v10 → v11 LoRA | — | +10.5 / +10.7 on held-out hard sets; −2.2 on human-labelled public sets | card |
| lev (Qwen3.5-4B LoRA) | untuned backbone 0.826 on summeval-consistency | lower after fine-tuning | "Fine-tuning introduced that" |
| Kev date arithmetic | base handled it | regressed; fixed with stated day counts + `KEV_DATE_FACTS=1` | issue #8 |

- Gains are measured in distribution; Kev and decider report separate regression checks.
- Start from a released decision checkpoint (Kev `--init_from`; decider replay toward the prior checkpoint).
- Refit temperatures on held-out data after training (Laya, Kev, decider, JEV).
- Distillation from Jev inherits Jev's errors (JEV-27B limitations).
- Knowledge-heavy tasks track base-model size (Kev: MMLU-Pro 0.52 vs Jev 0.84; decider: MMLU/MedQA/ARC "improves little").

## Sources

- READMEs: `github.com/jaredpalmer/kev` (plus the `jaredpalmer/kev-4b` card), `github.com/Mapika/decider`, `github.com/NandhaKishorM/laya`, `github.com/fastino-ai/GLiNER2`, `github.com/togethercomputer/tev1`, `github.com/Contrastive-LM/CLM`.
- Model cards: `convaiinnovations/laya`, `Mapika/decider-2b`, `autotrust/JEV-27B`, `com-kotobalabs/open-jev-deberta-v3-large`, `VTXAI/VTX-JEV-1`, `denis-pplx/autojev-27b`, `EldanRing/Winnow-E4B`, `chaoliangUNSW/Jev-Style-Qwen3.5-2B-Decision-GGUF`, `chaoliangUNSW/Jev-Style-2B-Decision-v3-MLX`, `alibiserikbay/JevK5`, `aimeigaoshou/agent-jev`, `interfaze-ai/lev`, `monotykamary/LFM2.5-2.6B-RLCD` (metadata only).
- Datasets: `huggingface.co/datasets/fastino/fast-decisions`.
- `huggingface.co/docs/huggingface_hub/guides/jobs` (flavors, prices, timeout); [Train Models on Jobs](https://huggingface.co/docs/hub/jobs-training), [Jobs configuration](https://huggingface.co/docs/hub/jobs-configuration), [Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing), [Jobs examples](https://huggingface.co/docs/hub/jobs-examples) (read 2026-10-02).
- Liquid AI LFM2 fine-tuning: `docs.liquid.ai/lfm/getting-started/intro`, `huggingface.co/LiquidAI/LFM2.5-2.6B-Base`.
- Jev Decision Index `data/index.json` (0.2.1).

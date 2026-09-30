# Fine-tuning decision models

Survey date: 2026-09-30. Research only: no training was run and no weights were downloaded. Commands and numbers are quoted from the cited cards and READMEs. "n/d" = not documented.

## Architectures and what gets trained

| Readout | Trained parts | Examples |
|---|---|---|
| Encoder + option-marker head (softmax within each question) | full encoder + head | Laya, open-jev-deberta-v3-large, Julia-1, VTX-JEV-1 |
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

- GLiNER2: `pip install gliner2[train]`, then `ExtractorTrainer(AutoExtractor.from_pretrained("fastino/gliner2-base-v1"), TrainingConfig(output_dir="./output", num_epochs=10)).train(train_data="train.jsonl")`. Starting from `fastino/GLiNER2.5-Decide` with this trainer is not shown (unverified).
- Laya notebook: `notebooks/laya_finetune_typed_decisions_2xT4_kaggle.ipynb` in `NandhaKishorM/laya`; uses gradient checkpointing (`model.head_checkpointing = True`). README: "The notebook's calibration samples come from its training items; evaluate on separate held-out data before claiming an improvement." Browser-agent example: `docs/finetune_browser_agent.md`, weights at `cklxx/laya-browser`.

## Qwen-based decoders

Qwen3.5 mixes Gated DeltaNet (linear attention) and attention layers. The Kev README states "The DeltaNet kernels have no MPS implementation"; the decider card requires `flash-linear-attention` (Triton, CUDA). Qwen3 is attention-only.

| Model (backbone) | Method | Data format | Hardware | Mac feasibility |
|---|---|---|---|---|
| [Kev](models/kev.md#fine-tuning) (Qwen3.5-0.8B/4B/9B-Base) | LoRA r16 on attention, MLP and DeltaNet projections + pointer head; `--init_from` a released checkpoint | JSONL, one API request per line with `label` per question (`choice`: option name; `noul`: `true`/`false`; `score`: level index from 0) | `--batch 1 --accum 8` bf16 fits 0.8B on a 4 GB GPU; Modal skill, ~$1 per Kev-4B run on H100 | documented: one job at a time; DeltaNet falls back to reference code |
| decider (Mapika; Qwen3.5) | earlier stages: full fine-tune, CE on ~95 public datasets, ≤10 options per example. v11: LoRA r64, α128, merged; lr 1e-4, 1,676 steps × 65,536 tokens, 42,749 rows; replay rows via KL(p_v10 ‖ p_model) | registry and generators in `Mapika/decider` (`decider/data/mixture.py`) | CUDA; `scripts/train.sh full` | no Mac path |
| autotrust JEV-9B / 27B | LoRA + 24-slot linear head on a frozen base; 27B 108.9M trained parameters, 9B 40.2M | `SargeDev/jev-distill-corpus-v3` (655k+ rows, mostly Jev 1.13 distributions), KL loss | 27B ≈9.2 B200-hours; 9B ≈3 | no Mac path; training code not in cards |
| AutoJev-27B | full-weight SFT, 73,000 examples, 286 updates | corpus not bundled | one H200 | no Mac path |
| Jev-Style v1 (Qwen3.5-2B) | LoRA r16 on all linear layers, log-score loss, custom chunk-parallel DeltaNet forward | n/d | n/d | MLX inference documented (`mlx-lm==0.31.3`, patched `GatedDeltaNet.__call__`) |
| JevK5 v0.3 | teacher questions kept only when two independent answers agree + public train-split replay | n/d | n/d | n/d |
| [Tev1](models/tev1.md) (Qwen3.5-4B) | LoRA r8, 1 epoch, lr 5e-5 | 37,840 examples from 8 sources; builders in `togethercomputer/tev1` | Together fine-tuning, ~$17, ~25 min | n/d |
| [CLM-8B](models/clm-8b.md#fine-tuning) (Qwen3-8B, frozen) | heads only; InfoNCE or soft CE | (state, action) traces, or `LocalLLaMA/typed-decisions` | CUDA (`--gpu`); hardware and time n/d | n/d |

## Other backbones

| Model (backbone) | Method | Data format | Hardware | Mac feasibility |
|---|---|---|---|---|
| Winnow-E4B / 12B (Gemma 4) | LoRA r32, α64, merged in FP32, then GGUF | n/d | n/d | n/d |
| LFM2.5-2.6B-RLCD (LFM2.5) | full fine-tune | in repo (not reviewed) | Modal (`lfm25_pcd_modal.py`) | n/d |
| VTX-JEV-1 (7M embedding model) | full fine-tune, then LF4 4-bit quantization | 655,806 rows, 2 epochs; `training/` in the repo | timings on T4 | n/d |
| AgentJev (backbone n/d) | supervised + RLCD on executed coding pairs | n/d | n/d | n/d |

Liquid AI documents SFT/DPO for LFM2 with TRL + PEFT (QLoRA, then merge). `notnotsamuel/LFM2.5-350M-RLCD` scores 1.38 and LFM2.5-2.6B-RLCD 6.76 on DI 0.2.1.

## Converting a Jev-shaped request to GLiNER2 rows

Map each `choice` to a task with `labels` = option keys, each `noul` to a two-label task, and each `score` to an ordinal task with string-digit labels (the `fastino/fast-decisions` shape adds `"multi_label": bool`). Neither project documents this mapping.

```jsonl
{"input": "This movie is absolutely fantastic! I loved every minute of it.", "output": {"classifications": [{"task": "sentiment", "labels": ["positive", "negative", "neutral"], "true_label": ["positive"]}]}}
```

## Hardware

- **Apple Silicon (M5 Max, 128 GB).** Unified memory holds bf16 weights of every model here, including 27B (~54 GB) and 35B-A3B (~65–69 GB). The constraints are missing MPS kernels (DeltaNet) and CUDA-only scripts. `mlx_lm.lora` on a Qwen3.5 base is general MLX tooling that no decision-model author documents.
- **Hugging Face Jobs.** Pay-per-second; default timeout 30 minutes. Command shape: `hf jobs uv run --name sft-training --flavor a10g-small "<script-url-or-path>"`. Region selection is not documented.

| Flavor | GPU | $/h | Fits (from cards) |
|---|---|---:|---|
| `t4-small` / `t4-medium` | 1× T4 16 GB | 0.40 / 0.60 | Laya targets 2×T4 (no 2×T4 flavor) |
| `a10g-small` / `a10g-large` | 1× A10G 24 GB | 1.00 / 1.50 | Kev-0.8B/4B LoRA; GLiNER2; open-jev-deberta |
| `a10g-largex2` | 2× A10G | 3.00 | closest to Laya's 2×T4 |
| `l40sx1` | 1× L40S 48 GB | 1.80 | Kev-9B LoRA |
| `a100-large` | 1× A100 80 GB | 2.50 | 27B LoRA |
| `h200` | 1× H200 141 GB | 5.00 | AutoJev-27B full SFT |
| `rtx-pro-6000` | 1× RTX PRO 6000 96 GB | 2.75 | Decision Index evaluation GPU |

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

- READMEs: `github.com/jaredpalmer/kev`, `github.com/NandhaKishorM/laya`, `github.com/fastino-ai/GLiNER2`, `github.com/togethercomputer/tev1`, `github.com/Contrastive-LM/CLM`.
- Model cards: `convaiinnovations/laya`, `Mapika/decider-2b`, `autotrust/JEV-27B`, `com-kotobalabs/open-jev-deberta-v3-large`, `VTXAI/VTX-JEV-1`, `denis-pplx/autojev-27b`, `EldanRing/Winnow-E4B`, `chaoliangUNSW/Jev-Style-Qwen3.5-2B-Decision-GGUF`, `chaoliangUNSW/Jev-Style-2B-Decision-v3-MLX`, `alibiserikbay/JevK5`, `aimeigaoshou/agent-jev`, `interfaze-ai/lev`, `monotykamary/LFM2.5-2.6B-RLCD` (metadata only).
- Datasets: `huggingface.co/datasets/fastino/fast-decisions`.
- `huggingface.co/docs/huggingface_hub/guides/jobs` (flavors, prices, timeout).
- Liquid AI LFM2 fine-tuning: `docs.liquid.ai/lfm/getting-started/intro`, `huggingface.co/LiquidAI/LFM2.5-2.6B-Base`.
- Jev Decision Index `data/index.json` (0.2.1).

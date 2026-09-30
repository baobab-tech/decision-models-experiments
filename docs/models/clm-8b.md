# CLM-8B

| | |
|---|---|
| Vendor | Contrastive-LM (Jacky Kwok, Hangoo Kang, Tarun Suresh, Jon Saad-Falcon, Marco Pavone, Christopher Ré, Azalia Mirhoseini; affiliations not stated) |
| Type | Contrastive dual encoder: frozen encoder (last-token pooling) + state head and action head (20M trainable parameters each); score = dot product, softmax over candidates |
| Backbone | Qwen3-8B |
| Size | Head `CLM_v0.1-8B.pt` 75 MB; encoder ~16 GB bf16 (local-jev-bench) |
| Licence | Apache-2.0 (code, `contrastive-lm` package, heads); Qwen3-8B Apache-2.0 |
| Run it via | `pip install contrastive-lm`; vLLM pooling server for the encoder + `clm-serve` (:8700). Vendor target: one NVIDIA GPU. Mac: vllm-metal (third-party recipe) |

Checked 2026-09-30. Nothing was run locally; no weights were downloaded.

## Overview

- Code: [`Contrastive-LM/CLM`](https://github.com/Contrastive-LM/CLM) (created 2026-09-23, last push 2026-09-24, 2,591 stars). Weights: [`Contrastive-LM/CLM-v0.1-8B`](https://huggingface.co/Contrastive-LM/CLM-v0.1-8B) (last modified 2026-09-24, 2,392 downloads, commit `e939398d`; `config.json`: `encoder_pooling: last-token`, `embedding_dim: 4096`). Also on HF: `deepswe-clm-heads-8k`, datasets `CLM-v0.1-Pretrain-Nemotron`, `deepswe-clm-train-embeddings-8k`.
- PyPI [`contrastive-lm`](https://pypi.org/project/contrastive-lm/) 0.1.0 (2026-09-24), Python ≥ 3.10, hard dependencies `torch>=2.1`, `vllm>=0.6`. Announced 2026-09-23 ([MarkTechPost](https://www.marktechpost.com/2026/09/23/contrastive-lm-releases-clm-8b-an-open-system-one-model-that-scores-agent-actions-up-to-9x-faster-than-jev/)); `/v1/models` reports `release_date: 2026-09-19`. [Notion blog](https://contrastive-lm.notion.site) did not render. Multimodal CLM-35B announced for "early October" (HF card).
- Focus: agent actions (computer use, games, tool calling) and best-of-N verification. Typed questions reuse the same ranking primitive.
- Training: bidirectional InfoNCE over a B × B similarity matrix. Pre-training on ~60M Nemotron DQA pairs; mid-training on ~30M hard negatives generated with Gemini 2.5 Flash-Lite; post-training on ~1M agent trajectories (Agent Data Protocol, Endless-Terminals, LiteCoder-Terminal-SFT) with 40% Nemotron replay.
- Inference: one encoder pass per new text, one dot product per cached candidate. No fitted temperature ships; `clm-raw` is an ablation (cosine in raw encoder space).

## Schema

`clm-serve` exposes a TypeSafe-shaped `POST /v1/systemone`; the README's client is CLM's own `CLMClient`. Whether the TypeSafe SDK works unchanged is not documented (unverified). README example, with outputs:

```python
from clm import CLMClient, Choice, Noul, Score

client = CLMClient()                          # CLM_BASE_URL (default http://127.0.0.1:8700), CLM_API_KEY
r = client.system_one(
    state="Customer: my invoice was charged twice and nobody answers the phone!",
    questions={
        "urgency": Noul(instructions="Is this urgent?"),
        "department": Choice(instructions="Which team should handle this?",
                             criteria={"billing": "Charges, invoices, refunds", "technical": "Bugs and outages"}),
        "frustration": Score(instructions="How frustrated is the customer?", criteria=["Calm", "Frustrated", "Very angry"]),
    },
)
r.answers["urgency"].noul                # 0.41022
r.answers["department"].probabilities    # {'billing': 0.93878, 'technical': 0.06122}
r.answers["frustration"].score           # 1.98386 (expected level, 0..2)
r.usage.input_tokens, r.latency_ms       # 38, 58.1 (106 tokens on a cold cache)
```

Differences from [../concepts.md](../concepts.md#typed-question-format):

- Extra request fields: `model` (`clm-latest` default, `clm-raw`, or any from `GET /v1/models`); `temperature` (0, 100], default 1, divides logits.
- The state head sees `state + "\n\n" + instructions`; each option is embedded as its description (or its key if empty) (`src/clm/schema.py`). Options are scored independently, so order cannot change the answer.
- Choice: no option cap found in `schema.py` (unverified). Score: ≥ 2 levels, no upper cap found (unverified); levels are independent candidates with no ordinal modelling; `score` = expected level index.
- Noul: two-candidate softmax over `"true: Yes. This is true: <instructions>"` and `"false: No. This is false: <instructions>"` unless `criteria` gives descriptions.
- `confidence` = top probability minus the mean of the others ("TypeSafe-style" docstring). Kev documents `(p_max − 1/K)/(1 − 1/K)` as TypeSafe's reference; which matches Jev is unverified.
- `usage.input_tokens` = encoder tokens on cache misses; `billing_units` = number of questions. Errors: `401`, `422` (also unknown model), `502` embedder unreachable. Header `X-CLM-Latency-Ms`.
- Extra routes: `POST /v1/rank` (`{"context", "question", "answers": [...]}` → ranked), `GET /v1/models`, `GET /health` (cache occupancy, hit rate), `GET /` playground (`--no-ui` disables). Auth: `CLM_API_KEY` requires a bearer token. `--cors` off by default.

## Benchmarks

Vendor, zero-shot, one RTX 4090 (README figures, MarkTechPost table):

| Task | CLM latency | Jev latency | CLM success | Jev success |
|---|---:|---:|---:|---:|
| T-Rex (Chrome dino) | 16.5 ms | 149.8 ms | 5/5 | 5/5 |
| BFCL v4 tool calling | 76.8 ms | 125.5 ms | 95.2% | 99.2% |
| WikiRacing | 79.8 ms | 225 ms | 26/30 | 30/30 |
| Super Mario | 33.5 ms | 132.6 ms | 5/5 | 5/5 |

- README calls this "on par with Jev". HF card: "With ~1k candidates, CLM is 13× faster than Jev" (setup not given).
- Verifier, best-of-N with fine-tuned heads (not the released checkpoint), H100: DeepSWE 38 held-out tasks (Opus 5 candidates) 81.6% (31/38) vs Jev 71.1%; Terminal-Bench 2.1, 30 tasks (Fable 5 candidates) 87.6% vs 83.1%. Latency 4.1–5.7× lower than Jev.
- Mid-training ablation, ~100K held-out questions (1 gold, 10 hard negatives): pre-training 52.1% top-1; + mid-training 69.2%; hard negatives from the start peak at 62.4%.
- Vector cache, RTX 4090, server p50, 3 → 50 actions: new state each call 28.6 → 28.0 / 28.8 → 28.1 ms; revisited states (20 rooms) 1.7 → 0.6 / 2.0 → 0.7 ms.
- No vendor calibration metric (ECE, Brier).

Independent: [local-jev-bench](https://github.com/tak-bro/local-jev-bench), M3 Max 36 GB, vllm-metal:

| Set | CLM-8B | First-call p50 | Kev-4B | AnyJev L0 |
|---|---:|---:|---:|---:|
| English 30 items (105 decisions) | 39% | 326.6 ms | 89% | 81% |
| Korean 30 items | 41% | 354.0 ms | 87% | 84% |
| BANKING77 20-way (300) | 20% | 142.3 ms | 89% | 80% |

- Order flip on BANKING77-20: 0/300 (possibly structural). It matched the README's `department` and `frustration` answers but got `urgency` 0.852 vs 0.41 (unresolved). vllm-metal embeddings matched transformers (MPS, bf16) at cosine ≥ 0.9998 on four probes.

## Running it

No vendor MPS or MLX path; heads run on CUDA if available, else CPU (`CLM_DEVICE` overrides). Vendor (Linux, NVIDIA):

```bash
pip install contrastive-lm
vllm serve Qwen/Qwen3-8B --served-model-name qwen3-8b --runner pooling --max-model-len 2048 --port 8090 &
clm-serve        # API on :8700; downloads the 75 MB head on first run
```

Mac recipe from local-jev-bench (third party; M3 Max 36 GB, vllm-metal 0.30.0, Python ≥ 3.12):

```bash
brew tap vllm-project/vllm-metal https://github.com/vllm-project/vllm-metal   # the tap needs the URL
brew install vllm-project/vllm-metal/vllm-metal
export VLLM_ENABLE_V1_MULTIPROCESSING=0 GLOO_SOCKET_IFNAME=lo0 VLLM_HOST_IP=127.0.0.1
vllm serve Qwen/Qwen3-8B --served-model-name qwen3-8b --runner pooling \
  --pooler-config '{"seq_pooling_type": "LAST", "use_activation": true}' \
  --max-model-len 2048 --gpu-memory-utilization 0.7 --host 127.0.0.1 --port 8090
uv run clm-serve --host 127.0.0.1 --port 8700 --emb-url http://127.0.0.1:8090/v1/embeddings \
  --emb-model qwen3-8b --max-tokens 2048
```

- Without `GLOO_SOCKET_IFNAME=lo0 VLLM_HOST_IP=127.0.0.1` the engine hung at init. The pooler config gives last-token pooling with L2 normalisation, which the head expects.
- `--gpu-memory-utilization` sets the Metal wired limit: 0.7 reserved about 20 GB on 36 GB; on 128 GB it scales with the wired limit (unverified).
- `contrastive-lm` only calls the embeddings endpoint over HTTP; the recipe blocks the second vLLM install with `override-dependencies = ["vllm; sys_platform == 'never'"]` in `pyproject.toml`. Without it, behaviour on macOS is untested here.
- Pre-fetch: `hf download Qwen/Qwen3-8B` and `hf download Contrastive-LM/CLM-v0.1-8B` (otherwise `clm-serve` fetches the head to `~/.cache/clm/`). Ollama is not supported (different pooling and API). GPU-free playground mock: `tools/playground_mock.py`. Ranking in-process: `from clm import Engine; Engine(emb_url="http://127.0.0.1:8090/v1/embeddings").rank(question, candidates)`.

## Scaling limits

- **Options:** no cap found (unverified). Each distinct option text is embedded once into an LRU vector cache (`--action-cache`, default 2% of device memory); a cached option costs a dot product. 100+ options: one encoder pass per uncached option, then O(K) dot products. Latency is flat from 3 to 50 cached actions; the ~1k-candidate claim is the only large-K data point. Accuracy vs option count is not documented as of 2026-09-30.
- **Multi-label:** not in one question (softmax assumes one answer). Use one `noul` per label, or `POST /v1/rank` and threshold. Probabilities are relative to the candidate set (HF card).
- **Input length:** default 2,048 tokens (`--max-model-len` on vLLM, `clm-serve --max-tokens`), including appended instructions. Longer states are truncated without an error (local-jev-bench rejects them itself). Raising both (e.g. 8,192) needs more GPU memory. ~100 tokens: one encoder pass (~28 ms on RTX 4090). Long-state accuracy is not documented as of 2026-09-30.

## Fine-tuning

- Only the heads train; the encoder stays frozen. `train/finetune.py --task clm` ((state, action) traces, in-batch InfoNCE, `--holdout-folds` / `--holdout-tasks`) or `--task choice` (`LocalLLaMA/typed-decisions`, `--loss infonce|softce`, `--targets soft|hard`).
- Defaults: `--epochs 20`, `--proj 512`, `--batch` 2048 (clm) / 256 (choice), `--lr` 5e-4 (choice), `--max-len` 8,192 (clm) / 2,048 (choice), `--gpu-mem 0.85`. Embeddings come from offline vLLM or a pooling server (`--embed-url`); the `--gpu` index argument targets CUDA.
- Typed decisions: `python train/finetune.py --task choice --data LocalLLaMA/typed-decisions --workflow all --init-ckpt "$(clm-download)" --out-dir runs/typed`.
- DeepSWE reproduction (31/38): `hf download Contrastive-LM/deepswe-clm-heads-8k`, then `evaluation/bon_eval.py`; fine-tune with `--task clm --holdout-tasks heads/deepswe/heldout_tasks.json --batch 512`. The README's `Contrastive-LM/deepswe-clm-embeddings-8k` is not in the org listing; the listed one is `deepswe-clm-train-embeddings-8k`.
- `docs/FINETUNING.md` is a prompt for an autonomous agent loop that edits `train/finetune.py`, not a human guide.
- Load custom heads with `clm-serve --ckpt PATH` (or `--ckpt-dir`, `--model NAME=PATH`); they hot-reload. A head works only with the encoder and pooling it was trained on.
- Hardware, time and data-size guidance are not documented as of 2026-09-30.

## Data governance

- **Self-host / air-gap:** yes. Encoder (vLLM) and `clm-serve` run locally; local-jev-bench binds 127.0.0.1. The only documented outbound call is the first-run head download (skip with `--ckpt PATH`).
- **Licences:** code and package Apache-2.0 (PyPI, repo LICENSE); heads Apache-2.0 (HF card); Qwen3-8B Apache-2.0.
- **Hosted option:** none. No vendor API; no region, retention, DPA or training-on-inputs terms apply.
- **Provenance and trust:** training data described at dataset level only (Nemotron DQA, Gemini 2.5 Flash-Lite negatives, ADP, Endless-Terminals, LiteCoder-Terminal-SFT); their licences are not listed. Training on Gemini outputs may be restricted by Google's API terms (unverified; not addressed). Author affiliations not stated. The head is a `torch.save` pickle with no published checksum. 0.1.0 is the only PyPI release; no push since 2026-09-24.

## Caveats

- Low independent accuracy on classification (20% BANKING77-20, 39–41% on ticket items); the vendor evaluates agent actions and verification.
- "On par with Jev" sits beside lower BFCL v4 and WikiRacing success. Verifier results use fine-tuned heads. No calibration metrics or fitted temperature. Confidence formula differs from Kev's documented TypeSafe formula.
- A README Noul value (0.41) was not reproduced (0.852). States over 2,048 tokens are truncated silently. The working Mac path is third-party.

## Sources

- [GitHub: Contrastive-LM/CLM](https://github.com/Contrastive-LM/CLM) (README; `src/clm/schema.py`, `src/clm/heads.py`, `train/finetune.py`, `serve_qwen3_8b.sh`, `docs/FINETUNING.md`)
- [HF: Contrastive-LM/CLM-v0.1-8B](https://huggingface.co/Contrastive-LM/CLM-v0.1-8B) (card, `config.json`) and [HF API](https://huggingface.co/api/models/Contrastive-LM/CLM-v0.1-8B)
- [PyPI: contrastive-lm](https://pypi.org/project/contrastive-lm/)
- [MarkTechPost, 2026-09-23](https://www.marktechpost.com/2026/09/23/contrastive-lm-releases-clm-8b-an-open-system-one-model-that-scores-agent-actions-up-to-9x-faster-than-jev/)
- [Contrastive-LM blog (Notion)](https://contrastive-lm.notion.site)
- [GitHub: tak-bro/local-jev-bench](https://github.com/tak-bro/local-jev-bench) (README, `scripts/serve-embed.sh`, `scripts/serve-clm.sh`, `pyproject.toml`)
- [vllm-metal](https://github.com/vllm-project/vllm-metal)
- [HF: Qwen/Qwen3-8B](https://huggingface.co/Qwen/Qwen3-8B)

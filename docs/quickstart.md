# Quickstart

Easiest ways to get a first decision from each model, on an Apple Silicon Mac or through an API. Details and caveats are in each [model doc](models/). None of these commands has been run in this repo yet.

## Pick a path

| You want | Use | Needs |
|---|---|---|
| The reference model, no local setup | [Jev](models/jev.md) API | TypeSafe early-access key |
| A free hosted model | [Liquid d1](models/liquid-d1.md) `d1:free` | Liquid console key |
| Local, small, CPU-friendly, open licence | [GLiNER2.5-Decide](models/gliner-decide.md) | `uv`, ~2 GB |
| Local Jev-compatible server (same request format as Jev) | [Kev-4B](models/kev.md) (MLX) or [Bonsai-Llama-Jev](models/bonsai-llama-jev.md) (llama.cpp) | ~3 GB / ~20 GB |
| Tiny and fast local model | [Laya](models/open-reproductions.md#laya) | `pip install laya` |
| Any open LLM as a decision model | [AnyJev](models/anyjev.md) | a Hugging Face model, `anyjev[hf]` |

Keys go in `.env`, which is gitignored (see [AGENTS.md](../AGENTS.md)). API-only models process data in the US; see [data-governance.md](data-governance.md) before sending anything non-public.

## One client for every Jev-compatible endpoint

Jev, d1, Kev, Laya (`laya-serve`), Bonsai-Llama-Jev, Decider 1 and Solar Decide all accept the same `/v1/systemone` request ([concepts.md](concepts.md)). The TypeSafe SDK talks to any of them by changing `base_url`:

```python
# /// script
# dependencies = ["typesafe-sdk"]
# ///
import os
from typesafe_sdk import Choice, Noul, TypeSafeClient

ENDPOINTS = {  # base_url, api key, model
    "jev":    ("https://api.typesafe.ai",   os.getenv("TYPESAFE_API_KEY"), None),
    "d1":     ("https://api.liquid.ai",     os.getenv("LIQUID_API_KEY"),   "d1:free"),
    "kev":    ("http://127.0.0.1:8009",     "local",                       "kev-latest"),
    "bonsai": ("http://localhost:54100",    None,                          None),
}

base_url, key, model = ENDPOINTS[os.getenv("TARGET", "jev")]
with TypeSafeClient(base_url=base_url, api_key=key) as client:
    r = client.system_one(
        **({"model": model} if model else {}),
        state="I've been charged twice for my order and nobody answers my emails.",
        questions={
            "department": Choice(instructions="Which team handles this",
                                 criteria={"billing": "Payments", "technical": "Bugs", "shipping": "Delivery"}),
            "is_urgent": Noul(instructions="The message conveys urgency"),
        },
    )
print(r.answers["department"].choice, r.answers["is_urgent"].noul)
```

Run with `TARGET=d1 uv run quickstart.py`. Liquid's [decision model guide](https://docs.liquid.ai/guides/decision-model-guide) uses this SDK with `base_url="https://api.liquid.ai"` (checked 2026-09-30); the raw HTTP path is `/decisions/v1/systemone` ([liquid-d1.md](models/liquid-d1.md#running-it)).

## Local models

**GLiNER2.5-Decide** (DeBERTa-v3-large encoder, 340M per card, Apache-2.0):

```bash
uv venv --python 3.10 && uv pip install "gliner2[local]==2.0.0"
```

```python
from gliner2 import AutoExtractor
m = AutoExtractor.from_pretrained("fastino/GLiNER2.5-Decide")
print(m.classify_text("Please confirm the retention rule before Friday's audit.",
                      {"intent": ["fyi", "request", "complaint"], "urgency": ["low", "high"]}))
```

It has its own Python API; it does not serve `/v1/systemone`.

**Kev-4B** (Qwen3.5-4B + pointer head, Apache-2.0, MLX):

```bash
git clone https://github.com/jaredpalmer/kev.git && cd kev
uv sync --extra serve
uv run --extra serve python -m kev.serve --run jaredpalmer/kev-4b --port 8009
```

**Bonsai-Llama-Jev** (Bonsai-2-27B, 2-bit Q2_64 GGUF, llama.cpp; ~20 GB disk):

```bash
git clone https://github.com/kyr0/Bonsai-Llama-Jev && cd Bonsai-Llama-Jev
make setup && make start   # serves :54100
```

**Laya** (ModernBERT, 421M, Apache-2.0):

```bash
uv pip install laya   # then: from laya import Router; Router()
```

**JevK5** (Qwen3.5-4B, GGUF on llama.cpp's Metal backend):

```bash
llama-server --hf-repo alibiserikbay/JevK5-GGUF --hf-file jevk5-4b-v0.3-Q8_0.gguf -c 8192 -ngl 99
```

Answers come from the `jevk5` client, not from plain chat. See [open-reproductions.md](models/open-reproductions.md#jevk5).

## API-only models

| Model | Endpoint | Key |
|---|---|---|
| [Jev](models/jev.md) | `POST https://api.typesafe.ai/v1/systemone` | `TYPESAFE_API_KEY` |
| [Liquid d1](models/liquid-d1.md) | `POST https://api.liquid.ai/decisions/v1/systemone`, or Vercel AI Gateway `liquid/d1` | `LIQUID_API_KEY` / `AI_GATEWAY_API_KEY` |
| [Decider 1](models/decider-1.md) | `POST https://meragpt.com/v1/systemone` | see doc |
| [Solar Decide](models/solar-decide.md) | `POST https://api.upstage.ai/v1/systemone` (beta) | see doc |
| [Span-01](models/span-01.md) | `POST https://api.respan.ai/api/v1/scores` (own format) | see doc |
| [Tev1](models/tev1.md) | Together chat completions, `together/Tev1-4B-experimental`; weights also on Hugging Face | `TOGETHER_API_KEY` |
| [OpenAI Decisions API](models/openai-decisions-api.md) | limited preview, no public docs | — |

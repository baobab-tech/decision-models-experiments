# ModernJEV-Decide-Preview (Maziyar Panahi)

| Field | Value |
|---|---|
| Vendor | Maziyar Panahi (individual; CNRS, per his LinkedIn post) |
| Type | Choice-ranking encoder for agent decisions: scores each supplied option, returns the top label. No Score or Noul |
| Backbone | `answerdotai/ModernBERT-base` (revision `8949b90`), cross-encoder with one scalar scoring head |
| Size | 149,605,633 parameters (HF safetensors total) |
| Licence | Apache-2.0 (HF `cardData`) |
| Run it via | `predict.py` in the repo: `DecisionModel("MaziyarPanahi/ModernJEV-Decide-Preview").decide(state=…, question=…, criteria=…)` |
| Status | Experimental preview. Repo created 2026-09-30, last modified 2026-10-01, revision `d5b398e`; public and ungated; 93 downloads, 8 likes |

Checked 2026-10-02.

## Overview

The model reads a conversation, its policy and the tool list, then scores each choice in the question.
Choice labels and descriptions are input text, so the label set is open.
It was trained on 60,000 decisions from [AgentToolDecisions-180K](#training-data) for two task families: next action (`text_response`, `tool_call`, …) and tool selection.
The card calls it "a small choice-ranking prototype, not a Jev reproduction".
It does not generate tool arguments or run tools.

The author trained it with HuggingChat's ML Intern agent plus Codex, on Hugging Face Jobs. The card publishes the prompt, recipe, job IDs and cost audit. See [Fine-tuning](#fine-tuning).

## Schema

- `decide(state, question, criteria)`. `state`: dict or text. `criteria`: dict of label → description, or a list of answer strings.
- Returns `predicted_label`, `candidates` (label, `score`, `raw_score`, `rank`), `truncated`, `max_sequence_length`.
- Scores are a softmax within the supplied choice set. The card: "they are not calibrated confidence estimates and cannot be compared directly across unrelated requests."
- Not TypeSafe-compatible: no `/v1/systemone` server, no `questions` map, no Score or Noul.

Documented example output ([example-output.json](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview/blob/main/example-output.json)): `lookup_order` 0.743 vs `search_catalog` 0.257.

## Benchmarks

Author's held-out test split of the training dataset, final checkpoint, one run ([card](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview)):

| Task | n | Model | Majority label | Allowed-choice frequency baseline | Uniform |
|---|---:|---:|---:|---:|---:|
| Next action (3 choices) | 1,158 | 73.40% | 53.20% | 53.20% | 33.33% |
| Tool selection (median 20 choices, 11–32) | 542 | 62.18% | 14.58% | 22.88% | 5.19% |
| When2Call, task family not trained (4 choices) | 3,652 | 34.39% | 35.46% | — | 25% |

- On When2Call the model scores 1.07 points below always picking the majority label. The card: "general decision-making and clinical use remain unvalidated."
- An untrained scalar head on the same encoder scores 42.83% and 0.74%.
- Label order: 100% agreement across five permutations of 299 decisions.
- Label wording: in one routing check, the intended answer won at 2, 3 and 7 choices and lost at 20. Renaming labels changed the pick at 3 and 7 choices.
- Latency: one candidate forward pass on GPU, median 23.6 ms, p95 24.2 ms, without tokenization. A decision runs one pass per candidate.
- No Jev comparison was run. Not on Decision Index or JevBench as of 2026-10-02.
- The LinkedIn post's "62% vs 23%" matches the tool-selection row (62.18% vs 22.88%).

## Running it

```bash
pip install "torch==2.12.0" "transformers==5.17.0" "huggingface-hub==1.33.0"
hf download MaziyarPanahi/ModernJEV-Decide-Preview predict.py --local-dir modernjev
```

Then use `from predict import DecisionModel` as in the card.
The card still says "your Hugging Face account must have access" during the private preview; the HF API reported the repo public and ungated on 2026-10-02.
- **Mac:** ModernBERT-base runs in Transformers on CPU; the card ran When2Call checks on "local CPU FP32". MPS is not documented (unverified). Weights are ~0.6 GB in fp32 (inferred from 149.6M parameters).

## Scaling limits

- **Input:** 4,096 tokens per (state, choice) pair, including both sequences. The helper reports truncation; 414 test pairs were truncated.
- **Options:** no cap in code; trained on gold plus up to three negatives; tested with up to 32 choices. Cost grows linearly with choices, one forward pass each.
- **Multi-label:** not supported.

## Fine-tuning

- **Recipe:** [`recipe/train.py`](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview/blob/main/recipe/train.py); per-decision softmax cross-entropy over candidate scores; 60,000 decisions stratified by family, seed 42; 3,720 optimizer steps; flash-attn2 kernel; dataset revision `f2fb14e`.
- **Hardware and cost:** one A100-SXM4-80GB on HF Jobs at $2.50/h. Training 129.8 min ≈ $5.41; full job 157 min ≈ $6.58; all attempts and pilots $8.79. Estimates from runtime, "not reconciled invoice amounts" ([COST-AUDIT.json](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview/blob/main/COST-AUDIT.json)).
- **ML Intern replay:** a separate 6,000-decision run (1,500 steps, 996.9 s training) from one HuggingChat message with attached prompt and recipe, GLM-5.3-Flash as the agent model, $10 compute cap. The first attempt failed before GPU spend; the successful one needed one self-repaired retry. Its checkpoint is not the published weights.
- The 60k run "started with ML Intern; Codex debugged, launched and completed the run".

## Training data

[`MaziyarPanahi/AgentToolDecisions-180K`](https://huggingface.co/datasets/MaziyarPanahi/AgentToolDecisions-180K) (revision `22b9113`, created 2026-09-26; 167 downloads, 11 likes on 2026-10-02):

- 180,000 rows: 171,056 train / 2,713 validation / 6,231 test; no decision group or source row crosses splits.
- Six task families: next action type 79,238; tool selection 37,233; tool argument completeness 37,233 (Noul); tool or text 14,349; tool response preference 8,295; When2Call 3,652.
- Built from `nvidia/Nemotron-SFT-Agentic-v2` (153,704 rows) and `nvidia/When2Call` (26,296). Labels are programmatic or automated from upstream; no Jev or other proprietary output.
- Each row has a `request_json` ready to send to Jev (`"model": "jev-1.13.0"`).
- Licence `other`: When2Call CC BY 4.0; Nemotron components CC BY 4.0, Apache 2.0 and MIT, per the card (unverified). Each row records its source licence.

Listed in [experiments/common/datasets.md](../../experiments/common/datasets.md).

## Data governance

| Item | Status | Evidence |
|---|---|---|
| Self-host | Yes; weights on HF | [HF API](https://huggingface.co/api/models/MaziyarPanahi/ModernJEV-Decide-Preview) |
| Fine-tuning | Yes; full recipe published | [card](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview) |
| Processing location | Your hardware | |
| EU processing option | Yes, on your EU infra | |
| Retention / ZDR | Your control | |
| Training on inputs | No | |
| DPA / GDPR | Not needed (no processor) | |
| Certifications | Your infra's | |
| Weights licence | Apache-2.0; base ModernBERT Apache-2.0; training data under mixed upstream terms | [card](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview) |

The author's training ran on HF Jobs under the `OpenMed` namespace (region n/d). A replay on your own data sends it to HF Jobs and, through ML Intern, to HuggingChat.

## Caveats

- Preview from one author, one seed, one checkpoint. Results are on the test split of the same dataset it trained on.
- Below the majority baseline on the one task family it did not train on.
- Choice only; scores are not calibrated.
- The card's cost figures are runtime estimates, not invoices.

## Sources

- [Model card](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview) (revision `d5b398e`), [HF API](https://huggingface.co/api/models/MaziyarPanahi/ModernJEV-Decide-Preview), [example-output.json](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview/blob/main/example-output.json), [COST-AUDIT.json](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview/blob/main/COST-AUDIT.json), [recipe/train.py](https://huggingface.co/MaziyarPanahi/ModernJEV-Decide-Preview/blob/main/recipe/train.py)
- [Dataset card](https://huggingface.co/datasets/MaziyarPanahi/AgentToolDecisions-180K) (revision `22b9113`)
- Maziyar Panahi's LinkedIn post (2026-10-01; screenshot shared by the maintainer; URL not recorded)
- [HF Jobs pricing](https://huggingface.co/docs/hub/jobs-pricing)

All read 2026-10-02.

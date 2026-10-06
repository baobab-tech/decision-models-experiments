#!/usr/bin/env bash
# Experiment 02, first step: fine-tune each small encoder as an HF Job in the baobabtech namespace.
# Every job reads the llm_labels config from the Hub and pushes its model and metrics to a private
# baobabtech/evaldocs-excerpt-tagger-<encoder>-llm repo, so anyone with access can rerun a single line.
# Encoders: released since March 2026, <= ~300M parameters, context >= 8k tokens; ModernBERT-base and
# Ettin as 2025 references. Job ids are appended to results/jobs.tsv.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results

run() {  # run <base> [extra args...]; skips (base, args) already in results/jobs.tsv
  local base=$1; shift
  if skip "$base" "$*"; then echo "skip $base $*"; return; fi
  local id
  id=$(hf jobs uv run --flavor a10g-small --timeout 2h --namespace baobabtech --secrets HF_TOKEN --detach \
        --label experiment=02 --label base="$(echo "$base" | tr -c "a-zA-Z0-9_\n-" "_")" \
        train_encoder.py -- --labels llm --dataset-revision 5b5de6f220c8c48679c8d84eda4f508af29bd317 --base "$base" "$@" | grep -oE '[0-9a-f]{24}' | head -1)
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$id" "$base" "$*" | tee -a results/jobs.tsv
}

done_bases=$(cut -f3,4 results/jobs.tsv 2>/dev/null || true)
skip() { grep -qxF "$(printf '%s\t%s' "$1" "$2")" <<<"$done_bases"; }
# 2025 references
run answerdotai/ModernBERT-base
run jhu-clsp/ettin-encoder-150m
run jhu-clsp/ettin-encoder-32m
# Released since March 2026
run ibm-granite/granite-embedding-97m-multilingual-r2
run LiquidAI/LFM2.5-Encoder-230M --trust-remote-code
run Hcompany/NeoMME-260M --trust-remote-code
run microsoft/harrier-oss-v1-270m --context-first   # one-directional (Gemma 3 decoder)
run codefuse-ai/F2LLM-v2-80M --context-first        # one-directional (Qwen3 decoder)
run MaziyarPanahi/ModernJEV-Decide-Preview
# Two-tower: document context encoded once per report, excerpt encoded alone (~6x fewer tokens per excerpt)
run jhu-clsp/ettin-encoder-150m --arch two_tower
# Multilingual reference (2025)
run jhu-clsp/mmBERT-small
run Alibaba-NLP/gte-modernbert-base

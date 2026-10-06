#!/usr/bin/env bash
# Experiment 02 sweep 2: fine-tune small encoders as HF Jobs in the baobabtech namespace, each with its own recipe
# (train_encoder.py RECIPES). Every job reads the llm_labels config from the Hub and pushes its model and metrics
# to a private baobabtech/evaldocs-excerpt-tagger-* repo, so anyone with access can rerun a single line.
# Setup: countries from the country-name lookup; the encoder tags themes, regions and methods.
# Sweep 1 job ids: results/jobs.tsv. Sweep 2 job ids: results/jobs_sweep2.tsv; runs already listed are skipped.
# Usage: REV=<decision-models-evaluation-docs revision> ./sweep.sh
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results
JOBS=results/jobs_sweep2.tsv
REV=${REV:?set REV to the decision-models-evaluation-docs revision with the llm_labels config}
done_runs=$(cut -f3,4 "$JOBS" 2>/dev/null || true)

run() {  # run <base> [extra args...]
  local base=$1; shift
  if grep -qxF "$(printf '%s\t%s' "$base" "$*")" <<<"$done_runs"; then echo "skip $base $*"; return; fi
  local id
  id=$(hf jobs uv run --flavor a10g-small --timeout 3h --namespace baobabtech --secrets HF_TOKEN --detach \
        --label experiment=02 --label base="$(echo "$base" | tr -c "a-zA-Z0-9_\n-" "_")" \
        train_encoder.py -- --labels llm --dataset-revision "$REV" --base "$base" \
        --exclude-fields countries --country-lookup "$@" | grep -oE '[0-9a-f]{24}' | head -1)
  printf '%s\t%s\t%s\t%s\n' "$(date -u +%FT%TZ)" "$id" "$base" "$*" | tee -a "$JOBS"
}

# All encoders on the full training set (random 10,000 + balanced extra sample)
for base in answerdotai/ModernBERT-base jhu-clsp/ettin-encoder-150m jhu-clsp/ettin-encoder-32m jhu-clsp/mmBERT-small \
            Alibaba-NLP/gte-modernbert-base ibm-granite/granite-embedding-97m-multilingual-r2 \
            MaziyarPanahi/ModernJEV-Decide-Preview LiquidAI/LFM2.5-Encoder-230M Hcompany/NeoMME-260M \
            microsoft/harrier-oss-v1-270m codefuse-ai/F2LLM-v2-80M; do
  run "$base"
done
# Two-tower: document context encoded once per report
run jhu-clsp/ettin-encoder-150m --arch two_tower

# Learning curve: Ettin-32M on the random sample at 1,000 / 2,500 / 5,000 excerpts, and on the whole random sample
for n in 1000 2500 5000; do run jhu-clsp/ettin-encoder-32m --train-sample random --limit-train "$n"; done
run jhu-clsp/ettin-encoder-32m --train-sample random

#!/bin/bash
# Marker-fix sanity check on typed-decisions (2026-09-24): reruns the EXACT NLI-base headline recipe (mq_nli_typed,
# scripts/run_experiments6.sh line 55) with the fixed marker tokens, to confirm the [OPT]-marker bug did not inflate or
# deflate the 0.766+-0.008 headline before we redo the standard-benchmark suite. Not used for any paper number.
set -uo pipefail
cd "$(dirname "$0")/.."
source <(sed -n '/^PY=/,/^ollama stop/p' scripts/run_experiments7.sh | grep -v "^ollama")
BASE="$PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks typed_decisions --epochs 6 --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3"
mchk() { local mk=$1; local o=out/mcheck-typed-$mk
  step mcheck_$mk       $o/verdict_config.json $BASE --marker $mk --out $o
  step mcheck_${mk}_eval RESULTS_mcheck_typed_$mk.md $PY scripts/eval_mq.py --ckpt $o --typed-split test --kind specialist --dump-preds preds_mcheck_typed_$mk.jsonl --out RESULTS_mcheck_typed_$mk.md; }
echo "=== marker check start $(date -Is) ==="
mchk mask
mchk cls
echo "=== MARKER CHECK DONE $(date -Is) ==="

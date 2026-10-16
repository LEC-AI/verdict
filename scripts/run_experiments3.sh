#!/bin/bash
# Batch 3 (single GPU): waits for batch 2, then
#  (a) option-order fix candidate: retrain verdict-base with option-order shuffling, re-run robustness
#  (b) RAFT 5-fold CV + leaderboard-format predictions
#  (c) Laya dump + prompt probe on GPU (quick)
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
TASKS="route_topic,signal_positive,affect"
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching"
run() { local name=$1; echo "=== [$name] $(date -Is) ==="; shift; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -30; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

while pgrep -f "^bash scripts/run_experiments2.sh" >/dev/null; do sleep 60; done
echo "=== batch 2 finished, starting batch 3 $(date -Is) ==="
ollama stop qwen2.5:7b-instruct 2>/dev/null || true; sleep 2

run laya_dump  $PY scripts/eval_laya.py --tasks $TASKS --limit 200 --dump-preds preds_laya.jsonl --out RESULTS_laya.md
run laya_probe $PY scripts/probe_laya_prompt.py --limit 100 --out RESULTS_laya_prompt_probe.md

run shuf_train $PY scripts/train.py --tasks $TASKS --out out/verdict-base-shuf --epochs 3 --batch-size 32 --limit 20000 --shuffle-options
run shuf_eval  $PY scripts/eval_orgbench.py --ckpt out/verdict-base-shuf --tasks $TASKS --permute-options --prompt-variant --dump-preds preds_verdict_shuf.jsonl --out RESULTS_shuf.md
run shuf_calib $PY scripts/calibration.py --ckpt out/verdict-base-shuf --tasks $TASKS --ablation --fit-temp --out RESULTS_shuf_calib

run raft $PY scripts/eval_raft.py --epochs 10 --out RESULTS_raft.md

echo "=== BATCH 3 DONE $(date -Is) ==="

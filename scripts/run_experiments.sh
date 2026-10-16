#!/bin/bash
# Serial experiment driver (single GPU). Runs quick evals first, long rematch
# last. Stops with the failing step's exit code if a step fails. Each step
# logs to logs/ and writes a RESULTS_*.{md,json}.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
TASKS="route_topic,signal_positive,affect"

run() { local name=$1; echo "=== [$name] $(date -Is) ==="; shift; "$@" 2>&1 | { grep -vE "Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored" || true; } | tail -25; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

run latency        $PY scripts/bench_latency.py --ckpt out/verdict-base --endpoint http://localhost:11434/v1 --model qwen2.5:7b-instruct --n 256 --out RESULTS_latency
run pertask        $PY scripts/eval_orgbench.py --ckpt out/verdict-base --tasks "$TASKS" --out RESULTS_pertask.md
run calibration    $PY scripts/calibration.py --ckpt out/verdict-base --tasks "$TASKS" --ablation --out RESULTS_calib
run operating_curve $PY scripts/operating_curve.py --ckpt out/verdict-base --tasks "$TASKS" --out RESULTS_opcurve
run plain_baseline $PY scripts/baseline_plain.py --tasks "$TASKS" --epochs 3 --batch-size 32 --out RESULTS_plain.md

# free ollama VRAM before the large-model rematch
ollama stop qwen2.5:7b-instruct 2>/dev/null || true; sleep 2
run rematch_large_soft $PY scripts/train_typed.py --backbone answerdotai/ModernBERT-large --soft --out out/verdict-typed-large --epochs 6 --batch-size 8 --out-md RESULTS_typed_large.md

echo "=== ALL EXPERIMENTS DONE $(date -Is) ==="

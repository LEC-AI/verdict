#!/bin/bash
# Batch 4 (single GPU): waits for batch 3, then
#  (a) typed-decisions: base + soft labels (de-confounds backbone size vs soft labels)
#  (b) distillation label-count sweep on ORG3: train on {250,500,1000,2000} labels/task
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
ORG="email_needs_reply,email_escalate,email_priority"
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching"
run() { local name=$1; echo "=== [$name] $(date -Is) ==="; shift; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -30; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

while pgrep -f "^bash scripts/run_experiments[23].sh" >/dev/null; do sleep 60; done
echo "=== batch 3 finished, starting batch 4 $(date -Is) ==="

run typed_base_soft $PY scripts/train_typed.py --soft --out out/verdict-typed-base-soft --epochs 6 --out-md RESULTS_typed_base_soft.md

for n in 250 500 1000 2000; do
  run org_lim$n $PY scripts/train.py --tasks $ORG --out out/verdict-org-lim$n --epochs 3 --batch-size 32 --limit $n
  run org_lim${n}_eval $PY scripts/eval_orgbench.py --ckpt out/verdict-org-lim$n --tasks $ORG --out RESULTS_org_lim$n.md
done

echo "=== BATCH 4 DONE $(date -Is) ==="

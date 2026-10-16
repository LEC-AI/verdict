#!/bin/bash
# Serial driver, batch 2 (single GPU). Waits for batch 1 to finish, then:
#  distill ORG3 (needs ollama) -> single-task ablation x3 -> seeds 1,2 ->
#  train+eval org tasks -> calibration/opcurve on org.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
TASKS="route_topic,signal_positive,affect"
ORG="email_needs_reply,email_escalate,email_priority"
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\."

run() { local name=$1; echo "=== [$name] $(date -Is) ==="; shift; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -30; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

while pgrep -f baseline_plain.py >/dev/null; do sleep 30; done
echo "=== R1 finished, starting batch 2 $(date -Is) ==="

# ORG3 distillation with the local judge (ollama serves on demand)
run distill $PY scripts/distill.py --tasks $ORG --endpoint http://localhost:11434/v1 --model qwen2.5:7b-instruct --limit 4000 --audit 300 --out-dir data/jsonl
ollama stop qwen2.5:7b-instruct 2>/dev/null || true; sleep 3

# single-task ablation: one checkpoint per task, same recipe as verdict-base
for t in route_topic signal_positive affect; do
  run single_$t $PY scripts/train.py --tasks $t --out out/verdict-single-$t --epochs 3 --batch-size 32 --limit 20000
  run single_eval_$t $PY scripts/eval_orgbench.py --ckpt out/verdict-single-$t --tasks $t --out RESULTS_single_$t.md
done

# seeds 1,2 of the headline multi-task model
for s in 1 2; do
  run seed$s $PY scripts/train.py --tasks $TASKS --out out/verdict-base-s$s --seed $s --epochs 3 --batch-size 32 --limit 20000
  run seed${s}_eval $PY scripts/eval_orgbench.py --ckpt out/verdict-base-s$s --tasks $TASKS --out RESULTS_pertask_s$s.md
done

# org-authentic tasks: train on distilled silver labels, eval + calibration + opcurve
run org_train $PY scripts/train.py --tasks $ORG --out out/verdict-org --epochs 3 --batch-size 32
run org_eval $PY scripts/eval_orgbench.py --ckpt out/verdict-org --tasks $ORG --out RESULTS_org.md
run org_calib $PY scripts/calibration.py --ckpt out/verdict-org --tasks $ORG --ablation --fit-temp --out RESULTS_org_calib
run org_opcurve $PY scripts/operating_curve.py --ckpt out/verdict-org --tasks $ORG --out RESULTS_org_opcurve

echo "=== BATCH 2 DONE $(date -Is) ==="

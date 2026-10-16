#!/bin/bash
# Batch 9 (2026-09-25): BoolQ (cls, k=22) stability fix. Of the 5 final seeds at the chosen (marker,k)=(cls,22), seeds
# 2 and 4 stalled (test acc 64.3%/67.0%, near majority class) while 0,1,3 succeeded (~82%) -- the exact same stall
# signature as the large-model instability fixed in run_experiments6.sh (healthy epoch-1 train loss <=0.656, stalled
# >=0.672). Same protocol: rerun the STALLED seeds under candidate fixes, judge by training loss (no test peeking),
# then dev accuracy from the same runs, pre-registered pick (scripts/pick_stable2.py), then 5 FRESH final seeds of
# the winning recipe replacing the unstable ones.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching|Generating|return Agent|RuntimeWarning"
GPUJOB="python[0-9.]* (-u )?scripts/(train|train_typed|train_mq|eval_mq|export_laya_encoder|finetune_laya|eval_orgbench|eval_typed|eval_laya_typed|significance|pick_recipe|pick_stable|pick_stable2|pick_split|pick_split2|baseline_mc|baseline_pair|calibration|operating_curve|baseline_plain)\.py"
wait_gpu() { while pgrep -f "$GPUJOB" >/dev/null; do sleep 30; done; }
step() { local name=$1 done=$2; shift 2
  wait_gpu
  if [ -e "$done" ]; then echo "=== [$name] skip ($done exists) ==="; return; fi
  echo "=== [$name] $(date -Is) ==="; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -40; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

ollama stop qwen2.5:7b-instruct 2>/dev/null || true
echo "=== batch 9 start $(date -Is) ==="
RAW=answerdotai/ModernBERT-base
BASE="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --val-limit 2000 --init $RAW --tasks boolq --epochs 3 --batch-cases 8 --joint-layers 22 --marker cls --grad-ckpt"

declare -A ARGS=([warm20]="--lr 3e-5 --warmup-frac 0.2" [llrd]="--lr 1e-5 --warmup-frac 0.1 --llrd 0.9")
for c in warm20 llrd; do
  for sd in 2 4; do
    o=out/stab2-boolq-$c-full-s$sd
    step stab2_boolq_${c}_s$sd $o/verdict_config.json $BASE ${ARGS[$c]} --seed $sd --out $o
    step stab2_boolq_${c}_s${sd}_dev RESULTS_boolq_stab2${c}_s${sd}_dev.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split val --batch-cases 8 --out RESULTS_boolq_stab2${c}_s${sd}_dev.md
  done
done
step pick_stable2_boolq out/chosen_stable2_boolq.txt $PY scripts/pick_stable2.py --task boolq --configs warm20,llrd --stall-seeds 2,4 --dev-seeds 2,4 --baseline-dev 0.644

CHOSEN=$(cat out/chosen_stable2_boolq.txt 2>/dev/null)
sig() { step sig_$1 RESULTS_sig_$1.md $PY scripts/significance.py --cluster-field auto --a $2 --b $3 --name-a "$4" --name-b "$5" --out RESULTS_sig_$1.md; }
for s in 0 1 2 3 4; do
  o=out/boolq-cls-k22-fixed-s$s
  step boolq_fixed_s$s $o/verdict_config.json $BASE $CHOSEN --seed $s --out $o
  step boolq_fixed_s${s}_test RESULTS_boolq_mqclsk22fixed_s$s.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split test --batch-cases 8 --dump-preds preds_boolq_mqclsk22fixed_s$s.jsonl --out RESULTS_boolq_mqclsk22fixed_s$s.md
  LB=$(cat out/chosen_lr_boolq_pair.txt 2>/dev/null || echo 5e-5)
  sig boolq_clsk22fixed_s$s preds_boolq_mqclsk22fixed_s$s.jsonl preds_boolq_pair_lr${LB}_s$s.jsonl "Verdict-MQ cls k=22 (fixed)" "pair classifier"
done
echo "=== BATCH 9 DONE $(date -Is) ==="

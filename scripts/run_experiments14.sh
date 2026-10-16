#!/bin/bash
# Batch 14 (2026-09-25): BoolQ stability search, round 2 (proper protocol, mirrors the large-model fix's rigor).
# Round 1 (batches 9, 11, 12, 13) tried marker, depth, and the option-mixer as the culprit -- all four configurations
# showed a 40-60% stall rate, ruling out the architecture. This round holds the architecture fixed at the setting
# already shown healthy-or-stalled in a roughly even split (cls, k=0, no option-mixer) and instead searches the
# optimizer recipe (learning rate, warmup fraction) that every prior BoolQ run left untouched -- unlike typed-decisions,
# BoolQ never got a stability-tuned recipe. 4 candidates x 4 FRESH seeds each (seeds 10-13, unused elsewhere), full
# 3-epoch training, judged by DEV ACCURACY STABILITY directly (scripts/pick_stable3.py), not an early-loss proxy
# (round 1's mistake: epoch-1 loss overlapped between seeds that went on to succeed and seeds that stalled).
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching|Generating|return Agent|RuntimeWarning"
GPUJOB="python[0-9.]* (-u )?scripts/(train|train_typed|train_mq|eval_mq|export_laya_encoder|finetune_laya|eval_orgbench|eval_typed|eval_laya_typed|significance|pick_recipe|pick_stable|pick_stable2|pick_stable3|pick_split|pick_split2|baseline_mc|baseline_pair|calibration|operating_curve|baseline_plain)\.py"
wait_gpu() { while pgrep -f "$GPUJOB" >/dev/null; do sleep 30; done; }
step() { local name=$1 done=$2; shift 2
  wait_gpu
  if [ -e "$done" ]; then echo "=== [$name] skip ($done exists) ==="; return; fi
  echo "=== [$name] $(date -Is) ==="; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -40; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

ollama stop qwen2.5:7b-instruct 2>/dev/null || true
echo "=== batch 14 start $(date -Is) ==="
RAW=answerdotai/ModernBERT-base
BASE="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --val-limit 2000 --init $RAW --tasks boolq --epochs 3 --batch-cases 8 --joint-layers 0 --marker cls"
declare -A ARGS=([warm30]="--lr 3e-5 --warmup-frac 0.3" [lowlr]="--lr 1e-5 --warmup-frac 0.06" [lowlr_warm20]="--lr 1e-5 --warmup-frac 0.2" [verylow]="--lr 5e-6 --warmup-frac 0.1")
for c in warm30 lowlr lowlr_warm20 verylow; do
  for sd in 10 11 12 13; do
    o=out/stab3-boolq-$c-s$sd
    step stab3_boolq_${c}_s$sd $o/verdict_config.json $BASE ${ARGS[$c]} --seed $sd --out $o
    step stab3_boolq_${c}_s${sd}_dev RESULTS_boolq_stab3${c}_s${sd}_dev.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split val --batch-cases 8 --out RESULTS_boolq_stab3${c}_s${sd}_dev.md
  done
done
step pick_stable3_boolq out/chosen_stable3_boolq.txt $PY scripts/pick_stable3.py --task boolq --configs warm30,lowlr,lowlr_warm20,verylow --seeds 10,11,12,13

CHOSEN=$(cat out/chosen_stable3_boolq.txt 2>/dev/null)
sig() { step sig_$1 RESULTS_sig_$1.md $PY scripts/significance.py --cluster-field auto --a $2 --b $3 --name-a "$4" --name-b "$5" --out RESULTS_sig_$1.md; }
if [ -z "$CHOSEN" ]; then
  echo "=== no stable BoolQ recipe found -- BoolQ is reported as unstable, no final seeds run ==="
else
  LB=$(cat out/chosen_lr_boolq_pair.txt 2>/dev/null || echo 5e-5)
  for s in 0 1 2 3 4; do
    o=out/boolq-cls-k0-stable-s$s
    step boolq_stable_s$s $o/verdict_config.json $BASE $CHOSEN --seed $s --out $o
    step boolq_stable_s${s}_test RESULTS_boolq_mqstable_s$s.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split test --batch-cases 8 --dump-preds preds_boolq_mqstable_s$s.jsonl --out RESULTS_boolq_mqstable_s$s.md
    sig boolq_stable_s$s preds_boolq_mqstable_s$s.jsonl preds_boolq_pair_lr${LB}_s$s.jsonl "Verdict-MQ cls k=0 (stable recipe)" "pair classifier"
  done
fi
echo "=== BATCH 14 DONE $(date -Is) ==="

#!/bin/bash
# Batch 11 (2026-09-25): BoolQ fallback. The batch-9 stability fix for (cls, k=22) failed (3 of 5 "fixed" seeds still
# stalled) -- a 2-seed stall check was too small a sample to tell a real fix from a config that merely trains slowly.
# Rather than keep hunting hyperparameters for a cell that may be intrinsically hard to train, fall back to (mask, k=4),
# which scored 82.1% and 82.3% on two INDEPENDENT single-seed runs (2026-09-24) with no instability signature seen
# either time. 5 fresh seeds here confirm that before it becomes BoolQ's reported number (MultiRC and RACE keep
# (cls, k=22): both were stable across their own 3 final seeds already run in batch 8).
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
echo "=== batch 11 start $(date -Is) ==="
RAW=answerdotai/ModernBERT-base
BASE="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --lr 3e-5 --val-limit 2000 --init $RAW --tasks boolq --epochs 3 --batch-cases 8 --joint-layers 4 --marker mask"
sig() { step sig_$1 RESULTS_sig_$1.md $PY scripts/significance.py --cluster-field auto --a $2 --b $3 --name-a "$4" --name-b "$5" --out RESULTS_sig_$1.md; }
LB=$(cat out/chosen_lr_boolq_pair.txt 2>/dev/null || echo 5e-5)
for s in 0 1 2 3 4; do
  o=out/boolq-mask-k4-final-s$s
  step boolq_maskk4_s$s $o/verdict_config.json $BASE --seed $s --out $o
  step boolq_maskk4_s${s}_test RESULTS_boolq_mqmaskk4final_s$s.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split test --batch-cases 8 --dump-preds preds_boolq_mqmaskk4final_s$s.jsonl --out RESULTS_boolq_mqmaskk4final_s$s.md
  sig boolq_maskk4final_s$s preds_boolq_mqmaskk4final_s$s.jsonl preds_boolq_pair_lr${LB}_s$s.jsonl "Verdict-MQ mask k=4" "pair classifier"
done
echo "=== BATCH 11 DONE $(date -Is) ==="

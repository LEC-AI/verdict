#!/bin/bash
# Batch 12 (2026-09-25): BoolQ, second fallback. Batch 11 showed (mask, k=4) is ALSO bimodal -- seed 0, identical
# hyperparameters to two runs that scored 82%, just scored 67.6% (a stall), confirming this is GPU non-determinism
# interacting with an unstable loss landscape at k>0 for BoolQ (base model), not a seed- or hyperparameter-fixable
# issue within the configs tried so far. Every repeat of (cls, k=0) or (mask, k=0) instead has shown only moderate
# spread (a few points), never a catastrophic stall -- 5 fresh seeds here confirm that as BoolQ's reported setting.
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
echo "=== batch 12 start $(date -Is) ==="
RAW=answerdotai/ModernBERT-base
BASE="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --lr 3e-5 --val-limit 2000 --init $RAW --tasks boolq --epochs 3 --batch-cases 8 --joint-layers 0 --marker cls"
sig() { step sig_$1 RESULTS_sig_$1.md $PY scripts/significance.py --cluster-field auto --a $2 --b $3 --name-a "$4" --name-b "$5" --out RESULTS_sig_$1.md; }
LB=$(cat out/chosen_lr_boolq_pair.txt 2>/dev/null || echo 5e-5)
for s in 0 1 2 3 4; do
  o=out/boolq-cls-k0-final-s$s
  step boolq_clsk0_s$s $o/verdict_config.json $BASE --seed $s --out $o
  step boolq_clsk0_s${s}_test RESULTS_boolq_mqclsk0final_s$s.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split test --batch-cases 8 --dump-preds preds_boolq_mqclsk0final_s$s.jsonl --out RESULTS_boolq_mqclsk0final_s$s.md
  sig boolq_clsk0final_s$s preds_boolq_mqclsk0final_s$s.jsonl preds_boolq_pair_lr${LB}_s$s.jsonl "Verdict-MQ cls k=0" "pair classifier"
done
echo "=== BATCH 12 DONE $(date -Is) ==="

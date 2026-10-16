#!/bin/bash
# Batch 16 (2026-09-27): phishing-email dataset (Kaggle, naserabdullahalam/phishing-email-dataset, 18,650 emails,
# 80/10/10 hash-based train/val/test split we built ourselves -- not peer-reviewed, an extra practical check).
# Verdict-MQ vs a matched-budget baseline classifier, both trained here; Jev and Laya tested separately (network/local,
# no GPU queue needed). 3 seeds each for a stability check, given the BoolQ lesson (2026-09-25/27).
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching|Generating|return Agent|RuntimeWarning"
GPUJOB="python[0-9.]* (-u )?scripts/(train|train_typed|train_mq|eval_mq|export_laya_encoder|finetune_laya|eval_orgbench|eval_typed|eval_laya_typed|eval_laya_std|significance|pick_recipe|pick_stable|pick_stable2|pick_stable3|pick_split|pick_split2|baseline_mc|baseline_pair|calibration|operating_curve|baseline_plain)\.py"
wait_gpu() { while pgrep -f "$GPUJOB" >/dev/null; do sleep 30; done; }
step() { local name=$1 done=$2; shift 2
  wait_gpu
  if [ -e "$done" ]; then echo "=== [$name] skip ($done exists) ==="; return; fi
  echo "=== [$name] $(date -Is) ==="; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -40; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

ollama stop qwen2.5:7b-instruct 2>/dev/null || true
echo "=== batch 16 start $(date -Is) ==="
TS=tasksource/ModernBERT-base-nli
MQ="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --lr 3e-5 --val-limit 2000 --init $TS --tasks phishing --epochs 3 --batch-cases 8 --joint-layers 0 --marker cls"
sig() { step sig_$1 RESULTS_sig_$1.md $PY scripts/significance.py --cluster-field auto --a $2 --b $3 --name-a "$4" --name-b "$5" --out RESULTS_sig_$1.md; }
for s in 0 1 2; do
  o=out/phishing-mq-s$s
  step phishing_mq_s$s $o/verdict_config.json $MQ --seed $s --out $o
  step phishing_mq_s${s}_test RESULTS_phishing_mq_s$s.md $PY scripts/eval_mq.py --ckpt $o --tasks phishing --task-split test --batch-cases 8 --dump-preds preds_phishing_mq_s$s.jsonl --out RESULTS_phishing_mq_s$s.md
done
for s in 0 1 2; do
  step phishing_base_s$s RESULTS_phishing_base_s$s.md $PY scripts/baseline_pair.py --task phishing --init $TS --epochs 3 --batch-size 16 --lr 3e-5 --seed $s --dump-preds preds_phishing_base_s$s.jsonl --out RESULTS_phishing_base_s$s.md
done
for s in 0 1 2; do
  sig phishing_s$s preds_phishing_mq_s$s.jsonl preds_phishing_base_s$s.jsonl "Verdict-MQ" "baseline classifier"
done
echo "=== BATCH 16 DONE $(date -Is) ==="

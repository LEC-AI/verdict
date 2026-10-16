#!/bin/bash
# BoolQ diagnostic (2026-09-24): split depth k = 22 (state reads the question in every layer) still sits at the majority
# class (dev 61.8, test 62.2), so question-blindness is not the cause of the BoolQ failure. Controlled one-change runs,
# then batch 7 resumes. Diagnostic only; nothing here is used for selection.
set -uo pipefail
cd "$(dirname "$0")/.."
source <(sed -n '/^PY=/,/^ollama stop/p' scripts/run_experiments7.sh | grep -v "^ollama")
TS=tasksource/ModernBERT-base-nli; RAW=answerdotai/ModernBERT-base
MQ="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --lr 3e-5 --val-limit 2000 --tasks boolq --epochs 3 --batch-cases 8 --seed 0 --grad-ckpt"
d() { local n=$1; shift; local o=out/diag-boolq-$n
  step diag_$n $o/verdict_config.json $MQ "$@" --out $o
  step diag_${n}_dev RESULTS_diag_boolq_${n}_dev.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split val --batch-cases 8 --out RESULTS_diag_boolq_${n}_dev.md
  step diag_${n}_test RESULTS_diag_boolq_$n.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split test --batch-cases 8 --out RESULTS_diag_boolq_$n.md; }
echo "=== diag start $(date -Is) ==="
# reference: the pair classifier on the new split (same step as batch 7, so batch 7 will skip it)
step boolq_pair_lr3e-5_s0 RESULTS_boolq_pair_lr3e-5_s0.md $PY scripts/baseline_pair.py --task boolq --init $RAW --epochs 3 --batch-size 16 --lr 3e-5 --seed 0 --eval-dev --dump-preds preds_boolq_pair_lr3e-5_s0.jsonl --out RESULTS_boolq_pair_lr3e-5_s0.md
d k22_ts     --init $TS --joint-layers 22                       # capacity: backbone already knows BoolQ (contaminated)
d k22_nomix  --init $RAW --joint-layers 22 --option-mixer 0     # the random 2-layer option mixer
d k22_lr1e5  --init $RAW --joint-layers 22 --lr 1e-5            # optimisation: lower lr
d k22_e6     --init $RAW --joint-layers 22 --epochs 6           # optimisation: slow start
echo "=== DIAG DONE $(date -Is) ==="
setsid nohup bash scripts/run_experiments7.sh >> logs/experiments7.log 2>&1 < /dev/null &

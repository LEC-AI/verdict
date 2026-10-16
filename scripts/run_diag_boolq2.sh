#!/bin/bash
# BoolQ diagnostic, part 2 (2026-09-24). Part 1: the NLI init, which was TRAINED on BoolQ, still sits at the majority
# class with the state reading the question in every layer (k = 22, dev 61.6). So the backbone knows the answer and the
# readout cannot use it. Test the readout: without the option mixer, and the question-option matching readout.
# Does NOT resume batch 7: the readout decision changes its configuration (see the SPLIT_PLAN.md amendment).
set -uo pipefail
cd "$(dirname "$0")/.."
source <(sed -n '/^PY=/,/^ollama stop/p' scripts/run_experiments7.sh | grep -v "^ollama")
TS=tasksource/ModernBERT-base-nli; RAW=answerdotai/ModernBERT-base
MQ="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --lr 3e-5 --val-limit 2000 --tasks boolq --epochs 3 --batch-cases 8 --seed 0 --grad-ckpt"
d() { local n=$1; shift; local o=out/diag-boolq-$n
  step diag_$n $o/verdict_config.json $MQ "$@" --out $o
  step diag_${n}_dev RESULTS_diag_boolq_${n}_dev.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split val --batch-cases 8 --out RESULTS_diag_boolq_${n}_dev.md
  step diag_${n}_test RESULTS_diag_boolq_$n.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split test --batch-cases 8 --out RESULTS_diag_boolq_$n.md; }
echo "=== diag2 start $(date -Is) ==="
d match_k22_ts   --init $TS  --joint-layers 22 --readout match
d k22_ts_nomix   --init $TS  --joint-layers 22 --option-mixer 0
d match_k22_raw  --init $RAW --joint-layers 22 --readout match
d match_k0_raw   --init $RAW --joint-layers 0  --readout match
echo "=== DIAG2 DONE $(date -Is) ==="

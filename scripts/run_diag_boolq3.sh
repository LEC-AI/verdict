#!/bin/bash
# BoolQ diagnostic, part 3 (2026-09-24): the NEW [OPT] marker token is the suspect (frozen-encoder probe: the answer is
# linearly readable from the passage+question tokens at 0.76 in pair format, 0.61 with [OPT] markers, 0.75-0.79 with
# existing special tokens as markers). Full BoolQ runs, dev + test, marker in {mask, cls}; nothing here selects k.
set -uo pipefail
cd "$(dirname "$0")/.."
source <(sed -n '/^PY=/,/^ollama stop/p' scripts/run_experiments7.sh | grep -v "^ollama")
TS=tasksource/ModernBERT-base-nli; RAW=answerdotai/ModernBERT-base
MQ="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --lr 3e-5 --val-limit 2000 --tasks boolq --epochs 3 --batch-cases 8 --seed 0 --grad-ckpt"
d() { local n=$1; shift; local o=out/diag-boolq-$n
  step diag_$n $o/verdict_config.json $MQ "$@" --out $o
  step diag_${n}_dev RESULTS_diag_boolq_${n}_dev.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split val --batch-cases 8 --out RESULTS_diag_boolq_${n}_dev.md
  step diag_${n}_test RESULTS_diag_boolq_$n.md $PY scripts/eval_mq.py --ckpt $o --tasks boolq --task-split test --batch-cases 8 --out RESULTS_diag_boolq_$n.md; }
echo "=== diag3 start $(date -Is) ==="
d mask_k0_raw   --init $RAW --joint-layers 0  --marker mask
d mask_k22_raw  --init $RAW --joint-layers 22 --marker mask
d cls_k0_raw    --init $RAW --joint-layers 0  --marker cls
d cls_k22_raw   --init $RAW --joint-layers 22 --marker cls
d mask_k4_raw   --init $RAW --joint-layers 4  --marker mask
d mask_k0_ts    --init $TS  --joint-layers 0  --marker mask
echo "=== DIAG3 DONE $(date -Is) ==="

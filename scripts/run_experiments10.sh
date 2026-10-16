#!/bin/bash
# Batch 10 (2026-09-25): the corrected typed-decisions headline. The opt-marker, k=0, warm20 recipe had already scored
# above Laya on all 5 seeds on 2026-09-24 (0.789+-0.007); that result stands on its own.
# This reruns the SAME recipe with the marker fix (cls, k=0 -- the cheap, shared-state setting; k=22 is reserved for
# the reading-comprehension section, not this headline) to get a properly-seeded, non-cherry-picked replacement
# number, since a single-seed sanity check (2026-09-24) already showed 0.783 > Laya's 0.767 at this setting.
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
echo "=== batch 10 start $(date -Is) ==="
LG="$PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3 --marker cls --joint-layers 0"
sig() { step sig_$1 RESULTS_sig_$1.md $PY scripts/significance.py --cluster-field auto --a $2 --b $3 --name-a "$4" --name-b "$5" --out RESULTS_sig_$1.md; }
for sd in 40 41 42 43 44; do
  step stable_cls_s$sd out/stable-cls-s$sd/verdict_config.json $LG --tasks typed_decisions $(cat out/chosen_stable.txt 2>/dev/null) --seed $sd --out out/stable-cls-s$sd
  step stable_cls_s${sd}_eval preds_stable_cls_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/stable-cls-s$sd --typed-split test --kind specialist --dump-preds preds_stable_cls_s$sd.jsonl --out RESULTS_stable_cls_s$sd.md
  sig stable_cls_s$sd preds_stable_cls_s$sd.jsonl preds_laya_td.jsonl "Verdict-MQ-large cls k=0" "Laya-td"
done
echo "=== BATCH 10 DONE $(date -Is) ==="

#!/bin/bash
# Batch 7 (2026-09-24): split-depth Verdict-MQ + re-tuned baselines, exactly as pre-registered in SPLIT_PLAN.md.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching|Generating|return Agent|RuntimeWarning"
GPUJOB="python[0-9.]* (-u )?scripts/(train|train_typed|train_mq|eval_mq|export_laya_encoder|finetune_laya|eval_orgbench|eval_typed|eval_laya_typed|significance|pick_recipe|pick_stable|pick_split|baseline_mc|baseline_pair|calibration|operating_curve|baseline_plain)\.py"
wait_gpu() { while pgrep -f "$GPUJOB" >/dev/null; do sleep 30; done; }
# step NAME DONE_FILE cmd...   (skipped if DONE_FILE exists, so the driver can be relaunched safely)
step() { local name=$1 done=$2; shift 2
  wait_gpu
  if [ -e "$done" ]; then echo "=== [$name] skip ($done exists) ==="; return; fi
  echo "=== [$name] $(date -Is) ==="; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -40; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

ollama stop qwen2.5:7b-instruct 2>/dev/null || true
echo "=== batch 7 start $(date -Is) ==="
TS=tasksource/ModernBERT-base-nli; RAW=answerdotai/ModernBERT-base
MQ="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --lr 3e-5 --val-limit 2000"
declare -A INIT=([boolq]=$RAW [multirc]=$RAW [race]=$TS)
declare -A EXTRA=([boolq]="--epochs 3" [multirc]="--epochs 3" [race]="--epochs 2 --option-dropout 0")

# mq TASK K SEED : train (k >= 8 with gradient checkpointing), then dev and test evaluation
mq() { local t=$1 k=$2 s=$3 o=out/$1-k$2-s$3 ck=""
  [ "$k" -ge 8 ] && ck="--grad-ckpt"
  step ${t}_k${k}_s$s      $o/verdict_config.json $MQ --init ${INIT[$t]} --tasks $t ${EXTRA[$t]} --batch-cases 8 --joint-layers $k --seed $s --out $o $ck
  step ${t}_k${k}_s${s}_dev  RESULTS_${t}_mqk${k}_s${s}_dev.md $PY scripts/eval_mq.py --ckpt $o --tasks $t --task-split val --batch-cases 8 --out RESULTS_${t}_mqk${k}_s${s}_dev.md
  step ${t}_k${k}_s${s}_test RESULTS_${t}_mqk${k}_s$s.md $PY scripts/eval_mq.py --ckpt $o --tasks $t --task-split test --batch-cases 8 --dump-preds preds_${t}_mqk${k}_s$s.jsonl --out RESULTS_${t}_mqk${k}_s$s.md
}
pair() { local t=$1 lr=$2 s=$3
  step ${t}_pair_lr${lr}_s$s RESULTS_${t}_pair_lr${lr}_s$s.md $PY scripts/baseline_pair.py --task $t --init $RAW --epochs 3 --batch-size 16 --lr $lr --seed $s --eval-dev --dump-preds preds_${t}_pair_lr${lr}_s$s.jsonl --out RESULTS_${t}_pair_lr${lr}_s$s.md; }
mc() { local s=$1
  step race_mc_lr3e-5_s$s RESULTS_race_mc_lr3e-5_s$s.md $PY scripts/baseline_mc.py --init $TS --task race --epochs 2 --batch-questions 4 --max-len 1024 --lr 3e-5 --seed $s --eval-dev --dump-preds preds_race_mc_lr3e-5_s$s.jsonl --out RESULTS_race_mc_lr3e-5_s$s.md; }
sig() { step sig_$1 RESULTS_sig_$1.md $PY scripts/significance.py --cluster-field auto --a $2 --b $3 --name-a "$4" --name-b "$5" --out RESULTS_sig_$1.md; }
LRS="1e-5 2e-5 3e-5 5e-5"

# reuse the k = 0 checkpoints trained with these exact settings and splits (SPLIT_PLAN.md)
[ -e out/race-k0-s0 ] || ln -s race-mq-ts out/race-k0-s0
[ -e out/multirc-k0-s0 ] || ln -s multirc-mq-raw out/multirc-k0-s0

# ---- 1. BoolQ sweep (diagnostic first: k = 22 and k = 4)
mq boolq 22 0; mq boolq 4 0
for lr in $LRS; do pair boolq $lr 0; done
for k in 0 2 8; do mq boolq $k 0; done
for k in 0 2 4 8 22; do mq boolq $k 1; done
for lr in $LRS; do pair boolq $lr 1; done
# ---- 2. RACE sweep (NLI-base init)
for k in 0 4 22 2 8; do mq race $k 0; done
# ---- 3. MultiRC sweep
for k in 0 4 22 2 8; do mq multirc $k 0; done
for s in 0 1; do for lr in $LRS; do pair multirc $lr $s; done; done
# ---- 4. pre-registered picks (dev only)
step pick_k out/chosen_k.txt $PY scripts/pick_split.py k --tasks boolq,multirc,race --ks 0,2,4,8,22
for t in boolq multirc; do step pick_lr_$t out/chosen_lr_${t}_pair.txt $PY scripts/pick_split.py lr --task $t --kind pair --lrs 1e-5,2e-5,3e-5,5e-5; done
[ -f out/chosen_k.txt ] || { echo "no k* chosen - stopping"; exit 1; }
K=$(cat out/chosen_k.txt); echo "=== k* = $K ==="
# ---- 5. latency, every k (seed 0): the accuracy-cost curve
for t in boolq multirc race; do for k in 0 2 4 8 22; do
  step lat_${t}_k$k RESULTS_lat_${t}_k$k.md $PY scripts/eval_mq.py --ckpt out/$t-k$k-s0 --latency --latency-task $t --out RESULTS_lat_${t}_k$k.md
done; done
# ---- 6. final seeds at k* and the chosen baseline lr, paired per seed
for s in 0 1 2 3 4; do
  mq boolq $K $s; LB=$(cat out/chosen_lr_boolq_pair.txt); pair boolq $LB $s
  sig boolq_k${K}_s$s preds_boolq_mqk${K}_s$s.jsonl preds_boolq_pair_lr${LB}_s$s.jsonl "Verdict-MQ k=$K" "pair classifier"
done
for s in 0 1 2; do
  mq multirc $K $s; LM=$(cat out/chosen_lr_multirc_pair.txt); pair multirc $LM $s
  sig multirc_k${K}_s$s preds_multirc_mqk${K}_s$s.jsonl preds_multirc_pair_lr${LM}_s$s.jsonl "Verdict-MQ k=$K" "pair classifier"
done
# the existing RACE MC run is lr 3e-5, seed 0 with this exact code path (it only lacks the dev score, which is not used)
for x in preds_race_mc_ts.jsonl:preds_race_mc_lr3e-5_s0.jsonl RESULTS_race_mc_ts.md:RESULTS_race_mc_lr3e-5_s0.md RESULTS_race_mc_ts.json:RESULTS_race_mc_lr3e-5_s0.json; do
  [ -e ${x#*:} ] || cp ${x%%:*} ${x#*:}; done
for s in 0 1 2; do mq race $K $s; done
for s in 0 1 2; do mc $s; sig race_k${K}_s$s preds_race_mqk${K}_s$s.jsonl preds_race_mc_lr3e-5_s$s.jsonl "Verdict-MQ k=$K" "MC head"; done
# ---- 7. typed-decisions, base, k*, no tuning on typed (vs final2-base-s6..8 at k = 0, and vs Laya)
for sd in 6 7 8; do
  step typed_k${K}_s$sd out/typed-k$K-s$sd/verdict_config.json $PY scripts/train_mq.py --init $TS --tasks typed_decisions --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3 $(cat out/chosen_base_recipe.txt) --joint-layers $K --grad-ckpt --seed $sd --out out/typed-k$K-s$sd
  step typed_k${K}_s${sd}_eval preds_typed_k${K}_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/typed-k$K-s$sd --typed-split test --kind specialist --dump-preds preds_typed_k${K}_s$sd.jsonl --out RESULTS_typed_k${K}_s$sd.md
  sig typed_k${K}_vs_k0_s$sd preds_typed_k${K}_s$sd.jsonl preds_final2_base_s$sd.jsonl "Verdict-MQ-base k=$K" "Verdict-MQ-base k=0"
  sig typed_k${K}_vs_laya_s$sd preds_typed_k${K}_s$sd.jsonl preds_laya_td.jsonl "Verdict-MQ-base k=$K" "Laya-td"
done
step lat_typed_k$K RESULTS_lat_typed_k$K.md $PY scripts/eval_mq.py --ckpt out/typed-k$K-s6 --latency --out RESULTS_lat_typed_k$K.md
echo "=== BATCH 7 DONE $(date -Is) ==="

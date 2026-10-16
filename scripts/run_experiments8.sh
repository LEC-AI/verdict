#!/bin/bash
# Batch 8 (2026-09-24): marker x depth joint sweep, per SPLIT_PLAN.md's amendment. The [OPT] marker token was found to
# be the primary cause of the BoolQ/RACE/MultiRC losses (frozen-encoder probe); this replaces the [OPT]
# cells of batch 7 rather than resuming it. All dev-only until the pick step; nothing here is used for selection
# except through scripts/pick_split2.py.
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching|Generating|return Agent|RuntimeWarning"
GPUJOB="python[0-9.]* (-u )?scripts/(train|train_typed|train_mq|eval_mq|export_laya_encoder|finetune_laya|eval_orgbench|eval_typed|eval_laya_typed|significance|pick_recipe|pick_stable|pick_split|pick_split2|baseline_mc|baseline_pair|calibration|operating_curve|baseline_plain)\.py"
wait_gpu() { while pgrep -f "$GPUJOB" >/dev/null; do sleep 30; done; }
step() { local name=$1 done=$2; shift 2
  wait_gpu
  if [ -e "$done" ]; then echo "=== [$name] skip ($done exists) ==="; return; fi
  echo "=== [$name] $(date -Is) ==="; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -40; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

ollama stop qwen2.5:7b-instruct 2>/dev/null || true
echo "=== batch 8 start $(date -Is) ==="
TS=tasksource/ModernBERT-base-nli; RAW=answerdotai/ModernBERT-base
declare -A INIT=([boolq]=$RAW [multirc]=$RAW [race]=$TS)
declare -A EXTRA=([boolq]="--epochs 3" [multirc]="--epochs 3" [race]="--epochs 2 --option-dropout 0")

# mq TASK MARKER K SEED : train (grad-ckpt at k >= 8), then dev and test evaluation
mq() { local t=$1 mk=$2 k=$3 s=$4; local o=out/$1-$2-k$3-s$4; local ck=""
  # MultiRC packs up to ~14 questions/case, so split-depth (k>0) duplicates the shared state that many times and OOMs
  # on the 16GB laptop GPU without checkpointing (observed 2026-09-24: multirc_mask_k4_s0 OOM'd at batch-cases 8).
  # BoolQ/RACE have far fewer questions/case and trained fine at k up to 22 without it, so only widen it for multirc.
  { [ "$k" -ge 8 ] || { [ "$t" = "multirc" ] && [ "$k" -gt 0 ]; }; } && ck="--grad-ckpt"
  step ${t}_${mk}_k${k}_s$s      $o/verdict_config.json $PY scripts/train_mq.py --soft --bf16 --max-len 2048 --option-mixer 2 --lr 3e-5 --val-limit 2000 --init ${INIT[$t]} --tasks $t ${EXTRA[$t]} --batch-cases 8 --joint-layers $k --marker $mk --seed $s --out $o $ck
  step ${t}_${mk}_k${k}_s${s}_dev  RESULTS_${t}_mq${mk}k${k}_s${s}_dev.md $PY scripts/eval_mq.py --ckpt $o --tasks $t --task-split val --batch-cases 8 --out RESULTS_${t}_mq${mk}k${k}_s${s}_dev.md
  step ${t}_${mk}_k${k}_s${s}_test RESULTS_${t}_mq${mk}k${k}_s$s.md $PY scripts/eval_mq.py --ckpt $o --tasks $t --task-split test --batch-cases 8 --dump-preds preds_${t}_mq${mk}k${k}_s$s.jsonl --out RESULTS_${t}_mq${mk}k${k}_s$s.md
}
pair() { local t=$1 lr=$2 s=$3
  step ${t}_pair_lr${lr}_s$s RESULTS_${t}_pair_lr${lr}_s$s.md $PY scripts/baseline_pair.py --task $t --init $RAW --epochs 3 --batch-size 16 --lr $lr --seed $s --eval-dev --dump-preds preds_${t}_pair_lr${lr}_s$s.jsonl --out RESULTS_${t}_pair_lr${lr}_s$s.md; }
mc() { local s=$1
  step race_mc_lr3e-5_s$s RESULTS_race_mc_lr3e-5_s$s.md $PY scripts/baseline_mc.py --init $TS --task race --epochs 2 --batch-questions 4 --max-len 1024 --lr 3e-5 --seed $s --eval-dev --dump-preds preds_race_mc_lr3e-5_s$s.jsonl --out RESULTS_race_mc_lr3e-5_s$s.md; }
sig() { step sig_$1 RESULTS_sig_$1.md $PY scripts/significance.py --cluster-field auto --a $2 --b $3 --name-a "$4" --name-b "$5" --out RESULTS_sig_$1.md; }
LRS="1e-5 2e-5 3e-5 5e-5"

# ---- 1. complete the BoolQ grid (mask/cls x 0/4/22): only cls@k4 is missing (rest done in the 2026-09-24 diagnostics,
#         re-run here under the standard naming so pick_split2.py finds them the same way)
for mk in mask cls; do for k in 0 4 22; do mq boolq $mk $k 0; done; done
# ---- 2. MultiRC grid
for mk in mask cls; do for k in 0 4 22; do mq multirc $mk $k 0; done; done
# ---- 3. RACE grid
for mk in mask cls; do for k in 0 4 22; do mq race $mk $k 0; done; done
# ---- 4. baseline lr sweeps (unchanged from batch 7's plan; safe to redo idempotently)
for s in 0 1; do for lr in $LRS; do pair boolq $lr $s; pair multirc $lr $s; done; done

# ---- 5. pre-registered joint pick (dev only)
step pick_mk out/chosen_marker_k.txt $PY scripts/pick_split2.py --tasks boolq,multirc,race --markers mask,cls --ks 0,4,22
for t in boolq multirc; do step pick_lr_$t out/chosen_lr_${t}_pair.txt $PY scripts/pick_split.py lr --task $t --kind pair --lrs 1e-5,2e-5,3e-5,5e-5; done
[ -f out/chosen_marker_k.txt ] || { echo "no (marker*, k*) chosen - stopping"; exit 1; }
read -r MK K < out/chosen_marker_k.txt; echo "=== marker* = $MK, k* = $K ==="

# ---- 6. latency, every grid cell (seed 0): the accuracy-cost surface
for t in boolq multirc race; do for mk in mask cls; do for k in 0 4 22; do
  step lat_${t}_${mk}_k$k RESULTS_lat_${t}_${mk}_k$k.md $PY scripts/eval_mq.py --ckpt out/$t-$mk-k$k-s0 --latency --latency-task $t --out RESULTS_lat_${t}_${mk}_k$k.md
done; done; done

# ---- 7. final seeds at (marker*, k*) and the chosen baseline lr, paired per seed
for s in 0 1 2 3 4; do
  mq boolq $MK $K $s; LB=$(cat out/chosen_lr_boolq_pair.txt); pair boolq $LB $s
  sig boolq_${MK}k${K}_s$s preds_boolq_mq${MK}k${K}_s$s.jsonl preds_boolq_pair_lr${LB}_s$s.jsonl "Verdict-MQ $MK k=$K" "pair classifier"
done
for s in 0 1 2; do
  mq multirc $MK $K $s; LM=$(cat out/chosen_lr_multirc_pair.txt); pair multirc $LM $s
  sig multirc_${MK}k${K}_s$s preds_multirc_mq${MK}k${K}_s$s.jsonl preds_multirc_pair_lr${LM}_s$s.jsonl "Verdict-MQ $MK k=$K" "pair classifier"
done
for x in preds_race_mc_ts.jsonl:preds_race_mc_lr3e-5_s0.jsonl RESULTS_race_mc_ts.md:RESULTS_race_mc_lr3e-5_s0.md RESULTS_race_mc_ts.json:RESULTS_race_mc_lr3e-5_s0.json; do
  [ -e ${x#*:} ] || cp ${x%%:*} ${x#*:}; done
for s in 0 1 2; do mq race $MK $K $s; done
for s in 0 1 2; do mc $s; sig race_${MK}k${K}_s$s preds_race_mq${MK}k${K}_s$s.jsonl preds_race_mc_lr3e-5_s$s.jsonl "Verdict-MQ $MK k=$K" "MC head"; done

# ---- 8. typed-decisions, base model, (marker*, k*), no tuning on typed: vs opt-marker k=0 (final2-base-s6..8) and Laya
for sd in 6 7 8; do
  step typed_${MK}k${K}_s$sd out/typed-$MK-k$K-s$sd/verdict_config.json $PY scripts/train_mq.py --init $TS --tasks typed_decisions --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3 $(cat out/chosen_base_recipe.txt) --joint-layers $K --marker $MK --grad-ckpt --seed $sd --out out/typed-$MK-k$K-s$sd
  step typed_${MK}k${K}_s${sd}_eval preds_typed_${MK}k${K}_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/typed-$MK-k$K-s$sd --typed-split test --kind specialist --dump-preds preds_typed_${MK}k${K}_s$sd.jsonl --out RESULTS_typed_${MK}k${K}_s$sd.md
  sig typed_${MK}k${K}_vs_optk0_s$sd preds_typed_${MK}k${K}_s$sd.jsonl preds_final2_base_s$sd.jsonl "Verdict-MQ-base $MK k=$K" "Verdict-MQ-base opt k=0"
  sig typed_${MK}k${K}_vs_laya_s$sd preds_typed_${MK}k${K}_s$sd.jsonl preds_laya_td.jsonl "Verdict-MQ-base $MK k=$K" "Laya-td"
done
step lat_typed_${MK}k$K RESULTS_lat_typed_${MK}k$K.md $PY scripts/eval_mq.py --ckpt out/typed-$MK-k$K-s6 --latency --out RESULTS_lat_typed_${MK}k$K.md

# ---- 9. IF base did not regress against the opt-marker k=0 base (mean acc across s6-8 >= final2-base mean - 0.5pt),
#         redo the large-model stable seeds (the paper's headline) at (marker*, k*). Gate checked from the .json files
#         (not test-peeking: it's the same benchmark the base model was already allowed to use for this go/no-go).
$PY - "$MK" "$K" <<'PYEOF'
import json, sys, glob
mk, k = sys.argv[1], sys.argv[2]
new = [json.load(open(f))["typed"]["acc"] for f in sorted(glob.glob(f"RESULTS_typed_{mk}k{k}_s*.json"))]
old = [json.load(open(f))["typed"]["acc"] for f in sorted(glob.glob("RESULTS_final2_base_s*.json"))]
ok = new and old and (sum(new) / len(new)) >= (sum(old) / len(old)) - 0.005
open("out/typed_base_gate.txt", "w").write(f"{'GO' if ok else 'STOP'} new={new} old={old}\n")
print(f"gate: {'GO' if ok else 'STOP'} new mean {sum(new)/len(new) if new else None} old mean {sum(old)/len(old) if old else None}")
PYEOF
if grep -q '^GO' out/typed_base_gate.txt 2>/dev/null; then
  for sd in 30 31 32 33 34; do
    step stable_${MK}k${K}_s$sd out/stable-$MK-k$K-s$sd/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3 --tasks typed_decisions $(cat out/chosen_stable.txt 2>/dev/null) --joint-layers $K --marker $MK --grad-ckpt --seed $sd --out out/stable-$MK-k$K-s$sd
    step stable_${MK}k${K}_s${sd}_eval preds_stable_${MK}k${K}_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/stable-$MK-k$K-s$sd --typed-split test --kind specialist --dump-preds preds_stable_${MK}k${K}_s$sd.jsonl --out RESULTS_stable_${MK}k${K}_s$sd.md
    sig stable_${MK}k${K}_s$sd preds_stable_${MK}k${K}_s$sd.jsonl preds_laya_td.jsonl "Verdict-MQ-large $MK k=$K" "Laya-td"
  done
else
  echo "=== typed base gate said STOP: NOT rerunning the large-model stable seeds; base regressed vs the opt-marker k=0 headline ==="
fi
echo "=== BATCH 8 DONE $(date -Is) ==="

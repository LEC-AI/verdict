#!/bin/bash
# Batch 6 (replaces the rest of batch 5 after the typed-decisions card review, 2026-09-23).
# Two tracks, labelled as the card requires:
#   SPECIALIST (trained on the 4 benchmark workflows): compared with the card's ModernBERT-base 0.646 and its ceilings .704/.735
#   GENERALIST (never sees the benchmark workflows, zero-shot): vs Jev 0.727 / Decider 1 0.768
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
P3="route_topic,signal_positive,affect"
ORG="email_needs_reply,email_escalate,email_priority"
OC="data/jsonl_orgcons"
MIXG="route_topic,affect,topic_dbpedia,topic_yahoo,question_type,irony,hate"
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching|Generating|return Agent|RuntimeWarning"
GPUJOB="python[0-9.]* (-u )?scripts/(train|train_typed|train_mq|eval_mq|export_laya_encoder|finetune_laya|eval_orgbench|eval_typed|eval_laya_typed|significance|pick_recipe|pick_stable|baseline_mc|baseline_pair|calibration|operating_curve|baseline_plain)\.py"
wait_gpu() { while pgrep -f "$GPUJOB" >/dev/null; do sleep 30; done; }
# step NAME DONE_FILE cmd...   (skipped if DONE_FILE exists, so the driver can be relaunched safely)
step() { local name=$1 done=$2; shift 2
  wait_gpu      # FIRST wait for any running GPU job (e.g. an orphan of a previous driver), THEN check done
  if [ -e "$done" ]; then echo "=== [$name] skip ($done exists) ==="; return; fi
  echo "=== [$name] $(date -Is) ==="; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -40; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

ollama stop qwen2.5:7b-instruct 2>/dev/null || true
echo "=== batch 6 start $(date -Is) ==="

# SPECIALIST: typed-decisions, descriptions + soft labels (base), card metrics + permutation
step typed_base_desc out/verdict-typed-desc/verdict_config.json $PY scripts/train_typed.py --soft --select last --epochs 6 --batch-size 16 --bf16 --out out/verdict-typed-desc --out-md RESULTS_typed_desc.md
step typed_base_desc_eval RESULTS_typed_desc_eval.md $PY scripts/eval_typed.py --ckpt out/verdict-typed-desc --permute-options --out RESULTS_typed_desc_eval.md
# Laya measured by us, native protocol, card metrics
step laya_typed_td RESULTS_laya_typed_td.md $PY scripts/eval_laya_typed.py --subfolder typed-decisions --out RESULTS_laya_typed_td.md
step laya_typed_def RESULTS_laya_typed_default.md $PY scripts/eval_laya_typed.py --subfolder default --out RESULTS_laya_typed_default.md

# ARCHITECTURE: Verdict-MQ (encode once, decide many) vs the per-question cross-encoder, same data/epochs
step mq_typed      out/mq-typed/verdict_config.json $PY scripts/train_mq.py --tasks typed_decisions --out out/mq-typed --epochs 6 --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3
step mq_typed_eval RESULTS_mq_typed.md $PY scripts/eval_mq.py --ckpt out/mq-typed --typed-split test --latency --kind specialist --dump-preds preds_mq_typed.jsonl --out RESULTS_mq_typed.md

# EVIDENCE CHECK before scaling the synthetic corpus: does the pilot corpus help?
#  (1) generalist: MQ trained ONLY on the pilot corpus, zero-shot on typed-decisions TRAIN (dev; never trained on)
#  (2) pre-training effect: that model fine-tuned on typed-decisions vs MQ from raw ModernBERT (mq_typed)
SP="synth@data/synth_pilot"
step mq_syn          out/mq-syn/verdict_config.json $PY scripts/train_mq.py --tasks $SP --out out/mq-syn --epochs 3 --batch-cases 8 --soft --bf16 --max-len 2048
step mq_syn_dev      RESULTS_mq_syn_dev.md $PY scripts/eval_mq.py --ckpt out/mq-syn --typed-split train --kind generalist --out RESULTS_mq_syn_dev.md
step mq_syn_typed    out/mq-syn-typed/verdict_config.json $PY scripts/train_mq.py --init out/mq-syn --tasks typed_decisions --out out/mq-syn-typed --epochs 6 --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3
step mq_syn_typed_eval RESULTS_mq_syn_typed.md $PY scripts/eval_mq.py --ckpt out/mq-syn-typed --typed-split test --kind specialist --dump-preds preds_mq_syn_typed.jsonl --out RESULTS_mq_syn_typed.md
# control for (1): same MQ on public single-question data only (no synthetic corpus)
step mq_pub          out/mq-pub/verdict_config.json $PY scripts/train_mq.py --tasks route_topic,affect,topic_dbpedia,topic_yahoo,question_type,irony,hate --cache-dir data/jsonl_mix --limit 3000 --out out/mq-pub --epochs 2 --batch-cases 16 --soft --bf16 --max-len 1024
step mq_pub_dev      RESULTS_mq_pub_dev.md $PY scripts/eval_mq.py --ckpt out/mq-pub --typed-split train --kind generalist --out RESULTS_mq_pub_dev.md

# GENERALIST LEVER (free, pilot data): start from a zero-shot NLI ModernBERT (tasksource, Apache-2.0,
# trained on hundreds of tasks) instead of raw ModernBERT. Dev = typed-decisions TRAIN split.
step mq_nli_syn       out/mq-nli-syn/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks $SP --out out/mq-nli-syn --epochs 3 --batch-cases 8 --soft --bf16 --max-len 2048
step mq_nli_syn_dev   RESULTS_mq_nli_syn_dev.md $PY scripts/eval_mq.py --ckpt out/mq-nli-syn --typed-split train --kind generalist --out RESULTS_mq_nli_syn_dev.md
step mq_nlil_syn      out/mq-nlil-syn/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks $SP --out out/mq-nlil-syn --epochs 3 --batch-cases 4 --lr 2e-5 --soft --bf16 --max-len 2048
step mq_nlil_syn_dev  RESULTS_mq_nlil_syn_dev.md $PY scripts/eval_mq.py --ckpt out/mq-nlil-syn --typed-split train --kind generalist --out RESULTS_mq_nlil_syn_dev.md
step mq_nli_typed     out/mq-nli-typed/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks typed_decisions --out out/mq-nli-typed --epochs 6 --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3
step mq_nli_typed_eval RESULTS_mq_nli_typed.md $PY scripts/eval_mq.py --ckpt out/mq-nli-typed --typed-split test --kind specialist --out RESULTS_mq_nli_typed.md

# SPECIALIST COMPARISON with the Laya typed-decisions checkpoint (0.767): scale, and the SAME start as Laya
step laya_encoder   out/laya-encoder/config.json $PY scripts/export_laya_encoder.py --subfolder default --out out/laya-encoder
# best recipe so far: NLI-initialized MQ specialist (0.763 seed 0) -> seeds + large NLI init
step mq_nli_typed_s1      out/mq-nli-typed-s1/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks typed_decisions --out out/mq-nli-typed-s1 --epochs 6 --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3 --seed 1
step mq_nli_typed_s1_eval RESULTS_mq_nli_typed_s1.md $PY scripts/eval_mq.py --ckpt out/mq-nli-typed-s1 --typed-split test --kind specialist --out RESULTS_mq_nli_typed_s1.md
step mq_nli_typed_s2      out/mq-nli-typed-s2/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks typed_decisions --out out/mq-nli-typed-s2 --epochs 6 --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3 --seed 2
step mq_nli_typed_s2_eval RESULTS_mq_nli_typed_s2.md $PY scripts/eval_mq.py --ckpt out/mq-nli-typed-s2 --typed-split test --kind specialist --out RESULTS_mq_nli_typed_s2.md
step mq_nlil_typed        out/mq-nlil-typed/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_decisions --out out/mq-nlil-typed --epochs 6 --batch-cases 4 --lr 2e-5 --soft --bf16 --max-len 2048 --option-dropout 0.3
step mq_nlil_typed_eval   RESULTS_mq_nlil_typed.md $PY scripts/eval_mq.py --ckpt out/mq-nlil-typed --typed-split test --kind specialist --latency --dump-preds preds_mq_nlil_typed.jsonl --out RESULTS_mq_nlil_typed.md
# paired significance vs Laya on identical decisions (McNemar + bootstrap + Holm over the 20 questions)
step laya_td_dump   preds_laya_td.jsonl $PY scripts/eval_laya_typed.py --subfolder typed-decisions --dump-preds preds_laya_td.jsonl --out RESULTS_laya_typed_td.md
for sd in "" "-s1" "-s2"; do
  step mq_nli_dump$sd preds_mq_nli_typed$sd.jsonl $PY scripts/eval_mq.py --ckpt out/mq-nli-typed$sd --typed-split test --kind specialist --dump-preds preds_mq_nli_typed$sd.jsonl --out RESULTS_mq_nli_typed$sd.md
  step sig_nli$sd RESULTS_sig_mqnli$sd.md $PY scripts/significance.py --cluster-field auto --a preds_mq_nli_typed$sd.jsonl --b preds_laya_td.jsonl --name-a Verdict-MQ$sd --name-b Laya-td --out RESULTS_sig_mqnli$sd.md
done
# large NLI init = best so far (0.789 seed 0): seeds 1-2 + paired significance vs Laya
for sd in 1 2; do
  step mq_nlil_typed_s$sd out/mq-nlil-typed-s$sd/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_decisions --out out/mq-nlil-typed-s$sd --epochs 6 --batch-cases 4 --lr 2e-5 --soft --bf16 --max-len 2048 --option-dropout 0.3 --seed $sd
  step mq_nlil_typed_s${sd}_eval preds_mq_nlil_typed_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/mq-nlil-typed-s$sd --typed-split test --kind specialist --dump-preds preds_mq_nlil_typed_s$sd.jsonl --out RESULTS_mq_nlil_typed_s$sd.md
done
for sd in "" "_s1" "_s2"; do
  step sig_nlil$sd RESULTS_sig_mqnlil$sd.md $PY scripts/significance.py --cluster-field auto --a preds_mq_nlil_typed$sd.jsonl --b preds_laya_td.jsonl --name-a Verdict-MQ-large$sd --name-b Laya-td --out RESULTS_sig_mqnlil$sd.md
done
# LARGE-MODEL RECIPE TUNING on the DEV split (large NLI init was unstable: 0.789 / 0.707 / 0.658 over seeds)
NLIL="$PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_dev --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3"
for cfg in "lr2e5e6:--lr 2e-5 --epochs 6" "lr1e5e6:--lr 1e-5 --epochs 6" "lr1e5e10:--lr 1e-5 --epochs 10" "lr5e6e10:--lr 5e-6 --epochs 10"; do
  c=${cfg%%:*}; f=${cfg#*:}
  for sd in 0 1; do
    step dev_${c}_s$sd out/dev-$c-s$sd/verdict_config.json $NLIL --out out/dev-$c-s$sd $f --seed $sd
    step dev_${c}_s${sd}_eval RESULTS_dev_${c}_s$sd.md $PY scripts/eval_mq.py --ckpt out/dev-$c-s$sd --typed-split dev --kind specialist --out RESULTS_dev_${c}_s$sd.md
    rm -rf out/dev-$c-s$sd/model.safetensors 2>/dev/null   # keep disk small; config stays as the done-marker
  done
done
step pick_recipe out/chosen_large_recipe.txt $PY scripts/pick_recipe.py --configs lr2e5e6,lr1e5e6,lr1e5e10,lr5e6e10
# FINAL large specialist. Primary = the dev-chosen recipe (out/chosen_large_recipe.txt). Seeds 0-2 of that exact
# recipe already exist (mq-nlil-typed*: 0.789/0.707/0.658; seeds 1-2 stalled early, visible in TRAINING loss), so
# the final runs use FRESH seeds 3-5 and the paper reports all six. Stability arm (labelled, not selected on test):
# lr 1e-5, the standard remedy for early-training stalls, dev 0.788 (within noise of the chosen recipe).
LARGE="$PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_decisions --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3"
for arm in "chosen:$(cat out/chosen_large_recipe.txt 2>/dev/null)" "lr1e5:--lr 1e-5 --epochs 6"; do
  an=${arm%%:*}; af=${arm#*:}
  for sd in 3 4 5; do
    step final_${an}_s$sd out/final-$an-s$sd/verdict_config.json $LARGE $af --seed $sd --out out/final-$an-s$sd
    step final_${an}_s${sd}_eval preds_final_${an}_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/final-$an-s$sd --typed-split test --kind specialist --dump-preds preds_final_${an}_s$sd.jsonl --out RESULTS_final_${an}_s$sd.md
    step sig_final_${an}_s$sd RESULTS_sig_final_${an}_s$sd.md $PY scripts/significance.py --cluster-field auto --a preds_final_${an}_s$sd.jsonl --b preds_laya_td.jsonl --name-a Verdict-MQ-large-$an-s$sd --name-b Laya-td --out RESULTS_sig_final_${an}_s$sd.md
  done
done
step mq_large_typed out/mq-large-typed/verdict_config.json $PY scripts/train_mq.py --init answerdotai/ModernBERT-large --tasks typed_decisions --out out/mq-large-typed --epochs 6 --batch-cases 4 --lr 2e-5 --soft --bf16 --max-len 2048 --option-dropout 0.3
step mq_large_typed_eval RESULTS_mq_large_typed.md $PY scripts/eval_mq.py --ckpt out/mq-large-typed --typed-split test --kind specialist --latency --out RESULTS_mq_large_typed.md
step mq_laya_typed  out/mq-laya-typed/verdict_config.json $PY scripts/train_mq.py --init out/laya-encoder --tasks typed_decisions --out out/mq-laya-typed --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3 $(cat out/chosen_large_recipe.txt 2>/dev/null)
step mq_laya_typed_eval RESULTS_mq_laya_typed.md $PY scripts/eval_mq.py --ckpt out/mq-laya-typed --typed-split test --kind specialist --dump-preds preds_mq_laya_typed.jsonl --out RESULTS_mq_laya_typed.md
step laya_ft_typed  RESULTS_laya_ft_typed.md $PY scripts/finetune_laya.py --tasks typed_decisions --epochs 3 --batch-size 4 --eval-batch-size 16 --lr 1e-5 --out RESULTS_laya_ft_typed.md

# ATTRIBUTION: which MQ component earns the gain over the cross-encoder? (one change each) + seeds
MQT="$PY scripts/train_mq.py --tasks typed_decisions --epochs 6 --batch-cases 8 --soft --bf16"
for spec in "s1:--max-len 2048 --option-dropout 0.3 --seed 1" "s2:--max-len 2048 --option-dropout 0.3 --seed 2" \
            "notype:--max-len 2048 --option-dropout 0.3 --no-type-emb" "ordered:--max-len 2048 --option-dropout 0.3 --ordered-options" \
            "noord:--max-len 2048 --option-dropout 0.3 --ordinal 0" "nodrop:--max-len 2048 --option-dropout 0" \
            "len512:--max-len 512 --option-dropout 0.3" "const:--max-len 2048 --option-dropout 0.3 --schedule constant --lr 2e-5"; do
  n=${spec%%:*}; f=${spec#*:}
  step mq_typed_$n out/mq-typed-$n/verdict_config.json $MQT --out out/mq-typed-$n $f
  step mq_typed_${n}_eval RESULTS_mq_typed_$n.md $PY scripts/eval_mq.py --ckpt out/mq-typed-$n --typed-split test --kind specialist --out RESULTS_mq_typed_$n.md
done

# Laya vs Verdict on PUBLIC3 (zero-shot + fine-tuned)
step laya_ft_public3 RESULTS_laya_ft_public3.md $PY scripts/finetune_laya.py --tasks $P3 --epochs 3 --batch-size 8 --out RESULTS_laya_ft_public3.md --dump-preds preds_laya_ft_public3.jsonl

# SCHEDULE CHECK ON DEV (ablation on test: constant lr 2e-5 gave 0.733 vs 0.681 +- 0.013 for linear 3e-5; a test
# observation must not pick the recipe, so the choice is re-made on the DEV split, then fresh test seeds).
BASE="$PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks typed_dev --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3"
for cfg in "lin3e5e6:--lr 3e-5 --epochs 6" "const2e5e6:--lr 2e-5 --epochs 6 --schedule constant" "const1e5e6:--lr 1e-5 --epochs 6 --schedule constant"; do
  c=${cfg%%:*}; f=${cfg#*:}
  for sd in 0 1; do
    step devb_${c}_s$sd out/devb-$c-s$sd/verdict_config.json $BASE --out out/devb-$c-s$sd $f --seed $sd
    step devb_${c}_s${sd}_eval RESULTS_devb_${c}_s$sd.md $PY scripts/eval_mq.py --ckpt out/devb-$c-s$sd --typed-split dev --kind specialist --out RESULTS_devb_${c}_s$sd.md
    rm -f out/devb-$c-s$sd/model.safetensors
  done
done
step pick_base out/chosen_base_recipe.txt $PY scripts/pick_recipe.py --prefix RESULTS_devb_ --configs lin3e5e6,const2e5e6,const1e5e6 --out out/chosen_base_recipe.txt --report RESULTS_recipe_dev_base.md
NLIL2="$PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_dev --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3"
for cfg in "const2e5e6:--lr 2e-5 --epochs 6 --schedule constant" "const1e5e6:--lr 1e-5 --epochs 6 --schedule constant"; do
  c=${cfg%%:*}; f=${cfg#*:}
  for sd in 0 1; do
    step dev_${c}_s$sd out/dev-$c-s$sd/verdict_config.json $NLIL2 --out out/dev-$c-s$sd $f --seed $sd
    step dev_${c}_s${sd}_eval RESULTS_dev_${c}_s$sd.md $PY scripts/eval_mq.py --ckpt out/dev-$c-s$sd --typed-split dev --kind specialist --out RESULTS_dev_${c}_s$sd.md
    rm -f out/dev-$c-s$sd/model.safetensors
  done
done
step pick_large2 out/chosen_large_recipe2.txt $PY scripts/pick_recipe.py --configs lr2e5e6,lr1e5e6,lr1e5e10,lr5e6e10,const2e5e6,const1e5e6 --out out/chosen_large_recipe2.txt --report RESULTS_recipe_dev_large2.md
# fresh TEST seeds for the dev-chosen recipes (seeds 6-8, never used before)
for sd in 6 7 8; do
  step final2_base_s$sd out/final2-base-s$sd/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks typed_decisions --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3 $(cat out/chosen_base_recipe.txt 2>/dev/null) --seed $sd --out out/final2-base-s$sd
  step final2_base_s${sd}_eval preds_final2_base_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/final2-base-s$sd --typed-split test --kind specialist --dump-preds preds_final2_base_s$sd.jsonl --out RESULTS_final2_base_s$sd.md
  step sig_final2_base_s$sd RESULTS_sig_final2_base_s$sd.md $PY scripts/significance.py --cluster-field auto --a preds_final2_base_s$sd.jsonl --b preds_laya_td.jsonl --name-a Verdict-MQ-base-s$sd --name-b Laya-td --out RESULTS_sig_final2_base_s$sd.md
  if grep -q constant out/chosen_large_recipe2.txt 2>/dev/null; then
    step final2_large_s$sd out/final2-large-s$sd/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_decisions --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3 $(cat out/chosen_large_recipe2.txt) --seed $sd --out out/final2-large-s$sd
    step final2_large_s${sd}_eval preds_final2_large_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/final2-large-s$sd --typed-split test --kind specialist --dump-preds preds_final2_large_s$sd.jsonl --out RESULTS_final2_large_s$sd.md
    step sig_final2_large_s$sd RESULTS_sig_final2_large_s$sd.md $PY scripts/significance.py --cluster-field auto --a preds_final2_large_s$sd.jsonl --b preds_laya_td.jsonl --name-a Verdict-MQ-large-s$sd --name-b Laya-td --out RESULTS_sig_final2_large_s$sd.md
  fi
done

# ARCHITECTURE: permutation-equivariant OPTION MIXER over option markers (set attention, no positions), so options can
# be compared while order invariance is kept. Gate on DEV (base), then fresh TEST seeds + matched-init vs Laya's arch.
MB="$PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks typed_dev --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3 --lr 3e-5 --epochs 6"
for m in 1 2; do for sd in 0 1; do
  step devm_mix${m}_s$sd out/devm-mix$m-s$sd/verdict_config.json $MB --option-mixer $m --out out/devm-mix$m-s$sd --seed $sd
  step devm_mix${m}_s${sd}_eval RESULTS_devm_mix${m}_s$sd.md $PY scripts/eval_mq.py --ckpt out/devm-mix$m-s$sd --typed-split dev --kind specialist --out RESULTS_devm_mix${m}_s$sd.md
  rm -f out/devm-mix$m-s$sd/model.safetensors
done; done
for sd in 0 1; do cp -n RESULTS_devb_lin3e5e6_s$sd.json RESULTS_devm_mix0_s$sd.json 2>/dev/null; done   # mixer 0 = same recipe, already run
step pick_mixer out/chosen_mixer.txt $PY scripts/pick_recipe.py --prefix RESULTS_devm_ --configs mix0,mix1,mix2 --out out/chosen_mixer.txt --report RESULTS_mixer_dev.md
if [ -s out/chosen_mixer.txt ] && grep -q option-mixer out/chosen_mixer.txt; then
  MX=$(cat out/chosen_mixer.txt)
  for sd in 9 10 11; do
    step mix_base_s$sd out/mix-base-s$sd/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks typed_decisions --batch-cases 8 --soft --bf16 --max-len 2048 --option-dropout 0.3 --lr 3e-5 --epochs 6 $MX --seed $sd --out out/mix-base-s$sd
    step mix_base_s${sd}_eval preds_mix_base_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/mix-base-s$sd --typed-split test --kind specialist --dump-preds preds_mix_base_s$sd.jsonl --out RESULTS_mix_base_s$sd.md
    step sig_mix_base_s$sd RESULTS_sig_mix_base_s$sd.md $PY scripts/significance.py --cluster-field auto --a preds_mix_base_s$sd.jsonl --b preds_laya_td.jsonl --name-a Verdict-MQ-mix-base-s$sd --name-b Laya-td --out RESULTS_sig_mix_base_s$sd.md
  done
  # matched init (Laya's own encoder): MQ+mixer vs Laya's architecture, 2 seeds each
  for sd in 0 1; do
    step mix_laya_s$sd out/mix-laya-s$sd/verdict_config.json $PY scripts/train_mq.py --init out/laya-encoder --tasks typed_decisions --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3 --lr 2e-5 --epochs 6 $MX --seed $sd --out out/mix-laya-s$sd
    step mix_laya_s${sd}_eval preds_mix_laya_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/mix-laya-s$sd --typed-split test --kind specialist --dump-preds preds_mix_laya_s$sd.jsonl --out RESULTS_mix_laya_s$sd.md
  done
  step laya_ft_typed_s1 RESULTS_laya_ft_typed_s1.md $PY scripts/finetune_laya.py --tasks typed_decisions --epochs 3 --batch-size 4 --eval-batch-size 16 --lr 1e-5 --seed 1 --out RESULTS_laya_ft_typed_s1.md
  step mq_laya_typed_s1 out/mq-laya-typed-s1/verdict_config.json $PY scripts/train_mq.py --init out/laya-encoder --tasks typed_decisions --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3 --lr 2e-5 --epochs 6 --seed 1 --out out/mq-laya-typed-s1
  step mq_laya_typed_s1_eval RESULTS_mq_laya_typed_s1.md $PY scripts/eval_mq.py --ckpt out/mq-laya-typed-s1 --typed-split test --kind specialist --out RESULTS_mq_laya_typed_s1.md
  # large + mixer: dev gate (vs lr2e5e6 = 0.798), then fresh test seeds
  for sd in 0 1; do
    step devl_mix_s$sd out/devl-mix-s$sd/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_dev --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3 --lr 2e-5 --epochs 6 $MX --seed $sd --out out/devl-mix-s$sd
    step devl_mix_s${sd}_eval RESULTS_dev_lr2e5e6mix_s$sd.md $PY scripts/eval_mq.py --ckpt out/devl-mix-s$sd --typed-split dev --kind specialist --out RESULTS_dev_lr2e5e6mix_s$sd.md
    rm -f out/devl-mix-s$sd/model.safetensors
  done
  step pick_large_mix out/chosen_large_mix.txt $PY scripts/pick_recipe.py --configs lr2e5e6,lr2e5e6mix --out out/chosen_large_mix.txt --report RESULTS_mixer_dev_large.md
  if grep -q MIXER out/chosen_large_mix.txt 2>/dev/null; then
    LMX=$(sed "s/MIXER/${MX##* }/" out/chosen_large_mix.txt)
    for sd in 9 10 11; do
      step mix_large_s$sd out/mix-large-s$sd/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_decisions --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3 $LMX --seed $sd --out out/mix-large-s$sd
      step mix_large_s${sd}_eval preds_mix_large_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/mix-large-s$sd --typed-split test --kind specialist --dump-preds preds_mix_large_s$sd.jsonl --out RESULTS_mix_large_s$sd.md
      step sig_mix_large_s$sd RESULTS_sig_mix_large_s$sd.md $PY scripts/significance.py --cluster-field auto --a preds_mix_large_s$sd.jsonl --b preds_laya_td.jsonl --name-a Verdict-MQ-mix-large-s$sd --name-b Laya-td --out RESULTS_sig_mix_large_s$sd.md
    done
  fi
fi

# Email tasks on strong-teacher labels (eval = 32B/DeepSeek consensus)
while [ ! -f $OC/READY ]; do sleep 60; done
step org_verdict out/verdict-org/verdict_config.json $PY scripts/train.py --tasks $ORG --cache-dir $OC --out out/verdict-org --epochs 3 --batch-size 16 --bf16 --select last --render v2 --shuffle-options
step org_verdict_eval RESULTS_org_verdict.md $PY scripts/eval_orgbench.py --ckpt out/verdict-org --tasks $ORG --cache-dir $OC --batch-size 16 --permute-options --dump-preds preds_verdict_org.jsonl --out RESULTS_org_verdict.md
step org_verdict_calib RESULTS_org_calib $PY scripts/calibration.py --ckpt out/verdict-org --tasks $ORG --cache-dir $OC --batch-size 16 --ablation --fit-temp --out RESULTS_org_calib
step org_verdict_curve RESULTS_org_opcurve $PY scripts/operating_curve.py --ckpt out/verdict-org --tasks $ORG --cache-dir $OC --batch-size 16 --holdout --out RESULTS_org_opcurve
step org_plain RESULTS_org_plain.md $PY scripts/baseline_plain.py --tasks $ORG --cache-dir $OC --epochs 3 --batch-size 8 --out RESULTS_org_plain.md
step org_laya RESULTS_laya_ft_org.md $PY scripts/finetune_laya.py --tasks $ORG --cache-dir $OC --epochs 3 --batch-size 4 --eval-batch-size 16 --out RESULTS_laya_ft_org.md --dump-preds preds_laya_ft_org.jsonl

# Email tasks with the paper's main model (Verdict-MQ, NLI-base init)
step org_mq       out/org-mq/verdict_config.json $PY scripts/train_mq.py --init tasksource/ModernBERT-base-nli --tasks email_needs_reply@$OC,email_escalate@$OC,email_priority@$OC --out out/org-mq --epochs 3 --batch-cases 4 --soft --bf16 --max-len 2048
step org_mq_eval  RESULTS_org_mq.md $PY scripts/eval_mq.py --ckpt out/org-mq --tasks email_needs_reply@$OC,email_escalate@$OC,email_priority@$OC --dump-preds preds_org_mq.jsonl --out RESULTS_org_mq.md

# STANDARD, PEER-REVIEWED BENCHMARKS. Every baseline shares init + epochs with its MQ run.
# Contamination rule: tasksource/*-nli trained on SuperGLUE BoolQ/MultiRC -> those use RAW ModernBERT as primary.
TS=tasksource/ModernBERT-base-nli; RAW=answerdotai/ModernBERT-base
MQ="$PY scripts/train_mq.py --soft --bf16 --max-len 2048 $(cat out/chosen_mixer.txt 2>/dev/null)"
# RACE (4-way MC, ~3.5 questions per article): Verdict-MQ vs the standard multiple-choice head, two inits
for ini in "ts:$TS" "raw:$RAW"; do
  n=${ini%%:*}; m=${ini#*:}
  step race_mq_$n      out/race-mq-$n/verdict_config.json $MQ --init $m --tasks race --out out/race-mq-$n --epochs 2 --batch-cases 8 --option-dropout 0 --val-limit 2000
  step race_mq_${n}_eval RESULTS_race_mq_$n.md $PY scripts/eval_mq.py --ckpt out/race-mq-$n --tasks race --task-split test --latency --latency-task race --dump-preds preds_race_mq_$n.jsonl --out RESULTS_race_mq_$n.md
  step race_mc_$n      RESULTS_race_mc_$n.md $PY scripts/baseline_mc.py --init $m --task race --epochs 2 --batch-questions 4 --max-len 1024 --dump-preds preds_race_mc_$n.jsonl --out RESULTS_race_mc_$n.md
done
# BoolQ and MultiRC (SuperGLUE, validation = reporting split): primary RAW init, tasksource init as a disclosed row
for t in boolq multirc; do
  step ${t}_mq_raw      out/$t-mq-raw/verdict_config.json $MQ --init $RAW --tasks $t --out out/$t-mq-raw --epochs 3 --batch-cases 8 --val-limit 2000
  step ${t}_mq_raw_eval RESULTS_${t}_mq_raw.md $PY scripts/eval_mq.py --ckpt out/$t-mq-raw --tasks $t --task-split test --latency --latency-task $t --dump-preds preds_${t}_mq_raw.jsonl --out RESULTS_${t}_mq_raw.md
  step ${t}_pair_raw    RESULTS_${t}_pair_raw.md $PY scripts/baseline_pair.py --task $t --init $RAW --epochs 3 --batch-size 16 --dump-preds preds_${t}_pair_raw.jsonl --out RESULTS_${t}_pair_raw.md
  step ${t}_mq_ts       out/$t-mq-ts/verdict_config.json $MQ --init $TS --tasks $t --out out/$t-mq-ts --epochs 3 --batch-cases 8 --val-limit 2000
  step ${t}_mq_ts_eval  RESULTS_${t}_mq_ts.md $PY scripts/eval_mq.py --ckpt out/$t-mq-ts --tasks $t --task-split test --out RESULTS_${t}_mq_ts.md
done
# CLINC150 (151 intents incl. out-of-scope) and Banking77 (77 intents): tasksource init allowed (not in its list)
for t in clinc banking77; do
  step ${t}_mq      out/$t-mq/verdict_config.json $MQ --init $TS --tasks $t --out out/$t-mq --epochs 3 --batch-cases 16 --option-dropout 0.3 --val-limit 2000
  step ${t}_mq_eval RESULTS_${t}_mq.md $PY scripts/eval_mq.py --ckpt out/$t-mq --tasks $t --task-split test --dump-preds preds_${t}_mq.jsonl --out RESULTS_${t}_mq.md
  step ${t}_cls     RESULTS_${t}_cls.md $PY scripts/baseline_pair.py --task $t --init $TS --epochs 3 --batch-size 32 --max-len 128 --dump-preds preds_${t}_cls.jsonl --out RESULTS_${t}_cls.md
done

# paired significance, Verdict-MQ vs its matched baseline, on identical items
step sig_race_ts   RESULTS_sig_race_ts.md   $PY scripts/significance.py --cluster-field auto --a preds_race_mq_ts.jsonl --b preds_race_mc_ts.jsonl --name-a Verdict-MQ --name-b MC-head --out RESULTS_sig_race_ts.md
step sig_race_raw  RESULTS_sig_race_raw.md  $PY scripts/significance.py --cluster-field auto --a preds_race_mq_raw.jsonl --b preds_race_mc_raw.jsonl --name-a Verdict-MQ --name-b MC-head --out RESULTS_sig_race_raw.md
for t in boolq multirc; do
  step sig_${t}_raw RESULTS_sig_${t}_raw.md $PY scripts/significance.py --cluster-field auto --a preds_${t}_mq_raw.jsonl --b preds_${t}_pair_raw.jsonl --name-a Verdict-MQ --name-b pair-classifier --out RESULTS_sig_${t}_raw.md
done
for t in clinc banking77; do
  step sig_${t} RESULTS_sig_${t}.md $PY scripts/significance.py --cluster-field auto --a preds_${t}_mq.jsonl --b preds_${t}_cls.jsonl --name-a Verdict-MQ --name-b classifier --out RESULTS_sig_${t}.md
done

# LARGE-MODEL STABILITY (the gate for a robust accuracy claim): 2 of 6 seeds of the chosen recipe stalled.
# Candidates (literature remedies): longer warmup; layer-wise LR decay. Choice uses NO test data:
#   training-loss stall check on the seeds that stalled before (full train, seeds 1-2) + DEV accuracy (seeds 0-1).
LG="$PY scripts/train_mq.py --init tasksource/ModernBERT-large-nli --batch-cases 4 --soft --bf16 --max-len 2048 --option-dropout 0.3"
for cfg in "warm20:--lr 2e-5 --epochs 6 --warmup-frac 0.2" "llrd:--lr 3e-5 --epochs 6 --warmup-frac 0.1 --llrd 0.9"; do
  c=${cfg%%:*}; f=${cfg#*:}
  for sd in 1 2; do
    step stab_${c}_full_s$sd out/stab-$c-full-s$sd/train_log.json $LG --tasks typed_decisions $f --seed $sd --out out/stab-$c-full-s$sd
    rm -f out/stab-$c-full-s$sd/model.safetensors
  done
  for sd in 0 1; do
    step devs_${c}_s$sd out/devs-$c-s$sd/verdict_config.json $LG --tasks typed_dev $f --seed $sd --out out/devs-$c-s$sd
    step devs_${c}_s${sd}_eval RESULTS_devs_${c}_s$sd.md $PY scripts/eval_mq.py --ckpt out/devs-$c-s$sd --typed-split dev --kind specialist --out RESULTS_devs_${c}_s$sd.md
    rm -f out/devs-$c-s$sd/model.safetensors
  done
done
step pick_stable out/chosen_stable.txt $PY scripts/pick_stable.py --configs warm20,llrd
# five brand-new test seeds of the chosen (possibly unchanged) recipe; all reported
for sd in 30 31 32 33 34; do
  step stable_s$sd out/stable-s$sd/verdict_config.json $LG --tasks typed_decisions $(cat out/chosen_stable.txt 2>/dev/null) --seed $sd --out out/stable-s$sd
  step stable_s${sd}_eval preds_stable_s$sd.jsonl $PY scripts/eval_mq.py --ckpt out/stable-s$sd --typed-split test --kind specialist --dump-preds preds_stable_s$sd.jsonl --out RESULTS_stable_s$sd.md
  step sig_stable_s$sd RESULTS_sig_stable_s$sd.md $PY scripts/significance.py --cluster-field auto --a preds_stable_s$sd.jsonl --b preds_laya_td.jsonl --name-a Verdict-MQ-large-stable-s$sd --name-b Laya-td --out RESULTS_sig_stable_s$sd.md
done

echo "=== BATCH 6 DONE $(date -Is) ==="

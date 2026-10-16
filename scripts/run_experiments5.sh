#!/bin/bash
# Batch 5 — the two deciding experiments (2026-09-23 plan).
#  A. Laya zero-shot + fine-tuned on PUBLIC3 (vs Verdict 89.3 / plain 93.5)
#  B. Email tasks on strong-teacher labels (Qwen3-VL-32B; eval on 32B==DeepSeek consensus):
#     Verdict-org, plain head, Laya zero-shot + fine-tuned, + calibration / held-out threshold
#  C. Own-model path: Verdict trained on a diverse typed-decision MIXTURE with shuffled
#     options + option-subset sampling; ZERO-SHOT on held-out tasks (sst2, banking77, email)
#  D. Mixture model fine-tuned on the email tasks (does diverse pre-training help, as Laya's does?)
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PYTHON:-python3}"
export HF_HUB_DISABLE_PROGRESS_BARS=1 PYTHONUNBUFFERED=1 PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
P3="route_topic,signal_positive,affect"
ORG="email_needs_reply,email_escalate,email_priority"
OC="data/jsonl_orgcons"
MIX="route_topic,affect,topic_dbpedia,topic_yahoo,question_type,irony,hate,typed_decisions"
FILT="Warning: You are sending|Kwargs passed|initialized from|mean_resizing|Loading weights|LOAD REPORT|UNEXPECTED|^Key |^Notes|can be ignored|MISSING|^-+\+|^\s*$|classifier\.|Fetching|Generating|return Agent"
run() { local name=$1; echo "=== [$name] $(date -Is) ==="; shift; "$@" 2>&1 | { grep -vE "$FILT" || true; } | tail -40; local rc=${PIPESTATUS[0]}
  if [ "$rc" -ne 0 ]; then echo "=== [$name] FAILED (exit $rc) $(date -Is) ==="; exit "$rc"; fi
  echo "=== [done] $(date -Is) ==="; }

while pgrep -f "/tmp/shuf_run.sh" >/dev/null; do sleep 60; done
ollama stop qwen2.5:7b-instruct 2>/dev/null || true; sleep 2
echo "=== batch 5 start $(date -Is) ==="

# 0. Typed-decisions benchmark, same protocol as Laya: the model receives the criterion descriptions Laya receives
run typed_base_desc      $PY scripts/train_typed.py --soft --select last --epochs 6 --out out/verdict-typed-desc --out-md RESULTS_typed_desc.md
run typed_base_desc_eval $PY scripts/eval_typed.py --ckpt out/verdict-typed-desc --permute-options --out RESULTS_typed_desc_eval.md

# A. Laya on PUBLIC3
run laya_ft_public3 $PY scripts/finetune_laya.py --tasks $P3 --epochs 3 --batch-size 8 --out RESULTS_laya_ft_public3.md --dump-preds preds_laya_ft_public3.jsonl

# B. email tasks (wait for the labelling machine to ship strong-teacher labels)
while [ ! -f $OC/READY ]; do sleep 60; done
run org_verdict        $PY scripts/train.py --tasks $ORG --cache-dir $OC --out out/verdict-org --epochs 3 --batch-size 16 --bf16 --select last --render v2
run org_verdict_eval   $PY scripts/eval_orgbench.py --ckpt out/verdict-org --tasks $ORG --cache-dir $OC --batch-size 16 --dump-preds preds_verdict_org.jsonl --out RESULTS_org_verdict.md
run org_verdict_calib  $PY scripts/calibration.py --ckpt out/verdict-org --tasks $ORG --cache-dir $OC --batch-size 16 --ablation --fit-temp --out RESULTS_org_calib
run org_verdict_curve  $PY scripts/operating_curve.py --ckpt out/verdict-org --tasks $ORG --cache-dir $OC --batch-size 16 --holdout --out RESULTS_org_opcurve
run org_plain          $PY scripts/baseline_plain.py --tasks $ORG --cache-dir $OC --epochs 3 --batch-size 8 --out RESULTS_org_plain.md
run org_laya           $PY scripts/finetune_laya.py --tasks $ORG --cache-dir $OC --epochs 3 --batch-size 4 --eval-batch-size 16 --out RESULTS_laya_ft_org.md --dump-preds preds_laya_ft_org.jsonl

# C. mixture (own cache dir so PUBLIC3 val caches are never overwritten)
run mix_train     $PY scripts/train.py --tasks $MIX --cache-dir data/jsonl_mix --out out/verdict-mix --epochs 3 --batch-size 16 --limit 8000 --val-limit 500 --shuffle-options --option-dropout 0.5 --bf16 --select last --render v2
run mix_heldout   $PY scripts/eval_orgbench.py --ckpt out/verdict-mix --tasks signal_positive,route_intent --permute-options --dump-preds preds_mix_heldout.jsonl --out RESULTS_mix_heldout.md
run mix_heldout_org $PY scripts/eval_orgbench.py --ckpt out/verdict-mix --tasks $ORG --cache-dir $OC --batch-size 16 --out RESULTS_mix_heldout_org.md
run mix_inmix     $PY scripts/eval_orgbench.py --ckpt out/verdict-mix --tasks route_topic,affect --permute-options --out RESULTS_mix_inmix.md
run mix_typed     $PY scripts/eval_typed.py --ckpt out/verdict-mix --permute-options --out RESULTS_typed_mix.md
run laya_heldout  $PY scripts/finetune_laya.py --tasks signal_positive,route_intent --epochs 0 --out RESULTS_laya_heldout.md --dump-preds preds_laya_heldout.jsonl

# E. typed-decisions, large backbone, descriptions + soft labels
run typed_large_desc      $PY scripts/train_typed.py --soft --select last --epochs 6 --batch-size 8 --backbone answerdotai/ModernBERT-large --out out/verdict-typed-large-desc --out-md RESULTS_typed_large_desc.md
run typed_large_desc_eval $PY scripts/eval_typed.py --ckpt out/verdict-typed-large-desc --permute-options --out RESULTS_typed_large_desc_eval.md

# D. mixture -> email fine-tune
run mixorg_train  $PY scripts/train.py --tasks $ORG --cache-dir $OC --backbone out/verdict-mix --out out/verdict-mix-org --epochs 3 --batch-size 16 --bf16 --select last --shuffle-options
run mixorg_eval   $PY scripts/eval_orgbench.py --ckpt out/verdict-mix-org --tasks $ORG --cache-dir $OC --batch-size 16 --dump-preds preds_verdict_mixorg.jsonl --out RESULTS_mixorg.md

echo "=== BATCH 5 DONE $(date -Is) ==="

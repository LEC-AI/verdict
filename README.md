# Verdict

**Encode once, decide many: an open decision layer for typed organizational decisions.**

Verdict is a research implementation from LEC AI for answering several typed questions about one shared input. This
repository contains the implementation, the experiment scripts and the saved evaluation outputs that accompany the
paper *Verdict: Encode Once, Decide Many* (Chouhan and Perry, 2026). Trained checkpoints are not included.

Verdict answers **typed** questions about one piece of state (an email, ticket, invoice, agent trace) with a
probability distribution over declared options, so an automation can act above a confidence threshold and escalate
below it. Three question types: `choice` (one of N described options), `noul` (yes/no), `score` (ordinal rubric).

**Verdict-MQ** reads a case *once* and answers *all* of its questions in one ModernBERT pass. A structured attention mask
guarantees, by construction (given identical retained state tokens after truncation):
- the state encoding does not depend on the questions (cacheable),
- questions do not influence each other (a packed answer equals the single-question answer),
- option order cannot change any answer (all options share position ids; the sliding window uses position ids).

```python
from verdict.mq import VerdictMQ, MQCase, MQQuestion

m = VerdictMQ.from_pretrained("out/mq-large")                   # a checkpoint trained as in Reproduce below
case = MQCase(state=email_text, questions=[
    MQQuestion("Does this email require a written reply?", ["false: no reply expected", "true: a reply is expected"], "noul"),
    MQQuestion("How urgent is handling this email?", ["level 0: no action", "level 1: low", "level 2: today", "level 3: immediately"], "score"),
])
p_reply, p_urgency = m.predict([case])[0]                   # one pass, two probability distributions
```

## Results (see the paper for full numbers, significance tests and caveats)

Typed-decisions benchmark (test split, specialist mode): a 395M Verdict-MQ matches the soft gold labels significantly
better than the released 421M Laya specialist on all five fresh seeds (KL 0.080 vs 0.117, Brier 0.045 vs 0.061),
robust to per-system temperature scaling; accuracy (0.801 vs 0.767) is past the benchmark's own saturation point, so
we read that margin mainly as agreement with the benchmark's labelling teacher, not as evidence of better decisions.
A 150M model ties Laya on accuracy. A held-out autonomy dial lets the large model auto-handle 62-71% of decisions at a
90% accuracy target, against Laya's 56%.

Standard, peer-reviewed benchmarks (RACE, BoolQ, MultiRC): against a matched fine-tuned baseline, Verdict-MQ wins on
MultiRC, loses narrowly on RACE, and loses on BoolQ, where training is unstable. Laya's general checkpoint and Jev
serve as zero-shot references, not fine-tuned on these tasks; Jev outperforms every fine-tuned model here.

A controlled k=0 vs. k=22 comparison prices the shared state directly: letting each question's state read the
question gains 0.9-3.5 points on RACE and MultiRC at 1.4-2.5x the per-case latency, and nothing measurable on typed
decisions, with the invariance guarantees unchanged at every depth. The accuracy lead over Laya, and the
distributional advantage above, are both most consistent with the NLI initialization rather than the architecture
(see the paper's attribution section); the architecture's own contribution is efficiency and the invariance
guarantees.

Packing is 2.7-2.8x faster per case than one pass per question at batch size 8 (1.3-1.8x at batch size 1).

Negative result: generalists trained on a synthetic multi-workflow corpus fail zero-shot (paper appendix).

## Install
```bash
pip install -e .                  # Python >= 3.10; version requirements in pyproject.toml
pip install -e ".[baselines]"     # optional: Laya and the Jev API client, for the baseline comparisons
```
Every number in the paper was produced with torch 2.11, transformers 5.17 and datasets 4.8. The Jev scripts read a
Vercel AI Gateway key from `~/.config/verdict/vercel_ai_gateway.key`. No trained checkpoints are distributed: train
one with the command below, then load it with `VerdictMQ.from_pretrained`.

## Reproduce
```bash
python3 scripts/test_mq.py                                   # architecture guarantees
python3 scripts/train_mq.py --init tasksource/ModernBERT-large-nli --tasks typed_decisions \
    --out out/mq-large --epochs 6 --batch-cases 4 --lr 2e-5 --warmup-frac 0.2 --marker cls \
    --soft --bf16 --max-len 2048 --option-dropout 0.3
python3 scripts/eval_mq.py --ckpt out/mq-large --typed-split test --latency --dump-preds preds.jsonl
python3 scripts/eval_laya_typed.py --subfolder typed-decisions --dump-preds preds_laya.jsonl
python3 scripts/significance.py --a preds.jsonl --b preds_laya.jsonl --cluster-field idx   # case-cluster bootstrap, as in the paper
```
Every run in the paper fits on one 16 GB GPU. Every results table in the paper is generated from the files in `results/`
by `python3 scripts/make_tables.py --out tables`.

The drivers `scripts/run_experiments*.sh` (batches 1 to 16) hold the exact command of every run in the paper,
including the standard benchmarks, in the order they were run. Their header comments record the reasoning at the time
each batch was launched and are kept as a record; where an early plan and the final analysis differ, the paper is
authoritative. Some early batches also contain preliminary experiments that the paper does not report.

## Repository layout
| Path | Contents |
|---|---|
| `verdict/` | the model (`mq.py`: Verdict-MQ, packing and attention masks), data loaders and typed-decision metrics |
| `scripts/` | training, evaluation, baselines, significance tests, table generation and the experiment drivers |
| `scripts/test_mq.py` | numerical checks of the invariance guarantees |
| `results/laptop-latest/` | result files and per-decision predictions behind every table (dated folders are earlier snapshots) |
| `data/labels/` | LLM-distilled labels for the Enron email tasks, keyed to message hashes |
| `SPLIT_PLAN.md` | the pre-registered plan for the split-depth experiments, with its dated amendment |
| `LICENSES-DATA.md` | the datasets and models used, their licences, and what this repository contains from each |

`SPLIT_PLAN.md` is kept unchanged since its dated amendment (2026-09-24, before any final result), as a record of the
original plan. The paper reports the final analyses and any deviations from that plan.

## Paper
Avdhesh Singh Chouhan and Jack Perry. *Verdict: Encode Once, Decide Many.* LEC AI, 2026. [arXiv:2610.20778](https://arxiv.org/abs/2610.20778).
If you use this code, please cite the paper (see Citation below).

## License
Code: Apache-2.0, copyright LEC AI Limited (see `LICENSE` and `NOTICE`). Model checkpoints are not part of this
release. Third-party datasets keep their own terms and are not redistributed; see `LICENSES-DATA.md`.

## Contact
Avdhesh Singh Chouhan (avdhesh.chouhan@lecai.ai) and Jack Perry (jack@lecai.ai), LEC AI.

## Citation
```bibtex
@article{chouhan2026verdict,
  title   = {Verdict: Encode Once, Decide Many},
  author  = {Chouhan, Avdhesh Singh and Perry, Jack},
  journal = {arXiv preprint arXiv:2610.20778},
  year    = {2026},
  eprint  = {2610.20778},
  archivePrefix = {arXiv},
  url     = {https://arxiv.org/abs/2610.20778}
}
```

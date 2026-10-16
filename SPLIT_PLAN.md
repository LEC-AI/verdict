# Split-depth Verdict-MQ — pre-registered plan (written 2026-09-24, before any split-depth result)

## Why

On standard benchmarks the fully shared model (k = 0) ties strong classifiers on intent detection but loses on reading
comprehension: RACE −4.1 against the multiple-choice head, BoolQ −15.2 against a pair classifier. Hypothesis: rule 1
(the state never attends to the question, at any layer) prevents question-specific reading of the passage.

## Model

`joint_layers = k` (verdict/mq.py). The lower L − k layers use the existing masks, so the state encoding is shared and
question-independent there (and cacheable). For the top k layers each question gets its own copy of the lower-layer
state; within that row, state and question tokens see the whole row, and each option sees the state, the question and
itself. Question independence and option-order invariance still hold exactly (scripts/test_mq.py, section 7).
k = 0 is the current model; k = L (22 for base) is one question per pass, the accuracy reference.

## AMENDMENT, 2026-09-24 10:00–11:45: a second, larger bug found and fixed first

Before evaluating k, a BoolQ diagnostic (k = 22, i.e. every layer question-aware, i.e. equivalent in information terms
to a per-question pass) still scored 62.1% test, at the majority-class floor — so the k sweep could not have worked
until this was fixed. Root cause, confirmed with a frozen-encoder linear probe on 600 BoolQ items (5-fold CV; standard
pair-format encoding scores 0.76, majority class is 0.63): the option marker is a newly-added `[OPT]` token, absorbed
by `resize_token_embeddings` with a random/mean-init embedding. Reading out from it (or from anything the model computes
in the presence of it) drops the probe to 0.57–0.61, near-majority, regardless of k or the option mixer (both ruled out
by their own controls). Reusing an EXISTING special token — `[MASK]` or `[CLS]` — as the marker restores the probe to
0.75–0.79 and, in full training runs, restores BoolQ to 81–83% (beats or ties the tuned pair-classifier baseline
80.9–80.9%), at k as low as 0. `verdict/mq.py` now takes `marker ∈ {opt, mask, cls, sep}`; `opt` is kept as the default
for backward compatibility only. **Every result reported before 2026-09-24 12:00 (typed-decisions headline, RACE,
MultiRC, BoolQ, the email tasks) used the `opt` marker and must be treated as a lower bound**, not a corrected number;
a same-recipe sanity check on typed-decisions found `mask`/`cls` at or slightly above the `opt` numbers (0.779/0.783
vs. 0.766 mean, better KL/Brier), i.e. no evidence of a hidden cost elsewhere, but it is one seed and not a substitute
for the full reruns below.

Marker and depth interact (BoolQ, seed 0, dev): `mask` peaks at k = 4 (77.5%) and is worse at k = 0 (67.8%) or k = 22
(68.8%); `cls` peaks at k = 0 (77.9%) and is much worse at k = 22 (64.4%). So (marker, k) must be chosen JOINTLY, not
one axis at a time, and the diagnostic numbers above (found while debugging, not for selection) do not by themselves
license a pick — the sweep below does that properly, on dev, still never on test.

## Benchmarks, inits, splits

| benchmark | init | train | dev (selection only) | test (reported) |
|---|---|---|---|---|
| BoolQ | raw ModernBERT-base (the NLI init saw BoolQ) | 90% of train | 10% of train, held out by passage | official validation |
| MultiRC | raw ModernBERT-base (the NLI init saw MultiRC) | 90% of train | 10% of train, held out by paragraph | official validation |
| RACE | tasksource ModernBERT-base-nli | train | official dev | official test |

BoolQ's dev split is new (earlier BoolQ runs trained on all of train), so every BoolQ run is redone.

## Sweep (dev only), revised for the marker × depth grid

* Verdict-MQ, (marker, k) ∈ {mask, cls} × {0, 4, 22}, lr 3e-5 fixed (not tuned), same epochs/batch as the original runs
  (BoolQ, MultiRC: 3 epochs; RACE: 2 epochs, option dropout 0), option mixer 2 layers, seed 0. `opt`-marker cells already
  collected (batch 7 and the diagnostics) are kept as the "before" reference but not eligible for selection.
* Baselines get an lr sweep, which Verdict-MQ does not get: pair classifier (BoolQ, MultiRC), lr ∈
  {1e-5, 2e-5, 3e-5, 5e-5}, seeds 0 and 1, 3 epochs. RACE multiple-choice head keeps lr 3e-5 (already 79.0%/80.9% under
  the two splits used).

## Selection rules (fixed now, before any RACE/MultiRC marker result exists)

* **(marker\*, k\*)** = the cell with the highest mean dev accuracy averaged over the three benchmarks, among
  {mask, cls} × {0, 4, 22}. Ties (within 0.5 points of the best) broken toward the smaller k, then toward `cls` (cheaper
  at inference: no extra top-k pass needed at k = 0).
* **Baseline lr** = highest mean dev accuracy, per benchmark (unchanged from the original plan).

## Final evaluation (test)

* Seeds: BoolQ 5 (0–4), MultiRC 3 (0–2), RACE 3 (0–2), for Verdict-MQ at (marker\*, k\*) and for the chosen baseline.
* Paired per seed: exact McNemar, 10k bootstrap CI.
* Reported for every (marker, k) cell tried on seed 0 (the full accuracy–cost grid, not only the chosen cell): test
  accuracy and latency (ms per passage, batch 1, bf16, RTX 4090 Laptop), next to the baseline's latency.
* Typed-decisions (no tuning there): the base model at (marker\*, k\*) with the base recipe, seeds 6–8, against the
  `opt`-marker k = 0 runs final2-base-s6..8 and against Laya. THEN, only if base does not regress: the large model at
  (marker\*, k\*), stable-recipe seeds 30–34, replacing the current paper headline (0.789 ± 0.007, `opt` marker).

## What counts as success (criterion 2)

Verdict-MQ at (marker\*, k\*) is at least as accurate as the tuned baseline on RACE (within the 95% CI or better) and on
BoolQ, while cheaper per passage. Anything else is reported as it comes out.

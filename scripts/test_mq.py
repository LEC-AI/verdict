"""Numerical checks of Verdict-MQ's architectural guarantees (random-init head, real backbone)."""
import os, sys, random
import torch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.mq import MQCase, MQQuestion, VerdictMQ

torch.manual_seed(0)
m = VerdictMQ.from_pretrained("answerdotai/ModernBERT-base", device="cpu")
state = '{"ticket": "INC-4471", "users_impacted": 42, "note": "ERP ledger returns 500 errors; VP needs it before the board meeting tomorrow."}'
q1 = MQQuestion("How urgent is this ticket?", ["level 0: none", "level 1: routine", "level 2: elevated", "level 3: critical"], "score")
q2 = MQQuestion("What should be done with this ticket?", ["keep_current_tier: can be solved here", "escalate_next_tier: needs specialists",
                "escalate_emergency: crisis team", "reassign_same_tier: wrong specialist"], "choice")
q3 = MQQuestion("The ticket has breached its SLA.", ["false: within SLA", "true: SLA breached"], "noul")

base = m.predict([MQCase(state, [q1, q2, q3])])[0]
# 1) option-order invariance
perm = [2, 0, 3, 1]
q2p = MQQuestion(q2.instructions, [q2.options[i] for i in perm], "choice")
pp = m.predict([MQCase(state, [q1, q2p, q3])])[0]
d_perm = max(abs(pp[1][j] - base[1][perm[j]]) for j in range(4))
# 2) question independence
alone = m.predict([MQCase(state, [q2])])[0][0]
d_indep = max(abs(a - b) for a, b in zip(alone, base[1]))
# 3) batching / padding
other = MQCase("short state", [q3])
batched = m.predict([MQCase(state, [q1, q2, q3]), other])
d_batch = max(abs(a - b) for a, b in zip(batched[0][0], base[0]))
# 4) non-degeneracy: option markers must NOT collapse to one representation
ids, pos, masks, packs = m.collate([MQCase(state, [q1, q2, q3])])
with torch.no_grad():
    h = m.backbone(input_ids=ids, position_ids=pos, attention_mask=masks).last_hidden_state[0]
mk = packs[0]["markers"][1]
spread = min(float((h[a] - h[b]).norm()) for a in mk for b in mk if a != b)
# 5) learnability: a few steps on one case must raise every gold option's probability
opt = torch.optim.AdamW(m.parameters(), lr=5e-5)
case = MQCase(state, [q1, q2, q3]); gold = [3, 1, 0]
p_before = m.predict([case])[0]
m.train()
for _ in range(15):
    lg = m.logits([case])[0]
    loss = sum(torch.nn.functional.cross_entropy(l.unsqueeze(0), torch.tensor([g])) for l, g in zip(lg, gold))
    opt.zero_grad(); loss.backward(); opt.step()
m.eval()
p_after = m.predict([case])[0]
gain = min(p_after[k][g] - p_before[k][g] for k, g in enumerate(gold))
print(f"max |dP| option permutation: {d_perm:.2e}\nmax |dP| alone vs packed:    {d_indep:.2e}\nmax |dP| batched vs single:  {d_batch:.2e}")
print(f"min marker spread (L2, must be > 0.1): {spread:.3f}\nmin gold-prob gain after 15 steps (must be > 0.05): {gain:.3f}")
print("probs before:", [[round(x, 3) for x in p] for p in p_before])
ok = d_perm < 1e-4 and d_indep < 1e-4 and d_batch < 1e-4 and spread > 0.1 and gain > 0.05
print("ALL GUARANTEES HOLD" if ok else "FAILED")

# 6) the same guarantees with the permutation-equivariant option mixer on
mm = VerdictMQ.from_pretrained("answerdotai/ModernBERT-base", device="cpu", mixer_layers=2)
mm.eval()
b2 = mm.predict([MCase := MQCase(state, [q1, q2, q3])])[0]
p2 = mm.predict([MQCase(state, [q1, q2p, q3])])[0]
d_perm2 = max(abs(p2[1][j] - b2[1][perm[j]]) for j in range(4))
alone2 = mm.predict([MQCase(state, [q2])])[0][0]
d_indep2 = max(abs(a - b) for a, b in zip(alone2, b2[1]))
print(f"[mixer] max |dP| option permutation: {d_perm2:.2e} | alone vs packed: {d_indep2:.2e} | "
      f"probs spread q2: {max(b2[1]) - min(b2[1]):.3f}")
ok2 = d_perm2 < 1e-4 and d_indep2 < 1e-4
print("MIXER GUARANTEES HOLD" if ok2 else "MIXER FAILED")

# 7) split depth: the state reads each question in the top k layers; guarantees must still hold exactly
okS = True
for k in (4, len(m.backbone.layers)):
    m.joint_layers = k; m.eval()
    bs = m.predict([MQCase(state, [q1, q2, q3])])[0]
    ps = m.predict([MQCase(state, [q1, q2p, q3])])[0]
    d_perm_s = max(abs(ps[1][j] - bs[1][perm[j]]) for j in range(4))
    d_indep_s = max(abs(a - b) for a, b in zip(m.predict([MQCase(state, [q2])])[0][0], bs[1]))
    d_batch_s = max(abs(a - b) for a, b in zip(m.predict([MQCase(state, [q1, q2, q3]), other])[0][0], bs[0]))
    with torch.no_grad():                   # logits, not probabilities: the trained head saturates the softmax
        ls = m.logits([MQCase(state, [q2])])[0][0]; m.joint_layers = 0; l0 = m.logits([MQCase(state, [q2])])[0][0]
    d_vs_shared = float((ls - l0).abs().max())                     # the question-aware state must change the answer
    print(f"[split k={k}] |dP| permutation {d_perm_s:.2e} | alone vs packed {d_indep_s:.2e} | batched {d_batch_s:.2e} | "
          f"logits vs shared k=0 {d_vs_shared:.2e} (must be > 1e-3)")
    okS &= d_perm_s < 1e-4 and d_indep_s < 1e-4 and d_batch_s < 1e-4 and d_vs_shared > 1e-3
# learnability through the split path
m.joint_layers = 4; m.train(); opt = torch.optim.AdamW(m.parameters(), lr=5e-5)
case2 = MQCase(state, [q1, q2, q3]); gold2 = [0, 2, 1]
pb = m.predict([case2])[0]; m.train()
for _ in range(15):
    lg = m.logits([case2])[0]
    loss = sum(torch.nn.functional.cross_entropy(l.unsqueeze(0), torch.tensor([g])) for l, g in zip(lg, gold2))
    opt.zero_grad(); loss.backward(); opt.step()
m.eval(); pa = m.predict([case2])[0]
gainS = min(pa[q][g] - pb[q][g] for q, g in enumerate(gold2))
print(f"[split k=4] min gold-prob gain after 15 steps: {gainS:.3f}")
okS &= gainS > 0.05
print("SPLIT GUARANTEES HOLD" if okS else "SPLIT FAILED")

# 8) match readout (question-summary x option marker): same guarantees, shared and split
okM = True
for ro, k in (("match", 0), ("match", 4), ("pool", 0), ("pool", 4)):
    mr = VerdictMQ.from_pretrained("answerdotai/ModernBERT-base", device="cpu", readout=ro); mr.eval()
    mr.joint_layers = k
    b3 = mr.predict([MQCase(state, [q1, q2, q3])])[0]; p3 = mr.predict([MQCase(state, [q1, q2p, q3])])[0]
    dp = max(abs(p3[1][j] - b3[1][perm[j]]) for j in range(4))
    di = max(abs(a - b) for a, b in zip(mr.predict([MQCase(state, [q2])])[0][0], b3[1]))
    print(f"[{ro} k={k}] |dP| permutation {dp:.2e} | alone vs packed {di:.2e}")
    okM &= dp < 1e-4 and di < 1e-4
print("READOUT GUARANTEES HOLD" if okM else "READOUT FAILED")

# 9) existing-token markers ([MASK]): same guarantees, markers distinct, learnable
mm2 = VerdictMQ.from_pretrained("answerdotai/ModernBERT-base", device="cpu", marker="mask"); mm2.eval()
okK = True
for k in (0, 4):
    mm2.joint_layers = k
    b4 = mm2.predict([MQCase(state, [q1, q2, q3])])[0]; p4 = mm2.predict([MQCase(state, [q1, q2p, q3])])[0]
    dp = max(abs(p4[1][j] - b4[1][perm[j]]) for j in range(4))
    di = max(abs(a - b) for a, b in zip(mm2.predict([MQCase(state, [q2])])[0][0], b4[1]))
    print(f"[marker=mask k={k}] |dP| permutation {dp:.2e} | alone vs packed {di:.2e}")
    okK &= dp < 1e-4 and di < 1e-4
assert "[OPT]" not in mm2.tokenizer.get_vocab() and mm2.opt_id == mm2.tokenizer.mask_token_id
print("MASK-MARKER GUARANTEES HOLD" if okK else "MASK-MARKER FAILED")

# 10) truncation and the invariance guarantee's real precondition (found by independent review, 2026-09-27): pack()
# truncates state to fit max_len minus the packed questions, so a long state can retain FEWER tokens when packed with
# MORE questions. The guarantee (packed == alone) holds given IDENTICAL retained state tokens, not the original state
# under arbitrary re-groupings. Both halves checked: (a) with identical retained tokens (small max_len forcing the
# same truncation regardless of grouping), invariance still holds exactly; (b) with DIFFERENT retained tokens (a case
# long enough that grouping changes what survives), answers CAN legitimately differ -- documented, not hidden.
mt = VerdictMQ.from_pretrained("answerdotai/ModernBERT-base", device="cpu", max_len=64); mt.eval()
long_state = " ".join(f"word{i}" for i in range(200))  # far longer than any max_len we test here
qA = MQQuestion("Question A?", ["false: no", "true: yes"], "noul")
qB = MQQuestion("Question B?", ["0: low", "1: high"], "choice")
# (a) identical retained tokens: max_len so small that qA's own room is already saturated; packing qB too can only
# shrink an ALREADY-maximal truncation by a little, so we pin retained tokens explicitly to be equal by using states
# short enough to never hit the cap in either grouping, at this max_len:
short_state = "A short state that fits well within max_len even with two questions appended after it for testing."
alone_a = mt.predict([MQCase(short_state, [qA])])[0][0]
packed_ab = mt.predict([MQCase(short_state, [qA, qB])])[0][0]
d_identical = max(abs(a - b) for a, b in zip(alone_a, packed_ab))
print(f"[trunc, identical retained state] |dP| alone vs packed: {d_identical:.2e} (must be < 1e-4)")
ok10 = d_identical < 1e-4
# (b) different retained tokens: force actual truncation by using a genuinely long state at a small max_len, so
# packing more questions leaves less state; we do NOT assert equality here, only that the mechanism behaves as
# documented (retained state differs) and predict() still runs without error.
p = mt.pack(MQCase(long_state, [qA]))
p2 = mt.pack(MQCase(long_state, [qA, qB]))
state_len_alone = sum(1 for b in p["blk"] if b == 0)
state_len_packed = sum(1 for b in p2["blk"] if b == 0)
print(f"[trunc, long state] retained state tokens: alone={state_len_alone}, packed-with-2nd-question={state_len_packed}"
      f" ({'differ, as documented' if state_len_alone != state_len_packed else 'coincidentally equal'})")
ok10 = ok10 and state_len_alone >= state_len_packed  # packing more questions never RESERVES more room for state
print("TRUNCATION-PRECONDITION CHECK HOLDS" if ok10 else "TRUNCATION-PRECONDITION CHECK FAILED")

# 11) packing overflow: pack() must raise, not silently return a sequence longer than max_len, when the packed
# questions/options alone already exceed the budget (found by independent review, 2026-09-28: an un-chunked
# MultiRC passage's full ~58-question set reaches 6,378 tokens against max_len=2048). Every real training/eval
# path goes through mq_data.to_cases()'s max_questions chunking before pack(), so this never fires on reported
# numbers (scripts/scan_truncation.py); this only checks pack() fails loudly if that precondition is skipped.
mo = VerdictMQ.from_pretrained("answerdotai/ModernBERT-base", device="cpu", max_len=64)
many_qs = [MQQuestion(f"Question {i}?", ["false: no", "true: yes"], "noul") for i in range(50)]
try:
    mo.pack(MQCase("short state", many_qs))
    ok11 = False
except ValueError:
    ok11 = True
print("OVERFLOW-GUARD CHECK HOLDS" if ok11 else "OVERFLOW-GUARD CHECK FAILED")

# 12) the guarantee checks above run in fp32 on CPU; every real training/eval run uses bf16 autocast (--bf16), where
# reduced mantissa precision means the exactly-symmetric attention mask no longer gives fp32-level agreement (found
# by independent review, 2026-09-28: the fp32 permutation-invariance check reports differences around 1e-7, but the
# SAME check under bf16 autocast reports differences around 1e-3 -- still small in absolute probability terms, but
# four orders of magnitude looser, and this is the precision actually used everywhere numbers are reported). We
# assert only a loose bound (bf16 must still be much better than a random/uninvariant baseline), not fp32-level
# tightness, and print the real figure so it isn't silently forgotten.
with torch.autocast(device_type="cpu", dtype=torch.bfloat16):
    base16 = m.predict([MQCase(state, [q1, q2, q3])])[0]
    pp16 = m.predict([MQCase(state, [q1, q2p, q3])])[0]
    d_perm16 = max(abs(pp16[1][j] - base16[1][perm[j]]) for j in range(4))
print(f"[bf16] max |dP| option permutation: {d_perm16:.2e} (fp32 was {d_perm:.2e}; must be < 1e-1)")
ok12 = d_perm16 < 1e-1

all_ok = {"guarantees": ok, "mixer": ok2, "split": okS, "readout": okM, "mask-marker": okK, "truncation": ok10,
          "overflow-guard": ok11, "bf16-invariance-sanity": ok12}
failed = [name for name, v in all_ok.items() if not v]
if failed:
    sys.exit(f"FAILED checks: {failed}")
print("ALL CHECKS PASSED")

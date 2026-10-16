"""Behavioral (not just numerical) consequences of bf16 on a FINAL trained checkpoint: does bf16 noise ever flip
an argmax, or move a decision across the autonomy dial's deployed confidence threshold, under permutation,
regrouping (alone vs packed) and batching (found requested by independent review, 2026-09-28: distinguish
mathematical equivariance from numerical behavior on real checkpoints, not just a random-head sanity model).

  python3 scripts/check_bf16_behavior.py --ckpt out/stable-cls-s42 --n 400 --tau 0.520
"""
import argparse
import os
import random
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.mq import MQCase, MQQuestion, VerdictMQ
from verdict.mq_data import to_cases
from verdict.data_typed import load_typed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--n", type=int, default=400, help="number of real test cases to check")
    ap.add_argument("--tau", type=float, default=0.520, help="the autonomy dial's fitted confidence threshold to check crossings against")
    a = ap.parse_args()
    device = "cuda" if torch.cuda.is_available() else "cpu"
    m = VerdictMQ.from_pretrained(a.ckpt, device=device)
    m.eval()
    bf16 = torch.autocast(device_type=device, dtype=torch.bfloat16)

    cases = [c for c, _ in to_cases(load_typed("test"))][: a.n]
    n_decisions = 0
    argmax_flips_dtype = 0        # fp32 vs bf16, same case, same grouping
    tau_crossings_dtype = 0
    argmax_flips_perm = 0         # bf16, permuted options vs original, same case
    tau_crossings_perm = 0
    argmax_flips_alone = 0        # bf16, alone vs packed with siblings
    tau_crossings_alone = 0

    rng = random.Random(0)
    for case in cases:
        with torch.no_grad():
            p_fp32 = m.predict([case])[0]
        with torch.no_grad(), bf16:
            p_bf16 = m.predict([case])[0]
        for qi in range(len(case.questions)):
            n_decisions += 1
            am32 = max(range(len(p_fp32[qi])), key=p_fp32[qi].__getitem__)
            am16 = max(range(len(p_bf16[qi])), key=p_bf16[qi].__getitem__)
            if am32 != am16:
                argmax_flips_dtype += 1
            c32, c16 = p_fp32[qi][am32], p_bf16[qi][am16]
            if (c32 >= a.tau) != (c16 >= a.tau):
                tau_crossings_dtype += 1

        # permutation check (bf16 only): permute a choice question's options, compare argmax (mapped back) and conf
        choice_qs = [i for i, q in enumerate(case.questions) if q.qtype == "choice" and len(q.options) > 1]
        if choice_qs:
            qi = rng.choice(choice_qs)
            q = case.questions[qi]
            perm = list(range(len(q.options))); rng.shuffle(perm)
            qp = MQQuestion(q.instructions, [q.options[i] for i in perm], "choice")
            new_questions = list(case.questions); new_questions[qi] = qp
            with torch.no_grad(), bf16:
                p_perm = m.predict([MQCase(case.state, new_questions)])[0]
            am_orig = max(range(len(p_bf16[qi])), key=p_bf16[qi].__getitem__)
            am_perm_raw = max(range(len(p_perm[qi])), key=p_perm[qi].__getitem__)
            am_perm_mapped = perm[am_perm_raw]  # map back to original option index
            if am_orig != am_perm_mapped:
                argmax_flips_perm += 1
            c_orig, c_perm = p_bf16[qi][am_orig], p_perm[qi][am_perm_raw]
            if (c_orig >= a.tau) != (c_perm >= a.tau):
                tau_crossings_perm += 1

        # alone-vs-packed check (bf16 only): answer one question alone vs packed with its siblings
        if len(case.questions) > 1:
            qi = rng.randrange(len(case.questions))
            with torch.no_grad(), bf16:
                p_alone = m.predict([MQCase(case.state, [case.questions[qi]])])[0][0]
            am_packed = max(range(len(p_bf16[qi])), key=p_bf16[qi].__getitem__)
            am_alone = max(range(len(p_alone)), key=p_alone.__getitem__)
            if am_packed != am_alone:
                argmax_flips_alone += 1
            c_packed, c_alone = p_bf16[qi][am_packed], p_alone[am_alone]
            if (c_packed >= a.tau) != (c_alone >= a.tau):
                tau_crossings_alone += 1

    print(f"checkpoint={a.ckpt} device={device} n_cases={len(cases)} n_decisions={n_decisions} tau={a.tau}")
    print(f"[fp32 vs bf16, same grouping]      argmax flips: {argmax_flips_dtype}/{n_decisions} | tau-crossings: {tau_crossings_dtype}/{n_decisions}")
    print(f"[bf16, option permutation]         argmax flips: {argmax_flips_perm}/{len(cases)} | tau-crossings: {tau_crossings_perm}/{len(cases)}")
    print(f"[bf16, alone vs packed]            argmax flips: {argmax_flips_alone}/{len(cases)} | tau-crossings: {tau_crossings_alone}/{len(cases)}")


if __name__ == "__main__":
    main()

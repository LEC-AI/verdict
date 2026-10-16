"""Why does a synthetic-corpus generalist score below uniform on typed-decisions? Compare predicted vs gold
marginals per primitive on the TRAIN (dev) split, and the same marginals in the synthetic corpus."""
import json, os, sys
from collections import Counter, defaultdict
import torch
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.mq import VerdictMQ  # noqa: E402
from verdict.mq_data import to_cases  # noqa: E402
from verdict.data_typed import load_typed  # noqa: E402

ckpts = sys.argv[1:] or ["out/mq-syn", "out/mq-nli-syn"]
cases = to_cases(load_typed("train"))[::4]            # 300 cases, 1500 decisions
def marg(recs_probs):
    st = defaultdict(lambda: {"n": 0, "hit": 0, "gold_idx": Counter(), "pred_idx": Counter(), "p_true": 0.0, "g_true": 0})
    for r, p in recs_probs:
        s = st[r.qtype]; top = max(range(len(p)), key=p.__getitem__)
        s["n"] += 1; s["hit"] += int(top == r.answer); s["gold_idx"][r.answer] += 1; s["pred_idx"][top] += 1
        if r.qtype == "noul": s["p_true"] += p[1]; s["g_true"] += int(r.answer == 1)
    return st
for ck in ckpts:
    m = VerdictMQ.from_pretrained(ck, device="cpu")
    rp = []
    for i in range(0, len(cases), 8):
        ch = cases[i:i + 8]
        for probs, (_, recs) in zip(m.predict([c for c, _ in ch]), ch):
            rp += list(zip(recs, probs))
    print(f"== {ck}")
    for t, s in marg(rp).items():
        extra = f" | mean P(true) {s['p_true']/s['n']:.2f} vs gold true-rate {s['g_true']/s['n']:.2f}" if t == "noul" else ""
        print(f"  {t}: acc {s['hit']/s['n']*100:.1f}% | gold idx {dict(sorted(s['gold_idx'].items()))} | pred idx {dict(sorted(s['pred_idx'].items()))}{extra}")
# synthetic corpus marginals
rows = [json.loads(l) for l in open("data/synth_pilot/synth_train.jsonl")]
g = defaultdict(Counter)
for r in rows: g[r["qtype"]][r["answer"]] += 1
print("== synthetic pilot gold argmax distribution:", {k: dict(sorted(v.items())) for k, v in g.items()})
t = defaultdict(Counter)
for c, recs in to_cases(load_typed("train")):
    for r in recs: t[r.qtype][r.answer] += 1
print("== benchmark TRAIN gold distribution:     ", {k: dict(sorted(v.items())) for k, v in t.items()})

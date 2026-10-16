"""Validate verdict/typed_metrics.py against the typed-decisions card's
reference rows. Card (test split): Uniform acc .308 soft .311 F1 .152 KL .444 TV .381 Brier .238 ECE .169;
Prior acc .470 soft .430 F1 .207 KL .347 TV .317 Brier .189 ECE .088."""
import json
import os
import sys
import types
from collections import Counter, defaultdict

_ROOT = os.path.join(os.path.dirname(__file__), "..")
_pkg = types.ModuleType("verdict"); _pkg.__path__ = [os.path.join(_ROOT, "verdict")]
sys.modules.setdefault("verdict", _pkg)
from verdict.typed_metrics import MD_HEADER, md_row, summarize  # noqa: E402


def cases(split):
    from datasets import load_dataset
    for ex in load_dataset("LocalLLaMA/typed-decisions", name="all", split=split):
        Q = json.loads(ex["questions"]); G = json.loads(ex["gold"])
        for qn, qd in Q.items():
            t = qd.get("type"); crit = qd.get("criteria")
            if t == "noul":
                keys = ["false", "true"]
            elif t == "score":
                keys = [str(i) for i in range(len(crit))] if isinstance(crit, list) else list(crit)
            else:
                keys = list(crit.keys())                     # card order (criteria order)
            g = G[qn]; probs = g.get("probabilities") or {}
            p = [float(probs.get(k, 0.0)) for k in keys]; s = sum(p) or 1.0; p = [x / s for x in p]
            lab = str(g.get("label"))
            if lab not in keys:
                continue
            yield dict(key=(ex["workflow"], qn), keys=keys, p=p, gold=keys.index(lab), qtype=t)


train = list(cases("train")); test = list(cases("test"))
freq = defaultdict(Counter)
for r in train:
    freq[r["key"]][r["gold"]] += 1
rows_u, rows_p = [], []
for r in test:
    k = len(r["keys"])
    rows_u.append({**r, "q": [1.0 / k] * k})
    c = freq[r["key"]]; tot = sum(c.values()) or 1
    rows_p.append({**r, "q": [c[i] / tot for i in range(k)]})
print("\n".join(MD_HEADER))
for mode in ["sum", "mean"]:
    print(md_row(f"Uniform (brier={mode})", "reference", summarize(rows_u, mode)))
    print(md_row(f"Prior (brier={mode})", "reference", summarize(rows_p, mode)))
print("| Uniform (card) | reference | 0.308 | 0.311 | 0.152 | 0.444 | 0.381 | 0.238 | 0.169 | - | - |")
print("| Prior (card) | reference | 0.470 | 0.430 | 0.207 | 0.347 | 0.317 | 0.189 | 0.088 | - | - |")
print(f"test decisions scored: {len(test)}")

# ---- variants: soft-mean prior; ECE on the System One confidence scale ----
import laya, inspect
print(inspect.getsource(laya.confidence_from_probs)[:900])
soft = defaultdict(lambda: None); cnt = Counter()
for r in train:
    k = r["key"]
    soft[k] = [a + b for a, b in zip(soft[k], r["p"])] if soft[k] else list(r["p"]); cnt[k] += 1
rows_ps = [{**r, "q": [x / cnt[r["key"]] for x in soft[r["key"]]]} for r in test]
print(md_row("Prior soft-mean", "reference", summarize(rows_ps)))
from verdict.typed_metrics import _ece
for name, rows in [("Uniform", rows_u), ("Prior", rows_p), ("Prior soft-mean", rows_ps)]:
    cr = []
    for r in rows:
        q = r["q"]; top = max(range(len(q)), key=q.__getitem__)
        cr.append((float(laya.confidence_from_probs(__import__("numpy").array(q), len(q))), int(top == r["gold"])))
    print(f"{name}: ECE on System-One confidence = {_ece(cr):.3f}")

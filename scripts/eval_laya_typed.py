"""Measure Laya ourselves on the typed-decisions TEST split, using the
benchmark's NATIVE question definitions (instructions + criteria descriptions),
exactly as Laya is meant to be called. Turns the vendor-reported 76.6% into a
measured number on our harness, per primitive and per workflow, with ECE.

Accuracy rule per primitive (same labels as verdict.data_typed):
  choice -> argmax option key == gold label
  noul   -> P(true) >= 0.5  <=> gold label == "true"
  score  -> argmax level == gold label (Laya's `score` is an expectation; we use the mode)

  python3 scripts/eval_laya_typed.py --subfolder typed-decisions --out RESULTS_laya_typed.md
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import types
from collections import defaultdict

_ROOT = os.path.join(os.path.dirname(__file__), "..")
_pkg = types.ModuleType("verdict"); _pkg.__path__ = [os.path.join(_ROOT, "verdict")]
sys.modules.setdefault("verdict", _pkg)
from verdict.typed_metrics import MD_HEADER, md_row, summarize  # noqa: E402


def ece10(rows):
    b = [[0, 0, 0.0] for _ in range(10)]
    for c, h in rows:
        k = min(int(c * 10), 9); b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / n if n else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subfolder", default="typed-decisions")
    ap.add_argument("--device", default=None)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--out", default="RESULTS_laya_typed.md")
    ap.add_argument("--dump-preds", default=None, help="per-decision JSONL keyed like eval_mq.py for significance.py")
    a = ap.parse_args()
    try:
        import laya
    except ImportError:
        raise SystemExit('Laya baseline not installed: pip install -e ".[baselines]"')
    from datasets import load_dataset
    agent = laya.load("convaiinnovations/laya", subfolder=None if a.subfolder in ("", "none", "default") else a.subfolder, device=a.device)
    ds = load_dataset("LocalLLaMA/typed-decisions", name="all", split="test")
    if a.limit:
        ds = ds.select(range(a.limit))
    by_p, by_w, rows, n, hit_all, t0 = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), [], 0, 0, time.time()
    card_rows = []
    dump = []
    import hashlib
    from verdict.data_typed import _state_text
    for ex in ds:
        Q = json.loads(ex["questions"]) if isinstance(ex["questions"], str) else ex["questions"]
        G = json.loads(ex["gold"]) if isinstance(ex["gold"], str) else ex["gold"]
        state = ex["state"]
        try:
            state = json.loads(state)
        except Exception:
            pass
        ans = agent.predict(state, Q)["answers"]
        for q, qd in Q.items():
            g = str(G.get(q, {}).get("label")); t = qd.get("type", "choice"); r = ans[q]
            crit = qd.get("criteria")
            keys = (["false", "true"] if t == "noul" else
                    [str(i) for i in range(len(crit))] if t == "score" and isinstance(crit, list) else list(crit))
            gp = G.get(q, {}).get("probabilities") or {}
            pg = [float(gp.get(k, 0.0)) for k in keys]; sg = sum(pg) or 1.0; pg = [x / sg for x in pg]
            if t == "noul":
                qp = [1 - float(r["noul"]), float(r["noul"])]
            else:
                qp = [float(r["probabilities"].get(k, 0.0)) for k in keys]; sq = sum(qp) or 1.0; qp = [x / sq for x in qp]
            if g in keys:
                card_rows.append({"q": qp, "p": pg, "gold": keys.index(g), "qtype": t, "key": (ex["workflow"], q)})
                top = max(range(len(qp)), key=qp.__getitem__)
                dump.append({"task": f"{ex['workflow']}:{q}", "idx": hashlib.sha1(_state_text(ex["state"]).encode()).hexdigest()[:16],
                             "gold": keys.index(g), "pred": top, "conf": max(qp), "hit": int(top == keys.index(g)), "probs": qp})
            if t == "choice":
                h = int(r["choice"] == g); c = max(r["probabilities"].values())
            elif t == "noul":
                h = int((r["noul"] >= 0.5) == (g == "true")); c = max(r["noul"], 1 - r["noul"])
            else:
                probs = r["probabilities"]; top = max(probs, key=probs.get)
                h = int(top == g); c = probs[top]
            by_p[t][0] += h; by_p[t][1] += 1
            by_w[ex["workflow"]][0] += h; by_w[ex["workflow"]][1] += 1
            rows.append((float(c), h)); n += 1; hit_all += h
    acc = hit_all / max(n, 1)
    md = [f"# Laya ({a.subfolder}) on typed-decisions TEST, native questions — measured by us", "",
          f"overall **{acc*100:.1f}%** (n={n} decisions, {len(ds)} cases), ECE-10 {ece10(rows):.3f}, {time.time()-t0:.0f}s", "",
          "by primitive: " + ", ".join(f"{k} {v[0]/v[1]*100:.1f}%" for k, v in by_p.items()),
          "by workflow: " + ", ".join(f"{k} {v[0]/v[1]*100:.1f}%" for k, v in by_w.items()),
          "", *MD_HEADER, md_row(f"Laya ({a.subfolder})", "see note", summarize(card_rows)),
          "", "Mode: the 'typed-decisions' checkpoint may have been fitted on this benchmark's train split (specialist); "
              "the default checkpoint is a general model scored zero-shot. Card leaderboard: Decider 1 0.768, Jev 0.727 (general)."]
    open(a.out, "w").write("\n".join(md) + "\n")
    if a.dump_preds:
        with open(a.dump_preds, "w") as f:
            for r in dump:
                f.write(json.dumps(r) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

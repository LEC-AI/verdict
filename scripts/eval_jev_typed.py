"""Measure Jev (TypeSafe AI) OURSELVES on the typed-decisions TEST split, native questions, via Vercel AI Gateway's
`/v1/evaluate` endpoint (2026-09-25) — the same identical protocol used for Laya (scripts/eval_laya_typed.py) and our
own Verdict-MQ, so this is a real, controlled, apples-to-apples comparison instead of citing Jev's own card number
(0.727, self-reported, general/zero-shot, methodology undisclosed).

Jev supports several typed questions against one state in a single request (its own "encode once, decide many" -
the same case-level test we already run for Verdict-MQ), so we send ONE call per case with all 5 of its questions,
mirroring the packed-latency comparison story.

Cost: ~$0.0000116/call per Vercel's own documented example (275 input / 20 output tokens) x 400 test cases ~= $0.005.
A --limit flag runs a small pilot first; nothing here is called until you choose to run it.

  python3 scripts/eval_jev_typed.py --limit 10 --out RESULTS_jev_typed_pilot.md   # pilot, ~10 calls
  python3 scripts/eval_jev_typed.py --out RESULTS_jev_typed.md --dump-preds preds_jev_typed.jsonl  # full run
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import types
from collections import defaultdict

import requests

_ROOT = os.path.join(os.path.dirname(__file__), "..")
_pkg = types.ModuleType("verdict"); _pkg.__path__ = [os.path.join(_ROOT, "verdict")]
sys.modules.setdefault("verdict", _pkg)
from verdict.typed_metrics import MD_HEADER, md_row, summarize  # noqa: E402
from verdict.data_typed import _state_text  # noqa: E402

GATEWAY = "https://ai-gateway.vercel.sh/v1/evaluate"
KEY_FILE = os.path.expanduser("~/.config/verdict/vercel_ai_gateway.key")
TYPE_MAP = {"noul": "boolean", "choice": "choice", "score": "score"}  # our type names -> Jev's request type names


def ece10(rows):
    b = [[0, 0, 0.0] for _ in range(10)]
    for c, h in rows:
        k = min(int(c * 10), 9); b[k][0] += 1; b[k][1] += h; b[k][2] += c
    n = len(rows)
    return sum(abs(h / c - cf / c) * c for c, h, cf in b if c) / n if n else float("nan")


def jev_questions(Q):
    """Our raw dataset question dict -> Jev's /v1/evaluate request schema. Returns (payload, keys_per_question)."""
    out, keys_by_q = {}, {}
    for qname, qdef in Q.items():
        qtype = qdef.get("type", "choice")
        crit = qdef.get("criteria")
        if qtype == "noul":
            out[qname] = {"type": "boolean", "instructions": qdef.get("instructions", qname),
                          **({"criteria": crit} if isinstance(crit, dict) else {})}
            keys_by_q[qname] = ["false", "true"]
        elif qtype == "score":
            if isinstance(crit, list):
                labels, keys = crit, [str(i) for i in range(len(crit))]
            elif isinstance(crit, dict):
                keys = sorted(crit.keys(), key=lambda x: int(x)) if all(k.isdigit() for k in crit) else sorted(crit.keys())
                labels = [crit[k] for k in keys]
            else:
                labels, keys = ["0", "1", "2", "3"], ["0", "1", "2", "3"]
            out[qname] = {"type": "score", "instructions": qdef.get("instructions", qname), "criteria": labels}
            keys_by_q[qname] = keys
        else:  # choice
            keys = sorted(crit.keys()) if isinstance(crit, dict) else list(crit)
            out[qname] = {"type": "choice", "instructions": qdef.get("instructions", qname),
                          "criteria": crit if isinstance(crit, dict) else {k: k for k in keys}}
            keys_by_q[qname] = keys
    return out, keys_by_q


def call_jev(key, state, questions, retries=4):
    for attempt in range(retries):
        r = requests.post(GATEWAY, headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                          json={"model": "typesafe-ai/jev", "state": state, "questions": questions}, timeout=60)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 500, 502, 503, 504) and attempt < retries - 1:
            time.sleep(2 ** attempt * 2); continue
        raise RuntimeError(f"Jev call failed ({r.status_code}): {r.text[:500]}")
    raise RuntimeError("Jev call failed: retries exhausted")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="pilot mode: only this many cases")
    ap.add_argument("--sleep", type=float, default=0.3, help="seconds between calls (politeness, not a rate-limit fix)")
    ap.add_argument("--out", default="RESULTS_jev_typed.md")
    ap.add_argument("--dump-preds", default=None, help="per-decision JSONL keyed like eval_laya_typed.py for significance.py")
    a = ap.parse_args()
    if not os.path.isfile(KEY_FILE):
        raise SystemExit(f"no Vercel AI Gateway key at {KEY_FILE}")
    key = open(KEY_FILE).read().strip()

    from datasets import load_dataset
    ds = load_dataset("LocalLLaMA/typed-decisions", name="all", split="test")
    if a.limit:
        ds = ds.select(range(min(a.limit, len(ds))))

    by_p, by_w, rows, n, hit_all, t0 = defaultdict(lambda: [0, 0]), defaultdict(lambda: [0, 0]), [], 0, 0, time.time()
    card_rows, dump, errors = [], [], []
    for i, ex in enumerate(ds):
        Q = json.loads(ex["questions"]) if isinstance(ex["questions"], str) else ex["questions"]
        G = json.loads(ex["gold"]) if isinstance(ex["gold"], str) else ex["gold"]
        state = ex["state"]
        try:
            state = json.loads(state)
        except Exception:
            pass
        payload, keys_by_q = jev_questions(Q)
        try:
            resp = call_jev(key, state, payload)
        except Exception as e:
            errors.append(str(e)); continue
        ans = resp.get("answers", {})
        for q, qd in Q.items():
            t = qd.get("type", "choice"); keys = keys_by_q[q]
            g = str(G.get(q, {}).get("label"))
            r = ans.get(q)
            if r is None:
                errors.append(f"case {i} missing answer for {q}"); continue
            gp_raw = G.get(q, {}).get("probabilities") or {}
            pg = [float(gp_raw.get(k, 0.0)) for k in keys]; sg = sum(pg) or 1.0; pg = [x / sg for x in pg]
            if t == "noul":
                p1 = float(r.get("probability", 0.5)); qp = [1 - p1, p1]
            else:
                probs = r.get("probabilities", {}); qp = [float(probs.get(k, 0.0)) for k in keys]
                sq = sum(qp) or 1.0; qp = [x / sq for x in qp]
            if g not in keys:
                continue
            gold_idx = keys.index(g)
            card_rows.append({"q": qp, "p": pg, "gold": gold_idx, "qtype": t, "key": (ex["workflow"], q)})
            top = max(range(len(qp)), key=qp.__getitem__)
            dump.append({"task": f"{ex['workflow']}:{q}", "idx": hashlib.sha1(_state_text(ex["state"]).encode()).hexdigest()[:16],
                         "gold": gold_idx, "pred": top, "conf": max(qp), "hit": int(top == gold_idx)})
            h = int(top == gold_idx); c = max(qp)
            by_p[t][0] += h; by_p[t][1] += 1
            by_w[ex["workflow"]][0] += h; by_w[ex["workflow"]][1] += 1
            rows.append((c, h)); n += 1; hit_all += h
        if (i + 1) % 25 == 0:
            print(f"  {i+1}/{len(ds)} cases, {n} decisions, acc so far {hit_all/max(n,1):.3f}, {len(errors)} errors", flush=True)
        time.sleep(a.sleep)

    acc = hit_all / max(n, 1)
    md = [f"# Jev (TypeSafe AI, typesafe-ai/jev) on typed-decisions TEST, native questions — measured by us via Vercel AI Gateway", "",
          f"overall **{acc*100:.1f}%** (n={n} decisions, {len(ds)} cases attempted, {len(errors)} errors), ECE-10 {ece10(rows):.3f}, {time.time()-t0:.0f}s", "",
          "by primitive: " + ", ".join(f"{k} {v[0]/v[1]*100:.1f}%" for k, v in by_p.items()),
          "by workflow: " + ", ".join(f"{k} {v[0]/v[1]*100:.1f}%" for k, v in by_w.items()),
          "", *MD_HEADER, md_row("Jev (measured)", "see note", summarize(card_rows)),
          "", "Measured ourselves via the Vercel AI Gateway /v1/evaluate endpoint, one call per case (all 5 questions "
              "batched, same protocol as Laya/Verdict-MQ). Card leaderboard (self-reported, undisclosed methodology): Jev 0.727."]
    if errors:
        md += ["", f"**{len(errors)} errors** (first 5): " + "; ".join(errors[:5])]
    open(a.out, "w").write("\n".join(md) + "\n")
    if a.dump_preds:
        with open(a.dump_preds, "w") as f:
            for r in dump:
                f.write(json.dumps(r) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

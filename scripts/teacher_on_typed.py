"""Diagnostic: how well does one of our corpus teachers agree with the typed-decisions gold?
Uses the exact labeling prompt of scripts/synth_typed.py on benchmark cases (TRAIN split by default,
i.e. the development split; never the test split). If a teacher agrees only ~X% with the benchmark's
gold, a student distilled from it is capped near X% zero-shot, however much synthetic data we make.

  python3 scripts/teacher_on_typed.py --model local:Qwen/Qwen3-VL-32B-Instruct-FP8 --n 200
"""
import argparse
import json
import math
import os
import sys
import urllib.request
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(__file__))
import synth_typed as S  # noqa: E402

WF = {
    "agent_trace_observability": "Assess an agent run to decide whether human review is needed, and how urgent it is.",
    "customer_service": "Determine the appropriate assistant response and action from a customer thread and account state.",
    "invoice_processing": "Review a vendor bill against the order and delivery to determine payment, hold or rejection.",
    "security_incidents": "Decide whether a security alert should be closed, investigated, or contained, from alert data and machine history.",
}


def rows(split, n):
    out, off = [], 0
    while len(out) < n:
        url = (f"https://datasets-server.huggingface.co/rows?dataset=LocalLLaMA/typed-decisions&config=all"
               f"&split={split}&offset={off}&length=100")
        with urllib.request.urlopen(url, timeout=60) as r:
            got = [x["row"] for x in json.loads(r.read())["rows"]]
        if not got:
            break
        out += got; off += 100
    # spread across workflows: take every k-th row
    step = max(1, len(out) // n)
    return out[::step][:n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="local:Qwen/Qwen3-VL-32B-Instruct-FP8")
    ap.add_argument("--split", default="train")
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--fetch", type=int, default=1200)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--out", default="RESULTS_teacher_on_typed.md")
    a = ap.parse_args()
    cases = rows(a.split, a.fetch)
    step = max(1, len(cases) // a.n); cases = cases[::step][: a.n]

    def one(ex):
        Q = json.loads(ex["questions"]); G = json.loads(ex["gold"])
        state = ex["state"] if isinstance(ex["state"], str) else json.dumps(ex["state"])
        prompt = S.LABEL_PROMPT.format(description=WF.get(ex["workflow"], ex["workflow"]), state=state,
                                       questions=S.render_questions(Q))
        out = S.parse_json(S.chat(a.model, prompt, temperature=0.0, max_tokens=700)) or {}
        res = []
        for qn, q in Q.items():
            keys = S.option_keys(q); pts = out.get(qn)
            if not isinstance(pts, dict):
                continue
            v = [S._num(pts.get(k, 0)) for k in keys]
            if sum(v) <= 0:
                continue
            p = [x / sum(v) for x in v]
            g = G[qn]; lab = str(g.get("label"))
            if lab not in keys:
                continue
            gp = [float((g.get("probabilities") or {}).get(k, 0)) for k in keys]; z = sum(gp) or 1; gp = [x / z for x in gp]
            top = max(range(len(p)), key=p.__getitem__)
            kl = sum(pi * math.log((pi + 1e-6) / (qi + 1e-6)) for pi, qi in zip(gp, p) if pi > 0)
            res.append((ex["workflow"], q["type"], int(top == keys.index(lab)), kl))
        return res

    with ThreadPoolExecutor(a.workers) as ex:
        allr = [r for rs in ex.map(one, cases) for r in rs]
    by_p, by_w = defaultdict(list), defaultdict(list)
    for w, t, h, _ in allr:
        by_p[t].append(h); by_w[w].append(h)
    acc = sum(h for _, _, h, _ in allr) / max(len(allr), 1)
    kl = sum(k for *_, k in allr) / max(len(allr), 1)
    md = [f"# Teacher-vs-benchmark agreement — {a.model} on typed-decisions {a.split.upper()} ({len(cases)} cases, {len(allr)} decisions)", "",
          f"argmax agreement with gold **{acc*100:.1f}%**, KL(gold || teacher) {kl:.3f}", "",
          "by primitive: " + ", ".join(f"{k} {sum(v)/len(v)*100:.1f}%" for k, v in by_p.items()),
          "by workflow: " + ", ".join(f"{k} {sum(v)/len(v)*100:.1f}%" for k, v in by_w.items()), "",
          "Reference: benchmark teacher self-agreement 0.735; perfect scenario understanding 0.704; prior 0.470."]
    open(a.out, "w").write("\n".join(md) + "\n"); print("\n".join(md))


if __name__ == "__main__":
    main()

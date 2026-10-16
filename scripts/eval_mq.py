"""Evaluate a Verdict-MQ checkpoint.

  --typed-split test|train : typed-decisions with the card's metrics (train = dev split for generalists)
  --tasks A,B --cache-dir D : per-task accuracy / macro-F1 / ECE on cached val splits (OrgBench-style)
  --latency                : ms per case, packed (all questions in one pass) vs one question per pass
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.mq import MQCase, VerdictMQ  # noqa: E402
from verdict.mq_data import item_key, load_split, to_cases  # noqa: E402
from verdict.typed_metrics import MD_HEADER, _ece, md_row, summarize  # noqa: E402


def run(model, cases, bs):
    out = []
    for i in range(0, len(cases), bs):
        out += model.predict([c for c, _ in cases[i:i + bs]])
    return out


def macro_f1(y, p):
    cls = sorted(set(y) | set(p)); fs = []
    for c in cls:
        tp = sum(1 for a, b in zip(y, p) if a == c and b == c); fp = sum(1 for a, b in zip(y, p) if a != c and b == c)
        fn = sum(1 for a, b in zip(y, p) if a == c and b != c)
        pr = tp / (tp + fp) if tp + fp else 0.0; rc = tp / (tp + fn) if tp + fn else 0.0
        fs.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    return sum(fs) / len(fs) if fs else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ckpt", required=True)
    ap.add_argument("--typed-split", default=None, choices=[None, "test", "train", "dev"],
                    help="dev = the 15%% of TRAIN cases held out by train_mq --tasks typed_dev (recipe tuning)")
    ap.add_argument("--tasks", default="")
    ap.add_argument("--task-split", default="val", choices=["val", "test"],
                    help="for --tasks: 'test' = reporting split of standard benchmarks (race/boolq/clinc)")
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--batch-cases", type=int, default=16)
    ap.add_argument("--latency", action="store_true")
    ap.add_argument("--latency-task", default="typed_decisions", help="cases for the latency test (typed_decisions|race|...)")
    ap.add_argument("--dump-preds", default=None)
    ap.add_argument("--kind", default="specialist", help="label for the typed table row (specialist|generalist)")
    ap.add_argument("--out", default="RESULTS_mq.md")
    a = ap.parse_args()
    model = VerdictMQ.from_pretrained(a.ckpt)
    amp = torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=torch.cuda.is_available())
    md, res, dump = [f"# Verdict-MQ evaluation — {a.ckpt}", ""], {}, []

    if a.typed_split:
        from verdict.data_typed import load_typed
        if a.typed_split == "dev":
            cases = to_cases(load_split("typed_dev", "val"))
        else:
            cases = to_cases(load_typed(a.typed_split))
        with amp:
            preds = run(model, cases, a.batch_cases)
        rows, by_p = [], {}
        for probs, (_, recs) in zip(preds, cases):
            for p, r in zip(probs, recs):
                rows.append({"q": p, "p": r.meta["soft"], "gold": r.answer, "qtype": r.qtype, "key": (r.meta["workflow"], r.meta["question"])})
                h = int(max(range(len(p)), key=p.__getitem__) == r.answer)
                by_p.setdefault(r.qtype, []).append(h)
                dump.append({"task": f"{r.meta['workflow']}:{r.meta['question']}",
                             "idx": __import__("hashlib").sha1(r.text.encode()).hexdigest()[:16],
                             "gold": r.answer, "pred": max(range(len(p)), key=p.__getitem__),
                             "conf": max(p), "hit": h, "probs": p})
        m = summarize(rows); res["typed"] = m
        md += [f"## typed-decisions {a.typed_split.upper()} ({len(cases)} cases, {len(rows)} decisions)", "", *MD_HEADER,
               md_row(os.path.basename(a.ckpt.rstrip('/')), a.kind, m),
               "| Laya typed-decisions ckpt (measured) | specialist | 0.767 | 0.605 | 0.661 | 0.117 | 0.174 | 0.061 | 0.214 | 0.242 | 0.981 |",
               "| ModernBERT-base (card) | specialist | 0.646 | 0.542 | 0.469 | 0.223 | 0.249 | 0.119 | 0.179 | 0.444 | 0.931 |",
               "| TypeSafe Jev 1.13.0 (card) | general | 0.727 | 0.580 | 0.613 | 1.442 | 0.251 | 0.148 | 0.144 | 0.391 | 0.952 |",
               "| meraGPT Decider 1 (card) | general | 0.768 | 0.608 | 0.641 | 0.096 | 0.149 | 0.052 | 0.180 | 0.219 | 0.984 |", "",
               "by primitive: " + ", ".join(f"{k} {sum(v)/len(v)*100:.1f}%" for k, v in by_p.items()), ""]

    if a.tasks:
        md += ["## tasks", "", "| task | n | acc | macro-F1 | ECE |", "|---|---|---|---|---|"]
        for t in a.tasks.split(","):
            cases = to_cases(load_split(t, a.task_split, a.cache_dir))
            with amp:
                preds = run(model, cases, a.batch_cases)
            y, pr, rows = [], [], []
            for probs, (case, recs) in zip(preds, cases):
                case_id = hashlib.sha1(case.state.encode("utf-8")).hexdigest()[:16]
                for p, r in zip(probs, recs):
                    top = max(range(len(p)), key=p.__getitem__); y.append(r.answer); pr.append(top); rows.append((p[top], int(top == r.answer)))
                    dump.append({"task": t.split("@")[0], "idx": item_key(r), "case": case_id, "gold": r.answer, "pred": top,
                                 "conf": p[top], "hit": int(top == r.answer), "probs": p})
            acc = sum(h for _, h in rows) / max(len(rows), 1)
            res[t] = {"n": len(rows), "acc": acc, "macro_f1": macro_f1(y, pr), "ece": _ece(rows)}
            md.append(f"| {t} | {len(rows)} | {acc*100:.1f}% | {res[t]['macro_f1']*100:.1f}% | {res[t]['ece']:.4f} |")
            if t.startswith("multirc"):
                allrecs = [r for _, recs in cases for r in recs]
                tp = sum(1 for g_, p_ in zip(y, pr) if g_ == 1 and p_ == 1); fp = sum(1 for g_, p_ in zip(y, pr) if g_ == 0 and p_ == 1)
                fn = sum(1 for g_, p_ in zip(y, pr) if g_ == 1 and p_ == 0)
                f1a = 2 * tp / max(2 * tp + fp + fn, 1)
                byq = {}
                for r, g_, p_ in zip(allrecs, y, pr):
                    byq.setdefault(r.meta["qid"], []).append(g_ == p_)
                em = sum(all(v) for v in byq.values()) / max(len(byq), 1)
                res[t].update({"f1a": f1a, "em": em, "n_questions": len(byq)})
                md.append(f"| {t} (official) | {len(byq)} questions | F1a {f1a*100:.1f} | EM {em*100:.1f} | |")
        md.append("")

    if a.latency:
        if a.latency_task == "typed_decisions":
            from verdict.data_typed import load_typed
            cases = [c for c, _ in to_cases(load_typed("test"))][:128]
        else:
            cases = [c for c, _ in to_cases(load_split(a.latency_task, "test"))][:128]
        single = [[MQCase(c.state, [q]) for q in c.questions] for c in cases]
        dev = next(model.parameters()).device
        sync = (lambda: torch.cuda.synchronize()) if dev.type == "cuda" else (lambda: None)
        lat = {}
        for bs in [1, 8]:
            for mode in ["packed", "one-question-per-pass"]:
                with amp:
                    model.predict(cases[:bs])            # warmup
                    sync(); t0 = time.perf_counter()
                    for i in range(0, len(cases), bs):
                        if mode == "packed":
                            model.predict(cases[i:i + bs])
                        else:
                            model.predict([s for c in single[i:i + bs] for s in c])
                    sync()
                lat[(mode, bs)] = 1000 * (time.perf_counter() - t0) / len(cases)
        q = sum(len(c.questions) for c in cases) / len(cases)
        md += ["## latency (%s test cases, %.2f questions per case, %s, bf16)" % (a.latency_task, q, dev), "",
               "| mode | batch (cases) | ms per case | ms per decision |", "|---|---|---|---|"]
        for (mode, bs), v in lat.items():
            md.append(f"| {mode} | {bs} | {v:.2f} | {v/q:.2f} |")
        res["latency_ms_per_case"] = {f"{k[0]}@{k[1]}": v for k, v in lat.items()}

    open(a.out, "w").write("\n".join(md) + "\n")
    json.dump(res, open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    if a.dump_preds:
        with open(a.dump_preds, "w") as f:
            for r in dump:
                f.write(json.dumps(r) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()

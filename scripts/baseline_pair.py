"""Standard classifier baselines for the peer-reviewed benchmarks, same init / epochs as the Verdict-MQ run they
are compared with.
  boolq, multirc   : AutoModelForSequenceClassification(2) on (passage, question[+answer]) pairs; the passage is
                     re-encoded for every question (the standard way)
  clinc, banking77 : AutoModelForSequenceClassification(n_labels) on the utterance
Reports accuracy / macro-F1 / ECE (MultiRC: official F1a and EM) on the reporting split, and ms per case.

  python3 scripts/baseline_pair.py --task boolq --init answerdotai/ModernBERT-base --epochs 3 --out RESULTS_boolq_pair_raw.md
"""
from __future__ import annotations

import argparse
import json
import math
import os
import random
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.mq_data import item_key, load_split, split_record, to_cases  # noqa: E402
from verdict.typed_metrics import _ece  # noqa: E402

PAIR = {"boolq", "multirc"}


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
    ap.add_argument("--task", required=True, choices=["boolq", "multirc", "clinc", "banking77", "phishing"])
    ap.add_argument("--init", default="answerdotai/ModernBERT-base")
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dump-preds", default=None)
    ap.add_argument("--eval-dev", action="store_true", help="also score the monitoring split (for lr selection)")
    a = ap.parse_args()
    random.seed(a.seed); torch.manual_seed(a.seed)
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    train = load_split(a.task, "train"); test = load_split(a.task, "test")
    n_labels = len(train[0].options)
    tok = AutoTokenizer.from_pretrained(a.init)
    model = AutoModelForSequenceClassification.from_pretrained(a.init, num_labels=n_labels, attn_implementation="sdpa",
                                                               ignore_mismatched_sizes=True).cuda()
    dev = next(model.parameters()).device
    amp = torch.autocast(device_type="cuda", dtype=torch.bfloat16)
    print(f"{a.task}: {len(train)} train / {len(test)} test, {n_labels} labels, init {a.init}", flush=True)

    def enc(recs):
        if a.task in PAIR:
            sts, qs = zip(*[split_record(r) for r in recs])
            e = tok(list(sts), list(qs), truncation="only_first", max_length=a.max_len, padding=True, return_tensors="pt")
        else:
            e = tok([r.text for r in recs], truncation=True, max_length=a.max_len, padding=True, return_tensors="pt")
        return {k: v.to(dev) for k, v in e.items()}

    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    steps = math.ceil(len(train) / a.batch_size) * a.epochs
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / max(1, int(0.06 * steps))) * max(0.0, (steps - s) / steps))
    for ep in range(a.epochs):
        random.shuffle(train); model.train(); t0 = time.time()
        for i in range(0, len(train), a.batch_size):
            ch = train[i:i + a.batch_size]
            with amp:
                logits = model(**enc(ch)).logits
            loss = torch.nn.functional.cross_entropy(logits.float(), torch.tensor([r.answer for r in ch], device=dev))
            opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
        print(f"== epoch {ep} done ({time.time()-t0:.0f}s) ==", flush=True)

    model.eval(); y, pr, rows, dump = [], [], [], []
    with torch.no_grad(), amp:
        for i in range(0, len(test), 32):
            ch = test[i:i + 32]
            p = torch.softmax(model(**enc(ch)).logits.float(), -1).tolist()
            for r, q in zip(ch, p):
                top = max(range(len(q)), key=q.__getitem__); y.append(r.answer); pr.append(top); rows.append((q[top], int(top == r.answer)))
                dump.append({"task": a.task, "idx": item_key(r), "gold": r.answer, "pred": top, "conf": q[top], "hit": int(top == r.answer)})
        cases = to_cases(test)[:128]; torch.cuda.synchronize(); t0 = time.perf_counter()
        for _, recs in cases:
            model(**enc(recs))
        torch.cuda.synchronize(); ms_case = 1000 * (time.perf_counter() - t0) / len(cases)
    acc = sum(h for _, h in rows) / len(rows)
    res = {"acc": acc, "macro_f1": macro_f1(y, pr), "ece": _ece(rows), "ms_per_case": ms_case,
           "q_per_case": sum(len(r) for _, r in cases) / len(cases)}
    md = [f"# {a.task} — standard classifier baseline ({a.init}, {a.epochs} epochs)", "",
          f"accuracy **{acc*100:.2f}%**, macro-F1 {res['macro_f1']*100:.1f}, ECE-10 {res['ece']:.4f} (n={len(rows)})",
          f"latency: {ms_case:.2f} ms per case ({res['q_per_case']:.2f} questions/case, one pass per question)"]
    if a.task == "multirc":
        tp = sum(1 for u, v in zip(y, pr) if u == 1 and v == 1); fp = sum(1 for u, v in zip(y, pr) if u == 0 and v == 1)
        fn = sum(1 for u, v in zip(y, pr) if u == 1 and v == 0)
        byq = {}
        for r, u, v in zip(test, y, pr):
            byq.setdefault(r.meta["qid"], []).append(u == v)
        res.update({"f1a": 2 * tp / max(2 * tp + fp + fn, 1), "em": sum(all(v) for v in byq.values()) / max(len(byq), 1)})
        md.append(f"official: F1a {res['f1a']*100:.1f}, EM {res['em']*100:.1f} ({len(byq)} questions)")
    res.update({"lr": a.lr, "seed": a.seed})
    if a.eval_dev:
        dv = load_split(a.task, "val"); hit = 0
        with torch.no_grad(), amp:
            for i in range(0, len(dv), 32):
                ch = dv[i:i + 32]
                top = model(**enc(ch)).logits.float().argmax(-1).tolist()
                hit += sum(int(t == r.answer) for t, r in zip(top, ch))
        res["dev_acc"] = hit / len(dv); md.append(f"dev accuracy {res['dev_acc']*100:.2f}% (n={len(dv)}, monitoring split)")
    open(a.out, "w").write("\n".join(md) + "\n"); json.dump(res, open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print("\n".join(md))
    if a.dump_preds:
        with open(a.dump_preds, "w") as f:
            for r in dump:
                f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()

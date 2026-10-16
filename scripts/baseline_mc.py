"""Standard multiple-choice baseline for RACE: ModernBertForMultipleChoice, one (article, question+option)
sequence per option, [CLS] -> linear -> softmax over options. Same initialization and epochs as Verdict-MQ,
so the comparison isolates the architecture. Reports test accuracy, ECE and latency per question/article.

  python3 scripts/baseline_mc.py --init tasksource/ModernBERT-base-nli --task race --epochs 2 --out RESULTS_race_mc.md
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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--init", default="tasksource/ModernBERT-base-nli")
    ap.add_argument("--task", default="race")
    ap.add_argument("--epochs", type=int, default=2)
    ap.add_argument("--batch-questions", type=int, default=4)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--max-len", type=int, default=1024)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="RESULTS_race_mc.md")
    ap.add_argument("--dump-preds", default=None)
    ap.add_argument("--eval-dev", action="store_true", help="also score the monitoring split (for lr selection)")
    a = ap.parse_args()
    random.seed(a.seed); torch.manual_seed(a.seed)
    from transformers import AutoModelForMultipleChoice, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(a.init)
    model = AutoModelForMultipleChoice.from_pretrained(a.init, attn_implementation="sdpa",
                                                       ignore_mismatched_sizes=True).cuda()   # NLI inits carry a 3-way head
    dev = next(model.parameters()).device
    amp = torch.autocast(device_type="cuda", dtype=torch.bfloat16)
    train = [r for r in load_split(a.task, "train", limit=a.limit) if 0 <= r.answer < len(r.options)]
    test = [r for r in load_split(a.task, "test") if 0 <= r.answer < len(r.options)]
    print(f"{a.task}: {len(train)} train / {len(test)} test questions; init {a.init}", flush=True)

    def enc(recs):
        firsts, seconds, n = [], [], len(recs[0].options)
        for r in recs:
            state, q = split_record(r)
            for o in r.options:
                firsts.append(state); seconds.append(f"{q} {o}")
        e = tok(firsts, seconds, truncation="only_first", max_length=a.max_len, padding=True, return_tensors="pt")
        return {k: v.view(len(recs), n, -1).to(dev) for k, v in e.items()}

    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=0.01)
    steps = math.ceil(len(train) / a.batch_questions) * a.epochs
    sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / max(1, int(0.06 * steps))) * max(0.0, (steps - s) / steps))
    for ep in range(a.epochs):
        random.shuffle(train); model.train(); t0 = time.time(); run = 0.0
        for i in range(0, len(train), a.batch_questions):
            ch = train[i:i + a.batch_questions]
            with amp:
                logits = model(**enc(ch)).logits
            loss = torch.nn.functional.cross_entropy(logits.float(), torch.tensor([r.answer for r in ch], device=dev))
            opt.zero_grad(); loss.backward(); torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step(); sched.step()
            run += loss.item(); s = i // a.batch_questions + 1
            if s % 500 == 0:
                print(f"  e{ep} step{s} loss={run/s:.4f} {s*a.batch_questions/(time.time()-t0):.1f} q/s", flush=True)
        print(f"== epoch {ep} done ({time.time()-t0:.0f}s) ==", flush=True)

    model.eval(); rows, dump = [], []
    with torch.no_grad(), amp:
        for i in range(0, len(test), 16):
            ch = test[i:i + 16]
            p = torch.softmax(model(**enc(ch)).logits.float(), -1)
            for r, pr in zip(ch, p.tolist()):
                top = max(range(len(pr)), key=pr.__getitem__); rows.append((pr[top], int(top == r.answer)))
                dump.append({"task": a.task, "idx": item_key(r), "gold": r.answer, "pred": top, "conf": pr[top], "hit": int(top == r.answer)})
        # latency: per article, all of its questions, the standard way (one sequence per option)
        cases = to_cases(test)[:128]; torch.cuda.synchronize(); t0 = time.perf_counter()
        for _, recs in cases:
            model(**enc(recs))
        torch.cuda.synchronize(); ms_case = 1000 * (time.perf_counter() - t0) / len(cases)
    acc = sum(h for _, h in rows) / len(rows)
    qpc = sum(len(r) for _, r in cases) / len(cases)
    md = [f"# {a.task.upper()} — standard multiple-choice baseline ({a.init}, {a.epochs} epochs, max_len {a.max_len})", "",
          f"test accuracy **{acc*100:.2f}%** (n={len(rows)}), ECE-10 {_ece(rows):.4f}", "",
          f"latency: {ms_case:.1f} ms per article ({qpc:.2f} questions, one sequence per option, batch = one article), "
          f"{ms_case/qpc:.1f} ms per question"]
    open(a.out, "w").write("\n".join(md) + "\n"); print("\n".join(md))
    res = {"acc": acc, "ece": _ece(rows), "ms_per_article": ms_case, "q_per_article": qpc, "lr": a.lr, "seed": a.seed}
    if a.eval_dev:
        dv = [r for r in load_split(a.task, "val") if 0 <= r.answer < len(r.options)]; hit = 0
        with torch.no_grad(), amp:
            for i in range(0, len(dv), 16):
                ch = dv[i:i + 16]
                top = model(**enc(ch)).logits.float().argmax(-1).tolist()
                hit += sum(int(t == r.answer) for t, r in zip(top, ch))
        res["dev_acc"] = hit / len(dv); print(f"dev accuracy {res['dev_acc']*100:.2f}% (n={len(dv)})")
    json.dump(res, open(a.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    if a.dump_preds:
        with open(a.dump_preds, "w") as f:
            for r in dump:
                f.write(json.dumps(r) + "\n")


if __name__ == "__main__":
    main()

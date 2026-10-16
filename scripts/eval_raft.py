"""External anchor on RAFT (Alex et al. 2021, arXiv:2109.14076; HF `ought/raft`).

RAFT = 11 real-world text classification tasks with exactly 50 labeled training
examples each and a hidden-label test set scored on the leaderboard. Published
anchors (RAFT Table 2, macro-F1 avg over tasks): human 0.735, GPT-3 175B
few-shot 0.627, majority 0.331.

This adapter (a) fits one Verdict per task on the 50 labeled examples as a
Choice over the class names, (b) reports 5-fold cross-validated accuracy /
macro-F1 on those 50 (the only labels we can score locally — a noisy
proxy, NOT the leaderboard number), and (c) writes leaderboard-format
predictions `raft_preds/<task>.csv` (columns ID,Label) for submission.

  python3 scripts/eval_raft.py --out RESULTS_raft.md --epochs 10
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import sys

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Choice, Verdict  # noqa: E402

RAFT_TASKS = ["ade_corpus_v2", "banking_77", "terms_of_service", "tai_safety_research",
              "neurips_impact_statement_risks", "overruling", "systematic_review_inclusion",
              "one_stop_english", "tweet_eval_hate", "twitter_complaints", "semiconductor_org_types"]

PROMPTS = {  # one plain-language framing per task (mirrors the RAFT task descriptions)
    "ade_corpus_v2": "Does this sentence describe an adverse drug event?",
    "banking_77": "Which banking intent does this customer query express?",
    "terms_of_service": "Is this terms-of-service clause potentially unfair to the consumer?",
    "tai_safety_research": "Is this paper transformative-AI safety research?",
    "neurips_impact_statement_risks": "Does this NeurIPS impact statement mention a harmful application?",
    "overruling": "Does this legal sentence overrule a previous decision?",
    "systematic_review_inclusion": "Should this paper be included in the systematic review?",
    "one_stop_english": "What reading level is this text written at?",
    "tweet_eval_hate": "Is this tweet hate speech?",
    "twitter_complaints": "Is this tweet a complaint?",
    "semiconductor_org_types": "What type of organization is this?",
}


def _text(ex, skip):
    return "\n".join(f"{k}: {v}" for k, v in ex.items() if k not in skip and v not in (None, ""))


def load_task(name):
    from datasets import load_dataset
    ds = load_dataset("ought/raft", name)
    names = ds["train"].features["Label"].names  # names[0] == "Unlabeled"
    classes = names[1:]
    skip = {"ID", "Label"}
    train = [(_text(ex, skip), int(ex["Label"]) - 1) for ex in ds["train"]]
    test = [(int(ex["ID"]), _text(ex, skip)) for ex in ds["test"]]
    return classes, train, test


def fit(model, classes, prompt, train, epochs, lr, seed):
    torch.manual_seed(seed); random.seed(seed)
    opt = torch.optim.AdamW(model.parameters(), lr=lr)
    model.train()
    for _ in range(epochs):
        random.shuffle(train)
        for i in range(0, len(train), 8):
            ch = train[i:i + 8]
            qs = [Choice(f"{prompt}\n\n{t}", classes) for t, _ in ch]
            lgs = model.logits_batch(qs)
            loss = sum(torch.nn.functional.cross_entropy(lg.float().unsqueeze(0), torch.tensor([y], device=lg.device))
                       for lg, (_, y) in zip(lgs, ch)) / len(ch)
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0); opt.step()
    model.eval()


@torch.no_grad()
def predict(model, classes, prompt, texts):
    out = []
    for i in range(0, len(texts), 16):
        qs = [Choice(f"{prompt}\n\n{t}", classes) for t in texts[i:i + 16]]
        out += [d.top for d in model.predict_batch(qs)]
    return out


def macro_f1(y, p, k):
    f = []
    for c in range(k):
        tp = sum(1 for a, b in zip(y, p) if a == c and b == c)
        fp = sum(1 for a, b in zip(y, p) if a != c and b == c)
        fn = sum(1 for a, b in zip(y, p) if a == c and b != c)
        if tp + fp + fn == 0:
            continue
        pr = tp / (tp + fp) if tp + fp else 0.0; rc = tp / (tp + fn) if tp + fn else 0.0
        f.append(2 * pr * rc / (pr + rc) if pr + rc else 0.0)
    return sum(f) / len(f) if f else 0.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default=",".join(RAFT_TASKS))
    ap.add_argument("--backbone", default="answerdotai/ModernBERT-base")
    ap.add_argument("--epochs", type=int, default=10)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--folds", type=int, default=5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--pred-dir", default="raft_preds")
    ap.add_argument("--out", default="RESULTS_raft.md")
    args = ap.parse_args()
    os.makedirs(args.pred_dir, exist_ok=True)

    rows, res = [], {}
    for task in args.tasks.split(","):
        classes, train, test = load_task(task)
        prompt = PROMPTS.get(task, "Classify this item.")
        rng = random.Random(args.seed); idx = list(range(len(train))); rng.shuffle(idx)
        folds = [idx[i::args.folds] for i in range(args.folds)]
        y_all, p_all = [], []
        for f in range(args.folds):
            te = set(folds[f])
            tr = [train[i] for i in idx if i not in te]
            model = Verdict.from_pretrained(args.backbone)
            fit(model, classes, prompt, list(tr), args.epochs, args.lr, args.seed)
            p = predict(model, classes, prompt, [train[i][0] for i in sorted(te)])
            y_all += [train[i][1] for i in sorted(te)]; p_all += p
            del model; torch.cuda.empty_cache()
        acc = sum(int(a == b) for a, b in zip(y_all, p_all)) / len(y_all)
        f1 = macro_f1(y_all, p_all, len(classes))
        maj = max(range(len(classes)), key=lambda c: sum(1 for _, y in train if y == c))
        maj_f1 = macro_f1(y_all, [maj] * len(y_all), len(classes))
        # final model on all 50 -> leaderboard predictions
        model = Verdict.from_pretrained(args.backbone)
        fit(model, classes, prompt, list(train), args.epochs, args.lr, args.seed)
        preds = predict(model, classes, prompt, [t for _, t in test])
        with open(os.path.join(args.pred_dir, f"{task}.csv"), "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["ID", "Label"])
            for (i, _), p in zip(test, preds):
                w.writerow([i, classes[p]])
        del model; torch.cuda.empty_cache()
        res[task] = {"classes": len(classes), "cv_acc": acc, "cv_macro_f1": f1, "majority_f1": maj_f1, "n_test": len(test)}
        rows.append(f"| {task} | {len(classes)} | {acc*100:.1f}% | {f1:.3f} | {maj_f1:.3f} | {len(test)} |")
        print(f"{task}: cv_acc={acc:.3f} cv_f1={f1:.3f} maj_f1={maj_f1:.3f} test={len(test)}", flush=True)

    avg_f1 = sum(r["cv_macro_f1"] for r in res.values()) / len(res)
    md = [f"# Verdict on RAFT — 5-fold CV over the 50 labeled examples per task ({args.backbone}, {args.epochs} epochs)", "",
          "NOT leaderboard numbers: RAFT test labels are hidden. Leaderboard-format predictions written to "
          f"`{args.pred_dir}/<task>.csv`. Published RAFT test macro-F1 anchors: human 0.735, GPT-3 175B 0.627, majority 0.331.", "",
          "| task | classes | CV acc | CV macro-F1 | majority macro-F1 | test items |", "|---|---|---|---|---|---|"] + rows
    md += ["", f"**Mean CV macro-F1 over {len(res)} tasks: {avg_f1:.3f}** (40 train / 10 held-out per fold; high variance)."]
    open(args.out, "w").write("\n".join(md) + "\n")
    json.dump(res, open(args.out.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print("\n".join(md))


if __name__ == "__main__":
    main()

"""Combine teacher label files into the org-task training/eval sets, and report
inter-teacher agreement (the no-human-label quality check).

  primary teacher  -> Record.answer        (default qwen3vl32b; train + val)
  check teacher    -> agreement / consensus (default deepseekv32; val)
  original 7B      -> kept in meta.labels as "qwen2.5-7b" for comparison

Writes
  data/jsonl_org/<task>_{train,val}.jsonl       primary-teacher labels, all items
  data/jsonl_orgcons/<task>_{train,val}.jsonl   same train; val = items where
                                                 primary == check (consensus)
  RESULTS_labels.md / .json                     distributions, agreement, Cohen's kappa
                                                 (quadratic-weighted for the 0-3 score)
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter


def key_of(text):
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def read_labels(path):
    if not os.path.isfile(path):
        return {}
    out = {}
    for line in open(path):
        if line.strip():
            r = json.loads(line)
            if r.get("label") is not None:
                out[r["key"]] = int(r["label"])
    return out


def kappa(a, b, k, weighted=False):
    n = len(a)
    if n == 0:
        return float("nan")
    w = [[((i - j) ** 2) / ((k - 1) ** 2) if weighted else float(i != j) for j in range(k)] for i in range(k)]
    obs = [[0] * k for _ in range(k)]
    for x, y in zip(a, b):
        obs[x][y] += 1
    ra = [sum(obs[i]) for i in range(k)]; cb = [sum(obs[i][j] for i in range(k)) for j in range(k)]
    num = sum(w[i][j] * obs[i][j] for i in range(k) for j in range(k)) / n
    den = sum(w[i][j] * ra[i] * cb[j] for i in range(k) for j in range(k)) / n ** 2
    return 1 - num / den if den else float("nan")


def pair_stats(la, lb, k, weighted):
    keys = sorted(set(la) & set(lb))
    a = [la[x] for x in keys]; b = [lb[x] for x in keys]
    agree = sum(x == y for x, y in zip(a, b)) / max(len(keys), 1)
    return {"n": len(keys), "agreement": agree, "kappa": kappa(a, b, k),
            **({"kappa_quadratic": kappa(a, b, k, True)} if weighted else {})}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="email_needs_reply,email_escalate,email_priority")
    ap.add_argument("--in-dir", default="data/jsonl")
    ap.add_argument("--labels-dir", default="data/labels")
    ap.add_argument("--primary", default="qwen3vl32b")
    ap.add_argument("--check", default="deepseekv32")
    ap.add_argument("--out-dir", default="data/jsonl_org")
    ap.add_argument("--cons-dir", default="data/jsonl_orgcons")
    ap.add_argument("--report", default="RESULTS_labels.md")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True); os.makedirs(args.cons_dir, exist_ok=True)
    report = {}
    md = [f"# Org-task labels: {args.primary} (primary) vs {args.check} (independent check) vs qwen2.5-7b (original)", "",
          "No human labels. Quality is measured as agreement between independent strong teachers; the consensus val "
          "subset (primary == check) is the evaluation set of record for the email tasks.", ""]
    for task in args.tasks.split(","):
        rep = {}
        k = None
        for split in ["train", "val"]:
            recs = [json.loads(l) for l in open(os.path.join(args.in_dir, f"{task}_{split}.jsonl")) if l.strip()]
            k = len(recs[0]["options"]); weighted = recs[0]["qtype"] == "score"
            prim = read_labels(os.path.join(args.labels_dir, f"{task}_{split}.{args.primary}.jsonl"))
            chk = read_labels(os.path.join(args.labels_dir, f"{task}_{split}.{args.check}.jsonl"))
            old = {key_of(r["text"]): int(r["answer"]) for r in recs}
            out, cons = [], []
            for r in recs:
                kk = key_of(r["text"])
                if kk not in prim:
                    continue
                labels = {"qwen2.5-7b": old[kk], args.primary: prim[kk]}
                if kk in chk:
                    labels[args.check] = chk[kk]
                r2 = dict(r); r2["answer"] = prim[kk]
                r2["meta"] = dict(r.get("meta") or {}); r2["meta"]["labels"] = labels
                r2["meta"]["judge_model"] = args.primary
                out.append(r2)
                if split == "val" and kk in chk and chk[kk] == prim[kk]:
                    cons.append(r2)
            with open(os.path.join(args.out_dir, f"{task}_{split}.jsonl"), "w") as f:
                for r in out:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            with open(os.path.join(args.cons_dir, f"{task}_{split}.jsonl"), "w") as f:
                for r in (cons if split == "val" else out):
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            rep[split] = {
                "n_records": len(recs), "n_primary": len(out), "n_check": len(chk),
                "n_consensus": len(cons) if split == "val" else None,
                "dist_7b": dict(Counter(old.values())), "dist_primary": dict(Counter(prim.values())),
                "dist_check": dict(Counter(chk.values())),
                "7b_vs_primary": pair_stats(old, prim, k, weighted),
                "7b_vs_check": pair_stats(old, chk, k, weighted) if chk else None,
                "primary_vs_check": pair_stats(prim, chk, k, weighted) if chk else None,
            }
        report[task] = rep
        v, t = rep["val"], rep["train"]
        md += [f"## {task} ({'score 0-3' if k == 4 else 'yes/no'})", "",
               "| pair | split | n | agreement | Cohen's kappa |" + (" quadratic kappa |" if k == 4 else ""),
               "|---|---|---|---|---|" + ("---|" if k == 4 else "")]
        def row(name, split, s):
            if not s:
                return
            md.append(f"| {name} | {split} | {s['n']} | {s['agreement']*100:.1f}% | {s['kappa']:.3f} |" +
                      (f" {s['kappa_quadratic']:.3f} |" if k == 4 else ""))
        row("qwen2.5-7b vs " + args.primary, "train", t["7b_vs_primary"])
        row("qwen2.5-7b vs " + args.primary, "val", v["7b_vs_primary"])
        row("qwen2.5-7b vs " + args.check, "val", v["7b_vs_check"])
        row(f"**{args.primary} vs {args.check}**", "val", v["primary_vs_check"])
        md += ["", f"Label distributions (val): 7B {dict(sorted(v['dist_7b'].items()))}, "
                   f"{args.primary} {dict(sorted(v['dist_primary'].items()))}, {args.check} {dict(sorted(v['dist_check'].items()))}. "
                   f"Train {args.primary}: {dict(sorted(t['dist_primary'].items()))}.",
               f"Consensus val items: **{v['n_consensus']}** of {v['n_primary']}.", ""]
    open(args.report, "w").write("\n".join(md) + "\n")
    json.dump(report, open(args.report.rsplit(".", 1)[0] + ".json", "w"), indent=2)
    print("\n".join(md))


if __name__ == "__main__":
    main()

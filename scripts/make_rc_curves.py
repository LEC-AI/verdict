"""Risk-coverage curve data for the paper figure (pgfplots CSV), from per-decision dumps.
Seeds of one system are pooled. Output columns: coverage, accuracy on covered."""
import json, os, sys

SRC = "results/laptop-latest"
systems = {
    "laya": ["preds_laya_td.jsonl"],
    "mq_base": ["preds_mq_nli_typed.jsonl", "preds_mq_nli_typed-s1.jsonl", "preds_mq_nli_typed-s2.jsonl"],
    "mq_large": [f"preds_stable_s{s}.jsonl" for s in (30, 31, 32, 33, 34)],
}
os.makedirs("paper/figures", exist_ok=True)
for name, files in systems.items():
    rows = []
    for f in files:
        p = os.path.join(SRC, f)
        if os.path.isfile(p):
            rows += [json.loads(l) for l in open(p) if l.strip()]
    if not rows:
        continue
    rows.sort(key=lambda r: -r["conf"]); n = len(rows); hits = 0; pts = []
    for k, r in enumerate(rows, 1):
        hits += r["hit"]
        if k % max(1, n // 200) == 0 or k == n:
            pts.append((k / n, hits / k))
    with open(f"paper/figures/rc_{name}.csv", "w") as fh:
        fh.write("coverage,accuracy\n" + "\n".join(f"{c:.4f},{a:.4f}" for c, a in pts) + "\n")
    print(name, n, "decisions,", len(pts), "points")

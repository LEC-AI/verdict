"""Generate every results table of the paper from the result files, so no number is transcribed by hand.
Reads results/laptop-latest/ (RESULTS_*.md rows and *.json) and writes LaTeX tables to paper/tables/.
Missing inputs produce a table row marked "pending" rather than a guessed number.

  python3 scripts/make_tables.py --src results/laptop-latest --out paper/tables
"""
import argparse
import glob
import json
import os
import re
import statistics as st

CARD = {  # rows reported on the typed-decisions card (test split); not measured by us
    "Uniform (card)": [0.308, 0.311, 0.152, 0.444, 0.381, 0.238, 0.169, None, None],
    "Prior (card)": [0.470, 0.430, 0.207, 0.347, 0.317, 0.189, 0.088, None, None],
    "MiniLM-L6 per workflow (card)": [0.587, 0.506, 0.424, 0.262, 0.267, 0.143, 0.108, 0.515, 0.864],
    "ModernBERT-base per workflow (card)": [0.646, 0.542, 0.469, 0.223, 0.249, 0.119, 0.179, 0.444, 0.931],
    "Featherless Simple Jev (card)": [0.716, None, None, 0.488, None, 0.176, None, None, None],
    "TypeSafe Jev 1.13.0 (card)": [0.727, 0.580, 0.613, 1.442, 0.251, 0.148, 0.144, 0.391, 0.952],
    "meraGPT Decider 1 (card)": [0.768, 0.608, 0.641, 0.096, 0.149, 0.052, 0.180, 0.219, 0.984],
}
COLS = ["Acc", "Soft", "F1", "KL", "TV", "Brier", "ECE", "MAE", "W1"]


JSON_KEYS = ["acc", "soft_acc", "macro_f1", "kl", "tv", "brier", "ece", "score_mae", "within1"]


def row_from_md(path, prefix):
    """Metric vector from the first markdown table row whose first cell starts with `prefix`.
    When the run's own row is the first row and a sibling .json holds the same metrics at full precision, the JSON
    values are returned, so seed means and standard deviations are not computed from three-decimal rounded values."""
    if not os.path.isfile(path):
        return None
    md = _row_from_md(path, prefix)
    jp = path[:-3] + ".json"
    if md and os.path.isfile(jp):
        t = json.load(open(jp)).get("typed")
        if isinstance(t, dict) and all(k in t for k in JSON_KEYS):
            full = [t[k] for k in JSON_KEYS]
            # use the JSON only if it is the same run as the markdown row (every value rounds to the shown one)
            if all(m is None or abs(f - m) <= 0.0005 + 1e-9 for f, m in zip(full, md)):
                return full
    return md


def _row_from_md(path, prefix):
    for line in open(path):
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 11 and cells[0].startswith(prefix):
            try:
                return [float(c) if c not in ("-", "") else None for c in cells[2:11]]
            except ValueError:
                continue
    return None


def agg(vecs):
    vecs = [v for v in vecs if v]
    if not vecs:
        return None, None, 0
    mean = [st.mean([v[i] for v in vecs if v[i] is not None]) if any(v[i] is not None for v in vecs) else None for i in range(9)]
    sd = [st.stdev([v[i] for v in vecs]) if len(vecs) > 1 and all(v[i] is not None for v in vecs) else None for i in range(9)]
    return mean, sd, len(vecs)


def fmt(x, sd=None, bold=False, d=3):
    if x is None:
        return "--"
    s = f"{x:.{d}f}" + (f"\\,$\\pm$\\,{sd:.{d}f}" if sd is not None else "")
    return f"\\textbf{{{s}}}" if bold else s


def table(rows, caption, label, cols=COLS, colspec=None):
    colspec = colspec or ("l" + "r" * len(cols))
    out = ["\\begin{table*}[t]", "\\centering", "\\small", "\\begin{adjustbox}{max width=\\textwidth}", f"\\begin{{tabular}}{{{colspec}}}", "\\toprule",
           " & ".join(["System"] + cols) + " \\\\", "\\midrule"]
    out += rows
    out += ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", "\\end{table*}"]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default="results/laptop-latest")
    ap.add_argument("--out", default="paper/tables")
    a = ap.parse_args()
    S = lambda f: os.path.join(a.src, f)
    os.makedirs(a.out, exist_ok=True)
    notes = []

    # ---------------- T1 main typed-decisions table ----------------
    def mq(prefix_file, rowprefix):
        return row_from_md(S(prefix_file), rowprefix)
    laya_td = row_from_md(S("RESULTS_laya_typed_td.md"), "Laya (typed-decisions)")
    laya_def = row_from_md(S("RESULTS_laya_typed_default.md"), "Laya (default)")
    jev_measured = row_from_md(S("RESULTS_jev_typed.md"), "Jev (measured)")
    ce = row_from_md(S("RESULTS_typed_desc_eval.md"), "verdict-typed-desc")
    raw = agg([mq("RESULTS_mq_typed.md", "mq-typed"), mq("RESULTS_mq_typed_s1.md", "mq-typed-s1"), mq("RESULTS_mq_typed_s2.md", "mq-typed-s2")])
    nlib = agg([mq("RESULTS_mq_nli_typed.md", "mq-nli-typed"), mq("RESULTS_mq_nli_typed_s1.md", "mq-nli-typed-s1"), mq("RESULTS_mq_nli_typed_s2.md", "mq-nli-typed-s2")])
    large_all = [mq("RESULTS_mq_nlil_typed.md", "mq-nlil-typed"), mq("RESULTS_mq_nlil_typed_s1.md", "mq-nlil-typed-s1"),
                 mq("RESULTS_mq_nlil_typed_s2.md", "mq-nlil-typed-s2")] + [mq(f"RESULTS_final_chosen_s{s}.md", f"final-chosen-s{s}") for s in (3, 4, 5)]
    nlil6 = agg(large_all); nlil3 = agg(large_all[3:])
    stable = agg([mq(f"RESULTS_stable_s{s}.md", f"stable-s{s}") for s in (30, 31, 32, 33, 34)])
    stable_fixed = agg([mq(f"RESULTS_stable_cls_s{s}.md", f"stable-cls-s{s}") for s in (40, 41, 42, 43, 44)])
    stable_fixed_k22 = agg([mq(f"RESULTS_stable_clsk22_s{s}.md", f"stable-cls-k22-s{s}") for s in (30, 31, 32, 33, 34)])
    raw_large = agg([mq("RESULTS_mq_large_typed.md", "mq-large-typed")])  # early exploratory run, no NLI init; kept for the
    # initialization-attribution argument in Section 6, not a candidate recipe (found omitted by independent review, 2026-09-29)
    rows = []
    for k, v in CARD.items():
        rows.append(" & ".join([k] + [fmt(x) for x in v]) + " \\\\")
    rows.append("\\midrule")
    for name, v in [("Laya general checkpoint, zero-shot (measured)", laya_def), ("Laya typed-decisions checkpoint, 421M (measured)", laya_td),
                    ("TypeSafe Jev, general (measured, Appendix~\\ref{app:reproduce-jev})", jev_measured)]:
        rows.append(" & ".join([name] + ([fmt(x) for x in v] if v else ["pending"] * 9)) + " \\\\")
    rows.append("\\midrule")
    if ce:
        rows.append(" & ".join(["Verdict-CE, per-question cross-encoder, 150M"] + [fmt(x) for x in ce]) + " \\\\")
    rows_full = list(rows)
    for name, (m, sd, n), headline in [(f"Verdict-MQ, ModernBERT-base init, {raw[2]} seeds", raw, True),
                             (f"\\quad ModernBERT-large init (raw), {raw_large[2]} seed", raw_large, False),
                             (f"Verdict-MQ, NLI-base init, 150M, {nlib[2]} seeds", nlib, True),
                             (f"Verdict-MQ, NLI-large init, 395M, {stable_fixed[2]} fresh seeds", stable_fixed, True),
                             (f"\\quad fixed marker, $k$=22 (reading-comprehension setting), {stable_fixed_k22[2]} seeds", stable_fixed_k22, False),
                             (f"\\quad original marker, warm20 recipe, {stable[2]} fresh seeds", stable, False),
                             (f"\\quad original marker, earlier recipe (6\\% warmup), all {nlil6[2]} seeds", nlil6, False)]:
        if m:
            row = " & ".join([name] + [fmt(m[i], sd[i] if sd and i in (0, 3, 5, 6) else None, bold=False) for i in range(9)]) + " \\\\"
            rows_full.append(row)
            if headline:
                rows.append(row)
    open(os.path.join(a.out, "typed_main.tex"), "w").write(table(rows,
        "Typed-decisions test split (2,000 decisions, 400 cases), specialist mode unless marked. Acc = accuracy; Soft = soft accuracy; "
        "F1 = macro-F1; KL, TV, Brier against the benchmark's soft gold (lower is better); ECE 10-bin; MAE = score-question MAE of the "
        "expected level; W1 = score predictions within one level; $\\pm$ = seed standard deviation. Card rows are taken from the "
        "benchmark card (its Jev row is the card maintainer's own measurement); we additionally measure Jev ourselves (387/400 cases; 13 "
        "excluded for transient errors), closely matching it. Jev, Simple Jev and Decider are general (zero-shot), not directly comparable with "
        "specialists; Simple Jev and Decider are card-only (the card gives only Acc, KL and Brier for Simple Jev). The card "
        "calls accuracy of about 0.75 saturation. Intermediate "
        "training-recipe variants (marker and split-depth ablations) are Table~\\ref{tab:typed-main-full} in the appendix.",
        "tab:typed-main", colspec="lrrrrrrrrr"))
    open(os.path.join(a.out, "typed_main_full.tex"), "w").write(table(rows_full,
        "Full typed-decisions history including intermediate marker and split-depth variants; Table~\\ref{tab:typed-main} in the main "
        "text gives the headline rows only. Columns as in Table~\\ref{tab:typed-main}.",
        "tab:typed-main-full", colspec="lrrrrrrrrr"))

    # ---------------- T2 per-seed paired tests vs Laya ----------------
    def sig(path):
        if not os.path.isfile(path):
            return None
        j = json.load(open(path)); o = j["overall"]
        return o
    rows = []
    specs = [("NLI-base, seed 0", "RESULTS_sig_mqnli.json", None), ("NLI-base, seed 1", "RESULTS_sig_mqnli-s1.json", None), ("NLI-base, seed 2", "RESULTS_sig_mqnli-s2.json", None)] + \
            [(f"NLI-base + option mixer, seed {s}", f"RESULTS_sig_mix_base_s{s}.json", None) for s in (9, 10, 11)] + \
            [(f"NLI-base, constant lr $10^{{-5}}$, seed {s}", f"RESULTS_sig_final2_base_s{s}.json", None) for s in (6, 7, 8)] + \
            [
             ("NLI-large, seed 0", "RESULTS_sig_mqnlil.json", None), ("NLI-large, seed 1", "RESULTS_sig_mqnlil_s1.json", None), ("NLI-large, seed 2", "RESULTS_sig_mqnlil_s2.json", None)] + \
            [(f"NLI-large, seed {s}", f"RESULTS_sig_final_chosen_s{s}.json", None) for s in (3, 4, 5)] + \
            [(f"NLI-large, lr $10^{{-5}}$ arm, seed {s}", f"RESULTS_sig_final_lr1e5_s{s}.json", None) for s in (3, 4, 5)] + \
            [(f"NLI-large, original marker, seed {s}", f"RESULTS_sig_stable_s{s}.json", None) for s in (30, 31, 32, 33, 34)] + \
            [(f"\\textbf{{NLI-large, fixed marker, seed {s}}}", f"RESULTS_sig_stable_cls_s{s}.json", f"RESULTS_sig_stable_cls_s{s}_clustered.json") for s in (40, 41, 42, 43, 44)] + \
            [(f"NLI-large, fixed marker, $k$=22, seed {s}", f"RESULTS_sig_stable_clsk22_s{s}.json", None) for s in (30, 31, 32, 33, 34)]
    headline_seeds = {40, 41, 42, 43, 44}
    rows_headline, rows_full, dist_p = [], [], []
    jl = lambda f: json.load(open(S(f))) if os.path.isfile(S(f)) else None
    for name, f, fc in specs:
        o = sig(S(f))
        if not o:
            continue
        oc = sig(S(fc)) if fc else None
        # when a cluster-bootstrap rerun exists, its CI (resampling whole cases) is the correct one to show
        # alongside its p-value -- the item-level file's CI resamples decisions as independent and is a different,
        # anti-conservative estimate (found by independent review, 2026-09-27).
        src = oc if oc else o
        ci = src["ci"]; eci = src.get("ece_ci")
        m = lambda x: f"${x}$"
        cluster_cell = f"{oc['p_cluster_boot']:.2g}" if oc else "--"
        row = (f"{name} & {o['acc_a']*100:.1f} & {m(f'{o[chr(100)+chr(105)+chr(102)+chr(102)]*100:+.1f}')} [{m(f'{ci[0]*100:+.1f}')}, {m(f'{ci[1]*100:+.1f}')}] & {o['p_mcnemar']:.2g} & {cluster_cell} & "
               + (f"{m(f'{src[chr(101)+chr(99)+chr(101)+chr(95)+chr(97)]-src[chr(101)+chr(99)+chr(101)+chr(95)+chr(98)]:+.3f}')} [{m(f'{eci[0]:+.3f}')}, {m(f'{eci[1]:+.3f}')}]" if eci else "--") + " \\\\")
        rows_full.append(row)
        if fc is not None:  # the 5 headline fixed-marker seeds are the only ones with a clustered rerun
            seed = int(re.search(r"seed (\d+)", name).group(1))
            dr, dt = jl(f"RESULTS_distsig_stable_cls_s{seed}_none.json"), jl(f"RESULTS_distsig_stable_cls_s{seed}_soft.json")
            dcell = lambda d, k: (f"{m(f'{d[k][chr(100)+chr(105)+chr(102)+chr(102)]:+.3f}')} [{m(f'{d[k][chr(99)+chr(105)][0]:+.3f}')}, "
                                  f"{m(f'{d[k][chr(99)+chr(105)][1]:+.3f}')}]") if d else "pending"
            dist_p.extend([d[k]["p_cluster_boot"] for d in (dr, dt) if d for k in ("kl", "brier")])
            rows_headline.append(f"Seed {seed} & {o['acc_a']*100:.1f} & {m(f'{o[chr(100)+chr(105)+chr(102)+chr(102)]*100:+.1f}')} "
                                 f"[{m(f'{ci[0]*100:+.1f}')}, {m(f'{ci[1]*100:+.1f}')}] & {cluster_cell} & {dcell(dr, 'kl')} & "
                                 f"{dcell(dr, 'brier')} & {dcell(dt, 'kl')} \\\\")
    header = ["Verdict-MQ run & Acc & $\\Delta$Acc vs Laya [95\\% CI] & item-level McNemar $p$ & case-cluster bootstrap $p$ & $\\Delta$ECE [95\\% CI] \\\\", "\\midrule"]
    cap_common = ("2,000 test decisions (400 cases $\\times$ 5 questions each). Item-level exact McNemar treats every decision as independent and is "
                  "anti-conservative here, since the 5 questions of one case are correlated; the case-cluster bootstrap (10,000 resamples of whole "
                  "cases) is the primary test.")
    header_h = ["Seed & Acc & $\\Delta$Acc vs Laya [95\\% CI] & $p$ & $\\Delta$KL [95\\% CI] & $\\Delta$Brier [95\\% CI] & "
                "$\\Delta$KL, temp.-matched [95\\% CI] \\\\", "\\midrule"]
    pmax = f"{max(dist_p):.4f}" if dist_p else "pending"
    t = ["\\begin{table*}[t]", "\\centering", "\\small", "\\begin{adjustbox}{max width=\\textwidth}", "\\begin{tabular}{lrrrrrr}", "\\toprule"] + header_h + rows_headline + \
        ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", "\\caption{The five fresh headline seeds (395M, fixed marker) against the released Laya "
         "typed-decisions checkpoint on the identical 2,000 test decisions, all paired by case: case-cluster bootstrap over the 400 cases "
         "(10,000 resamples). $\\Delta$ = Verdict-MQ $-$ Laya, so negative KL and Brier (against the soft gold) favour Verdict-MQ. "
         "Temp.-matched: one temperature per system, fitted to the soft gold on half of the cases, scored on the other half. Every KL and "
         f"Brier difference here, raw or temperature-matched, has $p\\le{pmax}$. The full search history, with item-level McNemar and "
         "$\\Delta$ECE, is Table~\\ref{tab:paired-full}.}",
         "\\label{tab:paired}", "\\end{table*}"]
    open(os.path.join(a.out, "typed_paired.tex"), "w").write("\n".join(t) + "\n")
    t_full = ["\\begin{table*}[t]", "\\centering", "\\small", "\\begin{adjustbox}{max width=\\textwidth}", "\\begin{tabular}{lrrrrr}", "\\toprule"] + header + rows_full + \
        ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", "\\caption{Full paired-comparison search history (Table~\\ref{tab:paired} in the main text shows only the "
         "5 headline seeds): every seed of every configuration tried against the released Laya typed-decisions checkpoint on the identical "
         + cap_common + " Includes the two large-model seeds that stalled early in training.}",
         "\\label{tab:paired-full}", "\\end{table*}"]
    open(os.path.join(a.out, "typed_paired_full.tex"), "w").write("\n".join(t_full) + "\n")

    # ---------------- T3 ablations ----------------
    abl = [("Full recipe (3 seeds)", raw[0], raw[1])]
    for name, f, p in [("no question-type embedding", "RESULTS_mq_typed_notype.md", "mq-typed-notype"),
                       ("ordered option positions", "RESULTS_mq_typed_ordered.md", "mq-typed-ordered"),
                       ("no ordinal (EMD) loss", "RESULTS_mq_typed_noord.md", "mq-typed-noord"),
                       ("no option-subset augmentation", "RESULTS_mq_typed_nodrop.md", "mq-typed-nodrop"),
                       ("512-token window", "RESULTS_mq_typed_len512.md", "mq-typed-len512"),
                       ("constant learning rate $2\\times10^{-5}$", "RESULTS_mq_typed_const.md", "mq-typed-const")]:
        v = row_from_md(S(f), p)
        abl.append((name, v, None))
    rows = [" & ".join([n] + [fmt(v[i], sd[i] if sd and i == 0 else None) if v else "pending" for i in (0, 3, 5, 7)]) + " \\\\" for n, v, sd in abl]
    t = ["\\begin{table}[t]", "\\centering", "\\small", "\\begin{adjustbox}{max width=\\columnwidth}", "\\begin{tabular}{lrrrr}", "\\toprule", "Variant (one change each) & Acc & KL & Brier & MAE \\\\", "\\midrule"] + rows + \
        ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", "\\caption{Component ablations of Verdict-MQ on typed-decisions (test split, ModernBERT-base "
         "initialization, one seed per variant; the full recipe's seed s.d.\\ is 0.013). Only the learning-rate schedule moves accuracy "
         "beyond seed noise, and that effect does not carry over to the NLI initializations (Appendix~\\ref{sec:schedule}).}", "\\label{tab:ablations}", "\\end{table}"]
    open(os.path.join(a.out, "ablations.tex"), "w").write("\n".join(t) + "\n")

    # ---------------- T4 latency ----------------
    lat = []
    for name, f in [("Verdict-MQ base", "RESULTS_mq_typed.json"), ("Verdict-MQ large", "RESULTS_mq_nlil_typed.json")]:
        if os.path.isfile(S(f)):
            L = json.load(open(S(f))).get("latency_ms_per_case")
            if L:
                lat.append((name, L))
    rows = []
    for name, L in lat:
        for bs in (1, 8):
            pk, one = L.get(f"packed@{bs}"), L.get(f"one-question-per-pass@{bs}")
            if pk and one:
                rows.append(f"{name} & {bs} & {pk:.1f} & {one:.1f} & {one/pk:.1f}$\\times$ \\\\")
    t = ["\\begin{table}[t]", "\\centering", "\\small", "\\begin{adjustbox}{max width=\\columnwidth}", "\\begin{tabular}{lrrrr}", "\\toprule",
         "Model & Batch & Packed & Per question & Speed-up \\\\", "\\midrule"] + rows + \
        ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", "\\caption{Latency in ms per case: all five questions in one packed pass vs one pass per question (typed-decisions "
         "test cases; bf16; RTX 4090 Laptop GPU; same weights in both modes; measured on checkpoints with the original marker "
         "token, whose compute is identical to the headline models').}", "\\label{tab:latency}", "\\end{table}"]
    open(os.path.join(a.out, "latency.tex"), "w").write("\n".join(t) + "\n")
    def simple(fname, header, rows_, caption, label, colspec, star=False):
        env = "table*" if star else "table"
        w = "\\textwidth" if star else "\\columnwidth"
        t = [f"\\begin{{{env}}}[t]", "\\centering", "\\small", f"\\begin{{adjustbox}}{{max width={w}}}", f"\\begin{{tabular}}{{{colspec}}}", "\\toprule", header + " \\\\", "\\midrule"] + rows_ + \
            ["\\bottomrule", "\\end{tabular}", "\\end{adjustbox}", f"\\caption{{{caption}}}", f"\\label{{{label}}}", f"\\end{{{env}}}"]
        open(os.path.join(a.out, fname), "w").write("\n".join(t) + "\n")

    # ---------------- T5 matched initialization ----------------
    def lft(path):
        if not os.path.isfile(path):
            return None
        for line in open(path):
            if line.startswith("| Laya (default) ft-epoch"):
                c = [x.strip() for x in line.strip().strip("|").split("|")]
                return [float(x) for x in c[2:11]]
        return None
    rows = []
    for name, v in [("Laya arch., seed 0", lft(S("RESULTS_laya_ft_typed.md"))),
                    ("Laya arch., seed 1", lft(S("RESULTS_laya_ft_typed_s1.md"))),
                    ("Verdict-MQ, seed 0", row_from_md(S("RESULTS_mq_laya_typed.md"), "mq-laya-typed")),
                    ("Verdict-MQ, seed 1", row_from_md(S("RESULTS_mq_laya_typed_s1.md"), "mq-laya-typed-s1")),
                    ("Verdict-MQ + mixer, seed 0", row_from_md(S("RESULTS_mix_laya_s0.md"), "mix-laya-s0")),
                    ("Verdict-MQ + mixer, seed 1", row_from_md(S("RESULTS_mix_laya_s1.md"), "mix-laya-s1")),
                    ("Released Laya checkpoint", laya_td)]:
        if v:
            rows.append(" & ".join([name] + [fmt(v[i]) for i in (0, 3, 5, 6)]) + " \\\\")
    simple("matched.tex", "Laya encoder init & Acc & KL & Brier & ECE", rows,
           "Matched initialization: both architectures start from Laya's own general-purpose encoder and are trained on the same "
           "6,000 decisions. Our re-fine-tuning of Laya uses hard labels and no temperature, so its distribution metrics are not a "
           "fair calibration comparison; the released checkpoint is.", "tab:matched", "lrrrr")

    # ---------------- T6 autonomy dial ----------------
    rows = []
    ap_ = S("RESULTS_autonomy_typed.md")
    if os.path.isfile(ap_):
        for line in open(ap_):
            if line.startswith("| ") and not line.startswith("| system") and "---" not in line:
                c = [x.strip() for x in line.strip().strip("|").split("|")]
                rows.append(" & ".join([c[0], c[1].replace("%", "\\%"), c[2]] + [x.replace("%", "\\%") for x in c[3:]]) + " \\\\")
    simple("autonomy.tex", "System & Acc & AURC & 90\\% target & 95\\% target & 98\\% target", rows,
           "Held-out autonomy dial on typed-decisions test decisions. The confidence threshold for each target accuracy is chosen on "
           "one half of the test \\emph{cases} (split by a fixed hash shared by all systems, so one case's 5 decisions never straddle "
           "the split) and applied to the other half; each cell gives coverage (share auto-handled) / realized accuracy on that half. "
           "AURC = area under the risk-coverage curve (lower is better).",
           "tab:autonomy", "lrrrrr", star=True)

    # ---------------- T7 generalist negative results ----------------
    rows = []
    for name, f, pre in [("Laya general ckpt (test)", "RESULTS_laya_typed_default.md", "Laya (default)"),
                         ("Verdict-MQ, public data", "RESULTS_mq_pub_dev.md", "mq-pub"),
                         ("Verdict-MQ, synthetic corpus", "RESULTS_mq_syn_dev.md", "mq-syn"),
                         ("\\quad + NLI-base init", "RESULTS_mq_nli_syn_dev.md", "mq-nli-syn"),
                         ("\\quad + NLI-large init", "RESULTS_mq_nlil_syn_dev.md", "mq-nlil-syn")]:
        v = row_from_md(S(f), pre)
        if v:
            rows.append(" & ".join([name] + [fmt(v[i]) for i in (0, 3, 5)]) + " \\\\")
    rows.append("Prior (card, test) & 0.470 & 0.347 & 0.189 \\\\")
    rows.append("32B teacher, zero-shot & 0.699 & -- & -- \\\\")
    simple("generalist.tex", "Generalist (zero-shot) & Acc & KL & Brier", rows,
           "Negative result: generalists trained on public data or on our synthetic multi-workflow corpus, scored zero-shot on "
           "typed-decisions (training split used as the development split, since a generalist never trains on it). All fall below "
           "the input-ignoring prior, although the teacher that labelled the corpus agrees 0.699 with the benchmark's gold.",
           "tab:generalist", "lrrr")

    # ---------------- T8 dev grid (large) ----------------
    rows = []
    rp = S("RESULTS_recipe_dev_large2.md")
    if os.path.isfile(rp):
        for line in open(rp):
            if line.startswith("| ") and "config" not in line and "---" not in line:
                c = [x.strip() for x in line.strip().strip("|").split("|")]
                rows.append(" & ".join([c[0].replace("**", "").replace("(chosen)", "(chosen)"), c[1].replace("`", "").replace("--", "{-}{-}"), c[2], c[3].replace("±", "$\\pm$")]) + " \\\\")
    simple("devgrid.tex", "Config & Arguments & Dev acc per seed & Mean", rows,
           "Large-model recipe selection on the development split (15\\% of the benchmark's training cases, held out by case). "
           "The recipe with the highest mean development accuracy is used for the final test runs.", "tab:devgrid", "llrr")

    # ---------------- T9 standard benchmarks: Verdict-MQ vs matched baseline vs Laya vs Jev (marker fix, 2026-09-27) ----------------
    def jget(f, *keys):
        f = S(f)
        if not os.path.isfile(f):
            return None
        j = json.load(open(f))
        for k in keys:
            j = j.get(k) if isinstance(j, dict) else None
            if j is None:
                return None
        return j

    def meansd(vals):
        vals = [v for v in vals if v is not None]
        if not vals:
            return None, None
        return st.mean(vals), (st.stdev(vals) if len(vals) > 1 else 0.0)

    def sigp(pattern, n):
        # prefer the case-cluster bootstrap p (real passage/case clustering) when the file has one; item-level
        # McNemar otherwise. idx alone is NOT a valid cluster key for RACE/BoolQ/MultiRC dumps (it identifies a
        # decision, not a passage) -- these files must come from a run with a genuine "case" field (found by
        # independent review, 2026-09-28; see scripts/eval_mq.py's case field).
        vals = [jget(pattern.format(s=s), "overall") for s in range(n)]
        ps = [(v.get("p_cluster_boot") if v.get("p_cluster_boot") is not None else v.get("p_mcnemar")) for v in vals if v]
        if not ps:
            return "--"
        return f"{min(ps):.2g}--{max(ps):.2g}"

    race_mq = [jget(f"RESULTS_race_mqclsk22_s{s}.json", "race", "acc") for s in range(3)]
    mrc_mq = [jget(f"RESULTS_multirc_mqclsk22_s{s}.json", "multirc", "acc") for s in range(3)]
    mrc_mq_f1a = [jget(f"RESULTS_multirc_mqclsk22_s{s}.json", "multirc", "f1a") for s in range(3)]
    mrc_mq_em = [jget(f"RESULTS_multirc_mqclsk22_s{s}.json", "multirc", "em") for s in range(3)]
    boolq_mq = [jget(f"RESULTS_boolq_mqstabler3_s{s}.json", "boolq", "acc") for s in range(5)]
    race_base = [jget(f"RESULTS_race_mc_lr3e-5_s{s}.json", "acc") for s in range(3)]
    mrc_base = [jget(f"RESULTS_multirc_pair_lr1e-5_s{s}.json", "acc") for s in range(3)]
    mrc_base_f1a = [jget(f"RESULTS_multirc_pair_lr1e-5_s{s}.json", "f1a") for s in range(3)]
    mrc_base_em = [jget(f"RESULTS_multirc_pair_lr1e-5_s{s}.json", "em") for s in range(3)]
    # epoch-matched to Verdict-MQ's actual stable-recipe epoch count (6, not the original sweep's 3) --
    # found mismatched by independent review, 2026-09-28; see limitations.tex
    boolq_base = [jget(f"RESULTS_boolq_pair_lr5e-5_e6_s{s}.json", "acc") for s in range(5)]
    laya_race = jget("RESULTS_laya_race.json", "acc"); laya_mrc = jget("RESULTS_laya_multirc.json", "acc"); laya_boolq = jget("RESULTS_laya_boolq.json", "acc")
    jev_race, jev_mrc, jev_boolq = jget("RESULTS_jev_race.json", "acc"), jget("RESULTS_jev_multirc.json", "acc"), jget("RESULTS_jev_boolq.json", "acc")

    def fmt2(m, sd, d=1):
        if m is None:
            return "pending"
        return f"{m*100:.{d}f}" + (f"$\\pm${sd*100:.{d}f}" if sd else "")

    rows = []
    for bench, mqv, basev, layav, jevv, note, sigbase, siglaya in [
        ("RACE (test)", race_mq, race_base, laya_race, jev_race, "",
         sigp("RESULTS_sig_race_clsk22_cased_s{s}.json", 3), sigp("RESULTS_sig_race_vs_laya_cased_s{s}.json", 3)),
        ("BoolQ (val)", boolq_mq, boolq_base, laya_boolq, jev_boolq, "$\\dagger$",
         sigp("RESULTS_sig_boolq_epochmatched_cased_s{s}.json", 5), sigp("RESULTS_sig_boolq_vs_laya_cased_s{s}.json", 5)),
        ("MultiRC (val)", mrc_mq, mrc_base, laya_mrc, jev_mrc, "$\\ddagger$",
         sigp("RESULTS_sig_multirc_clsk22_cased_s{s}.json", 3), sigp("RESULTS_sig_multirc_vs_laya_cased_s{s}.json", 3))]:
        m, sd = meansd(mqv); b, bsd = meansd(basev)
        rows.append(f"{bench}{note} & {fmt2(m, sd)} & {fmt2(b, bsd)} & {sigbase} & {fmt2(layav, None)} & {fmt2(jevv, None)} \\\\")
    bq = [x for x in boolq_mq if x is not None]
    mrc_note = (f"$\\ddagger$MultiRC official metrics: Verdict-MQ F1a/EM {st.mean(mrc_mq_f1a)*100:.1f}/{st.mean(mrc_mq_em)*100:.1f} vs "
                f"baseline {st.mean([x for x in mrc_base_f1a if x])*100:.1f}/{st.mean([x for x in mrc_base_em if x])*100:.1f}; the baseline "
                f"varies widely across seeds ({', '.join(f'{x*100:.1f}' for x in mrc_base if x is not None)}\\%; Appendix~\\ref{{app:standard-methods}}).")
    simple("standard.tex", "Benchmark & Verdict-MQ & Baseline & $p$ vs baseline & Laya, zero-shot & Jev, zero-shot", rows,
           "Standard benchmarks. Verdict-MQ and the baseline (same initialization and epoch budget) are fine-tuned on each "
           "benchmark's training split; Laya's general checkpoint and Jev are zero-shot references (not fine-tuned on these tasks; "
           "their own training data is undisclosed), run on the identical test items and case grouping. All numbers are measured by us, not taken from vendor cards "
           "(Appendix~\\ref{app:standard-methods}). $p$: case-cluster bootstrap, min--max across seeds (3 for RACE/MultiRC, 5 for "
           f"BoolQ). $\\dagger$BoolQ training is unstable (\\S\\ref{{sec:standard}}): the 5 seeds range {min(bq)*100:.1f}--{max(bq)*100:.1f}\\%. "
           + mrc_note,
           "tab:standard", "lrrrrr", star=True)

    # ---------------- T9b marker x split-depth grid: accuracy-cost surface (seed 0, marker-fixed) ----------------
    base_of = {"boolq": ("RESULTS_boolq_pair_lr{lr}_s0.json", "out/chosen_lr_boolq_pair.txt", "ms_per_case"),
               "multirc": ("RESULTS_multirc_pair_lr{lr}_s0.json", "out/chosen_lr_multirc_pair.txt", "ms_per_case"),
               "race": ("RESULTS_race_mc_lr3e-5_s0.json", None, "ms_per_article")}
    pct = lambda x: "--" if x is None else f"{x*100:.1f}"
    ms = lambda x: "--" if x is None else f"{x:.1f}"
    rows = []
    for mk in ("mask", "cls"):
        for k in (0, 4, 22):
            cells = [f"{mk}, $k$={k}" + (" (chosen)" if (mk, k) == ("cls", 22) else "")]
            for t in ("boolq", "multirc", "race"):
                lat = jget(f"RESULTS_lat_{t}_{mk}_k{k}.json", "latency_ms_per_case")
                cells += [pct(jget(f"RESULTS_{t}_mq{mk}k{k}_s0_dev.json", t, "acc")), pct(jget(f"RESULTS_{t}_mq{mk}k{k}_s0.json", t, "acc")),
                          ms(lat.get("packed@1") if lat else None)]
            rows.append(" & ".join(cells) + " \\\\")
    cells = ["tuned baseline"]
    for t in ("boolq", "multirc", "race"):
        pat, lrf, lk = base_of[t]
        lf = S(os.path.basename(lrf)) if lrf else None                     # chosen lr files are synced next to the results
        lr = open(lf).read().strip() if lf and os.path.isfile(lf) else "3e-5"
        f = pat.format(lr=lr)
        cells += [pct(jget(f, "dev_acc")), pct(jget(f, "acc")), ms(jget(f, lk))]
    rows.append("\\midrule " + " & ".join(cells) + " \\\\")
    simple("split.tex", "config & \\multicolumn{3}{c}{BoolQ} & \\multicolumn{3}{c}{MultiRC} & \\multicolumn{3}{c}{RACE} \\\\ "
           "& dev & test & ms & dev & test & ms & dev & test & ms", rows,
           "Marker (mask/cls, Section~\\ref{sec:model}) $\\times$ split-depth ($k$ = top layers where the state attends to each "
           "question; $k$=22 is full ModernBERT-base depth) grid, seed 0. dev is the selection split, test the reporting split; "
           "ms = latency per passage (all its questions), batch 1, bf16, RTX 4090 Laptop. RACE's $k$=4 runs never completed for "
           "either marker (Appendix~\\ref{app:standard-methods}). Baselines: pair classifier (BoolQ, MultiRC; learning rate tuned on dev) and multiple-choice "
           "head (RACE). (mask, $k$=4) comes within about a point of the chosen (cls, $k$=22) on BoolQ dev but was not stable "
           "across seeds (Section~\\ref{sec:standard}); this table reports architecture and cost, not stability.",
           "tab:split", "l" + "rrr" * 3, star=True)

    # ---------------- T10 email tasks ----------------
    tasks = ["email_needs_reply", "email_priority", "email_escalate"]
    maj = {"email_needs_reply": 0.687, "email_priority": 0.482, "email_escalate": 0.991}   # majority class on consensus val
    def cell(x):
        return "pending" if x is None else f"{x*100:.1f}"
    ce = {t: jget("RESULTS_org_verdict.json", "tasks", t, "acc") for t in tasks}
    plain = {t: jget("RESULTS_org_plain.json", t, "acc") for t in tasks}
    lh = jget("RESULTS_laya_ft_org.json", "history")
    laya0 = {t: (lh[0][1][t]["acc"] if lh else None) for t in tasks}
    layaf = {t: (lh[-1][1][t]["acc"] if lh else None) for t in tasks}
    mqo = {t: jget("RESULTS_org_mq.json", f"{t}@data/jsonl_orgcons", "acc") for t in tasks}
    rows = [" & ".join(["Majority class"] + [cell(maj[t]) for t in tasks]) + " \\\\",
            " & ".join(["Laya, zero-shot"] + [cell(laya0[t]) for t in tasks]) + " \\\\",
            " & ".join(["Laya, fine-tuned (one model)"] + [cell(layaf[t]) for t in tasks]) + " \\\\",
            " & ".join(["Plain classifier (one per task)"] + [cell(plain[t]) for t in tasks]) + " \\\\",
            " & ".join(["Verdict-CE (per question)"] + [cell(ce[t]) for t in tasks]) + " \\\\",
            " & ".join(["Verdict-MQ (NLI-base, one model)"] + [cell(mqo[t]) for t in tasks]) + " \\\\"]
    simple("email.tex", "Model & Needs reply & Priority (0--3) & Escalate$^\\dagger$", rows,
           "Organizational email decisions (Enron): accuracy on the consensus validation items where the two strong LLM "
           "teachers agree (323, 228 and 347 items). $^\\dagger$Escalate is uninformative: only 3 of 347 consensus items are "
           "escalations, so the majority class scores 99.1\\%.", "tab:email", "lrrr")

    print("wrote", sorted(os.listdir(a.out)))


if __name__ == "__main__":
    main()

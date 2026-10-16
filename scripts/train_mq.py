"""Train Verdict-MQ ("encode once, decide many") on a mixture of task specs.

  python3 scripts/train_mq.py --tasks synth@data/synth --out out/mq-syn --epochs 3 --batch-cases 8 --soft --bf16
  python3 scripts/train_mq.py --tasks typed_decisions --out out/mq-typed --epochs 6 --soft --bf16
Reports the LAST epoch (no selection on the reported split).
"""
from __future__ import annotations

import argparse
import math
import os
import random
import sys
import time

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict.mq import VerdictMQ, ordinal_emd2  # noqa: E402
from verdict.mq_data import load_split, to_cases  # noqa: E402


def subset_options(case, recs, rng, p):
    """Option-subset augmentation for choice questions (>2 options): keeps gold, renormalizes soft."""
    import copy
    case = copy.deepcopy(case); new = []
    for q, r in zip(case.questions, recs):
        soft = (r.meta or {}).get("soft")
        ans, n = r.answer, len(q.options)
        if q.qtype == "choice" and n > 2 and rng.random() < p:
            k = rng.randint(2, n - 1)
            keep = sorted([ans] + rng.sample([i for i in range(n) if i != ans], k - 1))
            q.options = [q.options[i] for i in keep]
            if soft and len(soft) == n:
                s = [soft[i] for i in keep]; z = sum(s) or 1.0; soft = [x / z for x in s]
            else:
                soft = None
            ans = keep.index(ans)
        new.append((ans, soft if soft and len(soft) == len(q.options) else None))
    return case, new


def case_loss(lgs, targets, qtypes, soft, ordinal, dev):
    ls = []
    for lg, (ans, sv), qt in zip(lgs, targets, qtypes):
        if soft and sv is not None:
            tgt = torch.tensor(sv, device=dev, dtype=torch.float32)
            l = -(tgt * torch.log_softmax(lg.float(), -1)).sum()
        else:
            tgt = torch.nn.functional.one_hot(torch.tensor(ans, device=dev), lg.shape[0]).float()
            l = torch.nn.functional.cross_entropy(lg.float().unsqueeze(0), torch.tensor([ans], device=dev))
        if ordinal and qt == "score":
            l = l + ordinal * ordinal_emd2(lg, tgt)
        ls.append(l)
    return torch.stack(ls).mean()


@torch.no_grad()
def quick_eval(model, cases, bs):
    model.eval(); hit = n = 0
    for i in range(0, len(cases), bs):
        ch = cases[i:i + bs]
        for probs, (_, recs) in zip(model.predict([c for c, _ in ch]), ch):
            for p, r in zip(probs, recs):
                hit += int(max(range(len(p)), key=p.__getitem__) == r.answer); n += 1
    return hit / max(n, 1), n


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True)
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--init", default="answerdotai/ModernBERT-base", help="backbone id or checkpoint dir")
    ap.add_argument("--out", required=True)
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch-cases", type=int, default=8)
    ap.add_argument("--lr", type=float, default=3e-5)
    ap.add_argument("--limit", type=int, default=0, help="max train records per task")
    ap.add_argument("--val-limit", type=int, default=1000)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--soft", action="store_true")
    ap.add_argument("--ordinal", type=float, default=1.0, help="weight of the EMD^2 term on score questions (0 = off)")
    ap.add_argument("--option-dropout", type=float, default=0.3)
    ap.add_argument("--bf16", action="store_true")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--no-type-emb", action="store_true", help="ablation: no question-type embedding")
    ap.add_argument("--ordered-options", action="store_true", help="ablation: consecutive option positions (order visible)")
    ap.add_argument("--schedule", choices=["linear", "constant"], default="linear", help="linear = 6%% warmup + linear decay")
    ap.add_argument("--option-mixer", type=int, default=0, help="layers of permutation-equivariant set attention over option markers")
    ap.add_argument("--warmup-frac", type=float, default=0.06, help="linear warmup as a fraction of total steps")
    ap.add_argument("--llrd", type=float, default=1.0,
                    help="layer-wise LR decay: layer l gets lr * llrd^(L-l); embeddings get the lowest rate; head gets lr")
    ap.add_argument("--joint-layers", type=int, default=0,
                    help="split depth: top k layers where the state attends to each question (0 = fully shared state)")
    ap.add_argument("--grad-ckpt", action="store_true", help="gradient checkpointing (same maths, less memory)")
    ap.add_argument("--readout", choices=["marker", "match", "pool"], default="marker",
                    help="match: [marker; question [SEP]; product]; pool: [marker; mean of state+question; product]")
    ap.add_argument("--marker", choices=["opt", "mask", "cls", "sep"], default="opt",
                    help="option marker token: opt = new [OPT] token (original); mask/cls/sep = reuse an existing special token")
    a = ap.parse_args()
    rng = random.Random(a.seed); torch.manual_seed(a.seed); random.seed(a.seed)

    train, val = [], []
    for t in a.tasks.split(","):
        tr = to_cases(load_split(t, "train", a.cache_dir, a.limit)); va = to_cases(load_split(t, "val", a.cache_dir, 0, a.val_limit))
        print(f"  {t}: {len(tr)} train cases ({sum(len(c.questions) for c, _ in tr)} decisions) / {len(va)} val cases", flush=True)
        train += tr; val += va
    model = VerdictMQ.from_pretrained(a.init, max_len=a.max_len, mixer_layers=a.option_mixer or None,
                                      joint_layers=a.joint_layers, readout=a.readout, marker=a.marker)
    model.max_len = a.max_len
    if a.grad_ckpt:
        model.backbone.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    if a.ordered_options:
        model.shared_option_pos = False
    if a.no_type_emb:
        model.head.type_emb.weight.data.zero_(); model.head.type_emb.weight.requires_grad_(False)
    dev = next(model.parameters()).device
    amp = torch.autocast(device_type=dev.type, dtype=torch.bfloat16, enabled=a.bf16 and dev.type == "cuda")
    if a.llrd < 1.0:
        layers = list(model.backbone.layers); L = len(layers); groups = []
        groups.append({"params": [p for p in model.backbone.embeddings.parameters() if p.requires_grad], "lr": a.lr * a.llrd ** (L + 1)})
        for i, layer in enumerate(layers):
            groups.append({"params": [p for p in layer.parameters() if p.requires_grad], "lr": a.lr * a.llrd ** (L - i)})
        seen = {id(p) for g in groups for p in g["params"]}
        rest = [p for p in model.parameters() if p.requires_grad and id(p) not in seen]      # final norm + head
        groups.append({"params": rest, "lr": a.lr})
        opt = torch.optim.AdamW(groups, lr=a.lr, weight_decay=0.01)
        print(f"LLRD {a.llrd}: layer lrs {groups[1]['lr']:.2e} .. {groups[L]['lr']:.2e}, head {a.lr:.2e}", flush=True)
    else:
        opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=a.lr, weight_decay=0.01)
    steps = math.ceil(len(train) / a.batch_cases) * a.epochs
    if a.schedule == "constant":
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: 1.0)
    else:
        sched = torch.optim.lr_scheduler.LambdaLR(opt, lambda s: min(1.0, (s + 1) / max(1, int(a.warmup_frac * steps))) * max(0.0, (steps - s) / steps))
    print(f"device={dev} train cases={len(train)} val cases={len(val)} steps={steps}", flush=True)
    train_log = []
    for ep in range(a.epochs):
        rng.shuffle(train); model.train(); t0 = time.time(); run = 0.0; nb = 0
        for i in range(0, len(train), a.batch_cases):
            ch = train[i:i + a.batch_cases]
            aug = [subset_options(c, r, rng, a.option_dropout) for c, r in ch]
            with amp:
                lgs = model.logits([c for c, _ in aug])
            loss = torch.stack([case_loss(l, tg, [q.qtype for q in c.questions], a.soft, a.ordinal, dev)
                                for l, (c, tg) in zip(lgs, aug)]).mean()
            opt.zero_grad(); loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); run += loss.item(); nb += 1
            if nb % 100 == 0:
                print(f"  e{ep} step{nb} loss={run/nb:.4f} {nb*a.batch_cases/(time.time()-t0):.1f} cases/s", flush=True)
        with amp:
            acc, n = quick_eval(model, val, a.batch_cases * 2)
        print(f"== epoch {ep}: train loss={run/max(nb,1):.4f} val acc={acc:.4f} (n={n} decisions) ({time.time()-t0:.0f}s) ==", flush=True)
        train_log.append({"epoch": ep, "train_loss": run / max(nb, 1)})
    model.save_pretrained(a.out)
    import json as _json
    _json.dump({"args": vars(a), "epochs": train_log}, open(os.path.join(a.out, "train_log.json"), "w"), indent=2)
    print(f"DONE saved last epoch -> {a.out}", flush=True)


if __name__ == "__main__":
    main()

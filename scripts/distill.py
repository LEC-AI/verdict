"""Distill org-authentic OrgBench labels from an LLM judge.

Takes the UNLABELED items from ``verdict.data_org`` (public Enron email set by
default; ``--corpus-file`` for the leads / finance placeholder families), asks an
instruct LLM — via an OpenAI-compatible endpoint, same request style as
``scripts/eval_baseline.py`` — for the TYPED decision on each item using that
task's rubric, and writes ``verdict.data.Record`` JSONL that ``scripts/train.py``
consumes directly.

For each task it produces, under ``--out-dir`` (default ``data/jsonl``):
  * ``<task>_train.jsonl`` / ``<task>_val.jsonl`` — distilled Records. The split
    is BY ITEM and content-hashed, so an email held out for one email_* task is
    held out for all of them (no cross-task leakage).
  * ``audit/<task>_audit.csv`` — a random ``--audit N`` subset with a BLANK
    ``human_label`` column, so a human can later score judge-label quality.
  * ``<task>.distill.json`` — sidecar: judge model id, endpoint, UTC date, the
    exact judge instruction/rubric, corpus id, counts + label distribution,
    seed. Plus a combined ``distill_run.json`` manifest for the whole run.

The judge is asked to answer with ONLY the option index (temperature 0);
replies that don't parse to a valid index are dropped and counted (an
unparseable label is unusable), as in eval_baseline.

Run:

  python3 scripts/distill.py \
      --tasks email_needs_reply,email_escalate,email_priority \
      --endpoint http://localhost:11434/v1 --model qwen2.5:7b-instruct \
      --limit 4000 --audit 500 --out-dir data/jsonl

  # placeholder families need a --corpus-file (no public corpus bundled):
  python3 scripts/distill.py --tasks finance_doc \
      --corpus-file data/raw/finance_docs --limit 2000 --audit 300

Outputs: the files above, plus a per-task stdout line
``<task>: labeled=.. unparsed=.. err=.. train=.. val=.. dist=..``.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import random
import sys
import time
import urllib.error
import urllib.request

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import data_org  # noqa: E402
from verdict.data import Record, dump_jsonl  # noqa: E402


# --- LLM judge (OpenAI-compatible; same shape as scripts/eval_baseline.py) --

def query(endpoint: str, model: str, prompt: str, timeout: int = 60,
          retries: int = 2) -> str:
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0, "max_tokens": 8,
    }).encode()
    url = endpoint.rstrip("/") + "/chat/completions"
    last: Exception | None = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(url, data=body,
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.loads(r.read())
            return out["choices"][0]["message"]["content"]
        except Exception as e:  # noqa: BLE001 — retry any transient failure
            last = e
            if attempt < retries:
                time.sleep(1.5 * (attempt + 1))
    raise last if last else RuntimeError("query failed")


# --- split by item (content-hashed, stable across tasks) ------------------

def side_of(text: str, val_frac: float, seed: int) -> str:
    h = hashlib.sha1(f"{seed}:{text}".encode("utf-8")).hexdigest()
    return "val" if (int(h[:8], 16) % 10_000) < int(val_frac * 10_000) else "train"


# --- per-task distillation -------------------------------------------------

def distill_task(task: str, args) -> dict:
    cfg = data_org.ORG_TASKS[task]
    options = list(cfg["options"])
    items = data_org.load_items_for_task(
        task, hf_id=args.hf_id, corpus_file=args.corpus_file, split=args.split,
        limit=args.limit, seed=args.seed,
    )
    print(f"[{task}] {len(items)} unlabeled items loaded "
          f"(family={cfg['family']})", flush=True)

    labeled: list[tuple[Record, int]] = []  # (record, side-agnostic order idx)
    n_unparsed = n_err = 0
    dist = [0] * len(options)
    t0 = time.perf_counter()
    for i, it in enumerate(items):
        prompt = data_org.judge_prompt(task, it.text)
        try:
            raw = query(args.endpoint, args.model, prompt,
                        timeout=args.timeout, retries=args.retries)
        except Exception as e:  # noqa: BLE001
            n_err += 1
            if n_err <= 3:
                print(f"  [{task}] query error: {e}", flush=True)
            continue
        ans = data_org.parse_judge(task, raw)
        if ans is None:
            n_unparsed += 1
            continue
        dist[ans] += 1
        rec = Record(
            text=it.text,
            question=data_org.record_question(task, it.text),
            options=options,
            answer=ans,
            qtype=cfg["qtype"],
            task=task,
            meta={"source": it.source, "judge_model": args.model,
                  "judge_raw": raw.strip()[:32], **it.meta},
        )
        labeled.append((rec, i))
        if (i + 1) % 100 == 0:
            rate = (i + 1) / max(time.perf_counter() - t0, 1e-6)
            print(f"  [{task}] {i + 1}/{len(items)} "
                  f"labeled={len(labeled)} ({rate:.1f} items/s)", flush=True)

    # split by item (stable hash), then write train/val JSONL
    train = [r for r, _ in labeled if side_of(r.text, args.val_frac, args.seed) == "train"]
    val = [r for r, _ in labeled if side_of(r.text, args.val_frac, args.seed) == "val"]
    os.makedirs(args.out_dir, exist_ok=True)
    dump_jsonl(train, os.path.join(args.out_dir, f"{task}_train.jsonl"))
    dump_jsonl(val, os.path.join(args.out_dir, f"{task}_val.jsonl"))

    # human-audit subset CSV (blank human_label)
    audit_dir = os.path.join(args.out_dir, "audit")
    os.makedirs(audit_dir, exist_ok=True)
    recs = [r for r, _ in labeled]
    audit_n = min(args.audit, len(recs))
    audit_sample = random.Random(args.seed).sample(recs, audit_n) if audit_n else []
    audit_path = os.path.join(audit_dir, f"{task}_audit.csv")
    with open(audit_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["idx", "task", "qtype", "options", "judge_label",
                    "judge_label_str", "human_label", "agree", "text"])
        for j, r in enumerate(audit_sample):
            w.writerow([j, task, r.qtype, "|".join(options), r.answer,
                        options[r.answer], "", "", r.text])

    # reproducibility sidecar
    sidecar = {
        "task": task,
        "qtype": cfg["qtype"],
        "options": options,
        "family": cfg["family"],
        "placeholder": cfg["placeholder"],
        "prompt": cfg["prompt"],
        "judge_instruction": data_org.judge_instruction(task),
        "judge_prompt_format": "<judge_instruction>\\n\\nITEM:\\n\"\"\"\\n<text>\\n\"\"\"\\n\\nNumber:",
        "judge_model": args.model,
        "endpoint": args.endpoint,
        "temperature": 0,
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "corpus": args.corpus_file or args.hf_id or data_org.DEFAULT_EMAIL_HF,
        "seed": args.seed,
        "val_frac": args.val_frac,
        "counts": {
            "items": len(items),
            "labeled": len(recs),
            "unparsed": n_unparsed,
            "errors": n_err,
            "train": len(train),
            "val": len(val),
            "audit": audit_n,
        },
        "label_distribution": {options[k]: dist[k] for k in range(len(options))},
    }
    with open(os.path.join(args.out_dir, f"{task}.distill.json"), "w", encoding="utf-8") as f:
        json.dump(sidecar, f, indent=2, ensure_ascii=False)

    print(f"{task}: labeled={len(recs)} unparsed={n_unparsed} err={n_err} "
          f"train={len(train)} val={len(val)} audit={audit_n} "
          f"dist={sidecar['label_distribution']}", flush=True)
    return sidecar


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", required=True,
                    help="comma list of org tasks, e.g. email_needs_reply,email_escalate")
    ap.add_argument("--limit", type=int, default=2000, help="max items to label per task")
    ap.add_argument("--audit", type=int, default=500, help="human-audit subset size per task")
    ap.add_argument("--endpoint", default="http://localhost:11434/v1")
    ap.add_argument("--model", default="qwen2.5:7b-instruct")
    ap.add_argument("--out-dir", default="data/jsonl")
    # corpus / split / judge knobs
    ap.add_argument("--hf-id", default=None, help=f"HF email dataset id (default {data_org.DEFAULT_EMAIL_HF})")
    ap.add_argument("--corpus-file", default=None, help="dir / .jsonl / .txt of raw texts (required for placeholder families)")
    ap.add_argument("--split", default=data_org.DEFAULT_EMAIL_SPLIT)
    ap.add_argument("--val-frac", type=float, default=0.1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--timeout", type=int, default=60)
    ap.add_argument("--retries", type=int, default=2)
    args = ap.parse_args()

    random.seed(args.seed)
    tasks = [t for t in args.tasks.split(",") if t.strip()]
    unknown = [t for t in tasks if t not in data_org.ORG_TASKS]
    if unknown:
        ap.error(f"unknown task(s) {unknown}; known: {data_org.list_tasks()}")

    manifest = {
        "run_utc": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
        "judge_model": args.model,
        "endpoint": args.endpoint,
        "tasks": {},
    }
    for task in tasks:
        manifest["tasks"][task] = distill_task(task, args)

    os.makedirs(args.out_dir, exist_ok=True)
    with open(os.path.join(args.out_dir, "distill_run.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    print(f"\nwrote distilled JSONL + audit CSVs + sidecars -> {args.out_dir} "
          f"(manifest: {os.path.join(args.out_dir, 'distill_run.json')})", flush=True)


if __name__ == "__main__":
    main()

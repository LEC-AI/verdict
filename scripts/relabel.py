"""Relabel (or cross-check) distilled OrgBench records with a stronger LLM.

Reads existing distilled Records (data/jsonl/<task>_<split>.jsonl), asks an
OpenAI-compatible teacher for the typed decision using the SAME rubric and
prompt as scripts/distill.py (verdict.data_org.judge_prompt), and writes one
label file per (task, split, tag):

    data/labels/<task>_<split>.<tag>.jsonl   {"key", "label", "raw"}

`key` = sha1(text)[:16], so label files from different teachers join on the
item. No record is modified here; scripts/build_org_data.py combines the label
files into a training set and an agreement report.

Concurrency via a thread pool (--workers). Resumable: keys already present in
the output file are skipped. Optional USD budget cap (--max-usd with
--price-in/--price-out in $/M tokens) stops the run before overspending.

  # primary teacher: Qwen3-VL-32B on the idle GB10 (direct vLLM endpoint)
  python3 scripts/relabel.py --tag qwen3vl32b --endpoint http://127.0.0.1:8003/v1 \
      --model Qwen/Qwen3-VL-32B-Instruct-FP8 --splits train,val --workers 6

  # independent check: DeepSeek V3.2 via OpenRouter on the val splits, capped at $1.50
  python3 scripts/relabel.py --tag deepseekv32 --endpoint https://openrouter.ai/api/v1 \
      --model deepseek/deepseek-v3.2 --api-key-file ~/.config/verdict/openrouter.key \
      --splits val --workers 8 --max-usd 1.5 --price-in 0.27 --price-out 0.40
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import threading
import time
import types
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

# import verdict.data_org without running verdict/__init__ (which needs torch)
_ROOT = os.path.join(os.path.dirname(__file__), "..")
_pkg = types.ModuleType("verdict"); _pkg.__path__ = [os.path.join(_ROOT, "verdict")]
sys.modules.setdefault("verdict", _pkg)
from verdict import data_org  # noqa: E402


def key_of(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8")).hexdigest()[:16]


def query(endpoint, model, prompt, api_key=None, timeout=90, retries=3, max_tokens=8):
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "temperature": 0, "max_tokens": max_tokens}
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    data = json.dumps(body).encode()
    last = None
    for attempt in range(retries + 1):
        try:
            req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", data=data, headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(str(out["error"])[:200])
            msg = out["choices"][0]["message"]
            return (msg.get("content") or ""), out.get("usage") or {}
        except Exception as e:  # noqa: BLE001
            last = e
            if attempt < retries:
                time.sleep(2.0 * (attempt + 1))
    raise last


def load_texts(path):
    rows = []
    for line in open(path, encoding="utf-8"):
        if line.strip():
            r = json.loads(line)
            rows.append((key_of(r["text"]), r["text"]))
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tasks", default="email_needs_reply,email_escalate,email_priority")
    ap.add_argument("--splits", default="train,val")
    ap.add_argument("--in-dir", default="data/jsonl")
    ap.add_argument("--out-dir", default="data/labels")
    ap.add_argument("--tag", required=True, help="short teacher id used in file names")
    ap.add_argument("--endpoint", required=True)
    ap.add_argument("--model", required=True)
    ap.add_argument("--api-key-file", default=None)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--limit", type=int, default=0, help="cap items per (task, split); 0 = all")
    ap.add_argument("--max-usd", type=float, default=0.0)
    ap.add_argument("--price-in", type=float, default=0.0, help="$ per 1M prompt tokens")
    ap.add_argument("--price-out", type=float, default=0.0, help="$ per 1M completion tokens")
    ap.add_argument("--max-tokens", type=int, default=8)
    args = ap.parse_args()
    api_key = open(os.path.expanduser(args.api_key_file)).read().strip() if args.api_key_file else None
    os.makedirs(args.out_dir, exist_ok=True)

    spent = {"in": 0, "out": 0}
    lock = threading.Lock()
    stop = threading.Event()

    def usd():
        return spent["in"] / 1e6 * args.price_in + spent["out"] / 1e6 * args.price_out

    for task in args.tasks.split(","):
        for split in args.splits.split(","):
            src = os.path.join(args.in_dir, f"{task}_{split}.jsonl")
            dst = os.path.join(args.out_dir, f"{task}_{split}.{args.tag}.jsonl")
            items = load_texts(src)
            if args.limit:
                items = items[: args.limit]
            done = set()
            if os.path.isfile(dst):
                done = {json.loads(l)["key"] for l in open(dst) if l.strip()}
            todo = [(k, t) for k, t in items if k not in done]
            print(f"[{args.tag}] {task}/{split}: {len(items)} items, {len(done)} already labeled, {len(todo)} to go", flush=True)
            if not todo or stop.is_set():
                continue
            t0 = time.time(); n_ok = n_bad = 0
            with open(dst, "a", encoding="utf-8") as fout, ThreadPoolExecutor(args.workers) as ex:
                def work(k, text):
                    if stop.is_set():
                        return k, None, "skipped", {}
                    raw, use = query(args.endpoint, args.model, data_org.judge_prompt(task, text),
                                     api_key=api_key, max_tokens=args.max_tokens)
                    return k, data_org.parse_judge(task, raw), raw, use
                futs = [ex.submit(work, k, t) for k, t in todo]
                for i, f in enumerate(as_completed(futs), 1):
                    try:
                        k, lab, raw, use = f.result()
                    except Exception as e:  # noqa: BLE001
                        n_bad += 1
                        if n_bad <= 3:
                            print(f"  error: {str(e)[:160]}", flush=True)
                        continue
                    if raw == "skipped":
                        continue
                    with lock:
                        spent["in"] += use.get("prompt_tokens", 0); spent["out"] += use.get("completion_tokens", 0)
                        fout.write(json.dumps({"key": k, "label": lab, "raw": (raw or "").strip()[:32]}) + "\n")
                        fout.flush()
                        n_ok += 1
                        if args.max_usd and usd() >= args.max_usd and not stop.is_set():
                            print(f"  BUDGET CAP reached (${usd():.3f} >= ${args.max_usd}); stopping", flush=True)
                            stop.set()
                    if i % 200 == 0:
                        rate = i / max(time.time() - t0, 1e-6)
                        print(f"  {task}/{split}: {i}/{len(todo)} ({rate:.1f}/s) spent=${usd():.3f}", flush=True)
            print(f"[{args.tag}] {task}/{split}: wrote {n_ok}, errors {n_bad}, {time.time()-t0:.0f}s, spent=${usd():.3f}", flush=True)
    print(f"DONE tag={args.tag} tokens in={spent['in']} out={spent['out']} spent=${usd():.3f}", flush=True)


if __name__ == "__main__":
    main()

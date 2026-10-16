"""Build the Kaggle phishing-email dataset (Naser Abdullah Alam, mirrored on HF as
zefang-liu/phishing-email-dataset, 18,650 emails) into the Record/JSONL cache format every other script in this
project already reads (verdict.data.Record, "name@dir" task spec). Not peer-reviewed like RACE/BoolQ/MultiRC -- an
extra, practically-motivated check, reported as such.

A single noul (yes/no) question per email, same convention as BoolQ/MultiRC: options ["false: ...", "true: ..."].
No official split exists, so we build one ourselves: a stable split by sha1(text) hash, 80/10/10 train/val/test,
so it is reproducible and never touches the test rows during any training or selection step.

  python3 scripts/build_phishing_data.py --out-dir data/jsonl
"""
import argparse
import hashlib
import json
import os
import sys
import types

_ROOT = os.path.join(os.path.dirname(__file__), "..")
_pkg = types.ModuleType("verdict"); _pkg.__path__ = [os.path.join(_ROOT, "verdict")]
sys.modules.setdefault("verdict", _pkg)
from verdict.data import Record, dump_jsonl  # noqa: E402


def bucket(text, train=80, val=10):
    h = int(hashlib.sha1(text.encode("utf-8")).hexdigest()[:8], 16) % 100
    return "train" if h < train else ("val" if h < train + val else "test")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", default="data/jsonl")
    ap.add_argument("--max-chars", type=int, default=6000, help="truncate very long emails (keep the start)")
    a = ap.parse_args()
    from datasets import load_dataset
    ds = load_dataset("zefang-liu/phishing-email-dataset")["train"]

    by_split = {"train": [], "val": [], "test": []}
    seen = set()
    n_none, n_dup, n_empty = 0, 0, 0
    for ex in ds:
        text = ex["Email Text"]
        if text is None:
            n_none += 1; continue
        text = text.strip()
        if not text:
            n_empty += 1; continue
        if text in seen:
            n_dup += 1; continue
        seen.add(text)
        label = ex["Email Type"]
        if label not in ("Safe Email", "Phishing Email"):
            continue
        answer = 1 if label == "Phishing Email" else 0
        text = text[: a.max_chars]
        q = "Is this email a phishing attempt?"
        rec = Record(
            text=text,
            question=f"{q}\n\nContext:\n{text}",
            options=["false: a legitimate, non-phishing email", "true: a phishing email"],
            answer=answer, qtype="noul", task="phishing",
            meta={"source": "kaggle:naserabdullahalam/phishing-email-dataset (via HF zefang-liu mirror)"},
        )
        by_split[bucket(text)].append(rec)

    os.makedirs(a.out_dir, exist_ok=True)
    for split, recs in by_split.items():
        dump_jsonl(recs, os.path.join(a.out_dir, f"phishing_{split}.jsonl"))
        pos = sum(r.answer for r in recs)
        print(f"{split}: {len(recs)} emails, {pos} phishing ({pos/max(len(recs),1)*100:.1f}%)")
    print(f"dropped: {n_none} null, {n_empty} empty, {n_dup} duplicate")


if __name__ == "__main__":
    main()

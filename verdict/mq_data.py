"""Records -> MQ cases (all questions that share one state become one case)."""
from __future__ import annotations

import os
from collections import OrderedDict

from .data import TASKS, build_task, load_jsonl
from .mq import MQCase, MQQuestion


def item_key(rec):
    """Stable per-decision key shared by every evaluator (pairs Verdict and baselines for significance tests)."""
    import hashlib
    return hashlib.sha1((rec.question + "||" + "|".join(rec.options)).encode("utf-8")).hexdigest()[:16]


def split_record(rec):
    """(state, instructions) from a Record. typed/synth: '<instr>\\n\\nContext:\\n<state>';
    OrgBench: '<prompt>\\n\\n<text>'."""
    q = rec.question
    if "\n\nContext:\n" in q:
        instr, state = q.split("\n\nContext:\n", 1)
        return state, instr.strip()
    if rec.text and q.endswith(rec.text):
        return rec.text, q[: -len(rec.text)].strip()
    return rec.text or q, q.split("\n\n", 1)[0].strip()


def to_cases(recs, max_questions=16):
    """-> list of (MQCase, [Record per question]) grouped by state, order preserved. A state with more than
    `max_questions` questions (e.g. MultiRC paragraphs with dozens of answer checks) is split into several
    cases so the packed blocks never crowd the state out of the context window."""
    groups = OrderedDict()
    for r in recs:
        if not (0 <= r.answer < len(r.options)) or len(r.options) < 2:
            continue
        state, instr = split_record(r)
        g = groups.setdefault(state, [])
        g.append((MQQuestion(instr, list(r.options), r.qtype), r))
    out = []
    for state, items in groups.items():
        for i in range(0, len(items), max_questions):
            chunk = items[i:i + max_questions]
            out.append((MQCase(state, [q for q, _ in chunk]), [r for _, r in chunk]))
    return out


# ---- standard benchmarks (public, peer-reviewed), built on the fly as Records ----
# split names: "train"; "val" = monitoring split (printed during training, never used for selection);
# "test" = the reporting split (RACE test, BoolQ validation since its test labels are hidden, CLINC150 test).
_STD = {
    "race":   {"repo": "ehovy/race", "config": "all", "train": "train", "val": "validation", "test": "test"},
    # BoolQ: test labels hidden -> validation is the reporting split; 10% of TRAIN passages are the monitoring split.
    "boolq":  {"repo": "google/boolq", "config": None, "train": "train", "val": "train", "test": "validation"},
    "clinc":  {"repo": "clinc/clinc_oos", "config": "plus", "train": "train", "val": "validation", "test": "test"},
    # SuperGLUE MultiRC: each (question, candidate answer) is a yes/no decision over the paragraph; test labels are
    # hidden, so validation is the reporting split and 10% of TRAIN paragraphs are the monitoring split.
    "multirc": {"repo": "aps/super_glue", "config": "multirc", "train": "train", "val": "train", "test": "validation"},
    # Banking77 has no validation split: 10% of TRAIN (by text hash) is the monitoring split.
    "banking77": {"repo": "legacy-datasets/banking77", "config": None, "train": "train", "val": "train", "test": "test"},
}
_HOLDOUT = {"multirc", "banking77", "boolq"}  # monitoring split carved from TRAIN (boolq: its "val" is the reporting split)


def _held(key):
    import hashlib
    return int(hashlib.sha1(key.encode("utf-8")).hexdigest()[:8], 16) % 100 < 10


def _std_records(task, split):
    from datasets import load_dataset
    from .data import Record
    cfg = _STD[task]
    ds = load_dataset(cfg["repo"], cfg["config"], split=cfg[split]) if cfg["config"] else load_dataset(cfg["repo"], split=cfg[split])
    recs = []
    if task == "race":
        for ex in ds:
            q = ex["question"].strip(); art = ex["article"].strip()
            recs.append(Record(text=art, question=f"{q}\n\nContext:\n{art}", options=[o.strip() for o in ex["options"]],
                               answer="ABCD".index(ex["answer"].strip()), qtype="choice", task="race",
                               meta={"example_id": ex["example_id"]}))
    elif task == "boolq":
        for ex in ds:
            q = ex["question"].strip().rstrip("?") + "?"; ps = ex["passage"].strip()
            recs.append(Record(text=ps, question=f"{q}\n\nContext:\n{ps}", options=["false: no", "true: yes"],
                               answer=int(bool(ex["answer"])), qtype="noul", task="boolq"))
    elif task == "multirc":
        for ex in ds:
            ps = ex["paragraph"].strip(); q = ex["question"].strip(); ans = ex["answer"].strip()
            idx = ex["idx"]; qid = f'{idx["paragraph"]}-{idx["question"]}'
            recs.append(Record(text=ps, question=f"Is this a correct answer to the question? Question: {q} Answer: {ans}\n\nContext:\n{ps}",
                               options=["false: incorrect answer", "true: correct answer"], answer=int(ex["label"]),
                               qtype="noul", task="multirc", meta={"qid": qid, "pid": idx["paragraph"]}))
    elif task == "banking77":
        names = [n.replace("_", " ") for n in ds.features["label"].names]
        for ex in ds:
            t = ex["text"].strip()
            recs.append(Record(text=t, question=f"Which banking intent does this customer message express?\n\nContext:\n{t}",
                               options=names, answer=int(ex["label"]), qtype="choice", task="banking77"))
    elif task == "clinc":
        names = [n.replace("_", " ") for n in ds.features["intent"].names]
        for ex in ds:
            t = ex["text"].strip()
            recs.append(Record(text=t, question=f"Which intent does this user request express?\n\nContext:\n{t}",
                               options=names, answer=int(ex["intent"]), qtype="choice", task="clinc",
                               meta={"oos": names[int(ex["intent"])] == "oos"}))
    return recs


def load_split(task, split, cache_dir="data/jsonl", limit=0, val_limit=0):
    """Records for one task spec. Specs: standard benchmark (race|boolq|clinc) | TASKS name |
    'typed_decisions' | 'typed_dev' | 'name@dir' (cached jsonl)."""
    if task in _STD:
        sp = split if split in ("train", "val", "test") else "val"
        recs = _std_records(task, sp)
        if task in _HOLDOUT and sp in ("train", "val"):
            key = (lambda r: str(r.meta.get("pid"))) if task == "multirc" else (lambda r: r.text)
            recs = [r for r in recs if _held(key(r)) == (sp == "val")]
        n = limit if split == "train" else val_limit
        return recs[:n] if n else recs
    n = limit if split == "train" else val_limit
    if task in ("typed_decisions", "typed_dev"):
        # typed_dev: recipe-tuning protocol. train = 85% of the benchmark TRAIN cases, "val" = the other 15%
        # (held out by case), so hyper-parameters are never chosen on the TEST split.
        import hashlib
        from .data_typed import load_typed
        if task == "typed_dev":
            recs = load_typed("train")
            held = lambda r: int(hashlib.sha1(r.text.encode("utf-8")).hexdigest()[:8], 16) % 100 < 15
            recs = [r for r in recs if held(r) == (split != "train")]
        else:
            recs = load_typed("train" if split == "train" else "test")
        return recs[:n] if n else recs
    tdir = cache_dir
    if "@" in task:
        task, tdir = task.split("@", 1)
    path = os.path.join(tdir, f"{task}_{split}.jsonl")
    if os.path.isfile(path):
        recs = load_jsonl(path)
    elif task in TASKS:
        try:
            recs = build_task(task, "train" if split == "train" else "validation", limit=limit)
        except Exception:
            recs = build_task(task, "test", limit=limit)
    else:
        raise FileNotFoundError(path)
    return recs[:n] if n else recs

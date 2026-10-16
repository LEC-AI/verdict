"""OrgBench distillation corpus + org-decision task definitions.

This module supplies the *unlabeled* side of the org-authentic OrgBench tasks
(the starred rows in the paper's §5 table): it turns a PUBLIC email / business
corpus into a stream of unlabeled items, and it declares each org decision as a
TYPED question (noul / score / choice) with an explicit judge rubric. The
*labels* are produced separately by ``scripts/distill.py`` (LLM judge over these
items) — nothing here contacts a model or invents a label.

Corpus (public only — the released benchmark is Apache-2.0):
  * Default email corpus: the public Enron email set via HF datasets.
    Default id ``corbt/enron-emails`` (clean ``body`` + ``subject``/``from``/
    ``to``/``date``, single ``train`` split). Alternative: ``Yale-LILY/aeslc``
    (field ``email_body``). Field detection is flexible across both.
  * Fallback for ANY task / corpus family: ``--corpus-file`` of raw texts —
    a directory (one item per file), a ``.jsonl`` (one object per line with a
    ``text``/``body`` field), or a ``.txt`` (items separated by a delimiter
    line, default ``%%%%``). This is how the placeholder ``leads`` / ``finance``
    families are fed until a bundled public corpus is chosen.

Tasks:
  email_needs_reply  noul       does this email require a reply
  email_escalate     noul       escalate to a human / senior person now
  email_priority     score(0-3) handling urgency
  lead_qualify       noul       is this lead worth a rep's time      (no bundled corpus)
  finance_doc        choice(4)  invoice / receipt / statement / other (no bundled corpus)

The email_* tasks all draw from the SAME email corpus, so one pass of items can
be labeled for all three (and split train/val consistently — see distill.py).
``lead_qualify`` / ``finance_doc`` are declared but ship WITHOUT a bundled public
corpus, so they require ``--corpus-file``. Neither is used in the paper.

Run (inspect unlabeled items — does NOT label anything):

  python3 verdict/data_org.py --task email_needs_reply --limit 5 --show
  python3 verdict/data_org.py --task email_escalate --limit 2000 \
      --out data/jsonl/email_items.jsonl        # dump unlabeled items as JSONL

Outputs: with --show, prints item count + the first few cleaned items to stdout.
With --out, writes JSONL of {"text","source","meta"} (one unlabeled item/line)
and prints the count. No network calls except the HF dataset download.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import random
import re
from dataclasses import dataclass, field

try:  # imported as `verdict.data_org`
    from .types import Choice, Noul, Question, Score
except ImportError:  # run directly as a script
    import sys as _sys

    _sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from verdict.types import Choice, Noul, Question, Score  # noqa: E402


# --- corpus defaults ------------------------------------------------------

DEFAULT_EMAIL_HF = "corbt/enron-emails"     # clean `body`; single `train` split
DEFAULT_EMAIL_SPLIT = "train"
# Field-name candidates so the same loader handles corbt/enron-emails,
# Yale-LILY/aeslc, and generic email dumps.
_TEXT_FIELDS = ("body", "email_body", "text", "message", "content")
_SUBJECT_FIELDS = ("subject", "subject_line")
_FROM_FIELDS = ("from", "sender", "from_address")
_TO_FIELDS = ("to", "recipient", "to_address")
_DATE_FIELDS = ("date", "datetime", "timestamp")

# Item length gates (chars). Bodies below MIN are dropped; above MAX truncated
# so the judge prompt stays bounded.
MIN_CHARS = 40
MAX_CHARS = 4000

# Corpus families and which public corpus backs each. "email" is bundled;
# leads / finance are placeholders that require --corpus-file.
CORPUS_BUNDLED = {"email": True, "leads": False, "finance": False}


@dataclass
class OrgItem:
    """One unlabeled item under decision (an email, message, or document)."""

    text: str
    source: str  # corpus family: "email" | "leads" | "finance"
    meta: dict = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps({"text": self.text, "source": self.source, "meta": self.meta},
                          ensure_ascii=False)


# --- org-decision task registry ------------------------------------------
# Each task: qtype, options (parallel to `rubric`), the org-decision `prompt`
# (framing prepended to the item, matching verdict.data's convention), the
# corpus `family`, and `placeholder` (no public corpus bundled).

ORG_TASKS: dict[str, dict] = {
    "email_needs_reply": dict(
        qtype="noul", family="email", placeholder=False,
        options=["no", "yes"],
        prompt="Does this email require a written reply from the recipient?",
        rubric=[
            "no  — no reply expected: an FYI / notification / newsletter / "
            "automated or confirmation message, or a thread already resolved; "
            "nothing asks the recipient for a response.",
            "yes — a reply is expected: the email puts a direct question, "
            "request, or action item to the recipient that calls for a written "
            "response.",
        ],
    ),
    "email_escalate": dict(
        qtype="noul", family="email", placeholder=False,
        options=["no", "yes"],
        prompt="Should this email be escalated to a human / senior person right now, "
               "beyond the normal handling flow?",
        rubric=[
            "no  — routine business email handled in the normal workflow; no "
            "unusual urgency or risk.",
            "yes — needs senior or human attention now: angry/threatening tone, "
            "a legal / compliance / security issue, significant money at risk, "
            "executive-level or hard-deadline matter, or a complaint/crisis that "
            "could escalate if left.",
        ],
    ),
    "email_priority": dict(
        qtype="score", family="email", placeholder=False,
        options=["0", "1", "2", "3"],
        prompt="How urgent is handling this email? Rate 0 (none) to 3 (urgent).",
        rubric=[
            "0 — no action needed: purely informational, can be archived.",
            "1 — low: routine, handle whenever convenient, no deadline.",
            "2 — medium: important, should be handled today.",
            "3 — high: urgent / time-critical, handle immediately.",
        ],
    ),
    # ---- placeholders: declared, but no public corpus bundled ----
    "lead_qualify": dict(
        qtype="noul", family="leads", placeholder=True,
        options=["no", "yes"],
        prompt="Is this inbound message a qualified sales lead worth a rep's time?",
        rubric=[
            "no  — not a real buying opportunity: spam, a job seeker, a vendor / "
            "partnership pitch, a student/research request, existing-customer "
            "support, or clearly no budget / authority / need / fit.",
            "yes — a genuine prospect showing interest, a real need, and "
            "plausible fit/budget — worth a rep following up.",
        ],
    ),
    "finance_doc": dict(
        qtype="choice", family="finance", placeholder=True,
        options=["invoice", "receipt", "statement", "other"],
        prompt="Which kind of financial document is this text?",
        rubric=[
            "invoice   — a request for payment for goods/services (invoice "
            "number, amount due, due date, bill-to).",
            "receipt   — proof a payment was already made (paid / amount "
            "tendered / transaction record).",
            "statement — a periodic summary of account activity or balance over "
            "a period (bank / credit-card / account statement).",
            "other     — any financial text that is none of the above (quote, "
            "purchase order, contract, report, general correspondence).",
        ],
    ),
}


def list_tasks() -> list[str]:
    return list(ORG_TASKS)


def task_family(task: str) -> str:
    return ORG_TASKS[task]["family"]


def record_question(task: str, text: str) -> str:
    """The `Record.question` string — same convention as verdict.data:
    task framing, blank line, then the item text."""
    return f"{ORG_TASKS[task]['prompt']}\n\n{text}"


def make_question(task: str, text: str) -> Question:
    """Build the typed question object for one item (used at inference/eval)."""
    t = ORG_TASKS[task]
    q = record_question(task, text)
    if t["qtype"] == "noul":
        return Noul(q)
    if t["qtype"] == "score":
        return Score(q, k=len(t["options"]))
    return Choice(q, list(t["options"]))


# --- LLM-judge prompt + parsing (task semantics live next to the task) ----

def judge_instruction(task: str) -> str:
    """The rubric + answer-format instruction, WITHOUT the item text. Stored
    verbatim in the distill sidecar so the labeling is reproducible."""
    t = ORG_TASKS[task]
    n = len(t["options"])
    lines = [f"{t['prompt']}", "", "Decide using this rubric:"]
    lines += [f"  {i}: {r}" for i, r in enumerate(t["rubric"])]
    lines += [
        "",
        f"Answer with ONLY the single digit index of the best option "
        f"(0-{n - 1}). No words, no punctuation, just the number.",
    ]
    return "\n".join(lines)


def judge_prompt(task: str, text: str) -> str:
    """Full judge prompt: the item under decision, then the instruction."""
    return (f"{judge_instruction(task)}\n\n"
            f"ITEM:\n\"\"\"\n{text}\n\"\"\"\n\n"
            f"Number:")


def parse_judge(task: str, raw: str) -> int | None:
    """Parse the judge's reply into a valid option index, else None."""
    if raw is None:
        return None
    m = re.search(r"-?\d+", raw)
    if not m:
        return None
    idx = int(m.group())
    return idx if 0 <= idx < len(ORG_TASKS[task]["options"]) else None


# --- email cleaning -------------------------------------------------------

_HEADER_RE = re.compile(
    r"^(message-id|date|from|to|cc|bcc|subject|mime-version|content-type|"
    r"content-transfer-encoding|x-[\w-]+|sent|reply-to|return-path)\s*:",
    re.IGNORECASE,
)
_FORWARD_RE = re.compile(
    r"^\s*(-{2,}\s*original message\s*-{2,}|-{2,}\s*forwarded by|"
    r"_{5,}|On .+ wrote:)\s*$",
    re.IGNORECASE,
)


def clean_email(raw: str, max_chars: int = MAX_CHARS) -> str:
    """Best-effort strip of leading RFC-822 headers, forwarded/quoted tails,
    and signature clutter. Safe on already-clean bodies (e.g. corbt's `body`)
    and on raw maildir dumps alike."""
    if not raw:
        return ""
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = text.split("\n")

    # Drop a contiguous header block only if it's at the very top.
    i = 0
    while i < len(lines) and (_HEADER_RE.match(lines[i]) or lines[i].strip() == ""):
        i += 1
    if i and i < len(lines):
        lines = lines[i:]

    out: list[str] = []
    quoted = 0
    for ln in lines:
        if _FORWARD_RE.match(ln):
            break  # stop at the first forwarded/reply boundary
        s = ln.strip()
        if s.startswith(">"):
            quoted += 1
            if quoted > 2:  # tolerate a little quoting, cut long quoted chains
                break
            continue
        out.append(ln)

    body = "\n".join(out)
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    if len(body) > max_chars:
        body = body[:max_chars].rstrip() + " …"
    return body


# --- corpus loaders -------------------------------------------------------

def _first(ex: dict, names) -> str | None:
    for k in names:
        if k in ex and ex[k] is not None:
            return k
    return None


def _row_to_item(ex: dict, source: str, min_chars: int, max_chars: int) -> OrgItem | None:
    tf = _first(ex, _TEXT_FIELDS)
    if tf is None:
        return None
    body = clean_email(str(ex[tf]), max_chars=max_chars)
    if len(body) < min_chars:
        return None
    meta: dict = {}
    sf = _first(ex, _SUBJECT_FIELDS)
    subject = str(ex[sf]).strip() if sf else ""
    if subject:
        meta["subject"] = subject
    for label, names in (("from", _FROM_FIELDS), ("to", _TO_FIELDS), ("date", _DATE_FIELDS)):
        f = _first(ex, names)
        if f:
            meta[label] = str(ex[f])
    # Prepend the subject so the judge sees it as part of the item.
    text = f"Subject: {subject}\n\n{body}" if subject else body
    return OrgItem(text=text, source=source, meta=meta)


def load_email_items(hf_id: str = DEFAULT_EMAIL_HF, split: str = DEFAULT_EMAIL_SPLIT,
                     limit: int = 0, seed: int = 0,
                     min_chars: int = MIN_CHARS, max_chars: int = MAX_CHARS) -> list[OrgItem]:
    """Load the public Enron email corpus from HF as unlabeled OrgItems."""
    from datasets import load_dataset

    ds = load_dataset(hf_id, split=split)
    idx = list(range(len(ds)))
    random.Random(seed).shuffle(idx)  # sample diverse items, not the first N
    items: list[OrgItem] = []
    for j in idx:
        it = _row_to_item(ds[j], "email", min_chars, max_chars)
        if it is None:
            continue
        items.append(it)
        if limit and len(items) >= limit:
            break
    return items


def load_raw_texts(path: str, source: str, limit: int = 0, seed: int = 0,
                   min_chars: int = MIN_CHARS, max_chars: int = MAX_CHARS,
                   delimiter: str = "%%%%") -> list[OrgItem]:
    """Load unlabeled items from a --corpus-file: a directory (one item per
    file), a .jsonl (object per line with a text/body field), or a .txt
    (items separated by a line equal to `delimiter`)."""
    raws: list[str] = []
    if os.path.isdir(path):
        for fp in sorted(glob.glob(os.path.join(path, "**", "*"), recursive=True)):
            if os.path.isfile(fp):
                try:
                    raws.append(open(fp, encoding="utf-8", errors="ignore").read())
                except OSError:
                    continue
    elif path.endswith(".jsonl"):
        for line in open(path, encoding="utf-8", errors="ignore"):
            line = line.strip()
            if not line:
                continue
            try:
                ex = json.loads(line)
            except json.JSONDecodeError:
                continue
            tf = _first(ex, _TEXT_FIELDS)
            if tf:
                raws.append(str(ex[tf]))
    else:  # single .txt with delimiter-separated records
        blob = open(path, encoding="utf-8", errors="ignore").read()
        raws = re.split(rf"^\s*{re.escape(delimiter)}\s*$", blob, flags=re.MULTILINE)

    random.Random(seed).shuffle(raws)
    items: list[OrgItem] = []
    for r in raws:
        body = clean_email(r, max_chars=max_chars)
        if len(body) < min_chars:
            continue
        items.append(OrgItem(text=body, source=source, meta={}))
        if limit and len(items) >= limit:
            break
    return items


def load_items_for_task(task: str, *, hf_id: str | None = None, corpus_file: str | None = None,
                        split: str = DEFAULT_EMAIL_SPLIT, limit: int = 0, seed: int = 0,
                        min_chars: int = MIN_CHARS, max_chars: int = MAX_CHARS) -> list[OrgItem]:
    """Resolve the corpus for `task` and return unlabeled OrgItems.

    A --corpus-file overrides everything (and is REQUIRED for placeholder
    families that ship without a bundled public corpus)."""
    if task not in ORG_TASKS:
        raise KeyError(f"unknown org task {task!r}; known: {list_tasks()}")
    family = task_family(task)
    if corpus_file:
        return load_raw_texts(corpus_file, family, limit=limit, seed=seed,
                              min_chars=min_chars, max_chars=max_chars)
    if family == "email":
        return load_email_items(hf_id or DEFAULT_EMAIL_HF, split=split, limit=limit,
                                seed=seed, min_chars=min_chars, max_chars=max_chars)
    raise NotImplementedError(
        f"task {task!r} uses the {family!r} corpus family, which has no bundled "
        f"public corpus. Pass --corpus-file (a dir of texts, a .jsonl with a "
        f"'text' field, or a delimited .txt)."
    )


# --- CLI: inspect / dump unlabeled items (no labeling) --------------------

def main() -> None:
    ap = argparse.ArgumentParser(description="Inspect/dump unlabeled OrgBench items.")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--task", choices=list_tasks(), help="org task whose corpus to load")
    g.add_argument("--list", action="store_true", help="list tasks and exit")
    ap.add_argument("--hf-id", default=None, help=f"HF email dataset id (default {DEFAULT_EMAIL_HF})")
    ap.add_argument("--corpus-file", default=None, help="dir / .jsonl / .txt of raw texts")
    ap.add_argument("--split", default=DEFAULT_EMAIL_SPLIT)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default=None, help="write items as JSONL here")
    ap.add_argument("--show", action="store_true", help="print the first few items")
    args = ap.parse_args()

    if args.list:
        for t in list_tasks():
            c = ORG_TASKS[t]
            tag = " (placeholder)" if c["placeholder"] else ""
            print(f"{t}: {c['qtype']} family={c['family']}{tag} -> {c['options']}")
        return

    items = load_items_for_task(args.task, hf_id=args.hf_id, corpus_file=args.corpus_file,
                                split=args.split, limit=args.limit, seed=args.seed)
    print(f"task={args.task} family={task_family(args.task)} items={len(items)}")
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            for it in items:
                f.write(it.to_json() + "\n")
        print(f"wrote {len(items)} unlabeled items -> {args.out}")
    if args.show:
        for it in items[:5]:
            print("-" * 60)
            print(it.text[:600])


if __name__ == "__main__":
    main()

"""OrgBench data: public text-classification datasets re-cast as
organizational-intelligence TYPED DECISIONS (choice / noul / score), plus the
unified Record schema training/eval consume.

Each task declares: a source HF dataset, how to turn a row into (question,
options, answer), and which decision type it is. Every source here is
permissively licensed (recorded in LICENSES-DATA.md) so the assembled
benchmark + any model trained on it is cleanly releasable.

The framing is deliberate: we phrase each task the way it shows up in an AI
chief-of-staff's workflow ("route this...", "is this...", "how urgent..."),
so the model learns the org-decision surface, not just academic labels.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field


@dataclass
class Record:
    text: str            # the item under decision (email, message, ticket...)
    question: str        # the org-decision prompt (task framing + text)
    options: list[str]
    answer: int
    qtype: str
    task: str
    meta: dict = field(default_factory=dict)

    def to_json(self):
        return json.dumps(self.__dict__, ensure_ascii=False)

    @classmethod
    def from_json(cls, line):
        return cls(**json.loads(line))


def load_jsonl(path):
    return [Record.from_json(l) for l in open(path) if l.strip()]


def dump_jsonl(recs, path):
    with open(path, "w") as f:
        for r in recs:
            f.write(r.to_json() + "\n")


# --- task registry -------------------------------------------------------
# Each entry: (hf_repo, config, split, text_field, label_field, qtype,
#              option_labels, task_prompt). option_labels=None -> read from
#              the dataset's ClassLabel names.

TASKS = {
    # Intent routing — the canonical org "route this request" decision.
    "route_intent": dict(
        # PolyAI/banking77 is script-based (unloadable with datasets>=3); parquet mirror, same 3,080 test items
        repo="legacy-datasets/banking77", config=None, text_field="text", label_field="label",
        qtype="choice", options=None, readable_labels=True,
        prompt="Route this customer message to the correct banking service intent:",
    ),
    # Topic routing — which desk/stream does this belong to.
    "route_topic": dict(
        repo="fancyzhx/ag_news", config=None, text_field="text", label_field="label",
        qtype="choice", options=["World", "Sports", "Business", "Sci/Tech"],
        prompt="Which desk should handle this incoming item?",
    ),
    # Sentiment as a yes/no org signal (is this message positive?).
    "signal_positive": dict(
        repo="stanfordnlp/sst2", config=None, text_field="sentence", label_field="label",
        qtype="noul", options=["no", "yes"],
        prompt="Is the sender's sentiment in this message positive?",
    ),
    # ---- held-out-task MIXTURE sources (training diversity for "read the options") ----
    # No sentiment datasets and no Enron-derived data here, so sentiment (sst2) and
    # the Enron email tasks stay truly unseen for the zero-shot held-out test.
    "topic_dbpedia": dict(
        repo="fancyzhx/dbpedia_14", config=None, text_field="content", label_field="label",
        shuffle_before_limit=True, qtype="choice",
        options=["Company", "Educational institution", "Artist", "Athlete", "Office holder",
                 "Means of transportation", "Building", "Natural place", "Village", "Animal",
                 "Plant", "Album", "Film", "Written work"],
        prompt="What kind of entity is this encyclopedia entry about?",
    ),
    "topic_yahoo": dict(
        repo="community-datasets/yahoo_answers_topics", config=None,
        text_field=["question_title", "question_content"], label_field="topic",
        shuffle_before_limit=True, qtype="choice", options=None,
        prompt="Which forum category should this question be posted in?",
    ),
    "question_type": dict(
        repo="SetFit/TREC-QC", config=None, text_field="text", label_field="label_coarse",
        label_text_field="label_coarse_text", shuffle_before_limit=True, qtype="choice", options=None,
        prompt="What type of answer is this question asking for?",
    ),
    "irony": dict(
        repo="cardiffnlp/tweet_eval", config="irony", text_field="text", label_field="label",
        shuffle_before_limit=True, qtype="noul", options=["no", "yes"],
        prompt="Is this message ironic or sarcastic?",
    ),
    "hate": dict(
        repo="cardiffnlp/tweet_eval", config="hate", text_field="text", label_field="label",
        shuffle_before_limit=True, qtype="noul", options=["no", "yes"],
        prompt="Does this message contain hate speech against a group?",
    ),
    # Emotion — coarse affect for prioritization/handling.
    "affect": dict(
        repo="dair-ai/emotion", config=None, text_field="text", label_field="label",
        qtype="choice", options=None,
        prompt="What is the dominant emotion in this message (for handling/prioritization)?",
    ),
}


_READABLE = {"ABBR": "abbreviation", "ENTY": "entity or thing", "DESC": "description or explanation",
             "HUM": "person or group", "LOC": "location", "NUM": "number or quantity"}


def build_task(name, split, limit=0, seed=0):
    """Materialize one OrgBench task split into Records."""
    import random

    from datasets import load_dataset

    t = TASKS[name]
    ds = load_dataset(t["repo"], t["config"], split=split)
    if limit and t.get("shuffle_before_limit") and len(ds) > limit:
        ds = ds.shuffle(seed=seed).select(range(limit))   # sorted-by-class sources (dbpedia)
    elif limit:
        ds = ds.select(range(min(limit, len(ds))))
    # option label strings
    options = t["options"]
    if options is None and t.get("label_text_field"):
        # integer label + parallel text label column (e.g. SetFit/TREC-QC)
        pairs = sorted({(int(a), str(b)) for a, b in zip(ds[t["label_field"]], ds[t["label_text_field"]])})
        names = {a: b for a, b in pairs}
        options = [_READABLE.get(names[i], names[i]) for i in range(max(names) + 1)]
    elif options is None:
        feat = ds.features[t["label_field"]]
        options = list(feat.names)
        if t.get("readable_labels"):
            options = [o.replace("_", " ") for o in options]   # "activate_my_card" -> "activate my card"
    fields = t["text_field"] if isinstance(t["text_field"], list) else [t["text_field"]]
    recs = []
    for ex in ds:
        text = "\n".join(str(ex[f]).strip() for f in fields if ex.get(f)).strip()
        if not text:
            continue
        ans = int(ex[t["label_field"]])
        q = f"{t['prompt']}\n\n{text}"
        recs.append(Record(text=text, question=q, options=list(options), answer=ans,
                           qtype=t["qtype"], task=name))
    rng = random.Random(seed)
    rng.shuffle(recs)
    return recs

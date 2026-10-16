"""Loader for the LocalLLaMA/typed-decisions benchmark (Apache-2.0) — the
apples-to-apples comparator where Laya scored 0.766 and Jev 0.727 (teacher
ceiling 0.735). Four org workflows (invoice_processing, security_incidents,
customer_service, agent_trace_observability), 300 train / 100 test each. Each
case carries 5 typed questions (outcome/action = 4-way choice, needs_review =
noul, risk/urgency = 0-3 score) with soft multi-annotator gold labels.

We map each (case, question) to one verdict.data.Record so the SAME Verdict
model + trainer evaluate on the identical protocol Laya/Jev used. Labels are the
majority-argmax (`gold[q]['label']`); note genuine annotator disagreement
(label_agreement.argmax_agree is often false), so ~0.77 is near the ceiling.

  from verdict.data_typed import load_typed
  train = load_typed('train'); test = load_typed('test')
"""

from __future__ import annotations

import json

from .data import Record

WORKFLOWS = ["invoice_processing", "security_incidents", "customer_service", "agent_trace_observability"]


def _state_text(state_str: str) -> str:
    # keep the JSON context compact + readable as the decision input
    try:
        obj = json.loads(state_str)
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return str(state_str)


def _options_for(qtype: str, criteria):
    if qtype == "noul":
        return ["false", "true"]          # index 1 == yes/true (matches Noul)
    if qtype == "score":
        if isinstance(criteria, dict):
            keys = [k for k in criteria.keys()]
            # score keys are "0".."K-1"
            try:
                return sorted(keys, key=lambda x: int(x))
            except Exception:
                return keys
        return ["0", "1", "2", "3"]
    # choice: stable (sorted) key order for consistent indexing across cases
    if isinstance(criteria, dict):
        return sorted(criteria.keys())
    return list(criteria)


def _option_texts(qtype: str, keys, criteria):
    """Human-readable option strings carrying the benchmark's own criterion
    descriptions (what Laya/Jev receive). Before 2026-09-23 Verdict saw only the
    bare keys ("0".."3", "human_review"), i.e. strictly less information."""
    if qtype == "noul":
        c = criteria if isinstance(criteria, dict) else {}
        return [f"false: {c.get('false') or 'no, the statement does not hold'}",
                f"true: {c.get('true') or 'yes, the statement holds'}"]
    if qtype == "score":
        if isinstance(criteria, list):
            return [f"level {i}: {c}" for i, c in enumerate(criteria)]
        if isinstance(criteria, dict):
            return [f"level {k}: {criteria.get(k, '')}" for k in keys]
        return [f"level {k}" for k in keys]
    if isinstance(criteria, dict):
        return [f"{k}: {criteria[k]}" if criteria.get(k) else k for k in keys]
    return list(keys)


def load_typed(split: str, repo: str = "LocalLLaMA/typed-decisions", config: str = "all", limit: int = 0,
               describe: bool = True):
    from datasets import load_dataset

    ds = load_dataset(repo, name=config, split=split)
    if limit:
        ds = ds.select(range(min(limit, len(ds))))
    recs = []
    for ex in ds:
        state = _state_text(ex["state"])
        workflow = ex.get("workflow", config)
        Q = json.loads(ex["questions"]) if isinstance(ex["questions"], str) else ex["questions"]
        G = json.loads(ex["gold"]) if isinstance(ex["gold"], str) else ex["gold"]
        for qname, qdef in Q.items():
            qtype = qdef.get("type", "choice")
            instr = qdef.get("instructions", qname)
            keys = _options_for(qtype, qdef.get("criteria"))
            if qtype == "score" and isinstance(qdef.get("criteria"), list):
                keys = [str(i) for i in range(len(qdef["criteria"]))]
            options = keys
            gold = G.get(qname, {})
            label = str(gold.get("label"))
            if qtype == "noul":
                answer = 1 if label == "true" else 0
            elif qtype == "score":
                answer = options.index(label) if label in options else (int(label) if label.isdigit() else 0)
            else:
                if label not in options:
                    continue
                answer = options.index(label)
            question = f"{instr}\n\nContext:\n{state}"
            # aligned soft-label vector over `options` (annotator probability
            # distribution) — this benchmark is soft-labeled with low agreement,
            # so training on it (not hard argmax) is the right, calibrated target.
            probs = gold.get("probabilities") or {}
            soft = [float(probs.get(o, 0.0)) for o in keys]
            s = sum(soft)
            soft = [x / s for x in soft] if s > 0 else [1.0 / len(options)] * len(options)
            shown = _option_texts(qtype, keys, qdef.get("criteria")) if describe else list(keys)
            recs.append(Record(
                text=state, question=question, options=shown, answer=answer,
                qtype=qtype, task=f"typed:{workflow}:{qname}",
                meta={"workflow": workflow, "question": qname, "primitive": qtype,
                      "soft": soft, "option_keys": list(keys)},
            ))
    return recs

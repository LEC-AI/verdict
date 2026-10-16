"""Shared bridge: an MQCase (from verdict.mq_data.to_cases, the SAME grouping/instructions/options our own model and
baselines are evaluated on for RACE/BoolQ/MultiRC) -> the typed-question dict Jev and Laya both expect. Written
2026-09-25 to give Jev and Laya a real, controlled test on standard peer-reviewed benchmarks, not just the niche
typed-decisions benchmark they were built around."""


def _strip_prefix(opt, keys=("false", "true")):
    if ": " in opt:
        pre, rest = opt.split(": ", 1)
        if pre.lower() in keys:
            return rest
    return opt


def build_questions(case, bool_type="boolean"):
    """-> {qname: {type, instructions, criteria}}, qname = 'q0', 'q1', ... in case.questions order."""
    out = {}
    for i, q in enumerate(case.questions):
        qname = f"q{i}"
        if q.qtype == "noul":
            out[qname] = {"type": bool_type, "instructions": q.instructions,
                          "criteria": {"false": _strip_prefix(q.options[0]), "true": _strip_prefix(q.options[1])}}
        elif q.qtype == "score":
            out[qname] = {"type": "score", "instructions": q.instructions, "criteria": [_strip_prefix(o) for o in q.options]}
        else:
            out[qname] = {"type": "choice", "instructions": q.instructions,
                          "criteria": {str(j): _strip_prefix(o) for j, o in enumerate(q.options)}}
    return out

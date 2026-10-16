import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from verdict.mq import VerdictMQ, MQCase
from verdict.mq_data import load_split, to_cases

MAX_LEN = 2048
mt = VerdictMQ.from_pretrained("answerdotai/ModernBERT-base", device="cpu", max_len=MAX_LEN)

def scan(task, split):
    recs = load_split(task, split)
    cases = to_cases(recs)
    worst_margin = None
    n_truncated = 0
    for c, _ in cases:
        blocks = []
        for q in c.questions:
            qids = mt._tok(f"{q.qtype} question: {q.instructions}")[:160] + [mt.tokenizer.sep_token_id]
            opts = [[mt.opt_id] + mt._tok(" " + o)[: mt.max_opt_tokens - 1] for o in q.options]
            blocks.append((qids, opts))
        block_len = sum(len(qi) + sum(len(o) for o in op) for qi, op in blocks)
        room = max(16, MAX_LEN - block_len - 2)
        state_len = len(mt._tok(c.state))
        margin = room - state_len
        if margin < 0:
            n_truncated += 1
        if worst_margin is None or margin < worst_margin:
            worst_margin = margin
    print(f"{task:12s} {split:6s} n_cases={len(cases):5d} n_truncated={n_truncated:4d} worst_margin={worst_margin}")

for task, split in [("race", "test"), ("boolq", "test"), ("multirc", "test"), ("typed_decisions", "test")]:
    scan(task, split)

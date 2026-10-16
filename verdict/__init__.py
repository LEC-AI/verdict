"""Verdict: encode once, decide many.

The paper's model is verdict.mq.VerdictMQ (one pass answers every typed question about a case):

    from verdict.mq import VerdictMQ, MQCase, MQQuestion
    m = VerdictMQ.from_pretrained("out/mq-large")   # a checkpoint you trained (see README)
    probs = m.predict([MQCase(state=text, questions=[MQQuestion("Needs a reply?", ["false", "true"], "noul")])])

The single-question v1 model (Verdict, Choice, Noul, Score) is kept for the ablations.
"""

from .model import Verdict, DEFAULT_BACKBONE, OPT_TOKEN, render
from .types import Choice, Decision, Noul, Question, Score

__all__ = ["Verdict", "Choice", "Noul", "Score", "Question", "Decision",
           "DEFAULT_BACKBONE", "OPT_TOKEN", "render"]
__version__ = "1.0.0"

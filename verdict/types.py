"""Typed questions and decisions.

Mirrors the Laya/Jev "System-1" contract: a question is TYPED — the caller
declares the output space up front, the model returns a calibrated probability
distribution over exactly that space in a single forward pass. No free text is
ever generated, so there is nothing to parse and nothing to hallucinate.

Three primitives (same vocabulary the text-only Laya uses, so tooling built
against Laya's contract ports directly):

  Choice  — pick one of N declared options            -> P(option_i)
  Noul    — a yes/no with calibrated probability      -> P(yes)
  Score   — an ordinal 0..K-1 rating (default K=4)    -> P(bucket_k)

Noul and Score are internally lowered onto the Choice machinery (yes/no and
bucket labels become options), so the model has ONE scoring pathway.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence


@dataclass(frozen=True)
class Choice:
    """Pick one of `options`. Options are short human-readable strings; for
    GUI decisions each option typically describes one candidate element,
    e.g. "button 'Search' at (512, 88)"."""

    question: str
    options: Sequence[str]

    def __post_init__(self) -> None:
        if len(self.options) < 2:
            raise ValueError("Choice needs at least 2 options")


@dataclass(frozen=True)
class Noul:
    """Calibrated yes/no. `predict` returns P(yes) as `probs[1]`."""

    question: str

    #: rendering of the two options in the prompt (index 1 == yes)
    options: Sequence[str] = field(default=("no", "yes"))


@dataclass(frozen=True)
class Score:
    """Ordinal rating on 0..K-1 (default 0-3, matching Laya's spectrum)."""

    question: str
    k: int = 4

    @property
    def options(self) -> Sequence[str]:
        return tuple(str(i) for i in range(self.k))


Question = Choice | Noul | Score


@dataclass(frozen=True)
class Decision:
    """The result of one typed question: a full calibrated distribution.

    `top` is the argmax index into the declared option space; `confidence`
    is its probability. For Noul, `probs[1]` is P(yes)."""

    question: Question
    probs: tuple[float, ...]

    @property
    def top(self) -> int:
        return max(range(len(self.probs)), key=self.probs.__getitem__)

    @property
    def confidence(self) -> float:
        return self.probs[self.top]

    @property
    def yes(self) -> float:
        """P(yes) — only meaningful for Noul questions."""
        if not isinstance(self.question, Noul):
            raise TypeError("`.yes` is only defined for Noul questions")
        return self.probs[1]

"""Verdict (v1, one question per pass): a Laya/Jev-compatible typed-decision model.
The packed multi-question model used in the paper is verdict.mq.VerdictMQ.

An encoder backbone (default ModernBERT-base, Apache-2.0) reads
{question + rendered options}; a 2-layer head scores the hidden state at each
option's marker token; softmax over those scalars — divided by a learned
calibration temperature — is a calibrated distribution over exactly the
declared options. ONE bidirectional forward pass, no generation, no parsing,
no hallucination. Handles choice / noul / score with arbitrary option sets.

Because the encoder is bidirectional, each option's marker token attends to
the full input (question + every option), so a single pass scores them all —
this is why it is fast (tens of ms) and why the probabilities are jointly
normalized rather than computed option-by-option.
"""

from __future__ import annotations

import json
import os

import torch
import torch.nn as nn

from .types import Decision, Question

DEFAULT_BACKBONE = "answerdotai/ModernBERT-base"
OPT_TOKEN = "[OPT]"


def render(q: Question, fmt: str = "v1") -> str:
    """v1 (original): question + item text, THEN the options. Right-truncation at
    512 tokens cuts the options off long inputs (~20% of the Enron emails).
    v2: options first, then the question + item text, so truncation only ever
    removes the tail of the item (the layout Laya uses). New checkpoints default
    to v2; the format is stored in verdict_config.json so old ones still load."""
    opts = [f"{OPT_TOKEN} {i}: {opt}" for i, opt in enumerate(q.options)]
    if fmt == "v2":
        return "\n".join(["Options:"] + opts + ["Question:", q.question])
    return "\n".join([q.question, "Options:"] + opts)


class DecisionHead(nn.Module):
    def __init__(self, hidden: int):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(hidden, hidden // 2), nn.GELU(),
            nn.LayerNorm(hidden // 2), nn.Linear(hidden // 2, 1),
        )
        self._raw_temp = nn.Parameter(torch.tensor(0.5413))  # softplus->1.0

    @property
    def temperature(self):
        return nn.functional.softplus(self._raw_temp) + 1e-4

    def forward(self, states):  # (..., n_opt, hidden) -> (..., n_opt)
        return self.net(states).squeeze(-1) / self.temperature


class Verdict(nn.Module):
    def __init__(self, backbone, tokenizer, head, render_fmt="v2"):
        super().__init__()
        self.backbone = backbone
        self.tokenizer = tokenizer
        self.head = head
        self.render_fmt = render_fmt
        self.opt_id = tokenizer.convert_tokens_to_ids(OPT_TOKEN)

    @classmethod
    def from_pretrained(cls, path=DEFAULT_BACKBONE, *, device=None, dtype=torch.float32, render_fmt=None):
        from transformers import AutoModel, AutoTokenizer

        head_file = os.path.join(path, "verdict_head.pt")
        is_ckpt = os.path.isfile(head_file)
        vcfg = json.load(open(os.path.join(path, "verdict_config.json"))) if is_ckpt else {}
        backbone_id = vcfg["backbone"] if is_ckpt else path
        # old checkpoints predate the key and were trained with v1
        fmt = render_fmt or (vcfg.get("render", "v1") if is_ckpt else "v2")
        src = path if is_ckpt else backbone_id

        tok = AutoTokenizer.from_pretrained(src)
        backbone = AutoModel.from_pretrained(src if is_ckpt else backbone_id)
        if OPT_TOKEN not in tok.get_vocab():
            tok.add_special_tokens({"additional_special_tokens": [OPT_TOKEN]})
            backbone.resize_token_embeddings(len(tok))
        head = DecisionHead(backbone.config.hidden_size)
        model = cls(backbone, tok, head, render_fmt=fmt)
        model._backbone_id = backbone_id
        if is_ckpt:
            model.head.load_state_dict(torch.load(head_file, map_location="cpu")["head"])
        model.to(device or ("cuda" if torch.cuda.is_available() else "cpu")).to(dtype)
        model.eval()
        return model

    def save_pretrained(self, out):
        os.makedirs(out, exist_ok=True)
        self.backbone.save_pretrained(out)
        self.tokenizer.save_pretrained(out)
        torch.save({"head": self.head.state_dict()}, os.path.join(out, "verdict_head.pt"))
        cfg_path = os.path.join(out, "verdict_config.json")
        json.dump({"backbone": getattr(self, "_backbone_id", None) or self.backbone.config._name_or_path,
                   "render": self.render_fmt},
                  open(cfg_path, "w"), indent=2)

    def collate(self, questions, device=None):
        device = device or next(self.backbone.parameters()).device
        enc = self.tokenizer([render(q, self.render_fmt) for q in questions], return_tensors="pt",
                             padding=True, truncation=True, max_length=512).to(device)
        positions = []
        for i in range(len(questions)):
            ids = enc["input_ids"][i].tolist()
            positions.append([j for j, t in enumerate(ids) if t == self.opt_id])
        return enc, positions

    def logits_batch(self, questions):
        enc, positions = self.collate(questions)
        out = self.backbone(**enc).last_hidden_state  # (B, seq, hidden)
        res = []
        for i, pos in enumerate(positions):
            res.append(self.head(out[i, pos]))
        return res

    @torch.no_grad()
    def predict(self, q: Question) -> Decision:
        logits = self.logits_batch([q])[0]
        probs = torch.softmax(logits.float(), -1).tolist()
        return Decision(question=q, probs=tuple(probs))

    @torch.no_grad()
    def predict_batch(self, questions):
        return [Decision(question=q, probs=tuple(torch.softmax(lg.float(), -1).tolist()))
                for q, lg in zip(questions, self.logits_batch(questions))]

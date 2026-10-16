"""Verdict-MQ: "encode once, decide many" typed-decision model.

One packed forward pass answers every typed question asked about one state:

    [CLS] state ... [SEP] | block_1 | block_2 | ... | block_K
    block_k = "<type> question: <instructions>" [SEP] [OPT] opt_1 ... [OPT] opt_n

Structured attention (both ModernBERT global and sliding-window layers):
  * state tokens attend only to state tokens -> the state encoding is independent of
    the questions (it can be computed once and cached, and a question cannot change it),
    GIVEN identical retained state tokens: pack() truncates state to fit max_len minus the
    packed questions' length, so a state long enough to be truncated can retain FEWER tokens
    when packed with more questions than when answered alone or in a smaller group. The
    guarantee is therefore precise for identical retained tokens (verified below), not for
    the original untruncated state under arbitrary re-groupings of a long case. Empirically,
    truncation never triggered on any case in typed-decisions, RACE, BoolQ or MultiRC at
    max_len=2048 (checked directly against every reported run), so this does not affect any
    number in the paper, but callers packing longer states than we evaluated should confirm
    their own cases fit, or hold max_len well above the largest case they group;
  * block k attends to the state and to itself only -> the K answers are exactly the
    answers K separate single-question passes would give (no cross-question leakage),
    again given identical retained state tokens;
  * every option of a block gets the SAME position ids (options start at one shared
    offset after the question) and the sliding window is defined on position ids, so the
    option set is order-invariant BY CONSTRUCTION (permuting options permutes the outputs).
  * inside a block, question tokens see every option of the block, but each option's tokens
    (including its [OPT] marker) see only the state, the question and their OWN option. If
    markers could see all options, identical marker tokens at identical positions would get
    identical inputs and collapse to one representation (found and fixed 2026-09-23).
    Alternatives still reach each option indirectly through the question tokens.
Readout: the hidden state at each [OPT] marker plus a learned question-type embedding ->
MLP -> one logit per option -> softmax over the declared options. Score questions can
add an ordinal (CDF / EMD^2) loss.

Cost: one pass over |state| + sum_k |block_k| tokens instead of K passes over
|state| + |block_k| tokens.

Split depth (joint_layers = k > 0, DeFormer-style): the rules above hold in the lower L-k layers only. Their state
encoding is question-independent (and cacheable). For the top k layers every question gets its own copy of the
lower-layer state, and inside that copy the state tokens may attend to their question and its options, like the
question tokens do; options still see only the state, the question and themselves. Question independence and option-
order invariance still hold exactly; the state is read in light of each question in the top k layers. k = 0 is
the fully shared model; k = L is one question per pass (no sharing), the accuracy reference.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Sequence

import torch
import torch.nn as nn

OPT_TOKEN = "[OPT]"
QTYPE_ID = {"choice": 0, "noul": 1, "score": 2}


@dataclass
class MQQuestion:
    instructions: str
    options: Sequence[str]            # rendered option texts ("key: description")
    qtype: str = "choice"


@dataclass
class MQCase:
    state: str
    questions: list = field(default_factory=list)   # list[MQQuestion]


class MQHead(nn.Module):
    """Readout over one question's option markers. With mixer_layers > 0, a small Transformer encoder WITHOUT
    positional encodings lets the options of a question attend to each other before scoring. Self-attention over an
    unordered set is permutation-equivariant, so order invariance is preserved while options can be compared
    (the relative-choice ability that rule 3 of the attention mask removes from the encoder)."""

    def __init__(self, hidden, mixer_layers=0, mixer_heads=8, match=False):
        super().__init__()
        self.mixer_layers = mixer_layers
        # match=True: score each option from [marker; question summary; marker * summary] (the question's [SEP], which
        # sees the state, the question and every option), so the context can interact multiplicatively with the option
        # identity instead of being added to both options of a yes/no question and cancelling in the softmax.
        self.match = match
        self.type_emb = nn.Embedding(len(QTYPE_ID), hidden)
        nn.init.zeros_(self.type_emb.weight)
        self.mixer = None
        if mixer_layers:
            layer = nn.TransformerEncoderLayer(d_model=hidden, nhead=mixer_heads, dim_feedforward=2 * hidden,
                                               dropout=0.1, batch_first=True, norm_first=True)
            self.mixer = nn.TransformerEncoder(layer, num_layers=mixer_layers)
        d_in = 3 * hidden if match else hidden
        self.net = nn.Sequential(nn.Linear(d_in, hidden // 2), nn.GELU(), nn.LayerNorm(hidden // 2), nn.Linear(hidden // 2, 1))

    def forward(self, states, qtype_id, qstate=None):   # (n_opt, hidden), int, (hidden,) -> (n_opt,)
        x = states + self.type_emb.weight[qtype_id]
        if self.mixer is not None:
            x = x + self.mixer(x.unsqueeze(0)).squeeze(0)
        if self.match:
            q = qstate.unsqueeze(0).expand_as(x)
            x = torch.cat([x, q, x * q], -1)
        return self.net(x).squeeze(-1)


class VerdictMQ(nn.Module):
    def __init__(self, backbone, tokenizer, head, max_len=2048, max_opt_tokens=48, backbone_id=None,
                 shared_option_pos=True, joint_layers=0, readout="marker", marker="opt"):
        super().__init__()
        # marker: the token that starts every option and whose state is read out. "opt" = a NEW [OPT] token (the
        # original design). Its resized embedding is out of distribution and, measured with a frozen encoder, removes the
        # linearly readable answer from the passage+question tokens (BoolQ probe 0.76 -> 0.61); an existing special token
        # ([MASK], [CLS], [SEP]) keeps it (0.75-0.79). (paper, Section 3).
        self.marker = marker
        # readout: marker = option marker only; match = marker x the question's [SEP]; pool = marker x the MEAN of the
        # question's context (state + question tokens), the pooling standard sequence classifiers use
        self.readout = readout
        assert 0 <= joint_layers <= len(backbone.layers), joint_layers
        self.joint_layers = joint_layers              # top layers where the state reads each question (0 = shared)
        self.backbone, self.tokenizer, self.head = backbone, tokenizer, head
        self.max_len, self.max_opt_tokens = max_len, max_opt_tokens
        self.shared_option_pos = shared_option_pos   # False = ablation: options get consecutive positions
        self.opt_id = {"opt": lambda: tokenizer.convert_tokens_to_ids(OPT_TOKEN), "mask": lambda: tokenizer.mask_token_id,
                       "cls": lambda: tokenizer.cls_token_id, "sep": lambda: tokenizer.sep_token_id}[marker]()
        self.window = int(getattr(backbone.config, "local_attention", 128)) // 2
        self._backbone_id = backbone_id

    # ------------------------------------------------------------------ io
    @classmethod
    def from_pretrained(cls, path, *, device=None, dtype=torch.float32, max_len=2048, mixer_layers=None,
                        joint_layers=None, readout=None, marker=None):
        from transformers import AutoModel, AutoTokenizer
        head_file = os.path.join(path, "mq_head.pt")
        is_ckpt = os.path.isfile(head_file)
        vcfg = json.load(open(os.path.join(path, "verdict_config.json"))) if is_ckpt else {}
        tok = AutoTokenizer.from_pretrained(path)
        backbone = AutoModel.from_pretrained(path, attn_implementation="sdpa")
        mk = marker or vcfg.get("marker", "opt")
        if mk == "opt" and OPT_TOKEN not in tok.get_vocab():
            tok.add_special_tokens({"additional_special_tokens": [OPT_TOKEN]})
            backbone.resize_token_embeddings(len(tok))
        ml = mixer_layers if mixer_layers is not None else vcfg.get("mixer_layers", 0)
        ro = readout or vcfg.get("readout", "marker")
        head = MQHead(backbone.config.hidden_size, mixer_layers=ml, match=(ro in ("match", "pool")))
        if is_ckpt:
            head.load_state_dict(torch.load(head_file, map_location="cpu"))
        m = cls(backbone, tok, head, max_len=vcfg.get("max_len", max_len),
                backbone_id=vcfg.get("backbone", path), shared_option_pos=vcfg.get("shared_option_pos", True),
                joint_layers=joint_layers if joint_layers is not None else vcfg.get("joint_layers", 0), readout=ro,
                marker=mk)
        m.to(device or ("cuda" if torch.cuda.is_available() else "cpu")).to(dtype)
        m.eval()
        return m

    def save_pretrained(self, out):
        os.makedirs(out, exist_ok=True)
        self.backbone.save_pretrained(out)
        self.tokenizer.save_pretrained(out)
        torch.save(self.head.state_dict(), os.path.join(out, "mq_head.pt"))
        json.dump({"arch": "mq", "backbone": self._backbone_id or self.backbone.config._name_or_path,
                   "max_len": self.max_len, "shared_option_pos": self.shared_option_pos,
                   "mixer_layers": self.head.mixer_layers, "joint_layers": self.joint_layers,
                   "readout": self.readout, "marker": self.marker},
                  open(os.path.join(out, "verdict_config.json"), "w"), indent=2)

    # ------------------------------------------------------------------ packing
    def _tok(self, text):
        return self.tokenizer(text, add_special_tokens=False)["input_ids"]

    def pack(self, case: MQCase):
        """-> dict(ids, pos, blk, markers=[[token idx per option] per question])

        The `room = max(16, ...)` floor below only protects the STATE from a negative/zero token budget; it does
        NOT cap the combined length of the packed questions and options, which pack() never truncates. If a case
        packs enough questions/options that they alone exceed roughly max_len - 18 tokens, the returned sequence
        is LONGER than max_len regardless of how little state room is left (found by independent review,
        2026-09-28: packing one MultiRC passage's full ~58-question set unchunked reaches 6,378 tokens against
        max_len=2048). Every real training/eval path goes through mq_data.to_cases()'s max_questions=16 chunking
        BEFORE calling pack(), which keeps every reported case well under max_len (verified: worst observed real
        case is 1,481 tokens -- scripts/scan_truncation.py) -- but pack() itself does not enforce this, so we
        assert it here rather than silently return an oversized, position-id-invalid sequence to a caller that
        skips to_cases()."""
        tok = self.tokenizer
        blocks = []
        for q in case.questions:
            qids = self._tok(f"{q.qtype} question: {q.instructions}")[:160] + [tok.sep_token_id]
            opts = [[self.opt_id] + self._tok(" " + o)[: self.max_opt_tokens - 1] for o in q.options]
            blocks.append((qids, opts, QTYPE_ID.get(q.qtype, 0)))
        block_len = sum(len(qi) + sum(len(o) for o in op) for qi, op, _ in blocks)
        room = max(16, self.max_len - block_len - 2)
        if block_len + 2 + 16 > self.max_len:
            raise ValueError(f"pack(): {len(case.questions)} packed questions need {block_len} tokens, leaving no "
                              f"room for state within max_len={self.max_len}; split this case into smaller chunks "
                              f"(e.g. mq_data.to_cases(..., max_questions=N)) before packing.")
        sids = [tok.cls_token_id] + self._tok(case.state)[:room] + [tok.sep_token_id]
        ids, pos, blk, seg = list(sids), list(range(len(sids))), [0] * len(sids), [0] * len(sids)
        Ls = len(sids)
        markers, qtypes, qseps = [], [], []
        for b, (qids, opts, qt) in enumerate(blocks, start=1):
            ids += qids; pos += list(range(Ls, Ls + len(qids))); blk += [b] * len(qids); seg += [0] * len(qids)
            qseps.append(len(ids) - 1)              # the question's [SEP]: sees the state, the question and all options
            p1 = Ls + len(qids)                     # shared start position for every option
            mk = []
            for j, o in enumerate(opts, start=1):
                mk.append(len(ids))
                ids += o; pos += list(range(p1, p1 + len(o))); blk += [b] * len(o); seg += [j] * len(o)
                if not self.shared_option_pos:
                    p1 += len(o)                    # ablation: option order becomes visible
            markers.append(mk); qtypes.append(qt)
        return {"ids": ids, "pos": pos, "blk": blk, "seg": seg, "markers": markers, "qtypes": qtypes, "qseps": qseps}

    def collate(self, cases, device=None):
        device = device or next(self.backbone.parameters()).device
        packs = [self.pack(c) for c in cases]
        B, T = len(packs), max(len(p["ids"]) for p in packs)
        pad = self.tokenizer.pad_token_id
        ids = torch.full((B, T), pad, dtype=torch.long)
        pos = torch.zeros((B, T), dtype=torch.long)
        blk = torch.full((B, T), -1, dtype=torch.long)
        seg = torch.zeros((B, T), dtype=torch.long)
        for i, p in enumerate(packs):
            n = len(p["ids"])
            ids[i, :n] = torch.tensor(p["ids"]); pos[i, :n] = torch.tensor(p["pos"])
            blk[i, :n] = torch.tensor(p["blk"]); seg[i, :n] = torch.tensor(p["seg"])
        bq, bk = blk.unsqueeze(2), blk.unsqueeze(1)                          # (B,T,1), (B,1,T)
        sq, sk = seg.unsqueeze(2), seg.unsqueeze(1)
        real_q, real_k = bq >= 0, bk >= 0
        same_block = (bq == bk) & (bq > 0)
        in_block = same_block & ((sq == 0) | (sk == 0) | (sq == sk))          # question<->all; option->question+own
        allowed = real_q & real_k & ((bk == 0) | in_block)                    # state->state; block->state+in_block
        allowed = allowed & ~((bq == 0) & (bk > 0))                           # state never sees questions
        eye = torch.eye(T, dtype=torch.bool).unsqueeze(0)
        full = allowed | eye                                                  # pads attend to themselves only
        dist = (pos.unsqueeze(2) - pos.unsqueeze(1)).abs()
        local = (allowed & (dist <= self.window)) | eye
        masks = {"full_attention": full.unsqueeze(1).to(device), "sliding_attention": local.unsqueeze(1).to(device)}
        return ids.to(device), pos.to(device), masks, packs

    # ------------------------------------------------------------------ forward
    def logits(self, cases):
        """-> list over cases of list over questions of (n_opt,) logits"""
        ids, pos, masks, packs = self.collate(cases)
        if self.joint_layers:
            return self._logits_split(ids, pos, masks, packs)
        h = self.backbone(input_ids=ids, position_ids=pos, attention_mask=masks).last_hidden_state
        out = []
        for i, p in enumerate(packs):
            if self.readout == "pool":
                blk = torch.tensor(p["blk"], device=h.device); seg = torch.tensor(p["seg"], device=h.device)
                ctx = [((blk == 0) | ((blk == b) & (seg == 0))).nonzero().squeeze(1) for b in range(1, len(p["markers"]) + 1)]
                qv = [h[i, c].mean(0) for c in ctx]
            else:
                qv = [h[i, qs] for qs in p["qseps"]]
            out.append([self.head(h[i, mk], qt, v) for mk, qt, v in zip(p["markers"], p["qtypes"], qv)])
        return out

    def _logits_split(self, ids, pos, masks, packs):
        """Lower L-k layers on the packed sequence (shared, question-independent state); then one row per question,
        [state copy | block], through the top k layers."""
        bb = self.backbone
        n_low = len(bb.layers) - self.joint_layers
        h = bb.embeddings(input_ids=ids)
        if n_low:
            pe = {t: bb.rotary_emb(h, pos, t) for t in set(bb.config.layer_types)}
            for layer in bb.layers[:n_low]:
                h = layer(h, attention_mask=masks[layer.attention_type], position_embeddings=pe[layer.attention_type])
        dev = h.device
        rows, rpos, rseg, where = [], [], [], []           # where: (case, question, marker idx in row)
        for i, p in enumerate(packs):
            blk = torch.tensor(p["blk"], device=dev); seg = torch.tensor(p["seg"], device=dev)
            st = (blk == 0).nonzero().squeeze(1)
            for b, (mk, qs) in enumerate(zip(p["markers"], p["qseps"]), start=1):
                bi = (blk == b).nonzero().squeeze(1)
                idx = torch.cat([st, bi])
                rows.append(h[i, idx]); rpos.append(pos[i, idx]); rseg.append(seg[idx])
                off = len(st) - int(bi[0])
                where.append((i, b - 1, torch.tensor(mk, device=dev) + off, qs + off))
        R, T = len(rows), max(len(r) for r in rows)
        h2 = torch.nn.utils.rnn.pad_sequence(rows, batch_first=True)
        pos2 = torch.nn.utils.rnn.pad_sequence(rpos, batch_first=True)
        seg2 = torch.nn.utils.rnn.pad_sequence(rseg, batch_first=True)
        real = torch.nn.utils.rnn.pad_sequence([torch.ones(len(r), dtype=torch.bool, device=dev) for r in rows], batch_first=True)
        sq, sk = seg2.unsqueeze(2), seg2.unsqueeze(1)
        # context (state + question, seg 0) <-> everything in the row; option -> context + its own tokens
        allowed = real.unsqueeze(2) & real.unsqueeze(1) & ((sq == 0) | (sk == 0) | (sq == sk))
        eye = torch.eye(T, dtype=torch.bool, device=dev).unsqueeze(0)
        dist = (pos2.unsqueeze(2) - pos2.unsqueeze(1)).abs()
        m2 = {"full_attention": (allowed | eye).unsqueeze(1), "sliding_attention": ((allowed & (dist <= self.window)) | eye).unsqueeze(1)}
        pe2 = {t: bb.rotary_emb(h2, pos2, t) for t in set(bb.config.layer_types)}
        for layer in bb.layers[n_low:]:
            h2 = layer(h2, attention_mask=m2[layer.attention_type], position_embeddings=pe2[layer.attention_type])
        h2 = bb.final_norm(h2)
        out = [[None] * len(p["markers"]) for p in packs]
        ctxm = ((seg2 == 0) & real).unsqueeze(-1).to(h2.dtype)                   # row context = state copy + question
        pooled = (h2 * ctxm).sum(1) / ctxm.sum(1).clamp(min=1)
        for r, (i, q, mk, qs) in enumerate(where):
            out[i][q] = self.head(h2[r, mk], packs[i]["qtypes"][q], pooled[r] if self.readout == "pool" else h2[r, qs])
        return out

    @torch.no_grad()
    def predict(self, cases):
        return [[torch.softmax(lg.float(), -1).tolist() for lg in case] for case in self.logits(cases)]


def ordinal_emd2(logits, target_probs):
    """Squared earth-mover distance between predicted and target distributions over ordered levels."""
    p = torch.softmax(logits.float(), -1)
    return ((torch.cumsum(p, -1) - torch.cumsum(target_probs, -1)) ** 2).sum()

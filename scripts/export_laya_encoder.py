"""Export Laya's ModernBERT encoder (Apache-2.0) as a plain HF checkpoint so Verdict-MQ can start from the
same pre-trained weights Laya uses: python3 scripts/export_laya_encoder.py --subfolder default --out out/laya-encoder"""
import argparse
import laya

ap = argparse.ArgumentParser()
ap.add_argument("--subfolder", default="default")
ap.add_argument("--out", default="out/laya-encoder")
a = ap.parse_args()
ag = laya.load("convaiinnovations/laya", subfolder=None if a.subfolder == "default" else a.subfolder, device="cpu")
ag.model.encoder.float().save_pretrained(a.out)
ag.tok.save_pretrained(a.out)
print("exported", type(ag.model.encoder).__name__, sum(p.numel() for p in ag.model.encoder.parameters()) // 1_000_000, "M ->", a.out)

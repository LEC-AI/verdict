"""Write a recalibrated copy of a prediction dump: fits one temperature on the FIT half (case-level split, same
convention as calibration_temp_scale.py) and applies it to EVERY row (fit half included, so the output dump can
feed autonomy_from_preds.py's own independent fit/eval split unchanged) -- lets the held-out autonomy dial be
recomputed on calibrated confidences instead of raw ones (found missing by independent review, 2026-09-27: raw-
confidence coverage/accuracy dominance and calibrated ECE were being combined into one deployment story without
checking whether dominance survives on calibrated confidences).

  python3 scripts/apply_calibration.py --in preds_laya_td.jsonl --out preds_laya_td_calibrated.jsonl
"""
import argparse
import json

from calibration_temp_scale import fit_side, fit_temperature, load, scaled_probs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = load(a.inp)
    fit = [r for r in rows if fit_side(r)]
    T = fit_temperature(fit)
    with open(a.out, "w") as f:
        for r in rows:
            sp = scaled_probs(r["probs"], T)
            r2 = dict(r); r2["conf"] = max(sp); r2["probs"] = sp
            f.write(json.dumps(r2) + "\n")
    print(f"wrote {a.out}: {len(rows)} rows, fitted T={T:.3f}")


if __name__ == "__main__":
    main()

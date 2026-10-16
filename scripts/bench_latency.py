"""Latency / throughput / cost comparison: Verdict vs an LLM-judge.

This produces the paper's efficiency table — the counterpart to the accuracy
table in eval_baseline.py. It measures how fast a single typed decision comes
out of Verdict (one bidirectional forward pass, no generation) on CPU and on
GPU across batch sizes, and how fast the same decision comes out of a
generative LLM-judge over an OpenAI-compatible endpoint. It then turns those
speeds into an estimated $/1000 decisions for each system.

  python3 scripts/bench_latency.py \
      --ckpt out/verdict-base \
      --endpoint http://localhost:11434/v1 --model qwen2.5:7b-instruct \
      --n 256 --out RESULTS_latency.json --llm-cost-per-1k 0.50

Outputs (both written; markdown also echoed to stdout with a short summary):
  * <out>.json   — machine-readable: per-device/per-batch ms/decision and
                   decisions/sec for Verdict, LLM-judge latency, and the
                   $/1000-decisions cost comparison + headline speedups.
  * <out>.md     — the same as a markdown table, ready to drop into a results log.

Notes on method:
  * GPU timings are WARM (warmup passes first) and CUDA-synchronized around the
    timed region; each config is repeated (--repeats) and the MEDIAN is kept.
  * "ms/decision" and "decisions/sec" at batch B are the end-to-end wall time
    (tokenization + forward + softmax + readback) to process all --n items in
    batches of B, divided by --n. Batch 1 is the latency-critical single-shot
    number; larger batches show throughput headroom.
  * Latency is architecture-bound, so even a default/untrained backbone gives
    representative timings; pass a real --ckpt to time the shipped model.
  * If CUDA is unavailable the GPU rows are skipped; if the endpoint is
    unreachable the LLM row is marked so and the Verdict rows still print.
  * This script does NOT run any training/eval — it only times forward passes
    and endpoint round-trips.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import random
import sys
import time
import urllib.request
from datetime import datetime, timezone

import torch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from verdict import Choice, Noul, Score, Verdict  # noqa: E402
from verdict.data import load_jsonl  # noqa: E402


# --- items under decision (shared by Verdict and the LLM, for parity) --------

def _synthetic_items():
    """Representative org-decision items, used only when no cached val splits
    are found. Kept deliberately varied in length so tokenization cost is
    realistic; labels are irrelevant here (we time, we don't score)."""
    base = [
        dict(qtype="choice",
             question="Which desk should handle this incoming item?\n\n"
                      "Quarterly cloud spend overran budget by 12% after the "
                      "migration; finance wants a variance note before board prep.",
             options=["World", "Sports", "Business", "Sci/Tech"]),
        dict(qtype="noul",
             question="Is the sender's sentiment in this message positive?\n\n"
                      "Thanks for the quick turnaround on the fix — the team is "
                      "unblocked and shipping again today.",
             options=["no", "yes"]),
        dict(qtype="choice",
             question="Route this customer message to the correct banking service intent:\n\n"
                      "My card was declined abroad even though I have funds, and I "
                      "did not get the usual verification text.",
             options=["card_declined", "verify_source_of_funds",
                      "lost_or_stolen_card", "top_up_failed"]),
        dict(qtype="score",
             question="How urgent is this message for handling/prioritization "
                      "(0=none, 3=critical)?\n\n"
                      "Production API is returning 500s for all EU customers and "
                      "the on-call pager is not acknowledging.",
             options=["0", "1", "2", "3"]),
        dict(qtype="choice",
             question="What is the dominant emotion in this message?\n\n"
                      "I cannot believe this happened again after you promised it "
                      "was fixed last week.",
             options=["sadness", "joy", "love", "anger", "fear", "surprise"]),
        dict(qtype="noul",
             question="Does this email need a reply from a human today?\n\n"
                      "Automated receipt: your subscription renewed successfully. "
                      "No action required.",
             options=["no", "yes"]),
    ]
    return base


def build_items(n, cache_dir, seed):
    """Assemble n decision items. Prefer real cached OrgBench val records (so
    text lengths match the shipped benchmark); fall back to synthetic."""
    items = []
    for f in sorted(glob.glob(os.path.join(cache_dir, "*_val.jsonl"))):
        try:
            for rec in load_jsonl(f):
                items.append(dict(question=rec.question,
                                  options=list(rec.options), qtype=rec.qtype))
        except Exception:
            continue
    if not items:
        items = _synthetic_items()
    rng = random.Random(seed)
    rng.shuffle(items)
    if len(items) < n:
        items = items * (n // len(items) + 1)
    return items[:n]


def to_question(item):
    q, opts, qt = item["question"], item["options"], item["qtype"]
    if qt == "noul":
        return Noul(q)
    if qt == "score":
        return Score(q, k=len(opts))
    return Choice(q, opts)


def render_prompt(item):
    """LLM-judge prompt — identical framing to scripts/eval_baseline.py so the
    two systems see the same decision."""
    opts = "\n".join(f"{i}: {o}" for i, o in enumerate(item["options"]))
    return (f"{item['question']}\n\nOptions:\n{opts}\n\n"
            f"Answer with ONLY the number of the single best option "
            f"(0-{len(item['options']) - 1}). No words, just the number.")


def query(endpoint, model, prompt, timeout=60):
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0, "max_tokens": 8,
    }).encode()
    req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions",
                                 data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        out = json.loads(r.read())
    return out["choices"][0]["message"]["content"]


# --- timing helpers ----------------------------------------------------------

def _sync(device):
    if str(device).startswith("cuda"):
        torch.cuda.synchronize()


def _batches(seq, b):
    for i in range(0, len(seq), b):
        yield seq[i:i + b]


def time_verdict(model, questions, batch_size, warmup, repeats, device):
    """Warm, synchronized, median-of-repeats timing at one batch size."""
    warm = questions[:batch_size] if len(questions) >= batch_size else questions
    for _ in range(max(warmup, 0)):
        model.predict_batch(warm)
    _sync(device)

    elapsed = []
    for _ in range(max(repeats, 1)):
        _sync(device)
        t0 = time.perf_counter()
        for ch in _batches(questions, batch_size):
            model.predict_batch(ch)
        _sync(device)
        elapsed.append(time.perf_counter() - t0)
    elapsed.sort()
    med = elapsed[len(elapsed) // 2]
    n = len(questions)
    return dict(batch_size=batch_size, n=n,
                ms_per_decision=1000.0 * med / n,
                decisions_per_sec=n / med,
                median_elapsed_s=med,
                all_elapsed_s=elapsed)


def measure_llm(endpoint, model, items, n_samples, timeout):
    """Sequential per-decision latency of the LLM-judge endpoint."""
    n = min(n_samples, len(items))
    lat, errors, first_err = [], 0, None
    for it in items[:n]:
        t0 = time.perf_counter()
        try:
            query(endpoint, model, render_prompt(it), timeout)
        except Exception as e:  # unreachable / timeout / bad response
            errors += 1
            if first_err is None:
                first_err = f"{type(e).__name__}: {e}"
            continue
        lat.append(time.perf_counter() - t0)
    if not lat:
        return dict(ok=False, n=n, errors=errors,
                    error=first_err or "no successful calls")
    lat.sort()
    mean = sum(lat) / len(lat)
    return dict(ok=True, n=len(lat), errors=errors,
                ms_per_decision_mean=1000.0 * mean,
                ms_per_decision_p50=1000.0 * lat[len(lat) // 2],
                ms_per_decision_p90=1000.0 * lat[min(len(lat) - 1, int(0.9 * len(lat)))],
                decisions_per_sec=1.0 / mean)


def electricity_floor_usd_per_1k(dps, power_w, kwh_cost):
    """Lower bound on Verdict's local compute cost: energy to run the
    device flat-out for 1000 decisions at the measured throughput."""
    if not dps or dps <= 0:
        return None
    sec_per_1k = 1000.0 / dps
    kwh = (power_w / 1000.0) * (sec_per_1k / 3600.0)
    return kwh * kwh_cost


# --- rendering ---------------------------------------------------------------

_DTYPES = {"float32": torch.float32, "float16": torch.float16,
           "bfloat16": torch.bfloat16}


def build_markdown(result):
    m = result["meta"]
    lines = [f"# Verdict latency / throughput / cost — {m['timestamp']}", ""]
    lines += [
        f"- **Verdict ckpt:** `{m['ckpt']}`  ",
        f"- **LLM-judge:** `{m['llm_model']}` @ `{m['endpoint'] or '(skipped)'}`  ",
        f"- **Items:** n={m['n']} (source: {m['item_source']}), "
        f"batches={m['batch_sizes']}, warmup={m['warmup']}, repeats={m['repeats']} (median)  ",
        f"- **torch** {m['torch']} · cpu-threads={m['cpu_threads']}"
        + (f" · gpu={m['gpu_name']}" if m.get('gpu_name') else " · gpu=none"),
        "",
        "## Verdict — per-decision latency (one forward pass, no generation)",
        "",
        "| device | dtype | batch | ms / decision | decisions / sec |",
        "|---|---|---:|---:|---:|",
    ]
    for dev in result["verdict"]:
        d = result["verdict"][dev]
        for b in d["by_batch"]:
            r = d["by_batch"][b]
            lines.append(f"| {d['device_label']} | {d['dtype']} | {b} | "
                         f"{r['ms_per_decision']:.2f} | {r['decisions_per_sec']:,.0f} |")
    lines += ["", "## LLM-judge — per-decision latency (generative, sequential)", ""]
    llm = result["llm_judge"]
    if llm.get("ok"):
        lines += [
            "| model | mean ms | p50 ms | p90 ms | decisions / sec |",
            "|---|---:|---:|---:|---:|",
            f"| {m['llm_model']} | {llm['ms_per_decision_mean']:.0f} | "
            f"{llm['ms_per_decision_p50']:.0f} | {llm['ms_per_decision_p90']:.0f} | "
            f"{llm['decisions_per_sec']:.2f} |",
            f"  _(n={llm['n']} successful calls, {llm['errors']} errors)_",
        ]
    else:
        lines.append(f"_LLM-judge not measured: {llm.get('error', 'skipped')} "
                     f"(errors={llm.get('errors', 0)}, tried n={llm.get('n', 0)})._")

    cost = result["cost"]
    lines += ["", "## Cost — estimated $ / 1000 decisions", "",
              "| system | $/1000 decisions | basis |",
              "|---|---:|---|",
              f"| Verdict | ${cost['verdict_usd_per_1k']:.4f} | "
              f"{cost['verdict_assumption']} |"]
    floor = cost.get("verdict_electricity_floor_usd_per_1k")
    if floor is not None:
        lines.append(f"| Verdict (electricity floor) | ${floor:.4f} | "
                     f"{cost['verdict_electricity_basis']} |")
    lines.append(f"| Cloud LLM ({m['llm_model']}) | ${cost['cloud_llm_usd_per_1k']:.4f} | "
                 f"--llm-cost-per-1k (user-supplied $/1000 decisions) |")

    h = result["headline"]
    lines += ["", "## Headline", ""]
    if h.get("verdict_batch1_ms") is not None:
        lines.append(f"- Verdict single decision: "
                     f"**{h['verdict_batch1_ms']:.2f} ms** on {h['verdict_batch1_device']}.")
    lines.append(f"- Verdict peak throughput: **{h['verdict_best_dps']:,.0f} decisions/sec** "
                 f"({h['verdict_best_device']}, batch {h['verdict_best_batch']}).")
    if h.get("llm_ms") is not None:
        lines.append(f"- LLM-judge: {h['llm_ms']:.0f} ms/decision "
                     f"({h['llm_dps']:.2f} decisions/sec).")
        if h.get("speedup_latency") is not None:
            lines.append(f"- **Speed:** Verdict is ~**{h['speedup_latency']:.0f}x** lower "
                         f"single-decision latency and ~**{h['speedup_throughput']:,.0f}x** "
                         f"higher throughput than the LLM-judge.")
    if h.get("cost_savings_per_1k") is not None:
        lines.append(f"- **Cost:** ~${h['cost_savings_per_1k']:.4f} saved per 1000 decisions "
                     f"vs the cloud LLM (Verdict local compute assumed negligible).")
    lines.append("")
    return "\n".join(lines)


# --- main --------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(description="Verdict vs LLM-judge latency/throughput/cost.")
    ap.add_argument("--ckpt", default="out/verdict-base",
                    help="Verdict checkpoint dir (falls back to default backbone if absent).")
    ap.add_argument("--endpoint", default="http://localhost:11434/v1",
                    help="OpenAI-compatible endpoint for the LLM-judge ('' to skip).")
    ap.add_argument("--model", default="qwen2.5:7b-instruct", help="LLM-judge model name.")
    ap.add_argument("--n", type=int, default=256, help="Decisions to time for Verdict.")
    ap.add_argument("--out", default="RESULTS_latency.json",
                    help="Output path; JSON + a sibling .md are written.")
    ap.add_argument("--llm-cost-per-1k", type=float, default=0.50,
                    help="Cloud LLM cost in $ per 1000 decisions (user-supplied estimate; "
                         "derive from your provider's input+output token price × tokens/decision).")
    # timing / device knobs
    ap.add_argument("--batch-sizes", default="1,8,32")
    ap.add_argument("--device", default="auto", choices=["auto", "cpu", "cuda"],
                    help="'auto' times CPU and (if present) CUDA.")
    ap.add_argument("--dtype", default="float32", choices=list(_DTYPES),
                    help="dtype for the CUDA run; CPU is always float32.")
    ap.add_argument("--warmup", type=int, default=3)
    ap.add_argument("--repeats", type=int, default=3)
    ap.add_argument("--llm-samples", type=int, default=50,
                    help="How many endpoint round-trips to time (LLM is slow/costly).")
    ap.add_argument("--llm-timeout", type=int, default=60)
    ap.add_argument("--cache-dir", default="data/jsonl")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--verdict-power-w", type=float, default=350.0,
                    help="Assumed device power for the electricity-floor cost estimate.")
    ap.add_argument("--kwh-cost", type=float, default=0.15,
                    help="Assumed $/kWh for the electricity-floor cost estimate.")
    args = ap.parse_args()

    random.seed(args.seed)
    torch.manual_seed(args.seed)
    batch_sizes = [int(x) for x in args.batch_sizes.split(",") if x.strip()]

    items = build_items(args.n, args.cache_dir, args.seed)
    item_source = ("cached OrgBench val splits"
                   if glob.glob(os.path.join(args.cache_dir, "*_val.jsonl"))
                   else "synthetic (no cached splits found)")
    questions = [to_question(it) for it in items]

    # which devices to time
    cuda_ok = torch.cuda.is_available()
    devices = []
    if args.device in ("auto", "cpu"):
        devices.append("cpu")
    if args.device in ("auto", "cuda"):
        if cuda_ok:
            devices.append("cuda")
        elif args.device == "cuda":
            print("WARNING: --device cuda requested but CUDA unavailable; timing CPU only.",
                  flush=True)
            if "cpu" not in devices:
                devices.append("cpu")

    verdict_out = {}
    best = dict(dps=-1.0, device=None, batch=None)
    batch1 = {}  # device -> ms
    for dev in devices:
        dt = torch.float32 if dev == "cpu" else _DTYPES[args.dtype]
        print(f"[verdict] loading on {dev} ({dt})...", flush=True)
        model = Verdict.from_pretrained(args.ckpt, device=dev, dtype=dt)
        label = dev + (f":{torch.cuda.get_device_name(0)}" if dev == "cuda" else "")
        by_batch = {}
        for b in batch_sizes:
            r = time_verdict(model, questions, b, args.warmup, args.repeats, dev)
            by_batch[str(b)] = r
            print(f"[verdict] {dev} batch={b}: {r['ms_per_decision']:.2f} ms/dec, "
                  f"{r['decisions_per_sec']:,.0f} dec/s", flush=True)
            if r["decisions_per_sec"] > best["dps"]:
                best = dict(dps=r["decisions_per_sec"], device=dev, batch=b)
            if b == 1:
                batch1[dev] = r["ms_per_decision"]
        verdict_out[dev] = dict(device_label=label, dtype=str(dt).replace("torch.", ""),
                                by_batch=by_batch)
        del model
        if dev == "cuda":
            torch.cuda.empty_cache()

    # LLM-judge
    if args.endpoint:
        print(f"[llm] timing {args.model} @ {args.endpoint} "
              f"(<= {args.llm_samples} calls)...", flush=True)
        llm = measure_llm(args.endpoint, args.model, items, args.llm_samples, args.llm_timeout)
    else:
        llm = dict(ok=False, error="endpoint empty (skipped)", errors=0, n=0)

    # cost model
    verdict_assumption = ("amortized local compute assumed negligible "
                          "(owned hardware, no per-call fee)")
    floor = electricity_floor_usd_per_1k(best["dps"], args.verdict_power_w, args.kwh_cost)
    cost = dict(
        verdict_usd_per_1k=0.0,
        verdict_assumption=verdict_assumption,
        verdict_electricity_floor_usd_per_1k=floor,
        verdict_electricity_basis=(f"{args.verdict_power_w:.0f} W @ ${args.kwh_cost:.2f}/kWh "
                                   f"at {best['dps']:,.0f} dec/s ({best['device']})"),
        cloud_llm_usd_per_1k=args.llm_cost_per_1k,
    )

    # headline
    b1_dev = "cuda" if "cuda" in batch1 else ("cpu" if "cpu" in batch1 else None)
    b1_ms = batch1.get(b1_dev) if b1_dev else None
    headline = dict(
        verdict_batch1_ms=b1_ms,
        verdict_batch1_device=b1_dev,
        verdict_best_dps=best["dps"],
        verdict_best_device=best["device"],
        verdict_best_batch=best["batch"],
        llm_ms=llm["ms_per_decision_mean"] if llm.get("ok") else None,
        llm_dps=llm["decisions_per_sec"] if llm.get("ok") else None,
    )
    if llm.get("ok") and b1_ms:
        headline["speedup_latency"] = llm["ms_per_decision_mean"] / b1_ms
        headline["speedup_throughput"] = best["dps"] / llm["decisions_per_sec"]
    headline["cost_savings_per_1k"] = (args.llm_cost_per_1k - 0.0) if args.endpoint else None

    result = dict(
        meta=dict(
            timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
            ckpt=args.ckpt, endpoint=args.endpoint, llm_model=args.model,
            n=args.n, item_source=item_source, batch_sizes=batch_sizes,
            warmup=args.warmup, repeats=args.repeats, dtype=args.dtype,
            torch=torch.__version__, cpu_threads=torch.get_num_threads(),
            gpu_name=torch.cuda.get_device_name(0) if cuda_ok else None,
            llm_samples=args.llm_samples,
            cost_note=("cloud_llm_usd_per_1k is user-supplied; derive as "
                       "(input_tokens+output_tokens)/1000 * price_per_1k_tokens "
                       "* 1000 decisions, or provider's per-request price * 1000."),
        ),
        verdict=verdict_out,
        llm_judge=llm,
        cost=cost,
        headline=headline,
    )

    stem, ext = os.path.splitext(args.out)
    json_path = args.out if ext == ".json" else stem + ".json"
    md_path = args.out if ext == ".md" else stem + ".md"
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    md = build_markdown(result)
    with open(md_path, "w") as f:
        f.write(md)

    print("\n" + md, flush=True)
    print(f"\nwrote {json_path} and {md_path}", flush=True)


if __name__ == "__main__":
    main()

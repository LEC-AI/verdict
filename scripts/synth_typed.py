"""Synthetic multi-workflow typed-decision corpus (the pre-training data Laya-class
models rely on), built with a strong local teacher. Mirrors the typed-decisions
recipe (latent factor skeleton -> rendered state -> soft teacher labels) on
OTHER workflows only, so a model trained on it can be scored zero-shot
("generalist" mode) on LocalLLaMA/typed-decisions.

Stages (each resumable, all outputs under --out-dir, default data/synth):
  catalog  -> catalog.json         workflows: description, state fields, latent factors, 5 typed questions
  cases    -> cases.jsonl          one rendered JSON state per sampled factor skeleton
  label    -> labels.jsonl         per case, --label-samples teacher samples of a points-out-of-100
                                   distribution for each question; gold = mean distribution
  export   -> synth_{train,val}.jsonl   verdict Records (same format as verdict.data_typed, describe=True)

Excluded on purpose (the benchmark's families): invoice/bill processing and payment approval,
security alert/incident triage, customer-service replies, AI-agent trace review.

Models are given as specs: "openrouter:<model id>" (key from ~/.config/verdict/openrouter.key,
reasoning disabled) or "local:<model id>" (the GB10 vLLM endpoint). Spend is tracked from response
usage x OpenRouter list prices; a stage stops cleanly at --max-usd or when the key runs out of credit
(HTTP 402), and resumes where it left off.

  python3 scripts/synth_typed.py catalog --model openrouter:anthropic/claude-sonnet-5 --per-domain 4
  python3 scripts/synth_typed.py cases --per-workflow 150 --workers 32 \
      --gen-models openrouter:deepseek/deepseek-v4.1-flash,openrouter:google/gemini-3.1-flash-lite
  python3 scripts/synth_typed.py label --tag dsv4pro --model openrouter:deepseek/deepseek-v4-pro --workers 32
  python3 scripts/synth_typed.py label --tag gem3flash --model openrouter:google/gemini-3-flash-preview --workers 32
  python3 scripts/synth_typed.py label --tag qwen32b --model local:Qwen/Qwen3-VL-32B-Instruct-FP8 --workers 24
  python3 scripts/synth_typed.py export --labelers dsv4pro,gem3flash,qwen36plus
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import random
import re
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

DOMAINS = [
    "HR and people operations", "recruiting and hiring", "sales and CRM pipeline", "marketing operations",
    "procurement and vendor management", "logistics and shipping", "manufacturing quality control",
    "IT operations and internal helpdesk", "software engineering (pull requests, deployments, bug reports)",
    "legal and contract review", "regulatory compliance and risk", "corporate finance (expenses, budgets, forecasts)",
    "facilities and real estate", "healthcare administration (scheduling, prior authorization; non-clinical)",
    "insurance claims", "banking operations (KYC, loan applications)", "e-commerce operations (orders, returns, fraud)",
    "content moderation and trust & safety", "product management (feature requests, user feedback)",
    "education administration", "travel and events", "research operations and grants",
    "public sector citizen services", "energy and utilities field operations",
]
EXCLUDE = ("invoice or bill processing and payment approval; security alert or incident triage; "
           "customer-service ticket/chat replies; review of AI agent runs or traces")

BENCH_Q = {"This trace requires human review."}  # exact benchmark instructions we must never reuse


LOCAL_ENDPOINT = "http://127.0.0.1:8003/v1"
OPENROUTER = "https://openrouter.ai/api/v1"
_PRICES = {}
_SPEND = {"usd": 0.0, "in": 0, "out": 0}
_LOCK = threading.Lock()


class BudgetStop(Exception):
    pass


def _prices():
    if not _PRICES:
        try:
            with urllib.request.urlopen(OPENROUTER + "/models", timeout=30) as r:
                for m in json.loads(r.read())["data"]:
                    p = m.get("pricing", {})
                    _PRICES[m["id"]] = (float(p.get("prompt", 0) or 0), float(p.get("completion", 0) or 0))
        except Exception:  # noqa: BLE001
            pass
    return _PRICES


def resolve(spec):
    kind, _, model = spec.partition(":")
    if kind == "local":
        return LOCAL_ENDPOINT, model, None
    if kind == "openrouter":
        key = open(os.path.expanduser("~/.config/verdict/openrouter.key")).read().strip()
        return OPENROUTER, model, key
    raise ValueError(f"bad model spec {spec!r} (use openrouter:<id> or local:<id>)")


def chat(spec, prompt, temperature=0.7, max_tokens=1500, timeout=240, retries=3, max_usd=0.0):
    endpoint, model, key = resolve(spec)
    body = {"model": model, "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature, "max_tokens": max_tokens}
    headers = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
        body["reasoning"] = {"enabled": False}
    if max_usd and _SPEND["usd"] >= max_usd:
        raise BudgetStop(f"stage budget ${max_usd} reached")
    last = None
    for a in range(retries + 1):
        try:
            req = urllib.request.Request(endpoint.rstrip("/") + "/chat/completions", data=json.dumps(body).encode(), headers=headers)
            with urllib.request.urlopen(req, timeout=timeout) as r:
                out = json.loads(r.read())
            if "error" in out:
                raise RuntimeError(str(out["error"])[:200])
            u = out.get("usage") or {}
            if key:
                pin, pout = _prices().get(model, (0.0, 0.0))
                with _LOCK:
                    _SPEND["in"] += u.get("prompt_tokens", 0); _SPEND["out"] += u.get("completion_tokens", 0)
                    _SPEND["usd"] += u.get("prompt_tokens", 0) * pin + u.get("completion_tokens", 0) * pout
            return out["choices"][0]["message"].get("content") or ""
        except urllib.error.HTTPError as e:
            if e.code == 402:
                raise BudgetStop("OpenRouter key out of credit (HTTP 402)")
            last = e; time.sleep(2 * (a + 1))
        except Exception as e:  # noqa: BLE001
            last = e; time.sleep(2 * (a + 1))
    raise last


def parse_json(text):
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.S)
    try:
        return json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.S)
        return json.loads(m.group(0)) if m else None


# ---------------------------------------------------------------- catalog
CATALOG_PROMPT = """You design evaluation workflows for an AI "decision layer" that runs inside companies.
Domain: {domain}

Propose {n} DISTINCT, realistic workflows from this domain. In each workflow the system receives ONE piece of
state (a JSON object) and must answer exactly 5 typed questions about it.

Return ONLY JSON of this form:
{{"workflows": [{{
  "name": "snake_case_name",
  "description": "one sentence: what decision the organization is making",
  "state_description": "which fields the JSON state contains (mix structured fields and free text such as messages, notes, descriptions)",
  "factors": [{{"name": "latent_factor", "values": ["v1", "v2", "v3"]}}],
  "questions": {{
    "q_name": {{"type": "noul", "instructions": "A declarative statement that is true or false about the case.",
               "criteria": {{"true": "when the statement holds", "false": "when it does not"}}}},
    "q_name2": {{"type": "choice", "instructions": "A question with one best answer?",
                "criteria": {{"option_key": "one-line description", "option_key2": "...", "option_key3": "..."}}}},
    "q_name3": {{"type": "score", "instructions": "A question answered on an ordered 4-level rubric?",
                "criteria": ["lowest level description", "second level", "third level", "highest level"]}}
  }}
}}]}}

Rules:
- 6 to 9 latent factors per workflow, each with 3 to 6 values; they must drive the correct answers.
- Exactly 5 questions: 1-2 noul, 1-2 choice (3 to 5 options, snake_case keys, each with a description),
  1-2 score (exactly 4 ordered levels, lowest first). Questions must require reading the state carefully;
  some should be genuinely ambiguous for borderline cases.
- Do NOT propose any of these (or near variants): {exclude}.
"""


def validate_workflow(w):
    try:
        assert re.fullmatch(r"[a-z0-9_]+", w["name"])
        assert 5 <= len(w["factors"]) <= 10 and all(2 <= len(f["values"]) <= 8 for f in w["factors"])
        qs = w["questions"]; assert len(qs) == 5
        types = [q["type"] for q in qs.values()]
        assert set(types) <= {"noul", "choice", "score"} and "choice" in types and "score" in types
        for q in qs.values():
            assert q["instructions"].strip() and q["instructions"] not in BENCH_Q
            if q["type"] == "noul":
                assert set(q.get("criteria", {})) >= {"true", "false"}
            elif q["type"] == "choice":
                assert 3 <= len(q["criteria"]) <= 6 and all(re.fullmatch(r"[a-z0-9_]+", k) for k in q["criteria"])
            else:
                assert isinstance(q["criteria"], list) and len(q["criteria"]) == 4
        return True
    except Exception:
        return False


def stage_catalog(a):
    path = os.path.join(a.out_dir, "catalog.json")
    cat = json.load(open(path)) if os.path.isfile(path) else {"workflows": []}
    have = {w["name"] for w in cat["workflows"]}
    done_domains = {w["domain"] for w in cat["workflows"]}
    todo = [d for d in DOMAINS if d not in done_domains]

    def work(dom):
        for _ in range(3):
            out = parse_json(chat(a.model, CATALOG_PROMPT.format(domain=dom, n=a.per_domain, exclude=EXCLUDE),
                                  temperature=0.8, max_tokens=8000, max_usd=a.max_usd))
            ws = [w for w in (out or {}).get("workflows", []) if validate_workflow(w)]
            if ws:
                for w in ws:
                    w["domain"] = dom
                return ws
        return []

    with ThreadPoolExecutor(a.workers) as ex:
        for fut in as_completed([ex.submit(work, d) for d in todo]):
            for w in fut.result():
                if w["name"] not in have:
                    have.add(w["name"]); cat["workflows"].append(w)
            json.dump(cat, open(path, "w"), indent=1)
    print(f"catalog: {len(cat['workflows'])} workflows over {len({w['domain'] for w in cat['workflows']})} domains -> {path}"
          f" | spent ${_SPEND['usd']:.3f}")


# ---------------------------------------------------------------- cases
CASE_PROMPT = """Workflow: {description}
The state is a JSON object containing: {state_description}

Write ONE realistic state for a case with these latent properties:
{factors}

Requirements: concrete and specific (names, amounts, dates, identifiers, short messages or notes where natural);
roughly 80-250 words of content in total; do NOT name the latent properties or state any decision explicitly;
they must be inferable only from the details. Return ONLY the JSON object."""


def stage_cases(a):
    cat = json.load(open(os.path.join(a.out_dir, "catalog.json")))["workflows"]
    path = os.path.join(a.out_dir, "cases.jsonl")
    done = {json.loads(l)["id"] for l in open(path)} if os.path.isfile(path) else set()
    rng = random.Random(a.seed)
    jobs = []
    for w in cat:
        for i in range(a.per_workflow):
            fac = {f["name"]: rng.choice(f["values"]) for f in w["factors"]}
            cid = f"{w['name']}-{i:04d}"
            if cid not in done:
                jobs.append((cid, w, fac))
    print(f"cases: {len(jobs)} to render ({len(done)} done)", flush=True)
    lock = threading.Lock(); t0 = time.time(); n = 0

    gens = [g for g in a.gen_models.split(",") if g]

    def work(cid, w, fac):
        gen = gens[int(hashlib.sha1(cid.encode()).hexdigest()[:6], 16) % len(gens)]
        txt = chat(gen, CASE_PROMPT.format(description=w["description"], state_description=w["state_description"],
                                           factors=json.dumps(fac, ensure_ascii=False)), temperature=0.9, max_tokens=900,
                   max_usd=a.max_usd)
        st = parse_json(txt)
        return cid, w["name"], fac, st, gen

    with open(path, "a") as f, ThreadPoolExecutor(a.workers) as ex:
        for fut in as_completed([ex.submit(work, *j) for j in jobs]):
            try:
                cid, wn, fac, st, gen = fut.result()
            except BudgetStop as e:
                print(f"  STOP: {e}", flush=True); ex.shutdown(cancel_futures=True); break
            except Exception as e:  # noqa: BLE001
                print("  case error:", str(e)[:120], flush=True); continue
            if not isinstance(st, dict) or len(json.dumps(st)) < 150:
                continue
            with lock:
                f.write(json.dumps({"id": cid, "workflow": wn, "factors": fac, "state": st, "generator": gen},
                                   ensure_ascii=False) + "\n"); f.flush()
                n += 1
                if n % 200 == 0:
                    print(f"  {n}/{len(jobs)} cases ({n/(time.time()-t0):.2f}/s) spent=${_SPEND['usd']:.3f}", flush=True)
    print(f"cases: wrote {n} | spent ${_SPEND['usd']:.3f}", flush=True)


# ---------------------------------------------------------------- labels
LABEL_PROMPT = """You are an experienced operator in this workflow: {description}

STATE:
{state}

Answer each question below with a probability distribution over its options: integer points per option
summing to 100. Spread points when the state is genuinely ambiguous; concentrate them when it is clear.

QUESTIONS:
{questions}

Return ONLY JSON mapping each question name to its points, e.g. {{"q_name": {{"option_key": 70, "other_key": 30}}}}."""


def _num(x):
    try:
        return max(0.0, float(x))
    except Exception:
        return 0.0


def option_keys(q):
    crit = q.get("criteria")
    if q["type"] == "noul":
        return ["false", "true"]
    if q["type"] == "score":
        return [str(i) for i in range(len(crit or [0, 1, 2, 3]))]
    return list(crit.keys()) if isinstance(crit, dict) else [str(k) for k in (crit or [])]


def render_questions(qs):
    out = []
    for name, q in qs.items():
        crit = q.get("criteria")
        if q["type"] == "noul":
            c = crit if isinstance(crit, dict) else {}
            opts = (f'true: {c.get("true") or "yes, the statement holds"} | '
                    f'false: {c.get("false") or "no, the statement does not hold"}')
        elif q["type"] == "score":
            opts = " | ".join(f"{i}: {c}" for i, c in enumerate(crit or ["lowest", "low", "high", "highest"]))
        else:
            items = crit.items() if isinstance(crit, dict) else [(k, "") for k in (crit or [])]
            opts = " | ".join(f"{k}: {v}" if v else str(k) for k, v in items)
        out.append(f'- {name} ({q["type"]}): {q["instructions"]}\n  options -> {opts}')
    return "\n".join(out)


def stage_label(a):
    cat = {w["name"]: w for w in json.load(open(os.path.join(a.out_dir, "catalog.json")))["workflows"]}
    cases = [json.loads(l) for l in open(os.path.join(a.out_dir, "cases.jsonl"))]
    path = os.path.join(a.out_dir, f"labels_{a.tag}.jsonl")
    done = {json.loads(l)["id"] for l in open(path)} if os.path.isfile(path) else set()
    todo = [c for c in cases if c["id"] not in done]
    print(f"label[{a.tag}] {a.model}: {len(todo)} cases to label ({len(done)} done), {a.label_samples} samples each", flush=True)
    lock = threading.Lock(); t0 = time.time(); n = 0

    def one(c):
        w = cat[c["workflow"]]
        prompt = LABEL_PROMPT.format(description=w["description"], state=json.dumps(c["state"], ensure_ascii=False),
                                     questions=render_questions(w["questions"]))
        dists = {q: [] for q in w["questions"]}
        for s in range(a.label_samples):
            out = parse_json(chat(a.model, prompt, temperature=0.7, max_tokens=700, max_usd=a.max_usd)) or {}
            for qn, q in w["questions"].items():
                pts = out.get(qn)
                if not isinstance(pts, dict):
                    continue
                keys = option_keys(q)
                v = [_num(pts.get(k, 0)) for k in keys]
                if sum(v) > 0:
                    dists[qn].append([x / sum(v) for x in v])
        gold = {}
        for qn, ds in dists.items():
            if len(ds) == a.label_samples:  # require every sample to parse, like a complete teacher draw
                k = len(ds[0]); mean = [sum(d[i] for d in ds) / len(ds) for i in range(k)]
                gold[qn] = {"probabilities": mean, "samples": ds}
        return c["id"], gold

    with open(path, "a") as f, ThreadPoolExecutor(a.workers) as ex:
        for fut in as_completed([ex.submit(one, c) for c in todo]):
            try:
                cid, gold = fut.result()
            except BudgetStop as e:
                print(f"  STOP: {e}", flush=True); ex.shutdown(cancel_futures=True); break
            except Exception as e:  # noqa: BLE001
                print("  label error:", str(e)[:120], flush=True); continue
            with lock:
                f.write(json.dumps({"id": cid, "gold": gold, "labeler": a.model}) + "\n"); f.flush(); n += 1
                if n % 200 == 0:
                    print(f"  [{a.tag}] {n}/{len(todo)} labeled ({n/(time.time()-t0):.2f}/s) spent=${_SPEND['usd']:.3f}", flush=True)
    print(f"label: wrote {n} | spent ${_SPEND['usd']:.3f}", flush=True)


# ---------------------------------------------------------------- export
def option_texts(q):
    if q["type"] == "noul":
        return [f'false: {q["criteria"]["false"]}', f'true: {q["criteria"]["true"]}']
    if q["type"] == "score":
        return [f"level {i}: {c}" for i, c in enumerate(q["criteria"])]
    return [f"{k}: {v}" for k, v in q["criteria"].items()]


def stage_export(a):
    cat = {w["name"]: w for w in json.load(open(os.path.join(a.out_dir, "catalog.json")))["workflows"]}
    cases = {json.loads(l)["id"]: json.loads(l) for l in open(os.path.join(a.out_dir, "cases.jsonl"))}
    tags = [t for t in a.labelers.split(",") if t]
    labs = {}
    for t in tags:
        for l in open(os.path.join(a.out_dir, f"labels_{t}.jsonl")):
            r = json.loads(l); labs.setdefault(r["id"], {})[t] = r["gold"]
    val_wf = {w for w in cat if int(hashlib.sha1(w.encode()).hexdigest()[:6], 16) % 100 < a.val_pct}
    tr, va = [], []
    agree = {"pairs": 0, "argmax_agree": 0, "tv_sum": 0.0}
    for cid, by_tag in labs.items():
        c = cases.get(cid); w = cat.get(c["workflow"]) if c else None
        if not w or any(t not in by_tag for t in tags):
            continue                                      # require every labeler on the case
        state = json.dumps(c["state"], ensure_ascii=False)
        for qn, q in w["questions"].items():
            ds = [by_tag[t][qn]["probabilities"] for t in tags if qn in by_tag[t]]
            if len(ds) != len(tags):
                continue
            k = len(ds[0]); p = [sum(d[i] for d in ds) / len(ds) for i in range(k)]
            for i in range(len(ds)):
                for j in range(i + 1, len(ds)):
                    agree["pairs"] += 1
                    agree["argmax_agree"] += int(max(range(k), key=ds[i].__getitem__) == max(range(k), key=ds[j].__getitem__))
                    agree["tv_sum"] += 0.5 * sum(abs(x - y) for x, y in zip(ds[i], ds[j]))
            ans = max(range(k), key=p.__getitem__)
            rec = {"text": state, "question": f'{q["instructions"]}\n\nContext:\n{state}', "options": option_texts(q),
                   "answer": ans, "qtype": q["type"], "task": f'synth:{c["workflow"]}:{qn}',
                   "meta": {"workflow": c["workflow"], "question": qn, "primitive": q["type"], "soft": p,
                            "option_keys": option_keys(q), "domain": w["domain"], "generator": c.get("generator"),
                            "labelers": {t: by_tag[t][qn]["probabilities"] for t in tags}}}
            (va if c["workflow"] in val_wf else tr).append(rec)
    for name, rows in [("synth_train", tr), ("synth_val", va)]:
        with open(os.path.join(a.out_dir, f"{name}.jsonl"), "w") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    from collections import Counter
    pr = max(agree["pairs"], 1)
    print(f"export: {len(tr)} train / {len(va)} val decisions ({len(val_wf)} held-out workflows), "
          f"primitives {dict(Counter(r['qtype'] for r in tr + va))}; labelers {tags}: pairwise argmax agreement "
          f"{agree['argmax_agree']/pr*100:.1f}%, mean TV {agree['tv_sum']/pr:.3f}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["catalog", "cases", "label", "export"])
    ap.add_argument("--model", default="openrouter:anthropic/claude-sonnet-5", help="model spec for catalog / label")
    ap.add_argument("--gen-models", default="openrouter:deepseek/deepseek-v4.1-flash,openrouter:google/gemini-3.1-flash-lite",
                    help="comma list of model specs for case rendering (assigned by case-id hash)")
    ap.add_argument("--tag", default="default", help="labeler tag (label stage)")
    ap.add_argument("--labelers", default="dsv4pro,gem3flash,qwen36plus", help="labeler tags to ensemble (export)")
    ap.add_argument("--out-dir", default="data/synth")
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--per-domain", type=int, default=4)
    ap.add_argument("--per-workflow", type=int, default=20)
    ap.add_argument("--label-samples", type=int, default=1)
    ap.add_argument("--val-pct", type=int, default=10)
    ap.add_argument("--max-usd", type=float, default=0.0, help="stop this stage once estimated OpenRouter spend reaches this")
    ap.add_argument("--seed", type=int, default=0)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    {"catalog": stage_catalog, "cases": stage_cases, "label": stage_label, "export": stage_export}[a.stage](a)


if __name__ == "__main__":
    main()

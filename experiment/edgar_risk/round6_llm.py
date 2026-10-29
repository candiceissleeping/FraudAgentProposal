"""Round 6: an LLM reads each (redacted) 10-K and lists internal contradictions (method L).

The packets are built once, here, from the raw SEC filings downloaded in round 5. Everything
after that runs on the user's own machine with their own Anthropic API key; the model never
sees the treatment / control labels.

Usage
  python -m experiment.edgar_risk.round6_llm build              # needs data/round5/raw (not in git)
  python -m experiment.edgar_risk.round6_llm count  [--limit N]  # token count of each packet (free)
  python -m experiment.edgar_risk.round6_llm submit [--limit N] [--runs 2] [--model ...]
  python -m experiment.edgar_risk.round6_llm status
  python -m experiment.edgar_risk.round6_llm collect             # writes results/round6/llm_raw/*.json
  python -m experiment.edgar_risk.round6_llm retry               # re-runs missing / failed requests one by one
  python -m experiment.edgar_risk.round6_llm score               # verifies quotes, writes llm_scores.csv
  python -m experiment.edgar_risk.round6_llm evaluate            # joins labels; run only after score is committed

Credentials: the SDK reads ANTHROPIC_API_KEY (or an `ant auth login` profile) from the environment.
"""
import argparse
import csv
import glob
import gzip
import hashlib
import json
import os
import random
import re
import sys
from collections import defaultdict

from .round3 import auc, auc_ci

PACKETS = "data/round6/packets"
OUT = "results/round6"
RAW_OUT = f"{OUT}/llm_raw"
BATCHES = f"{OUT}/batches.json"
KEY = "results/round4/key.json"
FILINGS = "data/round5/filings.json"
POOL = "config/round4_pool.json"
MODEL = "claude-opus-5-5"
SEVERITY = {"low": 1, "medium": 2, "high": 3}
CATEGORIES = ["A1_within_statement", "A2_between_statements", "A3_notes_vs_statements", "A4_prior_year_changed",
              "A5_mdna_vs_numbers", "A6_inconsistent_statements", "A7_implausible_explanation"]

# ---------------------------------------------------------------- prompts (pre-registered; see protocol.md)
SYSTEM = "You are a forensic accountant who reads SEC annual reports carefully and reports only what the text supports."

REVIEW_TASK = """The documents above are parts of a company's annual report (Form 10-K). Company names, people,
places and absolute years have been redacted: [COMPANY], [NAME], [URL]; Y0 is the latest fiscal year, Y-1 the year
before, and so on. DOCUMENT A is the current-year 10-K (MD&A, financial statements, notes; business description and
governance sections removed). DOCUMENT B, if present, is the prior-year 10-K (financial statements and notes).

Task: find internal contradictions - places where the filing's own figures or statements do not agree with each other.
Base every judgment only on these documents. Do not try to work out which company this is, and do not use anything
you may know about any company's later history.

Categories
- A1_within_statement: a statement does not add up (totals, subtotals, EPS vs net income / shares)
- A2_between_statements: statements disagree (net income, ending cash, retained-earnings roll-forward, working-capital
  changes on the cash-flow statement vs balance-sheet changes)
- A3_notes_vs_statements: a note or schedule disagrees with the face statements (segments, debt, tax, allowances,
  inventory, PP&E, equity, quarterly data)
- A4_prior_year_changed: a Y-1 figure in DOCUMENT A differs from the same figure in DOCUMENT B
- A5_mdna_vs_numbers: MD&A text contradicts the numbers (direction, size, or the stated reason)
- A6_inconsistent_statements: two passages state incompatible facts, policies or estimates
- A7_implausible_explanation: the explanation given cannot account for the size of the change

Rules
1. Each finding quotes two passages, copied exactly (contiguous text, at most 300 characters each), one for each side
   of the contradiction, and names the document (A or B) each comes from.
2. Give the two amounts being compared, as written.
3. Check whether the filing itself explains the difference (restatement, reclassification, pooling of interests,
   discontinued operations, acquisition or disposal, accounting change, foreign exchange, different definitions).
   If it does, set explained = true and quote the explanation; otherwise explained = false and explanation_quote = "".
4. Ignore rounding and differences below 0.5%. Missing information is not a contradiction.
5. Report only contradictions you have checked by reading both places. At most 25 findings; if there are none,
   return an empty list.
6. severity: high = a material figure (revenue, income, assets, equity, cash flow) is inconsistent; medium = a
   secondary figure or a narrative contradiction; low = minor.
7. overall_rating (0-100): how strongly the unexplained contradictions suggest the financial statements are unreliable.
   0 = fully consistent.
"""

IDENTIFY_TASK = """The documents above are parts of a redacted annual report. Based only on these documents, which
company filed it, and for which fiscal year? Give your single best guess, and your confidence (0-100). If you have no
idea, say "unknown" with confidence 0."""

REVIEW_SCHEMA = {
    "type": "object",
    "properties": {
        "findings": {"type": "array", "items": {
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": CATEGORIES},
                "description": {"type": "string"},
                "doc_a": {"type": "string", "enum": ["A", "B"]},
                "quote_a": {"type": "string"},
                "amount_a": {"type": "string"},
                "doc_b": {"type": "string", "enum": ["A", "B"]},
                "quote_b": {"type": "string"},
                "amount_b": {"type": "string"},
                "explained": {"type": "boolean"},
                "explanation_quote": {"type": "string"},
                "severity": {"type": "string", "enum": list(SEVERITY)},
            },
            "required": ["category", "description", "doc_a", "quote_a", "amount_a", "doc_b", "quote_b", "amount_b",
                         "explained", "explanation_quote", "severity"],
            "additionalProperties": False,
        }},
        "overall_rating": {"type": "integer"},
        "summary": {"type": "string"},
    },
    "required": ["findings", "overall_rating", "summary"],
    "additionalProperties": False,
}

IDENTIFY_SCHEMA = {
    "type": "object",
    "properties": {"company_guess": {"type": "string"}, "fiscal_year_guess": {"type": "string"},
                   "confidence": {"type": "integer"}},
    "required": ["company_guess", "fiscal_year_guess", "confidence"],
    "additionalProperties": False,
}


# ---------------------------------------------------------------- build packets (run once, needs raw filings)
ITEM = re.compile(r"^\s*item\s*(\d{1,2})([a-c])?\b", re.I)
MUST = ["total assets", "operating activities", "net income", "notes to"]


def _clean(lines):
    out = []
    for ln in lines:
        ln = re.sub(r"\.{4,}|_{4,}|-{6,}|={4,}", " ", ln)
        ln = re.sub(r"[ \t]{2,}", "  ", ln).strip()
        if not ln or re.fullmatch(r"(page\s*)?[F-]*\s*-?\d{1,3}-?|table of contents", ln, re.I):
            continue
        out.append(ln)
    return out


def _headings(lines):
    hs = [(i, int(m.group(1)), (m.group(2) or "").lower()) for i, ln in enumerate(lines)
          if len(ln) < 200 and (m := ITEM.match(ln))]
    # a table of contents is a run of headings a few lines apart; keep only body headings
    return [h for k, h in enumerate(hs)
            if not ((k + 1 < len(hs) and hs[k + 1][0] - h[0] <= 3) or (k > 0 and h[0] - hs[k - 1][0] <= 3))]


def _trim(lines, keep_mdna):
    """Drop Items 1-4 and 10-14 of a 10-K main document; fall back to the whole text if that loses the statements."""
    hs = _headings(lines)

    def last(n, sub=""):
        c = [i for i, a, b in hs if a == n and b == sub]
        return c[-1] if c else None
    start = last(5) or last(6) or last(7)
    if start is None:
        return lines
    keep = [i >= start for i in range(len(lines))]
    a, b = last(10), last(15)
    if a is not None:
        for i in range(a, b if b and b > a else len(lines)):
            keep[i] = False
    if not keep_mdna:
        m, e = last(7), last(7, "a") or last(8)
        if m and e and e > m:
            for i in range(m, e):
                keep[i] = False
    out = [ln for ln, k in zip(lines, keep) if k]
    whole, cut = "\n".join(lines).lower(), "\n".join(out).lower()
    if any(w in whole and w not in cut for w in MUST):
        return lines
    return out


def packet_text(raw, keep_mdna):
    from .fin_extract import doc_lines
    out = []
    for doc in raw.split("<DOCUMENT>")[1:]:
        typ = re.search(r"<TYPE>\s*([^\s<]+)", doc).group(1).upper()
        fname = re.search(r"<FILENAME>\s*([^\s<]+)", doc)
        if fname and not fname.group(1).lower().endswith((".htm", ".html", ".txt")):
            continue  # PDF / graphic copies
        lines = _clean(doc_lines(doc))
        if typ.startswith("10-K"):
            lines = _trim(lines, keep_mdna)
        out += lines
    return "\n".join(out)


def build():
    from .redact import make_redactor
    filings = json.load(open(FILINGS))
    pool = json.load(open(POOL))
    aliases = {}
    for pr in pool["pairs"]:
        for side in ("treatment", "control"):
            c = pr[side]
            aliases[c["name"]] = c["aliases"] + [c["name"]]
    os.makedirs(PACKETS, exist_ok=True)
    manifest = {}
    for pid, f in sorted(filings.items()):
        years = sorted(f["filings"], reverse=True)[:2]
        fy = int(f["filings"][years[0]]["period"][:4])
        parts = []
        for i, y in enumerate(years):
            path = f"data/round5/raw/{f['cik']}_{y}.txt"
            if not os.path.exists(path):
                continue
            parts.append(packet_text(open(path, errors="ignore").read(), keep_mdna=(i == 0)))
        redact = make_redactor(aliases[f["name"]], fy, "\n".join(parts))
        text = f"<DOCUMENT A>\n{redact(parts[0])}\n</DOCUMENT A>\n"
        text += f"<DOCUMENT B>\n{redact(parts[1])}\n</DOCUMENT B>\n" if len(parts) > 1 else "<DOCUMENT B>\n(not available)\n</DOCUMENT B>\n"
        with gzip.open(f"{PACKETS}/{pid}.txt.gz", "wt", encoding="utf-8") as fh:
            fh.write(text)
        manifest[pid] = {"chars": len(text), "docs": len(parts), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        print(pid, len(text))
    json.dump(manifest, open(f"{PACKETS}/manifest.json", "w"), indent=1)


def load_packet(pid):
    with gzip.open(f"{PACKETS}/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
        return fh.read()


def packet_ids(limit=None, only=None):
    ids = sorted(os.path.basename(p)[:-7] for p in glob.glob(f"{PACKETS}/*.txt.gz"))
    if only:
        ids = [p for p in ids if p in only]
    return ids[:limit] if limit else ids


# ---------------------------------------------------------------- API requests (run locally)
def params(pid, kind, model):
    content = [{"type": "text", "text": load_packet(pid), "cache_control": {"type": "ephemeral"}},
               {"type": "text", "text": REVIEW_TASK if kind == "review" else IDENTIFY_TASK}]
    schema = REVIEW_SCHEMA if kind == "review" else IDENTIFY_SCHEMA
    return {
        "model": model,
        "max_tokens": 64000 if kind == "review" else 4000,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": content}],
        "output_config": {"effort": "high" if kind == "review" else "low",
                          "format": {"type": "json_schema", "schema": schema}},
    }


def request_ids(pids, runs):
    return [f"{p}-review-{r}" for p in pids for r in range(1, runs + 1)] + [f"{p}-identify" for p in pids]


def _client():
    try:
        import anthropic
    except ImportError:
        sys.exit("pip install -U anthropic")
    return anthropic, anthropic.Anthropic()


def count(args):
    _, client = _client()
    total = 0
    for pid in packet_ids(args.limit, args.only):
        p = params(pid, "review", args.model)
        n = client.messages.count_tokens(model=p["model"], system=p["system"], messages=p["messages"]).input_tokens
        total += n
        print(pid, n)
    print("input tokens per review run:", total)


def submit(args):
    _, client = _client()
    pids = packet_ids(args.limit, args.only)
    reqs = []
    for cid in request_ids(pids, args.runs):
        pid, kind = cid.split("-")[:2]
        reqs.append({"custom_id": cid, "params": params(pid, kind, args.model)})
    batch = client.messages.batches.create(requests=reqs)
    log = json.load(open(BATCHES)) if os.path.exists(BATCHES) else []
    log.append({"id": batch.id, "model": args.model, "runs": args.runs, "n": len(reqs), "pids": pids})
    os.makedirs(OUT, exist_ok=True)
    json.dump(log, open(BATCHES, "w"), indent=1)
    print(f"batch {batch.id}: {len(reqs)} requests ({len(pids)} packets x {args.runs} review runs + identify)")


def status(args):
    _, client = _client()
    for b in json.load(open(BATCHES)):
        r = client.messages.batches.retrieve(b["id"])
        c = r.request_counts
        print(b["id"], r.processing_status, f"succeeded={c.succeeded} errored={c.errored} processing={c.processing} "
              f"expired={c.expired} canceled={c.canceled}")


def _save(cid, message=None, error=None, model=None):
    os.makedirs(RAW_OUT, exist_ok=True)
    rec = {"custom_id": cid, "requested_model": model, "error": error}
    if message is not None:
        rec.update(model=message.model, stop_reason=message.stop_reason,
                   usage=message.usage.to_dict() if hasattr(message.usage, "to_dict") else dict(message.usage),
                   text=next((b.text for b in message.content if b.type == "text"), ""))
    json.dump(rec, open(f"{RAW_OUT}/{cid}.json", "w"), indent=1)


def collect(args):
    _, client = _client()
    for b in json.load(open(BATCHES)):
        r = client.messages.batches.retrieve(b["id"])
        if r.processing_status != "ended":
            print(b["id"], "not finished yet")
            continue
        for res in client.messages.batches.results(b["id"]):
            t = res.result.type
            if t == "succeeded":
                _save(res.custom_id, message=res.result.message, model=b["model"])
            elif not os.path.exists(f"{RAW_OUT}/{res.custom_id}.json"):
                err = getattr(getattr(res.result, "error", None), "type", None) or t
                _save(res.custom_id, error=str(err), model=b["model"])
    print("saved to", RAW_OUT)


def _usable(cid):
    path = f"{RAW_OUT}/{cid}.json"
    if not os.path.exists(path):
        return False
    rec = json.load(open(path))
    return not rec.get("error") and rec.get("stop_reason") == "end_turn"


def retry(args):
    """Sequential, streaming re-run of anything missing or not ended normally, with server-side refusal fallback."""
    anthropic, client = _client()
    log = json.load(open(BATCHES))
    for b in log:
        for cid in request_ids(b["pids"], b["runs"]):
            if _usable(cid):
                continue
            pid, kind = cid.split("-")[:2]
            print("retry", cid)
            try:
                with client.beta.messages.stream(**params(pid, kind, b["model"]),
                                                 betas=["server-side-fallback-2026-07-01"],
                                                 extra_body={"fallbacks": "default"}) as stream:
                    _save(cid, message=stream.get_final_message(), model=b["model"])
            except anthropic.RateLimitError:
                sys.exit("rate limited - run retry again later")
            except anthropic.APIStatusError as e:
                _save(cid, error=f"{e.status_code} {e.message}", model=b["model"])
            except anthropic.APIConnectionError as e:
                print("connection error:", e)


# ---------------------------------------------------------------- scoring (no labels)
def _norm(s):
    s = s.lower().replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = re.sub(r"[–—]", "-", s)
    return re.sub(r"[\s$,]+", "", s)


def _found(quote, hay):
    q = _norm(quote)
    if len(q) < 8:
        return False
    if q in hay:
        return True
    # allow the model to have dropped or changed a few characters at the ends
    return len(q) >= 40 and (q[:40] in hay or q[-40:] in hay)


def score(args):
    rows, finding_rows = [], []
    per = defaultdict(lambda: {"runs": []})
    for path in sorted(glob.glob(f"{RAW_OUT}/*-review-*.json")):
        rec = json.load(open(path))
        pid, _, run = rec["custom_id"].split("-")
        if rec.get("error") or rec.get("stop_reason") != "end_turn":
            print("skip", rec["custom_id"], rec.get("error") or rec.get("stop_reason"))
            continue
        out = json.loads(rec["text"])
        text = load_packet(pid)
        docs = {"A": _norm(text.split("</DOCUMENT A>")[0]), "B": _norm(text.split("</DOCUMENT A>")[-1])}
        L = L_all = n_ver = 0
        for i, f in enumerate(out["findings"]):
            va = _found(f["quote_a"], docs[f["doc_a"]]) or _found(f["quote_a"], docs["A"] + docs["B"])
            vb = _found(f["quote_b"], docs[f["doc_b"]]) or _found(f["quote_b"], docs["A"] + docs["B"])
            verified = va and vb
            w = SEVERITY[f["severity"]]
            L_all += 0 if f["explained"] else w
            if verified and not f["explained"]:
                L += w
            n_ver += verified
            finding_rows.append({"pid": pid, "run": run, "n": i + 1, "category": f["category"], "severity": f["severity"],
                                 "explained": f["explained"], "verified": verified, "quote_a_found": va,
                                 "quote_b_found": vb, "amount_a": f["amount_a"], "amount_b": f["amount_b"],
                                 "description": f["description"]})
        per[pid]["runs"].append({"run": run, "L": L, "L_unverified": L_all, "rating": out["overall_rating"],
                                 "findings": len(out["findings"]), "verified": n_ver})
    ident = {}
    for path in glob.glob(f"{RAW_OUT}/*-identify.json"):
        rec = json.load(open(path))
        if not rec.get("error") and rec.get("stop_reason") == "end_turn":
            ident[rec["custom_id"].split("-")[0]] = json.loads(rec["text"])
    for pid in sorted(per):
        rs = per[pid]["runs"]
        mean = lambda k: round(sum(r[k] for r in rs) / len(rs), 3)
        g = ident.get(pid, {})
        rows.append({"pid": pid, "runs": len(rs), "L": mean("L"), "L_unverified": mean("L_unverified"),
                     "rating": mean("rating"), "findings": mean("findings"), "verified": mean("verified"),
                     "L_by_run": ";".join(f"{r['run']}:{r['L']}" for r in sorted(rs, key=lambda r: r["run"])),
                     "guess": g.get("company_guess", ""), "guess_confidence": g.get("confidence", "")})
    os.makedirs(OUT, exist_ok=True)
    for name, data in (("llm_scores.csv", rows), ("llm_findings.csv", finding_rows)):
        if data:
            with open(f"{OUT}/{name}", "w", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
                w.writeheader()
                w.writerows(data)
    print(f"{len(rows)} packets scored, {len(finding_rows)} findings "
          f"({sum(r['verified'] for r in finding_rows)} with both quotes found)")


# ---------------------------------------------------------------- evaluation (joins labels)
def _spearman(xs, ys):
    def rk(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                r[o[k]] = (i + j) / 2
            i = j + 1
        return r
    a, b = rk(xs), rk(ys)
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    cov = sum((x - ma) * (y - mb) for x, y in zip(a, b))
    va = sum((x - ma) ** 2 for x in a) ** 0.5
    vb = sum((y - mb) ** 2 for y in b) ** 0.5
    return cov / (va * vb) if va and vb else float("nan")


def evaluate(args):
    from .round5 import pct_rank
    key = json.load(open(KEY))
    llm = {r["pid"]: r for r in csv.DictReader(open(f"{OUT}/llm_scores.csv"))}
    cons = {r["pid"]: r for r in csv.DictReader(open("results/round5/consistency_scores.csv"))}
    feats = {r["pid"]: r for r in csv.DictReader(open("results/round5/financial_features.csv"))}
    kw = {r["packet"]: float(r["keyword_score"]) for r in csv.DictReader(open("results/round4/keyword_scores.csv"))}
    rub = {r["packet"]: float(r["rubric_total"]) for r in csv.DictReader(open("results/round4/scores.csv"))}
    num = lambda s: float(s) if s not in ("", None) else None
    pids = [p for p in key if p in llm]
    meth = {
        "L LLM contradictions": {p: num(llm[p]["L"]) for p in pids},
        "L unverified": {p: num(llm[p]["L_unverified"]) for p in pids},
        "L overall rating": {p: num(llm[p]["rating"]) for p in pids},
        "C consistency (round 5)": {p: num(cons[p]["C"]) for p in pids},
        "T keyword (round 4)": {p: kw[p] for p in pids},
        "R rubric v2 (round 4)": {p: rub[p] for p in pids},
        "F Dechow (round 5)": {p: num(feats[p]["F"]) for p in pids},
    }
    ranks = {m: pct_rank(v) for m, v in meth.items()}

    def combo(parts):
        out = {}
        for p in pids:
            rs = [ranks[m][p] for m in parts if ranks[m][p] is not None]
            out[p] = sum(rs) / len(rs) if rs else None
        return out
    meth["R+L"] = combo(["R rubric v2 (round 4)", "L LLM contradictions"])
    meth["T+L"] = combo(["T keyword (round 4)", "L LLM contradictions"])

    # recognition: the identify guess matches the company's name or an alias
    aliases = {}
    for pr in json.load(open(POOL))["pairs"]:
        for side in ("treatment", "control"):
            aliases[pr[side]["name"]] = [a.lower() for a in pr[side]["aliases"] + [pr[side]["name"]]]
    recog = {p: any(a in llm[p]["guess"].lower() for a in aliases[key[p]["name"]] if len(a) > 2) for p in pids}

    lines = [f"Packets scored: {len(pids)}; recognised by the identify request: {sum(recog.values())}"]

    def report(label, keep):
        lines.append(f"\n## {label}")
        lines.append("| Method | n (treat/ctrl) | AUC | 95% CI |")
        lines.append("|---|---|---|---|")
        for m, v in meth.items():
            pos = [v[p] for p in keep if key[p]["group"] == "treatment" and v[p] is not None]
            neg = [v[p] for p in keep if key[p]["group"] == "control" and v[p] is not None]
            if len(pos) < 3 or len(neg) < 3:
                continue
            lo, hi = auc_ci(pos, neg)
            lines.append(f"| {m} | {len(pos)}/{len(neg)} | {auc(pos, neg):.2f} | {lo:.2f}-{hi:.2f} |")
    pair_of = {}
    for i, pr in enumerate(json.load(open(POOL))["pairs"]):
        pair_of[pr["treatment"]["name"]] = pair_of[pr["control"]["name"]] = i
    post = {"American International Group", "ITT Educational Services", "Navistar International"}
    report("All scored filings", pids)
    report("Not recognised by the model", [p for p in pids if not recog[p]])
    report("Recognised by the model", [p for p in pids if recog[p]])
    drop = {pair_of[key[p]["name"]] for p in pids if key[p]["name"] in post}
    report("Excluding post-disclosure pairs (AIG, ITT, Navistar)", [p for p in pids if pair_of[key[p]["name"]] not in drop])

    # H6: paired bootstrap, AUC(R+L) - AUC(R)
    rng = random.Random(11)
    pos = [p for p in pids if key[p]["group"] == "treatment"]
    neg = [p for p in pids if key[p]["group"] == "control"]

    def a(m, P, N):
        return auc([meth[m][p] for p in P if meth[m][p] is not None], [meth[m][p] for p in N if meth[m][p] is not None])
    lines.append("\n## Paired bootstrap (2000 draws)")
    for comb, base in (("R+L", "R rubric v2 (round 4)"), ("L LLM contradictions", "C consistency (round 5)")):
        ds = []
        for _ in range(2000):
            P = [rng.choice(pos) for _ in pos]
            N = [rng.choice(neg) for _ in neg]
            ds.append(a(comb, P, N) - a(base, P, N))
        ds.sort()
        lines.append(f"- {comb} - {base}: {a(comb, pos, neg) - a(base, pos, neg):+.2f} (95% CI {ds[50]:+.2f} to {ds[1949]:+.2f})")

    # reliability between runs
    by_run = defaultdict(dict)
    for p in pids:
        for item in llm[p]["L_by_run"].split(";"):
            r, v = item.split(":")
            by_run[r][p] = float(v)
    if len(by_run) >= 2:
        r1, r2 = sorted(by_run)[:2]
        common = [p for p in pids if p in by_run[r1] and p in by_run[r2]]
        x, y = [by_run[r1][p] for p in common], [by_run[r2][p] for p in common]
        agree = sum((u > 0) == (v > 0) for u, v in zip(x, y))
        lines.append(f"\n## Run-to-run reliability\n- Spearman rank correlation of L, run {r1} vs {r2}: {_spearman(x, y):.2f}"
                     f"\n- Same flag (L > 0 vs L = 0) in both runs: {agree}/{len(common)}")

    lines.append("\n## Within-pair comparison (treatment higher / tie / lower)")
    pairs = defaultdict(dict)
    for p in pids:
        pairs[pair_of[key[p]["name"]]][key[p]["group"]] = p
    for m in meth:
        w = t = l = 0
        for pr in pairs.values():
            if len(pr) < 2 or meth[m][pr["treatment"]] is None or meth[m][pr["control"]] is None:
                continue
            x, y = meth[m][pr["treatment"]], meth[m][pr["control"]]
            w, t, l = w + (x > y), t + (x == y), l + (x < y)
        lines.append(f"- {m}: {w} / {t} / {l}")

    lines.append("\n## Flag rate (L > 0)")
    for grp in ("treatment", "control"):
        g = [p for p in pids if key[p]["group"] == grp]
        lines.append(f"- {grp}: {sum(meth['L LLM contradictions'][p] > 0 for p in g)}/{len(g)}")
    txt = "\n".join(lines)
    open(f"{OUT}/evaluation_output.md", "w").write(txt + "\n")
    print(txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["build", "count", "submit", "status", "collect", "retry", "score", "evaluate"])
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--runs", type=int, default=2, help="independent review runs per packet")
    ap.add_argument("--limit", type=int, help="only the first N packets (pilot)")
    ap.add_argument("--only", nargs="*", help="only these packet ids, e.g. Q01 Q02")
    args = ap.parse_args()
    {"build": lambda a: build(), "count": count, "submit": submit, "status": status, "collect": collect,
     "retry": retry, "score": score, "evaluate": evaluate}[args.action](args)


if __name__ == "__main__":
    main()

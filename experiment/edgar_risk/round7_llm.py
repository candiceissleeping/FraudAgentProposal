"""Round 7 baseline B: give the whole 10-K to an LLM and ask for one risk score (0-100).

The simplest possible LLM baseline: no redaction, no checklist, no quote verification. It reuses the
batch / chunk / collect / retry machinery of round6_llm with round-7 paths and prompt.

Usage
  python -m experiment.edgar_risk.round7_llm build                       # here; needs SEC_UA (downloads the 28 Y0 10-Ks)
  python -m experiment.edgar_risk.round7_llm count
  python -m experiment.edgar_risk.round7_llm run --provider openai --model gpt-5.5 [--runs 1]
  python -m experiment.edgar_risk.round7_llm status | collect | retry
  python -m experiment.edgar_risk.round7_llm score                       # writes results/round7/llm_risk_scores.csv
"""
import argparse
import csv
import glob
import gzip
import hashlib
import json
import os
import re
import sys

from . import round6_llm as base
from .fin_extract import doc_lines

PACKETS = "data/round7/packets"
OUT = "results/round7/llm"

SYSTEM = "You are an experienced forensic accountant and equity analyst."

RISK_TASK = """The document above is a company's annual report on Form 10-K.

Rate the risk that this company's financial statements in this filing are materially misstated, through fraud
or serious accounting errors, on a scale of 0 to 100 (0 = no concern, 100 = almost certainly misstated).

Base the score on this filing. Then answer two short questions separately: do you recognise the company, and do
you know of later accounting problems, restatements or SEC enforcement involving this filing period?"""

RISK_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_score": {"type": "integer"},
        "main_reasons": {"type": "array", "items": {"type": "string"}},
        "recognised_company": {"type": "boolean"},
        "company_name_guess": {"type": "string"},
        "knows_later_problems": {"type": "boolean"},
    },
    "required": ["risk_score", "main_reasons", "recognised_company", "company_name_guess", "knows_later_problems"],
    "additionalProperties": False,
}


def build(args):
    """Download each Y0 10-K (main document and EX-13) and store its plain text, unredacted."""
    os.makedirs(PACKETS, exist_ok=True)
    from .round7 import _get, _pairs
    manifest = {}
    for pid, name, cik, a0, p0, a1, p1, group, sic in _pairs():
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{a0.replace('-', '')}/{a0}.txt"
        raw = _get(url).decode("utf-8", errors="ignore")
        parts = []
        for doc in raw.split("<DOCUMENT>")[1:]:
            typ = re.search(r"<TYPE>\s*([^\s<]+)", doc).group(1).upper()
            fname = re.search(r"<FILENAME>\s*([^\s<]+)", doc)
            if not (typ.startswith("10-K") or typ.startswith("EX-13")):
                continue
            if fname and not fname.group(1).lower().endswith((".htm", ".html", ".txt")):
                continue
            doc = re.sub(r"<ix:header>.*?</ix:header>", " ", doc, flags=re.S | re.I)  # hidden inline-XBRL contexts
            parts.append("\n".join(base._clean(doc_lines(doc))))
        text = "\n\n".join(parts)
        with gzip.open(f"{PACKETS}/{pid}.txt.gz", "wt", encoding="utf-8") as fh:
            fh.write(text)
        manifest[pid] = {"accession": a0, "chars": len(text), "sha256": hashlib.sha256(text.encode()).hexdigest()}
        print(pid, name, len(text), flush=True)
    json.dump(manifest, open(f"{PACKETS}/manifest.json", "w"), indent=1)


# ---------------------------------------------------------------- reuse round 6 machinery with round-7 settings
def request_ids(pids, runs):
    return [f"{p}-risk-{r}" for p in pids for r in range(1, runs + 1)]


def openai_body(pid, kind, model):
    return {
        "model": model,
        "messages": [{"role": "system", "content": SYSTEM},
                     {"role": "user", "content": base.load_packet(pid) + "\n\n" + RISK_TASK}],
        "response_format": {"type": "json_schema", "json_schema": {"name": "risk", "strict": True, "schema": RISK_SCHEMA}},
        "reasoning_effort": "high",
        "max_completion_tokens": 32000,
    }


def params(pid, kind, model):
    return {
        "model": model,
        "max_tokens": 32000,
        "system": SYSTEM,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": base.load_packet(pid), "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": RISK_TASK}]}],
        "output_config": {"effort": "high", "format": {"type": "json_schema", "schema": RISK_SCHEMA}},
    }


def _configure():
    base.PACKETS, base.OUT = PACKETS, OUT
    base.RAW_OUT, base.BATCHES = f"{OUT}/raw", f"{OUT}/batches.json"
    base.request_ids, base.openai_body, base.params = request_ids, openai_body, params


def score(args):
    rows = []
    for path in sorted(glob.glob(f"{OUT}/raw/*-risk-*.json")):
        rec = json.load(open(path))
        pid, _, run = rec["custom_id"].split("-")
        if rec.get("error") or rec.get("stop_reason") != "end_turn":
            print("skip", rec["custom_id"], rec.get("error") or rec.get("stop_reason"))
            continue
        out = json.loads(rec["text"])
        rows.append({"pid": pid, "run": run, "risk_score": out["risk_score"], "recognised": out["recognised_company"],
                     "guess": out["company_name_guess"], "knows_later_problems": out["knows_later_problems"],
                     "reasons": " | ".join(out["main_reasons"])[:600], "model": rec.get("model")})
    with open("results/round7/llm_risk_scores.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} scored runs for {len({r['pid'] for r in rows})} filings")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["build", "count", "submit", "run", "status", "collect", "retry", "score"])
    ap.add_argument("--provider", choices=["anthropic", "openai"], default="openai")
    ap.add_argument("--model", default=base.MODEL)
    ap.add_argument("--runs", type=int, default=1)
    ap.add_argument("--limit", type=int)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--budget", type=int, default=1_200_000)
    args = ap.parse_args()
    _configure()
    if args.action == "build":
        return build(args)
    if args.action == "score":
        return score(args)
    {"count": base.count, "submit": base.submit, "run": base.run_openai, "status": base.status,
     "collect": base.collect, "retry": base.retry}[args.action](args)


if __name__ == "__main__":
    main()

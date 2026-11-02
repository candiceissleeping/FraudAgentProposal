"""Round 8: separate "reading the signal" from "already knowing the outcome" (L2 redaction pilot).

Pilot input = the round-7 packets (the exact text baseline B read), so L2 vs. B isolates the effect of
cutting identity.  See results/round8/protocol.md.

Usage
  python -m experiment.edgar_risk.round8 identifiers [--pids P01T,P01C,...]   # SEC submissions API + signatures
  python -m experiment.edgar_risk.round8 build [--pids ...]                   # L2 packets + key
  python -m experiment.edgar_risk.round8 audit [--pids ...]                   # leak audit, scaling check, top caps
  python -m experiment.edgar_risk.round8 agent-files --pids ... --out DIR     # neutral file names for scoring agents
"""
import argparse
import gzip
import json
import math
import os
import random
import re
import subprocess
import time

from .redact_v2 import L2Redactor, leak_audit, person_names, top_caps
from .round7 import _pairs

SRC = "data/round7/packets"
DATA = "data/round8"
OUT = "results/round8"
UA = "FraudAgentProposal academic research"
SEED = 8

RISK_TASK_L2 = """The document above is a company's annual report on Form 10-K. It has been redacted for a research
study: the company's name, people, places, other proper nouns and identifiers are replaced by placeholders such as
[COMPANY], [NAME_3] or [PERSON_1] (the same placeholder always means the same thing within this document); years are
shown relative to the fiscal year of the report (Y0 = this fiscal year, Y-1 = the year before); and every monetary
amount has been multiplied by one undisclosed constant, so ratios, growth rates and sums are preserved but absolute
sizes are not (differences of about 1 in a total are rounding).

Rate the risk that this company's financial statements in this filing are materially misstated, through fraud
or serious accounting errors, on a scale of 0 to 100 (0 = no concern, 100 = almost certainly misstated).

Base the score on this filing. Then answer two short questions separately: do you recognise the company, and do
you know of later accounting problems, restatements or SEC enforcement involving this filing period?"""


def _pids(arg):
    allp = [p[0] for p in _pairs()]
    return allp if not arg else [p for p in arg.split(",") if p in allp]


def _info():
    return {p[0]: {"name": p[1], "cik": int(p[2]), "acc": p[3], "period": p[4], "group": p[7], "sic": p[8]}
            for p in _pairs()}


def _src(pid):
    with gzip.open(f"{SRC}/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
        return fh.read()


def _sec_json(cik):
    url = f"https://data.sec.gov/submissions/CIK{cik:010d}.json"
    for attempt in range(4):
        r = subprocess.run(["curl", "-s", "--fail", "-A", UA, url], capture_output=True)
        if r.returncode == 0:
            time.sleep(0.15)
            return json.loads(r.stdout)
        time.sleep(2 ** attempt)
    raise RuntimeError(url)


def identifiers(args):
    """Per-company identifier list (contains real names: never given to a scoring agent)."""
    os.makedirs(f"{DATA}/identifiers", exist_ok=True)
    info = _info()
    for pid in _pids(args.pids):
        s = _sec_json(info[pid]["cik"])
        text = _src(pid)
        names = [s["name"]] + [f["name"] for f in s.get("formerNames", [])] + [info[pid]["name"]]
        addresses, numbers = [], [info[pid]["cik"]]
        for a in (s.get("addresses") or {}).values():
            for key in ("street1", "street2", "city"):
                if a.get(key):
                    addresses.append(a[key].strip())
            if a.get("zipCode"):
                numbers.append(a["zipCode"])
        if s.get("ein"):
            numbers.append(s["ein"])
        if s.get("phone"):
            numbers.append(s["phone"])
        ident = {"pid": pid, "names": sorted(set(names)), "tickers": s.get("tickers", []),
                 "people": person_names(text), "addresses": sorted(set(addresses)),
                 "numbers": sorted(set(str(n) for n in numbers))}
        json.dump(ident, open(f"{DATA}/identifiers/{pid}.json", "w"), indent=1)
        print(pid, info[pid]["name"], len(ident["people"]), "people", flush=True)


def _keys():
    """One scaling factor per packet, log-uniform on [0.5, 2], fixed seed, drawn for all 28 at once."""
    rng = random.Random(SEED)
    return {pid: round(math.exp(rng.uniform(math.log(0.5), math.log(2))), 4) for pid in sorted(_info())}


def build(args):
    os.makedirs(f"{DATA}/packets/L2", exist_ok=True)
    keys = _keys()
    json.dump(keys, open(f"{DATA}/key.json", "w"), indent=1)
    info = _info()
    for pid in _pids(args.pids):
        ident = json.load(open(f"{DATA}/identifiers/{pid}.json"))
        text = _src(pid)
        red = L2Redactor(ident, int(info[pid]["period"][:4]), keys[pid], text)
        out = red.l2(text)
        with gzip.open(f"{DATA}/packets/L2/{pid}.txt.gz", "wt", encoding="utf-8") as fh:
            fh.write(out)
        print(pid, len(text), "->", len(out), "entities", len(red.entities), flush=True)


def _first_total_assets(text):
    for ln in text.split("\n"):
        if re.match(r"(?i)\s*total assets\b", ln):
            m = re.search(r"\$?\(?(\d[\d,]*(?:\.\d+)?)", ln[len("total assets"):])
            if m:
                return float(m.group(1).replace(",", ""))
    return None


def audit(args):
    keys = json.load(open(f"{DATA}/key.json"))
    lines = ["# 第八輪 L2 遮蔽檢查（程式輸出）", "",
             "| 資料包 | 殘留識別碼 | Total assets：L2 ÷ L0 | k | 誤差 |", "|---|---|---|---|---|"]
    caps = []
    for pid in _pids(args.pids):
        ident = json.load(open(f"{DATA}/identifiers/{pid}.json"))
        with gzip.open(f"{DATA}/packets/L2/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
            l2 = fh.read()
        hits = leak_audit(l2, ident)
        a0, a2 = _first_total_assets(_src(pid)), _first_total_assets(l2)
        ratio = a2 / a0 if a0 and a2 else None
        err = f"{abs(ratio / keys[pid] - 1):.2%}" if ratio else "—"
        lines.append(f"| {pid} | {', '.join(f'{k}×{v}' for k, v in hits.items()) or '0'} | "
                     f"{ratio:.4f} | {keys[pid]} | {err} |" if ratio else
                     f"| {pid} | {', '.join(f'{k}×{v}' for k, v in hits.items()) or '0'} | — | {keys[pid]} | — |")
        caps.append(f"- {pid}: " + ", ".join(f"{t}({c})" for t, c in top_caps(l2, 50)))
    lines += ["", "## 未遮蔽大寫詞（各前 50 名，供人工檢查漏網的專有名詞）", ""] + caps
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/audit_L2_pilot.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:4 + len(_pids(args.pids))]))


def agent_files(args):
    """Copy L2 packets to neutral names (random order) outside the repository, for blind scoring agents."""
    pids = _pids(args.pids)
    order = pids[:]
    random.Random(SEED + 1).shuffle(order)
    os.makedirs(args.out, exist_ok=True)
    mapping = {}
    for i, pid in enumerate(order, 1):
        with gzip.open(f"{DATA}/packets/L2/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
            open(f"{args.out}/report_{i:02d}.txt", "w").write(fh.read())
        mapping[f"report_{i:02d}"] = pid
    json.dump(mapping, open(f"{OUT}/agent_filename_map.json", "w"), indent=1)
    print(json.dumps(mapping, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["identifiers", "build", "audit", "agent-files"])
    ap.add_argument("--pids", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    {"identifiers": identifiers, "build": build, "audit": audit, "agent-files": agent_files}[a.cmd](a)


if __name__ == "__main__":
    main()

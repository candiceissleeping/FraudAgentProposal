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

from .redact_v2 import (L2Redactor, drop_descriptive, l3_select, l3_stub, leak_audit, mark_sections, mask_segments,
                        mask_units, person_names, segment_names, top_caps, unit_names, unmark)
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


RISK_TASK_L3 = RISK_TASK_L2.replace(
    "(differences of about 1 in a total are rounding).",
    "(differences of about 1 in a total are rounding). Only some sections of the report are included (risk factors, "
    "legal proceedings, MD&A, financial statements and notes, controls); the business description has been removed "
    "and replaced by a one-line summary, business-segment names are replaced by [SEGMENT_n], and sentences that "
    "describe the company's market position or history have been removed.")

RISK_TASK_L3B = RISK_TASK_L3.replace(
    "every monetary\namount has been multiplied by one undisclosed constant, so ratios, growth rates and sums are preserved but absolute\nsizes are not",
    "every monetary\namount has been multiplied by one undisclosed constant and every share count by another, so per-share amounts\n"
    "change by their ratio; ratios, growth rates, sums and per-share identities (income / shares) are preserved but\n"
    "absolute sizes and per-share figures are not").replace(
    "business-segment names are replaced by [SEGMENT_n],",
    "business-segment and business-unit names are replaced by [SEGMENT_n] / [UNIT_n], days of the month are removed "
    "from dates,")

DISPLAY = {"P01T": "Latch, Inc.", "P01C": "AerSale Corporation", "P02T": "Archer-Daniels-Midland Company",
           "P02C": "Bunge Limited", "P03T": "AMMO, Inc.", "P03C": "National Presto Industries, Inc.",
           "P04T": "Adamis Pharmaceuticals Corporation", "P04C": "PDS Biotechnology Corporation",
           "P05T": "Becton, Dickinson and Company", "P05C": "Boston Scientific Corporation"}

RISK_TASK_NAMED = """The document above is the annual report on Form 10-K of {name}. It has been prepared for a research study:
the names of people, places, other companies and other identifiers are replaced by placeholders such as [NAME_3] or
[PERSON_1] (the same placeholder always means the same thing within this document); years are shown relative to the
fiscal year of the report (Y0 = this fiscal year, Y-1 = the year before); and every monetary amount has been
multiplied by one undisclosed constant and every share count by another, so per-share amounts change by their ratio;
ratios, growth rates, sums and per-share identities (income / shares) are preserved but absolute sizes and per-share
figures are not (differences of about 1 in a total are rounding). Only some sections of the report are included (risk
factors, legal proceedings, MD&A, financial statements and notes, controls); the business description has been removed
and replaced by a one-line summary, business-segment and business-unit names are replaced by [SEGMENT_n] / [UNIT_n],
days of the month are removed from dates, and sentences that describe the company's market position or history have
been removed.

Rate the risk that this company's financial statements in this filing are materially misstated, through fraud
or serious accounting errors, on a scale of 0 to 100 (0 = no concern, 100 = almost certainly misstated).

Base the score on this filing. Then answer two short questions separately: do you know of later accounting problems,
restatements or SEC enforcement involving this company and filing period? And is the content of this document
consistent with what you know about {name}?"""


# Strings the L2-pilot agents actually used to recognise the company (verified present in the pilot packets).
REGRESSION = {"P01C": ["20211231"], "P02T": ["1ADM", "Oilseeds", "Nutrition", "Carbohydrate Solutions"],
              "P02C": ["1818"], "P03T": ["90,870,094", "Marketplace"], "P03C": ["npk", "Housewares", "Small Appliance"],
              "P04T": ["admp", "Compounding"], "P04C": ["Versamune", "07932"], "P05T": [" BD ", "bdx"],
              "P05C": ["683-4000", "Interventional", "Rhythm"]}


def _assets():
    out = {}
    for i, c in enumerate(json.load(open("results/round7/controls.json")), 1):
        out[f"P{i:02d}T"], out[f"P{i:02d}C"] = c["case_assets"], c["control_assets"]
    return out


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


def _keys_j():
    """Rule v3: a second factor for share counts, drawn so that per-share amounts move by at least 25% (|ln k/j| >= ln 1.25)."""
    k, rng, out = _keys(), random.Random(SEED + 100), {}
    for pid in sorted(k):
        while True:
            j = round(math.exp(rng.uniform(math.log(0.5), math.log(2))), 4)
            if abs(math.log(k[pid] / j)) >= math.log(1.25):
                break
        out[pid] = j
    return out


def _keys():
    """One scaling factor per packet, log-uniform on [0.5, 2], fixed seed, drawn for all 28 at once."""
    rng = random.Random(SEED)
    return {pid: round(math.exp(rng.uniform(math.log(0.5), math.log(2))), 4) for pid in sorted(_info())}


def _write(level, pid, text):
    os.makedirs(f"{DATA}/packets/{level}", exist_ok=True)
    with gzip.open(f"{DATA}/packets/{level}/{pid}.txt.gz", "wt", encoding="utf-8") as fh:
        fh.write(text)


def build(args):
    """Rule v2 -> packets L2 / L3 (already scored in the pilots); rule v3 (--v3) -> L2b / L3b."""
    keys = _keys()
    json.dump(keys, open(f"{DATA}/key.json", "w"), indent=1)
    jkeys = _keys_j() if args.v3 else {}
    if args.v3:
        json.dump(jkeys, open(f"{DATA}/key_j.json", "w"), indent=1)
    suffix = args.tag if args.v3 else ""
    info, assets = _info(), _assets()
    stats = {}
    for pid in _pids(args.pids):
        ident = json.load(open(f"{DATA}/identifiers/{pid}.json"))
        text = _src(pid)
        red = L2Redactor(ident, int(info[pid]["period"][:4]), keys[pid], text, j=jkeys.get(pid))
        marked = red.l2(mark_sections(text))     # sections found on the original text, see mark_sections
        l2 = unmark(marked)
        _write("L2" + suffix, pid, l2)
        body, kept = l3_select(marked)
        segs = segment_names(l2)
        units = unit_names(l2, segs) if args.v3 else []
        body = mask_units(body, units) if args.v3 else body
        body = mask_segments(body, segs)
        body, dropped = drop_descriptive(body)
        l3 = l3_stub(info[pid]["sic"], assets[pid], info[pid]["period"]) + "\n\n" + body
        _write("L3" + suffix, pid, l3)
        stats[pid] = {"chars_L0": len(text), "chars_L2": len(l2), "chars_L3": len(l3), "items_kept": kept,
                      "segments": len(segs), "units": len(units), "sentences_dropped": dropped,
                      "inconsistent_numbers": len(red.inconsistent_numbers()), "share_values": len(red.share_values)}
        print(pid, stats[pid], flush=True)
    json.dump(stats, open(f"{OUT}/build_stats{_stats_tag(suffix)}.json", "w"), indent=1)


def _stats_tag(tag):
    return "" if not tag else "_v3" if tag == "b" else f"_v3{tag}"


def _first_total_assets(text):
    for ln in text.split("\n"):
        if re.match(r"(?i)\s*total assets\b", ln):
            m = re.search(r"\$?\(?(\d[\d,]*(?:\.\d+)?)", ln[len("total assets"):])
            if m:
                return float(m.group(1).replace(",", ""))
    return None


def audit(args):
    keys = json.load(open(f"{DATA}/key.json"))
    lv = args.level
    sf = f"{OUT}/build_stats{_stats_tag(lv[2:])}.json"
    stats = json.load(open(sf)) if os.path.exists(sf) else {}
    lines = [f"# 第八輪 {lv} 遮蔽檢查（程式輸出）", "",
             "| 資料包 | 殘留識別碼 | 試跑漏洞回歸（應為 0） | 同數字處理不一致 | Total assets：遮蔽後 ÷ L0 | k |",
             "|---|---|---|---|---|---|"]
    caps = []
    for pid in _pids(args.pids):
        ident = json.load(open(f"{DATA}/identifiers/{pid}.json"))
        with gzip.open(f"{DATA}/packets/{lv}/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
            red = fh.read()
        hits = leak_audit(red, ident)
        reg = {s_: red.count(s_) for s_ in REGRESSION.get(pid, []) if red.count(s_)}
        a0, a2 = _first_total_assets(_src(pid)), _first_total_assets(red)
        ratio = f"{a2 / a0:.4f}" if a0 and a2 else "—"
        lines.append(f"| {pid} | {', '.join(f'{k}×{v}' for k, v in hits.items()) or '0'} | "
                     f"{', '.join(f'{k}×{v}' for k, v in reg.items()) or '0'} | "
                     f"{stats.get(pid, {}).get('inconsistent_numbers', '—')} | {ratio} | {keys[pid]} |")
        caps.append(f"- {pid}: " + ", ".join(f"{t}({c})" for t, c in top_caps(red, 50)))
    lines += ["", "## 未遮蔽大寫詞（各前 50 名，供人工檢查漏網的專有名詞）", ""] + caps
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/audit_{lv}.md", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:4 + len(_pids(args.pids))]))


def agent_files(args):
    """Copy L2 packets to neutral names (random order) outside the repository, for blind scoring agents."""
    pids = _pids(args.pids)
    order = pids[:]
    random.Random(SEED + 1 + {"L2": 0, "L3": 1, "L2b": 2, "L3b": 3, "L2c": 4, "L3c": 5}[args.level]).shuffle(order)   # new order per level
    os.makedirs(args.out, exist_ok=True)
    mapping = {}
    for i, pid in enumerate(order, 1):
        with gzip.open(f"{DATA}/packets/{args.level}/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
            open(f"{args.out}/report_{i:02d}.txt", "w").write(fh.read())
        mapping[f"report_{i:02d}"] = pid
    name = "agent_filename_map.json" if args.level == "L2" else f"agent_filename_map_{args.level}.json"
    json.dump(mapping, open(f"{OUT}/{name}", "w"), indent=1)
    print(json.dumps(mapping, indent=1))


def swap_files(args):
    """Identity-swap test (protocol section 10): each L3c packet x {real name, partner's name, no name}."""
    pids = _pids(args.pids)
    jobs = []
    for pid in pids:
        partner = pid[:3] + ("C" if pid.endswith("T") else "T")
        for cond, named in (("real", pid), ("swap", partner), ("none", None)):
            jobs.append((pid, cond, named))
    random.Random(SEED + 10).shuffle(jobs)
    os.makedirs(args.out, exist_ok=True)
    mapping, prompts = {}, {}
    for i, (pid, cond, named) in enumerate(jobs, 1):
        with gzip.open(f"{DATA}/packets/L3c/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
            text = fh.read()
        if named:
            name = DISPLAY[named]
            text = f"Company: {name} — Annual report on Form 10-K\n\n" + text.replace("[COMPANY]", name).replace(
                "[TICKER]", name)
            prompts[f"report_{i:02d}"] = RISK_TASK_NAMED.format(name=name)
        else:
            prompts[f"report_{i:02d}"] = RISK_TASK_L3B
        open(f"{args.out}/report_{i:02d}.txt", "w").write(text)
        mapping[f"report_{i:02d}"] = {"content": pid, "condition": cond, "named": named,
                                      "content_group": "treatment" if pid.endswith("T") else "control"}
    json.dump(mapping, open(f"{OUT}/agent_filename_map_swap.json", "w"), indent=1)
    json.dump(prompts, open(f"{args.out}/prompts.json", "w"), indent=1)
    print(len(jobs), "files")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["identifiers", "build", "audit", "agent-files", "swap-files"])
    ap.add_argument("--pids", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--level", default="L2", choices=["L2", "L3", "L2b", "L3b", "L2c", "L3c"])
    ap.add_argument("--tag", default="b", help="with --v3: packet suffix (b = scored L3b; c = v3.1 scaling fixes)")
    ap.add_argument("--v3", action="store_true", help="rule version 3: share-count factor j, dates, unit names")
    a = ap.parse_args()
    {"identifiers": identifiers, "build": build, "audit": audit, "agent-files": agent_files,
     "swap-files": swap_files}[a.cmd](a)


if __name__ == "__main__":
    main()

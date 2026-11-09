"""Experiment E2: score anonymized company-type cards with Opus 5.5 (protocol: results/mem_type/protocol.md).

  SEC_UA="<name email>" python -m experiment.mem_type build    # fetch as-of-fiscal-year facts from SEC, write cards
  python -m experiment.mem_type probe --level L1                # closed-set matching: can the cards be re-identified?
  python -m experiment.mem_type run --level L1 --runs 5         # scoring sessions (same no-tool environment)
  python -m experiment.mem_type evaluate --level L1             # after raw runs are committed

Every value on a card is as of the fiscal year: the 10-K for that year (XBRL Assets, dei:EntityPublicFloat, the
exchange registered under Section 12(b) on its cover) and the years since the first EDGAR filing.
"""
import argparse
import csv
import html
import json
import os
import random
import re
import subprocess
import sys
import time

from experiment.mem_isolated import HARDENED, claude, load_events, parse_scores, verify

D, R = "data/mem_type", "results/mem_type"
SAMPLES = ("round8", "oot")
SCRATCH = os.environ.get("MEM_TYPE_SCRATCH", "/tmp")


def _get(url):
    p = subprocess.run(["curl", "-sS", "-L", "--compressed", "-A", os.environ["SEC_UA"], url], capture_output=True)
    time.sleep(0.25)
    return p.stdout


def companies():
    """pid -> {cik, sic, y0_acc, fy_end} for the round 8 and out-of-time samples, from the sampling records."""
    out = {"round8": {}, "oot": {}}
    orig = {r["pid"]: r["company"] for r in csv.DictReader(open("results/mem_isolated/reference/round8_MEM_original.csv"))}
    cases = {c["name"]: c for c in json.load(open("config/round7_cases.json"))}
    ctrls = json.load(open("results/round7/controls.json"))
    for pid, name in orig.items():
        if pid.endswith("T"):
            c = cases[name]; k = next(x for x in ctrls if x["case"] == name)
            out["round8"][pid] = {"cik": int(c["cik"]), "sic": k["case_sic"], "y0_acc": c["y0_acc"], "fy_end": c["y0_period"]}
        else:
            k = next(x for x in ctrls if x["control"] == name)
            p = k["y0_period"]
            out["round8"][pid] = {"cik": int(k["control_cik"]), "sic": k["control_sic"], "y0_acc": k["y0_acc"],
                                  "fy_end": f"{p[:4]}-{p[4:6]}-{p[6:]}"}
    pairs = json.load(open(os.environ.get("ROUND9_PAIRS", f"{D}/round9_pairs.json")))
    for i, p in enumerate(pairs, 1):
        for side, suf in (("case", "T"), ("control", "C")):
            x = p[side]; d = x["y0_period"]
            out["oot"][f"O{i:02d}{suf}"] = {"cik": int(x["cik"]), "sic": x["sic"], "y0_acc": x["y0_acc"],
                                            "fy_end": f"{d[:4]}-{d[4:6]}-{d[6:]}"}
    return out


def _exchange(cover):
    t = re.sub(r"\s+", " ", cover)
    m = re.search(r"securities registered (?:pursuant to|under) section 12\(b\)", t, re.I)
    if not m:
        return "none"   # no Section 12(b) registration line on the cover
    i = m.start()
    # the cover's exchange table can sit after the 12(g) line, so read up to the next cover question
    j = t.lower().find("well-known seasoned issuer", i + 1)
    seg = t[i:j if j > i else i + 1500]
    if re.search(r"NYSE American|NYSE MKT|American Stock Exchange", seg, re.I):
        return "NYSE American"
    if re.search(r"New York Stock Exchange|\bNYSE\b", seg, re.I):
        return "NYSE"
    if re.search(r"Nasdaq|NASDAQ", seg):
        return "Nasdaq"
    return "none"


def cmd_build(args):
    os.makedirs(D, exist_ok=True)
    sic_html = _get("https://www.sec.gov/search-filings/standard-industrial-classification-sic-code-list").decode("utf-8", "ignore")
    sic = {c: html.unescape(t).strip() for c, _, t in
           re.findall(r"<tr[^>]*>\s*<td[^>]*>\s*(\d{3,4})\s*</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>", sic_html, re.S)}
    facts = {}
    for s, comps in companies().items():
        for pid, c in sorted(comps.items()):
            cik = c["cik"]
            cf = json.loads(_get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json") or b"{}")
            assets = [u["val"] for u in cf.get("facts", {}).get("us-gaap", {}).get("Assets", {}).get("units", {}).get("USD", [])
                      if u.get("accn") == c["y0_acc"] and u.get("end") == c["fy_end"]]
            flt = [u["val"] for u in cf.get("facts", {}).get("dei", {}).get("EntityPublicFloat", {}).get("units", {}).get("USD", [])
                   if u.get("accn") == c["y0_acc"]]
            sub = json.loads(_get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json"))
            blocks = [sub["filings"]["recent"]] + [json.loads(_get("https://data.sec.gov/submissions/" + f["name"]))
                                                   for f in sub["filings"].get("files", [])]
            first = min(d for b in blocks for d in b["filingDate"])
            doc = next((b["primaryDocument"][i] for b in blocks for i, a in enumerate(b["accessionNumber"]) if a == c["y0_acc"]), None)
            cover = ""
            if doc:
                raw = _get(f"https://www.sec.gov/Archives/edgar/data/{cik}/{c['y0_acc'].replace('-', '')}/{doc}").decode("utf-8", "ignore")
                raw = re.sub(r"(?is)<ix:header>.*?</ix:header>", "", raw)   # hidden inline-XBRL block before the cover
                cover = html.unescape(re.sub(r"<[^>]+>", " ", raw))[:60000]
            facts[pid] = {**c, "sample": s, "sic_title": sic.get(str(int(c["sic"])), ""),
                          "major_group": sic.get(str(int(c["sic"]))[:-2] + "00", "") if len(str(int(c["sic"]))) == 4 else "",
                          "assets": assets[0] if assets else None, "public_float": flt[0] if flt else None,
                          "exchange": _exchange(cover) if cover else None, "first_filing": first, "primary_doc": doc}
            print(pid, facts[pid]["sic_title"][:30], facts[pid]["assets"], facts[pid]["public_float"],
                  facts[pid]["exchange"], first, flush=True)
    json.dump(facts, open(f"{D}/facts.json", "w"), indent=1)


def _bucket(v, edges, labels):
    if v is None:
        return "not reported"
    for e, l in zip(edges, labels):
        if v < e:
            return l
    return labels[-1]


def card(f, level):
    yrs = (int(f["fy_end"][:4]) - int(f["first_filing"][:4]))
    years = _bucket(yrs, [3, 10, 20], ["under 3 years", "3-10 years", "10-20 years", "20 years or more"])
    if level == "L1":
        ind = f"SIC {int(f['sic'])} {f['sic_title'].title()}"
        assets = _bucket(f["assets"], [1e7, 1e8, 1e9, 1e10], ["under $10 million", "$10-100 million", "$100 million-$1 billion",
                                                                 "$1-10 billion", "$10 billion or more"])
        flt = _bucket(f["public_float"], [1e7, 7.5e7, 2.5e8, 7e8, 5e9], ["under $10 million", "$10-75 million", "$75-250 million",
                                                                           "$250-700 million", "$700 million-$5 billion", "$5 billion or more"])
        fy = f"fiscal year ended {f['fy_end']}"
    else:
        ind = (f["major_group"].title() or "not reported") if level == "L2" else None
        assets = _bucket(f["assets"], [1e8, 1e9], ["under $100 million", "$100 million-$1 billion", "$1 billion or more"])
        flt = _bucket(f["public_float"], [7.5e7, 7e8], ["under $75 million", "$75-700 million", "$700 million or more"])
        fy = f"fiscal year {f['fy_end'][:4]}"
    parts = ([f"industry: {ind}"] if ind else []) + [fy, f"total assets: {assets}", f"public float: {flt}",
                                                       f"exchange listing (Section 12(b)): {f['exchange'] or 'not reported'}",
                                                       f"filing with the SEC for: {years}"]
    return "; ".join(parts)


PROMPT = """# Company-type baseline

Below are {n} anonymized company profiles for one annual report each. You are NOT given the company names or the reports.
Every value describes the company as of that fiscal year.

For each profile, using only the profile and what you already know, rate the risk that the company's financial statements
for that fiscal year are materially misstated, through fraud or serious accounting errors (0 = no concern, 100 = almost
certainly misstated). Also give your best guess of which company it is ("unknown" if you cannot tell), and say whether you
know of later accounting problems, restatements or SEC enforcement involving that period.

Reply with only this JSON list, one entry per profile, in the order given, and nothing else:
[{{"id": <number as listed>, "risk_score": <int>, "company_guess": "<name or unknown>", "knows_later_problems": <true|false>, "basis": "short reason"}}, ...]

"""

PROBE = """Below are {n} company names (with the fiscal year of one annual report each) and {n} anonymized profiles of the same
{n} annual reports in a different order. Each profile describes exactly one of the listed companies as of that fiscal year.
Match every profile to the company you think it describes, using each company once. Use only what you already know.

Reply with only this JSON list and nothing else:
[{{"id": <profile number>, "company": "<one name exactly as listed>", "confidence": <0-100>}}, ...]

COMPANIES
{names}

PROFILES
{cards}
"""


def _names(sample):
    key = "results/mem_isolated/key.tsv" if sample == "round8" else "results/mem_isolated_oot/key.tsv"
    inp = "data/mem_isolated/input_round8.txt" if sample == "round8" else "data/mem_isolated_oot/input_round9.txt"
    k = {r["pid"]: r["company"] for r in csv.DictReader(open(key), delimiter="\t")}
    fy = {}
    for l in open(inp, encoding="utf-8"):
        if l.strip():
            n = re.sub(r"^\s*\d+\.\s*", "", l).split(" — ")[0]
            fy[n] = l.strip().rsplit(" ", 1)[1]
    return {p: f"{n} (fiscal year ended {fy[n]})" for p, n in k.items()}


def cmd_cards(level):
    facts = json.load(open(f"{D}/facts.json"))
    return {s: {p: card(f, level) for p, f in facts.items() if f["sample"] == s} for s in SAMPLES}


def cmd_probe(args):
    cards = cmd_cards(args.level)
    os.makedirs(f"{R}/probe", exist_ok=True)
    for s in SAMPLES:
        names = _names(s)
        pids = sorted(cards[s])
        rng = random.Random(f"probe{args.level}{s}")
        np_, cp = pids[:], pids[:]
        rng.shuffle(np_); rng.shuffle(cp)
        prompt = PROBE.format(n=len(pids), names="\n".join(names[p] for p in np_),
                              cards="\n".join(f"{i}. {cards[s][p]}" for i, p in enumerate(cp, 1)))
        raw = f"{R}/probe/{args.level}_{s}.jsonl"
        v = verify(claude(prompt, HARDENED, raw))
        rep = parse_scores(v["answer"]) or []
        guess = {int(e["id"]): str(e.get("company", "")) for e in rep if "id" in e}
        bare = lambda x: x.split(" (fiscal")[0].strip().lower()   # the model answers with the name, without the year
        correct = [cp[i - 1] for i, g in guess.items() if 1 <= i <= len(cp) and bare(g) == bare(names[cp[i - 1]])]
        json.dump({"level": args.level, "sample": s, "checks_pass": v["all_pass"], "card_order": cp, "name_order": np_,
                   "reply": rep, "correct": correct}, open(f"{R}/probe/{args.level}_{s}.json", "w"), indent=1)
        print(f"{args.level} {s}: checks_pass={v['all_pass']} matched {len(correct)}/{len(pids)} correct; replies={len(rep)}")


def cmd_run(args):
    cards = cmd_cards(args.level)
    for s in SAMPLES:
        out = f"{R}/{args.level}/{s}"
        os.makedirs(f"{out}/raw", exist_ok=True)
        pids = sorted(cards[s])
        for k in range(1, args.runs + 1):
            order = pids[:]
            random.Random(args.seed + k).shuffle(order)
            listing = "\n".join(f"{i}. {cards[s][p]}" for i, p in enumerate(order, 1))
            raw = f"{out}/raw/run{k}.jsonl"
            for attempt in (1, 2):
                v = verify(claude(PROMPT.format(n=len(pids)) + listing + "\n", HARDENED, raw))
                rep = parse_scores(v["answer"])
                ok = isinstance(rep, list) and sorted(int(e["id"]) for e in rep) == list(range(1, len(pids) + 1))
                if ok or attempt == 2:
                    break
                os.replace(raw, f"{out}/raw/run{k}_incomplete{attempt}.jsonl")
            json.dump({"seed": args.seed + k, "order": order, "listing": listing, "attempts": attempt, "complete": ok,
                       "verification": {c: v[c] for c in ("tools_empty", "mcp_empty", "no_tool_blocks", "server_web_zero",
                                                          "no_subagents", "single_turn", "completed", "all_pass")},
                       "reply": rep}, open(f"{out}/run{k}.json", "w"), indent=1, ensure_ascii=False)
            print(f"{s} run{k}: all_pass={v['all_pass']} complete={ok} attempts={attempt}", flush=True)


def cmd_evaluate(args):
    from experiment.edgar_risk.round3 import auc, auc_ci
    from experiment.mem_isolated import _pairs_auc, spearman
    import statistics as st
    names = {s: _names(s) for s in SAMPLES}
    L = [f"# 實驗 E2：公司類型卡評分結果（等級 {args.level}）", "",
         "| 樣本 | 5 次 AUC | 平均分數 AUC | 95% CI | 組內勝／平／負 | 猜中公司（5 次合計） | 說「知道」（5 次合計） | 與只給名稱 MEM 的 Spearman ρ |",
         "|---|---|---|---|---|---|---|---|"]
    mem_dirs = {"round8": "results/mem_isolated", "oot": "results/mem_isolated_oot"}
    from experiment.mem_isolated import _by_pid
    for s in SAMPLES:
        out = f"{R}/{args.level}/{s}"
        runs = []
        for k in range(1, 6):
            for p in (f"{out}/raw/run{k}.jsonl", f"{out}/run{k}.json"):
                if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", p]).returncode or \
                        subprocess.run(["git", "ls-files", "--error-unmatch", p], capture_output=True).returncode:
                    raise SystemExit(f"{p} is not committed unchanged")
            v = verify(load_events(f"{out}/raw/run{k}.jsonl"))
            if not v["all_pass"]:
                raise SystemExit(f"{out}/raw/run{k}.jsonl fails verification")
            j = json.load(open(f"{out}/run{k}.json"))
            runs.append({j["order"][int(e["id"]) - 1]: e for e in j["reply"]})
        pids = sorted(runs[0])
        per = [_pairs_auc({p: int(r[p]["risk_score"]) for p in pids})[0] for r in runs]
        mean = {p: st.mean(int(r[p]["risk_score"]) for r in runs) for p in pids}
        a, lo, hi, w, t, l = _pairs_auc(mean)
        def hit(r, p):
            g = str(r[p].get("company_guess", "")).lower()
            n = names[s][p].split(" (fiscal")[0].lower()
            tok = re.split(r"[ ,.]", n)[0]
            return g not in ("", "unknown") and (tok in g or g in n)
        hits = sum(hit(r, p) for r in runs for p in pids)
        knows = sum(bool(r[p].get("knows_later_problems")) for r in runs for p in pids)
        key = "results/mem_isolated/key.tsv" if s == "round8" else "results/mem_isolated_oot/key.tsv"
        kk = {r["company"]: r["pid"] for r in csv.DictReader(open(key), delimiter="\t")}
        mem = [_by_pid(json.load(open(f"{mem_dirs[s]}/run{k}.json"))["scores"], open(f"{mem_dirs[s]}/inputs/run{k}.txt").read(), kk)
               for k in range(1, 6)]
        memmean = [st.mean(m[p][0] for m in mem) for p in pids]
        rho = spearman([mean[p] for p in pids], memmean)
        L.append(f"| {s} | {' / '.join(f'{x:.2f}' for x in per)} | **{a:.2f}** | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} | "
                 f"{hits}/{5 * len(pids)} | {knows}/{5 * len(pids)} | {rho:.2f} |")
        with open(f"{R}/{args.level}/{s}_scores.csv", "w", newline="") as fh:
            wr = csv.writer(fh); wr.writerow(["pid", "card"] + [f"run{k}" for k in range(1, 6)] + ["mean", "name_only_mem_mean"])
            for p, mm in zip(pids, memmean):
                wr.writerow([p, card(json.load(open(f"{D}/facts.json"))[p], args.level)] +
                            [runs[k][p]["risk_score"] for k in range(5)] + [f"{mean[p]:.1f}", f"{mm:.1f}"])
    open(f"{R}/evaluation.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build").set_defaults(fn=cmd_build)
    for name, fn in (("probe", cmd_probe), ("run", cmd_run), ("evaluate", cmd_evaluate)):
        p = sub.add_parser(name); p.add_argument("--level", default="L1"); p.set_defaults(fn=fn)
        if name == "run":
            p.add_argument("--runs", type=int, default=5); p.add_argument("--seed", type=int, default=20261110)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

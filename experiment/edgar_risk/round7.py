"""Round 7 pilot: recent AAER cases, automatically matched controls, XBRL-based M / F / C.

Steps (see results/round7/protocol.md)
  python -m experiment.edgar_risk.round7 index      # SEC Financial Statement Data Sets sub.txt -> 10-K index
  python -m experiment.edgar_risk.round7 controls   # one control per case: same SIC, same period, closest assets
  python -m experiment.edgar_risk.round7 extract    # XBRL companyfacts -> values as filed in each 10-K
  python -m experiment.edgar_risk.round7 features   # M, F, consistency checks (round 5 code)
  python -m experiment.edgar_risk.round7 evaluate   # joins labels

Network steps need an SEC User-Agent with a contact e-mail in the SEC_UA environment variable.
"""
import argparse
import csv
import datetime as dt
import gzip
import json
import math
import os
import random
import re
import struct
import subprocess
import sys
import time
import zlib
from collections import defaultdict

from . import round5
from .round3 import auc, auc_ci

CASES = "config/round7_cases.json"
DATA = "data/round7"
OUT = "results/round7"
INDEX = f"{DATA}/sub_10k.tsv.gz"
FACTS = f"{DATA}/companyfacts"  # cache, not committed
AAER = f"{DATA}/aaer_list_2017_2026.json"
FSDS = "https://www.sec.gov/files/dera/data/financial-statement-data-sets/{q}.zip"


# ---------------------------------------------------------------- SEC access
def _ua():
    ua = os.environ.get("SEC_UA")
    if not ua:
        sys.exit("set SEC_UA, e.g. 'Your Name your@email' (SEC requires a contact in the User-Agent)")
    return ua


def _get(url, out=None, rng=None):
    cmd = ["curl", "-s", "--fail", "-A", _ua()] + (["-r", rng] if rng else []) + (["-o", out] if out else []) + [url]
    for attempt in range(4):
        r = subprocess.run(cmd, capture_output=True)
        if r.returncode == 0:
            time.sleep(0.12)  # stay well under the SEC's 10 requests per second
            return r.stdout
        time.sleep(2 ** attempt)
    raise RuntimeError(f"download failed: {url}")


def _zip_member(url, name):
    """Read one member of a remote zip with HTTP range requests (the data-set zips are ~100 MB each)."""
    head = subprocess.run(["curl", "-sI", "-A", _ua(), url], capture_output=True, text=True).stdout
    n = int([ln for ln in head.splitlines() if ln.lower().startswith("content-length")][-1].split()[1])
    tail = _get(url, rng=f"{n - 65536}-{n - 1}")
    i = tail.rfind(b"PK\x05\x06")
    cd_size, cd_off = struct.unpack("<II", tail[i + 12:i + 20])
    cd = _get(url, rng=f"{cd_off}-{cd_off + cd_size - 1}")
    p = 0
    while p < len(cd):
        meth, csz = struct.unpack("<H", cd[p + 10:p + 12])[0], struct.unpack("<I", cd[p + 20:p + 24])[0]
        nl, el, cl = struct.unpack("<HHH", cd[p + 28:p + 34])
        off = struct.unpack("<I", cd[p + 42:p + 46])[0]
        if cd[p + 46:p + 46 + nl].decode() == name:
            lh = _get(url, rng=f"{off}-{off + 29}")
            ln, le = struct.unpack("<HH", lh[26:30])
            start = off + 30 + ln + le
            data = _get(url, rng=f"{start}-{start + csz - 1}")
            return zlib.decompress(data, -15) if meth == 8 else data
        p += 46 + nl + el + cl
    raise KeyError(name)


# ---------------------------------------------------------------- 10-K index
def index(args):
    keep = ["adsh", "cik", "name", "sic", "form", "period", "fy", "fp", "filed"]
    rows = []
    for y in range(2016, 2025):
        for q in range(1, 5):
            txt = _zip_member(FSDS.format(q=f"{y}q{q}"), "sub.txt").decode("latin-1")
            for r in csv.DictReader(txt.splitlines(), delimiter="\t"):
                if r["form"] in ("10-K", "10-KT"):
                    rows.append({k: r[k] for k in keep})
            print(y, q, len(rows), flush=True)
    os.makedirs(DATA, exist_ok=True)
    with gzip.open(INDEX, "wt", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keep, delimiter="\t")
        w.writeheader()
        w.writerows(rows)


def load_index():
    with gzip.open(INDEX, "rt", encoding="utf-8") as fh:
        return list(csv.DictReader(fh, delimiter="\t"))


def _date(s):
    return dt.date(int(s[:4]), int(s[4:6]), int(s[6:8])) if "-" not in s else dt.date.fromisoformat(s)


# ---------------------------------------------------------------- controls
SUFFIX = r"\b(the|inc|incorporated|corp|corporation|co|company|ltd|limited|holdings?|group|plc|lp|llc|nv|sa|de)\b"


def _core(name):
    n = re.sub(r"[^a-z0-9 ]", " ", name.lower().replace("&", " and "))
    return re.sub(r"\s+", " ", re.sub(SUFFIX, " ", n)).strip()


def _aaer_names():
    names = set()
    for r in json.load(open(AAER)):
        for part in re.split(r",| and |;|\(", r["name"]):
            c = _core(part)
            if len(c) >= 4:
                names.add(c)
    return names


def _frame_assets(period):
    """Total assets of every filer for the calendar quarter that contains this balance-sheet date."""
    d = _date(period)
    q = (d.month - 1) // 3 + 1
    path = f"{DATA}/frames/Assets_CY{d.year}Q{q}I.json"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _get(f"https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/USD/CY{d.year}Q{q}I.json", out=path)
    return {str(x["cik"]): x["val"] for x in json.load(open(path))["data"]}


def controls(args):
    cases = json.load(open(CASES))
    idx = load_index()
    by_adsh = {r["adsh"]: r for r in idx}
    by_cik = defaultdict(list)
    for r in idx:
        by_cik[r["cik"]].append(r)
    aaer = _aaer_names()
    treated = {str(c["cik"]) for c in cases}
    used = set()
    out = []
    for c in cases:
        t = by_adsh.get(c["y0_acc"])
        if t is None:
            sys.exit(f"{c['name']}: Y0 10-K {c['y0_acc']} not in the data-set index")
        p0 = _date(t["period"])
        assets = _frame_assets(t["period"])
        ta = assets.get(str(c["cik"]))
        pool = []
        for r in idx:
            if r["cik"] in treated or r["cik"] in used or r["form"] != "10-K":
                continue
            if abs((_date(r["period"]) - p0).days) > 92:
                continue
            if _core(r["name"]) in aaer:
                continue
            prior = [x for x in by_cik[r["cik"]] if x["form"] == "10-K" and 330 <= (_date(r["period"]) - _date(x["period"])).days <= 400]
            if not prior or str(r["cik"]) not in assets:
                continue
            pool.append((r, prior[0]))
        chosen, level = None, None
        for digits in (4, 3, 2):
            same = [(r, pr) for r, pr in pool if r["sic"][:digits] == t["sic"][:digits]]
            if len(same) >= 3 or digits == 2:
                same.sort(key=lambda x: abs(math.log(assets[x[0]["cik"]] / ta)))
                chosen, level = same[0], digits
                break
        r, pr = chosen
        used.add(r["cik"])
        out.append({"case": c["name"], "case_cik": c["cik"], "case_sic": t["sic"], "case_assets": ta,
                    "control": r["name"], "control_cik": int(r["cik"]), "control_sic": r["sic"], "sic_digits": level,
                    "control_assets": assets[r["cik"]], "pool_size": len(same),
                    "y0_acc": r["adsh"], "y0_period": r["period"], "y1_acc": pr["adsh"], "y1_period": pr["period"]})
        print(f"{c['name']:<28} -> {r['name']:<40} SIC {r['sic']} ({level} digits, pool {len(same)}), "
              f"assets {ta / 1e6:,.0f}M vs {assets[r['cik']] / 1e6:,.0f}M")
    json.dump(out, open(f"{OUT}/controls.json", "w"), indent=1)


# ---------------------------------------------------------------- XBRL extraction
TAGS = {
    "rev": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet",
            "RevenueFromContractWithCustomerIncludingAssessedTax"],
    "cogs": ["CostOfGoodsAndServicesSold", "CostOfRevenue", "CostOfGoodsSold", "CostOfServices"],
    "gp": ["GrossProfit"],
    "sga": ["SellingGeneralAndAdministrativeExpense"],
    "dep": ["DepreciationDepletionAndAmortization", "DepreciationAndAmortization", "Depreciation"],
    "ni": ["NetIncomeLoss", "ProfitLoss"],
    "eps_d": ["EarningsPerShareDiluted"],
    "sh_d": ["WeightedAverageNumberOfDilutedSharesOutstanding"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue"],
    "rcash": ["RestrictedCashCurrent", "RestrictedCashAndCashEquivalentsAtCarryingValue"],
    "rcash_nc": ["RestrictedCashNoncurrent", "RestrictedCashAndCashEquivalentsNoncurrent"],
    "ar": ["AccountsReceivableNetCurrent"],
    "inv": ["InventoryNet"],
    "tca": ["AssetsCurrent"],
    "ppe": ["PropertyPlantAndEquipmentNet"],
    "ta": ["Assets"],
    "tcl": ["LiabilitiesCurrent"],
    "ltd": ["LongTermDebtNoncurrent", "LongTermDebt"],
    "tl": ["Liabilities"],
    "eq": ["StockholdersEquity"],
    "tle": ["LiabilitiesAndStockholdersEquity"],
    "mi": ["MinorityInterest"],
    "re": ["RetainedEarningsAccumulatedDeficit"],
    "cfo": ["NetCashProvidedByUsedInOperatingActivities"],
    "cfi": ["NetCashProvidedByUsedInInvestingActivities"],
    "cff": ["NetCashProvidedByUsedInFinancingActivities"],
    "fx": ["EffectOfExchangeRateOnCashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents",
           "EffectOfExchangeRateOnCashAndCashEquivalents"],
    "dcash": ["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseIncludingExchangeRateEffect",
              "CashAndCashEquivalentsPeriodIncreaseDecrease"],
    "dcash_ex": ["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect",
                 "CashAndCashEquivalentsPeriodIncreaseDecreaseExcludingExchangeRateEffect"],
    "cash_cf": ["CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents", "CashAndCashEquivalentsAtCarryingValue"],
    "ch_ar": ["IncreaseDecreaseInAccountsReceivable"],
    "ch_inv": ["IncreaseDecreaseInInventories"],
    "div": ["PaymentsOfDividendsCommonStock", "PaymentsOfDividends"],
    "iss_eq": ["ProceedsFromIssuanceOfCommonStock", "ProceedsFromIssuanceOrSaleOfEquity"],
    "iss_debt": ["ProceedsFromIssuanceOfLongTermDebt", "ProceedsFromIssuanceOfDebt", "ProceedsFromIssuanceOfSeniorLongTermDebt",
                 "ProceedsFromConvertibleDebt"],
}
INSTANT = {"cash", "rcash", "rcash_nc", "ar", "inv", "tca", "ppe", "ta", "tcl", "ltd", "tl", "eq", "tle", "mi", "re", "cash_cf"}
NEGATE = {"ch_ar", "ch_inv"}  # XBRL reports the increase; the round-5 checks use the cash-flow sign


def companyfacts(cik):
    path = f"{FACTS}/CIK{int(cik):010d}.json"
    if not os.path.exists(path):
        os.makedirs(FACTS, exist_ok=True)
        _get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json", out=path)
    return json.load(open(path))


def doc_values(facts, acc, period_end, label_year):
    """Values reported in one filing, keyed by item and column year (label_year = year of this filing's period)."""
    gaap = facts.get("facts", {}).get("us-gaap", {})
    e0 = _date(period_end)
    out = defaultdict(dict)
    src = {}
    for item, tags in TAGS.items():
        for tag in tags:
            units = gaap.get(tag, {}).get("units", {})
            unit = "USD/shares" if item == "eps_d" else ("shares" if item == "sh_d" else "USD")
            got = False
            for f in units.get(unit, []):
                if f.get("accn") != acc:
                    continue
                end = _date(f["end"])
                if item not in INSTANT:
                    if "start" not in f or not 330 <= (end - _date(f["start"])).days <= 400:
                        continue
                k = round((e0 - end).days / 365.25)
                if abs((e0 - end).days - 365.25 * k) > 45:
                    continue
                col = label_year - k
                if col in out[item]:
                    continue
                v = f["val"]
                if item not in ("eps_d",):
                    v = v / 1e6  # $ millions; shares in millions
                out[item][col] = -v if item in NEGATE else v
                got = True
            if got:
                src[item] = tag
                break
    # derived items
    for col in list(out.get("cash_cf", {})):
        out["cash_end"][col] = out["cash_cf"][col]
        if col - 1 in out["cash_cf"]:
            out["cash_beg"][col] = out["cash_cf"][col - 1]
        if src.get("cash_cf", "").startswith("CashCashEquivalentsRestricted") and col in out.get("cash", {}):
            out["cash"][col] = out["cash"][col] + out.get("rcash", {}).get(col, 0) + out.get("rcash_nc", {}).get(col, 0)
    if "dcash" not in out:
        for col, v in out.get("dcash_ex", {}).items():
            out["dcash"][col] = v + out.get("fx", {}).get(col, 0)
    for col in set(out.get("iss_eq", {})) | set(out.get("iss_debt", {})) | set(out.get("cfo", {})):
        out["issue"][col] = 1.0 if (out.get("iss_eq", {}).get(col, 0) > 0 or out.get("iss_debt", {}).get(col, 0) > 0) else 0.0
    for k in ("cash_cf", "rcash", "rcash_nc", "dcash_ex", "iss_eq", "iss_debt"):
        out.pop(k, None)
    return out, src


def _pairs():
    cases = {c["name"]: c for c in json.load(open(CASES))}
    rows = []
    for i, ctl in enumerate(json.load(open(f"{OUT}/controls.json")), 1):
        c = cases[ctl["case"]]
        rows.append((f"P{i:02d}T", c["name"], c["cik"], c["y0_acc"], c["y0_period"], c["y1_acc"], c["y1_period"], "treatment", ctl["case_sic"]))
        rows.append((f"P{i:02d}C", ctl["control"], ctl["control_cik"], ctl["y0_acc"], ctl["y0_period"], ctl["y1_acc"], ctl["y1_period"],
                     "control", ctl["control_sic"]))
    return rows


def extract(args):
    lines = []
    sources = {}
    for pid, name, cik, a0, p0, a1, p1, group, sic in _pairs():
        facts = companyfacts(cik)
        y0 = _date(p0).year
        for acc, period, label in ((a0, p0, y0), (a1, p1, y0 - 1)):
            vals, src = doc_values(facts, acc, period, label)
            sources[f"{pid} {acc}"] = src
            for item, cols in vals.items():
                for col, v in sorted(cols.items()):
                    lines.append({"pid": pid, "doc_year": label, "col_year": col, "item": item, "value": round(v, 6),
                                  "unit": "M", "source": f"xbrl {acc}", "note": ""})
        print(pid, name, "done", flush=True)
    with open(f"{OUT}/xbrl_values.tsv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(lines[0].keys()), delimiter="\t")
        w.writeheader()
        w.writerows(lines)
    json.dump(sources, open(f"{OUT}/xbrl_tags_used.json", "w"), indent=1)


# ---------------------------------------------------------------- features and checks (round 5 code)
def _key():
    key = {}
    for pid, name, cik, a0, p0, a1, p1, group, sic in _pairs():
        bank = sic[:2] in ("60", "61", "62", "63", "64", "67")
        # cik "none" keeps round 5's text check (IV-1) from picking up an old EDGAR-CORPUS file
        key[pid] = {"name": name, "cik": "none", "year": _date(p0).year, "group": group,
                    "industry": "financial" if bank else sic, "sic": sic}
    return key


def _load():
    vals = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    units = defaultdict(dict)
    for r in csv.DictReader(open(f"{OUT}/xbrl_values.tsv"), delimiter="\t"):
        vals[r["pid"]][int(r["doc_year"])][r["item"]][int(r["col_year"])] = float(r["value"])
        units[r["pid"]][int(r["doc_year"])] = "M"
    return vals, units


def features(args):
    key = _key()
    vals, units = _load()
    notes = defaultdict(lambda: defaultdict(str))
    feats = round5.features(vals, notes, key, None)
    # Latch's Y-1 10-K belongs to the SPAC shell, so its prior-year document is not comparable (protocol 1)
    for pid, k in key.items():
        if k["name"] == "Latch":
            vals[pid].pop(k["year"] - 1, None)
    rows = [r for r in round5.run_checks(vals, notes, units, key, None) if not r["check"].startswith(("IV-1", "II-1", "II-6"))]
    for name, data in (("financial_features.csv", feats), ("consistency_checks.csv", rows)):
        with open(f"{OUT}/{name}", "w", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=list(data[0].keys()))
            w.writeheader()
            w.writerows(data)
    scores = round5.consistency_scores(rows, {})
    with open(f"{OUT}/consistency_scores.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pid", "C", "C_program", "unexplained_failures", "explained", "testable_weight"])
        w.writeheader()
        for pid in sorted(scores):
            w.writerow(dict(pid=pid, **scores[pid]))
    print(f"{len(feats)} firms; {sum(r['status'] != 'untestable' for r in rows)} testable checks; "
          f"{sum(r['status'] == 'fail' for r in rows)} program failures")


# ---------------------------------------------------------------- evaluation (labels)
def evaluate(args):
    key = _key()
    feats = {r["pid"]: r for r in csv.DictReader(open(f"{OUT}/financial_features.csv"))}
    cons = {r["pid"]: r for r in csv.DictReader(open(f"{OUT}/consistency_scores.csv"))}
    num = lambda s: float(s) if s not in ("", None) else None
    neg = lambda s: -float(s) if s not in ("", None) else None
    meth = {
        "M Beneish": {p: num(feats[p]["M"]) for p in key},
        "F Dechow": {p: num(feats[p]["F"]) for p in key},
        "C consistency (program)": {p: num(cons[p]["C_program"]) for p in key},
        "CFO/NI (lower = riskier)": {p: neg(feats[p]["cfo_to_ni"]) for p in key},
        "Accruals TATA": {p: num(feats[p]["TATA"]) for p in key},
    }
    lines = ["# Round 7 pilot evaluation (14 recent AAER cases vs matched controls)", "",
             "| Method | n (treat/ctrl) | AUC | 95% CI |", "|---|---|---|---|"]
    for m, v in meth.items():
        pos = [v[p] for p in key if key[p]["group"] == "treatment" and v[p] is not None]
        ngt = [v[p] for p in key if key[p]["group"] == "control" and v[p] is not None]
        if len(pos) >= 3 and len(ngt) >= 3:
            lo, hi = auc_ci(pos, ngt)
            lines.append(f"| {m} | {len(pos)}/{len(ngt)} | {auc(pos, ngt):.2f} | {lo:.2f}-{hi:.2f} |")
    lines += ["", "## Within-pair (treatment higher / tie / lower / not computable)"]
    for m, v in meth.items():
        w = t = l = na = 0
        for i in range(1, 15):
            a, b = v.get(f"P{i:02d}T"), v.get(f"P{i:02d}C")
            if a is None or b is None:
                na += 1
            else:
                w, t, l = w + (a > b), t + (a == b), l + (a < b)
        lines.append(f"- {m}: {w} / {t} / {l} / {na}")
    lines += ["", "## Threshold flags"]
    for m, thr in (("M Beneish", -1.78), ("F Dechow", 1.0), ("C consistency (program)", 0.0)):
        for grp in ("treatment", "control"):
            vs = [meth[m][p] for p in key if key[p]["group"] == grp and meth[m][p] is not None]
            lines.append(f"- {m} > {thr}, {grp}: {sum(x > thr for x in vs)}/{len(vs)}")
    lines += ["", "## Per pair", "| Pair | Case | M | F | C | CFO/NI | Control | M | F | C | CFO/NI |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for i in range(1, 15):
        t, c = f"P{i:02d}T", f"P{i:02d}C"
        cell = lambda p: " | ".join(str(x) if x != "" else "—" for x in (feats[p]["M"], feats[p]["F"], cons[p]["C_program"], feats[p]["cfo_to_ni"]))
        lines.append(f"| {i} | {key[t]['name']} | {cell(t)} | {key[c]['name']} | {cell(c)} |")
    txt = "\n".join(lines)
    open(f"{OUT}/evaluation_output.md", "w").write(txt + "\n")
    print(txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("action", choices=["index", "controls", "extract", "features", "evaluate"])
    args = ap.parse_args()
    os.makedirs(OUT, exist_ok=True)
    {"index": index, "controls": controls, "extract": extract, "features": features, "evaluate": evaluate}[args.action](args)


if __name__ == "__main__":
    main()

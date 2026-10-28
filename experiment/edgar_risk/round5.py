"""Round 5: financial-statement features (Beneish M, Dechow F) and statement-consistency checks.

Inputs
  results/round5/raw_values.tsv     values read from the Y0 and Y-1 10-Ks (document units)
  results/round5/check_review.tsv   manual verdict for every check the program fails (see protocol 6.3)
  data/round4/<cik>_<year>.json     EDGAR-CORPUS text (Item 7) for the text-vs-figures check

Usage
  python -m experiment.edgar_risk.round5 features   # writes financial_features.csv, consistency_checks.csv
  python -m experiment.edgar_risk.round5 evaluate   # joins labels (after the above are committed)
"""
import argparse
import csv
import glob
import json
import math
import os
import random
import re
from collections import defaultdict

from .round3 import auc, auc_ci

OUT = "results/round5"
RAW = f"{OUT}/raw_values.tsv"
REVIEW = f"{OUT}/check_review.tsv"
FILINGS = "data/round5/filings.json"
KEY = "results/round4/key.json"
SCALE = {"K": 0.001, "M": 1.0, "U": 1e-6}
PER_SHARE = {"eps_d"}
COUNTS = {"sh_d", "issue", "restated_label", "doc_note", "merger_note"}
WEIGHT = {"I": 3, "II": 2, "III": 3, "IV": 1}
FINANCIAL = {"financial"}


# ---------------------------------------------------------------- loading
def load_values():
    """vals[pid][doc_year][item][col_year] = value in $ millions (per-share and counts unscaled)."""
    vals = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    notes = defaultdict(lambda: defaultdict(str))
    units = defaultdict(dict)
    for r in csv.DictReader(open(RAW), delimiter="\t"):
        item, v = r["item"], float(r["value"])
        if item not in PER_SHARE | COUNTS and not item.startswith("q"):
            v *= SCALE[r["unit"]]
        elif item.startswith("q"):
            v *= SCALE[r["unit"]]
        vals[r["pid"]][int(r["doc_year"])][item][int(r["col_year"])] = v
        if r["note"]:
            notes[r["pid"]][item] += r["note"] + " "
        units[r["pid"]][int(r["doc_year"])] = r["unit"]
    return vals, notes, units


def tol(a, b, unit_m):
    """Protocol 6.1: max(0.5% of the larger amount, twice the reporting unit)."""
    return max(0.005 * max(abs(a), abs(b)), 2 * unit_m)


def unit_of(units, pid, doc):
    u = units[pid].get(doc, "M")
    return {"K": 0.001, "M": 0.1, "U": 1e-6}[u]


# ---------------------------------------------------------------- checks
def run_checks(vals, notes, units, key, filings):
    rows = []

    def add(pid, code, a, b, status, detail=""):
        rows.append(dict(pid=pid, check=code, value_a="" if a is None else round(a, 4),
                         value_b="" if b is None else round(b, 4),
                         diff="" if a is None or b is None else round(a - b, 4), status=status, detail=detail))

    for pid in sorted(key):
        fy = key[pid]["year"]
        d = vals[pid].get(fy, {})
        prev = vals[pid].get(fy - 1, {})
        u = unit_of(units, pid, fy)
        nt = notes[pid]

        def g(item, year):
            return d.get(item, {}).get(year)

        for yr, tag in ((fy, "Y0"), (fy - 1, "Y-1")):
            # I-1 assets = liabilities + equity
            ta, tle = g("ta", yr), g("tle", yr)
            computed = re.search(r"computed|sum of|= liab|unlabelled|liabilities \+", nt.get("ta", ""))
            if ta is not None and tle is not None and not computed:
                add(pid, f"I-1 {tag}", ta, tle, "pass" if abs(ta - tle) <= tol(ta, tle, u) else "fail", "total assets vs total liabilities and equity")
            elif ta is not None and g("tl", yr) is not None and g("eq", yr) is not None and not computed:
                mi = 0 if re.search(r"minority", nt.get("tl", "")) else (g("mi", yr) or 0)
                rhs = g("tl", yr) + g("eq", yr) + mi
                add(pid, f"I-1 {tag}", ta, rhs, "pass" if abs(ta - rhs) <= tol(ta, rhs, u) else "fail", "total assets vs liabilities + minority + equity")
            else:
                add(pid, f"I-1 {tag}", None, None, "untestable", "total-assets row not independently reported" if computed else "missing items")
            # I-3 revenue - cost of sales = gross profit
            rev, cogs, gp = g("rev", yr), g("cogs", yr), g("gp", yr)
            if None not in (rev, cogs, gp):
                add(pid, f"I-3 {tag}", rev - cogs, gp, "pass" if abs(rev - cogs - gp) <= tol(rev, gp, u) else "fail", "revenue - cost of sales vs gross profit")
            else:
                add(pid, f"I-3 {tag}", None, None, "untestable", "no gross-profit line")
            # I-4 sections sum to net change in cash
            parts = [g(k, yr) for k in ("cfo", "cfi", "cff")]
            dc = g("dcash", yr)
            if None not in parts and dc is not None and "computed" not in nt.get("dcash", ""):
                s = sum(parts) + (g("fx", yr) or 0)
                add(pid, f"I-4 {tag}", s, dc, "pass" if abs(s - dc) <= tol(s, dc, u) * 2 else "fail", "CFO+CFI+CFF+FX vs net change in cash")
            else:
                add(pid, f"I-4 {tag}", None, None, "untestable", "cash-flow sections incomplete")
            # I-5 beginning cash + change = ending cash
            cb, ce = g("cash_beg", yr), g("cash_end", yr)
            if None not in (cb, ce, dc):
                add(pid, f"I-5 {tag}", cb + dc, ce, "pass" if abs(cb + dc - ce) <= tol(cb + dc, ce, u) else "fail", "beginning cash + change vs ending cash")
            else:
                add(pid, f"I-5 {tag}", None, None, "untestable", "missing cash roll-forward")
            # I-6 diluted EPS
            ni, sh, eps = g("ni", yr), g("sh_d", yr), g("eps_d", yr)
            if None not in (ni, sh, eps) and sh:
                unit_scale = SCALE[units[pid][fy]]
                calc = ni / unit_scale / sh
                add(pid, f"I-6 {tag}", calc, eps, "pass" if abs(calc - eps) <= max(0.02, 0.02 * abs(eps)) else "fail", "net income / diluted shares vs diluted EPS")
            else:
                add(pid, f"I-6 {tag}", None, None, "untestable", "shares or EPS not recorded")
            # II-1 income statement NI = cash-flow NI
            ncf = g("ni_cf", yr)
            cands = [g(k, yr) for k in ("ni", "ni_tot", "ni_cont") if g(k, yr) is not None]
            if ncf is not None and cands:
                best = min(cands, key=lambda c: abs(c - ncf))
                add(pid, f"II-1 {tag}", best, ncf, "pass" if abs(best - ncf) <= tol(best, ncf, u) else "fail", "income statement vs cash-flow starting income")
            else:
                add(pid, f"II-1 {tag}", None, None, "untestable", "no cash-flow starting income")
            # II-2 CF ending cash = BS cash
            cash = g("cash", yr)
            if None not in (cash, ce):
                add(pid, f"II-2 {tag}", ce, cash, "pass" if abs(ce - cash) <= tol(ce, cash, u) else "fail", "cash-flow ending cash vs balance-sheet cash")
            else:
                add(pid, f"II-2 {tag}", None, None, "untestable", "missing cash")
        # II-3 retained earnings roll-forward (Y0 only; needs Y-1 balance)
        re0, re1, ni0, div0, ta0 = g("re", fy), g("re", fy - 1), g("ni", fy), g("div", fy), g("ta", fy)
        if None not in (re0, re1, ni0) and ta0:
            calc = re1 + ni0 - (div0 or 0)
            add(pid, "II-3", calc, re0, "pass" if abs(calc - re0) <= 0.005 * ta0 else "fail", "RE(t-1) + NI - dividends vs RE(t)")
        else:
            add(pid, "II-3", None, None, "untestable", "missing retained earnings or dividends")
        # II-4 / II-5 working-capital articulation
        for code, bs, cf in (("II-4", "ar", "ch_ar"), ("II-5", "inv", "ch_inv")):
            b0, b1, c0 = g(bs, fy), g(bs, fy - 1), g(cf, fy)
            if None not in (b0, b1, c0) and ta0:
                implied = -(b0 - b1)
                add(pid, code, implied, c0, "pass" if abs(implied - c0) <= 0.01 * ta0 else "fail", f"-change in balance-sheet {bs} vs cash-flow {cf}")
            else:
                add(pid, code, None, None, "untestable", f"missing {bs} or {cf}")
        # II-6 quarters sum to the year
        for item, ann in (("qrev", "rev"), ("qni", "ni")):
            qs = [d.get(f"{item}{i}", {}).get(fy) for i in range(1, 5)]
            a = g(ann, fy)
            if None not in qs and a is not None:
                s = sum(qs)
                add(pid, f"II-6 {ann}", s, a, "pass" if abs(s - a) <= max(0.005 * abs(a), 4 * u) else "fail", f"sum of quarterly {ann} vs annual")
            else:
                add(pid, f"II-6 {ann}", None, None, "untestable", "no quarterly table")
        # III-1 prior-year figures vs the prior 10-K as originally filed
        for item in ("rev", "ni", "ta", "eq", "cfo", "ar"):
            a = g(item, fy - 1)
            b = prev.get(item, {}).get(fy - 1)
            if a is not None and b is not None:
                status = "pass" if abs(a - b) <= tol(a, b, max(u, unit_of(units, pid, fy - 1))) else "fail"
                add(pid, f"III-1 {item}", a, b, status, "Y-1 figure in Y0 10-K vs Y-1 10-K as filed")
            else:
                add(pid, f"III-1 {item}", None, None, "untestable", "no prior-year 10-K value")
        # IV-1 MD&A text vs figures
        for r in text_checks(pid, key[pid], d, fy):
            rows.append(r)
    return rows


AMT = re.compile(r"\$\s?(?P<num>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?P<mag>billion|million|thousand)?", re.I)


def text_checks(pid, k, d, fy):
    """IV-1: sentences in Item 7 that state Y0 revenue or net income as a dollar amount."""
    out = []
    files = glob.glob(f"data/round4/{k['cik']}_*.json")
    if not files:
        return [dict(pid=pid, check="IV-1", value_a="", value_b="", diff="", status="untestable", detail="no corpus text")]
    text = json.load(open(files[0])).get("section_7", "") or ""
    pats = {"rev": r"\b(total revenues?|net revenues?|revenues?|net sales|total net sales|sales)\b",
            "ni": r"\bnet (income|earnings|loss)\b"}
    tested = 0
    for item, pat in pats.items():
        y0, y1 = d.get(item, {}).get(fy), d.get(item, {}).get(fy - 1)
        if y0 is None:
            continue
        for sent in re.split(r"(?<=[.;])\s+", text):
            if len(sent) > 400 or not re.search(pat, sent, re.I) or str(fy) not in sent:
                continue
            if re.search(r"segment|division|group|international|domestic|quarter|per share|percent of|%\s+of|"
                         r"excluding|pro forma|backlog|guidance|expect|anticipat", sent, re.I):
                continue
            m = re.search("(?:" + pat + r")[^$]{0,80}?" + AMT.pattern, sent, re.I)
            if not m:
                continue
            raw_num = m.group("num")
            num = float(raw_num.replace(",", ""))
            mult = {"billion": 1000, "million": 1, "thousand": 0.001}.get((m.group("mag") or "").lower())
            if mult is None:
                continue
            stated = num * mult
            if stated < 0.01 * abs(y0):  # fragments such as "$3 million increase"
                continue
            prec = 10 ** -len(raw_num.split(".")[1]) * mult if "." in raw_num else mult
            ok = any(v is not None and abs(abs(v) - stated) <= max(0.01 * abs(v), prec) for v in (y0, y1))
            tested += 1
            out.append(dict(pid=pid, check=f"IV-1 {item}", value_a=round(stated, 4), value_b=round(y0, 4),
                            diff=round(stated - abs(y0), 4), status="pass" if ok else "fail",
                            detail=sent.strip()[:300]))
            break
    if not tested:
        out.append(dict(pid=pid, check="IV-1", value_a="", value_b="", diff="", status="untestable", detail="no matching sentence"))
    return out


# ---------------------------------------------------------------- financial models
def ratio(a, b):
    return a / b if a is not None and b not in (None, 0) else None


def features(vals, notes, key, filings):
    out = []
    for pid in sorted(key):
        k = key[pid]
        fy = k["year"]
        d = vals[pid].get(fy, {})
        prev = vals[pid].get(fy - 1, {})

        def g(item, yr):
            return d.get(item, {}).get(yr)

        t, s = fy, fy - 1
        rev0, rev1 = g("rev", t), g("rev", s)
        gp0 = g("gp", t) if g("gp", t) is not None else (rev0 - g("cogs", t) if None not in (rev0, g("cogs", t)) else None)
        gp1 = g("gp", s) if g("gp", s) is not None else (rev1 - g("cogs", s) if None not in (rev1, g("cogs", s)) else None)
        dep0 = g("dep", t) if g("dep", t) is not None else g("dep_cf", t)
        dep1 = g("dep", s) if g("dep", s) is not None else g("dep_cf", s)
        ta0, ta1 = g("ta", t), g("ta", s)
        ta2 = prev.get("ta", {}).get(s - 1)
        ni_c0 = g("ni_cont", t) if g("ni_cont", t) is not None else g("ni", t)
        ni0, ni1 = g("ni", t), g("ni", s)
        f = dict(pid=pid, industry=k["industry"])
        financial = k["industry"] in FINANCIAL or "merger" in notes[pid].get("merger_note", "") or "merger_note" in d
        # Beneish 1999
        comp = {
            "DSRI": ratio(ratio(g("ar", t), rev0), ratio(g("ar", s), rev1)),
            "GMI": ratio(ratio(gp1, rev1), ratio(gp0, rev0)),
            "AQI": ratio(1 - (g("tca", t) + g("ppe", t)) / ta0 if None not in (g("tca", t), g("ppe", t), ta0) else None,
                         1 - (g("tca", s) + g("ppe", s)) / ta1 if None not in (g("tca", s), g("ppe", s), ta1) else None),
            "SGI": ratio(rev0, rev1),
            "DEPI": ratio(ratio(dep1, (dep1 or 0) + (g("ppe", s) or 0)) if dep1 is not None and g("ppe", s) is not None else None,
                          ratio(dep0, (dep0 or 0) + (g("ppe", t) or 0)) if dep0 is not None and g("ppe", t) is not None else None),
            "SGAI": ratio(ratio(g("sga", t), rev0), ratio(g("sga", s), rev1)),
            "LVGI": ratio(ratio((g("tcl", t) or 0) + (g("ltd", t) or 0), ta0) if g("tcl", t) is not None else None,
                          ratio((g("tcl", s) or 0) + (g("ltd", s) or 0), ta1) if g("tcl", s) is not None else None),
            "TATA": ratio(ni_c0 - g("cfo", t), ta0) if None not in (ni_c0, g("cfo", t)) else None,
        }
        missing = [c for c, v in comp.items() if v is None]
        f.update({c: (round(v, 4) if v is not None else "") for c, v in comp.items()})
        if financial or len(missing) > 3:
            f["M"] = ""
        else:
            x = {c: (v if v is not None else (0.0 if c == "TATA" else 1.0)) for c, v in comp.items()}
            f["M"] = round(-4.84 + 0.920 * x["DSRI"] + 0.528 * x["GMI"] + 0.404 * x["AQI"] + 0.892 * x["SGI"]
                           + 0.115 * x["DEPI"] - 0.172 * x["SGAI"] + 4.679 * x["TATA"] - 0.327 * x["LVGI"], 4)
        f["M_missing"] = ";".join(missing)
        # Dechow et al. 2011 model 1 (rsst_acc uses the protocol's fallback: (NI - CFO) / average assets)
        avg0 = (ta0 + ta1) / 2 if None not in (ta0, ta1) else ta0
        avg1 = (ta1 + ta2) / 2 if None not in (ta1, ta2) else ta1
        dar0 = (g("ar", t) - g("ar", s)) if None not in (g("ar", t), g("ar", s)) else None
        dar1 = (g("ar", s) - prev.get("ar", {}).get(s - 1)) if None not in (g("ar", s), prev.get("ar", {}).get(s - 1)) else None
        dinv = (g("inv", t) - g("inv", s)) if None not in (g("inv", t), g("inv", s)) else 0.0
        fv = {
            "rsst_acc": ratio(ni_c0 - g("cfo", t), avg0) if None not in (ni_c0, g("cfo", t), avg0) else None,
            "ch_rec": ratio(dar0, avg0),
            "ch_inv": ratio(dinv, avg0),
            "soft_assets": ratio(ta0 - (g("ppe", t) or 0) - (g("cash", t) or 0), ta0) if ta0 else None,
            "ch_cs": None,
            "ch_roa": (ratio(ni0, avg0) - ratio(ni1, avg1)) if None not in (ni0, ni1, avg0, avg1) else None,
            "issue": g("issue", t),
        }
        if None not in (rev0, rev1, dar0):
            cs0, cs1 = rev0 - dar0, rev1 - (dar1 or 0.0)
            fv["ch_cs"] = ratio(cs0 - cs1, cs1)
        f.update({c: (round(v, 4) if v is not None else "") for c, v in fv.items()})
        fmiss = [c for c, v in fv.items() if v is None]
        if financial or len(fmiss) > 3:
            f["F"] = ""
        else:
            z = {c: (v if v is not None else 0.0) for c, v in fv.items()}
            p = (-7.893 + 0.790 * z["rsst_acc"] + 2.518 * z["ch_rec"] + 1.191 * z["ch_inv"] + 1.979 * z["soft_assets"]
                 + 0.171 * z["ch_cs"] - 0.932 * z["ch_roa"] + 1.029 * z["issue"])
            f["F"] = round(math.exp(p) / (1 + math.exp(p)) / 0.0037, 4)
        f["F_missing"] = ";".join(fmiss)
        # F3 simple indicators
        f["accrual_ratio"] = f["TATA"]
        f["ar_growth_minus_sales_growth"] = (round(ratio(g("ar", t), g("ar", s)) - ratio(rev0, rev1), 4)
                                             if None not in (g("ar", t), g("ar", s), rev0, rev1) and g("ar", s) else "")
        f["cfo_to_ni"] = round(ratio(g("cfo", t), ni0), 4) if None not in (g("cfo", t), ni0) and ni0 else ""
        out.append(f)
    return out


# ---------------------------------------------------------------- consistency score
def consistency_scores(rows, review):
    """C = 100 * sum(weight * unexplained failure) / sum(weight * testable); program-only variant ignores review."""
    by = defaultdict(list)
    for r in rows:
        by[r["pid"]].append(r)
    res = {}
    for pid, rs in by.items():
        num = den = num_raw = den_raw = 0
        fails = explained = 0
        for r in rs:
            typ = r["check"].split("-")[0]
            w = WEIGHT[typ]
            if r["status"] == "untestable":
                continue
            den_raw += w
            verdict = review.get((pid, r["check"]))
            final = r["status"]
            if r["status"] == "fail":
                num_raw += w
                if verdict:
                    final = verdict["verdict"]
            if final == "extraction_error":
                continue  # not a check of the filing; re-tested after correction
            den += w
            if final == "fail":
                num += w
                fails += 1
            elif final == "explained":
                explained += 1
        res[pid] = dict(C=round(100 * num / den, 2) if den else "", C_program=round(100 * num_raw / den_raw, 2) if den_raw else "",
                        unexplained_failures=fails, explained=explained, testable_weight=den)
    return res


def load_review():
    if not os.path.exists(REVIEW):
        return {}
    return {(r["pid"], r["check"]): r for r in csv.DictReader(open(REVIEW), delimiter="\t")}


# ---------------------------------------------------------------- evaluation
def pct_rank(xs):
    vals = sorted(v for v in xs.values() if v is not None)
    return {k: (sum(1 for u in vals if u < v) + 0.5 * sum(1 for u in vals if u == v)) / len(vals) if v is not None else None
            for k, v in xs.items()}


def evaluate():
    key = json.load(open(KEY))
    feats = {r["pid"]: r for r in csv.DictReader(open(f"{OUT}/financial_features.csv"))}
    cons = {r["pid"]: r for r in csv.DictReader(open(f"{OUT}/consistency_scores.csv"))}
    kw = {r["packet"]: float(r["keyword_score"]) for r in csv.DictReader(open("results/round4/keyword_scores.csv"))}
    rub = {r["packet"]: float(r["rubric_total"]) for r in csv.DictReader(open("results/round4/scores.csv"))}
    num = lambda s: float(s) if s not in ("", None) else None
    meth = {
        "T keyword": {p: kw[p] for p in key},
        "M Beneish": {p: num(feats[p]["M"]) for p in key},
        "F Dechow": {p: num(feats[p]["F"]) for p in key},
        "C consistency": {p: num(cons[p]["C"]) for p in key},
        "C program-only": {p: num(cons[p]["C_program"]) for p in key},
        "R rubric v2": {p: rub[p] for p in key},
    }
    ranks = {m: pct_rank(v) for m, v in meth.items()}

    def combo(parts):
        out = {}
        for p in key:
            rs = [ranks[m][p] for m in parts if ranks[m][p] is not None]
            out[p] = sum(rs) / len(rs) if rs else None
        return out
    meth["T+F"] = combo(["T keyword", "F Dechow"])
    meth["T+F+C"] = combo(["T keyword", "F Dechow", "C consistency"])
    meth["R+F+C"] = combo(["R rubric v2", "F Dechow", "C consistency"])
    post = {"American International Group", "ITT Educational Services", "Navistar International"}
    lines = []

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
    for i, pr in enumerate(json.load(open("config/round4_pool.json"))["pairs"]):
        pair_of[pr["treatment"]["name"]] = pair_of[pr["control"]["name"]] = i
    all_p = list(key)
    report("All 72 filings", all_p)
    drop_post = {pair_of[key[p]["name"]] for p in key if key[p]["name"] in post}
    report("Excluding post-disclosure pairs (AIG, ITT, Navistar)", [p for p in all_p if pair_of[key[p]["name"]] not in drop_post])
    drop_fin = {pair_of[key[p]["name"]] for p in key if key[p]["industry"] in FINANCIAL}
    report("Excluding financial-industry pairs", [p for p in all_p if pair_of[key[p]["name"]] not in drop_fin])
    # H3: paired bootstrap of AUC(T+F+C) - AUC(T)
    rng = random.Random(7)
    pos = [p for p in key if key[p]["group"] == "treatment"]
    neg = [p for p in key if key[p]["group"] == "control"]

    def a(m, P, N):
        return auc([meth[m][p] for p in P if meth[m][p] is not None], [meth[m][p] for p in N if meth[m][p] is not None])
    diffs = {}
    for comb in ("T+F", "T+F+C"):
        ds = []
        for _ in range(2000):
            P = [rng.choice(pos) for _ in pos]
            N = [rng.choice(neg) for _ in neg]
            ds.append(a(comb, P, N) - a("T keyword", P, N))
        ds.sort()
        diffs[comb] = (a(comb, pos, neg) - a("T keyword", pos, neg), ds[50], ds[1949])
    lines.append("\n## H3: AUC gain over the keyword method (paired bootstrap, 2000 draws)")
    for comb, (dd, lo, hi) in diffs.items():
        lines.append(f"- {comb} - T: {dd:+.2f} (95% CI {lo:+.2f} to {hi:+.2f})")
    # within-pair
    lines.append("\n## Within-pair comparison (treatment higher / tie / lower / not computable)")
    pairs = defaultdict(dict)
    for p in key:
        pairs[pair_of[key[p]["name"]]][key[p]["group"]] = p
    for m in meth:
        w = t = l = na = 0
        for pr in pairs.values():
            if len(pr) < 2:
                continue
            x, y = meth[m][pr["treatment"]], meth[m][pr["control"]]
            if x is None or y is None:
                na += 1
            elif x > y:
                w += 1
            elif x == y:
                t += 1
            else:
                l += 1
        lines.append(f"- {m}: {w} / {t} / {l} / {na}")
    # thresholds
    lines.append("\n## Threshold flags (share of treatment flagged = hit rate; share of control flagged = false alarm)")
    for m, thr in (("M Beneish", -1.78), ("F Dechow", 1.0), ("C consistency", 0.0)):
        tp = [meth[m][p] for p in pos if meth[m][p] is not None]
        cn = [meth[m][p] for p in neg if meth[m][p] is not None]
        lines.append(f"- {m} > {thr}: treatment {sum(v > thr for v in tp)}/{len(tp)}, control {sum(v > thr for v in cn)}/{len(cn)}")
    txt = "\n".join(lines)
    open(f"{OUT}/evaluation_output.md", "w").write(txt + "\n")
    print(txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["features", "evaluate"])
    args = ap.parse_args()
    if args.action == "evaluate":
        return evaluate()
    key = json.load(open(KEY))
    filings = json.load(open(FILINGS))
    vals, notes, units = load_values()
    feats = features(vals, notes, key, filings)
    with open(f"{OUT}/financial_features.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(feats[0].keys()))
        w.writeheader()
        w.writerows(feats)
    rows = run_checks(vals, notes, units, key, filings)
    with open(f"{OUT}/consistency_checks.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    scores = consistency_scores(rows, load_review())
    with open(f"{OUT}/consistency_scores.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["pid", "C", "C_program", "unexplained_failures", "explained", "testable_weight"])
        w.writeheader()
        for pid in sorted(scores):
            w.writerow(dict(pid=pid, **scores[pid]))
    fails = [r for r in rows if r["status"] == "fail"]
    print(f"{len(feats)} feature rows; {len(rows)} checks; {sum(r['status'] != 'untestable' for r in rows)} testable; {len(fails)} program failures")


if __name__ == "__main__":
    main()

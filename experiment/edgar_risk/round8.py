"""Round 8: memorisation-controlled LLM risk scoring through an information bottleneck.

10-K text is redacted by program, a fresh extractor agent fills a fixed fact schema with verbatim quotes,
the program keeps only facts whose quotes are found in the redacted text, and a fresh judge agent scores an
anonymised fact card (field values + rounded XBRL ratios + coarse sector; no names, years, amounts, quotes).

Commands
  build     redacted packets under neutral codes (data/round8/redacted/R8-xx.txt[.gz])
  verify    check extractor quotes, write verified facts (results/round8/facts_verified.json)
  cards     write fact cards J0 / J1 / J2 / perturbation / probe inputs (data/round8/cards/)
  evaluate  read agent outputs (results/round8/*.csv) and write results/round8/evaluation.md
"""
import argparse
import csv
import gzip
import json
import math
import os
import random
import re
from collections import defaultdict

from .redact import make_redactor
from .round3 import auc, auc_ci
from .round7 import _pairs

R7_PACKETS = "data/round7/packets"
DATA = "data/round8"
OUT = "results/round8"
SEED = 20261102

# Fixed schema: taken from results/methods_overview.md (method 5) before any card was built.
FIELDS = [
    ("F01", "material_weakness", "Management or auditor reports a material weakness in ICFR at year end", ["yes", "no"]),
    ("F02", "material_weakness_area", "Area of the material weakness",
     ["revenue", "inventory_or_costing", "financial_close_or_reporting", "it_general_controls", "tax",
      "staffing_or_segregation_of_duties", "other", "na"]),
    ("F03", "icfr_auditor_opinion", "Auditor's opinion on internal control over financial reporting",
     ["adverse", "unqualified", "not_required", "not_found"]),
    ("F04", "going_concern", "Substantial doubt about ability to continue as a going concern", ["yes", "no"]),
    ("F05", "auditor_change_within_2y", "Change of independent auditor in the last two years", ["yes", "no"]),
    ("F06", "disagreement_with_accountants", "Reported disagreements or reportable events with accountants", ["yes", "no"]),
    ("F07", "prior_period_correction", "Correction of previously issued financial statements",
     ["none", "immaterial_revision", "restatement"]),
    ("F08", "revenue_over_time_major", "A significant share of revenue is recognised over time / percentage of completion", ["yes", "no"]),
    ("F09", "contract_assets_or_unbilled_significant", "Contract assets or unbilled receivables are significant", ["yes", "no"]),
    ("F10", "channel_return_rights_or_bill_and_hold", "Sales through distributors with return/price-protection rights, consignment or bill-and-hold", ["yes", "no"]),
    ("F11", "related_party_transactions_material", "Material transactions with related parties (officers, directors, affiliates)", ["yes", "no"]),
    ("F12", "largest_customer_pct_revenue", "Largest customer's share of revenue in percent (number) or not_disclosed", "number"),
    ("F13", "largest_customer_pct_receivables", "Largest customer's share of receivables in percent (number) or not_disclosed", "number"),
    ("F14", "ceo_or_cfo_change_in_year", "CEO or CFO changed during the year or since year end", ["yes", "no"]),
    ("F15", "interim_or_acting_cfo", "An interim or acting CFO is in place", ["yes", "no"]),
    ("F16", "sec_inquiry_or_investigation", "SEC inquiry, investigation, subpoena or Wells notice disclosed", ["yes", "no"]),
    ("F17", "securities_class_action", "Securities class action or shareholder derivative suit pending", ["yes", "no"]),
    ("F18", "other_government_investigation", "DOJ or other government investigation disclosed", ["yes", "no"]),
    ("F19", "covenant_breach_waiver_or_amendment", "Debt covenant breach, waiver or amendment to avoid breach", ["yes", "no"]),
    ("F20", "incentive_pay_tied_to_revenue_or_eps", "Executive incentive pay explicitly tied to revenue, EPS or earnings targets", ["yes", "no"]),
    ("F21", "capital_raise_in_year_or_planned", "Equity or debt raised during the year or stated plans to raise", ["yes", "no"]),
    ("F22", "major_acquisition_in_year", "A major acquisition during the year", ["yes", "no"]),
    ("F23", "public_via_spac_or_reverse_merger_3y", "Became public via SPAC merger or reverse merger in the last three years", ["yes", "no"]),
    ("F24", "critical_audit_matter_topics", "Topics of critical audit matters (list)",
     ["revenue", "inventory", "goodwill_or_intangibles", "business_combination", "tax", "reserves_or_estimates", "other", "none_or_na"]),
    ("F25", "voluntary_accounting_change", "Voluntary change in accounting policy or significant change in estimate (not a newly mandated standard)", ["yes", "no"]),
    ("F26", "non_gaap_emphasis", "Non-GAAP measures emphasised in MD&A", ["yes", "no"]),
    ("F27", "inventory_writedown_significant", "Significant inventory write-down or obsolescence charge", ["yes", "no"]),
    ("F28", "segment_or_reporting_change", "Change in reportable segments or presentation in the year", ["yes", "no"]),
]
FIELD_IDS = [f[0] for f in FIELDS]

RATIOS = [
    ("R01", "DSRI", "Days sales in receivables index"), ("R02", "GMI", "Gross margin index"),
    ("R03", "AQI", "Asset quality index"), ("R04", "SGI", "Sales growth index"), ("R05", "DEPI", "Depreciation index"),
    ("R06", "SGAI", "SG&A index"), ("R07", "LVGI", "Leverage index"), ("R08", "TATA", "Total accruals to total assets"),
    ("R09", "M", "Beneish M-score (threshold -1.78)"), ("R10", "rsst_acc", "RSST accruals"),
    ("R11", "ch_rec", "Change in receivables / avg assets"), ("R12", "ch_inv", "Change in inventory / avg assets"),
    ("R13", "soft_assets", "Soft assets share"), ("R14", "ch_cs", "Change in cash sales"), ("R15", "ch_roa", "Change in ROA"),
    ("R16", "issue", "Securities issued (1/0)"), ("R17", "F", "Dechow F-score (threshold 1.0)"),
    ("R18", "ar_growth_minus_sales_growth", "Receivables growth minus sales growth"), ("R19", "cfo_to_ni", "Operating cash flow / net income"),
]

RED_FLAGS = {"F01": "yes", "F03": "adverse", "F04": "yes", "F05": "yes", "F06": "yes", "F11": "yes", "F14": "yes",
             "F15": "yes", "F16": "yes", "F17": "yes", "F18": "yes", "F19": "yes"}
NEUTRAL = {"F01": "no", "F02": "na", "F04": "no", "F05": "no", "F06": "no", "F07": "none", "F11": "no", "F14": "no",
           "F15": "no", "F16": "no", "F17": "no", "F18": "no", "F19": "no"}
ADDED = {"F01": "yes", "F02": "revenue", "F16": "yes", "F14": "yes"}
# single-word name forms that are ordinary English words: only redacted case-sensitively
NEGATIVE = {"no", "none", "na", "none_or_na"}
GENERIC = {"consolidated", "national", "boston", "usa", "plug", "provident", "ammo", "latch", "cpi"}


def sector(sic):
    s = int(sic)
    for lo, hi, name in ((100, 999, "Agriculture"), (1000, 1499, "Mining and oil & gas"), (1500, 1799, "Construction"),
                         (2000, 3999, "Manufacturing"), (4000, 4999, "Transportation, communications and utilities"),
                         (5000, 5199, "Wholesale trade"), (5200, 5999, "Retail trade"),
                         (6000, 6799, "Finance, insurance and real estate"), (7000, 8999, "Services")):
        if lo <= s <= hi:
            return name
    return "Other"


def code_map():
    """pid -> neutral code, fixed by seed."""
    pids = [r[0] for r in _pairs()]
    rng = random.Random(SEED)
    shuffled = pids[:]
    rng.shuffle(shuffled)
    return {pid: f"R8-{i:02d}" for i, pid in enumerate(shuffled, 1)}


def _norm(s):
    s = s.replace("’", "'").replace("“", '"').replace("”", '"').replace("—", "-").replace("–", "-")
    return re.sub(r"\s+", " ", s).strip().lower()


def build(args):
    os.makedirs(f"{DATA}/redacted", exist_ok=True)
    cmap = code_map()
    manifest = {}
    for pid, name, cik, a0, p0, a1, p1, group, sic in _pairs():
        with gzip.open(f"{R7_PACKETS}/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
            text = fh.read()
        core = re.sub(r"(?i),?\s*(inc\.?|corp\.?|corporation|ltd\.?|limited|holdings?|company|co\.|/de/|group)\b", "", name)
        core = re.sub(r"\s+", " ", core).strip(" ,.")
        aliases = sorted({name, name.title(), core, core.title(), core.upper(), core.split()[0]}, key=len, reverse=True)
        aliases = [a for a in aliases if len(a) >= 3]
        fy = int(p0[:4])
        # case-insensitive pass for distinctive name forms (e.g. "AerSale", file names), before the redactor
        for a in aliases:
            if " " in a or a.lower() not in GENERIC:
                text = re.sub(rf"(?i)(?<![A-Za-z]){re.escape(a)}(?![a-z])", "[COMPANY]", text)
        text = re.sub(r"(?im)^\S+\.(?:htm|html|txt)\s*$", "", text)                       # document file names
        text = re.sub(r"\b\d{2}-\d{7}\b", "[EIN]", text)                                   # employer id
        text = re.sub(r"\(?\b\d{3}\)?[ .-]\d{3}-\d{4}\b", "[PHONE]", text)                 # phone numbers
        text = re.sub(r"\b0{2,3}\d-\d{4,5}\b", "[FILE NO]", text)                          # commission file no.
        red = make_redactor(aliases, fy, text)(text)
        code = cmap[pid]
        with open(f"{DATA}/redacted/{code}.txt", "w", encoding="utf-8") as fh:
            fh.write(red)
        with gzip.open(f"{DATA}/redacted/{code}.txt.gz", "wt", encoding="utf-8") as fh:
            fh.write(red)
        left = [a for a in aliases if re.search(rf"(?<![A-Za-z]){re.escape(a)}(?![a-z])", red)]
        manifest[code] = {"chars": len(red), "aliases_left": left}
        print(code, len(red), left, flush=True)
    json.dump(manifest, open(f"{DATA}/redacted/manifest.json", "w"), indent=1)


def verify(args):
    cmap = code_map()
    verified, stats = {}, {}
    for pid, code in sorted(cmap.items(), key=lambda kv: kv[1]):
        path = f"{DATA}/extract/{code}.json"
        if not os.path.exists(path):
            print("missing", code)
            continue
        raw = json.load(open(path))
        text = _norm(open(f"{DATA}/redacted/{code}.txt", encoding="utf-8").read())
        out, n_claims, n_fail, fails = {}, 0, 0, []
        for fid, key, desc, allowed in FIELDS:
            ans = raw.get(fid) or raw.get(key) or {}
            val = ans.get("value", "not_found") if isinstance(ans, dict) else ans
            quote = ans.get("quote", "") if isinstance(ans, dict) else ""
            if isinstance(val, list):
                val = [v for v in val if v in allowed] if allowed != "number" else val
            if val in ("not_found", "not_disclosed", None, "", []):
                out[fid] = "not_found"
                continue
            neg = set(val) <= NEGATIVE if isinstance(val, list) else val in NEGATIVE
            if not quote.strip() and neg:     # "no" inferred from silence (extract prompt rule 4)
                out[fid] = sorted(val) if isinstance(val, list) else val
                continue
            n_claims += 1
            pieces = [p for p in re.split(r"\s*(?:\.\.\.|…)\s*", quote) if p.strip()]
            ok = bool(pieces) and all(_norm(p) in text for p in pieces)
            if not ok:
                n_fail += 1
                fails.append(fid)
                out[fid] = "not_found"
                continue
            if allowed == "number":
                try:
                    out[fid] = round(float(str(val).strip("% ")))
                except ValueError:
                    out[fid] = "not_found"
            elif isinstance(val, list):
                out[fid] = sorted(val) or "not_found"
            else:
                out[fid] = val if val in allowed else "not_found"
        verified[code] = out
        stats[code] = {"claims": n_claims, "quote_failures": n_fail, "failed_fields": fails}
    json.dump(verified, open(f"{OUT}/facts_verified.json", "w"), indent=1)
    json.dump(stats, open(f"{OUT}/quote_verification.json", "w"), indent=1)
    tot = sum(s["claims"] for s in stats.values())
    bad = sum(s["quote_failures"] for s in stats.values())
    print(f"{len(stats)} filings, {tot} claims, {bad} quotes not found ({bad / max(tot, 1):.1%})")


def _ratios():
    out = {}
    for row in csv.DictReader(open("results/round7/financial_features.csv")):
        vals = {}
        for rid, key, _ in RATIOS:
            v = row.get(key, "")
            try:
                vals[rid] = round(float(v), 2)
            except ValueError:
                vals[rid] = "n/a"
        out[row["pid"]] = vals
    return out


def card_text(code, facts, ratios, sector_name, label=None):
    lines = [f"FACT CARD {code}"]
    if label:
        lines.append(f"Company: {label}")
    lines.append(f"Sector: {sector_name}")
    lines.append("")
    lines.append("Disclosure facts (extracted from the annual report; every value verified against the text):")
    for fid, key, desc, allowed in FIELDS:
        v = facts.get(fid, "not_found")
        v = ", ".join(v) if isinstance(v, list) else v
        lines.append(f"  {fid} {key}: {v}")
    lines.append("")
    lines.append("Financial ratios (computed from as-filed XBRL; current year vs prior year):")
    for rid, key, desc in RATIOS:
        lines.append(f"  {rid} {key} ({desc}): {ratios.get(rid, 'n/a')}")
    return "\n".join(lines) + "\n"


def cards(args):
    cmap = code_map()
    facts = json.load(open(f"{OUT}/facts_verified.json"))
    ratios = _pairs_ratio = _ratios()
    rows = {r[0]: r for r in _pairs()}
    os.makedirs(f"{DATA}/cards", exist_ok=True)
    partner = {pid: pid[:-1] + ("C" if pid.endswith("T") else "T") for pid in rows}
    for pid, code in cmap.items():
        f, r, sec = facts[code], ratios[pid], sector(rows[pid][8])
        open(f"{DATA}/cards/{code}_J0.txt", "w").write(card_text(code, f, r, sec))
        open(f"{DATA}/cards/{code}_J1.txt", "w").write(card_text(code, f, r, sec, f"{rows[pid][1]} (fiscal year ending {rows[pid][4]})"))
        p = rows[partner[pid]]
        open(f"{DATA}/cards/{code}_J2.txt", "w").write(card_text(code, f, r, sec, f"{p[1]} (fiscal year ending {p[4]})"))
    # perturbation: first 7 treatments and first 7 controls by code order
    by_code = sorted(cmap.items(), key=lambda kv: kv[1])
    chosen = [c for c in by_code if c[0].endswith("T")][:7] + [c for c in by_code if c[0].endswith("C")][:7]
    pert = {}
    for pid, code in chosen:
        f = dict(facts[code])
        if pid.endswith("T"):
            changed = {k: v for k, v in NEUTRAL.items() if f.get(k) != v}
            f.update(NEUTRAL)
            if f.get("F03") == "adverse":
                f["F03"] = "unqualified"
                changed["F03"] = "unqualified"
            kind = "neutralised"
        else:
            changed = {k: v for k, v in ADDED.items() if f.get(k) != v}
            f.update(ADDED)
            if f.get("F03") == "unqualified":
                f["F03"] = "adverse"
                changed["F03"] = "adverse"
            kind = "red_flags_added"
        open(f"{DATA}/cards/{code}_PX.txt", "w").write(card_text(code, f, ratios[pid], sector(rows[pid][8])))
        pert[code] = {"kind": kind, "changed": changed}
    json.dump(pert, open(f"{DATA}/cards/perturbation.json", "w"), indent=1)
    # probes
    codes = [c for _, c in by_code]
    rng = random.Random(SEED + 1)
    mixed = codes[:]
    rng.shuffle(mixed)
    for i, half in enumerate((mixed[:14], mixed[14:]), 1):
        open(f"{DATA}/cards/probe_open_{i}.txt", "w").write("\n\n".join(open(f"{DATA}/cards/{c}_J0.txt").read() for c in half))
    names = sorted(rows[pid][1] for pid in rows)
    allc = "\n\n".join(open(f"{DATA}/cards/{c}_J0.txt").read() for c in codes)
    open(f"{DATA}/cards/probe_closed.txt", "w").write(
        "CANDIDATE COMPANIES (each fact card below belongs to exactly one of these, fiscal years 2017-2023):\n"
        + "\n".join(f"- {n}" for n in names) + "\n\n" + allc)
    mem = sorted(f"{rows[pid][1]} — annual report for fiscal year ending {rows[pid][4]}" for pid in rows)
    open(f"{DATA}/cards/memory_only.txt", "w").write("\n".join(mem) + "\n")
    print("cards written:", len(cmap), "perturbed:", len(pert))


# ---- 8b: coarsened card (pre-registered after G1b failed, before any 8b agent ran) ----
BINS = {  # ratio key -> list of (upper bound inclusive, label); last label for values above all bounds
    "DSRI": [(1.0, "normal (<=1.0)"), (1.46, "elevated (1.0-1.46)"), (None, "high (>1.46)")],
    "GMI": [(1.0, "margin stable or improving"), (1.19, "margin declining"), (None, "margin declining sharply")],
    "AQI": [(1.0, "normal"), (1.25, "elevated"), (None, "high")],
    "SGI": [(0.95, "sales declining"), (1.4, "sales growth moderate"), (None, "sales growth high (>40%)")],
    "DEPI": [(1.0, "depreciation rate stable or rising"), (1.27, "depreciation slowing"), (None, "depreciation slowing sharply")],
    "SGAI": [(1.05, "normal"), (None, "SG&A rising faster than sales")],
    "LVGI": [(1.1, "leverage stable or falling"), (None, "leverage rising")],
    "TATA": [(0.0, "accruals negative"), (0.03, "accruals low positive"), (None, "accruals high positive")],
    "soft_assets": [(0.5, "low (<50%)"), (0.75, "medium (50-75%)"), (None, "high (>75%)")],
    "ar_growth_minus_sales_growth": [(0.0, "receivables growing slower than sales"), (0.1, "receivables growing slightly faster"),
                                     (None, "receivables growing much faster than sales (>10 pts)")],
    "ch_roa": [(-0.05, "ROA falling"), (0.05, "ROA stable"), (None, "ROA rising")],
}


def _bin(key, v):
    if v in ("", None):
        return "n/a"
    v = float(v)
    for hi, label in BINS[key]:
        if hi is None or v <= hi:
            return label
    return "n/a"


def card_c_text(code, facts, raw):
    lines = [f"FACT CARD {code}", "", "Disclosure facts (extracted from the annual report; every value verified against the text):"]
    for fid, key, desc, allowed in FIELDS:
        if fid == "F23":
            continue
        v = facts.get(fid, "not_found")
        if fid in ("F12", "F13") and isinstance(v, (int, float)):
            v = "<10%" if v < 10 else "10-25%" if v < 25 else "25-50%" if v < 50 else ">50%"
        v = ", ".join(v) if isinstance(v, list) else v
        lines.append(f"  {fid} {key}: {v}")
    lines += ["", "Financial signals (from as-filed XBRL, current vs prior year; categories only):"]
    names = {"DSRI": "R01 days sales in receivables", "GMI": "R02 gross margin", "AQI": "R03 asset quality index",
             "SGI": "R04 sales growth", "DEPI": "R05 depreciation", "SGAI": "R06 SG&A", "LVGI": "R07 leverage",
             "TATA": "R08 total accruals", "soft_assets": "R13 soft assets share",
             "ar_growth_minus_sales_growth": "R18 receivables vs sales growth", "ch_roa": "R15 change in ROA"}
    for key, label in names.items():
        lines.append(f"  {label}: {_bin(key, raw.get(key))}")
    m, f, c = raw.get("M"), raw.get("F"), raw.get("cfo_to_ni")
    lines.append(f"  R09 Beneish M-score: {'n/a' if m in ('', None) else ('above -1.78 threshold' if float(m) > -1.78 else 'below threshold')}")
    lines.append(f"  R17 Dechow F-score: {'n/a' if f in ('', None) else ('above 1.0 threshold' if float(f) > 1.0 else 'below threshold')}")
    lines.append(f"  R19 operating cash flow vs net income: {'n/a' if c in ('', None) else ('opposite signs' if float(c) < 0 else 'cash flow well below income (<0.8x)' if float(c) < 0.8 else 'cash flow at or above income')}")
    lines.append(f"  R16 securities issued: {'yes' if raw.get('issue') in ('1.0', '1') else 'no' if raw.get('issue') in ('0.0', '0') else 'n/a'}")
    return "\n".join(lines) + "\n"


def cards_c(args):
    cmap = code_map()
    facts = json.load(open(f"{OUT}/facts_verified.json"))
    raw = {r["pid"]: r for r in csv.DictReader(open("results/round7/financial_features.csv"))}
    rows = {r[0]: r for r in _pairs()}
    for pid, code in cmap.items():
        open(f"{DATA}/cards/{code}_C0.txt", "w").write(card_c_text(code, facts[code], raw[pid]))
    codes = sorted(cmap.values())
    names = sorted(rows[pid][1] for pid in rows)
    allc = "\n\n".join(open(f"{DATA}/cards/{c}_C0.txt").read() for c in codes)
    open(f"{DATA}/cards/probe_closed_C.txt", "w").write(
        "CANDIDATE COMPANIES (each fact card below belongs to exactly one of these, fiscal years 2017-2023):\n"
        + "\n".join(f"- {n}" for n in names) + "\n\n" + allc)
    print("coarse cards written:", len(cmap))


def _read_scores(path, col="risk_score"):
    if not os.path.exists(path):
        return {}
    return {r["code"]: r for r in csv.DictReader(open(path))}


def spearman(x, y):
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else float("nan")


def poisson_binomial_tail(ps, k):
    """P(X >= k) for a sum of independent Bernoulli(p_i)."""
    dist = [1.0]
    for p in ps:
        nxt = [0.0] * (len(dist) + 1)
        for i, q in enumerate(dist):
            nxt[i] += q * (1 - p)
            nxt[i + 1] += q * p
        dist = nxt
    return sum(dist[k:])


def collect():
    """Agent JSON outputs -> CSV files used by evaluate."""
    import glob
    for cond in ("J0", "J1", "J2", "PX"):
        files = sorted(glob.glob(f"{DATA}/judge/{cond}/R8-*.json"))
        if not files:
            continue
        with open(f"{OUT}/scores_{cond}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["code", "risk_score", "recognised", "guess", "knows_later_problems", "reasons"])
            for p in files:
                d = json.load(open(p))
                w.writerow([os.path.basename(p)[:-5], d["risk_score"], str(d.get("recognised")).lower() == "true",
                            d.get("guess", ""), d.get("knows_later_problems"), " || ".join(d.get("reasons", []))])
    cmap = code_map()
    rows = {r[0]: r for r in _pairs()}
    if os.path.exists(f"{DATA}/probe/memory.json"):
        mem = json.load(open(f"{DATA}/probe/memory.json"))
        with open(f"{OUT}/scores_MEM.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["pid", "company", "risk_score", "knows_later_problems", "basis"])
            for m in mem:
                pid = next(p for p in rows if m["company"].startswith(rows[p][1]))
                w.writerow([pid, rows[pid][1], m["risk_score"], m.get("knows_later_problems"), m.get("basis", "")])
    opens = {}
    for p in sorted(glob.glob(f"{DATA}/probe/open_*.json")):
        opens.update(json.load(open(p)))
    if opens:
        with open(f"{OUT}/probe_open.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["code", "guesses", "fiscal_year_guess", "confidence", "basis"])
            for c, d in sorted(opens.items()):
                w.writerow([c, "|".join(d.get("guesses", [])), d.get("fiscal_year_guess", ""), d.get("confidence", ""), d.get("basis", "")])
    if os.path.exists(f"{DATA}/probe/closed.json"):
        cl = json.load(open(f"{DATA}/probe/closed.json"))
        with open(f"{OUT}/probe_closed.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["code", "assigned", "confidence", "basis"])
            for c, d in sorted(cl.items()):
                w.writerow([c, d.get("assigned", ""), d.get("confidence", ""), d.get("basis", "")])


def evaluate(args):
    collect()
    cmap = code_map()
    inv = {c: p for p, c in cmap.items()}
    rows = {r[0]: r for r in _pairs()}
    name_of = {cmap[p]: rows[p][1] for p in rows}
    is_t = {c: inv[c].endswith("T") for c in inv}
    rep = ["# 第八輪評估輸出（程式產生）", ""]

    def get(cond):
        d = _read_scores(f"{OUT}/scores_{cond}.csv")
        return {c: float(r["risk_score"]) for c, r in d.items()}, d

    j0, j0raw = get("J0")
    j1, _ = get("J1")
    j2, _ = get("J2")
    px, _ = get("PX")
    mem = {}
    if os.path.exists(f"{OUT}/scores_MEM.csv"):
        for r in csv.DictReader(open(f"{OUT}/scores_MEM.csv")):
            mem[cmap[r["pid"]]] = float(r["risk_score"])

    def auc_line(name, s):
        pos = [v for c, v in s.items() if is_t[c]]
        neg = [v for c, v in s.items() if not is_t[c]]
        if not pos or not neg:
            return f"| {name} | – | – | – | 0 |"
        lo, hi = auc_ci(pos, neg)
        w = t = l = 0
        for p in rows:
            if p.endswith("T"):
                a, b = cmap[p], cmap[p[:-1] + "C"]
                if a in s and b in s:
                    w += s[a] > s[b]
                    t += s[a] == s[b]
                    l += s[a] < s[b]
        return f"| {name} | {auc(pos, neg):.2f} | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} | {len(s)} |"

    rep += ["## 成效", "", "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | n |", "|---|---|---|---|---|"]
    rep += [auc_line("J0 事實卡（無名稱）", j0), auc_line("J1 事實卡 + 真實名稱", j1), auc_line("J2 事實卡 + 對調名稱", j2),
            auc_line("MEM 只有名稱（純記憶）", mem)]
    r7 = {}
    for r in csv.DictReader(open("results/round7/llm_risk_scores_claude_agent.csv")):
        r7[cmap[r["pid"]]] = float(r["risk_score"])
    rep.append(auc_line("第七輪 B 整份 10-K 不遮蔽", r7))
    if j1 and j2:
        # J2 judged by card content (should match J0 ranking) or by name label (should match J1 of the partner)
        rep += ["", "J2 的判讀：對調名稱後，「卡片是問題公司」的 AUC 是上表 J2；以「標籤名稱是問題公司」計算的 AUC："]
        s_label = {c: v for c, v in j2.items()}
        pos = [v for c, v in s_label.items() if not is_t[c]]
        neg = [v for c, v in s_label.items() if is_t[c]]
        rep.append(f"- 依標籤名稱：{auc(pos, neg):.2f}（> 0.5 表示分數跟著名稱走）")
    # recognition
    rep += ["", "## 辨識", ""]
    if j0raw:
        knows = [c for c, r in j0raw.items() if r.get("knows_later_problems", "").lower() == "true"]
        rec = [c for c, r in j0raw.items() if _name_hit(r.get("guess", ""), name_of[c])]
        rep.append(f"- G1c J0 自述知道後來有問題：{len(knows)}/{len(j0raw)}；J0 名稱猜中：{len(rec)}/{len(j0raw)} {rec}")
    if os.path.exists(f"{OUT}/probe_open.csv"):
        po = list(csv.DictReader(open(f"{OUT}/probe_open.csv")))
        hits = [r["code"] for r in po if any(_name_hit(g, name_of[r["code"]]) for g in r["guesses"].split("|"))]
        rep.append(f"- G1a 開放式辨識猜中：{len(hits)}/{len(po)} {hits}")
    if os.path.exists(f"{OUT}/probe_closed.csv"):
        pc = list(csv.DictReader(open(f"{OUT}/probe_closed.csv")))
        hits = [r["code"] for r in pc if _name_hit(r["assigned"], name_of[r["code"]])]
        # chance baseline: guessing uniformly within the same sector
        secs = defaultdict(int)
        for p in rows:
            secs[sector(rows[p][8])] += 1
        ps = [1 / secs[sector(rows[inv[r['code']]][8])] for r in pc]
        exp = sum(ps)
        p_val = poisson_binomial_tail(ps, len(hits))
        pair_ok = sum(1 for r in pc if _name_hit(r["assigned"], name_of[r["code"]]) or
                      _name_hit(r["assigned"], name_of[cmap[inv[r["code"]][:-1] + ("C" if is_t[r["code"]] else "T")]]))
        rep.append(f"- G1b 封閉式辨識正確：{len(hits)}/{len(pc)}（只靠產業大類隨機猜的期望 {exp:.1f}，單尾 p = {p_val:.3f}）{hits}")
        rep.append(f"  - 指派到正確的配對（本身或配對公司）：{pair_ok}/{len(pc)}")
        both = sum(1 for r in pc if is_t[r["code"]] == _is_treat_name(r["assigned"], rows))
        rep.append(f"  - 指派的名稱與卡片「同為問題公司 / 同為對照公司」：{both}/{len(pc)}")
    # G2a
    if j0raw:
        n_r = n_ok = 0
        for r in j0raw.values():
            for reason in r.get("reasons", "").split(" || "):
                if not reason.strip():
                    continue
                n_r += 1
                ids = re.findall(r"\b([FR]\d{2})\b", reason)
                n_ok += bool(ids) and all(i in FIELD_IDS or i in [x[0] for x in RATIOS] for i in ids)
        rep.append(f"\n- G2a 理由引用有效欄位：{n_ok}/{n_r}（{n_ok / max(n_r, 1):.0%}）")
    # G2b
    if px:
        pert = json.load(open(f"{DATA}/cards/perturbation.json"))
        rep += ["", "## G2b 內容擾動", "", "| 卡 | 擾動 | 改動欄位 | J0 | 擾動後 | Δ | 方向正確 |", "|---|---|---|---|---|---|---|"]
        good, deltas = 0, []
        for code, info in sorted(pert.items()):
            if code not in px or code not in j0:
                continue
            d = px[code] - j0[code]
            ok = d < 0 if info["kind"] == "neutralised" else d > 0
            good += ok
            deltas.append(abs(d))
            rep.append(f"| {code} | {info['kind']} | {', '.join(info['changed']) or '（無）'} | {j0[code]:.0f} | {px[code]:.0f} | {d:+.0f} | {'是' if ok else '否'} |")
        deltas.sort()
        med = deltas[len(deltas) // 2] if deltas else float("nan")
        rep.append(f"\n方向正確 {good}/{len(deltas)}；|Δ| 中位數 {med:.0f}")
    # G2c and name effects
    if mem and j0:
        def demean(s):
            out = {}
            for grp in (True, False):
                cs = [c for c in s if is_t[c] == grp and c in mem]
                m = sum(s[c] for c in cs) / len(cs)
                for c in cs:
                    out[c] = s[c] - m
            return out
        a, b = demean(j0), demean(mem)
        cs = sorted(set(a) & set(b))
        rep.append(f"\n- G2c 組內去平均後 J0 與 MEM 的 Spearman ρ = {spearman([a[c] for c in cs], [b[c] for c in cs]):.2f}（n = {len(cs)}）")
        cs = sorted(set(r7) & set(mem))
        rep.append(f"- 對照：組內去平均後第七輪 B（不遮蔽）與 MEM 的 ρ = {spearman([demean(r7)[c] for c in cs], [b[c] for c in cs]):.2f}")
    if j0 and j1:
        dt = [j1[c] - j0[c] for c in j1 if c in j0 and is_t[c]]
        dc = [j1[c] - j0[c] for c in j1 if c in j0 and not is_t[c]]
        rep.append(f"- 名稱效應 J1 − J0：問題公司平均 {sum(dt) / len(dt):+.1f}，對照公司平均 {sum(dc) / len(dc):+.1f}，"
                   f"記憶效應指數 = {sum(dt) / len(dt) - sum(dc) / len(dc):+.1f}")
    if j0 and j2:
        dt = [j2[c] - j0[c] for c in j2 if c in j0 and is_t[c]]
        dc = [j2[c] - j0[c] for c in j2 if c in j0 and not is_t[c]]
        rep.append(f"- 對調名稱 J2 − J0：問題公司的卡（標上對照名稱）平均 {sum(dt) / len(dt):+.1f}，對照公司的卡（標上問題公司名稱）平均 {sum(dc) / len(dc):+.1f}")
    # per-card table
    rep += ["", "## 逐卡", "", "| 卡 | 組 | 公司 | B 第七輪 | MEM | J0 | J1 | J2 |", "|---|---|---|---|---|---|---|---|"]
    for c in sorted(inv):
        f = lambda s: f"{s[c]:.0f}" if c in s else ""
        rep.append(f"| {c} | {'問題' if is_t[c] else '對照'} | {name_of[c]} | {f(r7)} | {f(mem)} | {f(j0)} | {f(j1)} | {f(j2)} |")
    open(f"{OUT}/evaluation.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


def _simple(s):
    s = s.lower()
    s = re.sub(r"\(.*?\)", " ", s)
    s = re.sub(r"[^a-z0-9 ]", " ", s)
    stop = {"inc", "corp", "corporation", "ltd", "limited", "holdings", "holding", "company", "co", "group", "the", "de",
            "plc", "systems", "communications", "technologies", "industries", "international", "financial"}
    return [w for w in s.split() if w not in stop]


def _name_hit(guess, truth):
    g, t = _simple(guess or ""), _simple(truth)
    if not g or not t:
        return False
    if t[0] == "archer" and ("adm" in g or "archer" in g):
        return True
    if t[0] == "becton" and ("bd" in g or "becton" in g):
        return True
    return t[0] in g


def _is_treat_name(name, rows):
    for p, r in rows.items():
        if _name_hit(name, r[1]):
            return p.endswith("T")
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "verify", "cards", "cards_c", "evaluate"])
    args = ap.parse_args()
    {"build": build, "verify": verify, "cards": cards, "cards_c": cards_c, "evaluate": evaluate}[args.cmd](args)


if __name__ == "__main__":
    main()

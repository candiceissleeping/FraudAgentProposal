"""Build the matched fraud/control firm-year sample for experiment 1.

Inputs: data/aaer_firm_year.csv (labels.py), data/edgar_index/ (index_corpus.py),
data/sic.json (sic.py). Outputs:
  config/exp1_sample.json   - matched pairs, with the pilot subset flagged
  results/exp1_attrition.md - how many firm-years each pre-registered rule removed

Rules (pre-registered in docs/exp1_yoy_diff_design.md):
  - a 10-K is usable if Item 7 (MD&A) and the financial statements each have
    >= MIN_CHARS characters; financial statements = Item 8, or Items 14+15 for
    older 10-Ks that put them there
  - fraud firm-year: first misstated year t of an AAER episode, with usable 10-Ks for t and t-1
  - control: never in any AAER, usable 10-Ks for t and t-1, same fiscal year t and
    same 2-digit SIC, closest log length of the text the LLM will read; each control firm used once

  python -m experiment.yoy.build_sample
"""
import argparse
import collections
import json
import math
import os
import random

from experiment.yoy import index_corpus, labels, sic as sic_mod

MIN_CHARS = 2000
LLM_SECTIONS = ("1A", "3", "7", "7A", "9", "9A")  # plus financial statements, see fs_chars
PILOT_PAIRS = 30
PILOT_SEED = 20261017


def fs_chars(r):
    return r["len_8"] if r["len_8"] >= MIN_CHARS else r["len_14"] + r["len_15"]


def usable(r):
    return r is not None and r["len_7"] >= MIN_CHARS and fs_chars(r) >= MIN_CHARS


def key_chars(r):
    """Characters of the sections the LLM reads; matching on it also equalises input length."""
    return sum(r[f"len_{s}"] for s in LLM_SECTIONS) + fs_chars(r)


def filing_check(idx, cik, t):
    """None if both years are usable, else the attrition reason."""
    for year, tag in ((t, "t"), (t - 1, "t-1")):
        r = idx.get((cik, year))
        if r is None:
            return f"no_10k_{tag}"
        if not usable(r):
            return f"empty_10k_{tag}"
    return None


def eligible_frauds(candidates, idx):
    kept, dropped = [], []
    for c in candidates:
        reason = filing_check(idx, c["cik"], c["t"])
        if reason:
            dropped.append(dict(c, reason=reason))
        else:
            kept.append(dict(c, key_chars=key_chars(idx[(c["cik"], c["t"])])))
    return kept, dropped


def control_pool(idx, years, exclude):
    """{t: [(cik, key_chars)]} of non-AAER firms with usable 10-Ks for t and t-1."""
    pool = collections.defaultdict(list)
    for (cik, year), r in idx.items():
        if year in years and cik not in exclude and filing_check(idx, cik, year) is None:
            pool[year].append((cik, key_chars(r)))
    for year in pool:
        pool[year].sort()
    return pool


def sic2(sic, cik):
    return (sic.get(cik, {}).get("sic") or "")[:2]


def match(frauds, pool, sic):
    pairs, dropped, used = [], [], set()
    for f in sorted(frauds, key=lambda f: (f["t"], f["cik"])):
        ind = sic2(sic, f["cik"])
        if not ind:
            dropped.append(dict(f, reason="no_sic"))
            continue
        options = [(abs(math.log(k) - math.log(f["key_chars"])), cik, k) for cik, k in pool.get(f["t"], [])
                   if cik not in used and sic2(sic, cik) == ind]
        if not options:
            dropped.append(dict(f, reason="no_control"))
            continue
        _, cik, k = min(options)
        used.add(cik)
        pairs.append({"t": f["t"], "sic2": ind,
                      "fraud": {"cik": f["cik"], "p_aaer": f["p_aaer"], "misstated_years": f["misstated_years"],
                                "key_chars": f["key_chars"]},
                      "control": {"cik": cik, "key_chars": k}})
    for i, p in enumerate(pairs, 1):
        p["pair_id"] = f"P{i:03d}"
    pilot = set(random.Random(PILOT_SEED).sample([p["pair_id"] for p in pairs], min(PILOT_PAIRS, len(pairs))))
    for p in pairs:
        p["pilot"] = p["pair_id"] in pilot
    return pairs, dropped


def _load(label_path, index_dir):
    rows = labels.load_rows(labels.download(label_path))
    candidates, label_dropped = labels.treatment_candidates(rows)
    idx = index_corpus.load_index(index_dir)
    frauds, filing_dropped = eligible_frauds(candidates, idx)
    return rows, label_dropped, idx, frauds, filing_dropped


def ciks_needing_sic(label_path=labels.DEFAULT_PATH, index_dir=index_corpus.DEFAULT_DIR):
    rows, _, idx, frauds, _ = _load(label_path, index_dir)
    pool = control_pool(idx, {f["t"] for f in frauds}, labels.fraud_ciks(rows))
    return {f["cik"] for f in frauds} | {cik for year in pool.values() for cik, _ in year}


def attrition_report(rows, label_dropped, filing_dropped, match_dropped, pairs, idx):
    years = sorted({y for _, y in idx})
    lines = ["# 實驗一樣本流失表（自動產生，勿手改）", "",
             f"- AAER 標籤：Bao et al. (2020)，{len(rows)} 個不實陳述 firm-years，"
             f"{len(labels.episodes(rows))} 個 AAER 事件",
             f"- EDGAR-CORPUS 索引：{len(idx):,} 份 10-K，會計年度 {years[0]}–{years[-1]}" if years else "",
             f"- 可用 10-K 門檻：Item 7 與財報（Item 8，或舊式 Item 14+15）各 ≥ {MIN_CHARS:,} 字元", "",
             "| 步驟 | 剔除原因 | 數量 |", "|---|---|---|"]
    for step, dropped in (("標籤", label_dropped), ("10-K 可用性", filing_dropped), ("配對", match_dropped)):
        for reason, n in collections.Counter(d["reason"] for d in dropped).most_common():
            lines.append(f"| {step} | `{reason}` | {n} |")
    lines += ["", f"**最終配對：{len(pairs)} 組**（試點 {sum(p['pilot'] for p in pairs)} 組，seed {PILOT_SEED}）", "",
              "| 會計年度 t | 配對數 |", "|---|---|"]
    for t, n in sorted(collections.Counter(p["t"] for p in pairs).items()):
        lines.append(f"| {t} | {n} |")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--labels", default=labels.DEFAULT_PATH)
    ap.add_argument("--index", default=index_corpus.DEFAULT_DIR)
    ap.add_argument("--sic", default=sic_mod.DEFAULT_PATH)
    ap.add_argument("--out", default="config/exp1_sample.json")
    ap.add_argument("--report", default="results/exp1_attrition.md")
    args = ap.parse_args()

    rows, label_dropped, idx, frauds, filing_dropped = _load(args.labels, args.index)
    sic = sic_mod.load(args.sic)
    if not sic:
        print(f"{len(frauds)} fraud firm-years have usable t and t-1 10-Ks; filing drops: "
              f"{dict(collections.Counter(d['reason'] for d in filing_dropped))}")
        raise SystemExit(f"No SIC codes in {args.sic}: run `python -m experiment.yoy.sic` first")
    pool = control_pool(idx, {f["t"] for f in frauds}, labels.fraud_ciks(rows))
    pairs, match_dropped = match(frauds, pool, sic)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump({"_comment": "Generated by experiment.yoy.build_sample; see docs/exp1_yoy_diff_design.md",
                   "pairs": pairs}, f, indent=1)
    os.makedirs(os.path.dirname(args.report) or ".", exist_ok=True)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write(attrition_report(rows, label_dropped, filing_dropped, match_dropped, pairs, idx))
    print(f"{len(pairs)} pairs -> {args.out}; attrition -> {args.report}")


if __name__ == "__main__":
    main()

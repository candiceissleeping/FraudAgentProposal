"""AAER fraud labels from Bao et al. (2020, JAR), github.com/JarFraud/FraudDetection.

AAER_firm_year.csv has one row per misstated firm-year:
  P_AAER (AAER id), CIK, YEARA (fiscal year), UNDERSTATEMENT (1 = earnings understated).
An episode is one (CIK, P_AAER); its first misstated year is the treatment year t,
so t-1 is still a clean year and the year-over-year diff spans the switch.

  python -m experiment.yoy.labels      # download to data/aaer_firm_year.csv and summarise
"""
import argparse
import collections
import csv
import os

import requests

# Pinned to the upstream commit the design was checked against (2022-08-10).
URL = ("https://raw.githubusercontent.com/JarFraud/FraudDetection/"
       "2d10bc6c7ce18f5dea051a90d823546907abaa84/AAER_firm_year.csv")
DEFAULT_PATH = "data/aaer_firm_year.csv"

# EDGAR-CORPUS covers fiscal years 1993-2020, and t-1 must be in it too.
FIRST_T, LAST_T = 1994, 2020


def download(path=DEFAULT_PATH):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        r = requests.get(URL, timeout=60)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
    return path


def load_rows(path=DEFAULT_PATH):
    with open(path, newline="", encoding="utf-8") as f:
        return [{"p_aaer": r["P_AAER"].strip(), "cik": r["CIK"].strip().lstrip("0"),
                 "year": int(r["YEARA"]), "understatement": r["UNDERSTATEMENT"].strip() == "1"}
                for r in csv.DictReader(f)]


def fraud_ciks(rows):
    """Every CIK that appears in any AAER; never eligible as a control."""
    return {r["cik"] for r in rows}


def episodes(rows):
    eps = collections.defaultdict(list)
    for r in rows:
        eps[(r["cik"], r["p_aaer"])].append(r)
    return [{"cik": cik, "p_aaer": p, "years": sorted(r["year"] for r in rs),
             "understatement": any(r["understatement"] for r in rs)}
            for (cik, p), rs in sorted(eps.items())]


def treatment_candidates(rows, first_t=FIRST_T, last_t=LAST_T):
    """Return (kept, dropped). kept: one dict per episode with t = first misstated year.

    Dropped reasons (pre-registered):
      understatement       - earnings were understated, not the fraud type studied
      outside_corpus_years - t or t-1 outside EDGAR-CORPUS
      prior_year_misstated - t-1 is misstated under another AAER of the same firm,
                             so there is no clean prior year to diff against
      duplicate_t          - same firm and t already kept from another AAER
    """
    misstated = collections.defaultdict(set)
    for r in rows:
        misstated[r["cik"]].add(r["year"])
    kept, dropped, seen = [], [], set()
    for ep in episodes(rows):
        t = ep["years"][0]
        cand = {"cik": ep["cik"], "p_aaer": ep["p_aaer"], "t": t, "misstated_years": ep["years"]}
        if ep["understatement"]:
            reason = "understatement"
        elif not first_t <= t <= last_t:
            reason = "outside_corpus_years"
        elif t - 1 in misstated[ep["cik"]]:
            reason = "prior_year_misstated"
        elif (ep["cik"], t) in seen:
            reason = "duplicate_t"
        else:
            seen.add((ep["cik"], t))
            kept.append(cand)
            continue
        dropped.append(dict(cand, reason=reason))
    return kept, dropped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", default=DEFAULT_PATH)
    args = ap.parse_args()
    rows = load_rows(download(args.path))
    kept, dropped = treatment_candidates(rows)
    print(f"{len(rows)} misstated firm-years, {len(episodes(rows))} AAER episodes, {len(fraud_ciks(rows))} firms")
    print(f"treatment candidates (first misstated year t in {FIRST_T}-{LAST_T}): {len(kept)}")
    for reason, n in collections.Counter(d["reason"] for d in dropped).most_common():
        print(f"  dropped {reason}: {n}")


if __name__ == "__main__":
    main()

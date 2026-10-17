"""Index every EDGAR-CORPUS 10-K by (cik, year) with per-section character counts.

Streams <year>/{train,validate,test}.jsonl from Hugging Face (~1 GB per year) and keeps
only lengths, so the sample builder can check which firms have usable 10-Ks for both
t and t-1 without storing any text. One file per year: data/edgar_index/<year>.csv,
so an interrupted run resumes where it stopped.

  python -m experiment.yoy.index_corpus                 # all years 1993-2020
  python -m experiment.yoy.index_corpus --years 2000 2001
"""
import argparse
import csv
import json
import os

from experiment.edgar_risk.fetch import BASE, SPLITS, _cik, _lines

YEARS = range(1993, 2021)
SECTIONS = ("1", "1A", "1B", "2", "3", "4", "5", "6", "7", "7A", "8", "9", "9A", "9B",
            "10", "11", "12", "13", "14", "15")
FIELDS = ["cik", "year", "split", "filename"] + [f"len_{s}" for s in SECTIONS]
DEFAULT_DIR = "data/edgar_index"


def index_row(row, split):
    out = {"cik": _cik(row.get("cik", "")), "year": row.get("year"), "split": split,
           "filename": row.get("filename", "")}
    for s in SECTIONS:
        out[f"len_{s}"] = len(row.get(f"section_{s}") or "")
    return out


def index_year(year, out_dir, lines_for=None):
    """Write <out_dir>/<year>.csv; lines_for(url) is injectable for tests."""
    lines_for = lines_for or _lines
    path = os.path.join(out_dir, f"{year}.csv")
    tmp = path + ".part"
    n = 0
    with open(tmp, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, FIELDS)
        w.writeheader()
        for split in SPLITS:
            for line in lines_for(f"{BASE}/{year}/{split}.jsonl"):
                if line:
                    w.writerow(index_row(json.loads(line), split))
                    n += 1
    os.replace(tmp, path)
    return n


def load_index(out_dir=DEFAULT_DIR):
    """{(cik, year): row}; if a firm has several rows in a year, keep the longest filing."""
    idx = {}
    for name in sorted(os.listdir(out_dir)):
        if not name.endswith(".csv"):
            continue
        with open(os.path.join(out_dir, name), newline="", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                for k in FIELDS[4:]:
                    r[k] = int(r[k])
                r["year"] = int(r["year"])
                key = (r["cik"], r["year"])
                if key not in idx or total_chars(r) > total_chars(idx[key]):
                    idx[key] = r
    return idx


def total_chars(r):
    return sum(r[f"len_{s}"] for s in SECTIONS)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=DEFAULT_DIR)
    ap.add_argument("--years", type=int, nargs="*", default=list(YEARS))
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for year in args.years:
        if os.path.exists(os.path.join(args.out, f"{year}.csv")):
            print(f"[{year}] already indexed", flush=True)
            continue
        print(f"[{year}] indexed {index_year(year, args.out):,} filings", flush=True)


if __name__ == "__main__":
    main()

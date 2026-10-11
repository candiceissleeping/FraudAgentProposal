"""Fetch 10-K filings for selected companies from EDGAR-CORPUS (eloukas/edgar-corpus).

Sources, tried in order:
  1. --local-jsonl: a manually downloaded EDGAR-CORPUS jsonl file (offline mode).
  2. Hugging Face datasets-server /filter API (no large download).
  3. Parquet shards of the year config, filtered by CIK (needs pyarrow), used when
     the /filter API truncates long sections.

Each filing is saved to data/<cik>_<year>.json with all section_* fields.
"""
import argparse
import json
import os
import sys
import tempfile

import requests

DATASET = "eloukas/edgar-corpus"
API = "https://datasets-server.huggingface.co"
TIMEOUT = 120


def _cik_variants(cik):
    bare = str(cik).lstrip("0")
    return [bare, bare.zfill(10)]


def _matches(row, cik):
    return str(row.get("cik", "")).lstrip("0") == str(cik).lstrip("0")


def from_local_jsonl(path, cik, year):
    with open(path, encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            if _matches(row, cik) and int(row.get("year", year)) == year:
                return row
    return None


def from_filter_api(cik, year):
    """Return (row, truncated_cells) or (None, None)."""
    for v in _cik_variants(cik):
        params = {
            "dataset": DATASET,
            "config": f"year_{year}",
            "split": "train",
            "where": f"\"cik\"='{v}'",
            "length": 10,
        }
        r = requests.get(f"{API}/filter", params=params, timeout=TIMEOUT)
        r.raise_for_status()
        rows = r.json().get("rows", [])
        if rows:
            return rows[0]["row"], rows[0].get("truncated_cells", [])
    return None, None


def from_parquet(cik, year):
    try:
        import pyarrow.parquet as pq
    except ImportError:
        sys.exit("pyarrow is required for the parquet fallback: pip install pyarrow")
    r = requests.get(f"{API}/parquet", params={"dataset": DATASET, "config": f"year_{year}"},
                     timeout=TIMEOUT)
    r.raise_for_status()
    for f in r.json().get("parquet_files", []):
        with tempfile.NamedTemporaryFile(suffix=".parquet") as tmp:
            with requests.get(f["url"], stream=True, timeout=TIMEOUT) as resp:
                resp.raise_for_status()
                for chunk in resp.iter_content(1 << 20):
                    tmp.write(chunk)
            tmp.flush()
            table = pq.read_table(tmp.name)
            for row in table.to_pylist():
                if _matches(row, cik):
                    return row
    return None


def fetch(company, local_jsonl=None):
    cik, year = company["cik"], company["year"]
    if local_jsonl:
        return from_local_jsonl(local_jsonl, cik, year)
    row, truncated = from_filter_api(cik, year)
    if row is not None and not truncated:
        return row
    if row is not None:
        print(f"  sections truncated by API ({', '.join(truncated)}); using parquet shards")
    return from_parquet(cik, year)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="config/companies.json")
    ap.add_argument("--out", default="data")
    ap.add_argument("--local-jsonl", help="offline EDGAR-CORPUS jsonl file")
    args = ap.parse_args()

    companies = json.load(open(args.config, encoding="utf-8"))["companies"]
    os.makedirs(args.out, exist_ok=True)
    missing = []
    for c in companies:
        print(f"{c['name']} (CIK {c['cik']}, {c['year']})")
        row = fetch(c, args.local_jsonl)
        if row is None:
            print("  NOT FOUND - check CIK / year in config")
            missing.append(c["name"])
            continue
        print(f"  matched filename: {row.get('filename')}")
        row["_company"] = c
        path = os.path.join(args.out, f"{c['cik']}_{c['year']}.json")
        json.dump(row, open(path, "w", encoding="utf-8"), ensure_ascii=False)
    if missing:
        print(f"\nMissing: {missing}")
        sys.exit(1)


if __name__ == "__main__":
    main()

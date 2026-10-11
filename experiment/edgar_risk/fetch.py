"""Fetch 10-K filings for selected companies from EDGAR-CORPUS (eloukas/edgar-corpus).

The dataset is stored as raw jsonl per year (<year>/{train,validate,test}.jsonl,
~1.2 GB per year) and is not supported by the Hugging Face dataset viewer API,
so each year's files are streamed line by line and only rows whose CIK matches
a target company are kept. Nothing else is written to disk.

Offline mode: --local-jsonl reads an already downloaded jsonl file instead.

Each filing is saved to data/<cik>_<year>.json with all section_* fields.
"""
import argparse
import collections
import json
import os
import sys

import requests

BASE = "https://huggingface.co/datasets/eloukas/edgar-corpus/resolve/main"
SPLITS = ("train", "validate", "test")
TIMEOUT = 120


def _cik(value):
    return str(value).strip().lstrip("0")


def _lines(url):
    with requests.get(url, stream=True, timeout=TIMEOUT) as r:
        r.raise_for_status()
        yield from r.iter_lines()


def scan(lines, wanted):
    """Yield rows whose CIK is in wanted (a set of bare CIKs), stopping once all are found."""
    remaining = set(wanted)
    for line in lines:
        if not line:
            continue
        # cheap substring pre-filter before full JSON parse of a multi-MB row
        if isinstance(line, str):
            line = line.encode("utf-8")
        if not any(c.encode() in line for c in remaining):
            continue
        row = json.loads(line)
        cik = _cik(row.get("cik", ""))
        if cik in remaining:
            remaining.discard(cik)
            yield row
            if not remaining:
                return


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="config/companies.json")
    ap.add_argument("--out", default="data")
    ap.add_argument("--local-jsonl", help="offline EDGAR-CORPUS jsonl file")
    args = ap.parse_args()

    companies = json.load(open(args.config, encoding="utf-8"))["companies"]
    os.makedirs(args.out, exist_ok=True)
    by_year = collections.defaultdict(dict)
    for c in companies:
        by_year[c["year"]][_cik(c["cik"])] = c

    found = set()
    for year, targets in sorted(by_year.items()):
        todo = {k: v for k, v in targets.items()
                if not os.path.exists(os.path.join(args.out, f"{v['cik']}_{year}.json"))}
        found |= set(targets) - set(todo)
        sources = [args.local_jsonl] if args.local_jsonl else [f"{BASE}/{year}/{s}.jsonl" for s in SPLITS]
        for src in sources:
            if not todo:
                break
            print(f"[{year}] scanning {src} for {sorted(c['name'] for c in todo.values())}", flush=True)
            lines = open(src, "rb") if args.local_jsonl else _lines(src)
            for row in scan(lines, todo):
                c = todo.pop(_cik(row["cik"]))
                print(f"  {c['name']}: {row.get('filename')}", flush=True)
                row["_company"] = c
                with open(os.path.join(args.out, f"{c['cik']}_{year}.json"), "w", encoding="utf-8") as f:
                    json.dump(row, f, ensure_ascii=False)
                found.add(_cik(c["cik"]))

    missing = [c["name"] for c in companies if _cik(c["cik"]) not in found]
    if missing:
        print(f"\nNot found (check CIK / year in config): {missing}")
        sys.exit(1)


if __name__ == "__main__":
    main()

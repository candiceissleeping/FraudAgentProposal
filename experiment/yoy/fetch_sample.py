"""Fetch the t and t-1 10-Ks of every firm in config/exp1_sample.json from EDGAR-CORPUS.

Each year's jsonl is streamed once; only target rows are kept (the longest one if a firm
has several, matching index_corpus.load_index). Saved as data/exp1/filings/<cik>_<year>.json.

  python -m experiment.yoy.fetch_sample [--pilot] [--workers 4]
"""
import argparse
import collections
import concurrent.futures
import json
import os
import re

import requests

from experiment.edgar_risk.fetch import BASE, SPLITS, _cik, _lines

DEFAULT_DIR = "data/exp1/filings"
_CIK = re.compile(rb'"cik":\s*"?(\d+)')


def targets(pairs):
    by_year = collections.defaultdict(set)
    for p in pairs:
        for role in ("fraud", "control"):
            for year in (p["t"], p["t"] - 1):
                by_year[year].add(p[role]["cik"])
    return by_year


def path_for(out_dir, cik, year):
    return os.path.join(out_dir, f"{cik}_{year}.json")


def load(out_dir, cik, year):
    with open(path_for(out_dir, cik, year), encoding="utf-8") as f:
        return json.load(f)


def _row_cik(line):
    m = _CIK.search(line[:500])  # cik is near the start of each row; avoids parsing MB-sized rows
    return _cik(m.group(1).decode()) if m else None


def fetch_year(year, ciks, out_dir, lines_for=None):
    lines_for = lines_for or _lines
    best = {}
    for split in SPLITS:
        for line in lines_for(f"{BASE}/{year}/{split}.jsonl"):
            if not line or _row_cik(line) not in ciks:
                continue
            row = json.loads(line)
            size = sum(len(v or "") for k, v in row.items() if k.startswith("section_"))
            cik = _cik(row["cik"])
            if cik not in best or size > best[cik][0]:
                best[cik] = (size, row)
    for cik, (_, row) in best.items():
        with open(path_for(out_dir, cik, year), "w", encoding="utf-8") as f:
            json.dump(row, f, ensure_ascii=False)
    return set(ciks) - set(best)


def _fetch_with_retry(year, todo, out_dir):
    for attempt in range(1, 4):  # Hugging Face sometimes drops a GB-sized stream midway
        try:
            return fetch_year(year, todo, out_dir)
        except (requests.ConnectionError, requests.exceptions.ChunkedEncodingError) as e:
            print(f"[{year}] attempt {attempt} failed: {e.__class__.__name__}", flush=True)
            if attempt == 3:
                raise


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", default="config/exp1_sample.json")
    ap.add_argument("--out", default=DEFAULT_DIR)
    ap.add_argument("--pilot", action="store_true", help="only the pilot pairs")
    ap.add_argument("--workers", type=int, default=4, help="years streamed in parallel")
    args = ap.parse_args()
    pairs = json.load(open(args.sample, encoding="utf-8"))["pairs"]
    if args.pilot:
        pairs = [p for p in pairs if p["pilot"]]
    os.makedirs(args.out, exist_ok=True)
    jobs = {}
    for year, ciks in sorted(targets(pairs).items()):
        todo = {c for c in ciks if not os.path.exists(path_for(args.out, c, year))}
        if todo:
            jobs[year] = todo
    missing = []
    with concurrent.futures.ProcessPoolExecutor(args.workers) as pool:  # JSON parsing is CPU-bound
        futures = {pool.submit(_fetch_with_retry, year, todo, args.out): year for year, todo in jobs.items()}
        for fut in concurrent.futures.as_completed(futures):
            year = futures[fut]
            missing += [(c, year) for c in fut.result()]
            print(f"[{year}] fetched {len(jobs[year]) - len(fut.result())}/{len(jobs[year])} filings", flush=True)
    if missing:
        raise SystemExit(f"not found in EDGAR-CORPUS: {missing}")


if __name__ == "__main__":
    main()

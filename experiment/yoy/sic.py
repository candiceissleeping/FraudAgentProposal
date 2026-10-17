"""Look up each firm's SIC industry code from SEC EDGAR (data.sec.gov submissions API).

EDGAR-CORPUS rows carry no industry, so controls are matched on SIC from here.
SEC asks for a User-Agent with contact details and at most 10 requests/second:

  SEC_USER_AGENT="Your Name your@email" python -m experiment.yoy.sic

Results are cached in data/sic.json ({cik: {"sic": "2834", "name": ...}}); reruns
only fetch missing CIKs. Note: the API returns the firm's *current* SIC code.
"""
import argparse
import json
import os
import sys
import time

import requests

URL = "https://data.sec.gov/submissions/CIK{:010d}.json"
DEFAULT_PATH = "data/sic.json"
MIN_INTERVAL = 0.125  # 8 requests/second, under SEC's 10/s limit


def load(path=DEFAULT_PATH):
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}


def fetch(ciks, path=DEFAULT_PATH, user_agent=None):
    cache = load(path)
    todo = sorted(c for c in set(ciks) if c not in cache)
    if not todo:
        return cache
    user_agent = user_agent or os.environ.get("SEC_USER_AGENT")
    if not user_agent:
        sys.exit("Set SEC_USER_AGENT to 'Name email' (required by SEC for data.sec.gov)")
    s = requests.Session()
    s.headers["User-Agent"] = user_agent
    print(f"fetching SIC for {len(todo):,} CIKs ({len(cache):,} cached)", flush=True)
    for i, cik in enumerate(todo, 1):
        start = time.monotonic()
        r = s.get(URL.format(int(cik)), timeout=30)
        if r.status_code == 404:
            cache[cik] = {"sic": "", "name": ""}
        else:
            r.raise_for_status()
            d = r.json()
            cache[cik] = {"sic": d.get("sic") or "", "name": d.get("name") or ""}
        if i % 500 == 0 or i == len(todo):
            _save(cache, path)
            print(f"  {i:,}/{len(todo):,}", flush=True)
        time.sleep(max(0.0, MIN_INTERVAL - (time.monotonic() - start)))
    return cache


def _save(cache, path):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cache, f, sort_keys=True)
    os.replace(tmp, path)


def main():
    from experiment.yoy import build_sample
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--path", default=DEFAULT_PATH)
    args = ap.parse_args()
    fetch(build_sample.ciks_needing_sic(), args.path)


if __name__ == "__main__":
    main()

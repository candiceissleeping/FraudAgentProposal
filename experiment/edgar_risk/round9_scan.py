"""Round 9: scan every 8-K / 8-K/A filed 2026-07-01..2026-10-31 for Item 4.02 (non-reliance).

Reads data/round9/idx/form.*.idx, fetches each filing's small .hdr.sgml header (items, SIC, state),
appends one line per filing to data/round9/8k_items.tsv. Resumable; stays under 10 requests/second.
"""
import glob
import os
import re
import subprocess
import threading
import time
from concurrent.futures import ThreadPoolExecutor

UA = os.environ.get("SEC_UA", "research candace7907@gmail.com")
OUT = "data/round9/8k_items.tsv"
lock = threading.Lock()
rate_lock = threading.Lock()
last = [0.0]


def throttle():
    with rate_lock:
        wait = last[0] + 0.115 - time.time()
        if wait > 0:
            time.sleep(wait)
        last[0] = time.time()


def fetch(row):
    form, name, cik, date, path = row
    acc = os.path.basename(path)[:-4]
    url = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{acc}.hdr.sgml"
    for attempt in range(4):
        throttle()
        r = subprocess.run(["curl", "-s", "--fail", "-m", "20", "-A", UA, url], capture_output=True)
        if r.returncode == 0:
            t = r.stdout.decode("latin-1")
            items = ",".join(re.findall(r"<ITEMS>([\d.]+)", t))
            sic = (re.search(r"<ASSIGNED-SIC>(\d+)", t) or [None, ""])[1]
            fye = (re.search(r"<FISCAL-YEAR-END>(\d+)", t) or [None, ""])[1]
            line = "\t".join([acc, form, cik, date, name, items, sic, fye]) + "\n"
            with lock:
                with open(OUT, "a") as fh:
                    fh.write(line)
            return
        time.sleep(2 ** attempt)
    with lock:
        with open(OUT + ".failed", "a") as fh:
            fh.write(acc + "\n")


def main():
    rows = []
    for f in sorted(glob.glob("data/round9/idx/form.*.idx")):
        for line in open(f, encoding="latin-1"):
            m = re.match(r"^(8-K(?:/A)?)\s{2,}(.+?)\s{2,}(\d+)\s+(\d{8})\s+(edgar/\S+\.txt)", line)
            if m:
                rows.append(m.groups())
    done = set()
    if os.path.exists(OUT):
        done = {l.split("\t")[0] for l in open(OUT)}
    todo = [r for r in rows if os.path.basename(r[4])[:-4] not in done]
    print(f"{len(rows)} 8-K filings, {len(todo)} to fetch", flush=True)
    with ThreadPoolExecutor(8) as ex:
        for i, _ in enumerate(ex.map(fetch, todo), 1):
            if i % 1000 == 0:
                print(i, flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()

"""Round 10: FraudDebate-Agent zero-shot replication + memory decomposition.

Subcommands
  corpus    stream EDGAR-CORPUS (filing years 2003-2009), keep 10-K records for CIKs mapped from Bao gvkeys
            -> data/round10/corpus/<year>.jsonl.gz  (+ index.tsv: cik, year, split, n_tokens_section_7)
"""
import argparse, csv, gzip, io, json, os, sys, urllib.error, urllib.request

import pyreadr

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = f"{ROOT}/data/round10"
RAW = f"{DATA}/raw"
HF = "https://huggingface.co/datasets/eloukas/edgar-corpus/resolve/main/{y}/{s}.jsonl"
TEST_FY = range(2003, 2009)


def bao_rows():
    return list(csv.DictReader(open(f"{RAW}/data_FraudDetection_JAR2020.csv")))


def gvkey_ciks():
    g = pyreadr.read_r(f"{RAW}/gvkey_ciks.rda")["gvkey_ciks"]
    out = {}
    for gv, cik, fd, ld in zip(g.gvkey, g.cik, g.first_date, g.last_date):
        out.setdefault(gv, []).append((int(cik), str(fd), str(ld)))
    return out


def corpus(args):
    m = gvkey_ciks()
    ciks = {c for r in bao_rows() if int(r["fyear"]) in TEST_FY for c, _, _ in m.get(r["gvkey"].zfill(6), [])}
    print("candidate CIKs", len(ciks), file=sys.stderr)
    os.makedirs(f"{DATA}/corpus", exist_ok=True)
    idx_path = f"{DATA}/corpus/index.tsv"
    done = set()
    if os.path.exists(idx_path):
        done = {tuple(l.split("\t")[:2]) for l in open(f"{DATA}/corpus/done.tsv")} if os.path.exists(f"{DATA}/corpus/done.tsv") else set()
    idx = open(idx_path, "a")
    for y in args.years:
        for s in ("train", "validate", "test"):
            if (str(y), s) in done:
                continue
            out = gzip.open(f"{DATA}/corpus/{y}_{s}.jsonl.gz", "wt")
            req = urllib.request.Request(HF.format(y=y, s=s), headers={"User-Agent": "research-script"})
            n = kept = 0
            with urllib.request.urlopen(req, timeout=600) as resp:
                for line in io.TextIOWrapper(resp, encoding="utf-8"):
                    n += 1
                    rec = json.loads(line)
                    if int(rec["cik"]) not in ciks:
                        continue
                    kept += 1
                    out.write(line)
                    idx.write(f"{int(rec['cik'])}\t{rec['year']}\t{s}\t{rec['filename']}\t{len((rec.get('section_7') or '').split())}\n")
            out.close(); idx.flush()
            open(f"{DATA}/corpus/done.tsv", "a").write(f"{y}\t{s}\t{n}\t{kept}\n")
            print(y, s, n, kept, file=sys.stderr, flush=True)


UA = os.environ.get("SEC_UA", "research candace7907@gmail.com")
FORMS_10K = {"10-K", "10-K405", "10-KSB", "10-KSB40", "10-KT", "10-KT405"}


def _get(url):
    import time
    for i in range(5):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "identity"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            time.sleep(2 ** i)
        except Exception:
            time.sleep(2 ** i)
    return None


def submissions(args):
    """Cache data.sec.gov submissions JSON (incl. older filing pages) for every candidate CIK."""
    import time
    m = gvkey_ciks()
    ciks = sorted({c for r in bao_rows() if int(r["fyear"]) in TEST_FY for c, _, _ in m.get(r["gvkey"].zfill(6), [])})
    d = f"{DATA}/submissions"; os.makedirs(d, exist_ok=True)
    for i, c in enumerate(ciks):
        path = f"{d}/{c}.json"
        if os.path.exists(path):
            continue
        b = _get(f"https://data.sec.gov/submissions/CIK{c:010d}.json")
        if b is None:
            open(path, "w").write("null"); continue
        j = json.loads(b)
        pages = [j["filings"]["recent"]]
        for f in j["filings"].get("files", []):
            time.sleep(0.12)
            bb = _get(f"https://data.sec.gov/submissions/{f['name']}")
            if bb:
                pages.append(json.loads(bb))
        keep = []
        for pg in pages:
            for k in range(len(pg["form"])):
                if pg["form"][k] in FORMS_10K:
                    keep.append({"form": pg["form"][k], "filingDate": pg["filingDate"][k],
                                 "reportDate": pg["reportDate"][k], "accession": pg["accessionNumber"][k]})
        json.dump({"cik": c, "name": j.get("name"), "formerNames": j.get("formerNames", []),
                   "sic": j.get("sic"), "tenk": keep}, open(path, "w"))
        time.sleep(0.12)
        if i % 200 == 0:
            print(i, len(ciks), file=sys.stderr, flush=True)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("corpus"); p.add_argument("--years", type=int, nargs="+", default=list(range(2003, 2010)))
    sub.add_parser("submissions")
    a = ap.parse_args()
    {"corpus": corpus, "submissions": submissions}[a.cmd](a)


if __name__ == "__main__":
    main()

"""Round 10: FraudDebate-Agent zero-shot replication + memory decomposition.

Subcommands
  corpus    stream EDGAR-CORPUS (filing years 2003-2009), keep 10-K records for CIKs mapped from Bao gvkeys
            -> data/round10/corpus/<year>.jsonl.gz  (+ index.tsv: cik, year, split, n_tokens_section_7)
"""
import argparse, collections, csv, gzip, io, json, os, sys, urllib.error, urllib.request

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


SEED = 20261103
RES = f"{ROOT}/results/round10"


def _fy_of(report_date):
    y, m = int(report_date[:4]), int(report_date[5:7])
    return y if m >= 6 else y - 1


def _name_at(sub, date):
    for f in sub.get("formerNames", []):
        if f["from"][:10] <= date <= (f["to"] or "9999")[:10]:
            return f["name"]
    return sub["name"]


def sample(args):
    import random
    m = gvkey_ciks()
    rows = [r for r in bao_rows() if int(r["fyear"]) in TEST_FY]
    fraud_gvkeys = {r["gvkey"] for r in bao_rows() if r["misstate"] == "1" and 1991 <= int(r["fyear"]) <= 2008}
    pre_aaers = {r["p_aaer"] for r in bao_rows() if r["misstate"] == "1" and int(r["fyear"]) <= 2002 and r["p_aaer"]}
    idx = {}
    for line in open(f"{DATA}/corpus/index.tsv"):
        cik, yr, split, fn, ntok = line.rstrip("\n").split("\t")
        idx.setdefault((int(cik), int(yr)), (split, fn, int(ntok)))
    subs = {}

    def sub(c):
        if c not in subs:
            path = f"{DATA}/submissions/{c}.json"
            subs[c] = json.load(open(path)) if os.path.exists(path) else None
        return subs[c]

    steps = collections.OrderedDict((k, [0, 0]) for k in (
        "1 Bao FY2003-2008", "2 gvkey->CIK mapped", "3 10-K for fiscal year identified", "4 record in EDGAR-CORPUS",
        "5 MD&A >= 100 tokens", "6 unique filing"))
    elig, seen = [], set()
    for r in rows:
        y = int(r["fyear"]); fr = r["misstate"] == "1"
        def bump(k): steps[k][0] += 1; steps[k][1] += fr
        bump("1 Bao FY2003-2008")
        cands = sorted(m.get(r["gvkey"].zfill(6), []), key=lambda t: not (t[1][:4] <= str(y + 1) <= t[2][:4]))
        if not cands: continue
        bump("2 gvkey->CIK mapped")
        hit = None
        for c, _, _ in cands:
            s_ = sub(c)
            tk = sorted([t for t in (s_ or {}).get("tenk", []) if t["reportDate"] and _fy_of(t["reportDate"]) == y],
                        key=lambda t: t["filingDate"])
            if tk:
                hit = (c, int(tk[0]["filingDate"][:4]), tk[0], 0); break
        if hit is None:  # fallback: assume filing year = fyear + 1, first candidate with a corpus record
            for c, _, _ in cands:
                if (c, y + 1) in idx:
                    hit = (c, y + 1, None, 1); break
        if hit is None: continue
        bump("3 10-K for fiscal year identified")
        c, fy_file, tk, inferred = hit
        if (c, fy_file) not in idx: continue
        bump("4 record in EDGAR-CORPUS")
        split, fn, ntok = idx[(c, fy_file)]
        if ntok < 100: continue
        bump("5 MD&A >= 100 tokens")
        if (c, fy_file) in seen: continue
        seen.add((c, fy_file))
        bump("6 unique filing")
        s_ = sub(c) or {}
        elig.append({"id": f"{c}_{y}", "gvkey": r["gvkey"].zfill(6), "cik": c, "fyear": y, "fraud": int(fr),
                     "p_aaer": r["p_aaer"], "fraud_firm": int(r["gvkey"] in fraud_gvkeys),
                     "serial_pre2003": int(fr and r["p_aaer"] in pre_aaers), "at": float(r["at"] or "nan"),
                     "corpus_year": fy_file, "corpus_split": split, "corpus_file": fn, "mda_tokens": ntok,
                     "period_inferred": inferred, "report_date": tk["reportDate"] if tk else "",
                     "filing_date": tk["filingDate"] if tk else "",
                     "name": _name_at(s_, tk["filingDate"]) if (tk and s_) else s_.get("name", ""),
                     "aliases": [s_.get("name", "")] + [f["name"] for f in s_.get("formerNames", [])] if s_ else []})
    rng = random.Random(SEED)
    frauds = [e for e in elig if e["fraud"]]
    pool = [e for e in elig if not e["fraud"]]
    nonf = rng.sample(pool, min(len(pool), 10 * len(frauds)))
    M = frauds + nonf
    mids = {e["id"] for e in M}
    s_pool = [e for e in pool if e["fraud_firm"] and e["id"] not in mids]
    S = s_pool if len(s_pool) <= 300 else random.Random(SEED).sample(s_pool, 300)
    dfr = frauds if len(frauds) <= 150 else random.Random(SEED).sample(frauds, 150)
    D = [e["id"] for e in dfr] + [e["id"] for e in random.Random(SEED).sample(nonf, 150)]
    order = [e["id"] for e in M]; random.Random(SEED).shuffle(order)
    pilot = [i for i in order if i in {e["id"] for e in frauds}][:4] + [i for i in order if i not in {e["id"] for e in frauds}][:16]
    os.makedirs(RES, exist_ok=True)
    json.dump({"seed": SEED, "M": M, "S": S, "D_ids": D, "pilot_ids": pilot,
               "pop_eligible_nonfraud": len(pool), "pop_eligible_fraud": len(frauds)},
              open(f"{RES}/sample.json", "w"), indent=1)
    with open(f"{RES}/attrition.tsv", "w") as f:
        f.write("step\tfirm_years\tfraud\n")
        for k, (n, fr) in steps.items():
            f.write(f"{k}\t{n}\t{fr}\n")
        f.write(f"7 sample M (all frauds + 10x random non-fraud)\t{len(M)}\t{len(frauds)}\n")
        f.write(f"S fraud-firm clean years (supplement)\t{len(S)}\t0\n")
        f.write(f"D subsample\t{len(D)}\t{len(dfr)}\n")
        f.write(f"frauds with p_aaer also in FY<=2002 (sensitivity)\t-\t{sum(e['serial_pre2003'] for e in frauds)}\n")
        f.write(f"period inferred (no submissions match)\t{sum(e['period_inferred'] for e in elig)}\t{sum(e['period_inferred'] for e in frauds)}\n")
    print(open(f"{RES}/attrition.tsv").read())


TRUNC = 4500
GENERIC = {"american", "national", "international", "general", "united", "first", "global", "pacific", "atlantic",
           "southern", "northern", "western", "eastern", "central", "standard", "capital", "financial", "energy"}


def _truncate(text, n=TRUNC):
    import re
    ms = list(re.finditer(r"\S+", text))
    return text if len(ms) <= n else text[:ms[n - 1].end()]


def _aliases(names):
    import re
    out = set()
    for name in names:
        if not name: continue
        core = re.sub(r"(?i),?\s*(inc\.?|corp\.?|corporation|ltd\.?|limited|holdings?|company|co\.|/de/|/[a-z]{2}/|group|plc|n\.v\.)(?=\s|$|,)", "", name)
        core = re.sub(r"\s+", " ", core).strip(" ,.")
        for a in {name, name.title(), core, core.title(), core.upper(), core.split()[0] if core else ""}:
            if len(a) >= 3 and (" " in a or a.lower() not in GENERIC):
                out.add(a)
    return sorted(out, key=len, reverse=True)


def inputs(args):
    """Opaque codes + A/B input files for M and S (no LLM)."""
    import hashlib, re
    from .redact import make_redactor
    smp = json.load(open(f"{RES}/sample.json"))
    recs = {e["id"]: e for e in smp["M"] + smp["S"]}
    want = {(e["corpus_year"], e["corpus_split"], e["corpus_file"]): i for i, e in recs.items()}
    texts = {}
    for (y, sp) in sorted({(k[0], k[1]) for k in want}):
        with gzip.open(f"{DATA}/corpus/{y}_{sp}.jsonl.gz", "rt") as fh:
            for line in fh:
                rec = json.loads(line)
                k = (y, sp, rec["filename"])
                if k in want:
                    texts[want[k]] = rec
    key = {}
    for d in ("A", "B"):
        os.makedirs(f"{DATA}/inputs/{d}", exist_ok=True)
    for i, e in recs.items():
        code = "r10_" + hashlib.sha256(f"{SEED}:{i}".encode()).hexdigest()[:10]
        key[i] = code
        mda = _truncate(texts[i]["section_7"])
        open(f"{DATA}/inputs/A/{code}.txt", "w").write(f"[CIK-FY] CIK: {e['cik']}, fiscal year: {e['fyear']}\n\n{mda}\n")
        t = mda
        for a in _aliases(e["aliases"] + [e["name"]]):
            t = re.sub(rf"(?i)(?<![A-Za-z]){re.escape(a)}(?![a-z])", "[COMPANY]", t)
        t = re.sub(rf"\b0*{e['cik']}\b", "[CIK]", t)
        t = re.sub(r"\b\d{2}-\d{7}\b", "[EIN]", t)
        t = re.sub(r"\(?\b\d{3}\)?[ .-]\d{3}-\d{4}\b", "[PHONE]", t)
        red = make_redactor(_aliases(e["aliases"] + [e["name"]]), e["fyear"], texts[i]["section_7"])(t)
        open(f"{DATA}/inputs/B/{code}.txt", "w").write(f"[COMPANY-Y0]\n\n{red}\n")
    json.dump(key, open(f"{RES}/code_key.json", "w"), indent=0)
    print(len(key), "inputs written", file=sys.stderr)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("corpus"); p.add_argument("--years", type=int, nargs="+", default=list(range(2003, 2010)))
    sub.add_parser("submissions"); sub.add_parser("sample"); sub.add_parser("inputs")
    a = ap.parse_args()
    {"corpus": corpus, "submissions": submissions, "sample": sample, "inputs": inputs}[a.cmd](a)


if __name__ == "__main__":
    main()

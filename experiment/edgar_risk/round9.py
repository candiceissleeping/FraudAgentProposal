"""Round 9: small, little-covered companies that the model is unlikely to recognise.

Three small issuers whose 10-K was misstated per recent SEC actions (config/round9_cases.json), each with one
automatically matched control (round-7 method). Packets: L0' (full text, unredacted, fixed extraction) and L3c
(round-8 rule v3.1 redaction). See results/round9/protocol.md.

Usage (needs SEC_UA with a contact e-mail)
  python -m experiment.edgar_risk.round9 controls
  python -m experiment.edgar_risk.round9 build          # download, extract L0', identifiers, L3c
  python -m experiment.edgar_risk.round9 agent-files --level L0|L3c --out DIR
"""
import argparse
import gzip
import html as htmlmod
import json
import math
import os
import random
import re
import subprocess
import time
from collections import defaultdict
from html.parser import HTMLParser

from . import round7
from .redact_v2 import (L2Redactor, drop_descriptive, l3_select, l3_stub, mark_sections, mask_segments, mask_units,
                        person_names, segment_names, unit_names, unmark)

CASES = "config/round9_cases.json"
DATA = "data/round9"
OUT = "results/round9"
AAER = f"{DATA}/aaer_index_2022_2026.json"
SEED = 9


def _ua():
    ua = os.environ.get("SEC_UA")
    if not ua:
        raise SystemExit("set SEC_UA (SEC requires a contact e-mail in the User-Agent)")
    return ua


def _get(url):
    for attempt in range(4):
        r = subprocess.run(["curl", "-s", "--fail", "-A", _ua(), url], capture_output=True)
        if r.returncode == 0:
            time.sleep(0.15)
            return r.stdout
        time.sleep(2 ** attempt)
    raise RuntimeError(url)


# ---------------------------------------------------------------- controls (round-7 rule, own case list)
def controls(args):
    os.environ.setdefault("SEC_UA", _ua())
    round7.DATA = "data/round7"           # filing index and XBRL frames cache live there
    round7.INDEX = "data/round7/sub_10k.tsv.gz"
    idx = round7.load_index()
    by_adsh = {r["adsh"]: r for r in idx}
    by_cik = defaultdict(list)
    for r in idx:
        by_cik[r["cik"]].append(r)
    aaer = set()
    for r in json.load(open(AAER)):
        for part in re.split(r",| and |;|\(", r["name"]):
            c = round7._core(part)
            if len(c) >= 2:
                aaer.add(c)
    cases = json.load(open(CASES))
    treated = {str(c["cik"]) for c in cases}
    used, out = set(), []
    for c in cases:
        t = by_adsh[c["y0_acc"]]
        sic = c.get("match_sic") or t["sic"]
        p0 = round7._date(t["period"])
        assets = round7._frame_assets(t["period"])
        ta = assets.get(str(c["cik"]))
        pool = []
        for r in idx:
            if r["cik"] in treated or r["cik"] in used or r["form"] != "10-K":
                continue
            if abs((round7._date(r["period"]) - p0).days) > 92 or round7._core(r["name"]) in aaer:
                continue
            prior = [x for x in by_cik[r["cik"]] if x["form"] == "10-K"
                     and 330 <= (round7._date(r["period"]) - round7._date(x["period"])).days <= 400]
            if not prior or not assets.get(str(r["cik"]), 0) > 0:
                continue
            pool.append((r, prior[0]))
        for digits in (4, 3, 2):
            same = [(r, pr) for r, pr in pool if r["sic"][:digits] == sic[:digits]]
            if len(same) >= 3 or digits == 2:
                same.sort(key=lambda x: abs(math.log(assets[x[0]["cik"]] / ta)))
                (r, pr), level = same[0], digits
                break
        used.add(r["cik"])
        out.append({"case": c["name"], "case_cik": c["cik"], "case_sic": t["sic"], "match_sic": sic, "case_assets": ta,
                    "control": r["name"], "control_cik": int(r["cik"]), "control_sic": r["sic"], "sic_digits": level,
                    "control_assets": assets[r["cik"]], "pool_size": len(same),
                    "y0_acc": r["adsh"], "y0_period": r["period"], "y1_acc": pr["adsh"], "y1_period": pr["period"]})
        print(f"{c['name']:<16} -> {r['name']:<40} SIC {r['sic']} ({level} digits, pool {len(same)}), "
              f"assets {ta / 1e6:,.1f}M vs {assets[r['cik']] / 1e6:,.1f}M")
    os.makedirs(OUT, exist_ok=True)
    json.dump(out, open(f"{OUT}/controls.json", "w"), indent=1)


def _pairs():
    cases = {c["name"]: c for c in json.load(open(CASES))}
    rows = []
    for i, ctl in enumerate(json.load(open(f"{OUT}/controls.json")), 1):
        c = cases[ctl["case"]]
        rows.append((f"S{i:02d}T", c["name"], c["cik"], c["y0_acc"], c["y0_period"], "treatment", ctl["case_sic"],
                     ctl["case_assets"]))
        rows.append((f"S{i:02d}C", ctl["control"], ctl["control_cik"], ctl["y0_acc"], ctl["y0_period"], "control",
                     ctl["control_sic"], ctl["control_assets"]))
    return rows


# ---------------------------------------------------------------- L0': HTML -> text without losing inline numbers
BLOCK = {"p", "div", "br", "li", "h1", "h2", "h3", "h4", "h5", "h6", "table", "tr", "ul", "ol", "section", "center",
         "blockquote", "pre", "hr", "page"}
SKIP = {"script", "style", "head", "title"}


class _Text(HTMLParser):
    """Paragraph text is accumulated across inline tags (span, ix:nonfraction, font, b, a ...) and flushed at block
    tags, so '$<ix>245</ix> million' stays one line. Table rows become cells joined by two spaces."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines, self.buf, self.cells, self.cell, self.skip, self.depth = [], [], None, None, 0, 0

    def _flush(self):
        s = " ".join("".join(self.buf).split())
        if s:
            self.lines.append(s)
        self.buf = []

    def handle_starttag(self, tag, attrs):
        if tag in SKIP:
            self.skip += 1
        elif tag == "table":
            self._flush()
            self.depth += 1
        elif tag == "tr" and self.depth:
            self.cells = []
        elif tag in ("td", "th") and self.cells is not None:
            self.cell = []
        elif tag in BLOCK and self.cell is None:
            self._flush()

    def handle_endtag(self, tag):
        if tag in SKIP:
            self.skip = max(0, self.skip - 1)
        elif tag in ("td", "th") and self.cell is not None and self.cells is not None:
            self.cells.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.cells is not None:
            row = [c for c in self.cells if c]
            line = "  ".join(row)
            line = re.sub(r"\$\s+(?=[\d(])", "$", line)          # "$  1,234" -> "$1,234"
            line = re.sub(r"(?<=\d)\s+\)", ")", line)            # "(1,234  )" -> "(1,234)"
            line = re.sub(r"\(\s+(?=\d)", "(", line)
            line = re.sub(r"(?<=\d)\s+%", "%", line)
            if line.strip():
                self.lines.append(line)
            self.cells = None
        elif tag == "table":
            self.depth = max(0, self.depth - 1)
        elif tag in BLOCK and self.cell is None:
            self._flush()

    def handle_data(self, data):
        if self.skip:
            return
        if self.cell is not None:
            self.cell.append(data)
        else:
            self.buf.append(data)

    def close(self):
        super().close()
        self._flush()


def html_text(doc):
    doc = re.sub(r"<ix:header>.*?</ix:header>", " ", doc, flags=re.S | re.I)
    if not re.search(r"<(p|div|table|br)[\s>]", doc, re.I):     # plain-text filing
        lines = htmlmod.unescape(re.sub(r"<[^>]+>", " ", doc)).splitlines()
    else:
        p = _Text()
        p.feed(doc)
        p.close()
        lines = p.lines
    out = []
    for ln in lines:
        ln = re.sub(r"[ \t\xa0]{2,}", "  ", ln.replace("\xa0", " ")).strip()
        if not ln or re.fullmatch(r"(?i)(page\s*)?[F-]*\s*-?\d{1,3}-?|table of contents", ln):
            continue                                                  # whole-block page numbers only
        ln = re.sub(r"\b(January|February|March|April|May|June|July|August|September|October|November|December)"
                    r"(\d{4})\b", r"\1 \2", ln)                       # "December2020" (no space in the HTML)
        out.append(ln)
    return "\n".join(out)


def filing_text(cik, acc):
    raw = _get(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{acc.replace('-', '')}/{acc}.txt").decode(
        "utf-8", errors="ignore")
    parts = []
    for doc in raw.split("<DOCUMENT>")[1:]:
        typ = re.search(r"<TYPE>\s*([^\s<]+)", doc).group(1).upper()
        fname = re.search(r"<FILENAME>\s*([^\s<]+)", doc)
        if not (typ.startswith("10-K") or typ.startswith("EX-13")):
            continue
        if fname and not fname.group(1).lower().endswith((".htm", ".html", ".txt")):
            continue
        parts.append(html_text(doc))
    return "\n".join(parts)


# ---------------------------------------------------------------- identifiers, keys, packets
def _identifiers(pid, cik, name, text):
    s = json.loads(_get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json"))
    names = [s["name"]] + [f["name"] for f in s.get("formerNames", [])] + [name]
    addresses, numbers = [], [int(cik)]
    for a in (s.get("addresses") or {}).values():
        for key in ("street1", "street2", "city"):
            if a.get(key):
                addresses.append(a[key].strip())
        if a.get("zipCode"):
            numbers.append(a["zipCode"])
    for k in ("ein", "phone"):
        if s.get(k):
            numbers.append(s[k])
    return {"pid": pid, "names": sorted(set(names)), "tickers": s.get("tickers", []), "people": person_names(text),
            "addresses": sorted(set(addresses)), "numbers": sorted(set(str(n) for n in numbers))}


def _keys(pids):
    rng, k, j = random.Random(SEED), {}, {}
    for pid in sorted(pids):
        k[pid] = round(math.exp(rng.uniform(math.log(0.5), math.log(2))), 4)
        while True:
            jj = round(math.exp(rng.uniform(math.log(0.5), math.log(2))), 4)
            if abs(math.log(k[pid] / jj)) >= math.log(1.25):
                break
        j[pid] = jj
    return k, j


def _write(level, pid, text):
    os.makedirs(f"{DATA}/packets/{level}", exist_ok=True)
    with gzip.open(f"{DATA}/packets/{level}/{pid}.txt.gz", "wt", encoding="utf-8") as fh:
        fh.write(text)


def _read(level, pid):
    with gzip.open(f"{DATA}/packets/{level}/{pid}.txt.gz", "rt", encoding="utf-8") as fh:
        return fh.read()


def build(args):
    pairs = _pairs()
    k, j = _keys([p[0] for p in pairs])
    json.dump({"k": k, "j": j}, open(f"{DATA}/key.json", "w"), indent=1)
    os.makedirs(f"{DATA}/identifiers", exist_ok=True)
    stats = {}
    for pid, name, cik, acc, period, group, sic, assets in pairs:
        text = filing_text(cik, acc)
        _write("L0", pid, text)
        ident = _identifiers(pid, cik, name, text)
        json.dump(ident, open(f"{DATA}/identifiers/{pid}.json", "w"), indent=1)
        red = L2Redactor(ident, int(str(period)[:4]), k[pid], text, j=j[pid])
        marked = red.l2(mark_sections(text))
        l2 = unmark(marked)
        body, kept = l3_select(marked)
        segs = segment_names(l2)
        units = unit_names(l2, segs)
        body = mask_segments(mask_units(body, units), segs)
        body, dropped = drop_descriptive(body)
        per = str(period) if "-" in str(period) else f"{str(period)[:4]}-{str(period)[4:6]}-{str(period)[6:]}"
        _write("L3c", pid, l3_stub(sic, assets, per) + "\n\n" + body)
        stats[pid] = {"name": name, "group": group, "chars_L0": len(text), "chars_L3c": len(body), "items_kept": kept,
                      "segments": len(segs), "units": len(units), "sentences_dropped": dropped,
                      "inconsistent_numbers": len(red.inconsistent_numbers()), "people": len(ident["people"])}
        print(pid, stats[pid], flush=True)
    json.dump(stats, open(f"{OUT}/build_stats.json", "w"), indent=1)


def agent_files(args):
    pids = [p[0] for p in _pairs()]
    random.Random(SEED + {"L0": 1, "L3c": 2}[args.level]).shuffle(pids)
    os.makedirs(args.out, exist_ok=True)
    mapping = {}
    for i, pid in enumerate(pids, 1):
        open(f"{args.out}/report_{i:02d}.txt", "w").write(_read(args.level, pid))
        mapping[f"report_{i:02d}"] = pid
    json.dump(mapping, open(f"{OUT}/agent_filename_map_{args.level}.json", "w"), indent=1)
    print(json.dumps(mapping))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["controls", "build", "agent-files"])
    ap.add_argument("--level", default="L3c", choices=["L0", "L3c"])
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    {"controls": controls, "build": build, "agent-files": agent_files}[a.cmd](a)


if __name__ == "__main__":
    main()

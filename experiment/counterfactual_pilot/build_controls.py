"""Counterfactual pilot, part 2: name-redacted control 10-Ks with and without an inserted bill-and-hold paragraph.

Amounts are NOT scaled. Names, URLs and absolute years are redacted with edgar_risk.redact (years become Y0, Y-1, ...).
Kept: everything from Item 1A on, minus Items 2, 4, 5, 6 and 10-14 (close to the user's masked file; the financial
statements are kept wherever they are filed). Item 1 is dropped and replaced by a one-line industry / size header.

Usage: python -m experiment.counterfactual_pilot.build_controls OUT_DIR
"""
import gzip
import json
import os
import sys

from experiment.edgar_risk import round6_llm as base
from experiment.edgar_risk.redact import make_redactor

CONTROLS = {
    "P09C": {"name": "Thermon Group Holdings, Inc.", "fy": 2020,
             "aliases": ["Thermon Group Holdings, Inc.", "Thermon Group Holdings", "Thermon Holding Corp.",
                         "Thermon Holding Corp", "Thermon Industries, Inc.", "Thermon Industries", "Thermon", "THERMON"],
             "year_end": "March Y0", "ship": "the first quarter of the following fiscal year",
             "header": "Industry: Electronic and other electrical equipment (SIC 36) | Size: total assets $100 million - $1 billion | Fiscal year ends in calendar quarter 1"},
    "P07C": {"name": "Ducommun Incorporated", "fy": 2018,
             "aliases": ["Ducommun Incorporated", "Ducommun AeroStructures", "Ducommun LaBarge Technologies",
                         "Ducommun", "DUCOMMUN"],
             "year_end": "December Y0", "ship": "Y+1",
             "header": "Industry: Transportation equipment (SIC 37) | Size: total assets $100 million - $1 billion | Fiscal year ends in calendar quarter 4"},
}
DROP = {2, 4, 5, 6, 10, 11, 12, 13, 14}

# Same paragraph as the Revolution Lighting M+ condition (20% is a hypothetical figure)
INSERT = ("Certain customers request that we hold products they have purchased in our warehouses until they are ready "
          "to take delivery. Under these bill-and-hold arrangements, we invoice the customer and recognize revenue when "
          "the products are completed and segregated for the customer, before shipment. Revenue recognized under "
          "bill-and-hold arrangements represented approximately 20% of total revenue in Y0, and a majority of these "
          "products had not been shipped as of {year_end} and are expected to ship during {ship}.")


def sections(lines):
    """Start at Item 1A; drop the spans of Items 2, 4, 5, 6 and 10-14; keep everything else, so financial
    statements are kept whether they sit under Item 8 or after Item 15."""
    hs = base._headings(lines)
    start = next(i for i, n, sub in hs if (n, sub) == (1, "a"))
    keep = [i >= start for i in range(len(lines))]
    for k, (i, n, sub) in enumerate(hs):
        if sub == "" and n in DROP:
            end = hs[k + 1][0] if k + 1 < len(hs) else len(lines)
            for j in range(i, end):
                keep[j] = False
    return [ln for ln, kp in zip(lines, keep) if kp]


def build(pid, cfg):
    lines = gzip.open(f"data/round7/packets/{pid}.txt.gz", "rt").read().split("\n")
    kept = sections(lines)
    redact = make_redactor(cfg["aliases"], cfg["fy"], "\n".join(lines))
    body = redact("\n".join(kept))
    return f"[Item 1 Business has been removed for this study.] {cfg['header']}\n\n{body}"


def insert_after(text, anchor, cfg):
    """Insert the paragraph after the last line containing `anchor` (the notes come after MD&A, so the last
    occurrence is the revenue policy in the financial statement notes)."""
    ls = text.split("\n")
    idx = [i for i, ln in enumerate(ls) if anchor in ln]
    assert idx, anchor
    return "\n".join(ls[:idx[-1] + 1] + [INSERT.format(**cfg)] + ls[idx[-1] + 1:])


if __name__ == "__main__":
    out = sys.argv[1]
    anchors = json.load(open(sys.argv[2])) if len(sys.argv) > 2 else {}
    os.makedirs(out, exist_ok=True)
    for pid, cfg in CONTROLS.items():
        t = build(pid, cfg)
        open(f"{out}/{pid}_C.txt", "w").write(t)
        if pid in anchors:
            open(f"{out}/{pid}_Cplus.txt", "w").write(insert_after(t, anchors[pid], cfg))
        print(pid, len(t), "total assets" in t.lower(), t.count("[COMPANY]"))

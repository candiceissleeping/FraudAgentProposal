"""Build name-redacted evidence packets for blind scoring, and unblind afterwards.

  python -m experiment.edgar_risk.blind            # build results/blind_packets/Bxx.md
  python -m experiment.edgar_risk.blind --unblind  # write results/blind_key.json + comparison

Every packet is built from the same fixed queries, so no company gets extra
scrutiny. The ID -> company key is written to data/blind/_key.json (git-ignored)
and only copied into results/ by --unblind, after scores are committed.
"""
import argparse
import json
import os
import random
import re

QUERIES = [
    ("Related-party transactions", r"related[- ]part(y|ies)"),
    ("Loans / guarantees to insiders", r"(loan|advance|guarant|co-borrow)\w*.{0,150}(officer|director|executive|chairman|family|founder)"),
    ("Restatement", r"\brestate(d|ment)?\b"),
    ("Material weakness", r"material weakness"),
    ("Auditor change", r"(dismiss|resign|engage)\w*.{0,60}(independent (registered public )?accountant|auditor)"),
    ("Going concern", r"going concern|substantial doubt"),
    ("Government investigation", r"subpoena|investigation|wells notice|civil investigative demand"),
    ("Securities class action", r"securities (class action|fraud)|section 10\(b\)|rule 10b-5"),
    ("Unconsolidated entities / VIE", r"variable interest entit|special purpose|unconsolidated (affiliate|entit|subsidiar)"),
    ("Judgmental revenue / valuation", r"level (3|iii)\b|mark[- ]to[- ](market|model)|indefeasible right|\biru\b|swap of capacity|channel inventor|wholesaler.{0,40}inventor|contractual allowance"),
    ("Accounting policy / estimate change", r"change in (accounting )?(estimate|principle|method)"),
    ("Price increases / acquisitions growth", r"price increase|acquisition[- ]related|non-gaap|adjusted ebitda"),
    ("Covenants / liquidity", r"covenant.{0,60}(waiver|violat|breach|default|amend)|(waiver|violat|breach|default).{0,60}covenant|downgrad|liquidity"),
    ("Revenue recognition", r"revenue recognition|recogni[sz]e[sd]? revenue"),
    ("Grower / supplier payments", r"(payment|pay)s? to (grower|supplier|vendor)s?|grower"),
]
FIXED_SECTIONS = [("section_9A", "Item 9A Controls and Procedures", 1500),
                  ("section_9", "Item 9 Changes in / Disagreements with Accountants", 800),
                  ("section_3", "Item 3 Legal Proceedings", 2500)]
PER_QUERY, BEFORE, AFTER = 2, 250, 1250  # notes run forward from their heading
SCAN = ["section_1A", "section_3", "section_7", "section_7A", "section_8", "section_9", "section_9A",
        "section_14", "section_15", "section_1"]


def redact(text, aliases):
    for a in sorted(aliases, key=len, reverse=True):
        text = re.sub(rf"(?<![A-Za-z]){re.escape(a)}(?![a-z])", "[COMPANY]", text)
    return text


def passages(filing, pattern, n=PER_QUERY):
    """Top-n non-overlapping windows, ranked by query matches plus dollar amounts inside the window
    (substantive disclosures beat passing mentions); ties keep document order."""
    rx, cands = re.compile(pattern, re.I), []
    for sec in SCAN:
        t = re.sub(r"\s+", " ", filing.get(sec) or "")
        last_end = -1
        for m in rx.finditer(t):
            if m.start() < last_end:
                continue
            s, e = max(0, m.start() - BEFORE), min(len(t), m.end() + AFTER)
            w = t[s:e]
            cands.append((2 * len(rx.findall(w)) + min(3, len(re.findall(r"\$\s?[\d,.]+ (million|billion)", w))), len(cands), sec, w))
            last_end = e
    cands.sort(key=lambda c: (-c[0], c[1]))
    return [(sec, w) for _, _, sec, w in cands[:n]]


def build_packet(pid, filing, aliases, redactor=None, queries=None):
    """redactor: optional text -> text function (round 3); default redacts aliases only (round 2)."""
    year = "Y0 (years shown relative to the fiscal year)" if redactor else filing.get("year")
    lines = [f"# Packet {pid}", "", f"Fiscal year: {year}  ",
             "Sections present: " + ", ".join(k for k, v in filing.items() if k.startswith("section_") and (v or "").strip()), ""]
    # with a redactor, only filing text is redacted, never the packet's own headings
    ev = redactor or (lambda t: t)
    for sec, title, n in FIXED_SECTIONS:
        t = re.sub(r"\s+", " ", filing.get(sec) or "").strip()
        lines += [f"## {title}", "", f"> {ev(t[:n]) or '(empty)'}", ""]
    for title, pat in (queries or QUERIES):
        lines += [f"## Query: {title}", ""]
        hits = passages(filing, pat)
        lines += [f"- [{s}] ...{ev(p)}..." for s, p in hits] if hits else ["- (no matches)"]
        lines.append("")
    text = "\n".join(lines)
    return text if redactor else redact(text, aliases)


def pick(companies, data_dir):
    """Per year: the treatment plus the first non-empty control (backups only if needed)."""
    chosen = []
    for year in sorted({c["year"] for c in companies}):
        group = [c for c in companies if c["year"] == year]
        for role in ("treatment", "control"):
            cands = [c for c in group if c["group"] == role] + \
                    ([c for c in group if c["group"] == "control_backup"] if role == "control" else [])
            for c in cands:
                path = os.path.join(data_dir, f"{c['cik']}_{year}.json")
                if os.path.exists(path):
                    f = json.load(open(path, encoding="utf-8"))
                    if sum(len(v or "") for k, v in f.items() if k.startswith("section_")) >= 5000:
                        chosen.append((c, f))
                        break
    return chosen


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", default="config/blind_companies.json")
    ap.add_argument("--data", default="data/blind")
    ap.add_argument("--out", default="results/blind_packets")
    ap.add_argument("--unblind", action="store_true")
    args = ap.parse_args()
    key_path = os.path.join(args.data, "_key.json")

    if args.unblind:
        key = json.load(open(key_path, encoding="utf-8"))
        json.dump(key, open("results/blind_key.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        for pid, c in sorted(key.items()):
            print(f"{pid}  {c['group']:<10} {c['name']} ({c['year']})")
        return

    companies = json.load(open(args.config, encoding="utf-8"))["companies"]
    chosen = pick(companies, args.data)
    random.SystemRandom().shuffle(chosen)
    os.makedirs(args.out, exist_ok=True)
    key = {}
    for i, (c, filing) in enumerate(chosen, 1):
        pid = f"B{i:02d}"
        key[pid] = {"name": c["name"], "cik": c["cik"], "year": c["year"],
                    "group": "control" if c["group"].startswith("control") else "treatment"}
        with open(os.path.join(args.out, f"{pid}.md"), "w", encoding="utf-8") as f:
            f.write(build_packet(pid, filing, c.get("aliases", []) + [c["name"]]))
    json.dump(key, open(key_path, "w", encoding="utf-8"), indent=2)
    print(f"Built {len(key)} packets in {args.out}/ (key sealed in {key_path})")


if __name__ == "__main__":
    main()

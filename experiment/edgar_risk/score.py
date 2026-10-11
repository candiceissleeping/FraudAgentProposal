"""Turn extracted evidence into a 0-100 risk score with written reasons.

Per category: points = weight * min(hits, SATURATION) / SATURATION.
Saturation keeps one long section with many repeated mentions from dominating.
Total is capped at 100.
"""
import argparse
import glob
import json
import os

from . import signals

SATURATION = 3
BANDS = [(75, "High"), (50, "Elevated"), (25, "Moderate"), (0, "Low")]


def band(score):
    return next(label for floor, label in BANDS if score >= floor)


def score_filing(filing):
    evidence = signals.extract(filing)
    breakdown, reasons = {}, []
    for cat, spec in signals.CATEGORIES.items():
        hits = evidence[cat]["hits"]
        pts = round(spec["weight"] * min(hits, SATURATION) / SATURATION, 1)
        breakdown[cat] = {"label": spec["label"], "hits": hits, "points": pts, "max": spec["weight"]}
        if pts:
            ex = evidence[cat]["examples"][0]
            reasons.append({
                "category": spec["label"], "points": pts, "hits": hits,
                "quote": ex["text"][:300], "section": ex["section"],
            })
    total = min(100.0, round(sum(b["points"] for b in breakdown.values()), 1))
    reasons.sort(key=lambda r: -r["points"])
    return {
        "score": total,
        "band": band(total),
        "breakdown": breakdown,
        "reasons": reasons,
        "evidence": evidence,
        "text_stats": signals.text_stats(filing),
    }


def render_report(results):
    lines = ["# EDGAR-CORPUS 10-K Risk Experiment - Rule-based Scores", "",
             "| Company | Group | 10-K year | Score | Band | Top reasons |",
             "|---|---|---|---|---|---|"]
    for r in sorted(results, key=lambda r: -r["score"]):
        c = r["company"]
        top = "; ".join(f"{x['category']} (+{x['points']})" for x in r["reasons"][:3]) or "No red flags found"
        lines.append(f"| {c['name']} | {c['group']} | {c['year']} | {r['score']} | {r['band']} | {top} |")
    lines.append("")
    for r in sorted(results, key=lambda r: -r["score"]):
        c = r["company"]
        lines += [f"## {c['name']} - {r['score']} ({r['band']})", "",
                  f"Filing: `{r['filename']}`  ", f"Sections present: {', '.join(r['text_stats']['sections_present'])}", ""]
        if not r["reasons"]:
            lines += ["No red-flag evidence matched. This is evidence of absence only for the patterns tested.", ""]
        for x in r["reasons"]:
            lines += [f"- **{x['category']}** +{x['points']} ({x['hits']} sentences) - {x['section']}:",
                      f"  > {x['quote']}", ""]
    tre = [r["score"] for r in results if r["company"]["group"] == "treatment"]
    ctl = [r["score"] for r in results if r["company"]["group"] == "control"]
    if tre and ctl:
        lines += ["## Group comparison", "",
                  f"- Treatment mean score: {sum(tre)/len(tre):.1f} (n={len(tre)})",
                  f"- Control mean score: {sum(ctl)/len(ctl):.1f} (n={len(ctl)})",
                  f"- Treatment companies scoring above every control: "
                  f"{sum(t > max(ctl) for t in tre)}/{len(tre)}", ""]
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--data", default="data")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    results = []
    for path in sorted(glob.glob(os.path.join(args.data, "*.json"))):
        filing = json.load(open(path, encoding="utf-8"))
        r = score_filing(filing)
        r["company"], r["filename"] = filing["_company"], filing.get("filename")
        results.append(r)
        out = os.path.join(args.out, os.path.basename(path))
        json.dump(r, open(out, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
        print(f"{r['company']['name']:<28} {r['score']:>5}  {r['band']}")
    if not results:
        raise SystemExit(f"No filings in {args.data}/ - run fetch first")
    with open(os.path.join(args.out, "rule_based_report.md"), "w", encoding="utf-8") as f:
        f.write(render_report(results))


if __name__ == "__main__":
    main()

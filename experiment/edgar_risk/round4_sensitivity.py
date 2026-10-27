"""Round-4 sensitivity analysis: post-disclosure exclusions, matched-pair win rates, per-industry AUC."""
import csv
import json
from collections import defaultdict

from .round3 import auc, auc_ci

OUT = "results/round4"
# Treatment filings that already discuss the problem behind the enforcement action (noted in scores.md before unblinding).
POST_DISCLOSURE = {"American International Group", "ITT Educational Services", "Navistar International"}
POSSIBLY_POST = {"Super Micro Computer"}


def load():
    key = json.load(open(f"{OUT}/key.json", encoding="utf-8"))
    kw = {r["packet"]: float(r["keyword_score"]) for r in csv.DictReader(open(f"{OUT}/keyword_scores.csv"))}
    hs = {r["packet"]: r for r in csv.DictReader(open(f"{OUT}/scores.csv"))}
    pool = json.load(open("config/round4_pool.json", encoding="utf-8"))["pairs"]
    pair_of = {}
    for i, p in enumerate(pool):
        pair_of[p["treatment"]["name"]] = pair_of[p["control"]["name"]] = i
    rows = []
    for pid, k in key.items():
        rows.append(dict(pid=pid, pair=pair_of[k["name"]], **k, keyword=kw[pid],
                         rubric=float(hs[pid]["rubric_total"]), holistic=float(hs[pid]["holistic"])))
    return rows


def report(rows, label):
    print(f"\n## {label} (n={len(rows)}: {sum(r['group'] == 'treatment' for r in rows)} treatment)")
    for m in ("keyword", "rubric", "holistic"):
        pos = [r[m] for r in rows if r["group"] == "treatment"]
        neg = [r[m] for r in rows if r["group"] == "control"]
        lo, hi = auc_ci(pos, neg)
        print(f"AUC {m:<9} {auc(pos, neg):.2f} (95% CI {lo:.2f}-{hi:.2f})")


def pair_wins(rows):
    by = defaultdict(dict)
    for r in rows:
        by[r["pair"]][r["group"]] = r
    full = [v for v in by.values() if len(v) == 2]
    print(f"\n## Within-pair comparison ({len(full)} complete pairs): treatment > control / tie / lower")
    for m in ("keyword", "rubric", "holistic"):
        w = sum(v["treatment"][m] > v["control"][m] for v in full)
        t = sum(v["treatment"][m] == v["control"][m] for v in full)
        print(f"{m:<9} {w} / {t} / {len(full) - w - t}")


def by_industry(rows):
    print("\n## Per industry (holistic AUC; small n, descriptive only)")
    ind = defaultdict(list)
    for r in rows:
        ind[r["industry"]].append(r)
    for name, rs in sorted(ind.items()):
        pos = [r["holistic"] for r in rs if r["group"] == "treatment"]
        neg = [r["holistic"] for r in rs if r["group"] == "control"]
        if pos and neg:
            print(f"{name:<22} pairs~{min(len(pos), len(neg))}  holistic AUC {auc(pos, neg):.2f}  rubric AUC "
                  f"{auc([r['rubric'] for r in rs if r['group'] == 'treatment'], [r['rubric'] for r in rs if r['group'] == 'control']):.2f}")


def main():
    rows = load()
    report(rows, "All filings")
    drop = {r["pair"] for r in rows if r["name"] in POST_DISCLOSURE}
    report([r for r in rows if r["pair"] not in drop], "Excluding post-disclosure pairs (AIG, ITT, Navistar)")
    drop2 = drop | {r["pair"] for r in rows if r["name"] in POSSIBLY_POST}
    report([r for r in rows if r["pair"] not in drop2], "Also excluding Super Micro pair")
    pair_wins(rows)
    by_industry(rows)


if __name__ == "__main__":
    main()

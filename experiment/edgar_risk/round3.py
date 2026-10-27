"""Round 3: random draw from a candidate pool, strong redaction, scores committed before unblinding.

  python -m experiment.edgar_risk.round3 draw      # validate pool, draw 5 pairs, build packets + keyword scores
  python -m experiment.edgar_risk.round3 unblind   # reveal key and compute AUC for each method

`draw` prints only counts, never names: the scorer knows the pool but not which
pairs were drawn. The key is sealed in data/round3/_key.json (git-ignored).
"""
import argparse
import csv
import json
import os
import random

from . import blind, score
from .redact import make_redactor

POOL = "config/round3_pool.json"
DATA = "data/round3"
OUT = "results/round3"
KEY = os.path.join(DATA, "_key.json")
N_PAIRS = 5
MIN_CHARS, MIN_NAME_HITS = 5000, 3

# Round-3 queries = round-2 queries + two items added to the pre-registered rubric v2
QUERIES = blind.QUERIES + [
    ("Internal investigation", r"(audit committee|special committee|independent counsel|outside counsel|forensic).{0,120}(investigat|inquiry|review)"),
    ("Founder / family / controlling holder", r"controlling (shareholder|stockholder)|members of (his|her|their) (immediate )?family|founder|class b common|super-?voting|voting control"),
]


def _text(filing):
    return " ".join(v or "" for k, v in filing.items() if k.startswith("section_"))


def _load(company, year):
    path = os.path.join(DATA, f"{company['cik']}_{year}.json")
    if not os.path.exists(path):
        return None
    filing = json.load(open(path, encoding="utf-8"))
    text = _text(filing)
    names = [company["name"].split()[0]] + company["aliases"][:2]
    if len(text) < MIN_CHARS or sum(text.count(n) for n in names) < MIN_NAME_HITS:
        return None  # empty (incorporated by reference) or the CIK points at another company
    return filing


def auc(pos, neg):
    """Probability a random treatment scores above a random control (ties count half)."""
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def draw():
    pairs = json.load(open(POOL, encoding="utf-8"))["pairs"]
    valid = []
    for p in pairs:
        t, c = _load(p["treatment"], p["year"]), _load(p["control"], p["year"])
        if t and c:
            valid.append((p, t, c))
    print(f"valid pairs: {len(valid)}/{len(pairs)}")
    if len(valid) < N_PAIRS:
        raise SystemExit(f"need {N_PAIRS} valid pairs")
    rng = random.SystemRandom()
    chosen = []
    for p, t, c in rng.sample(valid, N_PAIRS):
        chosen += [(p, "treatment", t), (p, "control", c)]
    rng.shuffle(chosen)

    os.makedirs(os.path.join(OUT, "packets"), exist_ok=True)
    key, rows = {}, []
    for i, (pair, role, filing) in enumerate(chosen, 1):
        pid, company, year = f"R{i:02d}", pair[role], pair["year"]
        redactor = make_redactor(company["aliases"] + [company["name"]], year, _text(filing))
        with open(os.path.join(OUT, "packets", f"{pid}.md"), "w", encoding="utf-8") as f:
            f.write(blind.build_packet(pid, filing, [], redactor=redactor, queries=QUERIES))
        kw = score.score_filing(filing)
        rows.append({"packet": pid, "keyword_score": kw["score"],
                     **{cat: b["hits"] for cat, b in kw["breakdown"].items()}})
        key[pid] = {"name": company["name"], "cik": company["cik"], "year": year,
                    "industry": pair["industry"], "group": role}
    with open(os.path.join(OUT, "keyword_scores.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(sorted(rows, key=lambda r: r["packet"]))
    json.dump(key, open(KEY, "w", encoding="utf-8"), indent=2)
    print(f"built {len(key)} packets and keyword scores; key sealed in {KEY}")


def unblind():
    key = json.load(open(KEY, encoding="utf-8"))
    json.dump(key, open(os.path.join(OUT, "key.json"), "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    kw = {r["packet"]: float(r["keyword_score"]) for r in csv.DictReader(open(os.path.join(OUT, "keyword_scores.csv")))}
    human = {r["packet"]: r for r in csv.DictReader(open(os.path.join(OUT, "scores.csv")))}
    print(f"{'pkt':<4} {'group':<9} {'company':<28} {'yr':<5} {'kw':>5} {'rubric':>6} {'holistic':>8}  guess")
    for pid in sorted(key):
        k, h = key[pid], human[pid]
        print(f"{pid:<4} {k['group']:<9} {k['name']:<28} {k['year']:<5} {kw[pid]:>5} {h['rubric_total']:>6} "
              f"{h['holistic']:>8}  {h['recognized_as']}")
    for label, get in [("keyword", lambda p: kw[p]), ("rubric", lambda p: float(human[p]["rubric_total"])),
                       ("holistic", lambda p: float(human[p]["holistic"]))]:
        pos = [get(p) for p in key if key[p]["group"] == "treatment"]
        neg = [get(p) for p in key if key[p]["group"] == "control"]
        print(f"AUC {label:<9} {auc(pos, neg):.2f}   treatment mean {sum(pos)/len(pos):.1f}  control mean {sum(neg)/len(neg):.1f}")
    correct = sum(1 for p in key if human[p]["recognized_as"].strip().lower() not in ("", "no", "none", "-")
                  and human[p]["recognized_as"].split(" ")[0].lower() in key[p]["name"].lower())
    print(f"recognized correctly: {correct}/{len(key)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("action", choices=["draw", "unblind"])
    args = ap.parse_args()
    draw() if args.action == "draw" else unblind()


if __name__ == "__main__":
    main()

"""Combined round 9 + 10 analysis (results/round10/protocol.md section 4). Descriptive only."""
import csv
from collections import defaultdict

FILES = ["results/round9/scores.csv", "results/round10/scores.csv"]


def knows(v):
    return str(v).strip().lower().startswith("true")


def auc(pos, neg):
    if not pos or not neg:
        return float("nan")
    s = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return s / (len(pos) * len(neg))


def main():
    rows = [r for f in FILES for r in csv.DictReader(open(f))]
    for level in ["L0", "L3c"]:
        by = defaultdict(dict)
        for r in rows:
            if r["level"] == level:
                by[r["pid"][:-1]][r["pid"][-1]] = r
        pairs = {k: v for k, v in by.items() if "T" in v and "C" in v}
        if not pairs:
            continue
        T = [int(v["T"]["risk_score"]) for v in pairs.values()]
        C = [int(v["C"]["risk_score"]) for v in pairs.values()]
        kn = {k: knows(v["T"]["knows_later_problems"]) for k, v in pairs.items()}
        rec = sum(r["recognised"] == "true" for r in rows if r["level"] == level)
        n = sum(1 for r in rows if r["level"] == level)
        print(f"== {level}: {len(pairs)} pairs; recognised {rec}/{n}; treatment knows-later {sum(kn.values())}/{len(kn)}")
        w = sum(t > c for t, c in zip(T, C)); ti = sum(t == c for t, c in zip(T, C))
        print(f"  all pairs: wins {w}/{ti}/{len(T)-w-ti}  AUC {auc(T, C):.2f}  mean T {sum(T)/len(T):.1f}  mean C {sum(C)/len(C):.1f}")
        unk = [k for k in pairs if not kn[k]]
        kno = [k for k in pairs if kn[k]]
        Tu = [int(pairs[k]["T"]["risk_score"]) for k in unk]
        Cu = [int(pairs[k]["C"]["risk_score"]) for k in unk]
        w = sum(t > c for t, c in zip(Tu, Cu)); ti = sum(t == c for t, c in zip(Tu, Cu))
        print(f"  PRIMARY (T does not know later): {unk}  wins {w}/{ti}/{len(Tu)-w-ti}  AUC vs all controls {auc(Tu, C):.2f}"
              + (f"  mean T {sum(Tu)/len(Tu):.1f}" if Tu else ""))
        Tk = [int(pairs[k]["T"]["risk_score"]) for k in kno]
        if Tk:
            print(f"  T knows later: n={len(Tk)} mean {sum(Tk)/len(Tk):.1f}  AUC vs all controls {auc(Tk, C):.2f}")
        for k in sorted(pairs):
            print(f"   {k}: T {pairs[k]['T']['company']:<22} {pairs[k]['T']['risk_score']:>3} knows={kn[k]!s:<5} | "
                  f"C {pairs[k]['C']['company']:<22} {pairs[k]['C']['risk_score']:>3}")


if __name__ == "__main__":
    main()

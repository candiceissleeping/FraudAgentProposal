"""Unblind a scored run and compute the pre-registered metrics (design section 3.6).

  python -m experiment.yoy.evaluate --run pilot   # -> results/exp1_<run>/report.md, scores.csv

Analysis set: pairs where both firms have a valid score in every arm (at least one repeat
parsed); exclusions are reported. A firm counts as identified by the probe when the guess
contains its current or former EDGAR name (or a distinctive word of it); metrics are repeated without the
pairs where either firm was identified.
"""
import argparse
import collections
import csv
import json
import math
import os
import random

from experiment.edgar_risk import score as keyword_score
from experiment.yoy import fetch_sample, mask, packets

BOOTSTRAP = 2000
SEED = 20261017
COMPARISONS = (("A2", "A0"), ("A2", "A1"), ("A1", "A0"), ("A3", "A0"))


def auc(pos, neg):
    """Probability a random positive outscores a random negative (ties count half)."""
    if not pos or not neg:
        return float("nan")
    wins = sum(1.0 if p > n else 0.5 if p == n else 0.0 for p in pos for n in neg)
    return wins / (len(pos) * len(neg))


def pair_auc(pairs, scores):
    """pairs: [(fraud_doc, control_doc)]; scores: {doc: value}."""
    return auc([scores[f] for f, _ in pairs], [scores[c] for _, c in pairs])


def bootstrap_delta(pairs, a, b, n=BOOTSTRAP, seed=SEED):
    """Pair-level bootstrap of AUC(a) - AUC(b); returns (delta, lo, hi)."""
    rng = random.Random(seed)
    deltas = []
    for _ in range(n):
        s = [rng.choice(pairs) for _ in pairs]
        deltas.append(pair_auc(s, a) - pair_auc(s, b))
    deltas.sort()
    return pair_auc(pairs, a) - pair_auc(pairs, b), deltas[int(0.025 * n)], deltas[int(0.975 * n) - 1]


def within_pair(pairs, scores):
    return [1.0 if scores[f] > scores[c] else 0.5 if scores[f] == scores[c] else 0.0 for f, c in pairs]


def mcnemar_p(x, y):
    """Exact two-sided McNemar on per-pair correctness (ties treated as wrong)."""
    b = sum(1 for i, j in zip(x, y) if i == 1.0 and j < 1.0)
    c = sum(1 for i, j in zip(x, y) if i < 1.0 and j == 1.0)
    k, m = min(b, c), b + c
    if m == 0:
        return 1.0, b, c
    p = 2 * sum(math.comb(m, i) for i in range(k + 1)) / 2 ** m
    return min(1.0, p), b, c


def accuracy(docs, scores, label, cut=50):
    return sum((scores[d] >= cut) == label[d] for d in docs) / len(docs)


def brier(docs, scores, label):
    return sum((scores[d] / 100 - label[d]) ** 2 for d in docs) / len(docs)


def load_responses(path):
    """-> ({(arm, doc): [prob, ...]}, {doc: probe}, {(arm, doc): [evidence]}, failures Counter)."""
    probs, probes, evidence = collections.defaultdict(list), {}, collections.defaultdict(list)
    failures = collections.Counter()
    with open(path, encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            cid, data = r["custom_id"], r["data"]
            if cid.startswith("PROBE-"):
                probes[cid[len("PROBE-"):]] = data
                continue
            arm, doc, _ = cid.split("-")
            if data is None:
                failures[(arm, r["status"], r["stop_reason"])] += 1
                continue
            probs[(arm, doc)].append(max(0, min(100, data["fraud_probability"])))
            evidence[(arm, doc)].extend(data["evidence"])
    return probs, probes, evidence, failures


def identified(probe, firm):
    if not probe:
        return False
    guess = probe["company_guess"].lower()
    return any(a.lower() in guess for a in mask.firm_aliases(firm))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--out", default=packets.DEFAULT_DIR)
    ap.add_argument("--filings", default=fetch_sample.DEFAULT_DIR)
    ap.add_argument("--firms", default=packets.FIRMS_PATH)
    args = ap.parse_args()

    with open(os.path.join(args.out, "key.json"), encoding="utf-8") as f:
        key = json.load(f)
    names = packets.load_firms(args.firms)
    probs, probes, evidence, failures = load_responses(os.path.join(args.out, "runs", args.run, "responses.jsonl"))
    scores = {arm: {d: sum(v) / len(v) for (a, d), v in probs.items() if a == arm} for arm in packets.ARMS}
    label = {d: k["role"] == "fraud" for d, k in key.items()}

    by_pair = collections.defaultdict(dict)
    for d, k in key.items():
        by_pair[k["pair_id"]][k["role"]] = d
    all_pairs = [(p["fraud"], p["control"]) for _, p in sorted(by_pair.items())]
    pairs = [(f, c) for f, c in all_pairs if all(f in scores[a] and c in scores[a] for a in packets.ARMS)]

    # non-LLM references: year-over-year dissimilarity and the existing keyword score
    with open(os.path.join(args.out, "features.csv"), encoding="utf-8") as f:
        feats = {r["doc_id"]: [float(v) for k, v in r.items() if k.startswith("sim_") and float(v) > 0]
                 for r in csv.DictReader(f)}
    refs = {"B0 dissimilarity": {d: 1 - sum(v) / len(v) if v else 0.0 for d, v in feats.items()},
            "B0 keyword score": {d: keyword_score.score_filing(fetch_sample.load(args.filings, k["cik"], k["t"]))["score"]
                                 for d, k in key.items()}}

    ident = {d: identified(probes.get(d), names.get(k["cik"], {})) for d, k in key.items()}
    year_hit = {d: bool(probes.get(d)) and abs(probes[d]["fiscal_year_guess"] - k["t"]) <= 1 for d, k in key.items()}
    clean = [(f, c) for f, c in pairs if not ident[f] and not ident[c]]
    docs = [d for p in pairs for d in p]

    L = [f"# 實驗一 {args.run}：結果（自動產生）", "",
         f"- 配對：{len(all_pairs)} 組；四組皆有有效分數：**{len(pairs)} 組**；排除被認出公司後：{len(clean)} 組",
         f"- 身分測試：認出公司 {sum(ident.values())}/{len(key)}；猜中年度（±1）{sum(year_hit.values())}/{len(key)}",
         "", "## 主要結果", "",
         "| 組別 | AUC | 配對內正確率 | Accuracy@50 | Brier | AUC（排除被認出） |", "|---|---|---|---|---|---|"]
    for arm in packets.ARMS:
        s = scores[arm]
        L.append(f"| {arm} | {pair_auc(pairs, s):.3f} | {sum(within_pair(pairs, s)) / len(pairs):.3f} | "
                 f"{accuracy(docs, s, label):.3f} | {brier(docs, s, label):.3f} | {pair_auc(clean, s):.3f} |")
    for name, s in refs.items():
        L.append(f"| {name} | {pair_auc(pairs, s):.3f} | {sum(within_pair(pairs, s)) / len(pairs):.3f} | — | — | "
                 f"{pair_auc(clean, s):.3f} |")
    L += ["", "## 組間比較（配對 bootstrap 95% CI；McNemar 為配對內正確與否）", "",
          "| 比較 | ΔAUC | 95% CI | ΔAUC（排除被認出） | McNemar p（只對 / 只錯） |", "|---|---|---|---|---|"]
    for a, b in COMPARISONS:
        d, lo, hi = bootstrap_delta(pairs, scores[a], scores[b])
        dc = pair_auc(clean, scores[a]) - pair_auc(clean, scores[b])
        p, nb, nc = mcnemar_p(within_pair(pairs, scores[a]), within_pair(pairs, scores[b]))
        L.append(f"| {a} − {b} | {d:+.3f} | [{lo:+.3f}, {hi:+.3f}] | {dc:+.3f} | {p:.3f} ({nb} / {nc}) |")
    src = collections.Counter(e["source"] for (arm, d), ev in evidence.items() if arm == "A2" for e in ev)
    L += ["", "## 機制與資料品質", "",
          f"- A2 引用證據來源：" + "、".join(f"{k} {v}" for k, v in src.most_common()),
          "- 無效回應（組別、狀態、stop_reason：次數）：" +
          ("、".join(f"{a}/{s}/{r}: {n}" for (a, s, r), n in sorted(failures.items())) or "無"),
          "", "> 試點只用來檢查流程與估計變異，不用來判定 H1；判定以主實驗為準（見設計文件 3.6）。"]

    rdir = os.path.join("results", f"exp1_{args.run}")
    os.makedirs(rdir, exist_ok=True)
    with open(os.path.join(rdir, "report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    with open(os.path.join(rdir, "scores.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["doc_id", "pair_id", "role", "cik", "t", *packets.ARMS, *refs, "identified", "year_guessed"])
        for d, k in sorted(key.items()):
            w.writerow([d, k["pair_id"], k["role"], k["cik"], k["t"],
                        *[f"{scores[a][d]:.1f}" if d in scores[a] else "" for a in packets.ARMS],
                        *[f"{refs[r][d]:.3f}" for r in refs], int(ident[d]), int(year_hit[d])])
    print("\n".join(L))


if __name__ == "__main__":
    main()

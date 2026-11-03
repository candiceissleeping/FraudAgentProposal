"""Round 9c: anonymity ladder (results/round9c/protocol.md).

Commands
  cards     L1 / L2 / L3 cards for the 54 round 9 filings + closed-set probe inputs (data/round9c/cards/)
  evaluate  results/round9c/evaluation.md
"""
import argparse
import csv
import glob
import json
import os
from collections import defaultdict

from . import round8, round9
from .round3 import auc, auc_ci

DATA = "data/round9c"
OUT = "results/round9c"
LEVELS = ("L1", "L2", "L3")


def _f(raw, key):
    try:
        return float(raw.get(key, ""))
    except ValueError:
        return None


def facets(f, raw):
    """Protocol §1: seven red-flag counts (count, out of)."""
    y = lambda k: f.get(k) == "yes"
    big = lambda k: isinstance(f.get(k), (int, float)) and f[k] >= 25
    m, fs, ta, cfo = _f(raw, "M"), _f(raw, "F"), _f(raw, "TATA"), _f(raw, "cfo_to_ni")
    num = [x for x in (m is not None and m > -1.78, fs is not None and fs > 1.0, ta is not None and ta > 0.03,
                       cfo is not None and cfo < 0.8)]
    avail = sum(v is not None for v in (m, fs, ta, cfo))
    return [
        ("Internal control and audit", sum([y("F01"), f.get("F03") == "adverse", y("F05"), y("F06")]), 4),
        ("Prior-period corrections and accounting changes", sum([f.get("F07") not in ("none", "not_found", None), y("F25"), y("F28")]), 3),
        ("Investigations and litigation", sum([y("F16"), y("F17"), y("F18")]), 3),
        ("Financial pressure", sum([y("F04"), y("F19"), y("F20"), y("F21")]), 4),
        ("Management turnover", sum([y("F14"), y("F15")]), 2),
        ("Transaction complexity", sum([y(k) for k in ("F08", "F09", "F10", "F11", "F22", "F23", "F27")] + [big("F12") or big("F13")]), 8),
        ("Numeric warning signals", sum(num), avail),
    ]


def l2_text(code, f, raw):
    lines = [f"FACT CARD {code}", "",
             "Red-flag counts by area (from the annual report and as-filed XBRL; which specific items are present is withheld):"]
    for name, n, k in facets(f, raw):
        lines.append(f"  {name}: {n} of {k}" + (" computable" if name.startswith("Numeric") else ""))
    lines += ["", "Areas: internal control and audit = material weakness, adverse ICFR opinion, auditor change, disagreement;",
              "corrections = restatement/revision, voluntary accounting change, segment change; investigations = SEC, class action,",
              "other government; pressure = going concern, covenant problem, incentive pay tied to revenue/EPS, capital raise;",
              "turnover = CEO/CFO change, interim CFO; complexity = over-time revenue, contract assets, return rights/bill-and-hold,",
              "related parties, major acquisition, SPAC/reverse merger, inventory write-down, customer concentration >=25%;",
              "numeric = Beneish M > -1.78, Dechow F > 1.0, accruals > 3% of assets, operating cash flow < 0.8x net income."]
    return "\n".join(lines) + "\n"


def l3_text(code, f, raw):
    fc = facets(f, raw)
    disc = sum(n for name, n, k in fc[:-1])
    _, num, avail = fc[-1]
    return (f"FACT CARD {code}\n\nTotal disclosure red flags (out of 24 possible): {disc}\n"
            f"Numeric warning signals: {num} of {avail} computable (Beneish M, Dechow F, accruals, cash flow vs income)\n")


def _setup():
    cmap = round9.code_map()
    rows = {r[0]: r for r in round9._rows()}
    facts = json.load(open("results/round9/facts_verified.json"))
    raw = {r["pid"]: r for r in csv.DictReader(open("results/round9/financial_features.csv"))}
    return cmap, rows, facts, raw


def cards(args):
    cmap, rows, facts, raw = _setup()
    os.makedirs(f"{DATA}/cards", exist_ok=True)
    counts = {}
    for pid, code in cmap.items():
        f, r = facts[code], raw.get(pid, {})
        open(f"{DATA}/cards/{code}_L1.txt", "w").write(round8.card_c_text(code, f, r))
        open(f"{DATA}/cards/{code}_L2.txt", "w").write(l2_text(code, f, r))
        open(f"{DATA}/cards/{code}_L3.txt", "w").write(l3_text(code, f, r))
        fc = facets(f, r)
        counts[code] = {"facets": [n for _, n, _ in fc], "disclosure_total": sum(n for _, n, _ in fc[:-1]), "numeric": fc[-1][1]}
    json.dump(counts, open(f"{DATA}/cards/counts.json", "w"), indent=1)
    names = sorted(rows[p][1] for p in rows)
    codes = sorted(cmap.values())
    for lv in LEVELS:
        allc = "\n\n".join(open(f"{DATA}/cards/{c}_{lv}.txt").read() for c in codes)
        open(f"{DATA}/cards/probe_closed_{lv}.txt", "w").write(
            "CANDIDATE COMPANIES (each fact card below belongs to exactly one of these; fiscal years 2024-2025):\n"
            + "\n".join(f"- {n}" for n in names) + "\n\n" + allc)
    print("cards", len(cmap))


def evaluate(args):
    cmap, rows, facts, raw = _setup()
    inv = {c: p for p, c in cmap.items()}
    name_of = {cmap[p]: rows[p][1] for p in rows}
    is_t = {c: inv[c].endswith("T") for c in inv}
    rep = ["# 第九輪 c 評估輸出（程式產生）", "", "設計：[`protocol.md`](protocol.md)", "", "## 封閉式辨識（54 家名單）", "",
           "| 等級 | 配對正確 | 隨機期望 | 單尾 p | 標準 ≤ 3 |", "|---|---|---|---|---|"]
    passed = None
    for lv in LEVELS:
        path = f"{DATA}/probe/closed_{lv}.json"
        if not os.path.exists(path):
            rep.append(f"| {lv} | – | 1.0 | – | 未執行 |")
            continue
        cl = json.load(open(path))
        hits = [c for c, d in cl.items() if c in name_of and round8._name_hit(d.get("assigned", ""), name_of[c])]
        p = round8.poisson_binomial_tail([1 / 54] * len(cl), len(hits))
        ok = len(hits) <= 3
        if ok and passed is None:
            passed = lv
        rep.append(f"| {lv} | {len(hits)}/{len(cl)} | 1.0 | {p:.3g} | {'通過' if ok else '未通過'} |")
    rep += ["", f"- 通過的最細等級（K 卡）：**{passed or '無'}**", ""]

    def line(name, s):
        pos = [s[c] for c in s if is_t[c]]
        neg = [s[c] for c in s if not is_t[c]]
        if not pos or not neg:
            return f"| {name} | – | – | – |"
        lo, hi = auc_ci(pos, neg)
        w = t = l = 0
        for p in rows:
            if p.endswith("T"):
                a, b = cmap[p], cmap[p[:-1] + "C"]
                if a in s and b in s:
                    w += s[a] > s[b]; t += s[a] == s[b]; l += s[a] < s[b]
        return f"| {name} | {auc(pos, neg):.2f} | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} |"

    counts = json.load(open(f"{DATA}/cards/counts.json"))
    rep += ["## 區分力", "", "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 |", "|---|---|---|---|"]
    j0 = {os.path.basename(f)[:-5]: float(json.load(open(f))["risk_score"]) for f in glob.glob("data/round9/judge/J0/R9-*.json")}
    rep.append(line("參考：J0 完整事實卡（第九輪）", j0))
    for lv in LEVELS:
        files = glob.glob(f"{DATA}/judge/{lv}/R9-*.json")
        if files:
            raw_j = {os.path.basename(f)[:-5]: json.load(open(f)) for f in files}
            rep.append(line(f"J0-K（{lv} 卡，LLM 評分）", {c: float(d["risk_score"]) for c, d in raw_j.items()}))
            kn = sum(str(d.get("knows_later_problems")).lower() == "true" for d in raw_j.values())
            gs = sum(bool(d.get("guess")) for d in raw_j.values())
            rep_k = f"- {lv} 評分者自述知道後來有問題：{kn}/{len(raw_j)}；有猜名稱：{gs}/{len(raw_j)}"
        else:
            rep_k = None
        if rep_k:
            rep.append("")
            rep.append(rep_k)
            rep += ["", "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 |", "|---|---|---|---|"]
    rep.append(line("程式：揭露紅旗總數（L3）", {c: v["disclosure_total"] for c, v in counts.items()}))
    rep.append(line("程式：揭露紅旗總數 + 數字訊號數", {c: v["disclosure_total"] + v["numeric"] for c, v in counts.items()}))
    mem = {}
    for m in json.load(open("data/round9/probe/memory.json")):
        for p in rows:
            if m["company"].startswith(rows[p][1]):
                mem[cmap[p]] = float(m["risk_score"])
    rep.append(line("參考：MEM 只有名稱", mem))
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/evaluation.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["cards", "evaluate"])
    globals()[ap.parse_args().cmd](None)


if __name__ == "__main__":
    main()

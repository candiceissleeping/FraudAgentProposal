"""Round 9e: L3 cards on the out-of-time 4.02 sample + memory partial correlations (results/round9e/protocol.md).

  python -m experiment.edgar_risk.round9e   -> results/round9e/evaluation.md
"""
import csv
import glob
import json
import math
import os
import random

from . import round9
from .round3 import auc, auc_ci


def _rank(v):
    o = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(v):
        j = i
        while j + 1 < len(v) and v[o[j + 1]] == v[o[i]]:
            j += 1
        for k in range(i, j + 1):
            r[o[k]] = (i + j) / 2
        i = j + 1
    return r


def _corr(a, b):
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    den = math.sqrt(sum((x - ma) ** 2 for x in a) * sum((y - mb) ** 2 for y in b))
    return sum((x - ma) * (y - mb) for x, y in zip(a, b)) / den if den else 0.0


def partial(y, x, z):
    """Spearman partial correlation of y and x controlling for z."""
    ry, rx, rz = _rank(y), _rank(x), _rank(z)
    a, b, c = _corr(ry, rx), _corr(ry, rz), _corr(rx, rz)
    d = math.sqrt(max((1 - b * b) * (1 - c * c), 1e-12))
    return (a - b * c) / d


def boot_partial(y, x, z, n=2000, seed=7):
    rng = random.Random(seed)
    idx = list(range(len(y)))
    out = []
    for _ in range(n):
        s = [rng.choice(idx) for _ in idx]
        out.append(partial([y[i] for i in s], [x[i] for i in s], [z[i] for i in s]))
    out.sort()
    return partial(y, x, z), out[int(0.025 * n)], out[int(0.975 * n) - 1]


def _scores(pattern):
    return {os.path.basename(f)[:-5]: float(json.load(open(f))["risk_score"]) for f in glob.glob(pattern)}


def main():
    rep = ["# 第九輪 e 評估輸出（程式產生）", "", "設計：[`protocol.md`](protocol.md)", ""]
    # ---- E1/E2: round 9 (4.02, out-of-time) L3 cards
    cmap = round9.code_map()
    inv = {c: p for p, c in cmap.items()}
    rows = {r[0]: r for r in round9._rows()}
    is_t = {c: inv[c].endswith("T") for c in inv}
    raw = {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob("data/round9c/judge/L3/R9-*.json")}
    l3 = {c: float(d["risk_score"]) for c, d in raw.items()}

    def line(name, s):
        pos = [s[c] for c in s if is_t[c]]
        neg = [s[c] for c in s if not is_t[c]]
        lo, hi = auc_ci(pos, neg)
        w = t = l = 0
        for p in rows:
            if p.endswith("T"):
                a, b = cmap[p], cmap[p[:-1] + "C"]
                if a in s and b in s:
                    w += s[a] > s[b]; t += s[a] == s[b]; l += s[a] < s[b]
        return f"| {name} | {auc(pos, neg):.2f} | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} | {len(pos)}+{len(neg)} |"

    rep += ["## E1 / E2：4.02 時間外樣本（27 對）", "", "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | n |", "|---|---|---|---|---|"]
    if l3:
        rep.append(line("**E1 J0-L3（只有紅旗總數，LLM 評分）**", l3))
    rep.append(line("參考：J0-L2（類別計數卡）", _scores("data/round9c/judge/L2/R9-*.json")))
    rep.append(line("參考：J0 完整事實卡", _scores("data/round9/judge/J0/R9-*.json")))
    cnt = json.load(open("data/round9c/cards/counts.json"))
    rep.append(line("參考：程式數紅旗（不用 LLM）", {c: v["disclosure_total"] + v["numeric"] for c, v in cnt.items()}))
    if raw:
        kn = sum(str(d.get("knows_later_problems")).lower() == "true" for d in raw.values())
        gs = sum(bool(d.get("guess")) for d in raw.values())
        rep += ["", f"- E2 J0-L3 自述知道後來有問題：**{kn}/{len(raw)}**；有猜名稱：{gs}/{len(raw)}",
                "- L3 卡給名單的封閉式辨識（第九輪 c）：1/54"]

    # ---- E3: memory partial correlations on the AAER sample (post hoc)
    key = json.load(open("data/round9d/cards/key.json"))
    cnt9d = json.load(open("data/round9d/cards/counts.json"))
    mem = {r["company"].upper(): float(r["risk_score"]) for r in csv.DictReader(open("results/round8/scores_MEM.csv"))}
    for m in json.load(open("data/round9b/probe/memory.json")):
        mem[m["company"].split(" — ")[0].upper()] = float(m["risk_score"])
    M = {}
    for c, v in key.items():
        n = v["name"].upper()
        k = next((x for x in mem if x.startswith(n) or n.startswith(x)), None)
        if k:
            M[c] = mem[k]
    rep += ["", "## E3：分數裡有沒有記憶（AAER 16 對；事後分析）", "",
            "記憶分數 MEM = 只給公司名稱與年度、不給任何年報時的風險分數（第八輪、9b 探針）。",
            "若評分只用卡片內容，控制卡片紅旗數後，分數與 MEM 應無關（偏相關 ≈ 0）。", "",
            "| 評分條件 | 與紅旗數 ρ | 與 MEM ρ | **偏相關（分數, MEM \\| 紅旗數）** | 95% CI |", "|---|---|---|---|---|"]
    cs = sorted(c for c in M if c in cnt9d)
    count = [cnt9d[c]["disclosure_total"] + cnt9d[c]["numeric"] for c in cs]
    mm = [M[c] for c in cs]
    for label, d in (("J0-L2（無名稱）", "L2"), ("J0-L3（無名稱）", "L3"), ("J1-L2（有名稱）", "L2N")):
        s = _scores(f"data/round9d/judge/{d}/A-*.json")
        y = [s[c] for c in cs]
        est, lo, hi = boot_partial(y, mm, count)
        rep.append(f"| {label} | {_corr(_rank(y), _rank(count)):.2f} | {_corr(_rank(y), _rank(mm)):.2f} | **{est:+.2f}** | {lo:+.2f} 至 {hi:+.2f} |")
    rep.append(f"\n- 紅旗數與 MEM 本身的 ρ = {_corr(_rank(count), _rank(mm)):.2f}（記得出事的公司，年報裡紅旗也多）")
    os.makedirs("results/round9e", exist_ok=True)
    open("results/round9e/evaluation.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


if __name__ == "__main__":
    main()

"""Round 9d: L2 category-count cards on 16 AAER pairs (results/round9d/protocol.md).

Commands
  cards     data/round9d/cards/A-xx_L2.txt, A-xx_L2N.txt (with name), probe_closed.txt, key.json
  evaluate  results/round9d/evaluation.md
"""
import argparse
import csv
import glob
import json
import os
import random

from . import round8, round9, round9c
from .round3 import auc, auc_ci

DATA = "data/round9d"
OUT = "results/round9d"
SEED = 20261103
POST_CUTOFF = {"Latch", "Travel + Leisure Co.", "The Bancorp, Inc."}


def _items():
    """[(pair, group, name, period, sic, facts, raw)] for the 16 AAER pairs."""
    out = []
    facts8 = json.load(open("results/round8/facts_verified.json"))
    raw7 = {r["pid"]: r for r in csv.DictReader(open("results/round7/financial_features.csv"))}
    cm8 = round8.code_map()
    for pid, name, cik, a0, p0, a1, p1, group, sic in round8._pairs():
        out.append((f"D{pid[1:3]}", pid[-1], name, str(p0), str(sic), facts8[cm8[pid]], raw7.get(pid, {})))
    saved = round9.DATA, round9.OUT, round9.PREFIX
    round9.DATA, round9.OUT, round9.PREFIX = "data/round9b", "results/round9b", "R9B"
    try:
        cm = round9.code_map()
        rows = round9._rows()
    finally:
        round9.DATA, round9.OUT, round9.PREFIX = saved
    facts9b = json.load(open("results/round9b/facts_verified.json"))
    raw9b = {r["pid"]: r for r in csv.DictReader(open("results/round9b/financial_features.csv"))}
    n = 15
    for i in (2, 3):  # 9b P01 (Latch) is the same 10-K as round 8 P01
        for tag in ("T", "C"):
            pid = f"P{i:02d}{tag}"
            r = next(x for x in rows if x[0] == pid)
            out.append((f"D{n:02d}", tag, r[1], r[4], r[8], facts9b[cm[pid]], raw9b.get(pid, {})))
        n += 1
    return out


def cards(args):
    items = _items()
    rng = random.Random(SEED)
    order = list(range(len(items)))
    rng.shuffle(order)
    os.makedirs(f"{DATA}/cards", exist_ok=True)
    key = {}
    for k, idx in enumerate(order, 1):
        code = f"A-{k:02d}"
        pair, tag, name, period, sic, f, raw = items[idx]
        p = str(period).replace("-", "")
        key[code] = {"pair": pair, "group": tag, "name": name, "period": p, "post_cutoff_aaer": name in POST_CUTOFF and tag == "T"}
        body = round9c.l2_text(code, f, raw)
        open(f"{DATA}/cards/{code}_L2.txt", "w").write(body)
        label = f"{name} (fiscal year ending {p[:4]}-{p[4:6]}-{p[6:]})"
        open(f"{DATA}/cards/{code}_L2N.txt", "w").write(body.replace(f"FACT CARD {code}\n", f"FACT CARD {code}\nCompany: {label}\n", 1))
    json.dump(key, open(f"{DATA}/cards/key.json", "w"), indent=1)
    names = sorted(v["name"].upper() for v in key.values())  # uniform case: no case-vs-control cue
    allc = "\n\n".join(open(f"{DATA}/cards/{c}_L2.txt").read() for c in sorted(key))
    open(f"{DATA}/cards/probe_closed.txt", "w").write(
        "CANDIDATE COMPANIES (each fact card below belongs to exactly one of these; fiscal years 2017-2024):\n"
        + "\n".join(f"- {n}" for n in names) + "\n\n" + allc)
    print("cards", len(key))


def evaluate(args):
    key = json.load(open(f"{DATA}/cards/key.json"))
    is_t = {c: v["group"] == "T" for c, v in key.items()}
    rep = ["# 第九輪 d 評估輸出（程式產生）", "", "設計：[`protocol.md`](protocol.md)", "", "## D1 封閉式辨識（32 家名單）", ""]
    ok1 = True
    for f in sorted(glob.glob(f"{DATA}/probe/closed_*.json")):
        cl = json.load(open(f))
        hits = [key[c]["name"] for c, d in cl.items() if c in key and round8._name_hit(d.get("assigned", ""), key[c]["name"])]
        p = round8.poisson_binomial_tail([1 / 32] * len(cl), len(hits))
        ok1 &= len(hits) <= 3
        rep.append(f"- {os.path.basename(f)}：**{len(hits)}/{len(cl)}**（隨機期望 1.0，單尾 p = {p:.3g}）{hits}")
    rep.append(f"- D1 判定（兩次都 ≤ 3）：{'通過' if ok1 else '未通過'}")
    files_b = sorted(glob.glob(f"{DATA}/probe_L2b/closed_*.json"))
    if files_b:
        rep += ["", "## 9d-b L2b 卡（不顯示可計算項數）封閉式辨識", ""]
        okb = True
        for f in files_b:
            cl = json.load(open(f))
            hits = [key[c]["name"] for c, d in cl.items() if c in key and round8._name_hit(d.get("assigned", ""), key[c]["name"])]
            p = round8.poisson_binomial_tail([1 / 32] * len(cl), len(hits))
            okb &= len(hits) <= 3
            rep.append(f"- {os.path.basename(f)}：**{len(hits)}/{len(cl)}**（隨機期望 1.0，單尾 p = {p:.3g}）{hits}")
        rep.append(f"- 判定（兩次都 ≤ 3）：{'通過' if okb else '未通過'}")
    # D2: round 9 L2 replicates
    saved = round9.DATA, round9.OUT, round9.PREFIX
    round9.DATA, round9.OUT, round9.PREFIX = "data/round9", "results/round9", "R9"
    try:
        cm9 = round9.code_map()
        rows9 = {r[0]: r for r in round9._rows()}
    finally:
        round9.DATA, round9.OUT, round9.PREFIX = saved
    name9 = {cm9[p]: rows9[p][1] for p in rows9}
    rep += ["", "## D2 第九輪 L2 封閉式辨識重複", ""]
    runs = []
    for f in sorted(glob.glob("data/round9c/probe/closed_L2*.json")):
        cl = json.load(open(f))
        h = sum(1 for c, d in cl.items() if c in name9 and round8._name_hit(d.get("assigned", ""), name9[c]))
        runs.append(h)
        rep.append(f"- {os.path.basename(f)}：{h}/{len(cl)}")
    if runs:
        rep.append(f"- 平均 {sum(runs) / len(runs):.2f}/54（標準 ≤ 3）：{'通過' if sum(runs) / len(runs) <= 3 else '未通過'}")

    def load(cond):
        return {os.path.basename(f)[:-5]: json.load(open(f)) for f in glob.glob(f"{DATA}/judge/{cond}/A-*.json")}

    j0raw, j1raw = load("L2"), load("L2N")
    j0 = {c: float(d["risk_score"]) for c, d in j0raw.items()}
    j1 = {c: float(d["risk_score"]) for c, d in j1raw.items()}

    def line(name, s, keep=None):
        cs = [c for c in s if keep is None or keep(c)]
        pos = [s[c] for c in cs if is_t[c]]
        neg = [s[c] for c in cs if not is_t[c]]
        if not pos or not neg:
            return f"| {name} | – | – | – |"
        lo, hi = auc_ci(pos, neg)
        w = t = l = 0
        pairs = {}
        for c in cs:
            pairs.setdefault(key[c]["pair"], {})[key[c]["group"]] = s[c]
        for v in pairs.values():
            if "T" in v and "C" in v:
                w += v["T"] > v["C"]; t += v["T"] == v["C"]; l += v["T"] < v["C"]
        return f"| {name} | {auc(pos, neg):.2f} | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} |"

    pre = {k["pair"] for k in key.values() if k["post_cutoff_aaer"]}
    rep += ["", "## D3–D5 評分", "", "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 |", "|---|---|---|---|"]
    rep.append(line("D4 J0-L2（L2 卡，無名稱），16 對", j0))
    rep.append(line("J0-L2，只看截止前 AAER（13 對）", j0, lambda c: key[c]["pair"] not in pre))
    rep.append(line("J1-L2（L2 卡 + 真實名稱），16 對", j1))
    rep.append(line("J1-L2，只看截止前 AAER（13 對）", j1, lambda c: key[c]["pair"] not in pre))
    kn0 = [key[c]["name"] for c, d in j0raw.items() if str(d.get("knows_later_problems")).lower() == "true"]
    gs0 = [d.get("guess") for d in j0raw.values() if d.get("guess")]
    kn1 = [key[c]["name"] for c, d in j1raw.items() if str(d.get("knows_later_problems")).lower() == "true"]
    rep += ["", f"- D3 J0-L2 自述知道後來有問題：**{len(kn0)}/{len(j0raw)}** {kn0}；有猜名稱：{len(gs0)} {gs0}",
            f"- 對照：J1-L2（看得到名稱）自述知道後來有問題：{len(kn1)}/{len(j1raw)}（問題組 {sum(is_t[c] for c, d in j1raw.items() if str(d.get('knows_later_problems')).lower() == 'true')}）"]
    for label, keep in (("16 對", lambda c: True), ("截止前 13 對", lambda c: key[c]["pair"] not in pre)):
        mei = round9._boot_mei({c: v for c, v in j0.items() if keep(c)}, {c: v for c, v in j1.items() if keep(c)}, is_t)
        if mei:
            rep.append(f"- D5 記憶效應指數（{label}）：問題組 {mei[3]:+.1f}，對照組 {mei[4]:+.1f} → **{mei[0]:+.1f}**（95% CI {mei[1]:+.1f} 至 {mei[2]:+.1f}）")
    rep += ["", "## 逐卡", "", "| 卡 | 配對 | 組 | 公司 | 截止後 AAER | J0-L2 | J1-L2 | J1 知道 |", "|---|---|---|---|---|---|---|---|"]
    for c in sorted(key):
        k = key[c]
        rep.append(f"| {c} | {k['pair']} | {'問題' if k['group'] == 'T' else '對照'} | {k['name']} | {'是' if k['post_cutoff_aaer'] else ''} | "
                   f"{j0.get(c, '')} | {j1.get(c, '')} | {j1raw.get(c, {}).get('knows_later_problems', '')} |")
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/evaluation.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["cards", "evaluate"])
    globals()[ap.parse_args().cmd](None)


if __name__ == "__main__":
    main()

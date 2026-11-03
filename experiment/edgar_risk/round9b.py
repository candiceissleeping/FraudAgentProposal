"""Round 9b: post-cutoff AAER cases (results/round9b/protocol.md), same pipeline as round 9.

Commands
  cases     write results/round9b/cases.json (the 3 pre-registered AAER issuers)
  controls / build / xbrl / verify / cards / memory_list   -> round9 functions on data/round9b, codes R9B-xx
  evaluate  results/round9b/evaluation.md (+ round 9 closed-set re-identification)
"""
import argparse
import json
import os
from collections import defaultdict

from . import round8, round9

round9.DATA = DATA = "data/round9b"
round9.OUT = OUT = "results/round9b"
round9.PREFIX = "R9B"

# Pre-registered (protocol §1.1): AAER released 2026-07-01..10-31, issuer files 10-K, Y0 = first original 10-K
# in the misstated period.
CASES = [
    dict(name="Latch, Inc.", cik="1826000", aaer="AAER-4604", aaer_date="20261001", y0_acc="0001826000-22-000020",
         y0_period="20211231", y0_doc="lat-20211231.htm", y1_acc="0001193125-21-083025", y1_period="20201231"),
    dict(name="Travel + Leisure Co.", cik="1361658", aaer="AAER-4603", aaer_date="20260930",
         y0_acc="0001361658-20-000012", y0_period="20191231", y0_doc="wynd-20191231x10k.htm",
         y1_acc="0001361658-19-000009", y1_period="20181231"),
    dict(name="The Bancorp, Inc.", cik="1295401", aaer="AAER-4599", aaer_date="20260903",
         y0_acc="0001562762-25-000040", y0_period="20241231", y0_doc="tbbk-20241231x10k.htm",
         y1_acc="0001562762-24-000049", y1_period="20231231"),
]


def cases(args):
    os.makedirs(OUT, exist_ok=True)
    out = []
    for c in CASES:
        s = round9.submissions(c["cik"])
        out.append(dict(c, sic=s.get("sic", ""), event_acc="", event_date=c["aaer_date"]))
    json.dump(out, open(f"{OUT}/cases.json", "w"), indent=1)
    print([(c["name"], c["sic"]) for c in out])


def controls(args):
    # exclude every round 9 firm and the AAER issuers themselves (protocol §1.2)
    used = set()
    for p in json.load(open("results/round9/pairs.json")):
        used |= {p["case"]["cik"], p["control"]["cik"]}
    round9.EXCLUDE_CIKS = used | {c["cik"] for c in CASES}
    round9.controls(args)


def _closed_probe(rep):
    """Protocol §3: round 9 closed-set re-identification."""
    path = "data/round9/probe/closed.json"
    if not os.path.exists(path):
        return
    round9.DATA, round9.OUT, round9.PREFIX = "data/round9", "results/round9", "R9"
    try:
        cmap = round9.code_map()
        inv = {c: p for p, c in cmap.items()}
        rows = {r[0]: r for r in round9._rows()}
    finally:
        round9.DATA, round9.OUT, round9.PREFIX = DATA, OUT, "R9B"
    name_of = {cmap[p]: rows[p][1] for p in rows}
    is_t = {c: inv[c].endswith("T") for c in inv}
    cl = json.load(open(path))
    hits = [c for c, d in cl.items() if c in name_of and round8._name_hit(d.get("assigned", ""), name_of[c])]
    secs = defaultdict(int)
    for p in rows:
        secs[round8.sector(rows[p][8])] += 1
    ps = [1 / secs[round8.sector(rows[inv[c]][8])] for c in cl if c in inv]
    p_val = round8.poisson_binomial_tail(ps, len(hits))
    partner = {}
    for p in rows:
        other = p[:-1] + ("C" if p.endswith("T") else "T")
        partner[cmap[p]] = name_of[cmap[other]]
    pair_ok = sum(1 for c, d in cl.items() if c in name_of and (round8._name_hit(d.get("assigned", ""), name_of[c])
                                                                 or round8._name_hit(d.get("assigned", ""), partner[c])))
    t_names = {name_of[c] for c in name_of if is_t[c]}
    same_grp = sum(1 for c, d in cl.items() if c in name_of and
                   (any(round8._name_hit(d.get("assigned", ""), n) for n in t_names) == is_t[c]))
    mem = {m["company"]: m for m in json.load(open("data/round9/probe/memory.json"))}
    known = [name_of[c] for c in hits if any(k.startswith(name_of[c]) and str(m.get("knows_later_problems")).lower() == "true"
                                             for k, m in mem.items())]
    rep += ["", "## 9b-B 第九輪封閉式辨識（54 家名單 + 54 張 J0 卡）", "",
            f"- 配對正確：**{len(hits)}/{len(cl)}**（只靠產業大類隨機猜的期望 {sum(ps):.1f}，單尾 p = {p_val:.3g}）",
            f"  - 問題組 {sum(is_t[c] for c in hits)}/27，對照組 {sum(not is_t[c] for c in hits)}/27",
            f"- 指派到正確配對（本身或配對公司）：{pair_ok}/{len(cl)}",
            f"- 指派的公司與卡片同組（問題／對照）：{same_grp}/{len(cl)}",
            f"- 配對正確者中，MEM 說知道後來有問題：{len(known)} {known}",
            f"- 配對正確的卡：{sorted(name_of[c] for c in hits)}"]


def evaluate(args):
    rep = ["# 第九輪 b 評估輸出（程式產生）", "", "設計：[`protocol.md`](protocol.md)", ""]
    cmap = round9.code_map()
    inv = {c: p for p, c in cmap.items()}
    rows = {r[0]: r for r in round9._rows()}
    j0raw, j1raw = round9._load_judge("J0"), round9._load_judge("J1")
    mem = json.load(open(f"{DATA}/probe/memory.json")) if os.path.exists(f"{DATA}/probe/memory.json") else []
    memd = {}
    for m in mem:
        for p in rows:
            if m["company"].startswith(rows[p][1]):
                memd[cmap[p]] = m
    rep += ["## 9b-A AAER 時間外案例", "",
            "| 配對 | 組 | 公司 | Y0 | A1(a) 知道會計問題 | A1(b) 知道 SEC 執法 | MEM 分數 | J0 | J1 | J0 自述知道 |",
            "|---|---|---|---|---|---|---|---|---|---|"]
    a1b = a1a = 0
    wins = []
    for i in range(1, len(rows) // 2 + 1):
        t, c = f"P{i:02d}T", f"P{i:02d}C"
        for p in (t, c):
            code = cmap[p]
            m = memd.get(code, {})
            ka = str(m.get("knows_accounting_problems")).lower() == "true"
            kb = str(m.get("knows_sec_enforcement")).lower() == "true"
            if p == t:
                a1a += ka
                a1b += kb
            j0 = j0raw.get(code, {}).get("risk_score", "")
            j1 = j1raw.get(code, {}).get("risk_score", "")
            kj = j0raw.get(code, {}).get("knows_later_problems", "")
            rep.append(f"| P{i:02d} | {'問題' if p == t else '對照'} | {rows[p][1]} | {rows[p][4][:4]} | {'是' if ka else '否'} | "
                       f"{'是' if kb else '否'} | {m.get('risk_score', '')} | {j0} | {j1} | {kj} |")
        if cmap[t] in j0raw and cmap[c] in j0raw:
            a, b = float(j0raw[cmap[t]]["risk_score"]), float(j0raw[cmap[c]]["risk_score"])
            wins.append("勝" if a > b else "平" if a == b else "負")
    n = len(rows) // 2
    rep += ["", f"- A1(b) 問題組知道 SEC 執法：**{a1b}/{n}**（標準 0/{n}）",
            f"- A1(a) 問題組知道該期間有會計問題或重編：{a1a}/{n}",
            f"- A2 J0 自述知道後來有問題：{sum(str(d.get('knows_later_problems')).lower() == 'true' for d in j0raw.values())}/{len(j0raw)}"]
    import glob
    opens = {}
    for f in glob.glob(f"{DATA}/probe/open_*.json"):
        opens.update(json.load(open(f)))
    if opens:
        name_of = {cmap[p]: rows[p][1] for p in rows}
        hits = [c for c, d in opens.items() if c in name_of and any(round8._name_hit(g, name_of[c]) for g in d.get("guesses", []))]
        rep.append(f"- A2 開放式辨識猜中：{len(hits)}/{len(opens)} {[name_of[c] for c in hits]}")
    rep.append(f"- A3 J0 組內（問題 vs 對照）：{' / '.join(wins)}")
    _closed_probe(rep)
    open(f"{OUT}/evaluation.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["cases", "controls", "build", "xbrl", "verify", "cards", "memory_list", "evaluate"])
    args = ap.parse_args()
    fn = globals().get(args.cmd) if args.cmd in ("cases", "controls", "evaluate") else getattr(round9, args.cmd)
    fn(args)


if __name__ == "__main__":
    main()

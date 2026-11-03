"""Round 9f: expand the AAER sample with 2017-2022 releases (results/round9f/protocol.md).

Commands
  cases     screening outputs -> results/round9f/cases.json (+ selection log)
  controls / build / xbrl / verify  -> round9 functions on data/round9f, codes R9F-xx
  cards     L3 cards + closed-set probe input (data/round9f/cards/)
  evaluate  results/round9f/evaluation.md (pooled with round 9d AAER pairs)
"""
import argparse
import csv
import glob
import json
import os
import random
import re
import urllib.parse

from . import round8, round9, round9c
from .round3 import auc, auc_ci

round9.DATA = DATA = "data/round9f"
round9.OUT = OUT = "results/round9f"
round9.PREFIX = "R9F"
round9.DEEP = True
SEED = 20261104


_LOOKUP = None


def _norm(n):
    n = re.sub(r"[^A-Z0-9 ]", " ", n.upper().replace("&", " AND "))
    n = re.sub(r"\b(INC|INCORPORATED|CORP|CORPORATION|CO|COMPANY|LTD|LIMITED|LLC|LP|L P|PLC|HOLDINGS|HOLDING|THE|DE|NEW)\b", " ", n)
    return re.sub(r"\s+", " ", n).strip()


def _cik(name):
    """Name -> CIK via SEC cik-lookup-data.txt (current and former names), normalised exact match."""
    global _LOOKUP
    if _LOOKUP is None:
        _LOOKUP = {}
        for line in open(f"{DATA}/cik-lookup-data.txt", encoding="latin-1"):
            parts = line.rstrip("\n").rsplit(":", 2)
            if len(parts) == 3:
                _LOOKUP.setdefault(_norm(parts[0]), []).append(parts[1].lstrip("0"))
    cands = _LOOKUP.get(_norm(name), [])
    for cik in cands:  # first candidate that actually files 10-Ks
        try:
            ks, _ = round9.tenks(cik)
        except Exception:
            continue
        if ks:
            return cik
    return None


def cases(args):
    screened = {}
    for f in sorted(glob.glob(f"{DATA}/screen/out_*.json")):
        screened.update(json.load(open(f)))
    ok, log = [], []
    for aaer, d in sorted(screened.items()):
        name = d.get("issuer", "")
        if not d.get("us_10k_filer"):
            log.append((aaer, name, "not a 10-K filer")); continue
        if not d.get("fs_misstatement"):
            log.append((aaer, name, "no annual financial statement misstatement")); continue
        years = sorted(int(y) for y in d.get("misstated_fiscal_years", []) if str(y).isdigit())
        if not years:
            log.append((aaer, name, "misstated years not determinable")); continue
        cik = _cik(name)
        if not cik:
            log.append((aaer, name, "CIK not found")); continue
        ks, s = round9.tenks(cik)
        ks = sorted(ks, key=lambda x: x["period"])

        def fy(k):
            y, m = int(k["period"][:4]), int(k["period"][4:6])
            return y - 1 if m <= 3 else y

        pick = None
        for y in years:
            for i, k in enumerate(ks):
                if fy(k) == y and k["xbrl"] and i > 0:
                    pick = (k, ks[i - 1]); break
            if pick:
                break
        if not pick:
            log.append((aaer, name, f"no original XBRL 10-K for misstated years {years}")); continue
        y0, y1 = pick
        ok.append(dict(name=s.get("name", name), cik=cik, sic=s.get("sic", ""), aaer=aaer, event_acc="", event_date="",
                       y0_acc=y0["acc"], y0_period=y0["period"], y0_doc=y0["doc"], y1_acc=y1["acc"], y1_period=y1["period"]))
    rng = random.Random(SEED)
    chosen = ok if len(ok) <= 30 else rng.sample(ok, 30)
    os.makedirs(OUT, exist_ok=True)
    json.dump(chosen, open(f"{OUT}/cases.json", "w"), indent=1)
    with open(f"{OUT}/case_selection_log.tsv", "w") as fh:
        for a, n, why in log:
            fh.write(f"{a}\t{n}\t{why}\n")
    print(len(screened), "screened;", len(ok), "eligible;", len(chosen), "chosen")


def controls(args):
    used = set()
    for path in ("results/round9/pairs.json", "results/round9b/pairs.json"):
        for p in json.load(open(path)):
            used |= {str(p["case"]["cik"]), str(p["control"]["cik"])}
    for r in round8._pairs():
        used.add(str(r[2]))
    for c in json.load(open(f"{OUT}/cases.json")):
        used.add(str(c["cik"]))
    round9.EXCLUDE_CIKS = used
    round9.controls(args)


def cards(args):
    cmap = round9.code_map()
    rows = {r[0]: r for r in round9._rows()}
    facts = json.load(open(f"{OUT}/facts_verified.json"))
    raw = {r["pid"]: r for r in csv.DictReader(open(f"{OUT}/financial_features.csv"))}
    os.makedirs(f"{DATA}/cards", exist_ok=True)
    counts = {}
    for pid, code in cmap.items():
        f, r = facts[code], raw.get(pid, {})
        fc = round9c.facets(f, r)
        disc, num = sum(n for _, n, _ in fc[:-1]), fc[-1][1]
        counts[code] = {"disclosure_total": disc, "numeric": num}
        open(f"{DATA}/cards/{code}_L3.txt", "w").write(
            f"FACT CARD {code}\n\nTotal disclosure red flags (out of 24 possible): {disc}\n"
            f"Numeric warning signals (Beneish M, Dechow F, accruals, cash flow vs income; not computable counts as not triggered): {num} of 4\n")
    json.dump(counts, open(f"{DATA}/cards/counts.json", "w"), indent=1)
    names = sorted(rows[p][1].upper() for p in rows)
    allc = "\n\n".join(open(f"{DATA}/cards/{c}_L3.txt").read() for c in sorted(cmap.values()))
    open(f"{DATA}/cards/probe_closed_L3.txt", "w").write(
        f"CANDIDATE COMPANIES (each fact card below belongs to exactly one of these):\n"
        + "\n".join(f"- {n}" for n in names) + "\n\n" + allc)
    print("cards", len(cmap))


def evaluate(args):
    cmap = round9.code_map()
    inv = {c: p for p, c in cmap.items()}
    rows = {r[0]: r for r in round9._rows()}
    name_of = {cmap[p]: rows[p][1] for p in rows}
    # new pairs (9f)
    new = {}
    for f in glob.glob(f"{DATA}/judge/L3/R9F-*.json"):
        c = os.path.basename(f)[:-5]
        new[c] = (json.load(open(f)), inv[c][:3], inv[c].endswith("T"))
    cnt = json.load(open(f"{DATA}/cards/counts.json"))
    # 9d pairs
    key = json.load(open("data/round9d/cards/key.json"))
    old = {}
    for f in glob.glob("data/round9d/judge/L3/A-*.json"):
        c = os.path.basename(f)[:-5]
        old[c] = (json.load(open(f)), "D" + key[c]["pair"], key[c]["group"] == "T")
    cnt9d = json.load(open("data/round9d/cards/counts.json"))

    def stats(items, score):
        pos = [score(c, d) for c, (d, p, t) in items.items() if t]
        neg = [score(c, d) for c, (d, p, t) in items.items() if not t]
        lo, hi = auc_ci(pos, neg)
        pairs = {}
        for c, (d, p, t) in items.items():
            pairs.setdefault(p, {})[t] = score(c, d)
        w = sum(1 for v in pairs.values() if len(v) == 2 and v[True] > v[False])
        tie = sum(1 for v in pairs.values() if len(v) == 2 and v[True] == v[False])
        n = sum(1 for v in pairs.values() if len(v) == 2)
        return f"{auc(pos, neg):.2f} | {lo:.2f}–{hi:.2f} | {w} / {tie} / {n - w - tie} | {n}"

    llm = lambda c, d: float(d["risk_score"])
    pooled = {**{("9d", c): v for c, v in old.items()}, **{("9f", c): v for c, v in new.items()}}
    cnt_all = {**{("9d", c): v for c, v in cnt9d.items()}, **{("9f", c): v for c, v in cnt.items()}}
    count_score = lambda c, d: cnt_all[c]["disclosure_total"] + cnt_all[c]["numeric"]
    rep = ["# 第九輪 f 評估輸出（程式產生）", "", "設計：[`protocol.md`](protocol.md)", "",
           "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | 對數 |", "|---|---|---|---|---|"]
    rep.append(f"| **F1 合併 AAER（9d + 9f），J0-L3 LLM 評分** | {stats(pooled, lambda c, d: llm(c, d))} |")
    rep.append(f"| 合併 AAER，程式數紅旗 | {stats(pooled, count_score)} |")
    if new:
        rep.append(f"| 只看 9f 新對，J0-L3 | {stats({('9f', c): v for c, v in new.items()}, lambda c, d: llm(c, d))} |")
    rep.append(f"| 只看 9d 的 16 對，J0-L3 | {stats({('9d', c): v for c, v in old.items()}, lambda c, d: llm(c, d))} |")
    kn = [c for c, (d, p, t) in pooled.items() if str(d.get("knows_later_problems")).lower() == "true"]
    gs = [c for c, (d, p, t) in pooled.items() if d.get("guess")]
    rep += ["", f"- F3 J0-L3 自述知道後來有問題：**{len(kn)}/{len(pooled)}**；有猜名稱：{len(gs)}/{len(pooled)}"]
    rep += ["", "## F2 封閉式辨識（9f 新名單）", ""]
    n_cards = len(cmap)
    for f in sorted(glob.glob(f"{DATA}/probe_L3/closed_*.json")):
        cl = json.load(open(f))
        hits = [name_of[c] for c, d in cl.items() if c in name_of and round8._name_hit(d.get("assigned", ""), name_of[c])]
        p = round8.poisson_binomial_tail([1 / n_cards] * len(cl), len(hits))
        rep.append(f"- {os.path.basename(f)}：**{len(hits)}/{len(cl)}**（隨機期望 1.0，單尾 p = {p:.3g}，標準 ≤ 3）{hits}")
    open(f"{OUT}/evaluation.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["cases", "controls", "build", "xbrl", "verify", "cards", "evaluate"])
    a = ap.parse_args()
    fn = globals().get(a.cmd) if a.cmd in ("cases", "controls", "cards", "evaluate") else getattr(round9, a.cmd)
    fn(a)


if __name__ == "__main__":
    main()

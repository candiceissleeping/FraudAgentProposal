"""Round 9g: full unredacted 10-K scored by an LLM on the round-9 out-of-time sample (results/round9g/protocol.md).

  python -m experiment.edgar_risk.round9g build      # download the 54 Y0 10-Ks, unredacted, as data/round9g/raw/G-xx.txt
  python -m experiment.edgar_risk.round9g evaluate   # results/round9g/evaluation.md
"""
import argparse
import gzip
import json
import os
import random
import re

from . import round8, round9
from .round3 import auc, auc_ci
from .round9 import _clean, _get, _rows, doc_lines

DATA = "data/round9g"
OUT = "results/round9g"
SEED = 20261105


def code_map():
    pids = [r[0] for r in _rows()]
    rng = random.Random(SEED)
    rng.shuffle(pids)
    return {pid: f"G-{i:02d}" for i, pid in enumerate(pids, 1)}


def build(args):
    os.makedirs(f"{DATA}/raw", exist_ok=True)
    cmap = code_map()
    for pid, name, cik, a0, p0, a1, p1, group, sic in _rows():
        code = cmap[pid]
        if os.path.exists(f"{DATA}/raw/{code}.txt"):
            continue
        url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{a0.replace('-', '')}/{a0}.txt"
        raw = _get(url).decode("utf-8", errors="ignore")
        parts = []
        for doc in raw.split("<DOCUMENT>")[1:]:
            typ = re.search(r"<TYPE>\s*([^\s<]+)", doc).group(1).upper()
            fname = re.search(r"<FILENAME>\s*([^\s<]+)", doc)
            if not (typ.startswith("10-K") or typ.startswith("EX-13")):
                continue
            if fname and not fname.group(1).lower().endswith((".htm", ".html", ".txt")):
                continue
            doc = re.sub(r"<ix:header>.*?</ix:header>", " ", doc, flags=re.S | re.I)
            parts.append("\n".join(_clean(doc_lines(doc))))
        text = "\n\n".join(parts)
        open(f"{DATA}/raw/{code}.txt", "w", encoding="utf-8").write(text)
        with gzip.open(f"{DATA}/raw/{code}.txt.gz", "wt", encoding="utf-8") as fh:
            fh.write(text)
        print(code, len(text), flush=True)


def _boot_diff(a, b, is_t, n=2000, seed=11):
    """Paired bootstrap (resampling matched pairs) of AUC(a) - AUC(b)."""
    pairs = [(t, c) for t, c in _pair_codes()]
    rng = random.Random(seed)
    out = []
    for _ in range(n):
        s = [rng.choice(pairs) for _ in pairs]
        pa = [a[t] for t, c in s]; na = [a[c] for t, c in s]
        pb = [b[t] for t, c in s]; nb = [b[c] for t, c in s]
        out.append(auc(pa, na) - auc(pb, nb))
    out.sort()
    return out[int(0.025 * n)], out[int(0.975 * n) - 1]


def _pair_codes():
    g = code_map()
    return [(g[p], g[p[:-1] + "C"]) for p in g if p.endswith("T")]


def evaluate(args):
    g = code_map()
    inv = {c: p for p, c in g.items()}
    rows = {r[0]: r for r in _rows()}
    r9 = round9.code_map()
    is_t = {c: inv[c].endswith("T") for c in inv}
    raw = {}
    for c in g.values():
        f = f"{DATA}/judge/{c}.json"
        if os.path.exists(f):
            raw[c] = json.load(open(f))
    rs = {c: float(d["risk_score"]) for c, d in raw.items()}
    j0 = {g[p]: float(json.load(open(f"data/round9/judge/J0/{r9[p]}.json"))["risk_score"]) for p in g}
    mem = {}
    for m in json.load(open("data/round9/probe/memory.json")):
        pid = next((p for p in rows if m["company"].startswith(rows[p][1])), None)
        if pid:
            mem[g[pid]] = float(m["risk_score"])
    pairs = _pair_codes()

    def line(name, s, keep=None):
        cs = [c for c in s if keep is None or keep(c)]
        pos = [s[c] for c in cs if is_t[c]]
        neg = [s[c] for c in cs if not is_t[c]]
        lo, hi = auc_ci(pos, neg)
        w = t = l = 0
        for a, b in pairs:
            if a in cs and b in cs:
                w += s[a] > s[b]; t += s[a] == s[b]; l += s[a] < s[b]
        return f"| {name} | {auc(pos, neg):.2f} | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} | {len(pos)}+{len(neg)} |"

    rep = ["# 第九輪 g 評估輸出（程式產生）", "", "設計：[`protocol.md`](protocol.md)", "",
           f"完成評分：{len(raw)}/54", "", "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | n |", "|---|---|---|---|---|"]
    rep.append(line("**G1 RAW：整份 10-K，不遮蔽**", rs))
    rep.append(line("參考：J0 事實卡（第九輪）", j0))
    rep.append(line("參考：MEM 只給名稱（第九輪）", mem))
    if len(rs) == 54:
        lo, hi = _boot_diff(rs, j0, is_t)
        d = auc([rs[a] for a, b in pairs], [rs[b] for a, b in pairs]) - auc([j0[a] for a, b in pairs], [j0[b] for a, b in pairs])
        rep += ["", f"- **G2 RAW − J0 的 AUC 差：{d:+.2f}（配對 bootstrap 95% CI {lo:+.2f} 至 {hi:+.2f}）**"]
    kt = [c for c, d in raw.items() if is_t[c] and str(d.get("knows_later_problems")).lower() == "true"]
    kc = [c for c, d in raw.items() if not is_t[c] and str(d.get("knows_later_problems")).lower() == "true"]
    rec = [c for c, d in raw.items() if str(d.get("recognised_company")).lower() == "true"]
    hit = [c for c, d in raw.items() if round8._name_hit(d.get("company_name_guess", ""), rows[inv[c]][1])]
    rep += [f"- G3 自述知道後來有問題：問題組 {len(kt)}/27，對照組 {len(kc)}/27 {[rows[inv[c]][1] for c in kt + kc]}",
            f"- G4 自述認得公司：{len(rec)}/{len(raw)}；名稱猜中：{len(hit)}/{len(raw)}"]
    known_pairs = set()
    for a, b in pairs:
        if a in kt:
            known_pairs |= {a, b}
    if known_pairs:
        rep += ["", "| 敏感度 | AUC | 95% CI | 組內勝 / 平 / 負 | n |", "|---|---|---|---|---|",
                line("RAW，排除問題組自述知道的配對", rs, lambda c: c not in known_pairs)]
    both = [c for c in rs if c in mem]
    x = [mem[c] for c in both]; y = [rs[c] for c in both]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    beta = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    resid = {c: rs[c] - (my + beta * (mem[c] - mx)) for c in both}
    yj = [j0[c] for c in both]
    myj = sum(yj) / len(yj)
    bj = sum((a - mx) * (b - myj) for a, b in zip(x, yj)) / sum((a - mx) ** 2 for a in x)
    residj = {c: j0[c] - (myj + bj * (mem[c] - mx)) for c in both}
    rep += ["", "| G5 扣除 MEM 線性部分後的殘差 | AUC | 95% CI | 組內勝 / 平 / 負 | n |", "|---|---|---|---|---|",
            line("RAW 殘差", resid), line("J0 殘差（參考）", residj), "",
            f"- Spearman ρ：RAW vs J0 = {round8.spearman([rs[c] for c in both], [j0[c] for c in both]):.2f}；"
            f"RAW vs MEM = {round8.spearman(y, x):.2f}；J0 vs MEM = {round8.spearman(yj, x):.2f}"]
    rep += ["", "## 逐對", "", "| 配對 | 問題公司 | RAW | J0 | MEM | 對照公司 | RAW | J0 | MEM |", "|---|---|---|---|---|---|---|---|---|"]
    for a, b in sorted(pairs, key=lambda t: inv[t[0]]):
        rep.append(f"| {inv[a][:3]} | {rows[inv[a]][1]} | {rs.get(a, '–')} | {j0[a]:.0f} | {mem.get(a, float('nan')):.0f} | "
                   f"{rows[inv[b]][1]} | {rs.get(b, '–')} | {j0[b]:.0f} | {mem.get(b, float('nan')):.0f} |")
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/evaluation.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["build", "evaluate"])
    a = ap.parse_args()
    {"build": build, "evaluate": evaluate}[a.cmd](a)


if __name__ == "__main__":
    main()

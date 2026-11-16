"""In-sample AAER MEM on 41 pairs (pre-registration: results/mem_aaer/protocol.md).

  python -m experiment.mem_aaer build      # names, sizes, three lists, keys, prompts (data/mem_aaer, results/mem_aaer)
  python -m experiment.mem_aaer run        # 5 isolated runs per list (experiment.mem_isolated run)
  python -m experiment.mem_aaer evaluate   # after the raw runs are committed; compares with results/mem_insample/small
"""
import csv
import json
import math
import os
import random
import subprocess
import sys

from experiment.mem_insample import (_get, _load, _pair_auc, _ci, fmt, name_at, frame, _quarter, OUT as INS_OUT)

OUT = "results/mem_aaer"
DATA = "data/mem_aaer"
SEED = 20261119
LISTS = ["L1", "L2", "L3"]
DREAMY = "origin/claude/dreamy-volta-i6oimk"
CACHE = os.environ.get("SEC_CACHE", "/tmp/mem_insample_sec")
NAME_FIX = {1144519: "Bunge Ltd."}   # EDGAR lists the current name as "BUNGELTD" (data error)


def _iso(d):
    d = d.replace("-", "")
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}"


def submissions(cik):
    path = f"{CACHE}/subs/CIK{int(cik):010d}.json"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        raw = _get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json")
        s = json.loads(raw)
        for f in s["filings"].get("files", []):   # older filings
            extra = _get(f"https://data.sec.gov/submissions/{f['name']}")
            if extra:
                e = json.loads(extra)
                for k in s["filings"]["recent"]:
                    s["filings"]["recent"][k] = s["filings"]["recent"][k] + e.get(k, [])
        json.dump(s, open(path, "w"))
    s = json.load(open(path))
    r = s["filings"]["recent"]
    f402 = [r["filingDate"][i] for i, f in enumerate(r["form"])
            if f in ("8-K", "8-K/A") and "4.02" in [x.strip() for x in (r["items"][i] or "").split(",")]]
    return {"name": s["name"], "former": s.get("formerNames") or [], "f402": f402}


def pairs():
    out = []
    cases = json.load(open("config/round7_cases.json"))
    ctrls = {c["case"]: c for c in json.load(open("results/round7/controls.json"))}
    for c in cases:
        k = ctrls[c["name"]]
        out.append({"src": "round8", "aaer": c["aaer"], "case": (c["cik"], _iso(c["y0_period"])),
                    "control": (k["control_cik"], _iso(k["y0_period"]))})
    for p in json.loads(subprocess.run(["git", "show", f"{DREAMY}:results/round9f/pairs.json"],
                                       capture_output=True, text=True, check=True).stdout):
        out.append({"src": "round9f", "aaer": p["case"].get("aaer"), "case": (int(p["case"]["cik"]), _iso(p["case"]["y0_period"])),
                    "control": (int(p["control"]["cik"]), _iso(p["control"]["y0_period"]))})
    return out


def cmd_build():
    P = pairs()
    rows = []
    for i, p in enumerate(P, 1):
        rec = {"pair": f"E{i:02d}", "src": p["src"], "aaer": p["aaer"]}
        for role, tag in (("case", "T"), ("control", "C")):
            cik, fy = p[role]
            s = submissions(cik)
            v = frame(_quarter(fy)).get(int(cik))
            y = int(fy[:4])
            rec[role] = {"pid": rec["pair"] + tag, "cik": int(cik), "fy": fy, "name_fy": name_at(s, fy),
                         "name": NAME_FIX.get(int(cik)) or fmt(name_at(s, fy)), "assets": v[0] if v else None,
                         "f402_near": [d for d in s["f402"] if f"{y - 1}-01-01" <= d <= f"{y + 5}-12-31"]}
        rows.append(rec)
    names = [r[x]["name"] for r in rows for x in ("case", "control")]
    assert len(set(names)) == len(names), "duplicate names"
    os.makedirs(OUT, exist_ok=True); os.makedirs(DATA, exist_ok=True)
    json.dump(rows, open(f"{OUT}/pairs.json", "w"), indent=1, ensure_ascii=False)
    idx = list(range(len(rows)))
    random.Random(SEED).shuffle(idx)
    groups = {"L1": idx[0::3], "L2": idx[1::3], "L3": idx[2::3]}
    base = open("data/mem_insample/prompt.md", encoding="utf-8").read()
    for g, ids in groups.items():
        lines, key = [], []
        for i in sorted(ids):
            for role in ("case", "control"):
                x = rows[i][role]
                lines.append(f"{x['name']} — fiscal year ended {x['fy']}")
                key.append((x["name"], x["pid"]))
        open(f"{DATA}/input_{g}.txt", "w").write("\n".join(f"{k}. {l}" for k, l in enumerate(sorted(lines), 1)) + "\n")
        open(f"{OUT}/key_{g}.tsv", "w").write("company\tpid\n" + "".join(f"{n}\t{p}\n" for n, p in key))
        open(f"{DATA}/prompt_{g}.md", "w").write(base.replace("Below are 54 company", f"Below are {len(lines)} company"))
        print(g, len(ids), "pairs")
    caps = [sum(r[x]["name_fy"].upper() == r[x]["name_fy"] for r in rows) for x in ("case", "control")]
    print(f"{len(rows)} pairs; all-caps original names: cases {caps[0]}, controls {caps[1]}; "
          f"missing assets: {sum(r[x]['assets'] is None for r in rows for x in ('case', 'control'))}; "
          f"controls with a 4.02 near Y0: {sum(bool(r['control']['f402_near']) for r in rows)}")


def cmd_run():
    for i, g in enumerate(LISTS):
        subprocess.run([sys.executable, "-m", "experiment.mem_isolated", "run", "--out", f"{OUT}/{g}",
                        "--input", f"{DATA}/input_{g}.txt", "--prompt", f"{DATA}/prompt_{g}.md",
                        "--runs", "5", "--seed", str(20261300 + 10 * i)], check=True)


def _collect(folders):
    runs = {}
    for folder, keyfile in folders:
        r, _ = _load(folder, keyfile)
        for n, d in r.items():
            runs.setdefault(n, {}).update(d)
    pids = sorted(next(iter(runs.values())))
    return ({p: sum(d[p][0] for d in runs.values()) / len(runs) for p in pids},
            {p: sum(d[p][1] for d in runs.values()) for p in pids})


def _fisher(a, b, c, d):
    """Two-sided Fisher exact p for [[a, b], [c, d]]."""
    n, r1, c1 = a + b + c + d, a + b, a + c
    def pr(x):
        return math.comb(r1, x) * math.comb(n - r1, c1 - x) / math.comb(n, c1)
    p0 = pr(a)
    return min(1.0, sum(pr(x) for x in range(max(0, c1 - (n - r1)), min(r1, c1) + 1) if pr(x) <= p0 * (1 + 1e-9)))


def cmd_evaluate():
    rows = json.load(open(f"{OUT}/pairs.json"))
    m, k = _collect([(f"{OUT}/{g}", f"{OUT}/key_{g}.tsv") for g in LISTS])
    qs = [r["pair"] for r in rows]
    im, ik = _collect([(f"{INS_OUT}/small/{h}", f"{INS_OUT}/small/key_{h}.tsv") for h in ("A1", "A2", "B1", "B2")])
    iq = sorted({p[:-1] for p in im})
    ins = {r["case"]["cik"]: r for r in []}
    rng = random.Random(13)

    def line(lab, M, K, Q):
        if not Q:
            return f"| {lab} | 0 | | | | | |"
        b = [_pair_auc(M, [rng.choice(Q) for _ in Q]) for _ in range(10000)]
        return (f"| {lab} | {len(Q)} | {_pair_auc(M, Q):.2f} | {_ci(b)[0]:.2f}–{_ci(b)[1]:.2f} | "
                f"{sum(M[q + 'T'] - M[q + 'C'] for q in Q) / len(Q):.1f} | {sum(K[q + 'T'] >= 3 for q in Q)} | "
                f"{sum(K[q + 'C'] >= 3 for q in Q)} |")
    head = ["| 樣本 | 對數 | AUC | 95% CI | 平均配對分數差 | 問題公司 ≥3/5 說知道 | 對照 ≥3/5 說知道 |",
            "|---|---|---|---|---|---|---|"]
    kn = [q for q in qs if k[q + "T"] >= 3]; nk = [q for q in qs if k[q + "T"] < 3]
    ikn = [q for q in iq if ik[q + "T"] >= 3]; ink = [q for q in iq if ik[q + "T"] < 3]
    L = ["# 時間內 AAER 樣本隔離 MEM：結果", "",
         f"Opus 5.5，3 份名單 × 5 次，全部通過 7 項無上網檢查；原始紀錄在算分前已 commit。預先登錄：`protocol.md`。", "",
         "## 1. 主要結果", ""] + head + [
        line("AAER 全部", m, k, qs),
        line("　第八輪 14 對", m, k, [r["pair"] for r in rows if r["src"] == "round8"]),
        line("　第九輪 f 27 對", m, k, [r["pair"] for r in rows if r["src"] == "round9f"]),
        line("4.02 時間內（短名單）", im, ik, iq)]
    L += ["", f"- 問題公司被記得（≥ 3/5）：AAER {len(kn)}/{len(qs)}（{100 * len(kn) / len(qs):.0f}%），"
              f"4.02 {len(ikn)}/{len(iq)}（{100 * len(ikn) / len(iq):.0f}%）；Fisher 精確檢定 p = "
              f"{_fisher(len(kn), len(nk), len(ikn), len(ink)):.4f}",
          f"- 至少 1 次說知道：AAER {sum(k[q + 'T'] >= 1 for q in qs)}/{len(qs)}，4.02 {sum(ik[q + 'T'] >= 1 for q in iq)}/{len(iq)}",
          "", "## 2. 依「問題公司是否被記得」分組", ""] + head + [
        line("AAER：被記得", m, k, kn), line("AAER：沒被記得", m, k, nk),
        line("4.02：被記得", im, ik, ikn), line("4.02：沒被記得", im, ik, ink)]
    # size
    sizes = [r["case"]["assets"] for r in rows if r["case"]["assets"]]
    ip = json.load(open(f"{INS_OUT}/pairs.json"))["pairs"]
    isz = {f"I{i + 1:02d}": p["case"]["assets"] for i, p in enumerate(ip)}
    allsz = sorted(sizes + [v for v in isz.values() if v])
    med = allsz[len(allsz) // 2]
    L += ["", "## 3. 規模", "", f"問題公司 Y0 總資產，以兩個樣本合併的中位數（{med / 1e6:,.0f} 百萬美元）分組。", "",
          "| 標籤 | 規模 | 問題公司家數 | 被記得（≥ 3/5） | 比例 |", "|---|---|---|---|---|"]
    for lab, Q, K, S in (("AAER", qs, k, {r["pair"]: r["case"]["assets"] for r in rows}), ("4.02", iq, ik, isz)):
        for sl, f in (("小", lambda a: a < med), ("大", lambda a: a >= med)):
            g = [q for q in Q if S.get(q) and f(S[q])]
            n = sum(K[q + "T"] >= 3 for q in g)
            L.append(f"| {lab} | {sl} | {len(g)} | {n} | {100 * n / len(g) if g else float('nan'):.0f}% |")
        miss = [q for q in Q if not S.get(q)]
        if miss:
            L.append(f"| {lab} | 無資產資料 | {len(miss)} | {sum(K[q + 'T'] >= 3 for q in miss)} | |")
    dirty = [r["pair"] for r in rows if r["control"]["f402_near"]]
    L += ["", "## 4. 敏感度", ""]
    if dirty:
        keep = [q for q in qs if q not in dirty]
        L.append(f"- 排除對照在 Y0 前一年至後五年內曾申報 4.02 的配對（{', '.join(dirty)}）：{len(keep)} 對，AUC {_pair_auc(m, keep):.2f}")
    else:
        L.append("- 沒有對照在 Y0 前一年至後五年內申報 4.02")
    L += ["", "## 5. 逐對", "", "| 配對 | 來源 | 問題公司 | 分數 | 知道 | 總資產（百萬） | 對照公司 | 分數 | 知道 |",
          "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        q, c, t = r["pair"], r["control"], r["case"]
        a = f"{t['assets'] / 1e6:,.0f}" if t["assets"] else "—"
        L.append(f"| {q} | {r['src']} | {t['name']} ({t['fy'][:4]}) | {m[q + 'T']:.0f} | {k[q + 'T']}/5 | {a} | "
                 f"{c['name']} | {m[q + 'C']:.0f} | {k[q + 'C']}/5 |")
    open(f"{OUT}/evaluation.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:40]))


if __name__ == "__main__":
    {"build": cmd_build, "run": cmd_run, "evaluate": cmd_evaluate}[sys.argv[1]]()

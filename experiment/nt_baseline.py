"""Post-hoc check: does counting late-filing notices (NT 10-K / NT 10-Q) match the name-only LLM score?

Samples: in-sample 4.02 (results/mem_insample, 54 pairs), in-sample AAER (results/mem_aaer, 41 pairs) and
out-of-time 4.02 (results/mem_isolated_oot, 27 pairs). Filing histories come from data.sec.gov submissions
(older pages included). Not pre-registered: the indicator was chosen after looking at the out-of-time sample.

Windows (counted per company, using its own pair's case dates for both members of a pair)
  strict : NT filings dated in (Y0 fiscal-year end - 3 years, Y0 fiscal-year end]
  wide   : NT filings dated in (Y0 end - 3 years, min(Y0 end + 150 days, event date - 1 day)]  (4.02 samples only;
           the out-of-time sample used this shape earlier, ending at the model's cutoff)

  python -m experiment.nt_baseline     # writes results/nt_baseline.md
"""
import csv
import glob
import json
import random
import re
from datetime import date, timedelta

from experiment.mem_aaer import submissions as _cache_subs, CACHE, _collect, OUT as AAER_OUT, LISTS
from experiment.mem_insample import _pair_auc, _ci, OUT as INS_OUT
from experiment.mem_isolated import _by_pid, spearman


def nt_dates(cik):
    _cache_subs(cik)   # make sure the full history (with older pages) is cached
    s = json.load(open(f"{CACHE}/subs/CIK{int(cik):010d}.json"))
    r = s["filings"]["recent"]
    return sorted(r["filingDate"][i] for i, f in enumerate(r["form"]) if f.startswith("NT 10-K") or f.startswith("NT 10-Q"))


def count(ds, lo, hi):
    return sum(lo < d <= hi for d in ds)


def window(y0, event=None, wide=False):
    e = date.fromisoformat(y0)
    lo = (e.replace(year=e.year - 3)).isoformat()
    hi = e
    if wide:
        hi = e + timedelta(days=150)
        if event:
            hi = min(hi, date.fromisoformat(event) - timedelta(days=1))
    return lo, hi.isoformat()


def iso(d):
    d = d.replace("-", "")
    return f"{d[:4]}-{d[4:6]}-{d[6:8]}"


def samples():
    out = {}
    # in-sample 4.02
    P = json.load(open(f"{INS_OUT}/pairs.json"))["pairs"]
    m, k = _collect([(f"{INS_OUT}/small/{h}", f"{INS_OUT}/small/key_{h}.tsv") for h in ("A1", "A2", "B1", "B2")])
    pairs = []
    for i, p in enumerate(P, 1):
        q = f"I{i:02d}"
        pairs.append(dict(q=q, case=p["case"]["cik"], ctrl=p["control"]["cik"], y0=p["case"]["y0_period"],
                          event=p["case"]["event_date"]))
    out["4.02 時間內"] = (pairs, m, k)
    # in-sample AAER
    rows = json.load(open(f"{AAER_OUT}/pairs.json"))
    m, k = _collect([(f"{AAER_OUT}/{g}", f"{AAER_OUT}/key_{g}.tsv") for g in LISTS])
    out["AAER 時間內"] = ([dict(q=r["pair"], case=r["case"]["cik"], ctrl=r["control"]["cik"], y0=r["case"]["fy"], event=None)
                          for r in rows], m, k)
    # out-of-time 4.02
    import subprocess
    pj = json.loads(subprocess.run(["git", "show", "origin/claude/dreamy-volta-i6oimk:results/round9/pairs.json"],
                                   capture_output=True, text=True, check=True).stdout)
    key = {r["company"]: r["pid"] for r in csv.DictReader(open("results/mem_isolated_oot/key.tsv"), delimiter="\t")}
    runs = []
    for js in sorted(glob.glob("results/mem_isolated_oot/run[0-9]*.json")):
        n = re.search(r"run(\d+)\.json", js).group(1)
        runs.append(_by_pid(json.load(open(js))["scores"], open(f"results/mem_isolated_oot/inputs/run{n}.txt").read(), key))
    pids = list(runs[0])
    m = {p: sum(r[p][0] for r in runs) / len(runs) for p in pids}
    k = {p: sum(r[p][1] for r in runs) for p in pids}
    out["4.02 時間外"] = ([dict(q=f"O{i:02d}", case=int(p["case"]["cik"]), ctrl=int(p["control"]["cik"]),
                               y0=iso(p["case"]["y0_period"]), event=iso(p["case"]["event_date"]))
                          for i, p in enumerate(pj, 1)], m, k)
    return out


def main():
    rng = random.Random(5)
    L = ["# 延遲申報次數基準：三個樣本（事後分析）", "",
         "指標：公司在指定期間內申報 NT 10-K／NT 10-Q（延遲申報通知）的次數，次數越多排越前面。",
         "這個指標是在看過時間外樣本之後才選的，不是預先登錄；只作為「只給名稱的 LLM 分數是否超出公開申報紀錄」的參考。", "",
         "- 嚴格期間：Y0 會計年度結束前 3 年內（不含之後）",
         "- 寬期間（只有 4.02 樣本）：Y0 結束前 3 年起，到 Y0 結束後 150 天或事件前一天（取較早者）；時間外樣本先前用的就是這個形狀", "",
         "| 樣本 | 子樣本 | 對數 | LLM 只給名稱 | 延遲申報次數（嚴格） | 延遲申報次數（寬） | LLM − 延遲申報（嚴格） | 有延遲申報的問題／對照家數（嚴格） | Spearman（LLM, 嚴格） |",
         "|---|---|---|---|---|---|---|---|---|"]
    for name, (pairs, m, k) in samples().items():
        nts = {}
        for p in pairs:
            lo, hi = window(p["y0"])
            wlo, whi = window(p["y0"], p["event"], wide=True)
            for role, tag in (("case", "T"), ("ctrl", "C")):
                ds = nt_dates(p[role])
                nts[p["q"] + tag] = (count(ds, lo, hi), count(ds, wlo, whi))
        strict = {x: v[0] for x, v in nts.items()}
        wide = {x: v[1] for x, v in nts.items()}
        subs = [("全部", [p["q"] for p in pairs])]
        if any(k[p["q"] + "T"] >= 3 for p in pairs):
            subs += [("問題公司沒被記得", [p["q"] for p in pairs if k[p["q"] + "T"] < 3]),
                     ("問題公司被記得", [p["q"] for p in pairs if k[p["q"] + "T"] >= 3])]
        for sub, Q in subs:
            if not Q:
                continue
            boot = [[rng.choice(Q) for _ in Q] for _ in range(5000)]
            def cell(S):
                b = [_pair_auc(S, s) for s in boot]
                return f"{_pair_auc(S, Q):.2f}（{_ci(b)[0]:.2f}–{_ci(b)[1]:.2f}）"
            d = [_pair_auc(m, s) - _pair_auc(strict, s) for s in boot]
            ids = [q + t for q in Q for t in "TC"]
            L.append(f"| {name} | {sub} | {len(Q)} | {cell(m)} | {cell(strict)} | "
                     f"{cell(wide) if name.startswith('4.02') else '—'} | "
                     f"{_pair_auc(m, Q) - _pair_auc(strict, Q):+.2f}（{_ci(d)[0]:+.2f} 至 {_ci(d)[1]:+.2f}） | "
                     f"{sum(strict[q + 'T'] > 0 for q in Q)}／{sum(strict[q + 'C'] > 0 for q in Q)} | "
                     f"{spearman([m[i] for i in ids], [strict[i] for i in ids]):.2f} |")
    L += ["", "括號內為配對 bootstrap 95% CI。AUC 以配對內問題公司與對照公司比較（平手算一半）；延遲申報次數平手很多，0.5 附近表示多數配對兩家都沒有延遲申報。"]
    open("results/nt_baseline.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()

"""Compare memory-only (MEM) scores across Claude models on the round 8 sample and the out-of-time sample.

Runs are produced by experiment.mem_isolated (same no-tool environment and checks); this module only reads them.
`compare` refuses to read labels unless every run passes the 7 no-web checks and is committed unchanged.

  python -m experiment.mem_models compare      # writes results/mem_models/evaluation.md
"""
import csv
import json
import os
import re
import statistics as st
import subprocess

from experiment.edgar_risk.round3 import auc
from experiment.mem_isolated import _by_pid, _pairs_auc, load_events, spearman, verify

MODELS = [("Opus 5.5", "claude-opus-5-5", {"round8": "results/mem_isolated", "oot": "results/mem_isolated_oot"}),
          ("Sonnet 5.5", "claude-sonnet-5-5", {"round8": "results/mem_models/sonnet-5-5/round8",
                                               "oot": "results/mem_models/sonnet-5-5/oot"}),
          ("Haiku 5.5", "claude-haiku-5-5", {"round8": "results/mem_models/haiku-5-5/round8",
                                             "oot": "results/mem_models/haiku-5-5/oot"})]
KEYS = {"round8": "results/mem_isolated/key.tsv", "oot": "results/mem_isolated_oot/key.tsv"}
SAMPLE_NAME = {"round8": "第八輪 28 家（AAER）", "oot": "時間外 54 家（截止後 4.02）"}
RUNS = 5
OUT = "results/mem_models"


def _committed(path):
    return not subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path]).returncode and \
        not subprocess.run(["git", "ls-files", "--error-unmatch", path], capture_output=True).returncode


def load(folder, key, model_id):
    """{run k: {pid: (score, knows)}} after the gate (checks pass, served model matches, files committed)."""
    out = {}
    for k in range(1, RUNS + 1):
        raw, js, inp = f"{folder}/raw/run{k}.jsonl", f"{folder}/run{k}.json", f"{folder}/inputs/run{k}.txt"
        v = verify(load_events(raw))
        if not v["all_pass"]:
            raise SystemExit(f"{raw} fails verification")
        if v["served_models"] != [model_id]:
            raise SystemExit(f"{raw} served by {v['served_models']}, expected {model_id}")
        for p in (raw, js, inp):
            if not _committed(p):
                raise SystemExit(f"{p} is not committed unchanged; commit raw outputs before comparing")
        out[k] = _by_pid(json.load(open(js))["scores"], open(inp, encoding="utf-8").read(), key)
    return out


def strata(runs):
    """Knows / not-known decomposition, pooled or averaged over runs (pre-registered in protocol section 6)."""
    knows_auc, resid_auc = [], []
    pool = {(g, kn): [] for g in "TC" for kn in (True, False)}
    for d in runs.values():
        pos = [d[p] for p in d if p.endswith("T")]
        neg = [d[p] for p in d if p.endswith("C")]
        knows_auc.append(auc([int(x[1]) for x in pos], [int(x[1]) for x in neg]))
        grp = {kn: st.mean([s for s, k in d.values() if k == kn]) for kn in (True, False)
               if any(k == kn for _, k in d.values())}
        res = {p: s - grp[k] for p, (s, k) in d.items()}
        resid_auc.append(auc([res[p] for p in d if p.endswith("T")], [res[p] for p in d if p.endswith("C")]))
        for p, (s, k) in d.items():
            pool[(p[-1], k)].append(s)
    nk_t, nk_c = pool[("T", False)], pool[("C", False)]
    return {"knows_auc": st.mean(knows_auc), "resid_auc": st.mean(resid_auc),
            "notknown_auc": auc(nk_t, nk_c) if nk_t and nk_c else float("nan"),
            "n_nk_t": len(nk_t), "n_nk_c": len(nk_c),
            "med": {g: st.median(v) if v else None for g, v in pool.items()},
            "n": {g: len(v) for g, v in pool.items()}}


def cmd_compare():
    keys = {s: {r["company"]: r["pid"] for r in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t")}
            for s, p in KEYS.items()}
    data = {(m, s): load(f, keys[s], mid) for m, mid, folders in MODELS for s, f in folders.items()}
    lines = ["# 不同模型的隔離 MEM：結果", "",
             "每個模型、每份樣本 5 次 `claude -p --tools \"\"`，第 k 次三個模型看到同一份名單；全部通過 7 項無上網檢查，原始紀錄在算分前已 commit。", ""]
    mean_auc = {}
    for s in ("round8", "oot"):
        pids = sorted(keys[s].values())
        npair = sum(p.endswith("T") for p in pids)
        opus_mean = [st.mean(data[("Opus 5.5", s)][k][p][0] for k in data[("Opus 5.5", s)]) for p in pids]
        lines += [f"## {SAMPLE_NAME[s]}", "",
                  "| 模型 | 平均分數 AUC | 95% CI | 5 次 AUC 範圍 | 組內勝 / 平 / 負 | 問題公司「知道出事」（5 次） | 對照公司「知道出事」（5 次） | 與 Opus 的 Spearman ρ |",
                  "|---|---|---|---|---|---|---|---|"]
        for m, _, _ in MODELS:
            runs = data[(m, s)]
            mean = {p: st.mean(runs[k][p][0] for k in runs) for p in pids}
            a, lo, hi, w, t, l = _pairs_auc(mean)
            mean_auc[(m, s)] = a
            per = [_pairs_auc({p: runs[k][p][0] for p in pids})[0] for k in runs]
            kt = [sum(runs[k][p][1] for p in pids if p.endswith("T")) for k in runs]
            kc = [sum(runs[k][p][1] for p in pids if p.endswith("C")) for k in runs]
            rho = spearman([mean[p] for p in pids], opus_mean)
            lines.append(f"| {m} | **{a:.2f}** | {lo:.2f}–{hi:.2f} | {min(per):.2f}–{max(per):.2f} | {w} / {t} / {l} | "
                         f"{min(kt)}–{max(kt)} / {npair} | {min(kc)}–{max(kc)} / {npair} | {rho:.2f} |")
        lines.append("")
    lines += ["## 記憶增量 Δ = 第八輪 AUC − 時間外 AUC（平均分數）", "",
              "| 模型 | 第八輪 | 時間外 | Δ | 第八輪問題公司「知道出事」平均比例 |", "|---|---|---|---|---|"]
    for m, _, _ in MODELS:
        runs = data[(m, "round8")]
        kt = st.mean(sum(runs[k][p][1] for p in runs[k] if p.endswith("T")) / 14 for k in runs)
        lines.append(f"| {m} | {mean_auc[(m, 'round8')]:.2f} | {mean_auc[(m, 'oot')]:.2f} | "
                     f"{mean_auc[(m, 'round8')] - mean_auc[(m, 'oot')]:+.2f} | {kt:.0%} |")
    lines += ["", "## 「知道／不知道」分層（實驗 2）", "",
              "- 只用「知道」旗標排序的 AUC：每次把「知道」當 1、「不知道」當 0 計算 AUC，取 5 次平均",
              "- 殘差 AUC：每次把分數減去同一次同一組（知道／不知道）的平均分數，再算 AUC，取 5 次平均",
              "- 「不知道」子集 AUC：5 次合併，只比較說「不知道」的問題公司與說「不知道」的對照公司（公司 × 次數為單位）", "",
              "| 樣本 | 模型 | 只用「知道」旗標 AUC | 殘差 AUC | 「不知道」子集 AUC（問題 n / 對照 n） | 中位數分數：問題知道 / 問題不知道 / 對照知道 / 對照不知道 |",
              "|---|---|---|---|---|---|"]
    for s in ("round8", "oot"):
        for m, _, _ in MODELS:
            r = strata(data[(m, s)])
            med = " / ".join("–" if r["med"][g] is None else f"{r['med'][g]:.0f}（n={r['n'][g]}）"
                             for g in (("T", True), ("T", False), ("C", True), ("C", False)))
            lines.append(f"| {SAMPLE_NAME[s][:3]} | {m} | {r['knows_auc']:.2f} | {r['resid_auc']:.2f} | "
                         f"{r['notknown_auc']:.2f}（{r['n_nk_t']} / {r['n_nk_c']}） | {med} |")
    os.makedirs(OUT, exist_ok=True)
    open(f"{OUT}/evaluation.md", "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    import sys
    if sys.argv[1:] != ["compare"]:
        raise SystemExit(__doc__)
    cmd_compare()

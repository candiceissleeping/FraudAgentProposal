"""In-sample 8-K Item 4.02 MEM run (pre-registration: results/mem_insample/protocol.md).

Same label, selection rules, prompt and isolated environment as the out-of-time sample (experiment B,
results/mem_isolated_oot), but with 4.02 events filed 2023-01-01..2025-06-30, before the model's training cutoff.

Only data.sec.gov is used (XBRL frames and submissions JSON).

  python -m experiment.mem_insample fetch      # frames + compact submissions summary (cache in SEC_CACHE)
  python -m experiment.mem_insample select     # cases, controls, names -> results/mem_insample/{cases,pairs}.json
  python -m experiment.mem_insample lists      # data/mem_insample/input_{A,B}.txt and results/mem_insample/key_{A,B}.tsv
  python -m experiment.mem_insample run        # 5 isolated runs per list (experiment.mem_isolated run)
  python -m experiment.mem_insample evaluate   # after the raw runs are committed
"""
import argparse
import csv
import glob
import json
import math
import os
import random
import re
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

OUT = "results/mem_insample"
DATA = "data/mem_insample"
CACHE = os.environ.get("SEC_CACHE", "/tmp/mem_insample_sec")
UA = "FraudAgentProposal academic research script"
WINDOW = ("2023-01-01", "2025-06-30")
CLEAN_FROM = "2021-01-01"          # controls: no 8-K 4.02 filed on or after this date
SEED = 20261116
N_CASES = 54
QUARTERS = [f"CY{y}Q{q}I" for y in range(2021, 2026) for q in range(1, 5)]
PRIOR = ["results/mem_isolated/key.tsv", "results/mem_isolated_oot/key.tsv"]   # experiments A and B

_lock = threading.Lock()
_last = [0.0]


def _get(url):
    for attempt in range(6):
        with _lock:   # stay under SEC's 10 requests per second
            wait = _last[0] + 0.13 - time.time()
            if wait > 0:
                time.sleep(wait)
            _last[0] = time.time()
        r = subprocess.run(["curl", "-s", "--fail", "-m", "60", "-A", UA, url], capture_output=True)
        if r.returncode == 0:
            return r.stdout
        if r.returncode == 22 and b"404" in r.stderr:
            return None
        time.sleep(2 ** attempt)
    return None


def frame(q):
    path = f"{CACHE}/frames/Assets_{q}.json"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        raw = _get(f"https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/USD/{q}.json")
        open(path, "wb").write(raw or b'{"data": []}')
    return {int(d["cik"]): (d["val"], d["end"], d["entityName"]) for d in json.load(open(path))["data"]}


def _summary(cik):
    raw = _get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json")
    if not raw:
        return {"cik": cik, "error": "no submissions"}
    s = json.loads(raw)
    r = s["filings"]["recent"]
    f402, tenk = [], []
    for i, form in enumerate(r["form"]):
        items = [x.strip() for x in (r["items"][i] or "").split(",")]
        if form in ("8-K", "8-K/A") and "4.02" in items:
            f402.append({"date": r["filingDate"][i], "acc": r["accessionNumber"][i], "form": form})
        if form == "10-K":
            tenk.append({"acc": r["accessionNumber"][i], "filed": r["filingDate"][i], "period": r["reportDate"][i],
                         "xbrl": bool(r["isXBRL"][i])})
    return {"cik": cik, "name": s.get("name"), "sic": s.get("sic") or "", "former": s.get("formerNames") or [],
            "oldest_recent": min(r["filingDate"]) if r["filingDate"] else None, "n_recent": len(r["form"]),
            "f402": f402, "tenk": tenk}


def cmd_fetch(args):
    ciks = set()
    for q in QUARTERS:
        ciks |= set(frame(q))
    path = f"{CACHE}/submissions_summary.jsonl"
    done = set()
    if os.path.exists(path):
        done = {json.loads(l)["cik"] for l in open(path)}
    todo = sorted(ciks - done)
    print(f"{len(ciks)} companies in frames {QUARTERS[0]}..{QUARTERS[-1]}; {len(todo)} to fetch", flush=True)
    with open(path, "a") as fh, ThreadPoolExecutor(4) as ex:
        for k, rec in enumerate(ex.map(_summary, todo), 1):
            with _lock:
                fh.write(json.dumps(rec) + "\n")
            if k % 500 == 0:
                fh.flush()
                print(f"  {k}/{len(todo)}", flush=True)


def _summaries():
    return {r["cik"]: r for r in map(json.loads, open(f"{CACHE}/submissions_summary.jsonl")) if "error" not in r}


def _prior_names():
    names = set()
    for p in PRIOR:
        for row in csv.DictReader(open(p, encoding="utf-8"), delimiter="\t"):
            names.add(_norm(row["company"]))
    return names


def _norm(n):
    return re.sub(r"[^a-z0-9]", "", re.sub(r"/[a-z]{2}/?|\b(incorporated|inc|corporation|corp|ltd|limited|co|company|plc|llc)\b",
                                         "", n.lower()))


def _quarter(date):
    y, m = int(date[:4]), int(date[5:7])
    return f"CY{y}Q{(m - 1) // 3 + 1}I"


def _days(a, b):
    from datetime import date
    return abs((date.fromisoformat(a) - date.fromisoformat(b)).days)


def name_at(rec, when):
    """Company name in effect on date `when` (formerNames carry from/to dates); current name otherwise."""
    for f in rec["former"]:
        if f.get("from", "")[:10] <= when <= (f.get("to") or "9999")[:10]:
            return f["name"]
    return rec["name"]


SUFFIX = {"inc": "Inc.", "corp": "Corp.", "ltd": "Ltd.", "co": "Co.", "llc": "LLC", "plc": "plc", "lp": "L.P.",
          "n.v": "N.V.", "s.a": "S.A."}


def fmt(name):
    """One formatting rule for every company: drop state tags, title-case all-caps names, dot common suffixes."""
    n = re.sub(r"\s*/[A-Za-z]{2,3}/?\s*$", "", name).strip()
    n = re.sub(r"\s+", " ", n)
    if n.upper() == n:
        n = " ".join(w.capitalize() if not re.fullmatch(r"[A-Z]{1,3}&[A-Z]{1,3}", w) else w for w in n.split())
    words = n.split()
    for i, w in enumerate(words):
        key = w.lower().rstrip(".,")
        if key in SUFFIX and i > 0:
            words[i] = SUFFIX[key] + ("," if w.endswith(",") else "")
    return " ".join(words)


def _assets(cik, period):
    v = frame(_quarter(period)).get(cik)
    return v[0] if v and v[0] and v[0] > 0 else None


def cmd_select(args):
    S = _summaries()
    prior = _prior_names()
    log, eligible = [], []
    for cik, r in S.items():
        ev = sorted((f for f in r["f402"] if WINDOW[0] <= f["date"] <= WINDOW[1]), key=lambda f: f["date"])
        if not ev:
            continue
        e = ev[0]
        if _norm(r["name"]) in prior or any(_norm(f["name"]) in prior for f in r["former"]):
            log.append((r["name"], "used in experiment A or B")); continue
        if r["sic"] == "6770":
            log.append((r["name"], "SIC 6770 blank check")); continue
        if not r["sic"]:
            log.append((r["name"], "no SIC")); continue
        ks = sorted((k for k in r["tenk"] if k["filed"] < e["date"]), key=lambda k: k["filed"], reverse=True)
        if len(ks) < 2:
            log.append((r["name"], f"{len(ks)} original 10-K before event")); continue
        if not ks[0]["xbrl"]:
            log.append((r["name"], "Y0 without XBRL")); continue
        if not _assets(cik, ks[0]["period"]):
            log.append((r["name"], "no total assets in frames for Y0 quarter")); continue
        eligible.append({"cik": cik, "sic": r["sic"], "event_date": e["date"], "event_acc": e["acc"],
                         "y0": ks[0], "y1": ks[1]})
    eligible.sort(key=lambda c: c["cik"])
    print(f"{len(eligible)} eligible cases; {len(log)} excluded")
    rng = random.Random(SEED)
    cases = rng.sample(eligible, min(N_CASES, len(eligible)))
    # control pool
    case_ciks = {c["cik"] for c in eligible}
    pool = []
    for cik, r in S.items():
        if cik in case_ciks or r["sic"] in ("", "6770"):
            continue
        if any(f["date"] >= CLEAN_FROM for f in r["f402"]):
            continue
        if _norm(r["name"]) in prior or any(_norm(f["name"]) in prior for f in r["former"]):
            continue
        if r["oldest_recent"] and r["oldest_recent"] > CLEAN_FROM and r["n_recent"] >= 1000:
            continue   # recent block does not reach back to 2021: cannot confirm a clean history
        pool.append(r)
    used, pairs, nocontrol = set(), [], []
    for c in cases:
        y0 = c["y0"]["period"]
        a_case = _assets(c["cik"], y0)
        best = fallback = None
        for digits in (4, 3, 2):
            cands = []
            for r in pool:
                if r["cik"] in used or r["sic"][:digits] != c["sic"][:digits]:
                    continue
                ks = sorted((k for k in r["tenk"] if _days(k["period"], y0) <= 92 and k["xbrl"]),
                            key=lambda k: _days(k["period"], y0))
                if not ks:
                    continue
                prev = [k for k in r["tenk"] if k["filed"] < ks[0]["filed"]]
                if not prev:
                    continue
                a = _assets(r["cik"], ks[0]["period"])
                if not a:
                    continue
                cands.append((abs(math.log(a / a_case)), r, ks[0], a))
            if not cands:
                continue
            cands.sort(key=lambda x: (x[0], x[1]["cik"]))
            if digits == 4:
                fallback = cands[0] + (4,)
            if math.exp(cands[0][0]) <= 3:
                best = cands[0] + (digits,)
                break
        if best is None:
            best = fallback
        if best is None:
            nocontrol.append(c["cik"]); log.append((S[c["cik"]]["name"], "no control found")); continue
        _, r, k, a, digits = best
        used.add(r["cik"])
        pairs.append({"case": {"cik": c["cik"], "name_now": S[c["cik"]]["name"], "name_fy": name_at(S[c["cik"]], y0),
                               "sic": c["sic"], "event_date": c["event_date"], "event_acc": c["event_acc"],
                               "y0_period": y0, "y0_acc": c["y0"]["acc"], "assets": a_case},
                      "control": {"cik": r["cik"], "name_now": r["name"], "name_fy": name_at(r, k["period"]),
                                  "sic": r["sic"], "sic_digits": digits, "y0_period": k["period"], "y0_acc": k["acc"],
                                  "assets": a, "size_ratio": round(max(a, a_case) / min(a, a_case), 2)}})
    os.makedirs(OUT, exist_ok=True)
    json.dump({"eligible": len(eligible), "sampled": len(cases), "pairs": pairs}, open(f"{OUT}/pairs.json", "w"),
              indent=1, ensure_ascii=False)
    with open(f"{OUT}/case_selection_log.tsv", "w") as fh:
        for n, why in sorted(log):
            fh.write(f"{n}\t{why}\n")
    big = sum(p["control"]["size_ratio"] > 3 for p in pairs)
    print(f"{len(pairs)} pairs; no control: {len(nocontrol)}; size ratio > 3: {big}; "
          f"SIC digits: {[sum(p['control']['sic_digits'] == d for p in pairs) for d in (4, 3, 2)]}")


def cmd_lists(args):
    P = json.load(open(f"{OUT}/pairs.json"))["pairs"]
    rng = random.Random(SEED + 1)
    idx = list(range(len(P)))
    rng.shuffle(idx)
    half = len(idx) // 2
    groups = {"A": sorted(idx[:half]), "B": sorted(idx[half:])}
    caps = {"T": 0, "C": 0}
    for g, ids in groups.items():
        lines, keyrows = [], []
        for n, i in enumerate(ids, 1):
            for role, tag in (("case", "T"), ("control", "C")):
                x = P[i][role]
                name = fmt(x["name_fy"])
                caps[tag] += x["name_fy"].upper() == x["name_fy"]
                lines.append(f"{name} — fiscal year ended {x['y0_period']}")
                keyrows.append((f"I{i + 1:02d}{tag}", name))
        names = [r[1] for r in keyrows]
        assert len(set(names)) == len(names), "duplicate formatted names"
        open(f"{DATA}/input_{g}.txt", "w").write("\n".join(f"{k}. {l}" for k, l in enumerate(sorted(lines), 1)) + "\n")
        with open(f"{OUT}/key_{g}.tsv", "w") as fh:
            fh.write("company\tpid\n" + "".join(f"{n}\t{p}\n" for p, n in keyrows))
    print(f"lists A/B: {len(groups['A'])}/{len(groups['B'])} pairs; originally all-caps names: "
          f"cases {caps['T']}, controls {caps['C']} of {len(P)} each")


def cmd_run(args):
    for g, seed in (("A", 20261117), ("B", 20261127)):
        subprocess.run([sys.executable, "-m", "experiment.mem_isolated", "run", "--out", f"{OUT}/{g}",
                        "--input", f"{DATA}/input_{g}.txt", "--prompt", f"{DATA}/prompt.md",
                        "--runs", "5", "--seed", str(seed)], check=True)


# ---------------------------------------------------------------- evaluation
def _committed(p):
    return not subprocess.run(["git", "diff", "--quiet", "HEAD", "--", p]).returncode and \
        not subprocess.run(["git", "ls-files", "--error-unmatch", p], capture_output=True).returncode


def _load(folder, keyfile):
    from experiment.mem_isolated import verify, load_events, _by_pid
    key = {r["company"]: r["pid"] for r in csv.DictReader(open(keyfile, encoding="utf-8"), delimiter="\t")}
    runs = {}
    for js in sorted(glob.glob(f"{folder}/run[0-9]*.json")):
        k = re.search(r"run(\d+)\.json", js).group(1)
        raw, inp = f"{folder}/raw/run{k}.jsonl", f"{folder}/inputs/run{k}.txt"
        if not verify(load_events(raw))["all_pass"]:
            raise SystemExit(f"{raw} fails verification")
        for p in (raw, js, inp):
            if not _committed(p):
                raise SystemExit(f"{p} is not committed unchanged; commit raw outputs before evaluating")
        runs[k] = _by_pid(json.load(open(js))["scores"], open(inp, encoding="utf-8").read(), key)
    return runs, key


def _auc(pos, neg):
    return sum((a > b) + 0.5 * (a == b) for a in pos for b in neg) / (len(pos) * len(neg))


def _pair_auc(S, qs):
    return _auc([S[q + "T"] for q in qs], [S[q + "C"] for q in qs])


def _ci(vals):
    v = sorted(vals)
    return v[int(0.025 * len(v))], v[int(0.975 * len(v)) - 1]


def cmd_evaluate(args):
    runs, key = {}, {}
    for g in ("A", "B"):
        r, k = _load(f"{OUT}/{g}", f"{OUT}/key_{g}.tsv")
        for n, d in r.items():
            runs.setdefault(n, {}).update(d)
        key.update(k)
    pids = sorted(set().union(*[set(d) for d in runs.values()]))
    mean = {p: sum(d[p][0] for d in runs.values()) / len(runs) for p in pids}
    knows = {p: sum(d[p][1] for d in runs.values()) for p in pids}
    qs = sorted({p[:-1] for p in pids})
    # experiment B
    oot_runs, oot_key = {}, {}
    from experiment.mem_isolated import _by_pid
    oot_key = {r["company"]: r["pid"] for r in csv.DictReader(open("results/mem_isolated_oot/key.tsv"), delimiter="\t")}
    for js in sorted(glob.glob("results/mem_isolated_oot/run[0-9]*.json")):
        k = re.search(r"run(\d+)\.json", js).group(1)
        oot_runs[k] = _by_pid(json.load(open(js))["scores"],
                              open(f"results/mem_isolated_oot/inputs/run{k}.txt").read(), oot_key)
    om = {p: sum(d[p][0] for d in oot_runs.values()) / len(oot_runs) for p in oot_key.values()}
    oq = sorted({p[:-1] for p in om})
    rng = random.Random(7)
    B = 10000
    boot_in = [_pair_auc(mean, [rng.choice(qs) for _ in qs]) for _ in range(B)]
    boot_oot = [_pair_auc(om, [rng.choice(oq) for _ in oq]) for _ in range(B)]
    gap = lambda S, q: S[q + "T"] - S[q + "C"]
    gin, gout = [gap(mean, q) for q in qs], [gap(om, q) for q in oq]
    bgap = [sum(rng.choices(gin, k=len(gin))) / len(gin) - sum(rng.choices(gout, k=len(gout))) / len(gout)
            for _ in range(B)]
    a_in, a_oot = _pair_auc(mean, qs), _pair_auc(om, oq)
    diff = [a - b for a, b in zip(boot_in, boot_oot)]
    w = sum(mean[q + "T"] > mean[q + "C"] for q in qs); t = sum(mean[q + "T"] == mean[q + "C"] for q in qs)
    kT = sum(knows[q + "T"] >= 3 for q in qs); kC = sum(knows[q + "C"] >= 3 for q in qs)
    kflag = {p: knows[p] / len(runs) for p in pids}
    L = ["# 時間內 4.02 樣本隔離 MEM：結果", "",
         f"Opus 5.5，{len(runs)} 次執行 × 2 份名單（A、B），全部通過 7 項無上網檢查；原始紀錄在算分前已 commit。"
         f"預先登錄：`protocol.md`。", "",
         "## 1. 主要結果", "",
         "| 樣本 | 事件時間 | 對數 | AUC | 95% CI | 組內勝／平／負 | 平均配對分數差 |", "|---|---|---|---|---|---|---|",
         f"| **時間內（本實驗）** | 2023-01 至 2025-06 | {len(qs)} | **{a_in:.2f}** | {_ci(boot_in)[0]:.2f}–{_ci(boot_in)[1]:.2f} "
         f"| {w}／{t}／{len(qs) - w - t} | {sum(gin) / len(gin):.1f} |",
         f"| 時間外（實驗 B） | 2026-07 至 2026-10 | {len(oq)} | {a_oot:.2f} | {_ci(boot_oot)[0]:.2f}–{_ci(boot_oot)[1]:.2f} "
         f"| {sum(om[q + 'T'] > om[q + 'C'] for q in oq)}／{sum(om[q + 'T'] == om[q + 'C'] for q in oq)}／"
         f"{sum(om[q + 'T'] < om[q + 'C'] for q in oq)} | {sum(gout) / len(gout):.1f} |", "",
         f"- AUC 差（時間內 − 時間外）：**{a_in - a_oot:+.2f}**，95% CI {_ci(diff)[0]:+.2f} 至 {_ci(diff)[1]:+.2f}",
         f"- 平均配對分數差的差：{sum(gin) / len(gin) - sum(gout) / len(gout):+.1f} 分，95% CI "
         f"{_ci(bgap)[0]:+.1f} 至 {_ci(bgap)[1]:+.1f}", "",
         "## 2. 模型說「知道後來出事」", "",
         f"- 問題公司 5 次中 ≥ 3 次說知道：{kT}/{len(qs)}；對照公司：{kC}/{len(qs)}",
         f"- 只用「知道」比例排序的 AUC：{_pair_auc(kflag, qs):.2f}"]
    know_q = [q for q in qs if knows[q + "T"] >= 3]
    nok_q = [q for q in qs if knows[q + "T"] < 3]
    for lab, g in (("問題公司被記得（≥ 3/5 說知道）", know_q), ("問題公司未被記得", nok_q)):
        if g:
            L.append(f"- {lab}：{len(g)} 對，AUC {_pair_auc(mean, g):.2f}，平均配對分數差 "
                     f"{sum(gap(mean, q) for q in g) / len(g):.1f}")
    # sensitivity: experiment B without pairs whose control filed a 4.02 since 2021 (same rule as here)
    S = {}
    cache = f"{CACHE}/submissions_summary.jsonl"
    L += ["", "## 3. 敏感度分析"]
    for g in ("A", "B"):
        r, _ = _load(f"{OUT}/{g}", f"{OUT}/key_{g}.tsv")
        m = {p: sum(d[p][0] for d in r.values()) / len(r) for p in next(iter(r.values()))}
        gq = sorted({p[:-1] for p in m})
        L.append(f"- 只用名單 {g}（{len(gq)} 對）：AUC {_pair_auc(m, gq):.2f}")
    dirty = args.oot_dirty.split(",") if args.oot_dirty else []
    if dirty:
        keep = [q for q in oq if q not in dirty]
        L.append(f"- 實驗 B 排除對照自 2021 年起曾申報 4.02 的配對（{', '.join(dirty)}）後：{len(keep)} 對，"
                 f"AUC {_pair_auc(om, keep):.2f}")
    inv = {v: k for k, v in key.items()}
    L += ["", "## 4. 逐對", "", "| 配對 | 問題公司 | 分數 | 知道 | 對照公司 | 分數 | 知道 |", "|---|---|---|---|---|---|---|"]
    for q in qs:
        L.append(f"| {q} | {inv[q + 'T']} | {mean[q + 'T']:.0f} | {knows[q + 'T']}/{len(runs)} | {inv[q + 'C']} | "
                 f"{mean[q + 'C']:.0f} | {knows[q + 'C']}/{len(runs)} |")
    open(f"{OUT}/evaluation.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L[:30]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name, fn in (("fetch", cmd_fetch), ("select", cmd_select), ("lists", cmd_lists), ("run", cmd_run)):
        sub.add_parser(name).set_defaults(fn=fn)
    e = sub.add_parser("evaluate"); e.add_argument("--oot-dirty", default=""); e.set_defaults(fn=cmd_evaluate)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

"""Round 9: out-of-time validation. Cases = 8-K Item 4.02 filed 2026-07-01..10-31 (after the model's cutoff).

Commands
  cases     pick 4.02 cases + Y0/Y-1 original 10-Ks (results/round9/cases.json)
  controls  same-SIC, size-matched controls without any 4.02 in the window (results/round9/pairs.json)
  build     10-K text -> redacted packets under neutral codes R9-xx (data/round9/redacted/)
  xbrl      as-filed XBRL values -> M/F features (results/round9/financial_features.csv)
  cards     verified facts -> J0 / J1 / PX cards, probe and MEM inputs (data/round9/cards/)
  evaluate  results/round9/evaluation.md
"""
import argparse
import csv
import gzip
import json
import math
import os
import random
import re
import subprocess
import time
from collections import defaultdict

from . import round5, round8
from .fin_extract import doc_lines
from .round3 import auc, auc_ci
from .round6_llm import _clean
from .redact import make_redactor
from .round7 import doc_values, _date

DATA = "data/round9"
OUT = "results/round9"
SEED = 20261102
UA = os.environ.get("SEC_UA", "research candace7907@gmail.com")
WINDOW = ("20260701", "20261031")


def _get(url, out=None):
    for attempt in range(5):
        r = subprocess.run(["curl", "-s", "--fail", "-m", "60", "-A", UA] + (["-o", out] if out else []) + [url],
                           capture_output=True)
        if r.returncode == 0:
            time.sleep(0.12)
            return r.stdout
        time.sleep(2 ** attempt)
    raise RuntimeError(url)


def submissions(cik):
    path = f"{DATA}/submissions/CIK{int(cik):010d}.json"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _get(f"https://data.sec.gov/submissions/CIK{int(cik):010d}.json", out=path)
    return json.load(open(path))


def companyfacts(cik):
    path = f"{DATA}/companyfacts/CIK{int(cik):010d}.json"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        try:
            _get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{int(cik):010d}.json", out=path)
        except RuntimeError:
            return {}
    return json.load(open(path))


def tenks(cik, before=None):
    """Original 10-K filings (accession, filing date, report date, xbrl flag), newest first."""
    s = submissions(cik)
    rec = s["filings"]["recent"]
    out = []
    for i, form in enumerate(rec["form"]):
        if form != "10-K":
            continue
        fd = rec["filingDate"][i].replace("-", "")
        if before and fd >= before:
            continue
        out.append({"acc": rec["accessionNumber"][i], "filed": fd, "period": rec["reportDate"][i].replace("-", ""),
                    "xbrl": bool(rec["isXBRL"][i]), "doc": rec["primaryDocument"][i]})
    return sorted(out, key=lambda x: x["filed"], reverse=True), s


def _items():
    rows = []
    for l in open(f"{DATA}/8k_items.tsv"):
        acc, form, cik, date, name, items, sic, fye = l.rstrip("\n").split("\t")
        rows.append(dict(acc=acc, form=form, cik=cik, date=date, name=name, items=items.split(","), sic=sic))
    return rows


def cases(args):
    rows = [r for r in _items() if "4.02" in r["items"] and WINDOW[0] <= r["date"] <= WINDOW[1]]
    first = {}
    for r in sorted(rows, key=lambda r: (r["date"], r["form"])):
        first.setdefault(r["cik"], r)
    print(f"{len(rows)} 4.02 filings, {len(first)} companies")
    ok, log = [], []
    for cik, r in sorted(first.items(), key=lambda kv: kv[1]["date"]):
        if r["sic"] == "6770":
            log.append((r["name"], "SIC 6770 blank check"))
            continue
        if not r["sic"]:
            log.append((r["name"], "no SIC"))
            continue
        ks, s = tenks(cik, before=r["date"])
        if len(ks) < 2:
            log.append((r["name"], f"{len(ks)} original 10-K before event"))
            continue
        y0, y1 = ks[0], ks[1]
        if not y0["xbrl"]:
            log.append((r["name"], "Y0 without XBRL"))
            continue
        if y0["period"] < "20240601":
            log.append((r["name"], f"Y0 too old ({y0['period']})"))
            continue
        ok.append(dict(name=s.get("name", r["name"]), cik=cik, sic=r["sic"], event_acc=r["acc"], event_date=r["date"],
                       y0_acc=y0["acc"], y0_period=y0["period"], y0_doc=y0["doc"], y1_acc=y1["acc"], y1_period=y1["period"]))
    rng = random.Random(SEED)
    chosen = ok if len(ok) <= 30 else sorted(rng.sample(ok, 30), key=lambda c: c["event_date"])
    os.makedirs(OUT, exist_ok=True)
    json.dump(chosen, open(f"{OUT}/cases.json", "w"), indent=1)
    with open(f"{OUT}/case_selection_log.tsv", "w") as fh:
        for n, why in log:
            fh.write(f"{n}\t{why}\n")
    print(f"{len(ok)} eligible, {len(chosen)} chosen; excluded {len(log)}")


def _frame_assets(period):
    d = _date(period)
    q = (d.month - 1) // 3 + 1
    path = f"{DATA}/frames/Assets_CY{d.year}Q{q}I.json"
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        _get(f"https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/USD/CY{d.year}Q{q}I.json", out=path)
    return {str(x["cik"]): x["val"] for x in json.load(open(path))["data"]}


def controls(args):
    cs = json.load(open(f"{OUT}/cases.json"))
    items = _items()
    flagged = {r["cik"] for r in items if "4.02" in r["items"]}
    sic_of = {}
    for r in items:
        if r["sic"]:
            sic_of[r["cik"]] = r["sic"]
    used, pairs = set(), []
    for c in cs:
        assets = _frame_assets(c["y0_period"])
        a0 = assets.get(str(int(c["cik"])))
        if not a0:
            # fall back to the case's own XBRL total assets
            f = companyfacts(c["cik"])
            vals, _ = doc_values(f, c["y0_acc"], c["y0_period"], int(c["y0_period"][:4]))
            a0 = vals.get("ta", {}).get(int(c["y0_period"][:4]))
            a0 = a0 * 1e6 if a0 else None
        if not a0:
            print("no assets for", c["name"])
            continue
        # revision (before any scoring): widen the SIC level when the closest same-industry firm is >3x off in size
        pool, digits = [], 4
        for digits in (4, 3, 2):
            lvl = [k for k, s in sic_of.items() if s[:digits] == c["sic"][:digits] and k not in flagged
                   and k != c["cik"] and k not in used and assets.get(str(int(k)), 0) > 0]
            lvl.sort(key=lambda k: abs(math.log(assets[str(int(k))] / a0)))
            if len(lvl) >= 3 and abs(math.log(assets[str(int(lvl[0]))] / a0)) <= math.log(3):
                pool = lvl
                break
            if len(lvl) > len(pool) or (lvl and pool and abs(math.log(assets[str(int(lvl[0]))] / a0)) < abs(math.log(assets[str(int(pool[0]))] / a0))):
                pool = lvl
        chosen = None
        for k in pool[:15]:
            ks, s = tenks(k)
            near = [x for x in ks if x["xbrl"] and abs((_date(x["period"]) - _date(c["y0_period"])).days) <= 92
                    and x["filed"] < WINDOW[1]]
            if not near:
                continue
            y0 = near[0]
            prev = [x for x in ks if x["filed"] < y0["filed"]]
            if not prev:
                continue
            chosen = dict(name=s.get("name"), cik=k, sic=sic_of[k], digits=digits, y0_acc=y0["acc"], y0_period=y0["period"],
                          y0_doc=y0["doc"], y1_acc=prev[0]["acc"], y1_period=prev[0]["period"],
                          assets_ratio=round(assets[str(int(k))] / a0, 3), pool=len(pool))
            break
        if not chosen:
            print("no control for", c["name"])
            continue
        used.add(chosen["cik"])
        pairs.append({"case": c, "control": chosen})
        print(c["name"], "->", chosen["name"], chosen["sic"], chosen["assets_ratio"], flush=True)
    json.dump(pairs, open(f"{OUT}/pairs.json", "w"), indent=1)
    print(len(pairs), "pairs")


def _rows():
    """(pid, name, cik, y0_acc, y0_period, y1_acc, y1_period, group, sic) like round7._pairs."""
    out = []
    for i, p in enumerate(json.load(open(f"{OUT}/pairs.json")), 1):
        for tag, side, grp in (("T", p["case"], "treatment"), ("C", p["control"], "control")):
            out.append((f"P{i:02d}{tag}", side["name"], side["cik"], side["y0_acc"], side["y0_period"], side["y1_acc"],
                        side["y1_period"], grp, side["sic"]))
    return out


def code_map():
    pids = [r[0] for r in _rows()]
    rng = random.Random(SEED + 9)
    rng.shuffle(pids)
    return {pid: f"R9-{i:02d}" for i, pid in enumerate(pids, 1)}


def build(args):
    os.makedirs(f"{DATA}/redacted", exist_ok=True)
    cmap = code_map()
    for pid, name, cik, a0, p0, a1, p1, group, sic in _rows():
        code = cmap[pid]
        if os.path.exists(f"{DATA}/redacted/{code}.txt"):
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
        core = re.sub(r"(?i),?\s*(inc\.?|corp\.?|corporation|ltd\.?|limited|holdings?|company|co\.|/de/|group|plc|n\.v\.)\b", "", name)
        core = re.sub(r"\s+", " ", core).strip(" ,.")
        aliases = [a for a in sorted({name, name.title(), core, core.title(), core.upper(), core.split()[0]}, key=len, reverse=True)
                   if len(a) >= 3]
        for a in aliases:
            if " " in a or a.lower() not in round8.GENERIC:
                text = re.sub(rf"(?i)(?<![A-Za-z]){re.escape(a)}(?![a-z])", "[COMPANY]", text)
        text = re.sub(r"(?im)^\S+\.(?:htm|html|txt)\s*$", "", text)
        text = re.sub(r"\b\d{2}-\d{7}\b", "[EIN]", text)
        text = re.sub(r"\(?\b\d{3}\)?[ .-]\d{3}-\d{4}\b", "[PHONE]", text)
        text = re.sub(r"\b0{2,3}\d-\d{4,5}\b", "[FILE NO]", text)
        red = make_redactor(aliases, int(p0[:4]), text)(text)
        open(f"{DATA}/redacted/{code}.txt", "w", encoding="utf-8").write(red)
        with gzip.open(f"{DATA}/redacted/{code}.txt.gz", "wt", encoding="utf-8") as fh:
            fh.write(red)
        print(code, len(red), flush=True)


def xbrl(args):
    vals = defaultdict(lambda: defaultdict(lambda: defaultdict(dict)))
    key, lines = {}, []
    for pid, name, cik, a0, p0, a1, p1, group, sic in _rows():
        f = companyfacts(cik)
        y0 = int(p0[:4])
        for acc, period, label in ((a0, p0, y0), (a1, p1, y0 - 1)):
            v, _ = doc_values(f, acc, period, label)
            for item, cols in v.items():
                for col, x in cols.items():
                    vals[pid][label][item][col] = x
                    lines.append([pid, label, col, item, x])
        bank = sic[:2] in ("60", "61", "62", "63", "64", "67")
        key[pid] = {"name": name, "cik": "none", "year": y0, "group": group, "industry": "financial" if bank else sic, "sic": sic}
    notes = defaultdict(lambda: defaultdict(str))
    feats = round5.features(vals, notes, key, None)
    with open(f"{OUT}/financial_features.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(feats[0].keys()))
        w.writeheader()
        w.writerows(feats)
    with open(f"{OUT}/xbrl_values.tsv", "w") as fh:
        fh.write("pid\tdoc_year\tcol_year\titem\tvalue\n")
        for l in lines:
            fh.write("\t".join(map(str, l)) + "\n")
    print(len(feats), "firms with features")


def cards(args):
    cmap = code_map()
    facts = json.load(open(f"{OUT}/facts_verified.json"))
    ratios = {}
    for row in csv.DictReader(open(f"{OUT}/financial_features.csv")):
        vals = {}
        for rid, key, _ in round8.RATIOS:
            try:
                vals[rid] = round(float(row.get(key, "")), 2)
            except ValueError:
                vals[rid] = "n/a"
        ratios[row["pid"]] = vals
    rows = {r[0]: r for r in _rows()}
    os.makedirs(f"{DATA}/cards", exist_ok=True)
    for pid, code in cmap.items():
        f, r, sec = facts[code], ratios.get(pid, {}), round8.sector(rows[pid][8])
        open(f"{DATA}/cards/{code}_J0.txt", "w").write(round8.card_text(code, f, r, sec))
        open(f"{DATA}/cards/{code}_J1.txt", "w").write(
            round8.card_text(code, f, r, sec, f"{rows[pid][1]} (fiscal year ending {rows[pid][4][:4]}-{rows[pid][4][4:6]}-{rows[pid][4][6:]})"))
    by_code = sorted(cmap.items(), key=lambda kv: kv[1])
    chosen = [c for c in by_code if c[0].endswith("T")][:6] + [c for c in by_code if c[0].endswith("C")][:6]
    pert = {}
    for pid, code in chosen:
        f = dict(facts[code])
        if pid.endswith("T"):
            changed = {k: v for k, v in round8.NEUTRAL.items() if f.get(k) != v}
            f.update(round8.NEUTRAL)
            if f.get("F03") == "adverse":
                f["F03"] = changed["F03"] = "unqualified"
            kind = "neutralised"
        else:
            changed = {k: v for k, v in round8.ADDED.items() if f.get(k) != v}
            f.update(round8.ADDED)
            if f.get("F03") == "unqualified":
                f["F03"] = changed["F03"] = "adverse"
            kind = "red_flags_added"
        open(f"{DATA}/cards/{code}_PX.txt", "w").write(round8.card_text(code, f, ratios.get(pid, {}), round8.sector(rows[pid][8])))
        pert[code] = {"kind": kind, "changed": changed}
    json.dump(pert, open(f"{DATA}/cards/perturbation.json", "w"), indent=1)
    codes = [c for _, c in by_code]
    rng = random.Random(SEED + 10)
    mixed = codes[:]
    rng.shuffle(mixed)
    half = len(mixed) // 2
    for i, part in enumerate((mixed[:half], mixed[half:]), 1):
        open(f"{DATA}/cards/probe_open_{i}.txt", "w").write("\n\n".join(open(f"{DATA}/cards/{c}_J0.txt").read() for c in part))
    print("cards", len(cmap), "perturbed", len(pert))


def memory_list(args):
    rows = _rows()
    os.makedirs(f"{DATA}/cards", exist_ok=True)
    mem = sorted(f"{r[1]} — annual report for fiscal year ending {r[4][:4]}-{r[4][4:6]}-{r[4][6:]}" for r in rows)
    open(f"{DATA}/cards/memory_only.txt", "w").write("\n".join(mem) + "\n")
    print(len(mem))


def covers(args):
    """Does the 4.02 8-K text mention the Y0 fiscal year? (secondary analysis flag)"""
    out = {}
    for p in json.load(open(f"{OUT}/pairs.json")):
        c = p["case"]
        acc = c["event_acc"]
        raw = _get(f"https://www.sec.gov/Archives/edgar/data/{int(c['cik'])}/{acc.replace('-', '')}/{acc}.txt").decode("utf-8", "ignore")
        body = raw.split("<DOCUMENT>")[1] if "<DOCUMENT>" in raw else raw
        text = re.sub(r"<[^>]+>", " ", body)
        text = re.sub(r"&#160;|&nbsp;", " ", text)
        text = re.sub(r"\s+", " ", text)
        y = c["y0_period"][:4]
        hit = bool(re.search(rf"(fiscal (year )?{y}|year ended [A-Za-z]+ \d{{1,2}}, {y}|{y} annual|{y} Form 10-K|December 31, {y})", text))
        m = re.search(r"Item 4\.02.{0,1500}", text)
        out[c["cik"]] = {"covers_y0": int(hit), "excerpt": m.group(0)[:1500] if m else text[:1500]}
    json.dump(out, open(f"{OUT}/covers_y0.json", "w"), indent=1)
    print(sum(v["covers_y0"] for v in out.values()), "/", len(out), "cover Y0")


def _load_judge(cond):
    import glob
    out = {}
    for f in glob.glob(f"{DATA}/judge/{cond}/R9-*.json"):
        out[os.path.basename(f)[:-5]] = json.load(open(f))
    return out


def _boot_mei(j0, j1, is_t, n=2000):
    """Memory-effect index (mean J1-J0 among cases minus among controls) with bootstrap CI."""
    t = [j1[c] - j0[c] for c in j1 if c in j0 and is_t[c]]
    k = [j1[c] - j0[c] for c in j1 if c in j0 and not is_t[c]]
    if not t or not k:
        return None
    rng = random.Random(1)
    est = sum(t) / len(t) - sum(k) / len(k)
    bs = sorted(sum(rng.choice(t) for _ in t) / len(t) - sum(rng.choice(k) for _ in k) / len(k) for _ in range(n))
    return est, bs[int(0.025 * n)], bs[int(0.975 * n) - 1], sum(t) / len(t), sum(k) / len(k)


def evaluate(args):
    cmap = code_map()
    inv = {c: p for p, c in cmap.items()}
    rows = {r[0]: r for r in _rows()}
    is_t = {c: inv[c].endswith("T") for c in inv}
    name_of = {cmap[p]: rows[p][1] for p in rows}
    j0raw, j1raw, pxraw = _load_judge("J0"), _load_judge("J1"), _load_judge("PX")
    j0 = {c: float(d["risk_score"]) for c, d in j0raw.items()}
    j1 = {c: float(d["risk_score"]) for c, d in j1raw.items()}
    mem = {}
    if os.path.exists(f"{DATA}/probe/memory.json"):
        for m in json.load(open(f"{DATA}/probe/memory.json")):
            pid = next((p for p in rows if m["company"].startswith(rows[p][1])), None)
            if pid:
                mem[cmap[pid]] = m
    cov = json.load(open(f"{OUT}/covers_y0.json")) if os.path.exists(f"{OUT}/covers_y0.json") else {}
    feats = {r["pid"]: r for r in csv.DictReader(open(f"{OUT}/financial_features.csv"))}
    rep = ["# 第九輪評估輸出（程式產生）", "", f"配對數：{len(rows) // 2}", ""]

    def line(name, s, keep=None):
        cs = [c for c in s if keep is None or keep(c)]
        pos = [s[c] for c in cs if is_t[c]]
        neg = [s[c] for c in cs if not is_t[c]]
        if not pos or not neg:
            return f"| {name} | – | – | – | 0 |"
        lo, hi = auc_ci(pos, neg)
        w = t = l = 0
        for p in rows:
            if p.endswith("T"):
                a, b = cmap[p], cmap[p[:-1] + "C"]
                if a in cs and b in cs:
                    w += s[a] > s[b]; t += s[a] == s[b]; l += s[a] < s[b]
        return f"| {name} | {auc(pos, neg):.2f} | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} | {len(pos)}+{len(neg)} |"

    def feat(key):
        out = {}
        for c in inv:
            v = feats.get(inv[c], {}).get(key, "")
            try:
                out[c] = float(v)
            except ValueError:
                pass
        return out

    known = {c for c, m in mem.items() if str(m.get("knows_later_problems")).lower() == "true"}
    pair_known = set()
    for p in rows:
        if p.endswith("T") and cmap[p] in known:
            pair_known |= {cmap[p], cmap[p[:-1] + "C"]}
    covered = set()
    for p in rows:
        if p.endswith("T") and cov.get(rows[p][2], {}).get("covers_y0"):
            covered |= {cmap[p], cmap[p[:-1] + "C"]}
    rep += ["## 成效", "", "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | n（問題+對照） |", "|---|---|---|---|---|"]
    rep.append(line("H1 J0 事實卡（無名稱）", j0))
    rep.append(line("J0，排除 MEM 說知道的配對", j0, lambda c: c not in pair_known))
    rep.append(line("J0，只看 4.02 涵蓋 Y0 的配對", j0, lambda c: c in covered))
    rep.append(line("J1 事實卡 + 真實名稱", j1))
    rep.append(line("MEM 只有名稱", {c: float(m["risk_score"]) for c, m in mem.items()}))
    rep.append(line("F-score（程式）", feat("F")))
    rep.append(line("M-score（程式）", feat("M")))
    rep += ["", "## 目標一：模型知不知道結果", ""]
    kt = sum(1 for c in known if is_t[c]); nt = sum(1 for c in mem if is_t[c])
    kc = sum(1 for c in known if not is_t[c]); nc = sum(1 for c in mem if not is_t[c])
    rep.append(f"- K1 MEM 探針說知道後來有問題：問題組 {kt}/{nt}，對照組 {kc}/{nc}（標準：問題組 ≤ 20%）")
    rep.append(f"  - 知道的公司：{sorted(name_of[c] for c in known)}")
    k2 = [c for c, d in j0raw.items() if str(d.get("knows_later_problems")).lower() == "true"]
    g2 = [c for c, d in j0raw.items() if d.get("guess")]
    rep.append(f"- K2 J0 評分者自述知道後來有問題：{len(k2)}/{len(j0raw)}；有猜名稱：{len(g2)}")
    k1j = [c for c, d in j1raw.items() if str(d.get("knows_later_problems")).lower() == "true"]
    rep.append(f"- J1（看得到名稱）自述知道後來有問題：問題組 {sum(is_t[c] for c in k1j)}，對照組 {sum(not is_t[c] for c in k1j)}")
    mei = _boot_mei(j0, j1, is_t)
    if mei:
        rep.append(f"- H3 記憶效應指數（J1 − J0：問題組 {mei[3]:+.1f}，對照組 {mei[4]:+.1f}）= {mei[0]:+.1f}，95% CI {mei[1]:+.1f} 至 {mei[2]:+.1f}（第八輪 +16.6）")
    import glob
    opens = {}
    for f in glob.glob(f"{DATA}/probe/open_*.json"):
        opens.update(json.load(open(f)))
    if opens:
        hits = [c for c, d in opens.items() if c in name_of and any(round8._name_hit(g, name_of[c]) for g in d.get("guesses", []))]
        rep.append(f"- 開放式辨識猜中：{len(hits)}/{len(opens)} {[name_of[c] for c in hits]}")
    rep += ["", "## H4 內容擾動", ""]
    if pxraw and os.path.exists(f"{DATA}/cards/perturbation.json"):
        pert = json.load(open(f"{DATA}/cards/perturbation.json"))
        good, ds = 0, []
        rep += ["| 卡 | 擾動 | 改動欄位 | J0 | 擾動後 | Δ | 方向正確 |", "|---|---|---|---|---|---|---|"]
        for c, info in sorted(pert.items()):
            if c in pxraw and c in j0:
                d = float(pxraw[c]["risk_score"]) - j0[c]
                ok = d < 0 if info["kind"] == "neutralised" else d > 0
                good += ok; ds.append(abs(d))
                rep.append(f"| {c} | {info['kind']} | {', '.join(info['changed']) or '（無）'} | {j0[c]:.0f} | {j0[c] + d:.0f} | {d:+.0f} | {'是' if ok else '否'} |")
        ds.sort()
        rep.append(f"\n方向正確 {good}/{len(ds)}；|Δ| 中位數 {ds[len(ds) // 2] if ds else float('nan'):.0f}")
    # Supplementary (not pre-registered): does J0 add information beyond the name-only prior (MEM)?
    memsc = {c: float(m["risk_score"]) for c, m in mem.items()}
    pairs = json.load(open(f"{OUT}/pairs.json"))
    tc = [(cmap[f"P{i:02d}T"], cmap[f"P{i:02d}C"], p["control"].get("assets_ratio")) for i, p in enumerate(pairs, 1)]
    rep += ["", "## 補充分析（非預先登錄）", ""]
    size_ok = set()
    for a, b, r in tc:
        if r and 1 / 3 <= float(r) <= 3:
            size_ok |= {a, b}
    rep.append("| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | n（問題+對照） |")
    rep.append("|---|---|---|---|---|")
    rep.append(line("J0，只看規模差 ≤ 3 倍的配對", j0, lambda c: c in size_ok))
    mem_wrong = set()
    for a, b, _ in tc:
        if a in memsc and b in memsc and memsc[a] <= memsc[b]:
            mem_wrong |= {a, b}
    rep.append(line("J0，只看 MEM 排錯或平手的配對", j0, lambda c: c in mem_wrong))
    both = [c for c in j0 if c in memsc]
    x = [memsc[c] for c in both]; y = [j0[c] for c in both]
    mx, my = sum(x) / len(x), sum(y) / len(y)
    beta = sum((a - mx) * (b - my) for a, b in zip(x, y)) / sum((a - mx) ** 2 for a in x)
    resid = {c: j0[c] - (my + beta * (memsc[c] - mx)) for c in both}
    rep.append(line("J0 扣除 MEM 線性部分後的殘差", resid))
    rep.append("")
    rep.append(f"- J0 與 MEM 的 Spearman ρ（54 張卡）= {round8.spearman(x, y):.2f}；J0 對 MEM 的斜率 = {beta:.2f}")
    rep.append(f"- 規模差 > 3 倍的配對：{[(name_of[a], f'{float(r):.3g}x') for a, b, r in tc if r and not 1 / 3 <= float(r) <= 3]}")
    rep += ["", "## 逐卡", "", "| 卡 | 組 | 公司 | MEM | MEM 知道 | J0 | J1 | F | 4.02 涵蓋 Y0 |", "|---|---|---|---|---|---|---|---|---|"]
    fsc = feat("F")

    def fmt(d, c, spec=".0f"):
        return format(d[c], spec) if c in d else ""

    for c in sorted(inv):
        p = inv[c]
        cv = cov.get(rows[p][2], {}).get("covers_y0", "") if p.endswith("T") else ""
        cells = [c, "問題" if is_t[c] else "對照", name_of[c], mem.get(c, {}).get("risk_score", ""),
                 "是" if c in known else "", fmt(j0, c), fmt(j1, c), fmt(fsc, c, ".2f"), cv]
        rep.append("| " + " | ".join(str(x) for x in cells) + " |")
    open(f"{OUT}/evaluation.md", "w").write("\n".join(rep) + "\n")
    print("\n".join(rep))


def verify(args):
    """Quote verification, same rule as round 8."""
    cmap = code_map()
    verified, stats = {}, {}
    for pid, code in sorted(cmap.items(), key=lambda kv: kv[1]):
        path = f"{DATA}/extract/{code}.json"
        if not os.path.exists(path):
            print("missing", code)
            continue
        raw = json.load(open(path))
        text = round8._norm(open(f"{DATA}/redacted/{code}.txt", encoding="utf-8").read())
        out, n_claims, n_fail = {}, 0, 0
        for fid, key, desc, allowed in round8.FIELDS:
            ans = raw.get(fid) or raw.get(key) or {}
            val = ans.get("value", "not_found") if isinstance(ans, dict) else ans
            quote = ans.get("quote", "") if isinstance(ans, dict) else ""
            if isinstance(val, list) and allowed != "number":
                val = [v for v in val if v in allowed]
            if val in ("not_found", "not_disclosed", None, "", []):
                out[fid] = "not_found"
                continue
            neg = set(val) <= round8.NEGATIVE if isinstance(val, list) else val in round8.NEGATIVE
            if not str(quote).strip() and neg:
                out[fid] = sorted(val) if isinstance(val, list) else val
                continue
            n_claims += 1
            pieces = [p for p in re.split(r"\s*(?:\.\.\.|…)\s*", quote) if p.strip()]
            if not (pieces and all(round8._norm(p) in text for p in pieces)):
                n_fail += 1
                out[fid] = "not_found"
                continue
            if allowed == "number":
                try:
                    out[fid] = round(float(str(val).strip("% ")))
                except ValueError:
                    out[fid] = "not_found"
            elif isinstance(val, list):
                out[fid] = sorted(val) or "not_found"
            else:
                out[fid] = val if val in allowed else "not_found"
        verified[code] = out
        stats[code] = {"claims": n_claims, "quote_failures": n_fail}
    json.dump(verified, open(f"{OUT}/facts_verified.json", "w"), indent=1)
    json.dump(stats, open(f"{OUT}/quote_verification.json", "w"), indent=1)
    print(len(stats), "filings,", sum(s["claims"] for s in stats.values()), "claims,", sum(s["quote_failures"] for s in stats.values()), "failures")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["cases", "controls", "build", "xbrl", "cards", "memory_list", "covers", "evaluate", "verify"])
    args = ap.parse_args()
    globals()[args.cmd](args)


if __name__ == "__main__":
    main()

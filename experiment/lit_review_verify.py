"""Phase 2 source verification for the integrative review (results/lit_review/protocol.md).

  python -m experiment.lit_review_verify            # checks every results/lit_review/phase2_bibliography/T*_sources.json

DOI -> Crossref /works/{doi}; arXiv ID -> arXiv API id_list. Title similarity (difflib ratio on normalized titles)
>= 0.70 and year within +/-1 -> VERIFIED; a resolving identifier with a different title -> DOI_MISMATCH /
ARXIV_MISMATCH; no identifier -> NEEDS_WEBSEARCH (checked by hand, outcome recorded in manual_checks.json);
lookup failure -> LOOKUP_FAILED. Writes phase2_verification/verification.json and .md.
"""
import difflib
import glob
import json
import os
import re
import subprocess
import time
import urllib.parse

B = "results/lit_review"
UA = "FraudAgentProposal research script"


def _get(url):
    p = subprocess.run(["curl", "-sS", "-L", "--max-time", "30", "-A", UA, url], capture_output=True)
    time.sleep(0.3)
    return p.stdout.decode("utf-8", "ignore")


def norm(t):
    t = re.sub(r"<[^>]+>", " ", t or "").lower()
    return re.sub(r"[^a-z0-9]+", " ", t).strip()


def sim(a, b):
    a, b = norm(a), norm(b)
    if min(len(a), len(b)) >= 10 and (a in b or b in a):   # main title without subtitle, or the reverse
        return 1.0
    return difflib.SequenceMatcher(None, a, b).ratio()


def crossref(doi):
    try:
        m = json.loads(_get("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/")))["message"]
    except (ValueError, KeyError):
        return None
    year = None
    for k in ("published-print", "published-online", "issued", "created"):
        if m.get(k, {}).get("date-parts") and m[k]["date-parts"][0][0]:
            year = m[k]["date-parts"][0][0]
            break
    return {"title": " ".join(m.get("title") or [""]), "year": year,
            "venue": " ".join(m.get("container-title") or []), "type": m.get("type")}


def arxiv(aid):
    x = _get("https://export.arxiv.org/api/query?id_list=" + urllib.parse.quote(re.sub(r"v\d+$", "", aid)))
    entries = re.findall(r"<entry>(.*?)</entry>", x, re.S)
    if not entries:
        return None
    e = entries[0]
    title = re.search(r"<title>(.*?)</title>", e, re.S)
    pub = re.search(r"<published>(\d{4})", e)
    return {"title": re.sub(r"\s+", " ", title.group(1)).strip() if title else "", "year": int(pub.group(1)) if pub else None}


def check(s):
    out = {"key": s.get("key"), "title": s.get("title"), "year": s.get("year"), "doi": s.get("doi"),
           "arxiv_id": s.get("arxiv_id")}
    for kind, ident, fn in (("doi", s.get("doi"), crossref), ("arxiv", s.get("arxiv_id"), arxiv)):
        if not ident:
            continue
        rec = fn(ident)
        if rec is None:
            out.setdefault("notes", []).append(f"{kind} lookup failed")
            continue
        r = sim(s.get("title", ""), rec["title"])
        yok = rec["year"] is None or s.get("year") is None or abs(int(rec["year"]) - int(s["year"])) <= 1
        out[f"{kind}_record_title"], out[f"{kind}_similarity"], out[f"{kind}_year"] = rec["title"], round(r, 3), rec["year"]
        if r >= 0.70 and yok:
            out["status"] = "VERIFIED"
            out["via"] = kind
            return out
        out["status"] = "DOI_MISMATCH" if kind == "doi" else "ARXIV_MISMATCH"
    out.setdefault("status", "NEEDS_WEBSEARCH" if not (s.get("doi") or s.get("arxiv_id")) else "LOOKUP_FAILED")
    return out


def main():
    manual = {}
    if os.path.exists(f"{B}/phase2_verification/manual_checks.json"):
        manual = json.load(open(f"{B}/phase2_verification/manual_checks.json"))
    res = {}
    for f in sorted(glob.glob(f"{B}/phase2_bibliography/T*_sources.json")):
        t = os.path.basename(f).split("_")[0]
        res[t] = []
        for s in json.load(open(f)):
            r = check(s)
            if r["status"] in ("NEEDS_WEBSEARCH", "LOOKUP_FAILED") and r["key"] in manual:
                r["status"], r["via"] = manual[r["key"]]["status"], "websearch"
                r["evidence"] = manual[r["key"]].get("evidence")
            res[t].append(r)
            print(t, r["key"], r["status"], r.get("via", ""), r.get("doi_similarity", r.get("arxiv_similarity", "")), flush=True)
    os.makedirs(f"{B}/phase2_verification", exist_ok=True)
    json.dump(res, open(f"{B}/phase2_verification/verification.json", "w"), indent=1, ensure_ascii=False)
    L = ["# 來源查核結果（Phase 2，source verification）", "",
         "依 `results/lit_review/protocol.md` 的查核規則。Semantic Scholar 無 API 金鑰，ARS 的 Tier 0 依降級規則略過（[S2-API-UNAVAILABLE]）。", "",
         "| 主題 | 篇數 | VERIFIED（DOI） | VERIFIED（arXiv） | PLAUSIBLE（WebSearch） | 不符／失敗／待查 |", "|---|---|---|---|---|---|"]
    for t, rs in res.items():
        c = lambda f: sum(1 for r in rs if f(r))
        bad = [r["key"] for r in rs if r["status"] not in ("VERIFIED", "PLAUSIBLE")]
        L.append(f"| {t} | {len(rs)} | {c(lambda r: r.get('via') == 'doi')} | {c(lambda r: r.get('via') == 'arxiv')} | "
                 f"{c(lambda r: r['status'] == 'PLAUSIBLE')} | {len(bad)}{'：' + '、'.join(bad) if bad else ''} |")
    L += ["", "## 逐筆", "", "| 主題 | key | 狀態 | 方式 | 題名相似度 | 查到的題名 |", "|---|---|---|---|---|---|"]
    for t, rs in res.items():
        for r in rs:
            rt = r.get("doi_record_title") or r.get("arxiv_record_title") or r.get("evidence") or ""
            simv = r.get("doi_similarity", r.get("arxiv_similarity", ""))
            L.append(f"| {t} | {r['key']} | {r['status']} | {r.get('via', '')} | {simv} | {str(rt)[:90]} |")
    open(f"{B}/phase2_verification/verification.md", "w", encoding="utf-8").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()

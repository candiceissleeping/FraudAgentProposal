"""Experiment 3: grade the models' "knows later problems" claims against SEC records (protocol: results/mem_factcheck).

  python -m experiment.mem_factcheck grade        # one no-tool Opus session per company, raw logs kept
  python -m experiment.mem_factcheck summarize    # verdicts, M1-M3 per model, agreement with the manual audit

The grader sees the coordinator's fact sheet, the AAER text (round 8 cases) and the EDGAR 8-K Item 4.02 excerpts,
plus every claim about that company with claim ids only (no model names). It fills four fields; the verdict is
computed here from the pre-registered rules.
"""
import collections
import csv
import json
import os
import random
import sys

from experiment.mem_isolated import HARDENED, claude, load_events, parse_scores, verify

D, R = "data/mem_factcheck", "results/mem_factcheck"
FIELDS = {"issue": ("match", "partial", "mismatch", "not_stated"), "consequence": ("correct", "incorrect", "not_stated"),
          "contradiction": ("yes", "no"), "record_exists": ("yes", "no")}

RUBRIC = """You are checking claims that AI models made from memory about a company's later accounting problems.
Use ONLY the fact sheet and source documents below as the truth. Do not use your own knowledge of the company.

The question the models answered: for the annual report of {company} for the fiscal year ended {fy}, do you know of
later accounting problems, restatements or SEC enforcement involving that period? Each claim below is a model's short
reason for answering "yes".

For each claim fill four fields:
- issue: the kind of accounting problem the claim names, compared with the fact sheet.
  match = same kind (e.g. revenue recognition, related-party transactions, lease accounting, intersegment sales);
  partial = related or only part of it, without conflict; mismatch = a different kind;
  not_stated = names no kind of accounting problem (only "material weaknesses", "control issues", "accounting
  problems", "restatement", "late filings" and the like count as not_stated).
- consequence: the later events the claim states (restatement / non-reliance, SEC investigation or enforcement,
  delayed filings): correct = consistent with the record; incorrect = states such an event that the record does not
  show; not_stated = states none.
- contradiction: yes if the claim states something that conflicts with the record on the facts the record covers:
  the kind of problem, the misstatement period, whether a restatement / non-reliance happened, whether SEC enforcement
  happened. A restatement or SEC enforcement that the record does not show counts as a contradiction. Events the record
  does not cover (bankruptcy, delisting, DOJ inquiries, auditor resignation, going concern, lawsuits) do NOT count.
  A claimed period that includes the asked fiscal year is not a period error; a date of a real event that is off by
  less than one year is not a contradiction.
- record_exists: copy the value given in the fact sheet.

Reply with only a JSON list, one entry per claim, and nothing else:
[{{"id": "<claim id>", "issue": "...", "consequence": "...", "contradiction": "yes|no", "record_exists": "yes|no",
"reason": "one short sentence"}}, ...]

=== FACT SHEET ===
{facts}
record_exists = {record_exists}

=== EDGAR 8-K ITEM 4.02 FILINGS BEFORE 2026-07-01 (excerpts) ===
{edgar}

=== AAER TEXT ===
{aaer}

=== CLAIMS ===
{claims}
"""


def verdict(g):
    if g["record_exists"] == "no":
        return "unsupported"
    if g["contradiction"] == "no" and g["issue"] in ("match", "partial"):
        return "correct_specific"
    if g["contradiction"] == "no" and g["issue"] == "not_stated" and g["consequence"] == "correct":
        return "correct_vague"
    return "wrong"


def _claims():
    return list(csv.DictReader(open(f"{R}/claims.csv", encoding="utf-8")))


def _valid(grades, ids):
    try:
        return (sorted(g["id"] for g in grades) == sorted(ids)
                and all(g[f] in opts for g in grades for f, opts in FIELDS.items()))
    except (KeyError, TypeError):
        return False


def cmd_grade():
    facts = json.load(open(f"{D}/facts.json", encoding="utf-8"))
    edgar = json.load(open(f"{D}/edgar/records.json", encoding="utf-8"))
    by = collections.defaultdict(list)
    for c in _claims():
        by[c["pid"]].append(c)
    os.makedirs(f"{R}/grader/raw", exist_ok=True)
    for pid, cs in sorted(by.items()):
        out = f"{R}/grader/{pid}.json"
        if os.path.exists(out):
            continue
        f = facts[pid]
        cs = sorted(cs, key=lambda c: c["claim_id"])
        random.Random(f"20261109{pid}").shuffle(cs)
        rec = edgar[pid]
        ed = "\n\n".join(f"- {x['form']} filed {x['date']}: {x['item_402_text'][:2500]}" for x in rec["filings_402"]) or "none"
        ed += f"\n(10-K/A filed: {', '.join(rec['amended_10k']) or 'none'}; late-filing notices: {len(rec['late_notices'])})"
        aaer = (open(f"{D}/aaer/AAER-{f['aaer']}.txt", encoding="utf-8").read() if f.get("aaer")
                else "No AAER names this company in the SEC AAER listing before 2026-07-01.")
        prompt = RUBRIC.format(company=cs[0]["company"], fy=cs[0]["fiscal_year_end"], facts=f["facts"],
                               record_exists=f["record_exists"], edgar=ed, aaer=aaer,
                               claims="\n".join(f'{c["claim_id"]}: {c["basis"]}' for c in cs))
        raw = f"{R}/grader/raw/{pid}.jsonl"
        for attempt in (1, 2):
            v = verify(claude(prompt, HARDENED, raw))
            grades = parse_scores(v["answer"])
            if v["all_pass"] and _valid(grades, [c["claim_id"] for c in cs]):
                break
            os.replace(raw, f"{R}/grader/raw/{pid}_failed{attempt}.jsonl")
            grades = None
        json.dump({"pid": pid, "attempts": attempt, "checks_pass": v["all_pass"], "grades": grades},
                  open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(pid, "ok" if grades else "FAILED", f"{len(cs)} claims, attempts={attempt}", flush=True)


def cmd_summarize():
    facts = json.load(open(f"{D}/facts.json", encoding="utf-8"))
    claims = {c["claim_id"]: c for c in _claims()}
    grades = {}
    for c in claims.values():
        g = json.load(open(f"{R}/grader/{c['pid']}.json"))
        assert g["checks_pass"] and g["grades"], c["pid"]
        for x in g["grades"]:
            grades[x["id"]] = x
    copied_wrong = [i for i, g in grades.items() if g["record_exists"] != facts[claims[i]["pid"]]["record_exists"]]
    for i in grades:   # record_exists is set by the fact sheet, not by the grader
        grades[i]["record_exists"] = facts[claims[i]["pid"]]["record_exists"]
    rows = []
    for i, c in sorted(claims.items()):
        g = grades[i]
        rows.append({**c, **{f: g[f] for f in FIELDS}, "verdict": verdict(g), "grader_reason": g.get("reason", "")})
    with open(f"{R}/graded_claims.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)

    def tab(sel):
        cnt = collections.Counter(r["verdict"] for r in sel)
        n = len(sel)
        return n, cnt
    L = ["# 實驗 3：模型「知道出事」自述的查核結果", "",
         f"共 {len(rows)} 則自述；評分者為每家公司一個無工具的 Opus 5.5 session（全部通過 7 項無上網檢查），不知道自述來自哪個模型。", ""]
    L += ["## M1、M2：第八輪問題公司的「知道」自述", "",
          "| 模型 | 則數 | 正確且具體 | 正確但籠統 | **正確合計（M1）** | 錯誤 | 無紀錄支持 |", "|---|---|---|---|---|---|---|"]
    for m in ("Opus", "Sonnet", "Haiku"):
        sel = [r for r in rows if r["model"] == m and r["sample"] == "round8" and r["group"] == "T"]
        n, c = tab(sel)
        ok = c["correct_specific"] + c["correct_vague"]
        L.append(f"| {m} | {n} | {c['correct_specific']}（{c['correct_specific']/n:.0%}） | {c['correct_vague']}（{c['correct_vague']/n:.0%}） | "
                 f"**{ok}（{ok/n:.0%}）** | {c['wrong']}（{c['wrong']/n:.0%}） | {c['unsupported']} |")
    L += ["", "## M3：第八輪對照公司與時間外樣本的「知道」自述", "",
          "| 模型 | 樣本／組 | 則數 | 有紀錄支持（正確） | 有紀錄但錯誤 | 無紀錄支持 |", "|---|---|---|---|---|---|"]
    for m in ("Opus", "Sonnet", "Haiku"):
        for s, g in (("round8", "C"), ("oot", "T"), ("oot", "C")):
            sel = [r for r in rows if r["model"] == m and r["sample"] == s and r["group"] == g]
            if not sel:
                continue
            n, c = tab(sel)
            ok = c["correct_specific"] + c["correct_vague"]
            L.append(f"| {m} | {s} {g} | {n} | {ok} | {c['wrong']} | {c['unsupported']}（{c['unsupported']/n:.0%}） |")
    L += ["", "## 逐家（第八輪問題公司，三個模型合計）", "", "| 公司 | 則數 | 正確且具體 | 正確但籠統 | 錯誤 |", "|---|---|---|---|---|"]
    for pid in sorted({r["pid"] for r in rows if r["sample"] == "round8" and r["group"] == "T"}):
        sel = [r for r in rows if r["pid"] == pid]
        n, c = tab(sel)
        L.append(f"| {sel[0]['company']} | {n} | {c['correct_specific']} | {c['correct_vague']} | {c['wrong']} |")
    L += ["", "## 逐家（對照公司與時間外樣本）", "", "| pid | 公司 | 年度有紀錄 | 則數（Opus / Sonnet / Haiku） | 錯誤 | 無紀錄支持 |", "|---|---|---|---|---|---|"]
    for pid in sorted({r["pid"] for r in rows if not (r["sample"] == "round8" and r["group"] == "T")}):
        sel = [r for r in rows if r["pid"] == pid]
        n, c = tab(sel)
        per = " / ".join(str(sum(r["model"] == m for r in sel)) for m in ("Opus", "Sonnet", "Haiku"))
        L.append(f"| {pid} | {sel[0]['company']} | {facts[pid]['record_exists']} | {per} | {c['wrong']} | {c['unsupported']} |")
    audit = list(csv.DictReader(open(f"{R}/manual_audit.csv", encoding="utf-8")))
    agree = {f: sum(a[f] == grades[a["claim_id"]][f] for a in audit) for f in ("issue", "consequence", "contradiction")}
    va = sum(verdict(a) == verdict(grades[a["claim_id"]]) for a in audit)
    L += ["", "## 人工抽查一致率", "",
          f"抽查 {len(audit)} 則（種子 20261109，人工判定在評分者執行前 commit）。", "",
          "| 欄位 | 一致 |", "|---|---|"]
    L += [f"| {f} | {k}/{len(audit)}（{k/len(audit):.0%}） |" for f, k in agree.items()]
    L.append(f"| **總判定** | **{va}/{len(audit)}（{va/len(audit):.0%}）** |")
    dis = [(a["claim_id"], verdict(a), verdict(grades[a["claim_id"]])) for a in audit if verdict(a) != verdict(grades[a["claim_id"]])]
    if dis:
        L += ["", "總判定不一致的自述（人工 → 評分者）：" + "；".join(f"{i} {x} → {y}" for i, x, y in dis)]
    L += ["", f"評分者抄錯 record_exists 的則數：{len(copied_wrong)}（已改用事實表的值）"]
    open(f"{R}/evaluation.md", "w", encoding="utf-8").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    {"grade": cmd_grade, "summarize": cmd_summarize}.get(sys.argv[1] if len(sys.argv) > 1 else "",
                                                          lambda: sys.exit(__doc__))()

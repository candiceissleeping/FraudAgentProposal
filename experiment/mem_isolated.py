"""Round 8 MEM (memory-only) rerun in a Claude Code session that has no way to reach the internet, plus a check.

Why this setup
  The model can only reach the web through a tool call. `claude -p --tools ""` starts a session with no built-in
  tools (so no WebSearch, WebFetch, Bash, Read, Agent, Skill, ToolSearch ...), `--strict-mcp-config` with no
  --mcp-config gives no MCP servers, `--setting-sources ""` skips user/project/local settings (CLAUDE.md, hooks,
  permissions, auto memory), and each run starts in a new empty directory. The model cannot read the repo's labels
  or results either, because it has no file tools.

What is checked for every run (all must pass; anything missing counts as a failure)
  tools_empty          system/init event lists no tools
  mcp_empty            system/init event lists no MCP servers
  no_tool_blocks       no tool_use / server_tool_use / *_tool_result block in any assistant message
  server_web_zero      result.usage.server_tool_use.web_search_requests == 0 and web_fetch_requests == 0, and
                       modelUsage[*].webSearchRequests == 0 (counted by the API server, not by the model).
                       Both are needed: Claude Code's WebSearch runs as a separate call on another model
                       (claude-haiku-5-5 on 2026-11-06), so a search shows up only in modelUsage[that model],
                       while result.usage stays 0 (seen in the canary_web_allowed positive control).
  no_subagents         result.subagent_stats.spawned == 0
  single_turn          result.num_turns == 1
  completed            result.subtype == "success" and not is_error

Usage
  python -m experiment.mem_isolated canary                       # positive control + post-cutoff question
  python -m experiment.mem_isolated run --runs 5 --seed 20261106 # MEM runs, shuffled list per run
  python -m experiment.mem_isolated verify results/mem_isolated/raw/*.jsonl
  python -m experiment.mem_isolated evaluate                      # after raw runs are committed
  Out-of-time sample (round 9, 27 pairs of 8-K Item 4.02 filers, events after the model's cutoff):
  python -m experiment.mem_isolated run --out results/mem_isolated_oot --input data/mem_isolated_oot/input_round9.txt \
      --prompt data/mem_isolated_oot/prompt.md --runs 5 --seed 20261107
"""
import argparse
import csv
import glob
import hashlib
import json
import os
import random
import re
import subprocess
import sys
import tempfile

OUT = "results/mem_isolated"
PROMPT = "data/mem_isolated/prompt.md"
INPUT = "data/mem_isolated/input_round8.txt"
MODEL = "claude-opus-5-5"
HARDENED = ["--tools", "", "--strict-mcp-config", "--setting-sources", "", "--no-session-persistence"]
STREAM = ["--output-format", "stream-json", "--verbose"]
CHECKS = ("tools_empty", "mcp_empty", "no_tool_blocks", "server_web_zero", "no_subagents", "single_turn", "completed")
# The model's training cutoff is June 2026, so it cannot know this without the web.
CANARY_Q = "2026 年 11 月 5 日台股加權指數（TAIEX）收盤是多少點？如果你無法確定，請直接說不知道，不要猜。"


# ---------------------------------------------------------------- verification (pure, unit-tested)
def verify(events):
    """Return {check: bool, ...} plus details for one stream-json session log. Missing evidence fails."""
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), None)
    result = next((e for e in reversed(events) if e.get("type") == "result"), None)
    tool_blocks, models = [], set()
    for e in events:
        if e.get("type") != "assistant":
            continue
        msg = e.get("message") or {}
        if msg.get("model"):
            models.add(msg["model"])
        for c in msg.get("content") or []:
            t = c.get("type", "")
            if t in ("tool_use", "server_tool_use", "mcp_tool_use") or t.endswith("tool_result"):
                tool_blocks.append({"type": t, "name": c.get("name"), "subagent": bool(e.get("parent_tool_use_id"))})
    out = {k: False for k in CHECKS}
    if init is not None:
        out["tools_empty"] = init.get("tools") == []
        out["mcp_empty"] = init.get("mcp_servers") == []
    out["no_tool_blocks"] = init is not None and not tool_blocks
    if result is not None:
        stu = (result.get("usage") or {}).get("server_tool_use")
        mu = result.get("modelUsage")
        out["server_web_zero"] = (
            isinstance(stu, dict) and stu.get("web_search_requests") == 0 and stu.get("web_fetch_requests") == 0
            and isinstance(mu, dict) and bool(mu) and all(v.get("webSearchRequests") == 0 for v in mu.values()))
        out["no_subagents"] = (result.get("subagent_stats") or {}).get("spawned") == 0
        out["single_turn"] = result.get("num_turns") == 1
        out["completed"] = result.get("subtype") == "success" and result.get("is_error") is False
    out["all_pass"] = all(out[k] for k in CHECKS)
    out["tool_blocks"] = tool_blocks
    out["init_model"] = (init or {}).get("model")
    out["served_models"] = sorted(models)
    out["claude_code_version"] = (init or {}).get("claude_code_version")
    out["web_search_requests"] = (((result or {}).get("usage") or {}).get("server_tool_use") or {}).get("web_search_requests")
    out["answer"] = str((result or {}).get("result") or "")
    return out


def load_events(path):
    with open(path, encoding="utf-8") as fh:
        return [json.loads(l) for l in fh if l.strip().startswith("{")]


def parse_scores(answer):
    """The JSON list in the reply (first '[' to last ']'), or None."""
    i, j = answer.find("["), answer.rfind("]")
    if i < 0 or j <= i:
        return None
    try:
        return json.loads(answer[i:j + 1])
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------- running
def claude(prompt, extra, path, model=MODEL, effort=None):
    """One fresh `claude -p` in a new empty directory; raw stream-json saved to path. Returns the events."""
    cmd = ["claude", "-p", prompt, "--model", model, *extra, *STREAM]
    if effort:
        cmd += ["--effort", effort]
    with tempfile.TemporaryDirectory(prefix="mem_jail_") as jail:
        p = subprocess.run(cmd, cwd=jail, stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=900)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(p.stdout)
    if p.returncode != 0:
        print(f"claude exited {p.returncode}: {p.stderr[:300]}", file=sys.stderr)
    return load_events(path)


def shuffled_list(lines, seed):
    names = [re.sub(r"^\s*\d+\.\s*", "", l).strip() for l in lines if l.strip()]
    random.Random(seed).shuffle(names)
    return "\n".join(f"{i}. {n}" for i, n in enumerate(names, 1))


def sha256(path):
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def write_row(row):
    path = f"{OUT}/verification.csv"
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(row))
        if new:
            w.writeheader()
        w.writerow(row)


def record(name, raw, v, expect_pass=True, note=""):
    row = {"run": name, **{k: v[k] for k in CHECKS}, "all_pass": v["all_pass"], "expected_all_pass": expect_pass,
           "web_search_requests": v["web_search_requests"], "tool_blocks": len(v["tool_blocks"]),
           "init_model": v["init_model"], "served_models": " ".join(v["served_models"]),
           "claude_code_version": v["claude_code_version"], "raw_sha256": sha256(raw), "note": note}
    write_row(row)
    flag = "OK " if v["all_pass"] == expect_pass else "BAD"
    print(f"[{flag}] {name}: all_pass={v['all_pass']} web_search_requests={v['web_search_requests']} "
          f"tool_blocks={len(v['tool_blocks'])} {note}")
    return row


def cmd_canary(args):
    # C1: hardened session, a question only the web can answer. Expect all checks pass and "don't know".
    raw = f"{OUT}/raw/canary_hardened.jsonl"
    v = verify(claude(CANARY_Q, HARDENED, raw, model=args.model, effort=args.effort))
    record("canary_hardened", raw, v, True, "answer: " + v["answer"][:120].replace("\n", " "))
    # C2: positive control. Same question, WebSearch allowed. Expect the checks to FAIL (search detected),
    # which shows the counters and the block scan really see a web search when there is one.
    raw = f"{OUT}/raw/canary_web_allowed.jsonl"
    v = verify(claude(CANARY_Q, ["--tools", "WebSearch", "--allowedTools", "WebSearch", "--strict-mcp-config",
                                 "--setting-sources", "", "--no-session-persistence"], raw,
                      model=args.model, effort=args.effort))
    record("canary_web_allowed", raw, v, False, "answer: " + v["answer"][:120].replace("\n", " "))


def complete_reply(scores, n):
    """True when the reply is a list with exactly one entry for each id 1..n and the needed fields."""
    try:
        return (isinstance(scores, list) and sorted(int(e["id"]) for e in scores) == list(range(1, n + 1))
                and all(isinstance(e["knows_later_problems"], bool) and 0 <= int(e["risk_score"]) <= 100
                        for e in scores))
    except (KeyError, TypeError, ValueError):
        return False


def cmd_run(args):
    prompt = open(args.prompt, encoding="utf-8").read()
    lines = open(args.input, encoding="utf-8").read().splitlines()
    for k in range(1, args.runs + 1):
        seed = args.seed + k
        if args.listings:   # reuse another run's list so that only the model differs
            listing = open(f"{args.listings}/run{k}.txt", encoding="utf-8").read().rstrip("\n")
            seed = f"listing from {args.listings}/run{k}.txt"
        else:
            listing = shuffled_list(lines, seed)
        n = len([l for l in listing.splitlines() if l.strip()])
        os.makedirs(f"{OUT}/inputs", exist_ok=True)
        with open(f"{OUT}/inputs/run{k}.txt", "w", encoding="utf-8") as fh:
            fh.write(listing + "\n")
        raw = f"{OUT}/raw/run{k}.jsonl"
        for attempt in (1, 2):   # an incomplete or unparseable reply is rerun once on the same list
            v = verify(claude(prompt + listing + "\n", HARDENED, raw, model=args.model, effort=args.effort))
            scores = parse_scores(v["answer"])
            if complete_reply(scores, n) or attempt == 2:
                break
            os.replace(raw, f"{OUT}/raw/run{k}_incomplete{attempt}.jsonl")
            print(f"run{k}: incomplete reply, kept as run{k}_incomplete{attempt}.jsonl; rerunning the same list")
        with open(f"{OUT}/run{k}.json", "w", encoding="utf-8") as fh:
            json.dump({"seed": seed, "model": args.model, "attempts": attempt, "complete": complete_reply(scores, n),
                       "verification": {c: v[c] for c in CHECKS + ("all_pass",)},
                       "scores": scores}, fh, ensure_ascii=False, indent=1)
        record(f"run{k}", raw, v, True, f"model={args.model} attempts={attempt} "
                                         f"complete={complete_reply(scores, n)} parsed={scores is not None and len(scores)}")


def cmd_verify(args):
    bad = 0
    for p in sorted(sum((glob.glob(x) for x in args.paths), [])):
        v = verify(load_events(p))
        failed = [k for k in CHECKS if not v[k]]
        bad += bool(failed)
        print(f"{'PASS' if not failed else 'FAIL'} {p} {('failed: ' + ','.join(failed)) if failed else ''}")
    sys.exit(1 if bad else 0)


def _pairs_auc(s):
    """s: {pid: score}. AUC (T vs C), bootstrap CI and within-pair wins / ties / losses."""
    from experiment.edgar_risk.round3 import auc, auc_ci
    pos = [v for k, v in s.items() if k.endswith("T")]
    neg = [v for k, v in s.items() if k.endswith("C")]
    w = t = l = 0
    for k, v in s.items():
        if k.endswith("T") and k[:-1] + "C" in s:
            c = s[k[:-1] + "C"]
            w, t, l = w + (v > c), t + (v == c), l + (v < c)
    lo, hi = auc_ci(pos, neg)
    return auc(pos, neg), lo, hi, w, t, l


def _by_pid(entries, listing, key):
    """Map a model reply (entries with id) to {pid: (score, knows)} using the listing the model was shown."""
    names = {i: re.sub(r"\s+—\s+fiscal year.*$", "", re.sub(r"^\s*\d+\.\s*", "", l)).strip()
             for i, l in enumerate([l for l in listing.splitlines() if l.strip()], 1)}
    out = {}
    for e in entries:
        pid = key[names[int(e["id"])]]
        out[pid] = (int(e["risk_score"]), bool(e["knows_later_problems"]))
    if len(out) != len(key):
        raise SystemExit(f"reply covers {len(out)} of {len(key)} companies")
    return out


def spearman(x, y):
    """Spearman rank correlation (average ranks for ties); same as round8.spearman on the round 8 branch."""
    def rank(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r, i = [0.0] * len(v), 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = (i + j) / 2
            i = j + 1
        return r
    rx, ry = rank(x), rank(y)
    mx, my = sum(rx) / len(rx), sum(ry) / len(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = (sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry)) ** 0.5
    return num / den if den else float("nan")


def _references(key):
    """Comparison runs in OUT/reference: claude.ai reruns (round 8 only) and *_MEM_original.csv files."""
    ref = {}
    for k in (1, 2):
        p = f"{OUT}/reference/claudeai_rerun{k}.json"
        if os.path.exists(p):
            ref[f"claude.ai rerun {k}"] = _by_pid(json.load(open(p)), open(INPUT, encoding="utf-8").read(), key)
    for p in sorted(glob.glob(f"{OUT}/reference/*_MEM_original.csv")):
        label = re.sub(r"round(\d+)", r"round \1", os.path.basename(p).replace("_MEM_original.csv", "")) + " original"
        ref[label] = {r["pid"]: (int(r["risk_score"]), r["knows_later_problems"] == "True")
                      for r in csv.DictReader(open(p, encoding="utf-8"))}
    return ref


def cmd_evaluate(args):
    runs = sorted(glob.glob(f"{OUT}/run*.json"), key=lambda p: int(re.search(r"run(\d+)", p).group(1)))
    # Gate: every raw log passes, and every raw log / reply is committed unchanged before labels are read.
    for r in runs:
        k = re.search(r"run(\d+)", r).group(1)
        raw = f"{OUT}/raw/run{k}.jsonl"
        if not verify(load_events(raw))["all_pass"]:
            raise SystemExit(f"{raw} fails verification")
        for p in (raw, r, f"{OUT}/inputs/run{k}.txt"):
            if subprocess.run(["git", "diff", "--quiet", "HEAD", "--", p]).returncode or \
                    subprocess.run(["git", "ls-files", "--error-unmatch", p], capture_output=True).returncode:
                raise SystemExit(f"{p} is not committed unchanged; commit raw outputs before evaluating")
    key = {}
    for row in csv.DictReader(open(f"{OUT}/key.tsv", encoding="utf-8"), delimiter="\t"):
        key[row["company"]] = row["pid"]
    res = {}
    for r in runs:
        k = re.search(r"run(\d+)", r).group(1)
        res[f"run{k}"] = _by_pid(json.load(open(r))["scores"], open(f"{OUT}/inputs/run{k}.txt").read(), key)
    ref = _references(key)
    base = next(n for n in ref if n.endswith("original"))   # the original MEM run of that round
    pids = sorted(key.values())
    npair = sum(p.endswith("T") for p in pids)
    mean = {p: sum(v[p][0] for v in res.values()) / len(res) for p in pids}
    orig = [ref[base][p][0] for p in pids]
    lines = [f"# {args.title}：結果", "",
             f"{len(res)} 次 `claude -p --tools \"\"` 執行，全部通過 7 項無上網檢查（`verification.csv`），原始紀錄在算分前已 commit。", "",
             "| 條件 | AUC | 95% CI | 組內勝 / 平 / 負 | 問題公司「知道出事」 | 對照公司「知道出事」 | 與原始 MEM 的 Spearman ρ |",
             "|---|---|---|---|---|---|---|"]

    def row(name, d):
        a, lo, hi, w, t, l = _pairs_auc({p: d[p][0] for p in pids})
        kt = sum(d[p][1] for p in pids if p.endswith("T")); kc = sum(d[p][1] for p in pids if p.endswith("C"))
        rho = spearman([d[p][0] for p in pids], orig)
        return f"| {name} | {a:.2f} | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} | {kt}/{npair} | {kc}/{npair} | {rho:.2f} |"
    lines += [row(n, d) for n, d in res.items()]
    a, lo, hi, w, t, l = _pairs_auc(mean)
    lines.append(f"| **隔離 {len(res)} 次平均分數** | **{a:.2f}** | {lo:.2f}–{hi:.2f} | {w} / {t} / {l} | | | "
                 f"{spearman([mean[p] for p in pids], orig):.2f} |")
    lines += [row(n, d) for n, d in ref.items()]
    names = list(res)
    rhos = [spearman([res[x][p][0] for p in pids], [res[y][p][0] for p in pids])
            for i, x in enumerate(names) for y in names[i + 1:]]
    if rhos:
        lines += ["", f"隔離各次之間的 Spearman ρ：最低 {min(rhos):.2f}，中位數 {sorted(rhos)[len(rhos) // 2]:.2f}"]
    lines += ["", "## 逐家（分數）", "", "| pid | 公司 | " + " | ".join(names) + " | 平均 | 原始 MEM |",
              "|---|---|" + "---|" * (len(names) + 2)]
    inv = {v: k for k, v in key.items()}
    for p in pids:
        lines.append(f"| {p} | {inv[p]} | " + " | ".join(str(res[n][p][0]) for n in names) +
                     f" | {mean[p]:.0f} | {ref[base][p][0]} |")
    report = args.report or f"{OUT}/evaluation.md"
    open(report, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print("\n".join(lines[:len(res) + len(ref) + 10]))


def cmd_watch(args):
    """Read stream-json from stdin, print a readable line per event as it arrives, then run verify()."""
    events = []
    for line in sys.stdin:
        if not line.strip().startswith("{"):
            continue
        e = json.loads(line)
        events.append(e)
        t, st = e.get("type"), e.get("subtype")
        if t == "system" and st == "init":
            print(f"[啟動] 模型={e.get('model')}  CLI={e.get('claude_code_version')}  目錄={e.get('cwd')}")
            print(f"[啟動] 可用工具={e.get('tools')}  MCP 伺服器={e.get('mcp_servers')}")
        elif t == "system" and st == "thinking_tokens":
            print("[思考中] …", flush=True)
        elif t == "assistant":
            for c in (e.get("message") or {}).get("content") or []:
                ct = c.get("type")
                if ct == "text":
                    print("[回答]\n" + c.get("text", ""))
                elif ct == "thinking":
                    print(f"[思考區塊] 回傳內容 {len(c.get('thinking') or '')} 字（目前模型不回傳原始思考）")
                else:
                    print(f"[!! 工具呼叫] {ct} {c.get('name')} {json.dumps(c.get('input'), ensure_ascii=False)[:150]}")
        elif t == "result":
            u = (e.get("usage") or {}).get("server_tool_use")
            mu = {k: v.get("webSearchRequests") for k, v in (e.get("modelUsage") or {}).items()}
            print(f"[結束] 輪數={e.get('num_turns')}  子代理={(e.get('subagent_stats') or {}).get('spawned')}  "
                  f"伺服器端搜尋/抓取={u}  各模型搜尋次數={mu}  花費=${e.get('total_cost_usd', 0):.3f}")
        sys.stdout.flush()
    v = verify(events)
    print("\n[檢查] " + "  ".join(f"{k}={'通過' if v[k] else '失敗'}" for k in CHECKS))
    print("[檢查] 全部通過：無法上網" if v["all_pass"] else "[檢查] 有項目失敗：這次不能當作純記憶結果")


def main():
    global OUT
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--out", default=OUT, help="results folder (default results/mem_isolated)")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("canary", parents=[common]); c.add_argument("--effort"); c.add_argument("--model", default=MODEL)
    c.set_defaults(fn=cmd_canary)
    r = sub.add_parser("run", parents=[common])
    r.add_argument("--runs", type=int, default=5); r.add_argument("--seed", type=int, default=20261106)
    r.add_argument("--input", default=INPUT); r.add_argument("--prompt", default=PROMPT); r.add_argument("--effort")
    r.add_argument("--model", default=MODEL)
    r.add_argument("--listings", help="folder with run1.txt.. to reuse (same lists as another model's runs)")
    r.set_defaults(fn=cmd_run)
    v = sub.add_parser("verify", parents=[common]); v.add_argument("paths", nargs="+"); v.set_defaults(fn=cmd_verify)
    e = sub.add_parser("evaluate", parents=[common])
    e.add_argument("--title", default="第八輪 MEM 隔離重跑"); e.add_argument("--report")
    e.set_defaults(fn=cmd_evaluate)
    w = sub.add_parser("watch", help="pretty-print a stream-json log from stdin, then verify it")
    w.set_defaults(fn=cmd_watch)
    a = ap.parse_args()
    OUT = getattr(a, "out", OUT)
    a.fn(a)


if __name__ == "__main__":
    main()

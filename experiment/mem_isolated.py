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
    v = verify(claude(CANARY_Q, HARDENED, raw, effort=args.effort))
    record("canary_hardened", raw, v, True, "answer: " + v["answer"][:120].replace("\n", " "))
    # C2: positive control. Same question, WebSearch allowed. Expect the checks to FAIL (search detected),
    # which shows the counters and the block scan really see a web search when there is one.
    raw = f"{OUT}/raw/canary_web_allowed.jsonl"
    v = verify(claude(CANARY_Q, ["--tools", "WebSearch", "--allowedTools", "WebSearch", "--strict-mcp-config",
                                 "--setting-sources", "", "--no-session-persistence"], raw, effort=args.effort))
    record("canary_web_allowed", raw, v, False, "answer: " + v["answer"][:120].replace("\n", " "))


def cmd_run(args):
    prompt = open(args.prompt, encoding="utf-8").read()
    lines = open(args.input, encoding="utf-8").read().splitlines()
    for k in range(1, args.runs + 1):
        seed = args.seed + k
        listing = shuffled_list(lines, seed)
        os.makedirs(f"{OUT}/inputs", exist_ok=True)
        with open(f"{OUT}/inputs/run{k}.txt", "w", encoding="utf-8") as fh:
            fh.write(listing + "\n")
        raw = f"{OUT}/raw/run{k}.jsonl"
        v = verify(claude(prompt + listing + "\n", HARDENED, raw, effort=args.effort))
        scores = parse_scores(v["answer"])
        with open(f"{OUT}/run{k}.json", "w", encoding="utf-8") as fh:
            json.dump({"seed": seed, "verification": {c: v[c] for c in CHECKS + ("all_pass",)},
                       "scores": scores}, fh, ensure_ascii=False, indent=1)
        record(f"run{k}", raw, v, True, f"seed={seed} parsed={scores is not None and len(scores)}")


def cmd_verify(args):
    bad = 0
    for p in sorted(sum((glob.glob(x) for x in args.paths), [])):
        v = verify(load_events(p))
        failed = [k for k in CHECKS if not v[k]]
        bad += bool(failed)
        print(f"{'PASS' if not failed else 'FAIL'} {p} {('failed: ' + ','.join(failed)) if failed else ''}")
    sys.exit(1 if bad else 0)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("canary"); c.add_argument("--effort"); c.set_defaults(fn=cmd_canary)
    r = sub.add_parser("run")
    r.add_argument("--runs", type=int, default=5); r.add_argument("--seed", type=int, default=20261106)
    r.add_argument("--input", default=INPUT); r.add_argument("--prompt", default=PROMPT); r.add_argument("--effort")
    r.set_defaults(fn=cmd_run)
    v = sub.add_parser("verify"); v.add_argument("paths", nargs="+"); v.set_defaults(fn=cmd_verify)
    a = ap.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()

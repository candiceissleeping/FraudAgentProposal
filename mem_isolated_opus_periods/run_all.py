#!/usr/bin/env python3
"""Send the 30 prompt files to Claude Opus 5.5 with no tools, one fresh session each. Python standard library only.

Put this file next to the `prompts` folder and run it on a machine where Claude Code is installed and logged in:

    python3 run_all.py canary      # 2 requests: must say it does not know; the web-allowed one must be caught
    python3 run_all.py run         # 30 requests; skips files already done, so it can be restarted

Raw session logs go to raw/<list>_run<k>.jsonl. Send the whole `raw` folder back; nothing is scored here.
The flags are the ones used for every earlier Opus run of this project (experiment/mem_isolated.py).
"""
import glob
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
MODEL = "claude-opus-5-5"
HARDENED = ["--tools", "", "--strict-mcp-config", "--setting-sources", "", "--no-session-persistence"]
WEB = ["--tools", "WebSearch", "--allowedTools", "WebSearch", "--strict-mcp-config", "--setting-sources", "",
       "--no-session-persistence"]
STREAM = ["--output-format", "stream-json", "--verbose"]
CANARY_Q = "2026 年 11 月 20 日台股加權指數（TAIEX）收盤是多少點？如果你無法確定，請直接說不知道，不要猜。"


def claude(prompt, extra, path):
    """One `claude -p` in a new empty directory; the raw stream-json is saved to path."""
    with tempfile.TemporaryDirectory(prefix="mem_jail_") as jail:
        p = subprocess.run(["claude", "-p", prompt, "--model", MODEL, *extra, *STREAM], cwd=jail,
                           stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=900)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(p.stdout)
    if p.returncode != 0:
        print(f"  claude exited {p.returncode}: {p.stderr[:300]}", file=sys.stderr)
    return [json.loads(l) for l in p.stdout.splitlines() if l.strip().startswith("{")]


def summary(events):
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    res = next((e for e in reversed(events) if e.get("type") == "result"), {})
    tools = [c.get("name") for e in events if e.get("type") == "assistant"
             for c in (e.get("message") or {}).get("content") or [] if "tool" in c.get("type", "")]
    searches = sum(v.get("webSearchRequests", 0) for v in (res.get("modelUsage") or {}).values())
    return {"tools": init.get("tools"), "mcp": init.get("mcp_servers"), "tool_calls": tools, "searches": searches,
            "ok": res.get("subtype") == "success" and res.get("is_error") is False,
            "answer": str(res.get("result") or "")}


def complete(answer, n):
    i, j = answer.find("["), answer.rfind("]")
    try:
        rows = json.loads(answer[i:j + 1])
        return sorted(int(r["id"]) for r in rows) == list(range(1, n + 1))
    except (ValueError, KeyError, TypeError):
        return False


def cmd_canary():
    s = summary(claude(CANARY_Q, HARDENED, f"{HERE}/raw/canary_hardened.jsonl"))
    print(f"[no tools]   tools={s['tools']} mcp={s['mcp']} tool_calls={s['tool_calls']} searches={s['searches']}")
    print(f"             answer: {s['answer'][:150]!r}")
    print("             expected: tools=[] mcp=[] no tool calls, 0 searches, and an answer that it does not know")
    s = summary(claude(CANARY_Q, WEB, f"{HERE}/raw/canary_web_allowed.jsonl"))
    print(f"[web allowed] tool_calls={s['tool_calls']} searches={s['searches']}")
    print("             expected: a WebSearch call is listed (this shows a search would be seen). "
          "If the first check is not as expected, stop and do not run the lists.")


def cmd_run():
    files = sorted(glob.glob(f"{HERE}/prompts/*_run*.txt"))
    if len(files) != 30:
        sys.exit(f"expected 30 prompt files in {HERE}/prompts, found {len(files)}")
    for f in files:
        name = os.path.basename(f)[:-4]
        raw = f"{HERE}/raw/{name}.jsonl"
        if os.path.exists(raw) and os.path.getsize(raw) > 0:
            print(f"{name}: already done, skipped")
            continue
        prompt = open(f, encoding="utf-8").read()
        n = sum(1 for l in prompt.splitlines() if l.split(". ")[0].isdigit())
        for attempt in (1, 2):      # an incomplete reply is sent once more on the same list; both logs are kept
            s = summary(claude(prompt, HARDENED, raw))
            if complete(s["answer"], n) or attempt == 2:
                break
            os.replace(raw, f"{HERE}/raw/{name}_incomplete1.jsonl")
        print(f"{name}: companies={n} complete={complete(s['answer'], n)} attempts={attempt} tools={s['tools']} "
              f"tool_calls={len(s['tool_calls'])} searches={s['searches']} ok={s['ok']}")


if __name__ == "__main__":
    {"canary": cmd_canary, "run": cmd_run}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()

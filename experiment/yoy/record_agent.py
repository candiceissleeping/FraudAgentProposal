"""Record one subagent's reply in the same responses.jsonl format as run_llm.collect.

Used when packets are scored by Claude Code subagents instead of the Batches API:

  python -m experiment.yoy.record_agent --run smoke --id A0-D0010-r1 < reply.json
  python -m experiment.yoy.record_agent --run smoke --id A0-D0010-r1 --transcript <agent>.output \
      --expect-file data/exp1/agent_packets/A0/D0010.txt

The reply should be a bare JSON object; code fences or text around it are stripped.
Anything that does not parse is recorded with status parse_error (an invalid response).
With --transcript the reply is taken from the subagent's hand-back, and every tool call is
audited: a subagent that used any tool other than Read on --expect-file is recorded as
status isolation_breach and its answer is not used.
"""
import argparse
import json
import os
import sys

from experiment.yoy import packets


def parse_reply(text):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError:
        return None


def from_transcript(path, expect_file):
    """-> (reply text, list of isolation problems) from a subagent JSONL transcript."""
    reply, problems = "", []
    with open(path, encoding="utf-8") as f:
        for line in f:
            content = json.loads(line).get("message", {}).get("content")
            if not isinstance(content, list):
                continue
            for b in content:
                if b.get("type") != "tool_use":
                    continue
                name, inp = b.get("name"), b.get("input", {})
                if name == "SubagentHandback":
                    reply = inp.get("message", "")
                elif not (name == "Read" and os.path.abspath(inp.get("file_path", "")) == os.path.abspath(expect_file)):
                    problems.append(f"{name} {json.dumps(inp)[:200]}")
    return reply, problems


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", required=True)
    ap.add_argument("--id", required=True, help="custom id, e.g. A2-D0010-r1 or PROBE-D0010")
    ap.add_argument("--out", default=packets.DEFAULT_DIR)
    ap.add_argument("--transcript", help="subagent JSONL transcript to take the reply from")
    ap.add_argument("--expect-file", help="the only file the subagent may read (with --transcript)")
    args = ap.parse_args()
    problems = []
    if args.transcript:
        text, problems = from_transcript(args.transcript, args.expect_file)
        if not text and not problems:  # no hand-back yet: the subagent is still running
            print(f"{args.id}: not finished, nothing recorded")
            sys.exit(3)
    else:
        text = sys.stdin.read()
    data = None if problems else parse_reply(text)
    rdir = os.path.join(args.out, "runs", args.run)
    os.makedirs(rdir, exist_ok=True)
    path = os.path.join(rdir, "responses.jsonl")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            if any(json.loads(line)["custom_id"] == args.id for line in f):
                raise SystemExit(f"{args.id} already recorded in {path}")
    status = "isolation_breach" if problems else "succeeded" if data is not None else "parse_error"
    row = {"custom_id": args.id, "status": status,
           "stop_reason": "end_turn" if data is not None else None, "data": data, "usage": None}
    if problems:
        row["problems"] = problems
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"{args.id}: {status}" + (f" {problems}" if problems else ""))


if __name__ == "__main__":
    main()

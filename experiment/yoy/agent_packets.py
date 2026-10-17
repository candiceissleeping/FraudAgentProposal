"""Copy packets for Claude Code subagents, wrapping lines at 1,000 characters.

The Read tool may cut very long lines; wrapping changes only line breaks, never words
(checked for every file).

  python -m experiment.yoy.agent_packets --out data/exp1v2
"""
import argparse
import os
import textwrap

from experiment.yoy import packets

WIDTH = 1000


def wrap(text, width=WIDTH):
    lines = []
    for line in text.split("\n"):
        lines.extend(textwrap.wrap(line, width, break_long_words=True, break_on_hyphens=False) or [""])
    wrapped = "\n".join(lines)
    assert wrapped.split() == text.split() or " ".join(wrapped.split()) == " ".join(text.split())
    return wrapped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", default=packets.DEFAULT_DIR)
    args = ap.parse_args()
    n = 0
    for arm in packets.ARMS:
        src, dst = os.path.join(args.out, "packets", arm), os.path.join(args.out, "agent_packets", arm)
        os.makedirs(dst, exist_ok=True)
        for name in sorted(os.listdir(src)):
            with open(os.path.join(src, name), encoding="utf-8") as f:
                text = wrap(f.read())
            with open(os.path.join(dst, name), "w", encoding="utf-8") as f:
                f.write(text)
            n += 1
    print(f"{n} packets wrapped into {args.out}/agent_packets/")


if __name__ == "__main__":
    main()

"""E2 v2 gate: open identification during scoring (protocol section 6). Reads only guesses and true names, not labels.

  python -m experiment.mem_type_ident L1      # prints every non-"unknown" guess next to the true name, plus a draft verdict
Draft verdicts are checked by hand; the final decisions go in results/mem_type/<level>/identification.csv.
"""
import json
import re
import sys

from experiment.mem_type import _names

GENERIC = {"the", "inc", "corp", "corporation", "company", "co", "ltd", "llc", "holdings", "group", "and", "of", "&"}


def words(s):
    return [w for w in re.split(r"[^a-z0-9]+", s.lower()) if len(w) >= 3 and w not in GENERIC]


def draft(guess, name):
    g, n = words(guess), words(name)
    return bool(g and n and (n[0] in g or g[0] in n))


def main(level):
    rows = []
    for s in ("round8", "oot"):
        names = {p: n.split(" (fiscal")[0] for p, n in _names(s).items()}
        n_firms, guessed, knows = len(names), 0, 0
        for k in range(1, 6):
            j = json.load(open(f"results/mem_type/{level}/{s}/run{k}.json"))
            for e in j["reply"]:
                pid = j["order"][int(e["id"]) - 1]
                g = str(e.get("company_guess", "")).strip()
                kn = bool(e.get("knows_later_problems"))
                knows += kn
                if g.lower() not in ("", "unknown") or kn:
                    d = draft(g, names[pid])
                    guessed += d
                    rows.append((s, k, names[pid], g, d, kn))
        print(f"{s}: draft correct guesses {guessed} over 5 runs ({guessed / 5:.1f} per run), knows {knows} ({knows / 5:.1f} per run), firms {n_firms}")
    print("\nall non-unknown guesses (sample | run | true company | guess | draft match | says knows):")
    for r in rows:
        print(" | ".join(str(x) for x in r))


if __name__ == "__main__":
    main(sys.argv[1])

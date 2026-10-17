"""Build the LLM inputs for each arm (design section 3.2) from fetched filings.

  A0  current-year 10-K
  A1  current-year 10-K + prior-year 10-K raw text, cut to the length of A2's diff
  A2  current-year 10-K + year-over-year diff
  A3  year-over-year diff only

The current-year part is identical in A0/A1/A2. Text is masked (mask.py) before the diff
is computed. Each section gets an equal share of a character budget; a section shorter
than its share hands the rest to the others. Sections are cut from the end.

Outputs (git-ignored, they contain 10-K text):
  data/exp1/packets/<arm>/<doc_id>.txt
  data/exp1/key.json       doc_id -> pair_id, role (fraud/control), cik, t
  data/exp1/features.csv   per-section year-over-year similarity, for the non-LLM baseline B0
  results/exp1_packets_<pilot|all>.sha256  committed digests; a rebuild must reproduce them exactly

  python -m experiment.yoy.packets [--pilot]
"""
import argparse
import csv
import hashlib
import json
import os
import random

from experiment.yoy import diff, fetch_sample, mask

ARMS = ("A0", "A1", "A2", "A3")
CURRENT_CHARS = 96_000  # ~24k tokens of current-year 10-K
EXTRA_CHARS = 32_000    # ~8k tokens of diff (A2/A3); A1's prior-year text matches the diff's length
DOC_SEED = 20261017
DEFAULT_DIR = "data/exp1"
FIRMS_PATH = "config/exp1_firms.json"


def load_firms(path=FIRMS_PATH):
    """{cik: {"name", "sic"}} for every sample firm (committed, so packets rebuild anywhere)."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)["firms"]


def check_manifest(path, digests):
    """Write the packet digests, or if the file exists, fail unless they match it exactly."""
    lines = [f"{h}  {name}" for name, h in sorted(digests.items())]
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            if f.read().splitlines() != lines:
                raise SystemExit(f"packets differ from {path}; the inputs are not the ones that were checked")
        print(f"packets match {path}")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {path}")


def allowances(sizes, budget):
    """Water-filling: equal shares, unused share redistributed. sizes: {key: chars}."""
    out, left, keys = {}, budget, sorted(sizes, key=lambda k: sizes[k])
    for n, k in enumerate(keys):
        share = left // (len(keys) - n)
        out[k] = min(sizes[k], share)
        left -= out[k]
    return out


TRUNCATED = " [...truncated]"
ABSENT = "(not present in this filing)"
# headings and markers count against the budget, so A1 really matches A2's length
OVERHEAD = sum(len(f"### {title}\n") + len(TRUNCATED) + 2 for _, title in diff.SECTIONS)


def sections_text(filing, budget):
    texts = {key: diff.section_text(filing, key).strip() for key, _ in diff.SECTIONS}
    allow = allowances({k: len(v) for k, v in texts.items()}, max(0, budget - OVERHEAD))
    blocks = []
    for key, title in diff.SECTIONS:
        body = texts[key][:allow[key]]
        if len(body) < len(texts[key]):
            body += TRUNCATED
        blocks.append(f"### {title}\n{body or ABSENT}")
    return "\n\n".join(blocks)


def masked_filing(filing, t, aliases):
    return {k: mask.mask(v, t, aliases) if k.startswith("section_") else v for k, v in filing.items()}


HEADER = ("Excerpts from a company's annual report on Form 10-K. The company's name, other entity names, "
          "people's names and audit firms are masked; calendar years are replaced by Year T (the fiscal "
          "year of this report), Year T-1 (the prior year), and so on.")


def build(current, prior):
    """current/prior: masked filings. Returns ({arm: text}, section similarities)."""
    yoy = diff.filing_diff(prior, current)
    diff_text = diff.render(yoy, EXTRA_CHARS)
    cur = "## CURRENT YEAR 10-K (Year T)\n\n" + sections_text(current, CURRENT_CHARS)
    prev = "## PRIOR YEAR 10-K (Year T-1)\n\n" + sections_text(prior, len(diff_text))
    changes = ("## CHANGES FROM THE YEAR T-1 10-K TO THE YEAR T 10-K\n"
               "Paragraph-level comparison per section; unchanged paragraphs are omitted.\n\n" + diff_text)
    arms = {"A0": [cur], "A1": [cur, prev], "A2": [cur, changes], "A3": [changes]}
    return ({a: "\n\n".join([HEADER] + parts) for a, parts in arms.items()},
            {key: d["similarity"] for key, d in yoy.items()})


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sample", default="config/exp1_sample.json")
    ap.add_argument("--filings", default=fetch_sample.DEFAULT_DIR)
    ap.add_argument("--firms", default=FIRMS_PATH)
    ap.add_argument("--out", default=DEFAULT_DIR)
    ap.add_argument("--pilot", action="store_true")
    ap.add_argument("--manifest", help="sha256 manifest to write, or to verify against if it exists")
    args = ap.parse_args()

    pairs = json.load(open(args.sample, encoding="utf-8"))["pairs"]
    if args.pilot:
        pairs = [p for p in pairs if p["pilot"]]
    names = load_firms(args.firms)
    docs = [(p, role) for p in pairs for role in ("fraud", "control")]
    ids = [f"D{i:04d}" for i in range(1, len(docs) + 1)]
    random.Random(DOC_SEED).shuffle(ids)

    for arm in ARMS:
        os.makedirs(os.path.join(args.out, "packets", arm), exist_ok=True)
    key, features, digests = {}, [], {}
    for doc_id, (p, role) in sorted(zip(ids, docs)):
        cik, t = p[role]["cik"], p["t"]
        aliases = mask.name_aliases(names.get(cik, {}).get("name", ""))
        current = masked_filing(fetch_sample.load(args.filings, cik, t), t, aliases)
        prior = masked_filing(fetch_sample.load(args.filings, cik, t - 1), t, aliases)
        texts, sims = build(current, prior)
        for arm, text in texts.items():
            with open(os.path.join(args.out, "packets", arm, f"{doc_id}.txt"), "w", encoding="utf-8") as f:
                f.write(text)
            digests[f"{arm}/{doc_id}.txt"] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        key[doc_id] = {"pair_id": p["pair_id"], "role": role, "cik": cik, "t": t}
        features.append({"doc_id": doc_id, **{f"sim_{k}": v for k, v in sims.items()}})
        print(f"{doc_id}: " + ", ".join(f"{a} {len(x):,}" for a, x in texts.items()), flush=True)

    with open(os.path.join(args.out, "key.json"), "w", encoding="utf-8") as f:
        json.dump(key, f, indent=1, sort_keys=True)
    with open(os.path.join(args.out, "features.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["doc_id"] + [f"sim_{k}" for k, _ in diff.SECTIONS])
        w.writeheader()
        w.writerows(features)
    check_manifest(args.manifest or f"results/exp1_packets_{'pilot' if args.pilot else 'all'}.sha256", digests)


if __name__ == "__main__":
    main()

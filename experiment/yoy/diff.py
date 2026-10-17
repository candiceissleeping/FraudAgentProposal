"""Deterministic year-over-year diff of two 10-Ks (design section 3.3), no LLM involved.

Per section, paragraphs of year t are matched one-to-one to paragraphs of year t-1 by
TF-IDF cosine similarity (greedy, highest similarity first):
  sim >= UNCHANGED          unchanged, not shown
  MODIFIED <= sim < UNCHANGED  modified, both versions shown
  otherwise                 added (only in t) / removed (only in t-1)
Tokens are letters only, so a paragraph whose words stay the same but whose numbers
change counts as unchanged: the diff is about narrative, not figures.

The rendered diff gives every section an equal share of the character budget; inside a
section the largest changes come first (entries that no longer fit are skipped), and budget a section leaves unused is handed to
the others in a second pass.
"""
import collections
import math
import re

SECTIONS = (("1A", "Item 1A Risk Factors"), ("3", "Item 3 Legal Proceedings"),
            ("7", "Item 7 MD&A"), ("7A", "Item 7A Market Risk"),
            ("FS", "Financial Statements and Notes"), ("9", "Item 9 Accountant Changes"),
            ("9A", "Item 9A Controls and Procedures"))
UNCHANGED = 0.95
MODIFIED = 0.5
MIN_PARA_CHARS = 80
LOOKUP_TERMS = 8        # candidate pairs come from each paragraph's 8 highest-weight terms
MAX_ENTRY_CHARS = 1500  # one paragraph (e.g. a flattened table) cannot eat a section's budget
FS_MIN_CHARS = 2000  # same rule as build_sample.fs_chars

_TOKEN = re.compile(r"[a-z]{2,}")


def section_text(filing, key):
    """Text of a section; 'FS' is Item 8, or Items 14+15 for older 10-Ks."""
    if key != "FS":
        return filing.get(f"section_{key}") or ""
    item8 = filing.get("section_8") or ""
    if len(item8) >= FS_MIN_CHARS:
        return item8
    return "\n".join(filing.get(f"section_{k}") or "" for k in ("14", "15"))


def paragraphs(text):
    paras = [" ".join(p.split()) for p in re.split(r"\n", text or "")]
    return [p for p in paras if len(p) >= MIN_PARA_CHARS]


def _tokens(text):
    return _TOKEN.findall(text.lower())


def _vectors(docs):
    """L2-normalised TF-IDF vectors (dicts) over the given documents."""
    tfs = [collections.Counter(_tokens(d)) for d in docs]
    df = collections.Counter(t for tf in tfs for t in tf)
    n = len(docs)
    vecs = []
    for tf in tfs:
        v = {t: (1 + math.log(c)) * (math.log((1 + n) / (1 + df[t])) + 1) for t, c in tf.items()}
        norm = math.sqrt(sum(x * x for x in v.values())) or 1.0
        vecs.append({t: x / norm for t, x in v.items()})
    return vecs


def _cos(a, b):
    if len(a) > len(b):
        a, b = b, a
    return sum(x * b.get(t, 0.0) for t, x in a.items())


def section_diff(prior_text, current_text):
    prior, current = paragraphs(prior_text), paragraphs(current_text)
    vecs = _vectors(prior + current + [prior_text or "", current_text or ""])
    pv, cv = vecs[:len(prior)], vecs[len(prior):len(prior) + len(current)]
    similarity = _cos(vecs[-2], vecs[-1]) if prior and current else 0.0

    # candidate pairs via an inverted index over prior paragraphs
    postings = collections.defaultdict(list)
    for j, v in enumerate(pv):
        for t in v:
            postings[t].append(j)
    scored = []
    for i, v in enumerate(cv):
        # a pair with cosine >= MODIFIED shares the paragraph's heaviest terms, so look those up only
        top = sorted(v, key=lambda t: (-v[t], t))[:LOOKUP_TERMS]
        for j in {j for t in top for j in postings.get(t, ())}:
            s = _cos(v, pv[j])
            if s >= MODIFIED:
                scored.append((s, i, j))
    scored.sort(key=lambda x: (-x[0], x[1], x[2]))
    used_c, used_p, modified, unchanged = set(), set(), [], 0
    for s, i, j in scored:
        if i in used_c or j in used_p:
            continue
        used_c.add(i)
        used_p.add(j)
        if s >= UNCHANGED:
            unchanged += 1
        else:
            modified.append({"similarity": round(s, 3), "prior": prior[j], "current": current[i]})
    return {"similarity": round(similarity, 3), "unchanged": unchanged,
            "added": [p for i, p in enumerate(current) if i not in used_c],
            "removed": [p for j, p in enumerate(prior) if j not in used_p],
            "modified": modified}


def filing_diff(prior_filing, current_filing):
    return {key: section_diff(section_text(prior_filing, key), section_text(current_filing, key))
            for key, _ in SECTIONS}


def _entries(d):
    """(size, text) per change, largest change first."""
    out = [(len(p), f"[ADDED in Year T] {p}") for p in d["added"]]
    out += [(len(p), f"[REMOVED since Year T-1] {p}") for p in d["removed"]]
    out += [((1 - m["similarity"]) * len(m["current"]),
             f"[MODIFIED, similarity {m['similarity']:.2f}]\n  Year T-1: {m['prior']}\n  Year T:   {m['current']}")
            for m in d["modified"]]
    out.sort(key=lambda e: (-e[0], e[1]))
    return [text if len(text) <= MAX_ENTRY_CHARS else text[:MAX_ENTRY_CHARS - 3] + "..." for _, text in out]


def render(diffs, budget_chars):
    """Render a filing_diff within budget_chars; returns the text."""
    headers, queues = {}, {}
    for key, title in SECTIONS:
        d = diffs[key]
        headers[key] = (f"## {title}: similarity to Year T-1 = {d['similarity']:.2f} "
                        f"(added {len(d['added'])}, removed {len(d['removed'])}, "
                        f"modified {len(d['modified'])}, unchanged {d['unchanged']} paragraphs)")
        queues[key] = _entries(d)
    used = sum(len(h) + 1 for h in headers.values())
    chosen = {key: [] for key, _ in SECTIONS}

    def take(key, allowance):
        """Take entries in order, skipping any that no longer fit."""
        spent, rest = 0, []
        for entry in queues[key]:
            if spent + len(entry) + 1 <= allowance:
                chosen[key].append(entry)
                spent += len(entry) + 1
            else:
                rest.append(entry)
        queues[key] = rest
        return spent

    share = max(0, budget_chars - used) // len(SECTIONS)
    for key, _ in SECTIONS:
        used += take(key, share)
    for key, _ in SECTIONS:  # second pass: leftover budget, same section order
        used += take(key, max(0, budget_chars - used))
    blocks = []
    for key, _ in SECTIONS:
        blocks.append("\n".join([headers[key]] + chosen[key]))
    return "\n\n".join(blocks)

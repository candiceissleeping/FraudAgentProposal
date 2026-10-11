"""Red-flag evidence extraction from 10-K sections.

Each category is a set of regex patterns plus the 10-K sections where it is
meaningful. A hit is a *sentence* matching a pattern; sentences with a nearby
negation ("no material weakness", "not aware of any ...") are skipped so
boilerplate assurances are not counted as evidence.
"""
import re

# section keys as named in EDGAR-CORPUS
SECTION_NAMES = {
    "section_1": "Item 1 Business",
    "section_1A": "Item 1A Risk Factors",
    "section_3": "Item 3 Legal Proceedings",
    "section_7": "Item 7 MD&A",
    "section_7A": "Item 7A Market Risk",
    "section_8": "Item 8 Financial Statements",
    "section_9": "Item 9 Changes in/Disagreements with Accountants",
    "section_9A": "Item 9A Controls and Procedures",
    # older 10-Ks often place the financial statements and notes here, with Item 8 only a cross-reference
    "section_14": "Item 14 Exhibits/Financial Statements",
    "section_15": "Item 15 Exhibits/Financial Statements",
}

FIN_STMT = ["section_8", "section_14", "section_15"]

ALL = list(SECTION_NAMES)

# weight = maximum points the category can contribute to the 0-100 score
CATEGORIES = {
    "going_concern": {
        "label": "Going-concern doubt",
        "weight": 25,
        "sections": ALL,
        "patterns": [r"substantial doubt", r"ability to continue as a going concern"],
    },
    "restatement": {
        "label": "Restatement of prior financials",
        "weight": 20,
        "sections": ALL,
        # "Amended and Restated Articles/Plan/Agreement" in exhibit lists is not a financial restatement
        "patterns": [r"(?<!amended and )\brestate(d|ment)?\b(?! (articles|certificate|by-?laws|charter|agreement|credit|plan|as of|to (reflect|include)))",
                     r"should no longer be relied upon",
                     r"previously (issued|reported) financial statements"],
    },
    "internal_control": {
        "label": "Internal-control weakness",
        "weight": 20,
        "sections": ["section_9A", "section_7", "section_1A"] + FIN_STMT,
        # skip the auditor-opinion boilerplate ("assessing the risk that a material weakness exists")
        # and textbook definitions ("A material weakness is a ...")
        "patterns": [r"(?<!risk that a )material weakness(?! (exists|is a))", r"significant deficienc",
                     r"(disclosure controls|internal control).{0,80}\bnot effective\b"],
    },
    "regulatory": {
        "label": "Regulatory / criminal investigation",
        "weight": 15,
        "sections": ALL,
        "patterns": [r"\bsubpoena", r"wells notice", r"formal order of (private )?investigation",
                     r"department of justice", r"grand jury",
                     r"(sec|securities and exchange commission).{0,40}(investigation|inquiry)",
                     r"deferred prosecution", r"consent (decree|order)"],
    },
    "securities_litigation": {
        "label": "Securities / shareholder litigation",
        "weight": 10,
        "sections": ["section_3", "section_1A", "section_7"] + FIN_STMT,
        "patterns": [r"securities (class action|fraud)", r"shareholder (class action|derivative)",
                     r"(class action|derivative (action|lawsuit|suit)).{0,80}(securities|shareholder|stockholder)",
                     r"section 10\(b\)", r"rule 10b-5"],
    },
    "auditor_change": {
        "label": "Auditor change / disagreement",
        "weight": 10,
        "sections": ["section_9", "section_9A"],
        # the Item 9 heading itself ("Changes in and Disagreements with Accountants ... None.") is not evidence
        "patterns": [r"dismiss(ed|al) .{0,60}(accountant|auditor)",
                     r"(?<!changes in and )disagreements? with (the )?(accountant|auditor)",
                     r"resign(ed|ation) .{0,40}(accountant|auditor)", r"reportable event"],
    },
    "off_balance_sheet": {
        "label": "Off-balance-sheet / related-party structures",
        "weight": 10,
        "sections": ["section_7", "section_1A"] + FIN_STMT,
        "patterns": [r"special purpose entit", r"variable interest entit", r"unconsolidated (affiliate|entit|subsidiar)",
                     r"related[- ]part(y|ies)", r"off-balance[- ]sheet", r"repurchase agreements? .{0,60}sales?"],
    },
    "aggressive_accounting": {
        "label": "Aggressive revenue / accounting choices",
        "weight": 10,
        "sections": ["section_7"] + FIN_STMT,
        "patterns": [r"bill[- ]and[- ]hold", r"channel (stuffing|inventory)", r"\bbarter\b",
                     r"mark[- ]to[- ](market|model)", r"round[- ]trip", r"capitaliz(ed|ation) of .{0,40}(cost|expense)",
                     r"change in (accounting )?estimate", r"specialty pharmacy"],
    },
    "liquidity_stress": {
        "label": "Liquidity / covenant stress",
        "weight": 10,
        "sections": ["section_7", "section_1A"] + FIN_STMT,
        "patterns": [r"covenant.{0,60}(waiver|violat|breach|default)", r"(waiver|violat|breach|default).{0,60}covenant",
                     r"(credit )?rating.{0,40}downgrad", r"downgrad.{0,40}rating", r"event of default",
                     r"liquidity (crisis|shortfall)"],
    },
    "impairment": {
        "label": "Large impairments / write-downs",
        "weight": 5,
        "sections": ["section_7"] + FIN_STMT,
        "patterns": [r"impairment (charge|loss)", r"write[- ](down|off)s?\b", r"goodwill impairment"],
    },
}

NEGATION = re.compile(
    r"\b(no|not aware|did not identify|does not believe|there were no|has not|have not|were not|was not|without)\b"
    r"[^.]{0,60}$", re.I)

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z(\"])")
_COMPILED = {k: [re.compile(p, re.I) for p in v["patterns"]] for k, v in CATEGORIES.items()}


def sentences(text):
    text = re.sub(r"\s+", " ", text or "")
    return [s.strip() for s in _SENT_SPLIT.split(text) if s.strip()]


def _negated(sentence, match):
    return bool(NEGATION.search(sentence[: match.start()]))


def extract(filing, max_examples=5):
    """Return {category: {"hits": int, "examples": [{"section", "text"}]}}."""
    split = {sec: sentences(filing.get(sec, "")) for sec in SECTION_NAMES}
    out = {}
    for cat, spec in CATEGORIES.items():
        hits, examples, seen = 0, [], set()
        for sec in spec["sections"]:
            for s in split.get(sec, []):
                for rx in _COMPILED[cat]:
                    m = rx.search(s)
                    if m and not _negated(s, m):
                        if s not in seen:
                            seen.add(s)
                            hits += 1
                            if len(examples) < max_examples:
                                examples.append({"section": SECTION_NAMES[sec], "text": s[:600]})
                        break
        out[cat] = {"hits": hits, "examples": examples}
    return out


def text_stats(filing):
    """Size / readability descriptors (Li 2008: harder-to-read reports correlate with weaker earnings)."""
    stats = {}
    for sec in ("section_1A", "section_7"):
        sents = sentences(filing.get(sec, ""))
        words = [w for s in sents for w in s.split()]
        complex_words = [w for w in words if _syllables(w) >= 3]
        fog = (0.4 * (len(words) / max(len(sents), 1) + 100 * len(complex_words) / max(len(words), 1))
               if words else None)
        stats[sec] = {"words": len(words), "fog_index": round(fog, 1) if fog else None}
    stats["sections_present"] = [SECTION_NAMES[s] for s in SECTION_NAMES if (filing.get(s) or "").strip()]
    return stats


def _syllables(word):
    w = re.sub(r"[^a-z]", "", word.lower())
    if not w:
        return 0
    n = len(re.findall(r"[aeiouy]+", w))
    if w.endswith("e") and n > 1:
        n -= 1
    return max(n, 1)

"""Redact identity cues from 10-K text before an LLM reads it (design section 3.5).

Replaced:
  - the firm's own name and its distinctive words           -> [COMPANY]
  - other legal-entity names (... Inc. / Corp. / LLC / L.P.)  -> [ENTITY]
  - honorific + surname (Mr. Smith, Ms. Lee, Dr. ...)        -> [PERSON]
  - audit-firm names (era cue: Arthur Andersen)              -> [AUDITOR]
  - calendar years                                           -> Year T, Year T-1, Year T+1, ...
Masking is heuristic; the identity probe in the LLM run measures what still leaks.
"""
import re

SUFFIXES = r"(?:Inc|Incorporated|Corp|Corporation|Co|Company|Companies|Ltd|Limited|LLC|L\.L\.C|LP|L\.P|PLC|N\.V|S\.A|AG|GmbH|Holdings?|Group|Trust|Bancorp)"
# only unambiguous legal suffixes, so "the Company" / "the Group" stay readable
_ENTITY = re.compile(r"\b(?:[A-Z][\w&'\-]*\.?,?\s+){1,5}"
                     r"(?:Inc|Incorporated|Corp|Corporation|Ltd|Limited|LLC|L\.L\.C|L\.P|PLC|N\.V|S\.A|GmbH)\b\.?")
_PERSON = re.compile(r"\b(?:Mr|Mrs|Ms|Dr)\.?\s+[A-Z][a-zA-Z'\-]+(?:\s+[A-Z][a-zA-Z'\-]+)?")
_AUDITORS = re.compile(
    r"\b(?:Arthur Andersen|Andersen LLP|KPMG(?: Peat Marwick)?|Ernst\s*&\s*Young|Coopers\s*&\s*Lybrand|"
    r"Price\s*Waterhouse(?:Coopers)?|Pricewaterhouse\s*Coopers|Deloitte(?:\s*&\s*Touche)?|"
    r"Grant Thornton|BDO(?: Seidman| USA)?|McGladrey(?:\s*&\s*Pullen)?|RSM US|Crowe(?: Horwath)?|"
    r"Moss Adams|Marcum|BKD)\b(?:\s*LLP)?", re.I)
_YEAR = re.compile(r"\b(19[5-9]\d|20[0-3]\d)\b")
_LEGAL = re.compile(r"[,.]?\s+" + SUFFIXES + r"\b\.?$", re.I)
# words too common to redact on their own even if they appear in a firm name
_COMMON = {"american", "national", "international", "united", "general", "first", "new", "the", "and",
           "global", "systems", "services", "technologies", "technology", "industries", "financial",
           "communications", "energy", "health", "healthcare", "capital", "resources", "solutions",
           "group", "holdings", "corp", "inc", "company", "of", "bank", "pharmaceuticals", "software"}


def name_aliases(name):
    """'ENRON CORP /OR/' -> ['ENRON CORP', 'ENRON'] (longest first; matched case-insensitively)."""
    name = re.sub(r"\s*/.*$", "", name or "").strip()  # EDGAR state suffix like /DE/
    if not name:
        return []
    base = _LEGAL.sub("", name).strip(" ,.")
    forms = {name, base}
    forms |= {w for w in re.findall(r"[A-Za-z][A-Za-z&'\-]{3,}", base) if w.lower() not in _COMMON}
    return sorted({f for f in forms if f}, key=len, reverse=True)


def mask(text, t, aliases=()):
    if not text:
        return ""
    for a in aliases:
        text = re.sub(r"(?<![\w])" + re.escape(a).replace(r"\ ", r"[\s,]+") + r"(?![\w])", "[COMPANY]", text,
                      flags=re.I)
    text = _AUDITORS.sub("[AUDITOR]", text)
    text = _PERSON.sub("[PERSON]", text)
    text = _ENTITY.sub(lambda m: m.group(0) if "[COMPANY]" in m.group(0) else "[ENTITY]", text)

    def year(m):
        k = int(m.group(1)) - t
        return "Year T" if k == 0 else f"Year T{k:+d}"
    return _YEAR.sub(year, text)

"""Redact identity cues from 10-K text before an LLM reads it (design section 3.5).

Replaced:
  - the firm's own name and its distinctive words           -> [COMPANY]
  - other legal-entity names (... Inc. / Corp. / LLC / L.P.)  -> [ENTITY]
  - honorific + surname (Mr. Smith, Ms. Lee, Dr. ...)        -> [PERSON]
  - audit-firm names (era cue: Arthur Andersen)              -> [AUDITOR]
  - calendar years                                           -> Year T, Year T-1, Year T+1, ...
Version 2 adds (pass a vocabulary from generic_vocab):
  - any other capitalised word that is rare across the sample's firms -> [NAME]
    (people, places, products, subsidiaries, counterparties: in the smoke run the
    identity probe named 6/6 firms from exactly these)
  - accounting-standard numbers (SFAS No. 125 -> SFAS No. [#]) and Year 2000 / Y2K,
    which date the filing even after calendar years are masked
  - US states, large cities and "City, State" pairs -> [PLACE]; court case numbers -> [CASENO]
    (common enough to survive the rarity rule, but they locate the firm)
Masking is heuristic; the identity probe in the LLM run measures what still leaks.
"""
import collections
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
_STANDARD = re.compile(
    r"\b((?:SFAS|FAS|SOP|EITF|FIN|APB|SAB|ASU|ASC|Statement of Financial Accounting Standards|"
    r"FASB Statement|FASB Interpretation|Staff Accounting Bulletin|Statement of Position|Opinion)"
    r"(?:\s+(?:No\.|Nos\.|Number|Issue|Topic))?\s*)\d[\d\-]*(?:\s*(?:and|,)\s*\d[\d\-]*)*")
_Y2K = re.compile(r"\b(?:Year\s+2000|Y2K)\b", re.I)
# capitalised words, not inside [PLACEHOLDER] brackets
_CAPWORD = re.compile(r"(?<![\w\[])[A-Z][A-Za-z0-9&'\-]*[A-Za-z0-9](?![\w\]])")
_LOWERWORD = re.compile(r"\b[a-z][a-z'\-]*[a-z]\b")
VOCAB_MIN_FIRMS = 5
_STATES = ("Alabama|Alaska|Arizona|Arkansas|California|Colorado|Connecticut|Delaware|Florida|Georgia|"
           "Hawaii|Idaho|Illinois|Indiana|Iowa|Kansas|Kentucky|Louisiana|Maine|Maryland|Massachusetts|"
           "Michigan|Minnesota|Mississippi|Missouri|Montana|Nebraska|Nevada|New Hampshire|New Jersey|"
           "New Mexico|New York|North Carolina|North Dakota|Ohio|Oklahoma|Oregon|Pennsylvania|"
           "Rhode Island|South Carolina|South Dakota|Tennessee|Texas|Utah|Vermont|Virginia|Washington|"
           "West Virginia|Wisconsin|Wyoming|District of Columbia|Puerto Rico")
_CITIES = ("Atlanta|Austin|Baltimore|Boston|Charlotte|Chicago|Cincinnati|Cleveland|Columbus|Dallas|Denver|"
           "Detroit|Fort Worth|Houston|Indianapolis|Jacksonville|Kansas City|Las Vegas|Los Angeles|Memphis|"
           "Miami|Milwaukee|Minneapolis|Nashville|New Orleans|Oklahoma City|Orlando|Philadelphia|Phoenix|"
           "Pittsburgh|Portland|Princeton|Raleigh|Sacramento|Salt Lake City|San Antonio|San Diego|"
           "San Francisco|San Jose|Seattle|St\\. Louis|Tampa|Tucson")
_PLACE = re.compile(r"\b(?:(?:[A-Z][a-z]+\s){0,2}[A-Z][a-z]+,\s+)?(?:" + _STATES + "|" + _CITIES + r")\b")
_CASE = re.compile(r"\b(?:MDL|Multiple District Litigation|Multidistrict Litigation|Master File|Case|Civil Action|Docket|Cause|Action|Index|Adversary Proceeding)"
                   r"(?:\s+(?:No\.?|Nos\.?|Number))?\s*[A-Z\d][\w\-:]*(?:\s[A-Z]{1,4}\s?\d[\w\-]*)?"
                   r"|\b\d{1,2}[\s\-](?:C|CV|Civ|cv)[\s\-]?\d{2,6}\b")
_LEGAL = re.compile(r"[,.]?\s+" + SUFFIXES + r"\b\.?$", re.I)
# words too common to redact on their own even if they appear in a firm name
_COMMON = {"american", "national", "international", "united", "general", "first", "new", "the", "and",
           "global", "systems", "services", "technologies", "technology", "industries", "financial",
           "communications", "energy", "health", "healthcare", "capital", "resources", "solutions",
           "group", "holdings", "corp", "inc", "company", "of", "bank", "pharmaceuticals", "software",
           "co", "us", "usa", "oil", "gas", "net", "tel", "air", "big", "one", "all", "pan", "old", "west",
           "east", "bio", "med", "pro", "tri", "nu"}


def name_aliases(name):
    """'ENRON CORP /OR/' -> ['ENRON CORP', 'ENRON'] (longest first; matched case-insensitively)."""
    name = re.sub(r"\s*[/\\].*$", "", name or "").strip()  # EDGAR state suffix like /DE/ or \DE\
    if not name:
        return []
    base = _LEGAL.sub("", name).strip(" ,.")
    forms = {name, base}
    forms |= {w for w in re.findall(r"[A-Za-z][A-Za-z&'\-]{3,}", base) if w.lower() not in _COMMON}
    first = re.match(r"[A-Za-z]{2,3}\b", base)  # short brand-like first word, e.g. KVH, FYI
    if first and first.group(0).lower() not in _COMMON:
        forms.add(first.group(0))
    return sorted({f for f in forms if f}, key=len, reverse=True)


def firm_aliases(firm):
    """Aliases from a firm's current and former EDGAR names, longest first."""
    names = [firm.get("name", "")] + list(firm.get("former_names", []))
    return sorted({a for n in names for a in name_aliases(n)}, key=len, reverse=True)


def generic_vocab(texts_by_firm, min_firms=VOCAB_MIN_FIRMS):
    """Capitalised words used by at least min_firms different firms, or whose lowercase
    form is an ordinary word used by that many firms. Everything else is identifying."""
    cap, low = collections.Counter(), collections.Counter()
    for texts in texts_by_firm.values():
        joined = "\n".join(texts)
        cap.update(set(_CAPWORD.findall(joined)))
        low.update(set(_LOWERWORD.findall(joined)))
    return {w for w, n in cap.items() if n >= min_firms or low[w.lower()] >= min_firms}


def mask(text, t, aliases=(), vocab=None):
    if not text:
        return ""
    for a in aliases:
        if re.fullmatch(r"[A-Za-z]{2,5}", a):  # short acronym: also match the dotted form, e.g. F.Y.I.
            pattern = r"\.?".join(map(re.escape, a)) + r"\.?"
        else:
            pattern = re.escape(a).replace(r"\ ", r"[\s,]+")
        text = re.sub(r"(?<![\w.])" + pattern + r"(?![\w])", "[COMPANY]", text, flags=re.I)
    text = _AUDITORS.sub("[AUDITOR]", text)
    text = _PERSON.sub("[PERSON]", text)
    text = _ENTITY.sub(lambda m: m.group(0) if "[COMPANY]" in m.group(0) else "[ENTITY]", text)
    if vocab is not None:
        text = _STANDARD.sub(lambda m: m.group(1) + "[#]", text)
        text = _Y2K.sub("[Y2K]", text)
        text = _CASE.sub("[CASENO]", text)
        text = _PLACE.sub("[PLACE]", text)
        text = _CAPWORD.sub(lambda m: m.group(0) if m.group(0) in vocab else "[NAME]", text)
        # merge runs like "[NAME] K. [NAME]" or "[NAME] & [NAME]" into one placeholder
        text = re.sub(r"\[NAME\](?:[\s,.&'\-]*(?:[A-Z]\.\s*)*\[NAME\])+", "[NAME]", text)

    def year(m):
        k = int(m.group(1)) - t
        return "Year T" if k == 0 else f"Year T{k:+d}"
    return _YEAR.sub(year, text)

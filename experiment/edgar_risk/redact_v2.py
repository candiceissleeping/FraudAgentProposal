"""Round-8 L2 redaction: cut the path from a 10-K back to the company's identity, keep its content.

Order matters (see results/round8/protocol.md section 4):
  1. URLs / e-mails
  2. identifiers from a per-company list (company names, tickers, people, auditors, addresses)
  3. format patterns (SEC file numbers, EIN, phone numbers, case numbers)
  4. remaining proper nouns -> numbered [NAME_n] / [COUNTRY_n], consistent within one packet
  5. years -> Y0, Y-1, ...
  6. monetary amounts x k (one secret factor per company); non-monetary counts -> 2 significant digits

Steps 5-6 come after 4 so that "Y0" and scaled numbers are never mistaken for proper nouns.
"""
import math
import re

from .redact import KEEP as _KEEP_V1, URL, YEAR, _common_words

COUNTRIES = [
    "United Kingdom", "South Korea", "North Korea", "South Africa", "New Zealand", "Saudi Arabia", "Hong Kong",
    "Czech Republic", "Dominican Republic", "Costa Rica", "Puerto Rico", "United Arab Emirates", "El Salvador",
    "China", "Japan", "Canada", "Mexico", "Germany", "France", "Italy", "Spain", "Portugal", "Netherlands",
    "Belgium", "Switzerland", "Austria", "Sweden", "Norway", "Denmark", "Finland", "Ireland", "Poland",
    "Hungary", "Romania", "Bulgaria", "Greece", "Turkey", "Russia", "Ukraine", "Israel", "Egypt", "Nigeria",
    "Kenya", "Morocco", "India", "Pakistan", "Bangladesh", "Indonesia", "Malaysia", "Singapore", "Thailand",
    "Vietnam", "Philippines", "Taiwan", "Korea", "Australia", "Brazil", "Argentina", "Chile", "Colombia",
    "Peru", "Venezuela", "Ecuador", "Uruguay", "Paraguay", "Bolivia", "Guatemala", "Honduras", "Panama",
    "Luxembourg", "Bermuda", "Cayman Islands", "Qatar", "Kuwait", "Iran", "Iraq", "Serbia", "Croatia",
    "Slovakia", "Slovenia", "Lithuania", "Latvia", "Estonia", "Kazakhstan", "Ghana", "Algeria", "Angola",
    "Paraguay", "Scotland", "England", "Wales", "Britain", "Great Britain", "UK", "U.K.", "PRC", "P.R.C.",
]
_COUNTRY_SET = {c for c in COUNTRIES}
REGIONS = {"Europe", "European", "Asia", "Asian", "Africa", "African", "America", "Americas", "American",
           "Latin", "North", "South", "EMEA", "APAC", "Pacific", "Atlantic", "Middle", "East", "Western", "Eastern"}
KEEP = (set(_KEEP_V1) - _COUNTRY_SET - {"China", "Canada", "Japan", "Mexico", "UK", "U.K."}) | REGIONS | {
    "COVID-19", "COVID", "Tax", "Cuts", "Jobs", "CARES", "Act", "Nasdaq", "Dodd-Frank", "Sarbanes-Oxley",
    "Treasury", "Fed", "Reserve", "Topic", "Subtopic", "Accounting", "Standards", "Update", "Codification",
    "Board's", "Inc.", "LLP", "Y0", "Y", "FY", "K", "Q"}

AUDITORS = [
    "PricewaterhouseCoopers", "Pricewaterhouse Coopers", "PwC", "Deloitte & Touche", "Deloitte", "KPMG",
    "Ernst & Young", "EY", "Grant Thornton", "BDO USA", "BDO", "RSM US", "RSM", "Marcum", "Moss Adams",
    "Crowe Horwath", "Crowe", "Baker Tilly", "CohnReznick", "Friedman", "BF Borgers", "Mazars", "Plante Moran",
    "EisnerAmper", "WithumSmith", "Withum", "Weinberg", "MaloneBailey", "Haskell & White", "Squar Milner",
    "Cherry Bekaert", "Dixon Hughes", "FORVIS", "Armanino", "Wipfli", "Eide Bailly", "BKD", "Elliott Davis",
    "Frazier & Deeter", "Salberg", "Rosenberg Rich Baker Berman", "KCCW", "Turner, Stone", "Whitley Penn",
]
SUFFIXES = {"INC", "INCORPORATED", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LIMITED", "PLC", "LLC", "LP",
            "L.P.", "HOLDINGS", "HOLDING", "GROUP", "THE", "N.V.", "S.A.", "AG", "SA", "NV", "/DE/", "/DE", "DE",
            "/MD/", "/NV/", "/NEW/", "NEW"}

TOKEN = re.compile(r"(?<![\w\[])([A-Z][A-Za-z0-9&'’.\-]*[A-Za-z0-9]|[A-Z])(?![\w\]])")
FILENAME = re.compile(r"\b[A-Za-z0-9]{1,8}-\d{8}(?:x\d+)?(?:_\w+)?(?:\.html?)?\b")
FILE_NO = re.compile(r"\b(?:000|001|002|333|811|814|028)-\d{4,6}\b")
EIN = re.compile(r"\b\d{2}-\d{7}\b")
PHONE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\b\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b")
CASE_NO = re.compile(r"(?i)\b((?:case|civil action|docket|index|file|claim)\s+(?:no\.?|number)\s*[:#]?\s*)"
                     r"[\w.:/\-]*\d[\w.:/\-]*")
ASU = re.compile(r"\bASU\s+(?:No\.\s*)?(?:19|20)\d\d-\d{2}\b")
FY = re.compile(r"\b(?:FY|fiscal(?:\s+year)?)\s*['’]?(\d{2}|\d{4})\b", re.I)
APOS_YEAR = re.compile(r"(?<=\s)['’](\d{2})\b")
MONEY = re.compile(r"(\$\s?\(?\s?)(\d[\d,]*(?:\.\d+)?)")
CELL_NUM = re.compile(r"^(\(?\$?\s?\(?)(\d[\d,]*(?:\.\d+)?)(\)?)$")
UNIT = re.compile(r"\bin\s+(?:thousands|millions|billions)\b|\b(?:dollars|amounts)\s+in\s+(?:thousands|millions)", re.I)
COUNT = re.compile(r"\b(\d{1,3}(?:,\d{3})+|\d{3,})(\s+(?:full[- ]time\s+|part[- ]time\s+|approximately\s+)?"
                   r"(?:employees|associates|team members|stores|locations|restaurants|facilities|offices|branches|"
                   r"customers|square feet|sq\.\s*ft\.|acres|vessels|aircraft|patients|members|subscribers|hospitals|"
                   r"clinics|warehouses|distribution centers|plants|dealers|franchisees|units|sites|towers|miles))\b", re.I)
SKIP_ROW = re.compile(r"(?i)(\bshares?\b(?!.*\bper\b)|employees|headcount|number of|\bdays\b|\bmonths?\b|"
                      r"\byears?\b(?!\s+ended)|\brate\s*$|\bratio\b|%|percent|basis points|square feet|acres|"
                      r"useful li(?:fe|ves)|\bterm\b)")


def _core_tokens(name):
    """'BECTON DICKINSON & CO' -> ['BECTON', 'DICKINSON']; 'BUNGELTD' -> ['BUNGE']."""
    name = re.sub(r"\s+/\w+/?$", "", name.strip())
    toks = [t for t in re.split(r"[\s,]+", name) if t]
    toks = [re.sub(r"(?<=\w)(LTD|INC|CORP)$", "", t) if len(toks) == 1 else t for t in toks]
    while toks and toks[-1].upper().strip(".,") in SUFFIXES:
        toks.pop()
    while toks and toks[0].upper() == "THE":
        toks.pop(0)
    return [t.strip(".,") for t in toks if t.strip(".,&")]


def name_patterns(names, text):
    """Regexes (case-insensitive) for a company's names, longest first, plus distinctive single words."""
    lower = _common_words(text)
    pats, words = [], set()
    for n in names:
        toks = [t for t in _core_tokens(n) if t != "&"]
        if not toks:
            continue
        sep = r"[\s,.\-]*(?:and\s+|&\s*)?"
        pats.append(r"(?<![A-Za-z])" + sep.join(re.escape(t) for t in toks) + r"(?:[\s,]+(?:Inc|Corp|Co|Ltd|"
                    r"Company|Corporation|Incorporated|Holdings|plc|LLC)\b\.?)?(?![a-z])")
        if len(toks) == 1 and " " not in toks[0] and len(toks[0]) >= 4 and toks[0][0].isalpha():
            # a one-word name such as THEMAVEN also appears as "theMaven" / "Maven"
            words.add(toks[0])
        for t in toks:
            if len(t) >= 4 and t.isalpha() and lower.get(t.lower(), 0) == 0 and t.capitalize() not in KEEP:
                words.add(t)
    pats += [rf"(?<![A-Za-z]){re.escape(w)}(?![a-z])" for w in sorted(words, key=len, reverse=True)]
    return sorted(set(pats), key=len, reverse=True)


def person_names(text):
    """Signers of the 10-K: '/s/ John A. Smith' (also catches the audit firm's signature)."""
    out = set()
    for m in re.finditer(r"/s/\s*([A-Z][A-Za-z.'’\- ]{2,40}?)(?=\s{2,}|\s*\n|\s*,|\s*$|\s+(?:Chief|President|"
                         r"Director|Chairman|Executive|Senior|Vice|Treasurer|Secretary|Controller|Principal))",
                         text, re.M):
        n = m.group(1).strip()
        if any(a.lower() in n.lower() for a in AUDITORS) or "LLP" in n:
            continue
        out.add(n)
    return sorted(out)


def _fmt(orig, value):
    dec = len(orig.split(".")[1]) if "." in orig else 0
    s = f"{value:,.{dec}f}" if ("," in orig or len(orig.split(".")[0]) < 4) else f"{value:.{dec}f}"
    return s


def _sig2(n):
    if n < 100:
        return n
    p = 10 ** (int(math.log10(n)) - 1)
    return int(round(n / p) * p)


class L2Redactor:
    def __init__(self, ident, fiscal_year, k, reference_text):
        self.k, self.fy = k, fiscal_year
        self.lower = _common_words(reference_text)
        self.subs = []   # (compiled regex, placeholder)
        for p in name_patterns(ident.get("names", []), reference_text):
            self.subs.append((re.compile(p, re.I), "[COMPANY]"))
        for t in ident.get("tickers", []):   # 3+ letter tickers also in lower case (file names, URLs)
            self.subs.append((re.compile(rf"(?<![\w\[]){re.escape(t)}(?![\w\]])", re.I if len(t) >= 3 else 0),
                              "[TICKER]"))
        for a in sorted(AUDITORS, key=len, reverse=True):
            self.subs.append((re.compile(rf"(?<![A-Za-z]){re.escape(a)}(?:\s+LLP|\s+&\s+Co\.?|\s+P\.?C\.?)?(?![a-z])"),
                              "[AUDITOR]"))
        people = ident.get("people", [])
        for i, p in enumerate(people, 1):
            toks = [t for t in re.split(r"\s+", p) if len(t.strip(".")) > 1]
            full = r"\s+(?:[A-Z]\.\s+)?".join(re.escape(t) for t in toks)
            self.subs.append((re.compile(rf"(?<![A-Za-z]){full}(?![a-z])"), f"[PERSON_{i}]"))
            if toks and len(toks[-1]) >= 3:
                self.subs.append((re.compile(rf"(?<![A-Za-z]){re.escape(toks[-1])}(?![a-z])"), f"[PERSON_{i}]"))
        for s in ident.get("addresses", []):
            if len(s) >= 4:
                self.subs.append((re.compile(rf"(?<![A-Za-z0-9]){re.escape(s)}(?![A-Za-z0-9])", re.I), "[ADDRESS]"))
        for d in ident.get("numbers", []):  # CIK, EIN, zip, phone digits
            digits = re.sub(r"\D", "", str(d))
            if len(digits) >= 5:
                rx = r"[\s.\-()]*".join(digits)
                self.subs.append((re.compile(rf"(?<!\d)0*{rx}(?!\d)"), "[ID]"))
        self.entities, self.countries = {}, {}

    # ---------------------------------------------------------------- steps
    def _identifiers(self, text):
        for rx, ph in self.subs:
            text = rx.sub(ph, text)
        return text

    @staticmethod
    def _patterns(text):
        text = URL.sub("[URL]", text)
        text = FILENAME.sub("[ID]", text)  # e.g. adm-20221231.htm carries the ticker and the period
        text = FILE_NO.sub("[ID]", text)
        text = EIN.sub("[ID]", text)
        text = PHONE.sub("[ID]", text)
        text = CASE_NO.sub(lambda m: m.group(1) + "[CASE_NO]", text)
        return ASU.sub("ASU [no.]", text)

    def _is_common(self, tok):
        core = tok.rstrip(".").removesuffix("'s").removesuffix("’s")
        if tok in KEEP or core in KEEP or re.fullmatch(r"Y[+\-]?\d+", core):
            return True
        if core.isupper() and len(core) > 1:
            return core.capitalize() in KEEP or self.lower.get(core.lower(), 0) >= 3  # headings: AND, TO, OF
        parts = re.split(r"[-'’]", core)
        return all(self.lower.get(p.lower(), 0) >= 2 for p in parts if p)

    def _proper_nouns(self, text):
        for c in sorted(COUNTRIES, key=len, reverse=True):
            def csub(m, c=c):
                key = c.replace(".", "").upper()
                self.countries.setdefault(key, len(self.countries) + 1)
                return f"[COUNTRY_{self.countries[key]}]"
            text = re.sub(rf"(?<![\w\[]){re.escape(c)}(?![\w\]])", csub, text)
        spans = [(m.start(), m.end()) for m in TOKEN.finditer(text) if not self._is_common(m.group(1))]
        runs = []
        for s, e in spans:   # join "Fox River", "Bank of Montreal", "Smith & Wesson" into one entity
            if runs and re.fullmatch(r"[\s&.'’\-]*(?:(?:of|de|du|la|del|von|van)\s+)?", text[runs[-1][1]:s]):
                runs[-1][1] = e
            else:
                runs.append([s, e])
        out, last = [], 0
        for s, e in runs:
            key = re.sub(r"\s+", " ", text[s:e]).lower().rstrip(".")
            self.entities.setdefault(key, len(self.entities) + 1)
            out += [text[last:s], f"[NAME_{self.entities[key]}]"]
            last = e
        out.append(text[last:])
        return "".join(out)

    def _rel(self, y):
        y = int(y)
        if y < 100:
            y += 2000 if y < 50 else 1900
        d = y - self.fy
        return "Y0" if d == 0 else f"Y{d:+d}"

    def _fiscal_years(self, text):
        """FY23 / fiscal 2023 / '23 -- before proper nouns, or "FY23" would be taken for a name."""
        text = FY.sub(lambda m: m.group(0)[: m.start(1) - m.start(0)].rstrip("'’ ") + " " + self._rel(m.group(1)), text)
        return APOS_YEAR.sub(lambda m: self._rel(m.group(1)), text)

    def _years(self, text):
        return YEAR.sub(lambda m: self._rel(m.group(1)), text)

    def _scale(self, num):
        v = float(num.replace(",", "")) * self.k
        return _fmt(num, v)

    def _scale_prose(self, line):
        line = MONEY.sub(lambda m: m.group(1) + self._scale(m.group(2)), line)
        return COUNT.sub(lambda m: f"{_sig2(int(m.group(1).replace(',', ''))):,}" + m.group(2), line)

    def _scale_row(self, line):
        cells = re.split(r"(\s{2,}|\s*\|\s*)", line)
        texts = cells[0::2]
        label = texts[0] if texts and not CELL_NUM.match(texts[0].strip()) else ""
        if label and SKIP_ROW.search(label):
            return line
        rng = {i for i, t in enumerate(texts) if t.strip().lower() == "to"}
        for i, t in enumerate(texts):
            st = t.strip()
            m = CELL_NUM.match(st)
            if not m or i in {j - 1 for j in rng} | {j + 1 for j in rng} or re.fullmatch(r"\(\d\)", st):
                continue
            if label == "" and i == 0 and not st.startswith("$"):
                pass
            texts[i] = t.replace(st, m.group(1) + self._scale(m.group(2)) + m.group(3))
        cells[0::2] = texts
        return "".join(cells)

    def _amounts(self, text):
        lines = text.split("\n")
        is_row = [(len(ln) < 400 and len(re.findall(r"(?:^|\s{2,}|\|)\s*\(?\$?\s?\d[\d,]*(?:\.\d+)?\)?(?=\s{2,}|\s*\||\s*$)",
                                                   ln)) >= 1 and re.search(r"\s{2,}|\|", ln) is not None) for ln in lines]
        out, i = [], 0
        while i < len(lines):
            if not is_row[i]:
                out.append(self._scale_prose(lines[i]))
                i += 1
                continue
            j = i
            while j < len(lines) and (is_row[j] or (len(lines[j]) < 120 and not lines[j].rstrip().endswith("."))):
                j += 1
            block = lines[i:j]
            ctx = "\n".join(lines[max(0, i - 4):j])
            money = "$" in "\n".join(block) or bool(UNIT.search(ctx))
            for ln, row in zip(block, is_row[i:j]):
                out.append(self._scale_row(ln) if (row and money) else self._scale_prose(ln) if not row else ln)
            i = j
        return "\n".join(out)

    # ---------------------------------------------------------------- public
    def l2(self, text):
        text = self._patterns(text)
        text = self._identifiers(text)
        text = self._fiscal_years(text)
        text = self._proper_nouns(text)
        text = self._years(text)
        return self._amounts(text)


def leak_audit(text, ident):
    """Count identifier strings that survive redaction (should all be zero)."""
    hits = {}
    for n in ident.get("names", []):
        for t in [" ".join(_core_tokens(n))] + [t for t in _core_tokens(n) if len(t) >= 4 and t.isalpha()]:
            c = len(re.findall(rf"(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", text, re.I))
            if c and t.upper() not in SUFFIXES:
                hits[f"name:{t}"] = c
    for t in ident.get("tickers", []):
        c = len(re.findall(rf"(?<![\w\[]){re.escape(t)}(?![\w\]])", text, re.I if len(t) >= 3 else 0))
        if c:
            hits[f"ticker:{t}"] = c
    for p in ident.get("people", []):
        for t in [p] + [w for w in p.split() if len(w.strip(".")) >= 3][-1:]:
            c = len(re.findall(rf"(?<![A-Za-z]){re.escape(t)}(?![A-Za-z])", text))
            if c:
                hits[f"person:{t}"] = c
    for s in ident.get("addresses", []):
        c = len(re.findall(rf"(?<![A-Za-z0-9]){re.escape(s)}(?![A-Za-z0-9])", text, re.I)) if len(s) >= 4 else 0
        if c:
            hits[f"address:{s}"] = c
    for d in ident.get("numbers", []):
        digits = re.sub(r"\D", "", str(d))
        if len(digits) >= 5 and re.search(rf"(?<!\d)0*{digits}(?!\d)", re.sub(r"[\s.\-()]", "", text)):
            hits[f"number:{d}"] = 1
    for a in AUDITORS:
        if len(a) > 3 and re.search(rf"(?<![A-Za-z]){re.escape(a)}(?![a-z])", text):
            hits[f"auditor:{a}"] = 1
    return hits


def top_caps(text, n=50):
    """Most frequent capitalised tokens left in a redacted packet, for manual review."""
    import collections
    c = collections.Counter(m.group(1) for m in TOKEN.finditer(text) if m.group(1) not in KEEP and len(m.group(1)) > 1)
    return c.most_common(n)

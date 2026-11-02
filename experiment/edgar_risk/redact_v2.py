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
FILE = re.compile(r"\S+\.(?:htm|html|xml|xsd|txt|jpe?g|gif|png|pdf)\b", re.I)   # npk20221231_10k.htm, admp-10k_123120.htm
YEAR2 = re.compile(r"(?<![\d$.,])(18\d\d|19\d\d|20[0-3]\d)(?!\d|,\d{3}|%)")       # also "founded in 1818"
PHONE7 = re.compile(r"(?<![\d$,.\-])\d{3}-\d{4}(?![\d,])")
ZIP = re.compile(r"(\]|\b[A-Z]{2})(,?\s+)\d{5}(?:-\d{4})?\b")
ENTITY_SUFFIX = re.compile(r"((?:[A-Z][\w&'’\-]*\s+){0,4}[A-Z][\w&'’\-]*),?\s+(?:Inc|LLC|Corp|Corporation|Ltd|L\.P\.|LP|"
                           r"plc|GmbH|S\.A\.)\b")
COUNT_WORDS = (r"shares|employees|associates|team members|stores|locations|restaurants|facilities|offices|branches|"
               r"customers|square feet|sq\.\s*ft\.|acres|vessels|aircraft|patients|members|subscribers|hospitals|"
               r"clinics|warehouses|distribution centers|plants|dealers|franchisees|units|sites|towers|miles")
PROSE_NUM = re.compile(r"(?P<pre>\$\s?\(?\s?)?(?<![\w.])(?P<num>\d[\d,]*(?:\.\d+)?)"
                       r"(?P<post>\s*(?:million|billion|thousand|trillion)\b|\s+(?:full[- ]time\s+|part[- ]time\s+)?"
                       rf"(?:{COUNT_WORDS})\b)?", re.I)
PER_SHARE_AFTER = re.compile(r"^\s*(?:per|a|each)\s+(?:common\s+|ordinary\s+|diluted\s+|basic\s+)?(?:share|unit)", re.I)
PER_SHARE_BEFORE = re.compile(r"(?:price|par value|per share)[^.$]{0,25}$", re.I)
PER_SHARE_LABEL = re.compile(r"(?i)per (?:common |ordinary |diluted |basic )?share|per unit|price per|par value|"
                             r"(?:share|stock|exercise|strike|offering|closing|market|conversion) price|"
                             r"dividends? (?:declared|paid) per")
SKIP_ROW2 = re.compile(r"(?i)%\s*$|\(%\)|as a % of|percent|\bratio\b|basis points|useful li(?:fe|ves)|\bdays\b|"
                       r"\bmonths?\b|\(?in years\)?|\byears\)|life \(years|term \(years|remaining (?:life|term)|volatility|"
                       r"\byield\b|\brates?\b(?!\s*(?:swap|contract|derivative|hedge|lock|cap|floor))")
FILE_NO = re.compile(r"\b(?:000|001|002|333|811|814|028)-\d{4,6}\b")
EIN = re.compile(r"\b\d{2}-\d{7}\b")
PHONE = re.compile(r"(?:\+?1[\s.\-]?)?\(?\b\d{3}\)?[\s.\-]\d{3}[\s.\-]\d{4}\b")
CASE_NO = re.compile(r"(?i)\b((?:case|civil action|docket|index|file|claim)\s+(?:no\.?|number)\s*[:#]?\s*)"
                     r"[\w.:/\-]*\d[\w.:/\-]*")
ASU = re.compile(r"\bASU\s+(?:No\.\s*)?(?:19|20)\d\d-\d{2}\b")
FY = re.compile(r"\b(?:FY|fiscal(?:\s+year)?)\s*['’]?(\d{2}|\d{4})\b", re.I)
APOS_YEAR = re.compile(r"(?<=\s)['’](\d{2})\b")
CELL_NUM = re.compile(r"^(\(?\$?\s?\(?)(\d[\d,]*(?:\.\d+)?)(\)?)$")


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


def acronyms(names, text):
    """Short forms a filing uses for itself: initials ('Becton Dickinson' -> BD, 'Archer-Daniels-Midland' -> ADM)
    and all-caps name words ('PDS'), kept only if the filing uses them at least 3 times. Matched case-sensitively,
    and also when glued to digits ('1ADM', 'PDS0101')."""
    out = set()
    for n in names:
        toks = [t for t in re.split(r"[\s\-]+", " ".join(_core_tokens(n))) if t and t[0].isalpha() and t != "&"]
        cands = [t for t in toks if t.isupper() and 2 <= len(t) <= 5 and t not in KEEP]
        if len(toks) >= 2:
            cands.append("".join(t[0] for t in toks).upper())
        for c in cands:
            if len(re.findall(rf"(?<![A-Za-z]){re.escape(c)}(?![A-Za-z])", text)) >= 3:
                out.add(c)
    return sorted(out, key=len, reverse=True)


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
        for a in acronyms(ident.get("names", []), reference_text):
            self.subs.append((re.compile(rf"(?<![A-Za-z\[]){re.escape(a)}(?![A-Za-z\]])"), "[COMPANY]"))
        for t in ident.get("tickers", []):   # 3+ letter tickers also in lower case and glued to digits (1ADM, bdx2019)
            if len(t) >= 3:
                self.subs.append((re.compile(rf"(?<![A-Za-z\[]){re.escape(t)}(?![A-Za-z\]])", re.I), "[TICKER]"))
            else:
                self.subs.append((re.compile(rf"(?<![\w\[]){re.escape(t)}(?![\w\]])"), "[TICKER]"))
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
        self.decisions = {}   # original number (>= 4 digits) -> {"scaled", "kept"}: the same number treated both ways
                              # would create a fake inconsistency in the packet

    # ---------------------------------------------------------------- steps
    def _identifiers(self, text):
        for rx, ph in self.subs:
            text = rx.sub(ph, text)
        return text

    @staticmethod
    def _patterns(text):
        text = URL.sub("[URL]", text)
        text = FILE.sub("[FILE]", text)    # source file names carry the ticker and the period
        text = FILENAME.sub("[ID]", text)
        text = FILE_NO.sub("[ID]", text)
        text = EIN.sub("[ID]", text)
        text = PHONE.sub("[ID]", text)
        text = PHONE7.sub("[ID]", text)
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

    def _suffix_entities(self, text):
        """'US Compounding, Inc.' -> [NAME_n] even though 'Compounding' is an ordinary word (subsidiaries are not
        all in our identifier list); the same words without the suffix are masked with the same number."""
        found = {}
        for m in ENTITY_SUFFIX.finditer(text):
            name = m.group(1).strip()
            if name.lower() in SEG_GENERIC or name in KEEP or len(name) < 4 or name.startswith("["):
                continue
            key = re.sub(r"\s+", " ", name).lower()
            self.entities.setdefault(key, len(self.entities) + 1)
            found[name] = f"[NAME_{self.entities[key]}]"
        for name in sorted(found, key=len, reverse=True):
            if " " in name:   # multi-word names also without the suffix; one-word names only with it
                text = re.sub(rf"(?<![\w\[]){re.escape(name)}(?![\w\]])", found[name], text)
            else:
                text = re.sub(rf"(?<![\w\[]){re.escape(name)}(?=,?\s+(?:Inc|LLC|Corp|Ltd|L\.P\.|LP|plc|GmbH|S\.A\.)\b)",
                              found[name], text)
        return text

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
        return YEAR2.sub(lambda m: self._rel(m.group(1)), text)

    # Scaling rule (protocol rev. 2): EVERY quantity is multiplied by k -- money, share counts, other counts --
    # except per-share amounts, percentages, ratios, rates and durations. Then net income / shares = EPS still
    # holds, and the same number is treated the same way wherever it appears.
    def _note(self, num, how):
        if len(re.sub(r"\D", "", num.split(".")[0])) >= 4:
            self.decisions.setdefault(num, set()).add(how)

    def _scale(self, num):
        self._note(num, "scaled")
        return _fmt(num, float(num.replace(",", "")) * self.k)

    def _scale_prose(self, line):
        def sub(m):
            pre, num, post = m.group("pre"), m.group("num"), m.group("post")
            if not pre and not post:
                return m.group(0)
            if pre and not post and (PER_SHARE_AFTER.match(line[m.end():m.end() + 30])
                                     or PER_SHARE_BEFORE.search(line[max(0, m.start() - 40):m.start()])):
                self._note(num, "kept")
                return m.group(0)
            return (pre or "") + self._scale(num) + (post or "")
        return PROSE_NUM.sub(sub, line)

    def _scale_row(self, line, header):
        cells = re.split(r"(\s{2,}|\s*\|\s*)", line)
        texts = cells[0::2]
        label = texts[0].strip() if texts and not CELL_NUM.match(texts[0].strip()) else ""
        plain = re.sub(r"[^a-z ]", "", label.lower()).strip()
        nums = [CELL_NUM.match(t.strip()) for t in texts[1:]]
        nums = [m.group(2) for m in nums if m]
        decimals = bool(nums) and all("." in n for n in nums)   # 2.92 / (0.81): per-share; 7,081: a share count
        per_share = decimals and (bool(PER_SHARE_LABEL.search(label)) or (
            plain in {"basic", "diluted", "basic and diluted", "basic earnings", "diluted earnings"}
            and "per" in header.lower() and "share" in header.lower()))
        if label and (per_share or SKIP_ROW2.search(label)):
            for t in texts[1:]:
                m = CELL_NUM.match(t.strip())
                if m:
                    self._note(m.group(2), "kept")
            return line
        rng = {i for i, t in enumerate(texts) if t.strip().lower() == "to"}
        near = {j - 1 for j in rng} | {j + 1 for j in rng}
        for i, t in enumerate(texts):
            st = t.strip()
            m = CELL_NUM.match(st)
            if not m or i in near or re.fullmatch(r"\(\d\)", st):
                continue
            texts[i] = t.replace(st, m.group(1) + self._scale(m.group(2)) + m.group(3))
        cells[0::2] = texts
        return "".join(cells)

    def _amounts(self, text):
        lines = text.split("\n")
        header = ""
        out = []
        prev = ""
        for ln in lines:
            m = CELL_NUM.match(ln.strip())
            if m and (prev.rstrip().endswith(("$", "$(")) or len(re.sub(r"\D", "", m.group(2).split(".")[0])) >= 4):
                # a number alone on a line: inline-XBRL breaks put "$" at the end of the line above
                out.append(ln.replace(m.group(2), self._scale(m.group(2))))
                prev = ln
                continue
            prev = ln
            row = (len(ln) < 400 and re.search(r"\s{2,}|\|", ln) is not None and
                   re.search(r"(?:^|\s{2,}|\|)\s*\(?\$?\s?\(?\d[\d,]*(?:\.\d+)?\)?(?=\s{2,}|\s*\||\s*$)", ln) is not None)
            if row:
                out.append(self._scale_row(ln, header))
            else:
                out.append(self._scale_prose(ln))
                if len(ln) < 200:
                    header = ln   # nearest line above a table row that has no numbers ("Earnings per share:")
        return "\n".join(out)

    def inconsistent_numbers(self):
        return sorted(n for n, d in self.decisions.items() if len(d) > 1)

    # ---------------------------------------------------------------- public
    def l2(self, text):
        text = self._patterns(text)
        text = self._identifiers(text)
        text = self._fiscal_years(text)
        text = self._suffix_entities(text)
        text = self._proper_nouns(text)
        text = ZIP.sub(lambda m: m.group(1) + m.group(2) + "[ID]", text)   # "[NAME_7] 07932" after the state is masked
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


# =============================================================================================== L3
ITEM_ORDER = ["1", "1a", "1b", "1c", "2", "3", "4", "5", "6", "7", "7a", "8", "9", "9a", "9b", "9c",
              "10", "11", "12", "13", "14", "15", "16"]
ITEM_HEAD = re.compile(r"^\s*item\s*(\d{1,2})\s*([a-c])?\s*[.:\-—–]?\s*(.*)$", re.I)
ITEM_TITLE = re.compile(r"(?i)^(business|risk|unresolved|cybersecurity|propert|legal|mine|submission|market|selected|"
                        r"\[?reserved|management|quantitative|financial statements|changes in|controls|other information|"
                        r"disclosure regarding|directors|executive compensation|security ownership|certain relationships|"
                        r"principal account|exhibits?|form 10-k|$)")


def split_items(text):
    """[(item_key, first_line, end_line)] for the body of a 10-K; front matter is item '0'.

    A heading starts with 'Item N' (or 'ITEM' alone on a line followed by 'N. TITLE'), has a recognised title and no
    trailing page number (lines with page numbers are the table of contents). When the table of contents writes
    'ITEM' in capitals, only capitalised headings count (mixed-case 'Item 8. ...' lines are then hyperlinks /
    cross-references). Among the candidates the longest run of increasing items is kept, earliest occurrence first,
    so repeated page headers and stray cross-references cannot break the order."""
    lines = text.split("\n")
    cands, toc_upper = [], []
    for i, ln in enumerate(lines):
        probe = ln
        if ln.strip().lower() == "item" and i + 1 < len(lines) and re.match(r"\s*\d", lines[i + 1]):
            probe = ln.strip() + " " + lines[i + 1].strip()
        m = ITEM_HEAD.match(probe)
        if not m or len(probe) > 160:
            continue
        key = m.group(1) + (m.group(2) or "").lower()
        if key not in ITEM_ORDER or not ITEM_TITLE.match(m.group(3).strip()):
            continue
        upper = probe.lstrip()[:4] == "ITEM"
        if re.search(r"\s{2,}\d{1,3}\s*$", probe):
            toc_upper.append(upper)
            continue
        cands.append((i, ITEM_ORDER.index(key), upper))
    if toc_upper and sum(toc_upper) > len(toc_upper) / 2 and sum(c[2] for c in cands) >= 4:
        cands = [c for c in cands if c[2]]
    best, prev = [1] * len(cands), [-1] * len(cands)
    for j in range(len(cands)):
        for i in range(j):
            if cands[i][1] < cands[j][1] and best[i] + 1 > best[j]:
                best[j], prev[j] = best[i] + 1, i
    heads = []
    if cands:
        j = max(range(len(cands)), key=lambda x: (best[x], -x))
        while j >= 0:
            heads.append((ITEM_ORDER[cands[j][1]], cands[j][0]))
            j = prev[j]
        heads.reverse()
    out = [("0", 0, heads[0][1] if heads else len(lines))]
    for n, (key, i) in enumerate(heads):
        out.append((key, i, heads[n + 1][1] if n + 1 < len(heads) else len(lines)))
    return out


L3_KEEP = {"1a", "1b", "3", "7", "7a", "8", "9", "9a", "9b"}
FIN_START = re.compile(r"(?i)^\s*(report of independent registered public accounting firm|index to (?:consolidated )?"
                       r"financial statements|(?:consolidated )?balance sheets?\s*$|(?:we )?have audited the accompanying)")
DESCRIPTIVE = re.compile(
    r"(?i)\b(?:we|the company|\[company\])\s+(?:is|are)\s+(?:a|an|the|one of)\b|headquarter|principal executive offices|"
    r"\b(?:the|a)\s+(?:leading|largest|premier|foremost)\b|\b(?:the|a)\s+(?:only|sole)\s+(?:company|provider|"
    r"manufacturer|producer|supplier|maker|developer)\b|\b(?:market|industry|world|global)[- ]leader|\bleader in\b|"
    r"market share|\bpioneer|#\s?1\b|\bno\.\s?1\b|\bfounded in\b|\bincorporated in\b|initial public offering|"
    r"went public|special purpose acquisition|\bSPAC\b")
SENT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\[(\"“])")
SEG_PHRASE = re.compile(r"((?:[A-Z][\w’'&/\-]*|\[[A-Z_0-9]+\])(?:\s+(?:and|&|of|[A-Z][\w’'&/\-]*|\[[A-Z_0-9]+\])){0,5})"
                        r"\s+(?:reportable\s+|operating\s+|business\s+)?segments?\b")
SEG_GENERIC = {"the", "our", "each", "other", "all", "all other", "total", "reportable", "operating", "business", "two",
               "three", "four", "five", "one", "its", "this", "that", "these", "corporate", "geographic", "single",
               "same", "prior", "segment", "consolidated", "revenue", "revenues", "net", "and", "of", "in", "by",
               "for", "a", "an", "y0", "company", "[company]", "remaining", "new", "both", "such", "every", "which"}
SIC2 = {"13": "Oil and gas extraction", "20": "Food and kindred products", "28": "Chemicals and allied products",
        "34": "Fabricated metal products", "35": "Industrial and commercial machinery and computer equipment",
        "36": "Electronic and other electrical equipment", "37": "Transportation equipment",
        "38": "Measuring, analyzing and controlling instruments; medical goods", "48": "Communications",
        "50": "Wholesale trade - durable goods", "60": "Depository institutions"}


def segment_names(text):
    """Business-segment names ('Ag Services and Oilseeds segment', 'Housewares/Small Appliance segment'),
    taken from phrases that precede 'segment(s)' at least twice; generic leading words are dropped."""
    import collections
    c = collections.Counter()
    for m in SEG_PHRASE.finditer(text):
        words = m.group(1).split()
        while words and words[0].lower() in SEG_GENERIC:
            words.pop(0)
        phrase = " ".join(words)
        if phrase and phrase.lower() not in SEG_GENERIC and not re.fullmatch(r"(?:\[[A-Z_0-9]+\]\s*)+", phrase):
            c[phrase] += 1
    return sorted([p for p, n in c.items() if n >= 2], key=len, reverse=True)


SEG_WORD_KEEP = {"Services", "Solutions", "Products", "Systems", "Group", "Other", "Corporate", "Business", "Segment",
                 "Total", "International", "Global", "North", "South", "East", "West", "America", "Americas", "Europe",
                 "Asia", "Pacific", "Consumer", "Commercial", "Industrial", "Specialty", "Retail", "Wholesale"}


def mask_segments(text, names):
    """Mask each segment name, then each distinctive word of it on its own ('Ag Services & Oilseeds',
    'Rhythm Management'): capitalised or upper-case forms only, so ordinary lower-case prose is untouched."""
    for i, p in enumerate(names, 1):
        flags = re.I if " " in p else 0
        text = re.sub(rf"(?<![\w\[]){re.escape(p)}(?![\w\]])", f"[SEGMENT_{i}]", text, flags=flags)
    for i, p in enumerate(names, 1):
        for w in re.findall(r"[A-Z][\w’'\-]{3,}", p):
            if w in SEG_WORD_KEEP:
                continue
            for form in {w, w.upper()}:
                text = re.sub(rf"(?<![\w\[]){re.escape(form)}(?![\w\]])", f"[SEGMENT_{i}]", text)
    return text


def drop_descriptive(text):
    """Remove self-description, market-position and history sentences from prose (table rows are kept)."""
    out, dropped = [], 0
    for ln in text.split("\n"):
        if re.search(r"\s{2,}\S", ln) and re.search(r"\d", ln):   # table row
            out.append(ln)
            continue
        sents = SENT.split(ln)
        keep = [s for s in sents if not DESCRIPTIVE.search(s)]
        dropped += len(sents) - len(keep)
        if keep:
            out.append(" ".join(keep))
    return "\n".join(out), dropped


MARK = "\x00SECTION:{}\x00"
MARK_RX = re.compile(r"\x00SECTION:(\w+)\x00\n?")


def mark_sections(text):
    """Insert a marker line before each section found in the ORIGINAL text; redaction leaves the markers alone
    (they contain no letters a pattern looks for), so the redacted text can be split at the same places."""
    lines = text.split("\n")
    out = []
    starts = {a: key for key, a, b in split_items(text)}
    for i, ln in enumerate(lines):
        if i in starts:
            out.append(MARK.format(starts[i]))
        out.append(ln)
    return "\n".join(out)


def unmark(text):
    return MARK_RX.sub("", text)


def l3_select(marked):
    """Keep Items 1A, 1B, 3, 7, 7A, 8, 9, 9A, 9B; when Item 8 only points elsewhere, keep the financial statements
    that follow in Items 15/16 (from the auditor's report / statement index onwards)."""
    parts = MARK_RX.split(marked)            # ['', key, body, key, body, ...]
    secs = list(zip(parts[1::2], parts[2::2]))
    keep, kept = [], []
    for key, body in secs:
        if key in L3_KEEP:
            keep.append(body)
            kept.append(key)
    item8 = "".join(b for k, b in secs if k == "8")
    if len(item8) < 5000:
        later = "\n".join(b for k, b in secs if k in ("15", "16")).split("\n")
        start = next((i for i, ln in enumerate(later) if FIN_START.match(ln)), None)
        if start is not None:
            keep.append("\n".join(later[start:]))
            kept.append("FS-from-15/16")
    return "\n".join(keep), kept


def l3_stub(sic, total_assets, period):
    sic2 = str(sic)[:2]
    size = ("under $100 million" if total_assets < 1e8 else "$100 million - $1 billion" if total_assets < 1e9 else
            "$1 - 10 billion" if total_assets < 1e10 else "over $10 billion")
    q = (int(period[5:7]) - 1) // 3 + 1
    return (f"[Item 1 Business has been removed for this study.] Industry: {SIC2.get(sic2, 'SIC ' + sic2)} "
            f"(SIC {sic2}) | Size: total assets {size} | Fiscal year ends in calendar quarter {q}")

"""Extract financial-statement line items from raw EDGAR 10-K submissions (round 5).

Both HTML tables and fixed-width text tables are reduced to "rows": a label plus the numbers
on that line.  Statements are located by anchor rows (total assets, net cash from operating
activities, ...), and the year header nearest above an anchor decides which column is Y0.
"""
import html
import re
from html.parser import HTMLParser

NUM = re.compile(r"\(?-?\$?\s*\d[\d,]*(?:\.\d+)?\s*\)?|(?<![\w])[—–-]{1,2}(?![\w])")
YEAR = re.compile(r"^(19[89]\d|20[0-2]\d)$")


class _Rows(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.rows, self.cells, self.cell, self.in_table = [], None, None, 0
        self.text = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table += 1
        elif tag == "tr" and self.in_table:
            self.cells = []
        elif tag in ("td", "th") and self.cells is not None:
            self.cell = []
        elif tag in ("br", "p", "div") and not self.in_table:
            self.text.append("\n")

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self.cell is not None and self.cells is not None:
            self.cells.append(" ".join("".join(self.cell).split()))
            self.cell = None
        elif tag == "tr" and self.cells is not None:
            line = "   ".join(c for c in self.cells if c)
            if line.strip():
                self.rows.append(line)
            self.cells = None
        elif tag == "table":
            self.in_table = max(0, self.in_table - 1)
            self.rows.append("")

    def handle_data(self, data):
        if self.cell is not None:
            self.cell.append(data)
        elif not self.in_table or self.cells is None:
            # Text outside tables, and SGML <TABLE> blocks of fixed-width text with no <tr> rows.
            self.text.append(data)
            for ln in data.splitlines():
                if ln.strip():
                    self.rows.append(ln)


def doc_lines(raw):
    """Turn a filing (HTML or text) into a list of text lines, one per table row / text line."""
    if re.search(r"<tr[\s>]", raw, re.I):
        p = _Rows()
        p.feed(raw)
        lines = p.rows
    else:
        lines = html.unescape(re.sub(r"<[^>]+>", " ", raw)).splitlines()
    out = []
    for ln in lines:
        ln = ln.replace("\xa0", " ").rstrip()
        # HTML tables often split "(1,234" and ")" or "$" and "1,234" into separate cells.
        ln = re.sub(r"\(\s+", "(", ln)
        ln = re.sub(r"\s+\)", ")", ln)
        ln = re.sub(r"\$\s+", "$", ln)
        out.append(ln)
    return out


def to_num(tok):
    t = tok.strip()
    if re.fullmatch(r"[—–-]{1,2}", t):
        return 0.0
    neg = t.startswith("(") or t.startswith("-") or t.endswith(")")
    t = re.sub(r"[()$,\s-]", "", t)
    if not t:
        return None
    try:
        v = float(t)
    except ValueError:
        return None
    return -v if neg else v


def split_row(line):
    """Return (label, [numbers]) for a statement line; footnote markers like (1) are dropped."""
    m = re.search(r"(?<![A-Za-z])(\(?\$?\s*\d[\d,]*(?:\.\d+)?\)?|[—–]|--?)(\s|$)", line)
    if not m:
        return line.strip(), []
    label = line[:m.start()].strip(" .:$")
    rest = line[m.start():]
    nums = []
    for tok in NUM.findall(rest):
        v = to_num(tok)
        if v is not None:
            nums.append(v)
    label = re.sub(r"\s*\(\d\)\s*$", "", label)
    return label, nums


def norm(label):
    s = label.lower().replace("’", "'").replace("`", "'")
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\.{2,}.*$", "", s)
    return s.strip(" .:-")


def year_header(lines, i, back=60):
    """Years in the closest header row above line i (e.g. ['2003', '2002'])."""
    for j in range(i - 1, max(0, i - back), -1):
        toks = re.findall(r"\b(?:19[89]\d|20[0-2]\d)\b", lines[j])
        words = re.sub(r"\b(?:19[89]\d|20[0-2]\d)\b|fiscal|years?|ended|december|january|february|march|april|"
                       r"may|june|july|august|september|october|november|\d+|,|weeks?|as of|at|and", "",
                       lines[j].lower())
        if len(toks) >= 2 and len(words.strip()) < 40:
            return [int(t) for t in toks]
    return None


def unit_near(lines, i, back=120):
    """Scale to millions from the nearest unit statement above line i."""
    for j in range(i, max(0, i - back), -1):
        s = lines[j].lower()
        if re.search(r"in millions|\(millions|millions of dollars|\$ ?millions|dollars in millions", s):
            return 1.0
        if re.search(r"in thousands|\(thousands|thousands of dollars|\(000'?s?\)|000'?s omitted|\$000|"
                     r"dollars in thousands|\(in 000", s):
            return 0.001
        if re.search(r"in billions", s):
            return 1000.0
    return None


SYN = {
    # balance sheet
    "cash": r"^(total )?cash(,)? and (cash )?equivalents|^cash and short-term investments|^cash$|^cash and temporary",
    "ar": r"receivables?|^receivable",
    "inv": r"^(total )?inventor|^merchandise inventor",
    "tca": r"^total current assets",
    "ppe": r"(property|plant|equipment).*net$|^net property|^property, plant and equipment, net|^net plant|"
           r"^property and equipment, (less|net)|^total property.*net",
    "ta": r"^total assets$|^total assets ",
    "tcl": r"^total current liabilities",
    "ltd": r"^long-term debt|^long term debt|^long-term borrowings|^senior debt",
    "tl": r"^total liabilities$",
    "eq": r"^total (stockholders|shareholders|share owners|shareowners|common stockholders|common shareholders)'? ?"
          r"(equity|investment)|^total equity$|^(stockholders|shareholders)'? equity$",
    "tle": r"^total liabilities and",
    "re": r"^retained earnings|^accumulated deficit|^reinvested earnings|^earnings (retained|reinvested)|"
          r"^retained (deficit|earnings \(deficit\))|^(accumulated|retained) (earnings|deficit)",
    # income statement
    "rev": r"^(total )?(net )?(sales|revenues?|operating revenues?)$|^total (net )?(sales|revenues?)|"
           r"^net sales and (operating )?revenues?|^revenues?, net|^sales and (other )?(operating )?revenues?$|"
           r"^net (sales|revenues?)",
    "cogs": r"^(total )?cost of (goods sold|sales|products sold|revenues?|merchandise sold|products and services)|"
            r"^cost of sales",
    "gp": r"^gross (profit|margin)",
    "sga": r"selling,? general,? (and|&) administrative|^selling, administrative|^marketing, general|"
           r"^selling and administrative|^general and administrative",
    "dep": r"^depreciation(,)? (and|&) amortization|^depreciation$|^depreciation, depletion",
    "ni": r"^net (income|earnings|loss|\(loss\) income|income \(loss\)|\(loss\) earnings|earnings \(loss\))"
          r"( for the (year|period))?( applicable to common.*| available to common.*| attributable to [a-z .,-]+)?$",
    "eps_d": r"^diluted|assuming (full )?dilution|^net income per share.*diluted|^earnings per share.*diluted",
    "sh_d": r"(weighted|average).*dilut|^diluted.*shares|^shares.*dilut",
    # cash flow statement
    "cfo": r"^net cash (provided by|from|provided from|used in|\(used in\)|provided by \(used in\)|"
           r"used for|generated (by|from)).*operat|^cash (provided by|from|flows? from) operat.*$|"
           r"^net cash flows? (provided by |from )?operat",
    "cfi": r"^net cash.*investing|^cash (used in|from|provided by) investing|^net cash flows? .*investing",
    "cff": r"^net cash.*financing|^cash (used in|from|provided by) financing|^net cash flows? .*financing",
    "fx": r"^effect of (foreign )?(currency )?exchange rate|exchange rate (changes|effect)|^effect of exchange",
    "dcash": r"^net (increase|decrease|change|\(decrease\) increase|increase \(decrease\)|decrease \(increase\))"
             r".*cash",
    "cash_beg": r"beginning of (the )?(year|period)|^balance at beginning",
    "cash_end": r"end of (the )?(year|period)|^balance at end",
    "issue": r"^(net )?proceeds from (the )?(issuance|sale|exercise)|^issuance of (common|long-term|debt|notes|stock)|"
             r"^proceeds from (long-term|borrowings|debt)",
    "div": r"dividends paid|^cash dividends|^dividends$|^payment of dividends",
}


def _match(lab, key):
    return re.search(SYN[key], lab) is not None


def _block(lines, start, stop_pat, max_len=140):
    blk = []
    for k in range(start, min(len(lines), start + max_len)):
        blk.append(k)
        if stop_pat and re.search(stop_pat, norm(split_row(lines[k])[0])) and split_row(lines[k])[1]:
            break
    return blk


def _cols(lines, i, fy):
    """Indices of the Y0 and Y-1 columns for the statement whose anchor is line i."""
    yrs = year_header(lines, i)
    if yrs:
        try:
            a = yrs.index(fy)
        except ValueError:
            a = None
        if a is not None:
            b = yrs.index(fy - 1) if (fy - 1) in yrs else (a + 1 if a + 1 < len(yrs) else a - 1)
            return a, b, yrs
    return 0, 1, yrs


def _take(nums, a, b, n_expected):
    """Pick Y0/Y-1 values; extra leading numbers (e.g. note references) are trimmed from the left."""
    if n_expected and len(nums) > n_expected:
        nums = nums[len(nums) - n_expected:]
    v0 = nums[a] if a is not None and 0 <= a < len(nums) else None
    v1 = nums[b] if b is not None and 0 <= b < len(nums) else None
    return v0, v1


def find_statement(lines, anchor, confirm, fy, window=90):
    """Candidate anchor lines whose statement also contains `confirm` within `window` lines."""
    cands = []
    for i, ln in enumerate(lines):
        lab, nums = split_row(ln)
        if len(nums) >= 2 and re.search(anchor, norm(lab)):
            seg = lines[max(0, i - window):i + window]
            if any(re.search(confirm, norm(split_row(s)[0])) and len(split_row(s)[1]) >= 2 for s in seg):
                cands.append(i)
    return cands


def extract(raw, fy):
    """Return {item: {'y0':..., 'y1':..., 'line':..., 'scale':...}} in millions where possible."""
    lines = doc_lines(raw)
    res = {}

    def grab(region, keys, a, b, n_exp, scale, stmt, first=True):
        for k in region:
            lab, nums = split_row(lines[k])
            if len(nums) < 2:
                continue
            nl = norm(lab)
            for key in keys:
                if key in res and first:
                    continue
                if _match(nl, key):
                    # receivables: only the first trade-receivable line, not "notes receivable from officers"
                    if key == "ar" and re.search(r"officer|employee|affiliat|related|income tax|deferred|"
                                                 r"long-term|noncurrent|non-current|from sale", nl):
                        continue
                    v0, v1 = _take(nums, a, b, n_exp)
                    if v0 is None:
                        continue
                    sc = scale or 1.0
                    if key in ("eps_d",):
                        sc = 1.0
                    res[key] = {"y0": v0 * sc, "y1": (v1 * sc if v1 is not None else None),
                                "line": lines[k][:160], "stmt": stmt, "scale": scale}
                    break

    # Balance sheet: "total assets" confirmed by "total liabilities and ..." nearby; prefer the last such
    # candidate before the cash-flow statement (selected financial data tables usually come first).
    bs = find_statement(lines, SYN["ta"], SYN["tle"], fy)
    if bs:
        i = bs[0] if len(bs) == 1 else max(bs, key=lambda c: sum(
            1 for s in lines[max(0, c - 70):c] if re.search(SYN["tca"] + "|" + SYN["cash"], norm(split_row(s)[0]))))
        a, b, yrs = _cols(lines, i, fy)
        n_exp = len(yrs) if yrs else 2
        scale = unit_near(lines, i, 160)
        start = max(0, i - 70)
        top = start
        for k in range(i - 1, start, -1):
            if re.search(r"^assets$|^current assets", norm(lines[k])):
                top = k
                break
        end = min(len(lines), i + 90)
        grab(range(top, i + 1), ["cash", "ar", "inv", "tca", "ppe", "ta"], a, b, n_exp, scale, "BS")
        grab(range(i + 1, end), ["tcl", "ltd", "tl", "eq", "tle", "re"], a, b, n_exp, scale, "BS")
        res["_bs"] = {"line_no": i, "years": yrs, "scale": scale}

    # Cash flow statement
    cf = find_statement(lines, SYN["cfo"], SYN["cfi"], fy, window=80)
    if cf:
        i = cf[-1] if len(cf) > 1 and not any(re.search(SYN["cfi"], norm(split_row(s)[0]))
                                             for s in lines[cf[0]:cf[0] + 80]) else cf[0]
        a, b, yrs = _cols(lines, i, fy)
        n_exp = len(yrs) if yrs else None
        scale = unit_near(lines, i, 160)
        top = i
        for k in range(i - 1, max(0, i - 70), -1):
            if re.search(r"operating activities", norm(lines[k])) and not split_row(lines[k])[1]:
                top = k
                break
        ni_cf = {}
        for k in range(top, i):
            lab, nums = split_row(lines[k])
            if len(nums) >= 2 and _match(norm(lab), "ni") and not ni_cf:
                v0, v1 = _take(nums, a, b, n_exp)
                ni_cf = {"y0": v0 * (scale or 1), "y1": v1 * (scale or 1) if v1 is not None else None,
                         "line": lines[k][:160], "stmt": "CF", "scale": scale}
        if ni_cf:
            res["ni_cf"] = ni_cf
        sub = {}
        for k in range(top, min(len(lines), i + 90)):
            lab, nums = split_row(lines[k])
            if len(nums) < 2:
                continue
            nl = norm(lab)
            for key, pat in (("dep_cf", SYN["dep"]), ("ch_ar", r"receivable"), ("ch_inv", r"inventor"),
                             ("cfo", SYN["cfo"]), ("cfi", SYN["cfi"]), ("cff", SYN["cff"]), ("fx", SYN["fx"]),
                             ("dcash", SYN["dcash"]), ("cash_beg", SYN["cash_beg"]), ("cash_end", SYN["cash_end"]),
                             ("issue", SYN["issue"]), ("div", SYN["div"])):
                if key in sub:
                    continue
                if key in ("ch_ar", "ch_inv") and k > i:
                    continue
                if re.search(pat, nl):
                    v0, v1 = _take(nums, a, b, n_exp)
                    if v0 is None:
                        continue
                    sub[key] = {"y0": v0 * (scale or 1), "y1": v1 * (scale or 1) if v1 is not None else None,
                                "line": lines[k][:160], "stmt": "CF", "scale": scale}
                    break
        res.update(sub)
        res["_cf"] = {"line_no": i, "years": yrs, "scale": scale}

    # Income statement: net income line confirmed by a revenue line within 60 lines above it
    is_c = []
    for i, ln in enumerate(lines):
        lab, nums = split_row(ln)
        if len(nums) >= 2 and _match(norm(lab), "ni"):
            above = lines[max(0, i - 60):i]
            if any(_match(norm(split_row(s)[0]), "rev") and len(split_row(s)[1]) >= 2 for s in above) and \
                    not any(re.search(r"operating activities", s.lower()) for s in above[-25:]):
                is_c.append(i)
    if is_c:
        # The statement proper is usually the candidate with the most expense lines above it.
        def score(c):
            seg = [norm(split_row(s)[0]) for s in lines[max(0, c - 60):c]]
            return sum(bool(re.search(SYN["cogs"] + "|" + SYN["sga"] + r"|income tax|interest expense", s)) for s in seg)
        i = max(is_c, key=score)
        a, b, yrs = _cols(lines, i, fy)
        n_exp = len(yrs) if yrs else None
        scale = unit_near(lines, i, 160)
        top = max(0, i - 60)
        for k in range(i - 1, top, -1):
            if _match(norm(split_row(lines[k])[0]), "rev") and len(split_row(lines[k])[1]) >= 2:
                top = k
        grab(range(top, i + 1), ["rev", "cogs", "gp", "sga", "dep"], a, b, n_exp, scale, "IS")
        lab, nums = split_row(lines[i])
        v0, v1 = _take(nums, a, b, n_exp)
        res["ni"] = {"y0": v0 * (scale or 1), "y1": v1 * (scale or 1) if v1 is not None else None,
                     "line": lines[i][:160], "stmt": "IS", "scale": scale}
        grab(range(i + 1, min(len(lines), i + 30)), ["eps_d", "sh_d"], a, b, n_exp, 1.0, "IS")
        if "sh_d" in res and scale:
            res["sh_d"]["note"] = "shares as printed"
        res["_is"] = {"line_no": i, "years": yrs, "scale": scale}
    return res, lines

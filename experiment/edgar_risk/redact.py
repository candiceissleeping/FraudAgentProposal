"""Stronger redaction for blind packets.

Beyond the company's own aliases this removes anything that tends to identify a
filer: proper nouns (people, subsidiaries, brands, places), unknown acronyms
and absolute years.

A capitalised word counts as a common word, and is kept, when its lowercase
form appears in the filing's own text (e.g. "Revenue" vs "revenue"). Proper
nouns rarely appear in lowercase, so they are replaced by [NAME]. Years
become relative to the fiscal year: 2001 -> Y0, 2000 -> Y-1.
"""
import collections
import re

# Capitalised words / acronyms that are generic in 10-K language
KEEP = {
    "Item", "Items", "Part", "Note", "Notes", "Exhibit", "Schedule", "Form", "Rule", "Rules", "Section", "Act",
    "Company", "Company's", "Registrant", "Corporation", "Inc", "Inc.", "Corp", "Corp.", "Co", "Co.", "LLC", "L.P.", "LP",
    "Ltd", "Ltd.", "plc", "N.V.", "B.V.", "S.A.", "AG", "GmbH",
    "Board", "Directors", "Committee", "Audit", "Chief", "Executive", "Financial", "Officer", "Officers", "President",
    "Chairman", "Vice", "Senior", "Treasurer", "Secretary", "Controller", "Mr.", "Ms.", "Mrs.", "Dr.",
    "Securities", "Exchange", "Commission", "Department", "Justice", "United", "States", "U.S.", "US", "USA",
    "Federal", "State", "Court", "District", "Attorney", "Office", "Internal", "Revenue", "Service", "Congress",
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November",
    "December", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "I", "II", "III", "IV", "V", "VI", "VII",
    "SEC", "GAAP", "FASB", "EITF", "SFAS", "SAB", "ASC", "ASU", "APB", "FIN", "IFRS", "PCAOB", "AICPA", "IRS", "FDA",
    "DOJ", "FTC", "FCC", "EPA", "OSHA", "ERISA", "CEO", "CFO", "COO", "CAO", "EBITDA", "EBIT", "EPS", "LIBOR", "SOFR",
    "NYSE", "NASDAQ", "IPO", "R&D", "IT", "VIE", "VIEs", "SPE", "SPEs", "QSPE", "IRU", "IRUs", "ABL", "OTC", "LIFO",
    "FIFO", "M&A", "CEOs", "UK", "U.K.", "EU", "Euro", "China", "Canada", "Europe", "Asia", "Japan", "Mexico",
    "Medicare", "Medicaid", "Level", "Q1", "Q2", "Q3", "Q4", "N/A", "NA", "Inc.'s", "ITEM", "PART", "NOTE",
}
TOKEN = re.compile(r"(?<![\w\[])([A-Z][A-Za-z0-9&'.\-]*[A-Za-z0-9]|[A-Z])(?![\w\]])")
YEAR = re.compile(r"(?<![\d$.,])(19[6-9]\d|20[0-3]\d)(?!\d|,\d{3}|%)")


def _common_words(text):
    """Lowercase words that occur (in lowercase) in this filing."""
    return collections.Counter(re.findall(r"\b[a-z][a-z'\-]+\b", text))


def make_redactor(aliases, fiscal_year, reference_text):
    """Return a function that redacts packet text for one filing."""
    lower = _common_words(reference_text)
    alias_rx = [re.compile(rf"(?<![A-Za-z]){re.escape(a)}(?![a-z])") for a in sorted(set(aliases), key=len, reverse=True)]

    def is_common(tok):
        core = tok.rstrip(".").removesuffix("'s").removesuffix("’s")
        if tok in KEEP or core in KEEP:
            return True
        if core.isupper() and len(core) > 1:            # acronym not on the keep list
            return core.capitalize() in KEEP or lower.get(core.lower(), 0) >= 3 and len(core) > 3
        parts = re.split(r"[-']", core)
        return all(lower.get(p.lower(), 0) >= 2 for p in parts if p)

    def year_sub(m):
        d = int(m.group(1)) - fiscal_year
        return "Y0" if d == 0 else f"Y{d:+d}"

    def redact(text):
        for rx in alias_rx:
            text = rx.sub("[COMPANY]", text)
        out, last = [], 0
        for m in TOKEN.finditer(text):
            tok = m.group(1)
            if is_common(tok):
                continue
            out.append(text[last:m.start()])
            out.append("[NAME]")
            last = m.end()
        out.append(text[last:])
        text = "".join(out)
        text = re.sub(r"\[NAME\](?:[\s,.&'-]*(?:of |and |de |du )?\[NAME\])+", "[NAME]", text)
        return YEAR.sub(year_sub, text)  # last, so "Y0" is not mistaken for a proper noun

    return redact

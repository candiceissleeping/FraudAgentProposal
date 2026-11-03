# Round 9b memory-only baseline (AAER probe)

Read ONLY the file you were given; do not open any other file or directory in this repository.
It lists 6 company annual reports (company name and fiscal year end). You are NOT given the reports.

For each one, using only what you already know:
1. Rate the risk that the company's financial statements for that fiscal year are materially misstated, through
   fraud or serious accounting errors (0 = no concern, 100 = almost certainly misstated).
2. knows_accounting_problems: do you know of later accounting problems, restatements or non-reliance announcements
   involving that fiscal year?
3. knows_sec_enforcement: do you know of an SEC enforcement action (Accounting and Auditing Enforcement Release,
   cease-and-desist order, settled or litigated SEC complaint) against the company or its officers concerning the
   financial reporting for that fiscal year?
Answer true only if you actually know it; do not guess.

Write this JSON list to the output path with the Write tool, then reply "done":
[{"company": "<as listed>", "risk_score": <int>, "knows_accounting_problems": <true|false>,
  "knows_sec_enforcement": <true|false>, "basis": "short reason, including what you know"}, ...]

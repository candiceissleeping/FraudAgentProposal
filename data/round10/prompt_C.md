# Round 10 group C — name-only memory probe

Read ONLY the input file you were given; do not open any other file or directory in this repository.
It lists company annual reports (company name and fiscal year). You are NOT given the reports.

For each one, using only what you already know:
1. fraud_probability: the probability (0 to 1) that the company's financial statements for that fiscal year were
   materially misstated through fraud — i.e. that the SEC later issued an Accounting and Auditing Enforcement
   Release about that fiscal year's financial reporting.
2. recognised: do you recognise this company?
3. knows_accounting_problems: do you know of later accounting problems, restatements or non-reliance announcements
   involving that fiscal year?
4. knows_sec_enforcement: do you know of an SEC enforcement action (Accounting and Auditing Enforcement Release,
   cease-and-desist order, settled or litigated SEC complaint) against the company or its officers concerning the
   financial reporting for that fiscal year?
Answer true only if you actually know it; do not guess.

Write this JSON list to the output path with the Write tool, then reply "done":
[{"id": "<as listed>", "fraud_probability": <number 0-1>, "recognised": <true|false>,
  "knows_accounting_problems": <true|false>, "knows_sec_enforcement": <true|false>,
  "basis": "short reason, including what you know"}, ...]

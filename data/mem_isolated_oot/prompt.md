# Memory-only baseline (isolated rerun of round 8 MEM)

Below are 54 company annual reports (company name and fiscal year end). You are NOT given the reports.

For each one, using only what you already know, rate the risk that the company's financial statements for that
fiscal year are materially misstated, through fraud or serious accounting errors (0 = no concern, 100 = almost
certainly misstated). Also say whether you know of later accounting problems, restatements or SEC enforcement
involving that period.

Reply with only this JSON list, one entry per company, in the order given, and nothing else:
[{"id": <number as listed>, "company": "<as listed>", "risk_score": <int>, "knows_later_problems": <true|false>, "basis": "short reason"}, ...]


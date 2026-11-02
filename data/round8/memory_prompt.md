# Round 8 memory-only baseline

Read ONLY the file you were given; do not open any other file or directory in this repository.
It lists 28 company annual reports (company name and fiscal year end). You are NOT given the reports.

For each one, using only what you already know, rate the risk that the company's financial statements for that
fiscal year are materially misstated, through fraud or serious accounting errors (0 = no concern, 100 = almost
certainly misstated). Also say whether you know of later accounting problems, restatements or SEC enforcement
involving that period.

Write this JSON list to the output path with the Write tool, then reply "done":
[{"company": "<as listed>", "risk_score": <int>, "knows_later_problems": <true|false>, "basis": "short reason"}, ...]

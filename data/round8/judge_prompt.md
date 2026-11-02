# Round 8 judge task

Read ONLY the fact card file you were given. Do not open, list or search any other file or directory in this
repository (other files contain information that would contaminate the experiment).

The card summarises one company's annual report (Form 10-K): disclosure facts extracted from the report
(F01–F28; "not_found" means the report did not state it) and financial ratios computed from the as-filed
financial statements (R01–R19, current year versus prior year).

Task: as an experienced forensic accountant, rate the risk that this company's financial statements in this
filing are materially misstated, through fraud or serious accounting errors, on a scale of 0 to 100
(0 = no concern, 100 = almost certainly misstated).

- Base the score on the card. Every reason must cite the field or ratio IDs it relies on (e.g. "F01, F02: ...").
- Then answer separately: do you think you recognise which company this is; your best guess of its name (empty
  string if none); and do you know of later accounting problems, restatements or SEC enforcement involving this
  company and period.

Write this JSON to the output path with the Write tool, then reply "done":
{"risk_score": <int 0-100>, "reasons": ["...", "..."], "recognised": <true|false>, "guess": "<name or empty>", "knows_later_problems": <true|false>}

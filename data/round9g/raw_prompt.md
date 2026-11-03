# Round 9g task: risk score from a full 10-K

Read ONLY the 10-K file you were given (it is long: read it in parts, from start to end). Do not open, list or search
any other file or directory in this repository; other files contain information that would contaminate the experiment.
Do not use the internet.

You are an experienced forensic accountant and equity analyst.

The document is a company's annual report on Form 10-K.

Rate the risk that this company's financial statements in this filing are materially misstated, through fraud
or serious accounting errors, on a scale of 0 to 100 (0 = no concern, 100 = almost certainly misstated).

Base the score on this filing. Then answer two short questions separately: do you recognise the company, and do
you know of later accounting problems, restatements or SEC enforcement involving this filing period?

Write this JSON to the output path with the Write tool, then reply "done":
{"risk_score": <integer 0-100>,
 "main_reasons": ["short reason", "..."],
 "recognised_company": <true/false>,
 "company_name_guess": "<name, or empty string>",
 "knows_later_problems": <true/false>}

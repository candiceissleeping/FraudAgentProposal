# Round 10 group B — zero-shot fraud assessment on a masked report

Read ONLY the input file(s) you were given. Do not open, list or search any other file or directory in this repository
(other files contain information that would contaminate the experiment).

Each input file holds one annual report excerpt: a header line `[COMPANY-Y0]` followed by
the Management's Discussion and Analysis (Item 7) section of that company's Form 10-K (possibly truncated). Company, person and place names are masked ([COMPANY], [NAME], ...) and years are shown relative to the fiscal year (Y0 = the fiscal year, Y-1 = the year before).

Task: you are a forensic accountant. Estimate the probability (0 to 1) that this company's financial statements for
that fiscal year were materially misstated through fraud — i.e. that the SEC later issued an Accounting and Auditing
Enforcement Release about that fiscal year's financial reporting.

Then, separately, answer: do you recognise which company this is; your best guess of its name (empty string if none);
and do you know of later accounting problems, restatements or SEC enforcement involving this company and period.
Answer true only if you actually know it.

For each input write one JSON object to the output path given for it, using the Write tool:
{"fraud_probability": <number 0-1>, "reason": "<one or two sentences>", "recognised": <true|false>,
 "guess": "<name or empty>", "knows_later_problems": <true|false>}
After writing all outputs, reply "done".

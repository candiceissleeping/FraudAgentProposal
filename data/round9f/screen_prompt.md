# Round 9f AAER screening task

Read ONLY the batch file you were given (and this prompt). It contains the first pages of several SEC Accounting and
Auditing Enforcement Releases (AAERs), each starting with a line "===== AAER-xxxx | released ... | respondent(s): ... =====".

For EACH AAER in the file, decide from the text only:
- issuer: the public company whose financial statements are at issue (exact legal name as written), or "" if none
- us_10k_filer: true if that issuer files annual reports on Form 10-K (US domestic registrant); false if it is a
  foreign private issuer (Form 20-F), a private company, a fund, or unclear
- fs_misstatement: true only if the issuer's own annual financial statements were materially misstated / not in
  conformity with GAAP (e.g. improper revenue recognition, overstated assets, understated expenses, restatement).
  false if the case is only about bribery/FCPA, disclosures outside the financial statements, non-GAAP measures,
  internal controls alone, insider trading, auditor independence, or quarterly results only
- misstated_fiscal_years: list of the issuer's FISCAL YEARS whose annual statements were misstated (integers), as
  stated or clearly implied by the text; [] if not determinable
- reason: one short sentence

Write a JSON object to the output path with the Write tool, then reply "done":
{"AAER-xxxx": {"issuer": "...", "us_10k_filer": true, "fs_misstatement": true, "misstated_fiscal_years": [2016, 2017], "reason": "..."}, ...}
Include every AAER in the batch.

# Round 8 fact extraction task

You are extracting facts from ONE annual report (Form 10-K) whose names have been masked.

## Rules
1. Read ONLY the file you were given. Do not open, list or search any other file or directory in this repository
   (other files contain information that would contaminate the experiment).
2. Answer only from what this document says. Do not use anything you know or believe about any company.
   If you think you recognise the company, ignore that and never write a company, person or product name.
3. For every field give a value and a supporting quote. The quote must be copied EXACTLY, character for character,
   from the file (contiguous text, at most 40 words). You may join two exact fragments with " ... ".
   Masked tokens such as [NAME], [COMPANY], Y0, Y-1 are part of the text; copy them as they appear.
4. If the document does not state the fact, use "not_found" (or "not_disclosed" for numbers) with an empty quote.
   A "no" answer also needs a quote when the document states it explicitly (e.g. "controls were effective");
   if "no" is only inferred from silence, use "no" with an empty quote. Values with an empty quote are treated as not_found
   unless the value is "no".
5. The file is long. Use Grep on the file for keywords (material weakness, going concern, restate, revision,
   subpoena, investigation, class action, related part, customer, concentration, critical audit matter,
   percentage-of-completion, over time, contract assets, unbilled, distributor, return, bill-and-hold,
   covenant, waiver, Chief Financial Officer, interim, resign, appointed, acquisition, merger, non-GAAP,
   write-down, obsolete, segment, change in accounting, change in estimate, incentive, bonus), then Read the
   surrounding lines to confirm before answering.

## Fields
- F01 `material_weakness` — Management or auditor reports a material weakness in ICFR at year end. Value: one of: yes, no.
- F02 `material_weakness_area` — Area of the material weakness. Value: one of: revenue, inventory_or_costing, financial_close_or_reporting, it_general_controls, tax, staffing_or_segregation_of_duties, other, na.
- F03 `icfr_auditor_opinion` — Auditor's opinion on internal control over financial reporting. Value: one of: adverse, unqualified, not_required, not_found.
- F04 `going_concern` — Substantial doubt about ability to continue as a going concern. Value: one of: yes, no.
- F05 `auditor_change_within_2y` — Change of independent auditor in the last two years. Value: one of: yes, no.
- F06 `disagreement_with_accountants` — Reported disagreements or reportable events with accountants. Value: one of: yes, no.
- F07 `prior_period_correction` — Correction of previously issued financial statements. Value: one of: none, immaterial_revision, restatement.
- F08 `revenue_over_time_major` — A significant share of revenue is recognised over time / percentage of completion. Value: one of: yes, no.
- F09 `contract_assets_or_unbilled_significant` — Contract assets or unbilled receivables are significant. Value: one of: yes, no.
- F10 `channel_return_rights_or_bill_and_hold` — Sales through distributors with return/price-protection rights, consignment or bill-and-hold. Value: one of: yes, no.
- F11 `related_party_transactions_material` — Material transactions with related parties (officers, directors, affiliates). Value: one of: yes, no.
- F12 `largest_customer_pct_revenue` — Largest customer's share of revenue in percent (number) or not_disclosed. Value: a number (percent) or "not_disclosed".
- F13 `largest_customer_pct_receivables` — Largest customer's share of receivables in percent (number) or not_disclosed. Value: a number (percent) or "not_disclosed".
- F14 `ceo_or_cfo_change_in_year` — CEO or CFO changed during the year or since year end. Value: one of: yes, no.
- F15 `interim_or_acting_cfo` — An interim or acting CFO is in place. Value: one of: yes, no.
- F16 `sec_inquiry_or_investigation` — SEC inquiry, investigation, subpoena or Wells notice disclosed. Value: one of: yes, no.
- F17 `securities_class_action` — Securities class action or shareholder derivative suit pending. Value: one of: yes, no.
- F18 `other_government_investigation` — DOJ or other government investigation disclosed. Value: one of: yes, no.
- F19 `covenant_breach_waiver_or_amendment` — Debt covenant breach, waiver or amendment to avoid breach. Value: one of: yes, no.
- F20 `incentive_pay_tied_to_revenue_or_eps` — Executive incentive pay explicitly tied to revenue, EPS or earnings targets. Value: one of: yes, no.
- F21 `capital_raise_in_year_or_planned` — Equity or debt raised during the year or stated plans to raise. Value: one of: yes, no.
- F22 `major_acquisition_in_year` — A major acquisition during the year. Value: one of: yes, no.
- F23 `public_via_spac_or_reverse_merger_3y` — Became public via SPAC merger or reverse merger in the last three years. Value: one of: yes, no.
- F24 `critical_audit_matter_topics` — Topics of critical audit matters (list). Value: a LIST chosen from: revenue, inventory, goodwill_or_intangibles, business_combination, tax, reserves_or_estimates, other, none_or_na.
- F25 `voluntary_accounting_change` — Voluntary change in accounting policy or significant change in estimate (not a newly mandated standard). Value: one of: yes, no.
- F26 `non_gaap_emphasis` — Non-GAAP measures emphasised in MD&A. Value: one of: yes, no.
- F27 `inventory_writedown_significant` — Significant inventory write-down or obsolescence charge. Value: one of: yes, no.
- F28 `segment_or_reporting_change` — Change in reportable segments or presentation in the year. Value: one of: yes, no.

## Output
Write a JSON object to the output path you were given, using the Write tool, in this exact shape:
{"F01": {"value": "yes", "quote": "..."}, "F02": {"value": "na", "quote": ""}, ..., "F28": {"value": "no", "quote": "..."}}
F24's value is a JSON list. F12/F13 values are numbers (e.g. 23) or "not_disclosed".
All 28 keys must be present. After writing the file, reply with just "done" and the number of fields with non-empty quotes.

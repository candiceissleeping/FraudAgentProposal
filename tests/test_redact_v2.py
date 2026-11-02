"""Round-8 L2 redaction: identity removed, content (ratios, sums, years-relative) preserved."""
import unittest

from experiment.edgar_risk.redact_v2 import L2Redactor, leak_audit

# Words a real 10-K always contains in lower case (the proper-noun rule keeps a capitalised word that does).
REF = ("the company recorded revenue and the committee reviewed receivables, inventory and cash. "
       "and to of the revenue was recognised, or not, pursuant to the act. total sales in the year for "
       "gross margin and weighted average shares were paid. ") * 5
IDENT = {"names": ["ACME WIDGETS CORP", "Acme Widgets"], "tickers": ["ACMW"], "people": ["John Q. Doe"],
         "addresses": ["123 Main Street", "Springfield"], "numbers": ["12-3456789", "555-123-4567"]}


class L2Test(unittest.TestCase):
    def setUp(self):
        self.r = L2Redactor(IDENT, 2022, 2.0, REF)

    def test_identity_removed(self):
        out = self.r.l2("Acme Widgets Corp (NASDAQ: ACMW), acmw-20221231.htm, 123 Main Street, Springfield. "
                        "/s/ John Q. Doe signed; Mr. Doe is CEO. Ernst & Young LLP audited. EIN 12-3456789.")
        for leak in ("Acme", "ACMW", "acmw", "Doe", "Main Street", "Springfield", "Ernst", "3456789"):
            self.assertNotIn(leak, out)
        self.assertIn("[COMPANY]", out)
        self.assertIn("[AUDITOR]", out)
        self.assertEqual(leak_audit(out, IDENT), {})

    def test_form_names_and_heading_words_kept(self):
        out = self.r.l2("ANNUAL REPORT PURSUANT TO SECTION 13 OR 15(d) OF THE ACT on Form 10-K and 10-Q.")
        self.assertIn("PURSUANT TO SECTION 13 OR", out)
        self.assertIn("Form 10-K and 10-Q", out)

    def test_same_entity_same_number(self):
        out = self.r.l2("Sales to Globex Industries rose. Globex Industries paid late.")
        self.assertEqual(out.count("[NAME_1]"), 2)

    def test_years_relative(self):
        out = self.r.l2("For the fiscal year ended December 31, 2022 compared with 2021 and FY23; ASU 2016-02 applies.")
        self.assertIn("December 31, Y0", out)
        self.assertIn("Y-1", out)
        self.assertIn("Y+1", out)
        self.assertIn("ASU [no.]", out)

    def test_money_scaled_sums_preserved(self):
        table = "(In millions)\nCash  $100  $50\nReceivables  200  25\nTotal assets  $300  $75"
        out = self.r.l2(table).split("\n")
        self.assertEqual(out[1], "Cash  $200  $100")
        self.assertEqual(out[2], "Receivables  400  50")
        self.assertEqual(out[3], "Total assets  $600  $150")

    def test_non_money_untouched(self):
        out = self.r.l2("(In millions)\nRevenue  $100  $90\nGross margin %  40.1%  38.2%\nWeighted average shares  1,000  990")
        self.assertIn("40.1%", out)
        self.assertIn("Weighted average shares  1,000  990", out)
        self.assertIn("Revenue  $200  $180", out)

    def test_prose_money_scaled_counts_rounded(self):
        out = self.r.l2("Revenue grew to $1.5 billion; we have approximately 1,234 employees and 12% margin.")
        self.assertIn("$3.0 billion", out)
        self.assertIn("1,200 employees", out)
        self.assertIn("12%", out)


if __name__ == "__main__":
    unittest.main()

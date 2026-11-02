"""Round-8 L2 redaction: identity removed, content (ratios, sums, years-relative) preserved."""
import unittest

from experiment.edgar_risk.redact_v2 import L2Redactor, leak_audit

# Words a real 10-K always contains in lower case (the proper-noun rule keeps a capitalised word that does).
REF = ("the company recorded revenue and the committee reviewed receivables, inventory and cash. "
       "and to of the revenue was recognised, or not, pursuant to the act. total sales in the year for "
       "gross margin and weighted average shares were paid. net earnings per basic and diluted share. ") * 5
IDENT = {"names": ["ACME WIDGETS CORP", "Acme Widgets"], "tickers": ["ACMW"], "people": ["John Q. Doe"],
         "addresses": ["123 Main Street", "Springfield"], "numbers": ["12-3456789", "555-123-4567"]}


class L2Test(unittest.TestCase):
    def setUp(self):
        self.r = L2Redactor(IDENT, 2022, 2.0, REF)

    def test_identity_removed(self):
        out = self.r.l2("Acme Widgets Corp (NASDAQ: ACMW), acmw20221231_10k.htm, the 1ACMW program, 123 Main Street, "
                        "Springfield. AW is our short name; AW grew; AW paid. Call 555-1234. Founded in 1898. "
                        "/s/ John Q. Doe signed; Mr. Doe is CEO. Ernst & Young LLP audited. EIN 12-3456789.")
        for leak in ("Acme", "ACMW", "acmw", "Doe", "Main Street", "Springfield", "Ernst", "3456789", "AW ",
                     "555-1234", "1898"):
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
        self.assertIn("December Y0", out)   # rule v3: day of month removed
        self.assertIn("Y-1", out)
        self.assertIn("Y+1", out)
        self.assertIn("ASU [no.]", out)

    def test_money_scaled_sums_preserved(self):
        table = "(In millions)\nCash  $100  $50\nReceivables  200  25\nTotal assets  $300  $75"
        out = self.r.l2(table).split("\n")
        self.assertEqual(out[1], "Cash  $200  $100")
        self.assertEqual(out[2], "Receivables  400  50")
        self.assertEqual(out[3], "Total assets  $600  $150")

    def test_counts_scaled_per_share_and_percent_kept(self):
        # every quantity x k (so net income / shares = EPS still holds); per-share, % and rates untouched
        out = self.r.l2("(In millions)\nRevenue  $100  $90\nGross margin %  40.1%  38.2%\n"
                        "Weighted average shares  1,000  990\nNet earnings per share  $2.92  $3.63\n"
                        "Earnings per share:\nBasic and diluted  1.25  0.90\nWeighted average shares:\n"
                        "Basic and diluted  7,081  7,060")
        self.assertIn("40.1%", out)
        self.assertIn("Weighted average shares  2,000  1,980", out)
        self.assertIn("Net earnings per share  $2.92  $3.63", out)
        self.assertIn("Basic and diluted  1.25  0.90", out)
        self.assertIn("Basic and diluted  14,162  14,120", out)
        self.assertIn("Revenue  $200  $180", out)

    def test_same_number_same_treatment(self):
        # regressions from the L2 pilot: 'year', 'par value', 'price' and coupon '%' in a label must not stop scaling
        out = self.r.l2("(In thousands)\nCash and cash equivalents  $1,500  $1,200\n"
                        "Cash and cash equivalents at end of year  $1,500  $1,200\n"
                        "Capital in excess of par value  1,600  1,500\nTotal purchase price  $1,700\n"
                        "3.125% Notes due Y+1  1,004  990")
        self.assertIn("at end of year  $3,000  $2,400", out)
        self.assertIn("par value  3,200  3,000", out)
        self.assertIn("Total purchase price  $3,400", out)
        self.assertIn("% Notes due Y+1  2,008  1,980", out)
        self.assertEqual(self.r.inconsistent_numbers(), [])

    def test_prose_money_and_counts_scaled(self):
        out = self.r.l2("Revenue grew to $1.5 billion; we have approximately 1,234 employees and 12% margin; "
                        "a dividend of $0.25 per share.")
        self.assertIn("$0.25 per share", out)
        self.assertIn("$3.0 billion", out)
        self.assertIn("2,468 employees", out)
        self.assertIn("12%", out)


if __name__ == "__main__":
    unittest.main()


class TwoFactorTest(unittest.TestCase):
    """Rule v3: money x k, share counts x j, per-share x k/j -- identities hold, EPS no longer matches the filing."""
    def setUp(self):
        self.r = L2Redactor(IDENT, 2022, 2.0, REF, j=0.5)

    def test_eps_identity_preserved(self):
        out = self.r.l2("(In thousands, except per share data)\nNet earnings  $20,000  $10,000\n"
                        "Weighted average shares outstanding  10,123,456  10,000,000\n"
                        "Net earnings per share  $2.00  $1.00\n"
                        "Balance  10,123,456  $10,000  $500,000\n"
                        "We had 10,123,456 shares outstanding and paid a dividend of $0.50 per share.")
        self.assertIn("Net earnings  $40,000  $20,000", out)                      # x k
        self.assertIn("outstanding  5,061,728  5,000,000", out)                   # x j
        self.assertIn("per share  $8.00  $4.00", out)                             # x k/j: 40,000k / 5,000,000
        self.assertIn("  5,061,728  $20,000  $1,000,000", out)   # share column in a mixed row, found by value
        self.assertIn("5,061,728 shares", out)
        self.assertIn("$2.00 per share", out)
        self.assertEqual(self.r.inconsistent_numbers(), [])

    def test_l3b_artifacts_fixed(self):
        # the three fake inconsistencies scoring agents found in L3b
        out = self.r.l2("Earnings per common share—diluted\nNet earnings  $10.51  $13.64\n"
                        "the earnings per share for the year was revised from $\n7.85\nand $\n7.39\n"
                        "Common stock, $0.001 par value, 22,261,619 shares issued and outstanding  7,346  1,742\n"
                        "Balance  22,261,619  $7,346")
        self.assertIn("Net earnings  $42.04  $54.56", out)   # per share: x k/j = 4
        self.assertIn("\n31.40\n", out)                       # standalone EPS in prose: x 4
        self.assertIn("11,130,810 shares issued", out)         # numbers inside a row label: shares x j
        self.assertIn("]  11,130,810  $14,692", out)
        self.assertEqual(self.r.inconsistent_numbers(), [])

    def test_company_tail_and_dates(self):
        r = L2Redactor({"names": ["BECTON DICKINSON & CO"]}, 2019, 2.0,
                       "Becton, Dickinson and Company sells. the closing occurred.")
        out = r.l2("Becton, Dickinson and Company closed the deal on December 29, 2017.")
        self.assertNotIn("and Company", out)
        self.assertIn("December Y-2", out)


class L3Test(unittest.TestCase):
    def test_sections_kept_and_dropped(self):
        from experiment.edgar_risk.redact_v2 import l3_select, mark_sections
        doc = "\n".join(["Cover page", "ITEM 1. BUSINESS", "We are the leading widget maker.",
                         "ITEM 1A. RISK FACTORS", "Risks here.", "ITEM 2. PROPERTIES", "Plant in town.",
                         "ITEM 7. MANAGEMENT'S DISCUSSION AND ANALYSIS", "Sales rose.",
                         "ITEM 8. FINANCIAL STATEMENTS", "See Item 15.", "ITEM 10. DIRECTORS", "Bios.",
                         "ITEM 15. EXHIBITS", "Exhibit list", "Report of Independent Registered Public Accounting Firm",
                         "Opinion.", "Balance sheet  $1  $2"])
        body, kept = l3_select(mark_sections(doc))
        for gone in ("Cover page", "widget maker", "Plant in town", "Bios", "Exhibit list"):
            self.assertNotIn(gone, body)
        for there in ("Risks here", "Sales rose", "Opinion.", "Balance sheet"):
            self.assertIn(there, body)
        self.assertEqual(kept[-1], "FS-from-15/16")

    def test_segments_and_descriptive_sentences(self):
        from experiment.edgar_risk.redact_v2 import drop_descriptive, mask_segments, segment_names
        text = ("Sales in the Ag Services and Oilseeds segment rose. The Nutrition segment fell. "
                "Ag Services and Oilseeds segment margins and Nutrition segment margins were flat.")
        segs = segment_names(text)
        out = mask_segments(text, segs)
        self.assertNotIn("Oilseeds", out)
        self.assertNotIn("Nutrition", out)
        kept, dropped = drop_descriptive("We are a leading provider of widgets. Revenue rose 5%. Founded in Y-30.")
        self.assertEqual(kept, "Revenue rose 5%.")
        self.assertEqual(dropped, 2)

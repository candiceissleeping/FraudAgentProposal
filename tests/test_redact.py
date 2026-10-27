"""Round-3 redaction: proper nouns and years are masked, ordinary words survive."""
import unittest

from experiment.edgar_risk.redact import make_redactor
from experiment.edgar_risk.round3 import auc

REF = ("the company recorded revenue and related party transactions with the family. "
       "revenue recognition during the year, the committee, investigation, receivables, advances, partnership. ") * 3


class RedactTest(unittest.TestCase):
    def setUp(self):
        self.r = make_redactor(["Acme", "ACME"], 2001, REF)

    def test_aliases_people_and_acronyms_masked(self):
        out = self.r("Acme advanced $5 million to John J. Rigas and KPNQwest via ACME Holdings in Colorado.")
        for leak in ("Acme", "ACME", "Rigas", "KPNQwest", "Colorado", "John"):
            self.assertNotIn(leak, out)
        self.assertIn("$5 million", out)

    def test_years_relative_and_common_words_kept(self):
        out = self.r("RELATED PARTY TRANSACTIONS During 2001 and 2000, Revenue Recognition at December 31, 2001, under the SEC rules.")
        self.assertIn("RELATED PARTY TRANSACTIONS During Y0 and Y-1", out)
        self.assertIn("Revenue Recognition at December 31, Y0", out)
        self.assertIn("SEC", out)

    def test_amounts_not_treated_as_years(self):
        self.assertIn("$2,000", self.r("a fee of $2,000 in 2002"))
        self.assertIn("Y+1", self.r("a fee of $2,000 in 2002"))

    def test_auc(self):
        self.assertEqual(auc([3, 4], [1, 2]), 1.0)
        self.assertEqual(auc([1], [1]), 0.5)


if __name__ == "__main__":
    unittest.main()

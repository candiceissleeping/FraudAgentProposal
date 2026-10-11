"""Scanner/scorer behaviour on hand-written snippets (not real filings)."""
import unittest

from experiment.edgar_risk import score, signals


class ScoringTest(unittest.TestCase):
    def test_clean_filing_scores_low(self):
        filing = {
            "section_9A": "Management concluded that our disclosure controls and procedures were effective. "
                          "There were no material weaknesses identified.",
            "section_7": "Revenue grew 10% driven by cloud services.",
        }
        r = score.score_filing(filing)
        self.assertEqual(r["score"], 0)
        self.assertEqual(r["band"], "Low")

    def test_negated_mentions_ignored(self):
        filing = {"section_9A": "We did not identify any material weakness in internal control."}
        self.assertEqual(signals.extract(filing)["internal_control"]["hits"], 0)

    def test_red_flags_score_with_reasons(self):
        filing = {
            "section_7": "These conditions raise substantial doubt about our ability to continue as a going concern. "
                         "We restated our previously issued financial statements for 2001.",
            "section_9A": "Management identified a material weakness in revenue recognition controls.",
            "section_3": "The Company received a subpoena from the SEC in connection with a formal order of investigation.",
        }
        r = score.score_filing(filing)
        cats = {x["category"] for x in r["reasons"]}
        self.assertIn("Going-concern doubt", cats)
        self.assertIn("Internal-control weakness", cats)
        self.assertIn("Regulatory / criminal investigation", cats)
        self.assertGreaterEqual(r["score"], 25)
        self.assertTrue(all(x["quote"] for x in r["reasons"]))

    def test_saturation_caps_category(self):
        filing = {"section_8": " ".join(f"Item {i} was restated." for i in range(20))}
        r = score.score_filing(filing)
        self.assertEqual(r["breakdown"]["restatement"]["points"], signals.CATEGORIES["restatement"]["weight"])

    def test_exhibit_and_heading_boilerplate_ignored(self):
        filing = {
            "section_14": "*3.01 - Amended and Restated Articles of Incorporation of the Company. "
                          "(3)-1 Restated Certificate of Incorporation, filed as Exhibit (3)-1.",
            "section_9": "CHANGES IN AND DISAGREEMENTS WITH ACCOUNTANTS ON ACCOUNTING AND FINANCIAL DISCLOSURE None.",
        }
        ev = signals.extract(filing)
        self.assertEqual(ev["restatement"]["hits"], 0)
        self.assertEqual(ev["auditor_change"]["hits"], 0)

    def test_mechanical_restatements_and_audit_boilerplate_ignored(self):
        filing = {
            "section_8": "Prior period share amounts have been restated to reflect the split. "
                         "Results for fiscal 2005 were not restated. "
                         "Our audit included assessing the risk that a material weakness exists.",
        }
        ev = signals.extract(filing)
        self.assertEqual(ev["restatement"]["hits"], 0)
        self.assertEqual(ev["internal_control"]["hits"], 0)

    def test_real_restatement_still_detected(self):
        filing = {"section_7": "We have restated our previously reported consolidated financial statements for 2001."}
        self.assertEqual(signals.extract(filing)["restatement"]["hits"], 1)


if __name__ == "__main__":
    unittest.main()

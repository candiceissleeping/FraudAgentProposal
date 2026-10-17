"""Year-over-year diff on hand-written paragraphs (not real filings)."""
import unittest

from experiment.yoy import diff

SAME = "The Company recognizes revenue when products are shipped and title passes to the customer under standard terms."
EDITED_PRIOR = ("Allowances for doubtful accounts are estimated from historical collection experience "
                "and reviewed by management every quarter for adequacy.")
EDITED_NOW = ("Allowances for doubtful accounts are estimated from historical collection experience; "
              "beginning this year management no longer reviews them every quarter for adequacy.")
NEW = "In the fourth quarter we entered into bill and hold arrangements with two distributors at their request."
GONE = "Our independent auditors have not identified any material weakness in internal control over reporting."


class SectionDiffTest(unittest.TestCase):
    def test_classifies_paragraphs(self):
        d = diff.section_diff("\n".join([SAME, EDITED_PRIOR, GONE]), "\n".join([SAME, EDITED_NOW, NEW]))
        self.assertEqual(d["unchanged"], 1)
        self.assertEqual(d["added"], [NEW])
        self.assertEqual(d["removed"], [GONE])
        self.assertEqual([(m["prior"], m["current"]) for m in d["modified"]], [(EDITED_PRIOR, EDITED_NOW)])
        self.assertTrue(diff.MODIFIED <= d["modified"][0]["similarity"] < diff.UNCHANGED)

    def test_number_changes_are_not_narrative_changes(self):
        d = diff.section_diff("Net sales increased 12% to $4,210 million in the fiscal year, driven mainly by higher unit volume.",
                              "Net sales increased 15% to $4,840 million in the fiscal year, driven mainly by higher unit volume.")
        self.assertEqual((d["unchanged"], d["added"], d["removed"], d["modified"]), (1, [], [], []))

    def test_short_lines_ignored(self):
        self.assertEqual(diff.paragraphs("Item 7.\n\n42\n" + SAME), [SAME])


class RenderTest(unittest.TestCase):
    def test_budget_respected_and_every_section_has_header(self):
        prior = {"section_7": "\n".join(f"Old paragraph {i} " + "about prior year operations " * 5 for i in range(30))}
        current = {"section_7": "\n".join(f"New paragraph {i} " + "describing different matters entirely " * 5
                                          for i in range(30)),
                   "section_9A": NEW}
        text = diff.render(diff.filing_diff(prior, current), budget_chars=3000)
        self.assertLessEqual(len(text), 3000)
        for _, title in diff.SECTIONS:
            self.assertIn(f"## {title}:", text)
        self.assertIn(NEW, text)  # small section is not crowded out by the big one

    def test_old_10k_financials_from_items_14_15(self):
        self.assertEqual(diff.section_text({"section_8": "see Item 14", "section_14": "x" * 2500}, "FS"),
                         "x" * 2500 + "\n")


if __name__ == "__main__":
    unittest.main()

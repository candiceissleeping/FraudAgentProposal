"""Packet construction on synthetic filings (not real 10-Ks)."""
import unittest

from experiment.yoy import mask, packets


def para(tag, i):
    return f"{tag} paragraph {i} discusses " + " ".join(f"{tag}word{j}" for j in range(i % 7, i % 7 + 15))


def filing(tag, n):
    text = "\n".join(para(tag, i) for i in range(n))
    return {"section_1A": text, "section_7": text * 3, "section_8": text * 5, "section_9A": para(tag, 0)}


class AllowanceTest(unittest.TestCase):
    def test_equal_shares_with_redistribution(self):
        self.assertEqual(packets.allowances({"a": 10, "b": 1000, "c": 1000}, 610), {"a": 10, "b": 300, "c": 300})
        self.assertEqual(packets.allowances({"a": 10, "b": 20}, 1000), {"a": 10, "b": 20})


class BuildTest(unittest.TestCase):
    def setUp(self):
        self.texts, self.sims = packets.build(filing("now", 120), filing("before", 120))

    def test_current_year_part_identical_across_arms(self):
        cur = self.texts["A0"]
        for arm in ("A1", "A2"):
            self.assertTrue(self.texts[arm].startswith(cur))
        self.assertNotIn("CURRENT YEAR", self.texts["A3"])

    def test_a1_length_matches_a2(self):
        a1 = len(self.texts["A1"]) - len(self.texts["A0"])
        a2 = len(self.texts["A2"]) - len(self.texts["A0"])
        self.assertLess(abs(a1 - a2) / a2, 0.03)

    def test_current_part_within_budget(self):
        self.assertLessEqual(len(self.texts["A0"]), packets.CURRENT_CHARS + len(packets.HEADER) + 100)

    def test_masking_applied_before_packets(self):
        f = {"section_7": "Acme Widgets Inc. reported results for 2001 and 2000. " * 3}
        m = packets.masked_filing(f, 2001, mask.name_aliases("ACME WIDGETS INC /DE/"))
        self.assertEqual(m["section_7"].split(".")[0], "[COMPANY]")
        self.assertIn("results for Year T and Year T-1", m["section_7"])


if __name__ == "__main__":
    unittest.main()

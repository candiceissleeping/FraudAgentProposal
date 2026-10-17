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


class MaskTest(unittest.TestCase):
    def test_former_names_dotted_acronyms_and_state_suffix(self):
        firm = {"name": "SOURCECORP INC", "former_names": ["FYI INC"]}
        text = mask.mask('Our mark "F.Y.I. INCORPORATED"; FYI Inc. and SourceCorp grew; fyi readers.', 2001,
                         mask.firm_aliases(firm))
        self.assertNotIn("F.Y.I", text)
        self.assertNotIn("FYI", text)
        self.assertNotIn("SourceCorp", text)
        self.assertIn("KVH", mask.name_aliases("KVH INDUSTRIES INC \\DE\\"))
        self.assertNotIn("NEW", mask.name_aliases("NEW ENGLAND BUSINESS SERVICE INC"))

    def test_generic_words_kept(self):
        text = mask.mask("The Company and the Group reported results.", 2001, mask.name_aliases("GENERAL GROUP INC"))
        self.assertEqual(text, "The Company and the Group reported results.")


class MaskV2Test(unittest.TestCase):
    def setUp(self):
        generic = "The Company reported Revenue under SFAS No. 5 in the United States. the company revenue"
        self.vocab = mask.generic_vocab({i: [generic] for i in range(5)} |
                                        {"rare": ["Donald K. McGhan sold MediVIEW pumps in Las Vegas."]})

    def test_vocab_keeps_words_used_by_many_firms(self):
        self.assertIn("Revenue", self.vocab)
        self.assertNotIn("McGhan", self.vocab)
        self.assertNotIn("MediVIEW", self.vocab)

    def test_rare_names_places_cases_and_standards_masked(self):
        text = mask.mask("The Company: Donald K. McGhan sold MediVIEW in Hurst, Texas and Las Vegas; "
                         "Multiple District Litigation No. 926 and Case No. 99 C 0351. "
                         "Adopted SFAS No. 125 in 1996 before the Year 2000 issue.", 1996, (), self.vocab)
        for leak in ("McGhan", "MediVIEW", "Hurst", "Texas", "Las Vegas", "926", "0351", "125", "2000", "1996"):
            self.assertNotIn(leak, text)
        self.assertIn("The Company: [NAME] sold [NAME]", text)
        self.assertIn("SFAS No. [#]", text)
        self.assertIn("[Y2K]", text)

    def test_v1_unchanged_without_vocab(self):
        self.assertEqual(mask.mask("Revenue under SFAS No. 125 in Texas.", 1996), "Revenue under SFAS No. 125 in Texas.")


if __name__ == "__main__":
    unittest.main()

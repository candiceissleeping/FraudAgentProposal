"""Label and matching rules for experiment 1 on hand-made rows (not real data)."""
import os
import tempfile
import unittest

from experiment.yoy import build_sample, index_corpus, labels


def filing(cik, year, mda=5000, fs=5000, other=1000, item14=0):
    r = {f"len_{s}": 0 for s in index_corpus.SECTIONS}
    r.update(cik=cik, year=year, len_7=mda, len_8=fs, len_1A=other, len_14=item14)
    return r


def index(*filings):
    return {(f["cik"], f["year"]): f for f in filings}


class LabelTest(unittest.TestCase):
    def setUp(self):
        fd, self.path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w") as f:
            f.write("P_AAER,CIK,YEARA,UNDERSTATEMENT\n"
                    "1,0000100,2000,0\n1,0000100,2001,0\n"   # kept, t = 2000
                    "2,200,1990,0\n"                         # t-1 before corpus
                    "3,300,2005,1\n"                         # understatement
                    "4,400,2003,0\n5,400,2004,0\n")          # second episode starts after a misstated year
        self.rows = labels.load_rows(self.path)

    def tearDown(self):
        os.remove(self.path)

    def test_first_misstated_year_is_t(self):
        kept, dropped = labels.treatment_candidates(self.rows)
        self.assertEqual([(c["cik"], c["t"]) for c in kept], [("100", 2000), ("400", 2003)])
        self.assertEqual({d["p_aaer"]: d["reason"] for d in dropped},
                         {"2": "outside_corpus_years", "3": "understatement", "5": "prior_year_misstated"})

    def test_all_aaer_firms_excluded_from_controls(self):
        self.assertEqual(labels.fraud_ciks(self.rows), {"100", "200", "300", "400"})


class FilingTest(unittest.TestCase):
    def test_needs_both_years_usable(self):
        idx = index(filing("1", 2000), filing("1", 1999),
                    filing("2", 2000), filing("2", 1999, mda=100),
                    filing("3", 2000))
        self.assertIsNone(build_sample.filing_check(idx, "1", 2000))
        self.assertEqual(build_sample.filing_check(idx, "2", 2000), "empty_10k_t-1")
        self.assertEqual(build_sample.filing_check(idx, "3", 2000), "no_10k_t-1")

    def test_old_10k_financials_in_item_14(self):
        self.assertTrue(build_sample.usable(filing("1", 1998, fs=0, item14=9000)))
        self.assertEqual(build_sample.key_chars(filing("1", 1998, fs=0, item14=9000)), 1000 + 5000 + 9000)


class MatchTest(unittest.TestCase):
    def test_same_industry_closest_length_used_once(self):
        frauds = [{"cik": "F1", "p_aaer": "1", "t": 2000, "misstated_years": [2000], "key_chars": 10000},
                  {"cik": "F2", "p_aaer": "2", "t": 2000, "misstated_years": [2000], "key_chars": 10000},
                  {"cik": "F3", "p_aaer": "3", "t": 2000, "misstated_years": [2000], "key_chars": 10000},
                  {"cik": "F4", "p_aaer": "4", "t": 2001, "misstated_years": [2001], "key_chars": 10000}]
        pool = {2000: [("C1", 11000), ("C2", 30000), ("C3", 10000)]}
        sic = {"F1": {"sic": "2834"}, "F2": {"sic": "2836"}, "F3": {"sic": ""},
               "F4": {"sic": "2834"}, "C1": {"sic": "2830"}, "C2": {"sic": "2800"}, "C3": {"sic": "7372"}}
        pairs, dropped = build_sample.match(frauds, pool, sic)
        self.assertEqual([(p["fraud"]["cik"], p["control"]["cik"]) for p in pairs], [("F1", "C1"), ("F2", "C2")])
        self.assertEqual({d["cik"]: d["reason"] for d in dropped}, {"F3": "no_sic", "F4": "no_control"})
        self.assertTrue(all(p["pilot"] for p in pairs))  # fewer pairs than PILOT_PAIRS


if __name__ == "__main__":
    unittest.main()

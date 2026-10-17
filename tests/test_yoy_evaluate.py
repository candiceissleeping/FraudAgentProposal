"""Metric helpers for experiment 1 on hand-made scores."""
import json
import os
import tempfile
import types
import unittest

from experiment.yoy import evaluate, run_llm


class MetricTest(unittest.TestCase):
    def test_auc_with_ties(self):
        self.assertEqual(evaluate.auc([3, 2], [1, 2]), (1 + 1 + 1 + 0.5) / 4)

    def test_pair_auc_and_within_pair(self):
        pairs = [("f1", "c1"), ("f2", "c2")]
        s = {"f1": 80, "c1": 20, "f2": 30, "c2": 30}
        self.assertEqual(evaluate.within_pair(pairs, s), [1.0, 0.5])
        self.assertEqual(evaluate.pair_auc(pairs, s), (1 + 1 + 1 + 0.5) / 4)

    def test_bootstrap_identical_arms_is_zero(self):
        pairs = [(f"f{i}", f"c{i}") for i in range(20)]
        s = {d: i for i, d in enumerate(x for p in pairs for x in p)}
        self.assertEqual(evaluate.bootstrap_delta(pairs, s, s, n=200), (0.0, 0.0, 0.0))

    def test_mcnemar(self):
        p, b, c = evaluate.mcnemar_p([1.0] * 10, [0.0] * 10)
        self.assertEqual((b, c), (10, 0))
        self.assertAlmostEqual(p, 2 / 1024)
        self.assertEqual(evaluate.mcnemar_p([1.0, 0.0], [1.0, 0.0])[0], 1.0)

    def test_identified(self):
        enron = {"name": "ENRON CORP /OR/"}
        self.assertTrue(evaluate.identified({"company_guess": "Probably Enron Corp."}, enron))
        self.assertFalse(evaluate.identified({"company_guess": "A Texas energy trader"}, enron))
        self.assertFalse(evaluate.identified(None, enron))
        renamed = {"name": "SOURCECORP INC", "former_names": ["FYI INC"]}
        self.assertTrue(evaluate.identified({"company_guess": "F.Y.I. Incorporated"}, renamed) or
                        evaluate.identified({"company_guess": "FYI Inc"}, renamed))

    def test_load_recall_reads_only_k0(self):
        rows = [{"custom_id": "K0-D0001-r1", "data": {"recalls_sec_enforcement_for_year": "yes"}},
                {"custom_id": "K0-D0002-r1", "data": None},
                {"custom_id": "A0-D0001-r1", "data": {"fraud_probability": 50}}]
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write("\n".join(json.dumps(r) for r in rows))
        self.assertEqual(evaluate.load_recall(f.name), {"D0001": "yes"})
        os.unlink(f.name)


def fake_result(stop_reason, text):
    msg = types.SimpleNamespace(stop_reason=stop_reason, content=[types.SimpleNamespace(type="text", text=text)],
                                usage=types.SimpleNamespace(input_tokens=10, output_tokens=5))
    return types.SimpleNamespace(result=types.SimpleNamespace(type="succeeded", message=msg))


class ParseTest(unittest.TestCase):
    def test_parses_json_only_on_end_turn(self):
        ok = run_llm.parse_result(fake_result("end_turn", json.dumps({"fraud_probability": 70})))
        self.assertEqual(ok["data"], {"fraud_probability": 70})
        self.assertIsNone(run_llm.parse_result(fake_result("refusal", ""))["data"])
        self.assertIsNone(run_llm.parse_result(fake_result("max_tokens", '{"fraud_prob'))["data"])
        errored = types.SimpleNamespace(result=types.SimpleNamespace(type="errored"))
        self.assertEqual(run_llm.parse_result(errored)["status"], "errored")


if __name__ == "__main__":
    unittest.main()

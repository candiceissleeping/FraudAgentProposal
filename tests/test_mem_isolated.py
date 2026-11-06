"""verify() on hand-written stream-json logs: a clean no-tool run passes, any sign of web access fails."""
import copy
import unittest

from experiment.mem_isolated import parse_scores, shuffled_list, verify

CLEAN = [
    {"type": "system", "subtype": "init", "tools": [], "mcp_servers": [], "model": "claude-opus-5-5"},
    {"type": "assistant", "message": {"model": "claude-opus-5-5", "content": [{"type": "text", "text": "[]"}]}},
    {"type": "result", "subtype": "success", "is_error": False, "num_turns": 1, "result": "[]",
     "usage": {"server_tool_use": {"web_search_requests": 0, "web_fetch_requests": 0}},
     "modelUsage": {"claude-opus-5-5": {"webSearchRequests": 0}}, "subagent_stats": {"spawned": 0}},
]


class VerifyTest(unittest.TestCase):
    def test_clean_passes(self):
        self.assertTrue(verify(CLEAN)["all_pass"])

    def test_tool_offered_fails(self):
        ev = copy.deepcopy(CLEAN); ev[0]["tools"] = ["WebSearch"]
        v = verify(ev)
        self.assertFalse(v["tools_empty"]); self.assertFalse(v["all_pass"])

    def test_mcp_server_fails(self):
        ev = copy.deepcopy(CLEAN); ev[0]["mcp_servers"] = [{"name": "github", "status": "connected"}]
        self.assertFalse(verify(ev)["all_pass"])

    def test_server_tool_block_fails(self):
        ev = copy.deepcopy(CLEAN)
        ev[1]["message"]["content"].insert(0, {"type": "server_tool_use", "name": "web_search", "input": {}})
        v = verify(ev)
        self.assertFalse(v["no_tool_blocks"]); self.assertEqual(v["tool_blocks"][0]["name"], "web_search")

    def test_subagent_tool_call_fails(self):
        ev = copy.deepcopy(CLEAN)
        ev.insert(2, {"type": "assistant", "parent_tool_use_id": "toolu_x",
                      "message": {"content": [{"type": "tool_use", "name": "WebFetch", "input": {}}]}})
        self.assertFalse(verify(ev)["all_pass"])

    def test_server_counter_fails(self):
        ev = copy.deepcopy(CLEAN); ev[2]["usage"]["server_tool_use"]["web_search_requests"] = 2
        self.assertFalse(verify(ev)["server_web_zero"])
        ev = copy.deepcopy(CLEAN); ev[2]["modelUsage"]["claude-opus-5-5"]["webSearchRequests"] = 1
        self.assertFalse(verify(ev)["server_web_zero"])

    def test_missing_evidence_fails(self):
        self.assertFalse(verify(CLEAN[:2])["all_pass"])          # no result event
        self.assertFalse(verify(CLEAN[1:])["all_pass"])          # no init event
        ev = copy.deepcopy(CLEAN); del ev[2]["usage"]["server_tool_use"]
        self.assertFalse(verify(ev)["server_web_zero"])

    def test_extra_turns_or_subagents_fail(self):
        ev = copy.deepcopy(CLEAN); ev[2]["num_turns"] = 3
        self.assertFalse(verify(ev)["single_turn"])
        ev = copy.deepcopy(CLEAN); ev[2]["subagent_stats"]["spawned"] = 1
        self.assertFalse(verify(ev)["no_subagents"])


class HelpersTest(unittest.TestCase):
    def test_parse_scores(self):
        self.assertEqual(parse_scores('ok\n[{"id": 1, "risk_score": 5}]\n'), [{"id": 1, "risk_score": 5}])
        self.assertIsNone(parse_scores("no json here"))

    def test_shuffle_is_seeded_and_renumbered(self):
        lines = ["1. A — x", "2. B — y", "3. C — z"]
        a, b = shuffled_list(lines, 7), shuffled_list(lines, 7)
        self.assertEqual(a, b)
        self.assertEqual([l.split(". ", 1)[0] for l in a.splitlines()], ["1", "2", "3"])
        self.assertEqual(sorted(l.split(". ", 1)[1] for l in a.splitlines()), ["A — x", "B — y", "C — z"])


if __name__ == "__main__":
    unittest.main()

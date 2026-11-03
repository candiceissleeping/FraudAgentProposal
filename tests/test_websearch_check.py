import unittest

from experiment.websearch_check import classify


def _assistant(name, inp, parent=None):
    return {"type": "assistant", "parent_tool_use_id": parent,
            "message": {"content": [{"type": "tool_use", "name": name, "input": inp}]}}


class ClassifyTest(unittest.TestCase):
    def test_clean_run(self):
        ev = [{"type": "system", "subtype": "init", "tools": ["Read", "WebSearch"]},
              {"type": "assistant", "message": {"content": [{"type": "text", "text": "I don't know."}]}},
              {"type": "result", "result": "I don't know.", "permission_denials": []}]
        r = classify(ev)
        self.assertFalse(r["any"])
        self.assertTrue(r["websearch_offered"])

    def test_websearch_and_toolsearch_count(self):
        self.assertTrue(classify([_assistant("WebSearch", {"query": "TAIEX"})])["web_tool"])
        self.assertTrue(classify([_assistant("ToolSearch", {"query": "select:WebSearch"})])["web_tool"])
        self.assertFalse(classify([_assistant("ToolSearch", {"query": "select:Read"})])["any"])

    def test_shell_network(self):
        self.assertTrue(classify([_assistant("Bash", {"command": "curl -s https://twse.com.tw"})])["shell_net"])
        self.assertFalse(classify([_assistant("Bash", {"command": "ls -la"})])["any"])

    def test_subagent_calls_are_scanned(self):
        r = classify([_assistant("Agent", {"prompt": "look it up"}),
                      _assistant("WebFetch", {"url": "https://x"}, parent="toolu_1")])
        self.assertTrue(r["delegate"] and r["web_tool"])
        self.assertTrue(r["hits"]["web_tool"][0]["subagent"])

    def test_other_routes(self):
        self.assertTrue(classify([_assistant("Bash", {"command": "gh api search/code -f q=enron"})])["shell_net"])
        self.assertTrue(classify([_assistant("Bash", {"command": "git clone x/y"})])["shell_net"])
        self.assertTrue(classify([_assistant("Write", {"file_path": "a.py", "content": "import requests"})])["shell_net"])
        self.assertTrue(classify([_assistant("Skill", {"skill": "anthropic-skills:deep-research"})])["delegate"])
        self.assertTrue(classify([_assistant("Workflow", {"script": "..."})])["delegate"])
        self.assertTrue(classify([_assistant("mcp__github__get_file_contents", {})])["mcp"])
        self.assertFalse(classify([_assistant("mcp__ccd_session__spawn_task", {})])["any"])
        self.assertFalse(classify([_assistant("Skill", {"skill": "pdf"})])["any"])

    def test_hard_block_not_offered(self):
        r = classify([{"type": "system", "subtype": "init", "tools": ["Read"]}])
        self.assertFalse(r["websearch_offered"])


if __name__ == "__main__":
    unittest.main()

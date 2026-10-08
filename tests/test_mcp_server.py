"""Unit tests for the stdio MCP server protocol and handlers."""

import json
import os
import tempfile
import unittest

from mcp.server import (
    handle_initialize,
    handle_tools_call,
    handle_tools_list,
)
from mcp.tools.receipts_verifier import create_receipt_file


class TestMcpServer(unittest.TestCase):

  def test_initialize_handshake(self):
    resp = handle_initialize(1, {})
    self.assertEqual(resp["id"], 1)
    result = resp.get("result", {})
    self.assertEqual(result.get("protocolVersion"), "2024-11-05")
    self.assertEqual(result.get("serverInfo", {}).get("name"), "orchestra-tools")

  def test_tools_list(self):
    resp = handle_tools_list(2)
    self.assertEqual(resp["id"], 2)
    tools = resp.get("result", {}).get("tools", [])
    tool_names = [t["name"] for t in tools]

    self.assertIn("detect_test_tampering", tool_names)
    self.assertIn("verify_receipts", tool_names)
    self.assertIn("get_orchestration_status", tool_names)
    self.assertIn("record_orchestration_event", tool_names)

  def test_tool_call_verify_receipts(self):
    with tempfile.TemporaryDirectory() as tmpdir:
      receipt_path = os.path.join(tmpdir, "receipt.txt")
      create_receipt_file(
          receipt_path=receipt_path,
          command="pytest",
          exit_code=0,
          output="1 passed",
      )

      resp = handle_tools_call(3, {
          "name": "verify_receipts",
          "arguments": {"receipt_path": receipt_path},
      })
      self.assertEqual(resp["id"], 3)
      content = resp["result"]["content"][0]["text"]
      parsed = json.loads(content)
      self.assertTrue(parsed["passed"])

  def test_tool_call_get_orchestration_status(self):
    resp = handle_tools_call(4, {
        "name": "get_orchestration_status",
        "arguments": {
            "conversation_id": "test-conv-123",
            "context_tokens": 50000,
        },
    })
    self.assertEqual(resp["id"], 4)
    content = resp["result"]["content"][0]["text"]
    parsed = json.loads(content)
    self.assertEqual(parsed["recommendation"], "continue")
    self.assertEqual(parsed["context_tokens"], 50000)

  def test_tool_call_record_orchestration_event(self):
    resp = handle_tools_call(5, {
        "name": "record_orchestration_event",
        "arguments": {
            "task_tier": "tier_1_surgical",
            "verification_outcome": "PASSED",
            "details": "Fix typo in auth service",
        },
    })
    self.assertEqual(resp["id"], 5)
    content = resp["result"]["content"][0]["text"]
    parsed = json.loads(content)
    self.assertTrue(parsed["recorded"])

  def test_tool_call_unknown_tool(self):
    resp = handle_tools_call(6, {
        "name": "nonexistent_tool",
        "arguments": {},
    })
    self.assertIn("error", resp)
    self.assertEqual(resp["error"]["code"], -32601)


if __name__ == "__main__":
  unittest.main()

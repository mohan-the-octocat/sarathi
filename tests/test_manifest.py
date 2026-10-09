"""Tests for Sarathi plugin.json and mcp_config.json manifests."""

import json
import pathlib
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent


class TestManifests(unittest.TestCase):

  def test_plugin_json_exists_and_valid(self):
    plugin_path = PROJECT_ROOT / "plugin.json"
    self.assertTrue(plugin_path.is_file(), "plugin.json must exist")

    with open(plugin_path, "r", encoding="utf-8") as f:
      manifest = json.load(f)

    self.assertEqual(manifest.get("name"), "sarathi")
    self.assertEqual(manifest.get("displayName"), "Sarathi")
    self.assertTrue(manifest.get("version"), "Must have a version")
    self.assertIn("capabilities", manifest)
    self.assertTrue(manifest["capabilities"].get("agents"))
    self.assertTrue(manifest["capabilities"].get("skills"))
    self.assertTrue(manifest["capabilities"].get("mcp"))

  def test_mcp_config_json_exists_and_valid(self):
    mcp_path = PROJECT_ROOT / "mcp_config.json"
    self.assertTrue(mcp_path.is_file(), "mcp_config.json must exist")

    with open(mcp_path, "r", encoding="utf-8") as f:
      config = json.load(f)

    self.assertIn("mcpServers", config)
    self.assertIn("sarathi-tools", config["mcpServers"])
    server_conf = config["mcpServers"]["sarathi-tools"]

    self.assertEqual(server_conf.get("command"), "python3")
    self.assertIn("args", server_conf)
    self.assertIn("mcp/server.py", server_conf["args"])

    enabled_tools = server_conf.get("enabledTools", [])
    expected_tools = [
        "detect_test_tampering",
        "verify_receipts",
        "get_orchestration_status",
        "record_orchestration_event",
    ]
    for tool in expected_tools:
      self.assertIn(tool, enabled_tools)


if __name__ == "__main__":
  unittest.main()

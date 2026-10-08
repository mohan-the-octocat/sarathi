"""Tests validating Antigravity agent definitions and YAML frontmatter."""

import pathlib
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
AGENTS_DIR = PROJECT_ROOT / "agents"


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
  """Simple parser for YAML frontmatter without external yaml dependency."""
  lines = content.splitlines()
  if not lines or lines[0].strip() != "---":
    return {}, content

  data = {}
  end_idx = -1
  for i, line in enumerate(lines[1:], start=1):
    if line.strip() == "---":
      end_idx = i
      break
    if ":" in line:
      key, val = line.split(":", 1)
      key = key.strip()
      val = val.strip().strip('"').strip("'")
      data[key] = val

  body = "\n".join(lines[end_idx + 1:]) if end_idx != -1 else ""
  return data, body


class TestAgents(unittest.TestCase):

  def test_all_expected_agents_exist(self):
    expected_agents = [
        "orchestra.md",
        "orchestra_scout.md",
        "orchestra_scout_deep.md",
        "orchestra_worker.md",
        "orchestra_worker_heavy.md",
        "orchestra_redteam.md",
        "orchestra_redteam_heavy.md",
    ]
    for agent_name in expected_agents:
      agent_path = AGENTS_DIR / agent_name
      self.assertTrue(agent_path.is_file(), f"Agent file missing: {agent_name}")

  def test_main_conductor_agent(self):
    path = AGENTS_DIR / "orchestra.md"
    content = path.read_text(encoding="utf-8")
    frontmatter, body = parse_frontmatter(content)

    self.assertEqual(frontmatter.get("name"), "orchestra")
    self.assertTrue(frontmatter.get("description"))
    self.assertEqual(frontmatter.get("mainAgent"), "true")
    self.assertEqual(frontmatter.get("subagent"), "true")

    # Body must have H1 headings for prompt sections
    self.assertIn("# Orchestra Conductor", body)
    self.assertIn("# Execution Tiers", body)
    self.assertIn("# Subagent Fleet & Delegation Protocol", body)
    self.assertIn("# Return Header & Verification Contract", body)
    self.assertIn("# Two-Turn Circuit Breaker", body)

  def test_subagent_roles_and_models(self):
    subagents = {
        "orchestra_scout.md": ("flash", "false", "true"),
        "orchestra_scout_deep.md": ("pro", "false", "true"),
        "orchestra_worker.md": ("flash", "false", "true"),
        "orchestra_worker_heavy.md": ("pro", "false", "true"),
        "orchestra_redteam.md": ("flash", "false", "true"),
        "orchestra_redteam_heavy.md": ("pro", "false", "true"),
    }
    for filename, (model, main_agent, subagent) in subagents.items():
      path = AGENTS_DIR / filename
      content = path.read_text(encoding="utf-8")
      fm, body = parse_frontmatter(content)

      self.assertEqual(fm.get("model"), model, f"Model mismatch for {filename}")
      self.assertEqual(fm.get("mainAgent"), main_agent, f"mainAgent mismatch for {filename}")
      self.assertEqual(fm.get("subagent"), subagent, f"subagent mismatch for {filename}")
      self.assertTrue(fm.get("description"), f"Missing description in {filename}")
      self.assertTrue(len(body.strip()) > 100, f"Body too short in {filename}")


if __name__ == "__main__":
  unittest.main()

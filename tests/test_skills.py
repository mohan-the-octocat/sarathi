"""Tests validating Antigravity skill definitions and slash commands."""

import pathlib
import unittest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


def parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
  """Simple parser for YAML frontmatter."""
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


class TestSkills(unittest.TestCase):

  def test_sarathi_skill(self):
    path = SKILLS_DIR / "sarathi" / "SKILL.md"
    self.assertTrue(path.is_file(), "skills/sarathi/SKILL.md must exist")
    content = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    self.assertEqual(fm.get("name"), "sarathi")
    self.assertTrue(fm.get("description"))
    self.assertIn("Complexity Tier Routing", body)
    self.assertIn("Dispatch Template", body)
    self.assertIn("Two-Turn Circuit Breaker", body)

  def test_sarathi_plan_skill(self):
    path = SKILLS_DIR / "sarathi_plan" / "SKILL.md"
    self.assertTrue(path.is_file(), "skills/sarathi_plan/SKILL.md must exist")
    content = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    self.assertEqual(fm.get("name"), "sarathi_plan")
    self.assertTrue(fm.get("description"))
    self.assertIn("Zero-Decision Rule", body)
    self.assertIn("Phase 1: Heilmeier Scoped Grill", body)
    self.assertIn("Phase 2: Semantic Split Draft", body)
    self.assertIn("Phase 3: Goldfish Split Audit", body)
    self.assertIn("Phase 4: Resolution & Implementation Handoff", body)

  def test_sarathi_verify_skill(self):
    path = SKILLS_DIR / "sarathi_verify" / "SKILL.md"
    self.assertTrue(path.is_file(), "skills/sarathi_verify/SKILL.md must exist")
    content = path.read_text(encoding="utf-8")
    fm, body = parse_frontmatter(content)

    self.assertEqual(fm.get("name"), "sarathi_verify")
    self.assertTrue(fm.get("description"))
    self.assertIn("Test Tampering Detection", body)
    self.assertIn("Receipts Reconciliation", body)


if __name__ == "__main__":
  unittest.main()

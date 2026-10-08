"""Audits Git and VCS diffs for test assertion tampering and added suppressions.

Scans diffs in test files to detect:
1. Deleted test assertions.
2. Commented-out test assertions.
3. Added compiler or linter suppression directives.
"""

from __future__ import annotations

import os
import pathlib
import re
import subprocess
from typing import Any

SUPPRESSION_PATTERNS = (
    r"@Suppress\b",
    r"@SuppressWarnings\b",
    r"//\s*NOLINT",
    r"/\*\s*NOLINT\s*\*/",
    r"#\s*pylint:\s*disable",
    r"#\s*noqa\b",
    r"#\s*flake8:\s*noqa\b",
    r"#\s*pytype:\s*disable",
    r"//\s*eslint-disable",
    r"/\*\s*eslint-disable\s*\*/",
    r"//\s*@ts-ignore\b",
    r"//\s*@ts-nocheck\b",
    r"//\s*@ts-expect-error\b",
    r"//\s*go:build\s*ignore\b",
    r"@unittest\.skip\w*",
    r"@pytest\.mark\.(?:skip\w*|xfail)\b",
    r"#\s*type:\s*ignore\b",
)

ASSERTION_PATTERNS = (
    r"\bassert\b",
    r"\bassert[A-Z]\w*\b",
    r"\bassert_\w+\b",
    r"\bassert\.NoError\b",
    r"\bassert\.(?:Equal|True|False|NotNil|Nil|Contains)\b",
    r"\brequire\.(?:Equal|NoError|True|False|NotNil|Nil)\b",
    r"\bpytest\.raises\b",
    r"\bexpect\(",
    r"\bt\.(?:Error|Errorf|Fatal|Fatalf)\b",
    r"\bassertEquals\(",
    r"\bassertTrue\(",
    r"\bassertFalse\(",
    r"\bassertThat\(",
    r"\bASSERT_\w+\b",
    r"\bEXPECT_\w+\b",
)

TEST_FILE_REGEX = re.compile(
    r"(_test\.(py|go|ts|js|cc|cpp)|Test\.(java|kt)|test_.*\.py|\.test\.(ts|js|jsx|tsx)|\.spec\.(ts|js|jsx|tsx))$"
)


def is_test_filename(filepath: str) -> bool:
  """Checks whether a filepath is a test file based on conventions."""
  basename = os.path.basename(filepath)
  return bool(TEST_FILE_REGEX.search(basename)) or "test" in filepath.lower().split(os.sep)


def scan_diff_for_tampering(diff_output: str) -> dict[str, Any]:
  """Scans unified diff text for deleted assertions and added suppressions.

  Args:
    diff_output: Raw unified diff output (e.g. from `git diff`).

  Returns:
    Dict containing tampering_detected bool, violations list, and files scanned.
  """
  violations: list[dict[str, Any]] = []
  test_files_scanned: set[str] = set()
  current_file = ""
  is_test_file = False

  for line in diff_output.splitlines():
    # Detect diff headers
    if line.startswith("diff ") or line.startswith("--- ") or line.startswith("+++ "):
      match = re.search(r"[ab]/([^\s]+)", line)
      if match:
        current_file = match.group(1)
        is_test_file = is_test_filename(current_file)
        if is_test_file:
          test_files_scanned.add(current_file)
      continue

    if not is_test_file:
      continue

    # Detect deleted assertions: line starts with '-' (excluding '---')
    if line.startswith("-") and not line.startswith("---"):
      content = line[1:].strip()
      for pattern in ASSERTION_PATTERNS:
        if re.search(pattern, content):
          violations.append({
              "file": current_file,
              "type": "DELETED_ASSERTION",
              "pattern": pattern,
              "snippet": content,
          })
          break

    # Detect added suppressions or commented-out assertions: line starts with '+' (excluding '+++')
    elif line.startswith("+") and not line.startswith("+++"):
      content = line[1:].strip()

      # Check for added linter/compiler suppressions
      for pattern in SUPPRESSION_PATTERNS:
        if re.search(pattern, content):
          violations.append({
              "file": current_file,
              "type": "ADDED_SUPPRESSION",
              "pattern": pattern,
              "snippet": content,
          })
          break

      # Check for commented-out assertions (e.g. `// assert...` or `# assert...`)
      commented_assertion_match = re.match(r"^(?://|#|/\*|\*)\s*(.*)$", content)
      if commented_assertion_match:
        comment_body = commented_assertion_match.group(1)
        for pattern in ASSERTION_PATTERNS:
          if re.search(pattern, comment_body):
            violations.append({
                "file": current_file,
                "type": "COMMENTED_OUT_ASSERTION",
                "pattern": pattern,
                "snippet": content,
            })
            break

  return {
      "tampering_detected": len(violations) > 0,
      "violations_count": len(violations),
      "violations": violations,
      "test_files_scanned": sorted(list(test_files_scanned)),
      "clean": len(violations) == 0,
  }


def detect_test_tampering(
    workspace_dir: str = ".",
    base_revision: str | None = None,
) -> dict[str, Any]:
  """Runs a test tampering audit against a workspace's Git working copy diff.

  Args:
    workspace_dir: The root directory of the workspace.
    base_revision: Optional Git base revision (e.g. HEAD~1, main, origin/main).

  Returns:
    Dictionary containing audit results and findings.
  """
  resolved_dir = str(pathlib.Path(workspace_dir).resolve())

  # Run git diff commands (staged and unstaged)
  diff_cmd = ["git", "diff", "--unified=0"]
  if base_revision:
    diff_cmd.append(base_revision)

  try:
    proc = subprocess.run(
        diff_cmd,
        cwd=resolved_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
      return {
          "tampering_detected": False,
          "error": f"git diff failed with exit code {proc.returncode}: {proc.stderr.strip()}",
          "clean": False,
      }
    diff_output = proc.stdout

    # Also capture staged diff if base_revision is not explicitly passed
    if not base_revision:
      staged_proc = subprocess.run(
          ["git", "diff", "--cached", "--unified=0"],
          cwd=resolved_dir,
          capture_output=True,
          text=True,
          check=False,
      )
      if staged_proc.returncode == 0:
        diff_output += "\n" + staged_proc.stdout

    result = scan_diff_for_tampering(diff_output)
    result["workspace_dir"] = resolved_dir
    result["base_revision"] = base_revision
    return result

  except FileNotFoundError:
    return {
        "tampering_detected": False,
        "error": "git executable not found in environment PATH",
        "clean": False,
    }
  except Exception as e:
    return {
        "tampering_detected": False,
        "error": f"Unexpected error during diff audit: {str(e)}",
        "clean": False,
    }

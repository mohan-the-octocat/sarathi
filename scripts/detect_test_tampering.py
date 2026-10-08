#!/usr/bin/env python3
"""CLI utility to audit Git diffs for test tampering and suppression additions."""

from __future__ import annotations

import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
  sys.path.insert(0, PROJECT_ROOT)

from mcp.tools.test_tampering import detect_test_tampering


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
      description="Audits Git diffs for deleted assertions, commented-out tests, and added suppressions."
  )
  parser.add_argument(
      "--workspace-dir",
      "-w",
      default=".",
      help="Workspace root directory (default: current directory).",
  )
  parser.add_argument(
      "--base-revision",
      "-b",
      default=None,
      help="Optional Git base revision (e.g. HEAD~1, main, origin/main).",
  )
  parser.add_argument(
      "--json",
      action="store_true",
      help="Emit machine-readable JSON output.",
  )

  args = parser.parse_args(argv)
  result = detect_test_tampering(
      workspace_dir=args.workspace_dir,
      base_revision=args.base_revision,
  )

  if args.json:
    print(json.dumps(result, indent=2))
    return 1 if result.get("tampering_detected") else 0

  if result.get("error"):
    print(f"[ERROR] {result['error']}", file=sys.stderr)
    return 2

  if result.get("tampering_detected"):
    violations = result.get("violations", [])
    print(f"[VIOLATION] Test tampering detected ({len(violations)} violation(s)):", file=sys.stderr)
    for v in violations:
      print(
          f"  - [{v.get('type')}] {v.get('file')}: `{v.get('snippet')}`"
          f" (matched pattern: {v.get('pattern')})",
          file=sys.stderr,
      )
    return 1

  print(f"[CLEAN] No test tampering detected across {len(result.get('test_files_scanned', []))} test file(s).")
  return 0


if __name__ == "__main__":
  sys.exit(main())

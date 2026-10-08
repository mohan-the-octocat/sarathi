#!/usr/bin/env python3
"""CLI utility to validate and reconcile worker receipts files."""

from __future__ import annotations

import argparse
import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
  sys.path.insert(0, PROJECT_ROOT)

from mcp.tools.receipts_verifier import verify_receipts


def main(argv: list[str] | None = None) -> int:
  parser = argparse.ArgumentParser(
      description="Validates that a receipts file exists, contains the executed command, and proves exit code 0."
  )
  parser.add_argument(
      "--file",
      "-f",
      required=True,
      help="Path to the receipts file to verify.",
  )
  parser.add_argument(
      "--json",
      action="store_true",
      help="Emit machine-readable JSON output.",
  )

  args = parser.parse_args(argv)
  result = verify_receipts(args.file)

  if args.json:
    print(json.dumps(result, indent=2))
    return 0 if result.get("passed") else 1

  if result.get("passed"):
    print(f"[PASSED] Valid receipts file: {result['receipt_path']}")
    print(f"  Command:   {result['command']}")
    print(f"  Exit code: {result['exit_code']}")
    return 0
  else:
    print(f"[FAILED] Invalid receipts file: {result['receipt_path']}", file=sys.stderr)
    for err in result.get("errors", []):
      print(f"  - {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
  sys.exit(main())

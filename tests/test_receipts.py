"""Unit tests for receipts verification and formatting."""

import os
import tempfile
import unittest

from mcp.tools.receipts_verifier import create_receipt_file, verify_receipts


class TestReceiptsVerifier(unittest.TestCase):

  def setUp(self):
    self.temp_dir = tempfile.TemporaryDirectory()

  def tearDown(self):
    self.temp_dir.cleanup()

  def test_valid_passing_receipt(self):
    receipt_path = os.path.join(self.temp_dir.name, "valid_receipt.txt")
    create_receipt_file(
        receipt_path=receipt_path,
        command="pytest tests/test_core.py",
        exit_code=0,
        output="==== 5 passed in 0.42s ====",
    )

    result = verify_receipts(receipt_path)
    self.assertTrue(result["valid"])
    self.assertTrue(result["passed"])
    self.assertEqual(result["exit_code"], 0)
    self.assertEqual(result["command"], "pytest tests/test_core.py")
    self.assertIn("5 passed", result["output_snippet"])

  def test_failing_exit_code_receipt(self):
    receipt_path = os.path.join(self.temp_dir.name, "failing_receipt.txt")
    create_receipt_file(
        receipt_path=receipt_path,
        command="npm test",
        exit_code=1,
        output="1 failing test: Expected 200, got 500",
    )

    result = verify_receipts(receipt_path)
    self.assertTrue(result["valid"])
    self.assertFalse(result["passed"])
    self.assertEqual(result["exit_code"], 1)

  def test_nonexistent_receipt_file(self):
    result = verify_receipts("/tmp/nonexistent_sarathi_receipt_xyz.txt")
    self.assertFalse(result["valid"])
    self.assertFalse(result["passed"])
    self.assertTrue(any("does not exist" in e for e in result["errors"]))

  def test_empty_receipt_file(self):
    receipt_path = os.path.join(self.temp_dir.name, "empty.txt")
    with open(receipt_path, "w") as f:
      pass

    result = verify_receipts(receipt_path)
    self.assertFalse(result["valid"])
    self.assertFalse(result["passed"])
    self.assertTrue(any("is empty" in e for e in result["errors"]))

  def test_missing_command_fence(self):
    receipt_path = os.path.join(self.temp_dir.name, "no_cmd.txt")
    with open(receipt_path, "w") as f:
      f.write("Exit code: 0\nOutput: test passed\n")

    result = verify_receipts(receipt_path)
    self.assertFalse(result["valid"])
    self.assertFalse(result["passed"])
    self.assertTrue(any("Missing or malformed test command" in e for e in result["errors"]))


if __name__ == "__main__":
  unittest.main()

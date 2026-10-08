"""Unit tests for test tampering detection across diffs."""

import unittest
from mcp.tools.test_tampering import scan_diff_for_tampering


class TestTamperingDetector(unittest.TestCase):

  def test_clean_diff_no_tampering(self):
    diff = """
diff --git a/tests/test_calculator.py b/tests/test_calculator.py
--- a/tests/test_calculator.py
+++ b/tests/test_calculator.py
@@ -10,2 +10,4 @@
+def test_addition():
+    assert add(1, 2) == 3
"""
    result = scan_diff_for_tampering(diff)
    self.assertTrue(result["clean"])
    self.assertFalse(result["tampering_detected"])
    self.assertEqual(len(result["violations"]), 0)

  def test_deleted_assertion_python(self):
    diff = """
diff --git a/tests/test_calculator.py b/tests/test_calculator.py
--- a/tests/test_calculator.py
+++ b/tests/test_calculator.py
@@ -10,3 +10,2 @@
 def test_addition():
-    assert add(1, 2) == 3
     return True
"""
    result = scan_diff_for_tampering(diff)
    self.assertFalse(result["clean"])
    self.assertTrue(result["tampering_detected"])
    self.assertEqual(len(result["violations"]), 1)
    self.assertEqual(result["violations"][0]["type"], "DELETED_ASSERTION")
    self.assertIn("assert add(1, 2) == 3", result["violations"][0]["snippet"])

  def test_deleted_assertion_go(self):
    diff = """
diff --git a/pkg/auth/auth_test.go b/pkg/auth/auth_test.go
--- a/pkg/auth/auth_test.go
+++ b/pkg/auth/auth_test.go
@@ -20,3 +20,1 @@
-	assert.NoError(t, err)
-	require.Equal(t, expected, actual)
"""
    result = scan_diff_for_tampering(diff)
    self.assertTrue(result["tampering_detected"])
    self.assertEqual(len(result["violations"]), 2)
    self.assertEqual(result["violations"][0]["type"], "DELETED_ASSERTION")

  def test_deleted_assertion_javascript(self):
    diff = """
diff --git a/src/client.test.ts b/src/client.test.ts
--- a/src/client.test.ts
+++ b/src/client.test.ts
@@ -15,2 +15,1 @@
-    expect(response.status).toBe(200);
"""
    result = scan_diff_for_tampering(diff)
    self.assertTrue(result["tampering_detected"])
    self.assertEqual(result["violations"][0]["type"], "DELETED_ASSERTION")

  def test_commented_out_assertion(self):
    diff = """
diff --git a/tests/test_worker.py b/tests/test_worker.py
--- a/tests/test_worker.py
+++ b/tests/test_worker.py
@@ -5,2 +5,2 @@
-    assert result.ok is True
+    # assert result.ok is True
"""
    result = scan_diff_for_tampering(diff)
    self.assertTrue(result["tampering_detected"])
    types = [v["type"] for v in result["violations"]]
    self.assertIn("DELETED_ASSERTION", types)
    self.assertIn("COMMENTED_OUT_ASSERTION", types)

  def test_added_suppression_annotations(self):
    diff = """
diff --git a/tests/test_api.py b/tests/test_api.py
--- a/tests/test_api.py
+++ b/tests/test_api.py
@@ -1,3 +1,5 @@
+@pytest.mark.skip(reason="temp fix")
 def test_failing_endpoint():
+    # noqa: E501
     assert call() == 200
"""
    result = scan_diff_for_tampering(diff)
    self.assertTrue(result["tampering_detected"])
    self.assertTrue(any(v["type"] == "ADDED_SUPPRESSION" for v in result["violations"]))

  def test_non_test_files_ignored(self):
    # In regular source code, assertions or noqas might be refactored without being test tampering
    diff = """
diff --git a/src/core/engine.py b/src/core/engine.py
--- a/src/core/engine.py
+++ b/src/core/engine.py
@@ -50,2 +50,1 @@
-    assert state is not None
+    if state is None: raise ValueError()
"""
    result = scan_diff_for_tampering(diff)
    self.assertTrue(result["clean"])
    self.assertFalse(result["tampering_detected"])


if __name__ == "__main__":
  unittest.main()

---
name: sarathi_verify
description: "Verifies subagent execution receipts, detects test tampering across VCS diffs, and checks manifest boundary compliance."
metadata:
  icon: 🛡️
---

# Sarathi Verify Skill

The `/sarathi-verify` skill performs deterministic verification of changes produced by workers and subagents.

It eliminates hallucinated or unverified test claims by comparing receipts against physical execution artifacts and auditing git diffs for assertion tampering.

## Core Verification Capabilities

### 1. Test Tampering Detection
A common failure mode in autonomous coding is test tampering: an agent that hits a failing test deletes the assertion, comments out the test, or adds suppression annotations (`@pytest.mark.skip`, `noqa`, `eslint-disable`, `@Suppress`, etc.) to force a green build.

`/sarathi-verify` scans the working copy diff for:
- Deleted or commented-out assertions (`assert`, `expect(`, `t.Error`, `require.Equal`, etc.)
- Added linter or compiler suppressions (`noqa`, `eslint-disable`, `@Suppress`, `@unittest.skip`, `@pytest.mark.skip`, `// NOLINT`, `type: ignore`, etc.)
- Modified test files outside the task scope

### 2. Receipts Reconciliation
Never trust chat statements that tests passed. `/sarathi-verify` inspects the physical `RECEIPTS_FILE`:
- Ensures the file exists and is non-empty.
- Validates the presence of the exact terminal command.
- Verifies an exit code of 0 and non-empty passing output.

### 3. Boundary & Manifest Compliance
- Checks that all modified files in `git status` match the `ASSIGNED_FILES_EXCLUSIVE` manifest.
- Reverts any accidental changes made outside the assigned boundaries.

## Standalone Usage

You can also run verification directly from the command line:

```bash
# Audit working tree for test tampering
python3 scripts/detect_test_tampering.py

# Verify receipts file format and output
python3 scripts/reconcile_receipts.py --file scratch/receipts.txt
```

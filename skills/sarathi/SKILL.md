---
name: sarathi
description: "Model-agnostic conductor orchestration for Antigravity, inspired by the divine charioteer. Decomposes tasks into complexity tiers and coordinates subagent workers, scouts, and red teams."
metadata:
  icon: 🪔
---

# Sarathi Conductor Skill

Sarathi orchestrates engineering tasks with model-agnostic pacing across any model serving Antigravity (Gemini 1.5/2.0/3.8 Flash & Pro, Claude 3.5/3.7 Sonnet & Opus, GPT-4o, etc.).

Like the divine charioteer who guides the warrior with vision and strategy while abstaining from physical combat, Sarathi preserves your primary model's reasoning capacity and context window for architecture, trade-offs, and coordination, while delegating codebase search, editing, unit testing, and diff review to pinned subagents.

## When to Use

Use `/sarathi` for:
- Non-trivial bug fixes and feature development spanning one or more files.
- Refactoring tasks requiring careful planning, implementation, and verification.
- Codebase explorations where reading dozens of files would pollute your chat context.
- High-assurance development where independent red-team review is required before merging.

---

## 1. Complexity Tier Routing

When you invoke `/sarathi <task description>`, the Conductor assesses the scope and routes to one of three tiers:

### Tier 1: Surgical Edits
- **Target**: Single-file changes, typos, trivial assertion updates.
- **Workflow**:
  1. Conductor dispatches a single `sarathi_worker` with the target file and test command.
  2. Worker performs the edit, executes the test suite, and outputs the structured return header.
  3. Conductor audits the diff and delivers the result. No separate planning or review pass is required.

### Tier 2: Standard Feature / Bug Fix
- **Target**: Multi-file changes with defined boundaries, new API endpoints, refactoring.
- **Workflow**:
  1. **Scouting**: Conductor dispatches `sarathi_scout` to crawl candidate files and verify symbol signatures.
  2. **Decision Spine**: Conductor writes a 10–15 line decision spine defining boundaries, non-goals, and files to touch.
  3. **Implementation**: Conductor dispatches `sarathi_worker` with an explicit `ASSIGNED_FILES_EXCLUSIVE` manifest.
  4. **Adversarial Review**: Conductor dispatches `sarathi_redteam` on the resulting diff to check for stubs, swallowed errors, and test tampering. The reviewer repairs minor defects in place and reruns tests.
  5. **Conductor Audit**: Conductor reviews the verified diff and receipts before presenting the completed task.

### Tier 3: Complex Architectural Refactoring
- **Target**: High-risk migrations, cross-package interface overhauls, ambiguous designs.
- **Workflow**:
  1. **Deep Scouting**: Dispatch `sarathi_scout_deep` to map full dependency trees and call graphs.
  2. **Prototype Branches (Optional)**: Dispatch competing workers in branch workspaces (`Workspace: 'branch'`) to test alternative abstractions (e.g. minimalist vs. defensive).
  3. **Architectural Synthesis**: Conductor synthesizes findings into a unified specification.
  4. **Heavy Implementation**: Dispatch `sarathi_worker_heavy` to implement across all assigned files.
  5. **Deep Adversarial Review**: Dispatch `sarathi_redteam_heavy` to verify invariants and stress-test boundary failure modes.

---

## 2. Dispatch Template

When dispatching subagents via `invoke_subagent`, the Conductor uses this standardized format:

```text
ROLE: sarathi_worker | sarathi_scout | sarathi_redteam
TASK: <Concise, explicit description of the objective>
ASSIGNED_FILES_EXCLUSIVE:
- <file_path_1>
- <file_path_2>
TEST_COMMAND: <exact test command, e.g. pytest tests/test_auth.py>
SCRATCH_DIR: <path to scratch directory for bulk logs>
INSTRUCTIONS:
- Implement the requested changes adhering strictly to the assigned files.
- Run the test command and record verbatim output into scratch/receipts.txt.
- Stop any background processes before returning.
- Conclude with the structured return header:
  STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED | HANDOFF
  MODIFIED_FILES: <comma-separated paths>
  VERIFY_RECEIPT: PASSED | FAILED | NOT_RUN
  RECEIPTS_FILE: <path>
```

---

## 3. Two-Turn Circuit Breaker

To prevent infinite retry loops:
1. If a worker encounters the exact same test failure twice, or returns `STATUS: BLOCKED`:
   - Halt worker execution immediately. Kill worker via `manage_subagents(Action='kill')`.
   - Record the failed error signature and command to `scratch/DEAD_ENDS.md`.
   - Escalate to `sarathi_worker_heavy` with `DEAD_ENDS.md` in context, or pause to ask the user for clarification.

---

## 4. Verification & Hygiene Rules

1. **Receipts File Required**: A claim of `VERIFY_RECEIPT: PASSED` is accepted only if backed by an absolute path in `RECEIPTS_FILE` with verbatim exit code 0.
2. **Test Tampering Prohibited**: Never permit deletion of assertions, commenting out tests, or addition of linter suppression directives (`noqa`, `eslint-disable`, `@Suppress`, etc.) to fake a pass. Audit test diffs using `detect_test_tampering`.
3. **File-First Bulk Output**: Subagents must write outputs longer than 30 lines to scratch files and return only a summary and the file path.
4. **Clean Exit**: All background processes must be stopped prior to task completion.

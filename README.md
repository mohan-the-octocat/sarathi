# Sarathi (सारथि)

<p align="center">
  <img src="assets/logo.svg" alt="Sarathi Logo" width="160" height="160" />
</p>

<p align="center">
  <strong>Model-Agnostic Conductor Plugin & Subagent Fleet for Google Antigravity</strong><br/>
  <i>Inspired by the divine charioteer: steering with vision, strategy, and judgment while directing the execution fleet.</i>
</p>

<p align="center">
  <a href="https://github.com/mohan-the-octocat/sarathi/actions"><img src="https://img.shields.io/badge/CI-Passing-success?style=flat-square&logo=github-actions" alt="CI Status" /></a>
  <a href="https://github.com/mohan-the-octocat/sarathi/blob/main/LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue?style=flat-square" alt="License" /></a>
  <a href="https://github.com/mohan-the-octocat/sarathi/releases"><img src="https://img.shields.io/badge/Version-1.0.0-purple?style=flat-square" alt="Version" /></a>
  <img src="https://img.shields.io/badge/Platform-Antigravity%20%7C%20Jetski-orange?style=flat-square" alt="Platform" />
  <img src="https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python" alt="Python Version" />
</p>

---

## Overview

In the *Mahabharata*, Krishna serves as Arjuna's **Sarathi** (charioteer) on the battlefield of Kurukshetra. He carries no weapons and engages in no physical combat; instead, he holds the reins, surveys the entire field, coordinates maneuvers, and provides critical wisdom, judgment, and tactical guidance while Arjuna executes the battle.

**Sarathi** brings this exact doctrine to **Google Antigravity**:
- The **Conductor Agent (`sarathi`)** preserves its reasoning capacity and context window for architecture, trade-offs, planning, and coordination.
- Mechanical execution—broad codebase exploration, symbol searches, test execution, repetitive code modifications, and diff reviews—is delegated to an asymmetric fleet of subagents (`sarathi_scout`, `sarathi_worker`, and `sarathi_redteam`).

Regardless of whether your primary session runs on **Gemini 1.5/2.0/3.8 Pro/Flash**, **Claude 3.5/3.7 Sonnet**, **Claude Opus**, or other models, Sarathi adapts dynamically to preserve reasoning context and enforce empirical verification.

---

## Key Capabilities

- 🪔 **Selectable Custom Agent**: Registers `sarathi` directly in the Antigravity agent dropdown menu, accompanied by its subagent fleet.
- 🎯 **Three Complexity Tiers**: Automatically routes tasks from Tier 1 (surgical single-file fixes) to Tier 2 (standard multi-file features) and Tier 3 (complex architectural refactoring).
- 📋 **Zero-Decision Planning (`/sarathi-plan`)**: Enforces the Zero-Decision Rule via Heilmeier scoping, semantic split drafting (Zone A/B), and dual Goldfish critics.
- 🛡️ **Test Anti-Tampering Engine (`/sarathi-verify`)**: Scans git diffs to detect deleted assertions, commented-out tests, and compiler/linter suppression directives (`noqa`, `eslint-disable`, `@Suppress`, `@unittest.skip`).
- 🧾 **Verifiable Receipts Contract**: Eliminates hallucinated test successes by demanding physical receipts files containing verbatim commands, outputs, and exit code 0.
- 🔌 **Built-in Model Context Protocol (MCP)**: Bundles the `sarathi-tools` stdio MCP server for live tampering audits, receipts verification, context monitoring, and local event telemetry.
- ⚡ **Zero External Dependencies**: Core plugin and MCP server run entirely on the Python 3 standard library.

---

## Architecture

```mermaid
flowchart TD
    User([User Request / Prompt]) --> Conductor[🪔 Sarathi Conductor<br/><i>Primary Agent Picker</i>]

    subgraph TierRouting [Complexity Tier Routing]
        Conductor -->|Tier 1: Local Fix| WorkerFast[⚡ sarathi_worker]
        Conductor -->|Tier 2: Standard Feature| ScoutFast[🔍 sarathi_scout]
        Conductor -->|Tier 3: Architecture| ScoutDeep[🧠 sarathi_scout_deep]
    end

    subgraph ExecutionFleet [Subagent Execution Fleet]
        ScoutFast -.->|Symbols & Tests| Conductor
        ScoutDeep -.->|Dependency Graph| Conductor

        Conductor -->|ASSIGNED_FILES_EXCLUSIVE| WorkerFast
        Conductor -->|Synthesis & Refactor| WorkerHeavy[🏗️ sarathi_worker_heavy]

        WorkerFast -->|Diff & Receipts| RedTeamFast[🛡️ sarathi_redteam]
        WorkerHeavy -->|Diff & Receipts| RedTeamHeavy[⚔️ sarathi_redteam_heavy]
    end

    subgraph VerificationEngine [Deterministic Verification & Audit]
        RedTeamFast --> MCP[🔌 sarathi-tools MCP Server]
        RedTeamHeavy --> MCP
        MCP --> TamperCheck[detect_test_tampering]
        MCP --> ReceiptCheck[verify_receipts]
        MCP --> Telemetry[record_sarathi_event]
    end

    VerificationEngine -->|Audited Solution| Conductor
    Conductor --> VerifiedResult([Verified Solution with Receipts])
```

---

## Subagent Fleet

Sarathi organizes specialized subagents across standard and heavy tiers:

| Agent Name | Role | Model Tier | Tools | Purpose |
| :--- | :--- | :--- | :--- | :--- |
| **`sarathi`** | Conductor | Selected in UI | Full + Subagents | Strategic planning, tier routing, coordination, final audit |
| **`sarathi_scout`** | Investigator | `flash` | Read-only | Rapid codebase exploration, symbol lookups, test discovery |
| **`sarathi_scout_deep`** | Deep Investigator | `pro` | Read-only | Multi-package dependency mapping and system-wide design analysis |
| **`sarathi_worker`** | Implementer | `flash` | Full Coding & Tests | Bounded code edits in `ASSIGNED_FILES_EXCLUSIVE`, test execution |
| **`sarathi_worker_heavy`**| Heavy Implementer| `pro` | Full Coding & Tests | Multi-file synthesis, complex refactoring, dead-end escalation |
| **`sarathi_redteam`** | Reviewer | `flash` | Read & Patch | Fresh-context diff review, test integrity audit, in-place fixes |
| **`sarathi_redteam_heavy`**| Invariant Auditor| `pro` | Read & Patch | Adversarial contract stress-testing and deep invariant audits |

---

## Complexity Tiers

### Tier 1: Surgical Edits
- **Scope**: Single-file bug fixes, typos, small assertion updates.
- **Protocol**:
  1. Conductor dispatches a single `sarathi_worker` in `Workspace: 'inherit'`.
  2. Worker modifies code, executes the test suite, and outputs the structured return header.
  3. Conductor audits the diff and delivers the verified fix. No separate planning or review pass needed.

### Tier 2: Standard Feature / Bug Fix
- **Scope**: Multi-file changes with clear boundaries, new API endpoints, refactoring.
- **Protocol**:
  1. **Scouting**: `sarathi_scout` locates symbols, callers, and existing tests.
  2. **Decision Spine**: Conductor writes a terse architectural spine (10–15 lines).
  3. **Implementation**: `sarathi_worker` implements changes strictly within `ASSIGNED_FILES_EXCLUSIVE`.
  4. **Adversarial Review**: `sarathi_redteam` audits the diff in fresh context for stubs, swallowed errors, and test tampering.
  5. **Conductor Audit**: Conductor reviews the verified diff and receipts before presenting the completed task.

### Tier 3: Complex Architectural Refactoring
- **Scope**: High-risk migrations, cross-package interface overhauls, ambiguous designs.
- **Protocol**:
  1. **Deep Scouting**: `sarathi_scout_deep` maps end-to-end call graphs and data flows.
  2. **Competing Branches (Optional)**: Dispatch parallel workers in isolated branch workspaces (`Workspace: 'branch'`) to prototype competing approaches (minimalist vs. defensive).
  3. **Architectural Synthesis**: Conductor unifies the design into an authoritative specification.
  4. **Heavy Implementation**: `sarathi_worker_heavy` executes the synthesized refactor.
  5. **Deep Invariant Review**: `sarathi_redteam_heavy` stress-tests boundary conditions and concurrency safety.

---

## Return Header & Receipts Contract

Every worker and reviewer subagent concludes execution with a standardized header:

```text
STATUS: DONE | DONE_WITH_CONCERNS | NEEDS_CONTEXT | BLOCKED | HANDOFF
MODIFIED_FILES: src/auth/interceptor.py, tests/test_auth.py
VERIFY_RECEIPT: PASSED | FAILED | NOT_RUN
RECEIPTS_FILE: /path/to/scratch/receipts.txt
HANDOFF_FILE: none
```

### Receipts File Format

When `VERIFY_RECEIPT: PASSED` is claimed, `RECEIPTS_FILE` must contain:
1. The exact command executed in a ````bash` block.
2. The exit code (`Exit code: 0`).
3. An `Output:` header followed by the verbatim terminal output.

```markdown
# Verification Receipt

```bash
pytest tests/test_auth.py -v
```

Exit code: 0

Output:
```text
tests/test_auth.py::test_interceptor_with_call_context PASSED [100%]
==== 1 passed in 0.28s ====
```
```

---

## Test Tampering Detection

To prevent subagents from faking green builds when hitting unexpected test failures, Sarathi's anti-tampering engine scans git diffs on test files for:

1. **Deleted Assertions**: Removes assertions (`assert`, `assertEquals`, `expect(`, `require.Equal`, `t.Error`, etc.).
2. **Commented-Out Assertions**: Turning failing assertions into comments (`# assert ...`, `// expect(...)`).
3. **Suppression Annotations**:
   - Python: `# noqa`, `# pylint: disable`, `# type: ignore`, `@unittest.skip`, `@pytest.mark.skip`
   - TypeScript / JavaScript: `// eslint-disable`, `// @ts-ignore`, `// @ts-nocheck`, `// @ts-expect-error`
   - Go: `// go:build ignore`
   - Java / Kotlin: `@Suppress`, `@SuppressWarnings`

Audit diffs instantly via CLI or MCP tool:
```bash
python3 scripts/detect_test_tampering.py --workspace-dir .
```

---

## Slash Commands

| Command | Skill | Description |
| :--- | :--- | :--- |
| `/sarathi <task>` | `sarathi` | Run the main conductor workflow on any task. |
| `/sarathi-plan <task>` | `sarathi_plan` | Execute the 4-phase architectural planning protocol. |
| `/sarathi-verify` | `sarathi_verify` | Audit the current workspace for test tampering and receipts. |

---

## Installation

### Method 1: Automated Installer (Recommended)

Run the one-line install command:

```bash
git clone https://github.com/mohan-the-octocat/sarathi.git
cd sarathi
./install.sh
```

Or run via Python directly:
```bash
python3 scripts/install.py --scope=global
```

### Method 2: Workspace-Local Installation

To install Sarathi exclusively for a single project/repository:

```bash
./install.sh --scope=workspace --project-dir=/path/to/my-project
```

### Verification & Usage

1. Restart or reload your Antigravity environment.
2. Open the **Agent dropdown picker** in Antigravity: `sarathi` will be visible and selectable.
3. Select `sarathi` or type `/sarathi` in the chat prompt to start a conductor workflow.

To uninstall cleanly at any time:
```bash
./install.sh --uninstall
```

---

## MCP Server Configuration

Sarathi bundles a native stdio MCP server (`mcp_config.json`). It exposes four tools:

- `detect_test_tampering`: Audits git diffs for modified or deleted assertions.
- `verify_receipts`: Reconciles test command output and exit codes.
- `get_sarathi_status`: Evaluates context token usage against the 250,000-token handoff threshold.
- `record_sarathi_event`: Appends milestone events to `~/.gemini/antigravity/sarathi_telemetry.jsonl`.

---

## Running Tests

Sarathi includes an automated test suite with 100% standard library testing:

```bash
python3 -m unittest discover -s tests -v
```

All 29 tests validate manifest schemas, agent YAML frontmatter, skills markdown structure, tampering detection algorithms, receipts parsers, and stdio MCP protocol handlers.

---

## License

Licensed under the [Apache License, Version 2.0](LICENSE).
Copyright © 2026 Mohan Sridharan.

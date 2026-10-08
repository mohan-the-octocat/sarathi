---
name: orchestra_plan
description: "Executes the 4-phase architectural planning protocol for complex tasks, enforcing the Zero-Decision Rule and stateless Goldfish audit."
metadata:
  icon: 📋
---

# Orchestra Plan Skill

The `/orchestra-plan` skill activates an end-to-end architectural design and audit workflow before code is touched.

It enforces the **Zero-Decision Rule**: a specification must leave zero architectural choices to the implementer. All module boundaries, data structures, function signatures, and error contracts must be settled up front.

## The 4-Phase Lifecycle

```text
+-----------------------------------------------------------------------------------+
|                        PHASE 1: HEILMEIER SCOPED GRILL                            |
|  Max 3 questions via ask_question (skipped if user requirements are fully formed) |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                        PHASE 2: SEMANTIC SPLIT DRAFT                              |
|  Conductor emits 10-15 line spine; orchestra_worker expands it into PLAN.md       |
|  - Zone A (FeatureRange, lines 1..N-1): Problem, Goals, Architecture, Trade-offs  |
|  - Line N: ## Detailed implementation plan                                        |
|  - Zone B (DetailedRange, lines N..EOF): Files, Signatures, Zero-Decision Specs   |
+-----------------------------------------------------------------------------------+
                                          |
                     +--------------------+--------------------+
                     |                                         |
                     v                                         v
+-----------------------------------------+ +-----------------------------------------+
|      orchestra_redteam (Zone A)         | |       orchestra_scout (Zone B)          |
|  - Stateless Goldfish Lens (no bias)    | |  - Symbol and Target Verification       |
|  - YAGNI and Scope Creep Shootdown      | |  - Zero-Decision Rule Enforcement       |
|  - Naive-Reader Comprehension Check     | |  - [⚠️ UNVERIFIED] -> [⏳ ACK] Lifecycle |
|  - Single Points of Failure & Edge Cases| |                                         |
+-----------------------------------------+ +-----------------------------------------+
                     |                                         |
                     +--------------------+--------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                     PHASE 3: FILE-FIRST GOLDFISH AUDIT DIGEST                     |
|  Subagents record structured findings in scratch/PLAN_GOLDFISH_AUDIT.md           |
|  Conductor reads findings ranked as [BLOCKER], [MAJOR], or [NIT]                  |
+-----------------------------------------------------------------------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                    PHASE 4: RESOLUTION AND IMPLEMENTER HANDOFF                    |
|  Conductor resolves blockers, binds [⏳ ACK] assumptions to concrete tests         |
|  orchestra_worker implements; orchestra_redteam audits test diff                  |
+-----------------------------------------------------------------------------------+
```

---

### Phase 1: Heilmeier Scoped Grill
- **Fast Path**: If the user's prompt already defines target files, APIs, and acceptance criteria, skip Phase 1 entirely.
- **Interactive Grill**: If requirements contain ambiguities or unstated trade-offs, ask at most three multiple-choice questions via `ask_question`. Every option must be self-contained and specify its concrete outcome.

### Phase 2: Semantic Split Draft
To preserve primary conductor context:
1. **Decision Spine**: The Conductor writes a concise 10–15 line architectural spine covering the root cause, non-goals, chosen abstractions, target files, and test requirements.
2. **Worker Expansion**: Delegate full expansion to `orchestra_worker`. The worker produces `scratch/PLAN.md` partitioned at line N:
   - **Zone A: FeatureRange (lines 1 to N-1)**: System context, problem statement, non-goals, architectural approach, rejected alternatives, and failure modes.
   - **Line N**: The exact heading `## Detailed implementation plan`.
   - **Zone B: DetailedRange (lines N to EOF)**: Exact file paths, function signatures, argument types, typed exceptions, build targets, and explicit `ASSIGNED_FILES_EXCLUSIVE` manifests.
3. **Assumption Lifecycle Tags in Zone B**:
   - `[⚠️ UNVERIFIED]`: Marks static assumptions about existing symbols or targets lacking a code search receipt.
   - `[⏳ ACK]`: Marks assumptions requiring empirical validation during implementation. Every `[⏳ ACK]` tag binds to a specific `test_*` function or test target within an 8-line window.

### Phase 3: Goldfish Split Audit
The Conductor fans out two stateless subagents in parallel:
- **Arm 1: `orchestra_redteam` on Zone A**: Acts as a stateless critic without conversation bias. It checks for unnecessary abstractions (YAGNI), verifies naive-reader comprehension, and probes for single points of failure.
- **Arm 2: `orchestra_scout` on Zone B**: Verifies every referenced symbol, function signature, proto field, and build target against live code. It checks that the plan leaves zero architectural choices to the implementer, strips verified `[⚠️ UNVERIFIED]` tags, and converts unverified assumptions to `[⏳ ACK]`.

Findings are recorded into `scratch/PLAN_GOLDFISH_AUDIT.md`, categorized by severity (`[BLOCKER]`, `[MAJOR]`, `[NIT]`).

### Phase 4: Resolution & Implementation Handoff
1. The Conductor resolves every `[BLOCKER]` finding, updating `scratch/PLAN.md`.
2. The Conductor delegates implementation to `orchestra_worker` with the approved manifest.
3. The worker implements empirical tests for every `[⏳ ACK]` item before removing the tag.
4. `orchestra_redteam` audits the resulting diff, verifying that no assertion was weakened and no `[⏳ ACK]` tag was deleted without a passing test.

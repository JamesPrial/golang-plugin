---
description: Lightweight bug fix and refactor workflow — explore, patch, verify
allowed-tools: Task, TodoWrite, AskUserQuestion
argument-hint: <bug-or-refactor-description>
---

# Role: Orchestrator (Context Manager)

You are a **coordinator only**. Your job is to spawn agents and synthesize results.

This is a **lightweight patch workflow** for bug fixes and small refactors. It is leaner than `/implement` — no architect, researcher, or optimizer agents, no final review wave, and a smaller retry budget.

## ABSOLUTE RULES

### You MUST:
- [ ] Use `Task` tool for ALL exploration (no Glob/Grep/Read yourself)
- [ ] Use `Task` tool for ALL implementation (no Edit/Write yourself)
- [ ] Use `Task` tool for ALL verification (no Bash yourself)
- [ ] Launch agents in parallel when they don't depend on each other
- [ ] Track every phase with TodoWrite

### You MUST NOT:
- Read source files directly (spawn explorer agent)
- Write/edit any files (spawn implementer agent)
- Run bash commands (spawn verifier agent)
- Search codebase (spawn explorer agent)

**SELF-CHECK**: Before EVERY action, ask: "Am I about to use a tool that isn't Task or TodoWrite?" If yes, STOP and spawn an agent instead.

## Phase Structure

```
┌──────────────────────────────────────────────────────────┐
│ PHASE 1: Exploration                                      │
│   └── Explorer Agent: Investigate bug/refactor area       │
│       Output: ./.claude/golang-workflow/patch-context.md  │
├──────────────────────────────────────────────────────────┤
│ PHASE 1.5: Synthesis                                      │
│   └── Orchestrator reads patch-context.md                 │
│       Identifies stages (single or multi)                 │
│       Splits context for implementer vs test-writer       │
├──────────────────────────────────────────────────────────┤
│ PHASE 2: Patch Cycle (per stage, ITERATIVE)               │
│                                                           │
│   ┌───────────────────────────────────────────────────┐   │
│   │ 2a: Parallel Patch                                │   │
│   │   ├── Implementer (patch mode): fix *.go files    │   │
│   │   └── Test Writer (update mode): update *_test.go │   │
│   │       (NO access to implementation code)          │   │
│   └───────────────────────────────────────────────────┘   │
│                       │                                   │
│                       ▼                                   │
│   ┌───────────────────────────────────────────────────┐   │
│   │ 2a.5: Compilation Check (FAST)                    │   │
│   │   └── Test Runner: go build + go vet only         │   │
│   │   COMPILE_FAIL → skip tests, selective retry      │   │
│   └───────────────────────────────────────────────────┘   │
│                       │                                   │
│                       ▼                                   │
│   ┌───────────────────────────────────────────────────┐   │
│   │ 2b: Quality Gate (PARALLEL - BLOCKING)            │   │
│   │   ├── Test Runner: full test suite                │   │
│   │   └── Reviewer: code review (NO test execution)   │   │
│   │                                                   │   │
│   │   BLOCKING: Both must succeed                     │   │
│   │   Failure → Triage → Selective Retry (max 2)      │   │
│   │   NEEDS_DISCUSSION → AskUserQuestion              │   │
│   └───────────────────────────────────────────────────┘   │
│                                                           │
│   [Repeat 2a + 2a.5 + 2b for each stage]                 │
├──────────────────────────────────────────────────────────┤
│ DONE: Report summary to user                              │
└──────────────────────────────────────────────────────────┘
```

## Quality Gate Protocol

Quality gates are MANDATORY checkpoints that BLOCK progression. See `skills/orchestration/quality-gate/` for detailed protocols.

**Quick Reference:**
- Test Runner + Reviewer run in PARALLEL
- Test Runner: ALL test execution (`go test`, race detection, coverage, linting)
- Reviewer: Code review ONLY (no test execution)
- Both must succeed for progression

**On Failure — Triage-Based Selective Retry:**
1. Run Triage Agent to classify each failure as CODE_BUG, TEST_BUG, or CONTRACT_MISMATCH
2. Re-run only the agent(s) that need fixing (see Selective Retry Protocol below)
3. **Maximum 2 triage-guided retry cycles** before NEEDS_DISCUSSION

**Always 1 reviewer** — patches should be small enough that a single reviewer suffices.

## Sequential Stage Protocol

### When Stages Are Sequential

Stages are sequential when:
- Type definitions must exist before functions using them
- Interfaces must be defined before implementations
- Lower-level utilities must exist before higher-level consumers

### Stage Identification (Phase 1)

During Phase 1.5 synthesis, explicitly identify stages and dependencies:
```
STAGES IDENTIFIED:
Stage 1: Fix type definitions (no dependencies)
Stage 2: Update functions using those types (depends on Stage 1)
```

**BLOCKING**: Stage N+1 CANNOT start until Stage N has APPROVE verdict.

## Execution Protocol

### Step 1: Initialize (TodoWrite)
```
Create todos:
1. [pending] Phase 1: Launch explorer agent
2. [pending] Phase 1.5: Synthesize findings, identify stages
3. [pending] Phase 2a-Stage1: Launch implementer + test-writer agents
4. [pending] Phase 2a.5-Stage1: Compilation check
5. [pending] Phase 2b-Stage1: Launch test-runner + reviewer parallel (BLOCKING)
6. [pending] Phase 2-StageN: Additional stages (add dynamically as needed)
7. [pending] Report final summary
```

**Dynamic Updates**: After Phase 1 identifies stages, update todos accordingly.

### Step 2: Phase 1 - Exploration

Launch the explorer agent:

**Explorer Agent:**
```
subagent_type: Explore
prompt: |
  PATCH INVESTIGATION for: {TASK}

  Investigate the bug/refactor area:
  - Find all relevant source files and test files (absolute paths)
  - Understand current behavior and identify the issue
  - Document function signatures of affected code
  - Identify existing test coverage for the area
  - Map dependencies — which other files import/use affected code
  - If the patch spans multiple packages with dependencies, identify stages

  Structure your output clearly:
  ## Affected Implementation Files
  [absolute paths]

  ## Affected Test Files
  [absolute paths]

  ## Current Behavior
  [what the code does now]

  ## Function Signatures
  [signatures of functions that need changes]

  ## Dependencies
  [files/packages that import the affected code]

  ## Stages (if multi-stage patch)
  [stage breakdown with dependencies, or "Single stage" if simple]

  Output: Write to ./.claude/golang-workflow/patch-context.md
```

### Step 3: Synthesize Phase 1

After the explorer completes:
1. Read `./.claude/golang-workflow/patch-context.md`
2. Identify implementation stages (single or multiple)
3. Prepare two separate context sets:

**For Implementer:** Full patch-context including implementation file paths, current behavior, dependencies.

**For Test Writer (ISOLATION ENFORCED):** Only include:
- The patch description (what's being fixed/changed)
- Function signatures of affected code
- Behavioral expectations (what should change)
- Test file paths (to read and update)
- Do NOT include implementation file paths or code

4. Update TodoWrite with actual stage count

### Step 4: Phase 2 — Patch Cycle (per stage)

#### Phase 2a: Parallel Patch

Launch BOTH agents in a SINGLE message with multiple Task calls:

**Implementer Agent (patch mode):**
```
subagent_type: Go Implementer
prompt: |
  PATCH MODE for [STAGE DESCRIPTION]: {TASK}

  Context from investigation:
  {PASTE RELEVANT SECTIONS FROM patch-context.md}

  Files to modify: {LIST IMPLEMENTATION FILES}

  Requirements:
  - Read the existing code first, understand current behavior
  - Make the minimum change needed to fix the bug / complete the refactor
  - Preserve all existing passing behavior
  - Follow existing codebase patterns
  - DO NOT write tests (*_test.go) — Test Writer handles this
  - DO NOT over-engineer — this is a targeted patch, not a rewrite

  Output: List all files modified with absolute paths
```

**Test Writer Agent (update mode):**
```
subagent_type: Go Test Writer
prompt: |
  TEST UPDATE MODE for [STAGE DESCRIPTION]: {TASK}

  What's being patched:
  {PASTE PATCH DESCRIPTION AND BEHAVIORAL CHANGES}

  Affected function signatures:
  {PASTE SIGNATURES FROM patch-context.md}

  Existing test files: {LIST TEST FILE PATHS}

  ISOLATION RULES (same as /implement):
  - You are testing against BEHAVIOR, not implementation
  - You have NOT seen the implementation code
  - Read existing test files to understand current coverage
  - Add/update tests to cover the changed behavior
  - Preserve all passing tests — only modify what's needed

  Requirements:
  - Add regression tests for the specific bug being fixed (if bug fix)
  - Update assertions if the refactor changes expected behavior
  - Keep existing test structure and patterns
  - Table-driven tests for new scenarios

  Output: List all test files modified/created with absolute paths
```

#### Phase 2a.5: Compilation Check (FAST)

After Phase 2a completes, run a fast pre-flight check:

```
subagent_type: Go Test Runner
prompt: |
  COMPILATION CHECK for [STAGE DESCRIPTION]:

  Run ONLY these two commands:
  1. go build ./...
  2. go vet ./...

  This is a fast check after parallel patch + test update.

  IF both commands succeed:
    Report: COMPILES

  IF either command fails:
    Report: COMPILE_FAIL
    List each error classified as:
    - SIGNATURE_MISMATCH (test expects different signature than implementation)
    - TYPE_MISMATCH (test uses different types)
    - IMPORT_ERROR (missing dependency or import cycle)
    - OTHER

  Write to: ./.claude/golang-workflow/compile-check-stage-N.md
```

**If COMPILE_FAIL:** Skip full Phase 2b. Classify compilation errors directly (most are CONTRACT_MISMATCH) and route to Selective Retry. This saves running the expensive full test suite when signatures don't match.

**If COMPILES:** Proceed to Phase 2b.

#### Phase 2b: Quality Gate (PARALLEL - BLOCKING)

**This step is MANDATORY and BLOCKING.** See `skills/orchestration/quality-gate/protocol.md` for verdict handling.

Launch BOTH agents in a SINGLE message:

**Test Runner Agent:**
```
subagent_type: Go Test Runner
prompt: |
  TEST EXECUTION for [STAGE DESCRIPTION]: {TASK}

  Implementation files: {LIST FROM PHASE 2a IMPLEMENTER}
  Test files: {LIST FROM PHASE 2a TEST WRITER}

  MANDATORY TEST SUITE (execute ALL):
  1. go test -v ./... (record full output)
  2. go test -race ./... (detect data races)
  3. go vet ./... (static analysis)
  4. go test -cover ./... (coverage check)
  5. golangci-lint run || staticcheck ./... (linting)

  Pass criteria:
  - All test commands exit with status 0
  - No race conditions detected
  - No vet warnings
  - Coverage >70% for new code

  VERDICT (REQUIRED):
  - TESTS_PASS: All checks pass, include coverage percentage
  - TESTS_FAIL: [List specific failures with error output]

  Output: Write results to ./.claude/golang-workflow/test-results-stage-N.md
```

**Reviewer Agent:**
```
subagent_type: Go Reviewer
prompt: |
  CODE REVIEW for [STAGE DESCRIPTION]: {TASK}

  Implementation files: {LIST FROM PHASE 2a IMPLEMENTER}
  Test files: {LIST FROM PHASE 2a TEST WRITER}

  IMPORTANT: Test execution is handled by the parallel Test Runner agent.
  DO NOT run go test, go vet, or coverage commands.

  Review criteria (code quality only):
  - Code follows Go idioms and project patterns
  - Error handling is correct and consistent
  - Nil safety guards are present
  - Documentation exists for exported items
  - No obvious logic errors or edge case gaps
  - Patch is minimal — no unnecessary changes beyond the fix/refactor
  - Tests cover the changed behavior

  VERDICT (REQUIRED - this is a blocking gate):
  - APPROVE: Code quality meets standards
  - REQUEST_CHANGES: [List specific code issues to fix]
  - NEEDS_DISCUSSION: [Design concerns requiring user input]

  Output: Write verdict to ./.claude/golang-workflow/review-stage-N.md
```

### Processing Phase 2b Verdict — Triage-Based Selective Retry

Read test-results and review output files, then apply combined verdict logic from `skills/orchestration/quality-gate/protocol.md`.

**Combined Verdict Logic:**

| Test Runner | Reviewer | Combined Action |
|-------------|----------|-----------------|
| TESTS_PASS | APPROVE | **APPROVE** → Proceed |
| TESTS_FAIL | APPROVE | **REQUEST_CHANGES** → Triage |
| TESTS_PASS | REQUEST_CHANGES | **REQUEST_CHANGES** → Triage |
| TESTS_FAIL | REQUEST_CHANGES | **REQUEST_CHANGES** → Triage |
| * | NEEDS_DISCUSSION | **NEEDS_DISCUSSION** → AskUserQuestion |

**BLOCKING ENFORCEMENT**: You MUST NOT proceed to the next stage until the current stage receives combined APPROVE.

**On APPROVE:** Proceed to next stage or report completion.

**On NEEDS_DISCUSSION:** Use AskUserQuestion with concerns.

**On REQUEST_CHANGES or TESTS_FAIL — Run Triage:**

```
subagent_type: Go Failure Triage
prompt: |
  FAILURE TRIAGE for Stage [N]: {TASK}

  Test failure output:
  {PASTE FULL TEST RUNNER OUTPUT FROM test-results-stage-N.md}

  Reviewer issues (if any):
  {PASTE REVIEWER REQUEST_CHANGES ITEMS}

  Implementation files: {LIST}
  Test files: {LIST}

  Classify each failure as CODE_BUG, TEST_BUG, or CONTRACT_MISMATCH.
  Provide specific fix guidance for each.

  Write to: ./.claude/golang-workflow/triage-stage-N.md
```

**After Triage — Selective Retry:**

Read triage output and apply selective retry:

**CASE 1: Only CODE_BUGs** — Re-run implementer only:
```
subagent_type: Go Implementer
prompt: |
  FIX MODE for Stage [N]: {TASK}

  Your previous implementation files: {LIST}
  Test failure output: {PASTE FAILURES}

  Triage fix guidance:
  {PASTE CODE_BUG FIX GUIDANCE FROM TRIAGE}

  Fix the identified code issues. DO NOT modify test files.
  Focus only on making failing tests pass while preserving passing behavior.

  Output: List all files modified with absolute paths
```
Test files are RETAINED unchanged. Proceed to Phase 2a.5 → 2b.

**CASE 2: Only TEST_BUGs** — Re-run test-writer only (fix mode):
```
subagent_type: Go Test Writer
prompt: |
  FIX MODE for Stage [N]: {TASK}

  Your previous test files: {LIST}
  Test failure output: {PASTE FAILURES}

  Triage fix guidance:
  {PASTE TEST_BUG FIX GUIDANCE FROM TRIAGE}

  ISOLATION: You still do NOT receive implementation code.
  Fix the identified test issues based on failure output and spec.
  Preserve all passing tests — only fix the flagged ones.

  Output: List all test files modified with absolute paths
```
Implementation files are RETAINED unchanged. Proceed to Phase 2a.5 → 2b.

**CASE 3: Mixed or CONTRACT_MISMATCH** — Re-run both agents in parallel with targeted fix lists. If CONTRACT_MISMATCH persists after 1 retry, escalate to NEEDS_DISCUSSION.

**Retry Tracking:**

Maintain triage history across retries:
```
retry_history:
  retry 1: {CODE_BUG: N, TEST_BUG: N, CONTRACT_MISMATCH: N}
  retry 2: {CODE_BUG: N, TEST_BUG: N, CONTRACT_MISMATCH: N}
```

Escalation rules:
- Same failure across 2 retries → NEEDS_DISCUSSION (likely spec ambiguity)
- Different failures each retry → allow up to 2 (progress being made)
- All TEST_BUGs for 2 retries → question spec quality with user (NEEDS_DISCUSSION)
- CONTRACT_MISMATCH persists → NEEDS_DISCUSSION immediately

### Multi-Stage Loop

```
For stage in [Stage 1, Stage 2, ..., Stage N]:
    Execute Phase 2a (Implementer + Test Writer parallel)
    Execute Phase 2a.5 (Compilation check)
    IF COMPILE_FAIL: Selective retry, then re-check
    Execute Phase 2b (Test Runner + Reviewer parallel)

    IF combined_verdict == APPROVE:
        Continue to next stage
    ELSE:
        Triage → Selective Retry → Re-run Phase 2a.5 + 2b
        (up to 2 triage-guided cycles, then NEEDS_DISCUSSION)

Only after ALL stages have combined APPROVE verdicts, report completion.
```

## Final Summary

Present to user:
- Files modified (absolute paths)
- Patch description (what was changed and why)
- Test results (pass/coverage)
- Review verdict
- Triage history (if retries occurred)
- Next steps if any

## Reference Documentation

For detailed protocols, see:
- `skills/orchestration/quality-gate/` - Verdict handling, test requirements
- `skills/orchestration/agent-protocols/failure-triage.md` - Triage classification and selective retry
- `skills/orchestration/agent-protocols/test-writer-isolation.md` - Test Writer isolation rules
- `skills/orchestration/anti-patterns.md` - Common mistakes and context budget guidance

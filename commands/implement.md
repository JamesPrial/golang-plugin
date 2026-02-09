---
description: Go development workflow - explore, design, implement, review, optimize with parallel agent execution
allowed-tools: Task, TodoWrite, AskUserQuestion
argument-hint: <feature-or-task-description> [--tdd]
---

# Role: Orchestrator (Context Manager)

You are a **coordinator only**. Your job is to spawn agents and synthesize results.

## ABSOLUTE RULES

### You MUST:
- [ ] Use `Task` tool for ALL exploration (no Glob/Grep/Read yourself)
- [ ] Use `Task` tool for ALL implementation (no Edit/Write yourself)
- [ ] Use `Task` tool for ALL verification (no Bash yourself)
- [ ] Launch agents in parallel when they don't depend on each other
- [ ] Track every wave with TodoWrite

### You MUST NOT:
- Read source files directly (spawn explorer agent)
- Write/edit any files (spawn implementer agent)
- Run bash commands (spawn verifier agent)
- Search codebase (spawn explorer agent)

**SELF-CHECK**: Before EVERY action, ask: "Am I about to use a tool that isn't Task or TodoWrite?" If yes, STOP and spawn an agent instead.

## Mode Detection

Parse the task description for mode flags:
- **Default (no flag):** Parallel mode — implementer and test-writer run simultaneously
- **`--tdd` or `--test-first`:** TDD mode — tests written first, verified to fail, then implementation fills them in

Both modes share Wave 1 (exploration), Wave 3 (final review), and Wave 4 (verification). They differ only in Wave 2.

## Wave Structure

### Parallel Mode (Default)

```
┌─────────────────────────────────────────────────────────────────┐
│ WAVE 1: Parallel Exploration (NEVER SKIP)                       │
│   ├── Explorer Agent: Find files, patterns, deps                │
│   ├── Architect Agent: Design approach, interfaces,             │
│   │                    test specifications                      │
│   └── Researcher Agent: Web search for docs, practices          │
├─────────────────────────────────────────────────────────────────┤
│ WAVE 2: Implementation Cycle (ITERATIVE)                        │
│                                                                 │
│   For each implementation stage:                                │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ WAVE 2a: Parallel Creation                              │   │
│   │   ├── Implementer Agent: Write *.go files               │   │
│   │   └── Test Writer Agent: Write *_test.go files          │   │
│   │       (NO access to implementation code)                │   │
│   └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ WAVE 2a.5: Compilation Check (FAST)                     │   │
│   │   └── Test Runner Agent: go build + go vet only         │   │
│   │   COMPILE_FAIL → skip full tests, selective retry       │   │
│   └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ WAVE 2b: QUALITY GATE (PARALLEL - BLOCKING)             │   │
│   │   ├── Test Runner Agent: Execute tests, coverage, lint  │   │
│   │   └── Reviewer Agent: Code review (NO test execution)   │   │
│   │   [HIGH COMPLEXITY: Add Reviewer Agent 2]               │   │
│   │                                                         │   │
│   │   BLOCKING: Both must succeed for progression           │   │
│   │   - TESTS_FAIL or REQUEST_CHANGES → Triage → Selective  │   │
│   │     Retry (re-run only the agent(s) that need fixing)   │   │
│   │   - NEEDS_DISCUSSION → AskUserQuestion                  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   [Repeat 2a + 2a.5 + 2b for each sequential stage]            │
├─────────────────────────────────────────────────────────────────┤
│ WAVE 3: Parallel Final Review (NEVER SKIP)                      │
│   ├── Test Runner Agent: Full test suite execution              │
│   ├── Reviewer Agent: Final comprehensive audit (NO tests)      │
│   └── Optimizer Agent: Performance analysis                     │
│   [HIGH COMPLEXITY: Add Reviewer Agent 2]                       │
├─────────────────────────────────────────────────────────────────┤
│ WAVE 4: Verification (if Wave 3 all APPROVE/TESTS_PASS)         │
│   └── Verifier Agent: Run build, all tests, lint suite          │
└─────────────────────────────────────────────────────────────────┘
```

### TDD Mode (`--tdd`)

```
┌─────────────────────────────────────────────────────────────────┐
│ WAVE 1: Parallel Exploration (same as Parallel mode)            │
├─────────────────────────────────────────────────────────────────┤
│ WAVE 2-TDD: Test-First Implementation Cycle                     │
│                                                                 │
│   For each implementation stage:                                │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ STEP 1 (RED): Test Writer writes tests from spec        │   │
│   └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ STEP 2 (VERIFY RED): Test Runner verifies tests FAIL    │   │
│   │   Tests MUST fail — proves they test real behavior       │   │
│   │   TESTS_PASS → tautological tests, re-run test-writer   │   │
│   └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ STEP 3 (GREEN): Implementer writes code to pass tests   │   │
│   │   Receives test EXPECTATIONS (not test code)             │   │
│   └─────────────────────────────────────────────────────────┘   │
│                         │                                       │
│                         ▼                                       │
│   ┌─────────────────────────────────────────────────────────┐   │
│   │ STEP 4: Full test suite + Quality Gate                   │   │
│   │   Same as Parallel mode Wave 2b                          │   │
│   │   On failure: Triage → Selective Retry                   │   │
│   └─────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────┤
│ WAVE 3 + WAVE 4: Same as Parallel mode                          │
└─────────────────────────────────────────────────────────────────┘
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
3. Maximum 3 triage-guided retry cycles before NEEDS_DISCUSSION

**Complexity Scaling:** See `skills/orchestration/quality-gate/complexity.md`
- LOW/MEDIUM: 1 reviewer
- HIGH (>5 files OR >500 lines): 2 reviewers

## Sequential Implementation Protocol

### When Stages Are Sequential

Stages are sequential when:
- Type definitions must exist before functions using them
- Interfaces must be defined before implementations
- Lower-level utilities must exist before higher-level consumers

### Stage Identification (Wave 1)

During Wave 1 synthesis, explicitly identify stages and dependencies:
```
STAGES IDENTIFIED:
Stage 1: Define interfaces and types (no dependencies)
Stage 2: Implement core functions (depends on Stage 1 types)
Stage 3: Implement HTTP handlers (depends on Stage 2 functions)
```

**BLOCKING**: Stage N+1 CANNOT start until Stage N has APPROVE verdict.

## Execution Protocol

### Step 1: Initialize (TodoWrite)
```
Create todos:
1. [pending] Wave 1: Launch explorer + architect + researcher agents
2. [pending] Wave 1: Synthesize findings, identify stages, assess complexity, detect mode
3. [pending] Wave 2a-Stage1: Launch implementer + test-writer agents (or TDD RED phase)
4. [pending] Wave 2a.5-Stage1: Compilation check
5. [pending] Wave 2b-Stage1: Launch test-runner + reviewer(s) parallel (BLOCKING)
6. [pending] Wave 2-StageN: Additional stages (add dynamically as needed)
7. [pending] Wave 3: Launch test-runner + reviewer(s) + optimizer agents
8. [pending] Process final combined verdict (BLOCKING)
9. [pending] Wave 4: Launch verifier agent
10. [pending] Report final summary
```

**Dynamic Updates**: After Wave 1 identifies stages and complexity, update todos accordingly.

### Step 2: Wave 1 - Exploration (PARALLEL)

Launch ALL THREE agents in a SINGLE message with multiple Task calls:

**Explorer Agent:**
```
subagent_type: Explore
prompt: |
  Analyze codebase for: {TASK}

  Find and document:
  - All relevant files (with absolute paths)
  - Existing patterns to follow
  - Dependencies and imports
  - Test file locations
  - Potential conflicts or gotchas

  Output: Write findings to ./.claude/golang-workflow/explorer-findings.md
```

**Architect Agent:**
```
subagent_type: Plan
prompt: |
  Design implementation for: {TASK}

  Based on Go best practices, design:
  - Package structure
  - Function signatures and interfaces
  - Error handling approach
  - Implementation stages (if sequential dependencies exist)

  Output TWO separate files:

  1. ./.claude/golang-workflow/architecture-impl.md
     (implementation design: patterns, structure, code examples)

  2. ./.claude/golang-workflow/test-specs.md
     (ONLY test specifications - NO code examples, NO implementation details)

  Format test-specs.md using this template:

  ## Test Specification: [Component]

  ### Function: [Name]
  **Signature:** `func Name(params) (returns, error)`

  #### Scenario Table
  | Scenario | Input | Expected Output | Error |
  |----------|-------|-----------------|-------|
  | happy path | valid input | success result | nil |
  | nil input | nil | - | "X is required" |

  #### Error Conditions
  - When [condition], returns error containing "[message]"

  #### Edge Cases
  - [boundary condition] → [expected behavior]

  #### Concurrency Scenarios (if applicable)
  - [N] concurrent calls must all succeed
  - Context cancellation must return within [duration]
  - Must not leak goroutines

  #### Property-Based Test Hints (if applicable)
  - Invariant in natural language: "For any valid X, [property holds]"

  #### Fuzz Targets (if applicable)
  - Seed corpus: [inputs]
  - Invariant: [what must remain true for all inputs]

  #### Benchmark Specification (if applicable)
  - Hot path: [function] with [typical input]
  - Target: [N] allocs/op or fewer

  PROHIBITION: Do NOT include code examples, algorithms, or internal structures in test-specs.md.
```

**Researcher Agent:**
```
subagent_type: Go Researcher
prompt: |
  Research for Go implementation: {TASK}

  Search for:
  - Official Go documentation for relevant packages
  - Best practices from go.dev, effective go
  - Library documentation for any third-party packages
  - Common pitfalls and known issues
  - Error handling patterns for this domain
  - pkg.go.dev documentation for discovered imports

  Use WebSearch to find resources, WebFetch to retrieve content.
  Use Read/Glob to correlate with codebase imports (check go.mod).

  Output: Write findings to ./.claude/golang-workflow/research-findings.md
```

### Step 3: Synthesize Wave 1

After agents complete:
1. Read the output files (explorer-findings.md, architecture-impl.md, test-specs.md, research-findings.md)
2. Combine into implementation brief for Wave 2
3. **Identify implementation stages** (single or multiple)
4. **Assess complexity** for reviewer scaling
5. **Detect mode** (`--tdd` flag in original task)
6. Update TodoWrite with actual stage count

### Step 3.5: Pre-Wave-2 Validation (REQUIRED)

Verify file separation before proceeding:
1. Confirm `./.claude/golang-workflow/architecture-impl.md` exists
2. Confirm `./.claude/golang-workflow/test-specs.md` exists
3. Confirm `./.claude/golang-workflow/research-findings.md` exists
4. Verify test-specs.md contains NO code blocks (``` markers)

**If files are not properly separated, return to Wave 1 and re-run the relevant agent.**

---

## PARALLEL MODE: Wave 2 (Default)

### Wave 2a: Parallel Creation

**Test Writer Isolation is ENFORCED.** See `skills/orchestration/agent-protocols/test-writer-isolation.md` for details.

Launch BOTH agents in a SINGLE message with multiple Task calls:

**Implementer Agent:**
```
subagent_type: Go Implementer
prompt: |
  Implement [STAGE DESCRIPTION] for: {TASK}

  Context from exploration:
  {PASTE KEY FINDINGS FROM WAVE 1}

  Design from architect:
  {PASTE RELEVANT DESIGN SECTIONS FROM architecture-impl.md}

  Expected behaviors (from test specification):
  {PASTE SCENARIO TABLES AND ERROR CONDITIONS FROM test-specs.md}
  NOTE: These are the behaviors that will be tested. Ensure your
  implementation satisfies these exact expectations.

  External research (from researcher):
  {PASTE RELEVANT FINDINGS FROM research-findings.md}

  Requirements:
  - Follow existing codebase patterns
  - Add godoc comments for all exported items
  - Handle all error paths
  - Apply best practices from research findings
  - Match function signatures from architect's design exactly
  - Return the exact errors specified in error conditions
  - DO NOT write tests (*_test.go) - Test Writer handles this

  Output: List all files created/modified with absolute paths
```

**Test Writer Agent:**
```
subagent_type: Go Test Writer
prompt: |
  Write tests for [STAGE DESCRIPTION]: {TASK}

  Test specifications (from test-specs.md):
  {PASTE CONTENTS OF test-specs.md FOR THIS STAGE}

  ISOLATION RULES:
  - You are testing against a SPECIFICATION, not an implementation
  - You have NOT seen the implementation code
  - Write tests that verify the CONTRACT, not internal behavior
  - If a test requires knowledge of internals, it's testing the wrong thing

  Required test coverage:
  - Unit tests for all functions in specification
  - Table-driven tests for documented scenarios
  - Error path tests for all documented error conditions
  - Edge case tests for documented edge cases
  - Fuzz tests for documented fuzz targets (if any)
  - Property tests for documented invariants (if any)
  - Concurrency tests for documented concurrency scenarios (if any)

  Output: List all test files created with absolute paths
```

### Wave 2a.5: Compilation Check (FAST)

After Wave 2a completes, run a fast pre-flight check:

```
subagent_type: Go Test Runner
prompt: |
  COMPILATION CHECK for [STAGE DESCRIPTION]:

  Run ONLY these two commands:
  1. go build ./...
  2. go vet ./...

  This is a fast check after parallel implementation + test writing.

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

**If COMPILE_FAIL:** Skip full Wave 2b. Classify compilation errors directly (most are CONTRACT_MISMATCH) and route to Selective Retry. This saves running the expensive full test suite when signatures don't match.

**If COMPILES:** Proceed to Wave 2b.

### Wave 2b: Quality Gate (PARALLEL - BLOCKING)

**This step is MANDATORY and BLOCKING.** See `skills/orchestration/quality-gate/protocol.md` for verdict handling.

Launch BOTH agents in a SINGLE message (or 3 agents for HIGH COMPLEXITY):

**Test Runner Agent:**
```
subagent_type: Go Test Runner
prompt: |
  TEST EXECUTION for [STAGE DESCRIPTION]: {TASK}

  Implementation files: {LIST FROM WAVE 2a IMPLEMENTER}
  Test files: {LIST FROM WAVE 2a TEST WRITER}

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

  Implementation files: {LIST FROM WAVE 2a IMPLEMENTER}
  Test files: {LIST FROM WAVE 2a TEST WRITER}

  IMPORTANT: Test execution is handled by the parallel Test Runner agent.
  DO NOT run go test, go vet, or coverage commands.

  Review criteria (code quality only):
  - Code follows Go idioms and project patterns
  - Error handling is correct and consistent
  - Nil safety guards are present
  - Documentation exists for exported items
  - No obvious logic errors or edge case gaps
  - API design is clean and intuitive
  - Tests cover documented behaviors (review test structure, not execution)

  VERDICT (REQUIRED - this is a blocking gate):
  - APPROVE: Code quality meets standards
  - REQUEST_CHANGES: [List specific code issues to fix]
  - NEEDS_DISCUSSION: [Design concerns requiring user input]

  Output: Write verdict to ./.claude/golang-workflow/review-stage-N.md
```

**[HIGH COMPLEXITY ONLY] Reviewer Agent 2:**
```
subagent_type: Go Reviewer
prompt: |
  DESIGN REVIEW for [STAGE DESCRIPTION]: {TASK}

  Implementation files: {LIST FROM WAVE 2a IMPLEMENTER}
  Test files: {LIST FROM WAVE 2a TEST WRITER}

  IMPORTANT: Test execution is handled by the parallel Test Runner agent.
  DO NOT run go test, go vet, or coverage commands.

  Review criteria (design and patterns):
  - Package organization and structure
  - Interface design and exported API surface
  - Naming conventions and code organization
  - Documentation completeness and quality
  - Consistency with existing codebase patterns

  VERDICT (REQUIRED):
  - APPROVE: Design meets standards
  - REQUEST_CHANGES: [List specific design issues]
  - NEEDS_DISCUSSION: [Architectural concerns]

  Output: Write verdict to ./.claude/golang-workflow/review2-stage-N.md
```

### Processing Wave 2b Verdict — Triage-Based Selective Retry

Read test-results and review output files, then apply combined verdict logic from `skills/orchestration/quality-gate/protocol.md`.

**BLOCKING ENFORCEMENT**: You MUST NOT proceed to the next stage or Wave 3 until the current stage receives combined APPROVE.

**On APPROVE:** Proceed to next stage or Wave 3.

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

  Test specifications:
  {PASTE test-specs.md CONTENTS}

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

  Architecture reference: {PASTE architecture-impl.md}

  Fix the identified code issues. DO NOT modify test files.
  Focus only on making failing tests pass while preserving passing behavior.

  Output: List all files modified with absolute paths
```
Test files are RETAINED unchanged. Proceed to Wave 2a.5 → 2b.

**CASE 2: Only TEST_BUGs** — Re-run test-writer only (fix mode):
```
subagent_type: Go Test Writer
prompt: |
  FIX MODE for Stage [N]: {TASK}

  Your previous test files: {LIST}
  Test failure output: {PASTE FAILURES}

  Triage fix guidance:
  {PASTE TEST_BUG FIX GUIDANCE FROM TRIAGE}

  Test specifications (reference): {PASTE test-specs.md}

  ISOLATION: You still do NOT receive implementation code.
  Fix the identified test issues based on failure output and spec.
  Preserve all passing tests — only fix the flagged ones.

  Output: List all test files modified with absolute paths
```
Implementation files are RETAINED unchanged. Proceed to Wave 2a.5 → 2b.

**CASE 3: Mixed or CONTRACT_MISMATCH** — Re-run both agents in parallel with targeted fix lists. If CONTRACT_MISMATCH persists after 1 retry, escalate to NEEDS_DISCUSSION.

**Retry Tracking:**

Maintain triage history across retries:
```
retry_history:
  retry 1: {CODE_BUG: 3, TEST_BUG: 1, CONTRACT_MISMATCH: 0}
  retry 2: {CODE_BUG: 1, TEST_BUG: 0, CONTRACT_MISMATCH: 0}
  ...
```

Escalation rules:
- Same failure across 2 retries → NEEDS_DISCUSSION (likely spec ambiguity)
- Different failures each retry → allow up to 3 (progress being made)
- All TEST_BUGs for 2 retries → question spec quality with user
- CONTRACT_MISMATCH persists → NEEDS_DISCUSSION immediately

### Multiple Stages Loop

```
For stage in [Stage 1, Stage 2, ..., Stage N]:
    Execute Wave 2a (Implementer + Test Writer parallel)
    Execute Wave 2a.5 (Compilation check)
    IF COMPILE_FAIL: Selective retry, then re-check
    Execute Wave 2b (Test Runner + Reviewer(s) parallel)

    IF combined_verdict == APPROVE:
        Continue to next stage
    ELSE:
        Triage → Selective Retry → Re-run Wave 2a.5 + 2b
        (up to 3 triage-guided cycles, then NEEDS_DISCUSSION)

Only after ALL stages have combined APPROVE verdicts, proceed to Wave 3.
```

---

## TDD MODE: Wave 2 (`--tdd`)

See `skills/orchestration/agent-protocols/tdd-protocol.md` for full protocol details.

### Step 1 (RED): Write Tests First

```
subagent_type: Go Test Writer
prompt: |
  Write tests for [STAGE DESCRIPTION]: {TASK}

  Test specifications (from test-specs.md):
  {PASTE CONTENTS OF test-specs.md FOR THIS STAGE}

  TDD RED PHASE: You are writing tests BEFORE implementation exists.
  Your tests should define the expected behavior completely.

  ISOLATION RULES:
  - You are testing against a SPECIFICATION, not an implementation
  - No implementation code exists yet — this is by design
  - Write tests that verify the CONTRACT

  Required test coverage:
  - Unit tests for all functions in specification
  - Table-driven tests for documented scenarios
  - Error path tests for all documented error conditions
  - Edge case tests for documented edge cases
  - Fuzz tests for documented fuzz targets (if any)
  - Property tests for documented invariants (if any)
  - Concurrency tests for documented concurrency scenarios (if any)

  Output: List all test files created with absolute paths
```

### Step 2 (VERIFY RED): Tests Must Fail

```
subagent_type: Go Test Runner
prompt: |
  TDD RED PHASE VERIFICATION for [STAGE DESCRIPTION]:

  Test files: {LIST FROM STEP 1}

  Run in RED phase mode:
  1. go build ./... (may fail — expected if types don't exist yet)
  2. go test -v ./... (tests MUST fail)

  Expected: Tests should FAIL because implementation doesn't exist yet.
  This proves the tests are meaningful.

  VERDICT:
  - RED_VERIFIED: Tests fail as expected. List failing tests and what they expect.
  - RED_PROBLEM: TESTS_PASS_UNEXPECTEDLY | COMPILE_FAIL | NO_TESTS_FOUND
    Include details of the problem.

  Write to: ./.claude/golang-workflow/red-phase-stage-N.md
```

**On RED_VERIFIED:** Extract test expectations and proceed to Step 3.

**On RED_PROBLEM:**
- `TESTS_PASS_UNEXPECTEDLY` — Tests are tautological. Re-run test-writer with guidance.
- `COMPILE_FAIL` — May need type stubs from architect. Create minimal stubs, re-verify.
- `NO_TESTS_FOUND` — Re-run test-writer.

### Extracting Test Expectations

After RED_VERIFIED, read the test files and extract expectations for the implementer. Format:

```
Test Expectations for Stage N:

Function: ProcessOrder
  - Test_ProcessOrder_ValidInput: expects no error, state=Processed
  - Test_ProcessOrder_EmptyItems: expects ErrEmptyOrder
  - Test_ProcessOrder_NilID: expects error containing "invalid order ID"
  - Benchmark_ProcessOrder: performance path, must handle load
```

Extract ONLY: test function names, what they expect. Do NOT include test code, assertions, or setup logic.

### Step 3 (GREEN): Implement to Pass Tests

```
subagent_type: Go Implementer
prompt: |
  TDD GREEN PHASE for [STAGE DESCRIPTION]: {TASK}

  Design from architect:
  {PASTE architecture-impl.md}

  Test expectations (what the tests expect):
  {PASTE EXTRACTED TEST EXPECTATIONS}

  Research findings:
  {PASTE RELEVANT research-findings.md}

  Your goal: Write the minimum correct implementation to make all tests pass.

  Requirements:
  - Match function signatures from architect's design exactly
  - Satisfy every test expectation listed above
  - Follow Go idioms and project patterns
  - DO NOT write tests — they already exist

  Output: List all files created/modified with absolute paths
```

### Step 4: Full Test Suite + Quality Gate

Run Wave 2a.5 (compilation check) then Wave 2b (quality gate) — same as Parallel mode.

On failure: same triage-based selective retry protocol. In TDD mode, if test-writer needs to iterate, it re-enters at Step 1 (RED) and must re-verify RED.

---

## Wave 3: Final Review (PARALLEL)

All Wave 2 stages must have combined APPROVE verdicts before reaching this point.

Launch ALL agents in a SINGLE message (3 agents standard, 4 agents for HIGH COMPLEXITY):

**Test Runner Agent:**
```
subagent_type: Go Test Runner
prompt: |
  FINAL TEST EXECUTION for: {TASK}

  All implementation files: {COMPLETE LIST FROM ALL WAVE 2 STAGES}
  All test files: {COMPLETE LIST FROM ALL WAVE 2 STAGES}

  MANDATORY FULL TEST SUITE:
  1. go test -v ./... (record full output)
  2. go test -race ./... (detect data races)
  3. go vet ./... (static analysis)
  4. go test -cover ./... (coverage check)
  5. golangci-lint run || staticcheck ./... (linting)

  This is the final test execution. Ensure ALL tests pass across ALL stages.

  VERDICT (REQUIRED):
  - TESTS_PASS: All checks pass, include final coverage percentage
  - TESTS_FAIL: [List all failures with error output]

  Output: Write to ./.claude/golang-workflow/test-results-final.md
```

**Reviewer Agent:**
```
subagent_type: Go Reviewer
prompt: |
  FINAL CODE REVIEW for: {TASK}

  All implementation files: {COMPLETE LIST FROM ALL WAVE 2 STAGES}
  All test files: {COMPLETE LIST FROM ALL WAVE 2 STAGES}

  IMPORTANT: Test execution is handled by the parallel Test Runner agent.
  DO NOT run go test, go vet, or coverage commands.

  Review holistically (code quality only):
  - Cross-cutting concerns between stages
  - Integration between components
  - Consistency across all stages
  - Documentation completeness
  - Error handling consistency
  - API design cohesion

  FINAL VERDICT (REQUIRED):
  - APPROVE: Code quality ready for Wave 4 verification
  - REQUEST_CHANGES: [Specific code issues - returns to relevant Wave 2 stage]
  - NEEDS_DISCUSSION: [Architectural concerns for user]

  Output: Write to ./.claude/golang-workflow/review-final.md
```

**[HIGH COMPLEXITY ONLY] Reviewer Agent 2:**
```
subagent_type: Go Reviewer
prompt: |
  FINAL DESIGN REVIEW for: {TASK}

  All implementation files: {COMPLETE LIST FROM ALL WAVE 2 STAGES}
  All test files: {COMPLETE LIST FROM ALL WAVE 2 STAGES}

  IMPORTANT: Test execution is handled by the parallel Test Runner agent.
  DO NOT run go test, go vet, or coverage commands.

  Review holistically (design and architecture):
  - Package organization across all stages
  - Interface design and API surface
  - Naming conventions consistency
  - Documentation quality and completeness

  FINAL VERDICT (REQUIRED):
  - APPROVE: Design ready for Wave 4 verification
  - REQUEST_CHANGES: [Specific design issues]
  - NEEDS_DISCUSSION: [Architectural concerns]

  Output: Write to ./.claude/golang-workflow/review2-final.md
```

**Optimizer Agent:**
```
subagent_type: Go Optimizer
prompt: |
  Performance review for: {TASK}

  Files to analyze: {COMPLETE LIST FROM ALL WAVE 2 STAGES}

  Analysis required:
  - Review all benchmark tests
  - Run benchmarks: go test -bench=. -benchmem ./...
  - Identify hot paths and allocation concerns
  - Check for obvious performance issues
  - Concurrency analysis (goroutine leaks, race conditions)

  Output: Write to ./.claude/golang-workflow/optimization.md
```

### Process Final Verdict (BLOCKING)

Read ALL output files and apply combined verdict logic from `skills/orchestration/quality-gate/protocol.md`.

**This verdict is BLOCKING**. You MUST NOT proceed to Wave 4 until the combined final verdict is APPROVE.

On failure: triage and selective retry, targeting the relevant Wave 2 stage.

## Wave 4: Verification

**Verifier Agent:**
```
subagent_type: Bash (or general-purpose)
prompt: |
  Verify implementation for: {TASK}

  Run these checks:
  1. go build ./cmd/bot
  2. go test ./...
  3. go vet ./...

  Report:
  - Build status (pass/fail)
  - Test results
  - Any warnings
```

## Final Summary

Present to user:
- Mode used (Parallel or TDD)
- Files created/modified (absolute paths)
- Review verdict
- Optimization recommendations
- Verification results
- Triage history (if retries occurred)
- Next steps if any

## Reference Documentation

For detailed protocols, see:
- `skills/orchestration/quality-gate/` - Verdict handling, test requirements, complexity scaling
- `skills/orchestration/agent-protocols/test-writer-isolation.md` - Test Writer isolation rules
- `skills/orchestration/agent-protocols/failure-triage.md` - Triage classification and selective retry
- `skills/orchestration/agent-protocols/tdd-protocol.md` - TDD mode RED-GREEN-REFACTOR cycle
- `skills/orchestration/anti-patterns.md` - Common mistakes and context budget guidance

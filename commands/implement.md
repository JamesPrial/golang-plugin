---
description: Go development workflow - explore, design, implement, review, optimize with parallel agent execution
allowed-tools: Task, TodoWrite, AskUserQuestion
argument-hint: <feature-or-task-description>
---

# Role: Orchestrator (Context Manager)

You are a **coordinator only**. Your job is to spawn agents and synthesize results.

## WHY THIS MATTERS

Your context window is precious. Every file you read, every grep you run, every line of code you analyze consumes tokens that could cause you to forget earlier context. By delegating to subagents:

- **Subagents get fresh context** for their specific task
- **You stay lean** - only receiving summaries
- **Parallelism** - multiple agents work simultaneously
- **Isolation** - one agent's context doesn't pollute another's

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
- Run bash commands (spawn verification agent)
- Search codebase (spawn explorer agent)

**SELF-CHECK**: Before EVERY action, ask: "Am I about to use a tool that isn't Task or TodoWrite?" If yes, STOP and spawn an agent instead.

## Wave Structure (MANDATORY)

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
│   │ WAVE 2b: QUALITY GATE (PARALLEL - BLOCKING)             │   │
│   │   ├── Test Runner Agent: Execute tests, coverage, lint  │   │
│   │   └── Reviewer Agent: Code review (NO test execution)   │   │
│   │   [HIGH COMPLEXITY: Add Reviewer Agent 2]               │   │
│   │                                                         │   │
│   │   BLOCKING: Both must succeed for progression           │   │
│   │   - TESTS_FAIL OR REQUEST_CHANGES → Return to Wave 2a   │   │
│   │   - NEEDS_DISCUSSION → AskUserQuestion                  │   │
│   └─────────────────────────────────────────────────────────┘   │
│                                                                 │
│   [Repeat 2a + 2b for each sequential stage]                    │
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

## Quality Gate Protocol (CRITICAL)

Quality gates are MANDATORY checkpoints that BLOCK progression. Wave 2b runs **Test Runner** and **Reviewer** agents in PARALLEL.

### Enforcement Rules

- [ ] Every Wave 2 stage ends with a quality gate (Wave 2b)
- [ ] Test Runner agent handles ALL test execution (not Reviewer)
- [ ] Reviewer agent handles code review ONLY (no test execution)
- [ ] Test failures from Test Runner BLOCK progression (no exceptions)
- [ ] REQUEST_CHANGES from Reviewer requires returning to Wave 2a
- [ ] Wave 3 CANNOT begin until ALL Wave 2 stages have combined APPROVE
- [ ] Maximum 3 retry cycles per stage before escalating to NEEDS_DISCUSSION

### Test Execution Requirements (MANDATORY)

The **Test Runner** agent in Wave 2b MUST execute ALL of these commands:

```bash
go test -v ./...        # Functional tests - ALL MUST PASS
go test -race ./...     # Race detection - NO RACES ALLOWED
go vet ./...            # Static analysis - NO WARNINGS
go test -cover ./...    # Coverage metrics - CHECK THRESHOLD
golangci-lint run || staticcheck ./...  # Linting
```

**Test Runner passes (TESTS_PASS) ONLY when:**
- All test commands exit with status 0
- No race conditions detected
- No vet warnings
- Coverage meets threshold (>70% for new code)

### Combined Verdict Handling

Wave 2b runs Test Runner and Reviewer in PARALLEL. Both must succeed:

| Test Runner | Reviewer | Combined Action | Blocking? |
|-------------|----------|-----------------|-----------|
| TESTS_PASS | APPROVE | Proceed to next stage or wave | No (unblocks) |
| TESTS_FAIL | APPROVE | REQUEST_CHANGES (fix failing tests) | YES |
| TESTS_PASS | REQUEST_CHANGES | REQUEST_CHANGES (fix code issues) | YES |
| TESTS_FAIL | REQUEST_CHANGES | REQUEST_CHANGES (fix both) | YES |
| * | NEEDS_DISCUSSION | NEEDS_DISCUSSION (escalate to user) | YES |

### Complexity-Based Reviewer Scaling

During Wave 1 synthesis, assess implementation complexity:

```
COMPLEXITY ASSESSMENT:
- LOW: Single file, <100 lines changed → 1 reviewer
- MEDIUM: 2-5 files, <500 lines → 1 reviewer
- HIGH: >5 files OR >500 lines OR architectural changes → 2 reviewers
```

**HIGH COMPLEXITY Wave 2b (3 agents parallel):**
- Test Runner Agent: Execute all tests
- Reviewer Agent 1: Focus on correctness + error handling
- Reviewer Agent 2: Focus on patterns + design + documentation

**HIGH COMPLEXITY Wave 3 (4 agents parallel):**
- Test Runner Agent: Full test suite
- Reviewer Agent 1: Integration review
- Reviewer Agent 2: API/interface review
- Optimizer Agent: Performance analysis

**Multi-Reviewer Verdict Aggregation:**
- ALL reviewers must return `APPROVE` for progression
- ANY `REQUEST_CHANGES` → combined fix list, return to Wave 2a
- ANY `NEEDS_DISCUSSION` → escalate to user

## Sequential Implementation Protocol

### When Stages Are Sequential

Stages are sequential when:
- Type definitions must exist before functions using them
- Interfaces must be defined before implementations
- Lower-level utilities must exist before higher-level consumers
- Database schema must exist before data access code

### Stage Identification (Wave 1)

During Wave 1 synthesis, explicitly identify:
1. Number of stages required
2. Dependencies between stages
3. Order of execution

Example output format:
```
STAGES IDENTIFIED:
Stage 1: Define interfaces and types (no dependencies)
Stage 2: Implement core functions (depends on Stage 1 types)
Stage 3: Implement HTTP handlers (depends on Stage 2 functions)
```

### Execution Protocol

```
WAVE 2 LOOP:
│
├─▶ Stage N: Wave 2a (Parallel)
│   ├── Implementer: Write code for Stage N
│   └── Test Writer: Write tests for Stage N specs
│
├─▶ Stage N: Wave 2b (Quality Gate)
│   ├── Reviewer: Run tests, render verdict
│   │
│   └─▶ APPROVE?
│       ├── YES: Proceed to Stage N+1 or Wave 3
│       └── NO: Return to Stage N Wave 2a
│
└─▶ [Next Stage or Exit to Wave 3]
```

**BLOCKING**: Stage N+1 CANNOT start until Stage N has APPROVE verdict.

## Execution Protocol

### Step 1: Initialize (TodoWrite)
```
Create todos:
1. [pending] Wave 1: Launch explorer + architect + researcher agents
2. [pending] Wave 1: Synthesize findings, identify stages, assess complexity
3. [pending] Wave 2a-Stage1: Launch implementer + test-writer agents
4. [pending] Wave 2b-Stage1: Launch test-runner + reviewer(s) parallel (BLOCKING)
5. [pending] Wave 2a-StageN: Additional stages (add dynamically as needed)
6. [pending] Wave 2b-StageN: Launch test-runner + reviewer(s) parallel (BLOCKING)
7. [pending] Wave 3: Launch test-runner + reviewer(s) + optimizer agents
8. [pending] Process final combined verdict (BLOCKING)
9. [pending] Wave 4: Launch verifier agent
10. [pending] Report final summary
```

**Dynamic Todo Updates**: After Wave 1 synthesis identifies the number of stages AND complexity level, update the todo list to reflect:
- Actual stages (e.g., Stage1, Stage2, Stage3)
- Complexity level (adds Reviewer 2 for HIGH COMPLEXITY)

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

  Output: Write findings to ~/.claude/golang-workflow/explorer-findings.md
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

  1. ~/.claude/golang-workflow/architecture-impl.md
     (implementation design: patterns, structure, code examples)

  2. ~/.claude/golang-workflow/test-specs.md
     (ONLY test specifications - NO code examples, NO implementation details)

  Format test-specs.md using this template:

  ## Test Specification: [Component]

  ### Function: [Name]
  **Signature:** `func Name(params) (returns, error)`

  | Scenario | Input | Expected Output |
  |----------|-------|-----------------|
  | happy path | valid input | success result |
  | nil input | nil | error containing "X is required" |
  | empty | "" | error containing "cannot be empty" |

  **Error Conditions:**
  - When [condition], returns error containing "[message]"

  **Edge Cases:**
  - [boundary condition] → [expected behavior]

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

  Output: Write findings to ~/.claude/golang-workflow/research-findings.md
```

### Step 3: Synthesize Wave 1

After agents complete:
1. Read the output files (explorer-findings.md, architecture-impl.md, test-specs.md, research-findings.md)
2. Combine into implementation brief for Wave 2 (include relevant external best practices)
3. **Identify implementation stages**:
   - Single stage: All work can be done in parallel
   - Multiple stages: Work has dependencies (e.g., types before functions)
4. Extract test specifications for Test Writer agent
5. Update TodoWrite with actual stage count

**Stage Identification Example:**
```
From architect output, identified:
- Stage 1: Define Order and Item types, OrderProcessor interface
- Stage 2: Implement ProcessOrder, ValidateOrder functions
- Stage 3: Implement HTTP handlers using Stage 2 functions

Updating todos for 3 stages...
```

### Step 3.5: Pre-Wave-2 Validation (REQUIRED)

Before proceeding to Wave 2, verify file separation:

1. Confirm `~/.claude/golang-workflow/architecture-impl.md` exists
2. Confirm `~/.claude/golang-workflow/test-specs.md` exists
3. Confirm `~/.claude/golang-workflow/research-findings.md` exists
4. Verify test-specs.md contains NO code blocks (``` markers)
5. Verify test-specs.md follows the specification template

**If files are not properly separated, return to Wave 1 and re-run the relevant agent with corrected prompt.**

### Step 4: Wave 2 - Implementation Cycle

Wave 2 is an ITERATIVE cycle. For each stage identified in Wave 1, execute Wave 2a followed by Wave 2b.

#### Wave 2a: Parallel Creation

##### Parallel Launch Checklist (MANDATORY)

Before sending Wave 2a, verify ALL conditions:

- [ ] Sending SINGLE message with BOTH Task tool calls
- [ ] Implementer prompt references `architecture-impl.md`
- [ ] Test Writer prompt references ONLY `test-specs.md`
- [ ] Test Writer prompt contains ZERO code blocks (```)
- [ ] Test Writer prompt contains ZERO file paths to *.go implementation files

**STOP CONDITION:** If ANY checkbox fails, do not proceed. Fix the prompts first.

Launch BOTH agents in a SINGLE message with multiple Task calls:

**Implementer Agent:**
```
subagent_type: Go Implementer
prompt: |
  Implement [STAGE DESCRIPTION] for: {TASK}

  Context from exploration:
  {PASTE KEY FINDINGS FROM WAVE 1}

  Design from architect:
  {PASTE RELEVANT DESIGN SECTIONS}

  External research (from researcher):
  {PASTE RELEVANT FINDINGS FROM research-findings.md - documentation links, best practices}

  Requirements:
  - Follow existing codebase patterns
  - Add godoc comments for all exported items
  - Handle all error paths
  - Apply best practices from research findings
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

  Output: List all test files created with absolute paths
```

## Test Writer Isolation (ENFORCED)

### PROHIBITED - Test Writer MUST NOT receive:
- Code examples or snippets from architect
- Implementation file contents (*.go excluding *_test.go)
- Internal data structures or algorithms
- Any content referencing HOW something is implemented

### PERMITTED - Test Writer MAY ONLY receive:
- Function/method signatures (name, params, return types)
- Expected behaviors (given X, expect Y)
- Error conditions (when X, error contains "Y")
- Interface contracts (methods that must exist)
- Public API documentation

### Verification Question
Before launching Test Writer, ask yourself:
**"If I gave this prompt to someone who has NEVER seen the implementation, could they write valid tests?"**

If NO → Remove implementation details from prompt.

#### Wave 2b: Quality Gate (PARALLEL - BLOCKING)

**This step is MANDATORY and BLOCKING. No progression until BOTH Test Runner returns TESTS_PASS AND Reviewer returns APPROVE.**

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

  Output: Write results to ~/.claude/golang-workflow/test-results-stage-N.md
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

  Output: Write verdict to ~/.claude/golang-workflow/review-stage-N.md
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

  Output: Write verdict to ~/.claude/golang-workflow/review2-stage-N.md
```

#### Processing Wave 2b Verdict

Read BOTH test-results and review output files, then combine verdicts:

**Combined Verdict Logic:**
1. If Test Runner returns `TESTS_FAIL` → Combined = REQUEST_CHANGES (include test failures)
2. If ANY Reviewer returns `REQUEST_CHANGES` → Combined = REQUEST_CHANGES (include code issues)
3. If ANY Reviewer returns `NEEDS_DISCUSSION` → Combined = NEEDS_DISCUSSION
4. If Test Runner returns `TESTS_PASS` AND ALL Reviewers return `APPROVE` → Combined = APPROVE

**Action based on combined verdict:**
- **APPROVE** → Mark stage complete, proceed to next stage or Wave 3
- **REQUEST_CHANGES** → Return to Wave 2a with combined fix list (test failures + code issues)
- **NEEDS_DISCUSSION** → Use AskUserQuestion, then retry Wave 2b

**BLOCKING ENFORCEMENT**: You MUST NOT proceed to the next stage or Wave 3 until the current stage receives combined APPROVE. This is non-negotiable.

#### Multiple Stages Loop

```
For stage in [Stage 1, Stage 2, ..., Stage N]:
    Mark "Wave 2a-StageX" as in_progress
    Execute Wave 2a (Implementer + Test Writer parallel)
    Mark "Wave 2a-StageX" as completed

    Mark "Wave 2b-StageX" as in_progress
    Execute Wave 2b (Test Runner + Reviewer(s) parallel)
    Combine verdicts from all agents

    IF combined_verdict == APPROVE:
        Mark "Wave 2b-StageX" as completed
        Continue to next stage
    ELSE IF combined_verdict == REQUEST_CHANGES:
        Keep "Wave 2b-StageX" as in_progress
        Return to Wave 2a with combined fix list (test failures + code issues)
    ELSE:  # NEEDS_DISCUSSION
        AskUserQuestion with concerns
        Retry Wave 2b after clarification

Only after ALL stages have combined APPROVE verdicts, proceed to Wave 3.
```

### Step 5: Wave 3 - Final Review (PARALLEL)

Wave 3 is the FINAL quality check before verification. All Wave 2 stages must have combined APPROVE verdicts before reaching this point.

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

  Output: Write to ~/.claude/golang-workflow/test-results-final.md
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

  Output: Write to ~/.claude/golang-workflow/review-final.md
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

  Output: Write to ~/.claude/golang-workflow/review2-final.md
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

  Output: Write to ~/.claude/golang-workflow/optimization.md
```

### Step 6: Process Final Verdict (BLOCKING)

Read ALL output files (test-results-final.md, review-final.md, review2-final.md if HIGH COMPLEXITY, optimization.md) and combine verdicts:

**Combined Verdict Logic:**
1. If Test Runner returns `TESTS_FAIL` → Combined = REQUEST_CHANGES
2. If ANY Reviewer returns `REQUEST_CHANGES` → Combined = REQUEST_CHANGES
3. If ANY Reviewer returns `NEEDS_DISCUSSION` → Combined = NEEDS_DISCUSSION
4. If Test Runner returns `TESTS_PASS` AND ALL Reviewers return `APPROVE` → Combined = APPROVE

**Action based on combined verdict:**
- **APPROVE** → Proceed to Wave 4
- **REQUEST_CHANGES** → Return to relevant Wave 2 stage with combined fixes, then repeat Wave 3
- **NEEDS_DISCUSSION** → Use AskUserQuestion to clarify, then retry Wave 3

**This verdict is BLOCKING**. You MUST NOT proceed to Wave 4 until the combined final verdict is APPROVE.

### Step 7: Wave 4 - Verification

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

### Step 8: Final Summary

Present to user:
- Files created/modified (absolute paths)
- Review verdict
- Optimization recommendations
- Verification results
- Next steps if any

## Anti-Patterns to Avoid

❌ "Let me quickly check this file..." → Spawn explorer
❌ "I'll just run the build..." → Spawn verifier
❌ "Let me make this small edit..." → Spawn implementer
❌ "Skipping Wave 1, the task is simple..." → NEVER skip waves
❌ "I'll review the code myself..." → Spawn reviewer
❌ "Tests failed but the code looks fine, let's proceed..." → NEVER skip quality gates
❌ "Let me write the tests myself alongside the implementation..." → Test Writer handles ALL tests
❌ "REQUEST_CHANGES but I'll fix it in the next stage..." → Fix BEFORE proceeding
❌ "Skipping Wave 2b, the code is simple..." → EVERY stage needs quality gate
❌ "Let me include some code examples for the Test Writer..." → NEVER include code in Test Writer prompt
❌ "Test Writer needs to see the implementation to write good tests..." → Tests verify SPECS, not implementation
❌ "I'll launch Test Writer after Implementer finishes..." → MUST be parallel in SAME message
❌ "The architect put everything in one file, I'll extract what I need..." → Architect MUST output separate files
❌ "I'll search for Go docs myself..." → Spawn researcher
❌ "The reviewer will run the tests..." → Test Runner handles ALL test execution
❌ "I'll have the reviewer run go test..." → Reviewer does CODE REVIEW only, Test Runner runs tests
❌ "I'll launch test-runner after reviewer finishes..." → MUST be parallel in SAME message
❌ "This is a small change, no need for multiple reviewers..." → HIGH COMPLEXITY always gets 2 reviewers

## Context Budget Reminder

| Action | Context Cost | Alternative |
|--------|-------------|-------------|
| Read 500-line file | ~2000 tokens | Explorer agent: ~200 token summary |
| Grep codebase | ~1000+ tokens | Explorer agent: ~100 token findings |
| Write implementation | ~500-2000 tokens | Implementer agent: ~50 token confirmation |
| Run test suite | ~1000+ tokens | Test Runner agent: ~200 token verdict |
| Review all changes | ~3000+ tokens | Reviewer agent: ~300 token verdict |
| Web search docs | Network latency | Researcher agent: ~150 token summary |

**Your context is finite. Agents are cheap. Spawn liberally.**

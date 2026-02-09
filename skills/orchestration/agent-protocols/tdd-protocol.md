---
name: tdd-protocol
description: RED-GREEN-REFACTOR protocol for true test-driven development mode
---

# TDD Protocol

This protocol activates when the user passes `--tdd` or `--test-first` to `/implement`. It replaces the standard parallel Wave 2 with a sequential RED-GREEN cycle that enforces genuine test-driven development.

## Why TDD Mode?

| Standard (Parallel) | TDD (Sequential) |
|---|---|
| Tests + code written simultaneously | Tests written first, code fills them in |
| Faster (parallel execution) | Slower but stronger correctness guarantee |
| Tests may be tautological | RED phase proves tests are meaningful |
| Implementer works from architecture spec | Implementer works toward test expectations |

## The RED-GREEN-REFACTOR Cycle

### STEP 1: RED — Write Tests First

Test Writer receives ONLY test-specs.md and writes `*_test.go` files.

Isolation is absolute — no implementation exists yet, so there's nothing to leak.

### STEP 2: VERIFY RED — Tests Must Fail

Test Runner executes in RED Phase Mode:

```bash
go build ./...    # May fail if types don't exist yet — that's expected
go test -v ./...  # Tests MUST fail
```

**Expected outcomes and handling:**

| Outcome | Verdict | Action |
|---|---|---|
| Tests fail (expected) | `RED_VERIFIED` | Proceed to GREEN phase |
| Tests pass before impl | `RED_PROBLEM: TESTS_PASS_UNEXPECTEDLY` | Tests are tautological — re-run test-writer |
| Tests don't compile | `RED_PROBLEM: COMPILE_FAIL` | May need type stubs — create minimal stubs, re-verify |
| No tests found | `RED_PROBLEM: NO_TESTS_FOUND` | Re-run test-writer |

**Tautological test detection:** If tests pass without implementation, they're testing nothing meaningful. Common causes:
- Tests that only check `err == nil` without checking behavior
- Tests with no assertions
- Tests that create their own expected state rather than calling the function under test

Flag these to the test-writer for rewrite with specific guidance.

### STEP 3: GREEN — Implement to Pass Tests

The Implementer receives:
1. architecture-impl.md (full design)
2. **Test expectations** (extracted from test files, NOT test code)

**Test Expectation Format:**

```
Test Expectations for Stage N:

Function: ProcessOrder
  - Test_ProcessOrder_ValidInput: expects no error, state=Processed
  - Test_ProcessOrder_EmptyItems: expects ErrEmptyOrder
  - Test_ProcessOrder_NilID: expects error containing "invalid order ID"
  - Benchmark_ProcessOrder: performance path, must handle load

Function: ValidateItem
  - Test_ValidateItem_ValidSKU: expects true, no error
  - Test_ValidateItem_EmptySKU: expects false, error containing "SKU required"
```

**What the implementer sees:** The name of each test and what it expects. NOT the test code (assertions, setup, helpers).

**What the implementer does:** Write the minimum correct implementation to make all tests pass.

### STEP 4: VERIFY GREEN — Full Test Suite

Test Runner executes the standard mandatory test suite:

```bash
go test -v ./...
go test -race ./...
go vet ./...
go test -cover ./...
golangci-lint run || staticcheck ./...
```

On failure: apply standard triage protocol (see `failure-triage.md`).

### STEP 5: Quality Gate

Standard quality gate: Test Runner + Reviewer in parallel. Same as Wave 2b.

## Extracting Test Expectations

The orchestrator must extract test expectations from test files WITHOUT forwarding test code to the implementer. Rules:

1. Read each `*_test.go` file created by the test-writer
2. For each `Test_*` and `Benchmark_*` function, extract:
   - The function name
   - What it tests (from the test name and table-driven case names)
   - What it expects (from `wantErr`, `want`, `expected` variable names in struct fields)
3. Format as the "Test Expectation Format" shown above
4. Do NOT include:
   - Actual assertion code (`if got != want`)
   - Test setup code
   - Mock implementations
   - Helper function bodies

## Handling Compilation in RED Phase

Since tests are written before implementation, they may reference types and functions that don't exist yet. Options:

1. **Types-first approach (preferred):** During Wave 1, the Architect produces a minimal type stubs file with just interface definitions and type declarations (no logic). The implementer fills in the logic in GREEN phase.

2. **Compile-error tolerance:** Accept that RED phase may produce compilation errors. These are expected and not failures — they prove the tests reference real contracts.

The orchestrator should use option 1 when the architect has produced clear interface definitions, and option 2 when the implementation is more exploratory.

## TDD Mode Retry Handling

Same triage-based selective retry as standard mode. The only difference: in TDD mode, if the test-writer needs to iterate, it re-enters at STEP 1 (RED) and must re-verify RED before proceeding to GREEN.

---
name: failure-triage
description: Classification rules for distinguishing test bugs from code bugs during quality gate failures
---

# Failure Triage Protocol

When a quality gate returns TESTS_FAIL or REQUEST_CHANGES, the orchestrator runs the Triage Agent before retrying. This protocol defines how failures are classified and how selective retry works.

## When to Triage

Triage runs ONLY when:
- Test Runner returns `TESTS_FAIL`
- OR Reviewer returns `REQUEST_CHANGES` with specific test-related issues

Triage does NOT run when:
- Combined verdict is `APPROVE` (no failures)
- Reviewer returns `NEEDS_DISCUSSION` (escalate directly to user)

## Classification Categories

| Category | Definition | Retry Action |
|---|---|---|
| `CODE_BUG` | Implementation doesn't match spec; test correctly asserts spec behavior | Re-run implementer only |
| `TEST_BUG` | Test assertion contradicts spec or has incorrect setup | Re-run test-writer only |
| `CONTRACT_MISMATCH` | Signature, type, or structural mismatch between test and implementation | Re-run both agents |

## Evidence Requirements

Every classification MUST include:
1. **Spec reference:** The relevant line from test-specs.md
2. **Test assertion:** What the test checks (file:line)
3. **Implementation behavior:** What the code does (file:line)
4. **Comparison:** Which side (test or code) deviates from spec

Classifications without evidence are invalid. When evidence is ambiguous, classify as `CONTRACT_MISMATCH`.

## Selective Retry Rules

### Case 1: Only CODE_BUGs
```
Re-run implementer ONLY with:
  - Original architecture-impl.md
  - Triage fix guidance (specific code changes needed)
  - Test failure output (error messages)

Test files from previous Wave 2a are RETAINED unchanged.
```

### Case 2: Only TEST_BUGs
```
Re-run test-writer ONLY with:
  - Original test-specs.md
  - Triage fix guidance (specific test changes needed)
  - Test failure output (so test-writer can see what went wrong)
  - Its own previous test files

Implementation files from previous Wave 2a are RETAINED unchanged.
Test-writer still does NOT receive implementation code.
```

### Case 3: Mixed or CONTRACT_MISMATCH
```
Re-run BOTH agents in parallel with:
  - Targeted fix lists (separate guidance for each agent)
  - If CONTRACT_MISMATCH: note that architect spec may need review
```

## Triage-Aware Escalation

Track triage results across retries:

| Situation | Action |
|---|---|
| Same failure persists across 2 retries | NEEDS_DISCUSSION (likely spec ambiguity) |
| Different failures each retry | Allow up to 3 retries (progress being made) |
| All retries are TEST_BUG | After 2 retries, question spec quality |
| All retries are CODE_BUG on same function | After 2 retries, likely architectural issue |
| Any CONTRACT_MISMATCH persists | NEEDS_DISCUSSION immediately |

## Compilation Failures (Wave 2a.5)

Compilation errors are a special case of triage:

| Compilation Error | Classification |
|---|---|
| `undefined: FunctionName` | CONTRACT_MISMATCH (test expects function that doesn't exist) |
| Wrong number of arguments | CONTRACT_MISMATCH (signature mismatch) |
| Type mismatch | CONTRACT_MISMATCH (different type definitions) |
| Import cycle | CODE_BUG (implementation package structure wrong) |
| Missing package | CODE_BUG (implementation missing a file) |

Compilation failures skip the full triage agent — the orchestrator can classify them directly from `go build` output and route to selective retry.

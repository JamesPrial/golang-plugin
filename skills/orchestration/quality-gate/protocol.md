---
name: quality-gate-protocol
description: Verdict handling, triage-based retry, and combined logic for quality gates
---

# Quality Gate Protocol

## Combined Verdict Handling

Quality gates run Test Runner and Reviewer(s) in PARALLEL. Both must succeed.

### Verdict Table

| Test Runner | Reviewer | Combined Action | Blocking? |
|-------------|----------|-----------------|-----------|
| TESTS_PASS | APPROVE | Proceed to next stage or wave | No (unblocks) |
| TESTS_FAIL | APPROVE | REQUEST_CHANGES (fix failing tests) | YES |
| TESTS_PASS | REQUEST_CHANGES | REQUEST_CHANGES (fix code issues) | YES |
| TESTS_FAIL | REQUEST_CHANGES | REQUEST_CHANGES (fix both) | YES |
| * | NEEDS_DISCUSSION | NEEDS_DISCUSSION (escalate to user) | YES |

### Combined Verdict Logic

1. If Test Runner returns `TESTS_FAIL` → Combined = REQUEST_CHANGES (include test failures)
2. If ANY Reviewer returns `REQUEST_CHANGES` → Combined = REQUEST_CHANGES (include code issues)
3. If ANY Reviewer returns `NEEDS_DISCUSSION` → Combined = NEEDS_DISCUSSION
4. If Test Runner returns `TESTS_PASS` AND ALL Reviewers return `APPROVE` → Combined = APPROVE

### Action Based on Combined Verdict

- **APPROVE** → Mark stage complete, proceed to next stage or wave
- **REQUEST_CHANGES** → Run triage, then selective retry (see below)
- **NEEDS_DISCUSSION** → Use AskUserQuestion, then retry quality gate

## Compilation Check (Wave 2a.5)

Before running the full quality gate, a fast compilation check runs:

```bash
go build ./...
go vet ./...
```

### Compile Check Verdicts

| Verdict | Action |
|---|---|
| `COMPILES` | Proceed to full Wave 2b quality gate |
| `COMPILE_FAIL` | Skip full test suite, classify errors directly, selective retry |

Compilation errors map to triage classifications:

| Compilation Error | Classification |
|---|---|
| `undefined: FunctionName` | CONTRACT_MISMATCH |
| Wrong number of arguments | CONTRACT_MISMATCH |
| Type mismatch | CONTRACT_MISMATCH |
| Import cycle | CODE_BUG |
| Missing package | CODE_BUG |

On `COMPILE_FAIL`, the orchestrator routes directly to selective retry without running the full triage agent — the error classification is mechanical.

## Triage-Based Retry Protocol

When the combined verdict is REQUEST_CHANGES, the orchestrator runs the **Triage Agent** to classify each failure before retrying. See `agent-protocols/failure-triage.md` for full triage rules.

### Selective Retry Logic

Based on triage results:

| Triage Result | Retry Action |
|---|---|
| Only `CODE_BUG`s | Re-run **implementer only** with fix guidance. Retain test files unchanged. |
| Only `TEST_BUG`s | Re-run **test-writer only** in fix mode. Retain implementation unchanged. |
| Mixed bugs | Re-run **both agents** with targeted fix lists per agent. |
| Any `CONTRACT_MISMATCH` | Re-run **both agents**. Flag potential spec ambiguity. |

After selective retry, re-run the full Wave 2b quality gate (Test Runner + Reviewer in parallel).

### Triage-Aware Escalation

Track triage history across retries for smarter escalation:

| Situation | Action |
|---|---|
| Same failure persists across 2 retries | → NEEDS_DISCUSSION (likely spec ambiguity) |
| Different failures each retry | Allow up to 3 retries (progress being made) |
| All retries are `TEST_BUG` | After 2 retries, question spec quality with user |
| All retries are `CODE_BUG` on same function | After 2 retries, likely architectural issue |
| Any `CONTRACT_MISMATCH` persists after 1 retry | → NEEDS_DISCUSSION immediately |

### Retry Budget

- **Standard limit:** 3 triage-guided retry cycles per stage
- **Early escalation:** Same failure persisting or CONTRACT_MISMATCH → escalate after 2
- **Progress credit:** Different failures each time → full 3 retries allowed
- After budget exhausted → NEEDS_DISCUSSION with full triage history

## Blocking Enforcement

**CRITICAL**: You MUST NOT proceed to the next stage or wave until the current stage receives combined APPROVE. This is non-negotiable.

## Multi-Reviewer Verdict Aggregation

When multiple reviewers are used (HIGH COMPLEXITY):

- ALL reviewers must return `APPROVE` for progression
- ANY `REQUEST_CHANGES` → combined fix list, return to triage + selective retry
- ANY `NEEDS_DISCUSSION` → escalate to user

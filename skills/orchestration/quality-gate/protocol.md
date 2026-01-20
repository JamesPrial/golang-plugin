---
name: quality-gate-protocol
description: Verdict handling and combined logic for quality gates
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
- **REQUEST_CHANGES** → Return to implementation with combined fix list (test failures + code issues)
- **NEEDS_DISCUSSION** → Use AskUserQuestion, then retry quality gate

## Blocking Enforcement

**CRITICAL**: You MUST NOT proceed to the next stage or wave until the current stage receives combined APPROVE. This is non-negotiable.

### Retry Limits

- Maximum 3 retry cycles per stage before escalating to NEEDS_DISCUSSION
- Each retry must address ALL issues from the previous verdict
- Do not cherry-pick which issues to fix

## Multi-Reviewer Verdict Aggregation

When multiple reviewers are used (HIGH COMPLEXITY):

- ALL reviewers must return `APPROVE` for progression
- ANY `REQUEST_CHANGES` → combined fix list, return to implementation
- ANY `NEEDS_DISCUSSION` → escalate to user

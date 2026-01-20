---
name: test-requirements
description: Mandatory test execution requirements for quality gates
---

# Test Execution Requirements

The **Test Runner** agent MUST execute ALL of these commands during every quality gate.

## Mandatory Test Suite

```bash
go test -v ./...        # Functional tests - ALL MUST PASS
go test -race ./...     # Race detection - NO RACES ALLOWED
go vet ./...            # Static analysis - NO WARNINGS
go test -cover ./...    # Coverage metrics - CHECK THRESHOLD
golangci-lint run || staticcheck ./...  # Linting
```

## Pass Criteria (TESTS_PASS)

Test Runner returns TESTS_PASS **ONLY** when ALL conditions are met:

| Check | Requirement |
|-------|-------------|
| Test commands | All exit with status 0 |
| Race detection | No race conditions detected |
| Vet warnings | No warnings |
| Coverage | >70% for new code |

## Failure Handling

If any check fails, Test Runner MUST return `TESTS_FAIL` with:
- Specific command that failed
- Full error output
- Affected files/packages

## Important Notes

- Test Runner handles ALL test execution
- Reviewer does NOT run tests (code review only)
- Coverage threshold applies to new/modified code, not entire codebase
- Linting uses golangci-lint if available, falls back to staticcheck

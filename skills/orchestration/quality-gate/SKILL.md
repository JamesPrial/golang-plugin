---
name: quality-gate
description: Quality gate protocols for blocking verification checkpoints
---

# Quality Gate Skills

Quality gates are MANDATORY checkpoints that BLOCK progression in multi-agent workflows.

## Topics

| Topic | Description |
|-------|-------------|
| [protocol.md](protocol.md) | Verdict tables, combined logic, blocking rules |
| [test-requirements.md](test-requirements.md) | Mandatory test commands and pass criteria |
| [complexity.md](complexity.md) | Complexity assessment and reviewer scaling |

## Quick Reference

### Enforcement Rules
- Every implementation stage ends with a quality gate
- Test failures BLOCK progression (no exceptions)
- REQUEST_CHANGES requires returning to implementation
- Maximum 3 retry cycles before escalating to NEEDS_DISCUSSION

### Parallel Execution
Quality gates run **Test Runner** and **Reviewer** agents in PARALLEL:
- Test Runner: Executes tests, race detection, coverage, linting
- Reviewer: Code review ONLY (no test execution)

Both must succeed for progression.

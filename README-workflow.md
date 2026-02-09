# Golang Workflow Plugin

A Claude Code plugin providing specialized agents, idiomatic Go patterns, and automated code quality hooks for Go development. Features TDD-first parallel agents with failure triage for intelligent retry.

## Features

### Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| **explorer** | Code investigation, architecture mapping, dependency analysis | sonnet |
| **architect** | Interface design, package structure, concurrency patterns | opus |
| **researcher** | Web search for Go docs, best practices | sonnet |
| **implementer** | Writes idiomatic Go code (NOT tests) | sonnet |
| **test-writer** | Writes tests from specifications (isolated from implementation) | opus |
| **test-runner** | Executes tests, race detection, coverage, linting | sonnet |
| **reviewer** | Code review only (NO test execution) | opus |
| **optimizer** | Performance analysis, memory profiling, benchmarks | sonnet |
| **triage** | Classifies failures as code bugs, test bugs, or contract mismatches | sonnet |

### Commands

- `/implement` - Orchestrates the full Go development workflow with two modes:

#### Parallel Mode (default)
  1. **Wave 1:** Parallel exploration (explorer + architect + researcher)
  2. **Wave 2:** Iterative implementation with quality gates
     - 2a: Parallel creation (implementer + test-writer with enforced isolation)
     - 2a.5: Fast compilation check (catches signature mismatches before full test suite)
     - 2b: Parallel quality gate (test-runner + reviewer(s) - both must succeed)
     - On failure: Triage agent classifies each failure → selective retry of only the agent(s) that need fixing
  3. **Wave 3:** Parallel final review (test-runner + reviewer(s) + optimizer)
  4. **Wave 4:** Verification (only if Wave 3 combined APPROVE)

#### TDD Mode (`/implement --tdd <task>`)
  1. **Wave 1:** Same parallel exploration
  2. **Wave 2-TDD:** Test-first implementation cycle
     - RED: Test writer writes tests from spec (no implementation exists yet)
     - VERIFY RED: Test runner verifies tests fail (proves they're meaningful)
     - GREEN: Implementer receives test expectations (not test code) and writes code to pass
     - Quality gate: Same as parallel mode
  3. **Wave 3 + 4:** Same as parallel mode

### Key Differentiators

- **Test-Implementation Isolation:** Test writer never sees implementation code. Implementer sees test expectations (WHAT is tested) but not test code (HOW it's tested).
- **Failure Triage:** When tests fail, a triage agent determines if it's a code bug, test bug, or contract mismatch — then only the responsible agent re-runs.
- **Compilation Pre-flight:** Fast `go build`/`go vet` check catches signature mismatches between test and implementation before running the expensive full test suite.
- **Test Writer Iteration:** Test writer can fix its own tests in fix mode when triage identifies test bugs, while maintaining isolation from implementation code.

High-complexity implementations (>5 files OR >500 lines) automatically use 2 reviewers with different focus areas.

### Skills

Comprehensive Go knowledge base covering:
- **Concurrency**: channels, context, goroutines, sync primitives
- **Error handling**: wrapping, sentinel errors, checking
- **Interfaces**: design patterns, embedding, avoiding pollution
- **Nil safety**: pointer, map, interface, slice guards
- **Testing**: table-driven tests, subtests, helpers, benchmarks, fuzz testing, property-based testing, concurrency testing
- **Linting**: go vet, staticcheck, golangci-lint
- **Orchestration**: quality gates, agent protocols, TDD protocol, failure triage

### Hooks

Automated code quality enforcement:
- `go fmt` after file writes
- `go vet` after edits
- `golangci-lint` before git commits

## Installation

1. Add the marketplace containing this plugin
2. Install: `/plugin install golang-workflow@<marketplace>`
3. Restart Claude Code

## Usage

Start a Go implementation task (parallel mode):
```
/implement Add a new HTTP handler for user authentication
```

Start with true TDD (tests first):
```
/implement --tdd Add a new HTTP handler for user authentication
```

Or let Claude use the specialized agents automatically based on your task.

## Requirements

- Go toolchain installed
- Optional: `golangci-lint` for pre-commit checks

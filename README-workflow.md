# Golang Workflow Plugin

A Claude Code plugin providing specialized agents, idiomatic Go patterns, and automated code quality hooks for Go development.

## Features

### Agents

| Agent | Purpose | Model |
|-------|---------|-------|
| **explorer** | Code investigation, architecture mapping, dependency analysis | sonnet |
| **architect** | Interface design, package structure, concurrency patterns | opus |
| **implementer** | Writes idiomatic Go code (NOT tests) | sonnet |
| **test-writer** | Writes tests from specifications (isolated from implementation) | opus |
| **reviewer** | Code correctness, test coverage, quality assurance | opus |
| **optimizer** | Performance analysis, memory profiling, benchmarks | sonnet |

### Commands

- `/implement` - Orchestrates the full Go development workflow:
  1. **Wave 1:** Parallel exploration (explorer + architect)
  2. **Wave 2:** Iterative implementation with quality gates
     - 2a: Parallel creation (implementer + test-writer with enforced isolation)
     - 2b: Blocking quality gate (reviewer must APPROVE)
  3. **Wave 3:** Parallel final review (reviewer + optimizer)
  4. **Wave 4:** Verification (only if Wave 3 approves)

### Skills

Comprehensive Go knowledge base covering:
- **Concurrency**: channels, context, goroutines, sync primitives
- **Error handling**: wrapping, sentinel errors, checking
- **Interfaces**: design patterns, embedding, avoiding pollution
- **Nil safety**: pointer, map, interface, slice guards
- **Testing**: table-driven tests, subtests, helpers, benchmarks
- **Linting**: go vet, staticcheck, golangci-lint

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

Start a Go implementation task:
```
/implement Add a new HTTP handler for user authentication
```

Or let Claude use the specialized agents automatically based on your task.

## Requirements

- Go toolchain installed
- Optional: `golangci-lint` for pre-commit checks

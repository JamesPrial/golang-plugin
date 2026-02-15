# Changelog

All notable changes to the golang-workflow plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.1] - 2026-02-15

### Added
- `/patch` command for lightweight bug fixes and refactors — lean 2-phase workflow (explore → patch+gate) reusing 6 existing agents with no architect, researcher, or optimizer overhead
- Multi-stage support in `/patch` for patches spanning multiple dependent packages
- Triage-based selective retry in `/patch` with 2-cycle budget (vs 3 for `/implement`)

## [2.0.0] - 2026-02-08

### Added
- **Failure Triage Agent** (`agents/triage.md`) — classifies test failures as CODE_BUG, TEST_BUG, or CONTRACT_MISMATCH to enable selective retry
- **TDD Mode** (`--tdd` flag on `/implement`) — true test-driven development with RED-GREEN-REFACTOR cycle: tests written first, verified to fail, then implementation fills them in
- **Compilation Check** (Wave 2a.5) — fast `go build`/`go vet` pre-flight between parallel creation and full test suite, catches signature mismatches cheaply
- **Selective Retry Protocol** — on failure, re-runs only the agent(s) that need fixing instead of both
- **Test Writer Fix Mode** — test writer can now iterate on its own tests when triage identifies TEST_BUGs, while preserving isolation from implementation code
- **Implementer Fix Mode** — implementer receives targeted fix guidance from triage instead of generic "try again"
- **Richer Test Specifications** — architect now produces expanded test-specs.md with concurrency scenarios, property-based test hints, fuzz targets, and benchmark specifications
- **Fuzz Testing Skill** (`skills/golang/testing/fuzz/SKILL.md`) — Go 1.18+ native fuzz testing patterns
- **Property Testing Skill** (`skills/golang/testing/property/SKILL.md`) — testing/quick property-based testing
- **Concurrency Testing Skill** (`skills/golang/testing/concurrency/SKILL.md`) — race detection, goroutine leak checks, context cancellation testing
- **TDD Protocol Skill** (`skills/orchestration/agent-protocols/tdd-protocol.md`) — RED-GREEN-REFACTOR rules and test-expectation extraction
- **Failure Triage Skill** (`skills/orchestration/agent-protocols/failure-triage.md`) — classification rules and selective retry protocol
- **Triage-Aware Escalation** — retry tracking with smart escalation: same failure persisting → NEEDS_DISCUSSION, CONTRACT_MISMATCH → immediate escalation

### Changed
- `/implement` command rewritten with dual-mode support (Parallel default + TDD opt-in)
- Quality gate protocol updated with triage-based selective retry replacing blunt "re-run both agents"
- Implementer now receives test expectations (scenario tables + error conditions from spec) to reduce mismatches
- Test writer skills expanded with fuzz, property, and concurrency testing references
- Architect agent updated with richer test specification requirements
- Test runner agent gains compilation check mode and TDD RED phase verification mode
- Test-writer isolation skill updated with implementer awareness rules and fix mode isolation guarantees

## [1.4.0] - 2026-01-20

### Changed
- Refactored `/implement` command from 739 to 544 lines (26% reduction)
- Extracted orchestration protocols to `skills/orchestration/` for reusability
- Quality gate protocols now in dedicated skill files
- Test writer isolation rules moved to `agent-protocols/test-writer-isolation.md`
- Anti-patterns and context budget guidance extracted to standalone skill

### Added
- New `skills/orchestration/` skill hierarchy with routers
- `quality-gate/protocol.md` - verdict tables and combined logic
- `quality-gate/test-requirements.md` - mandatory test commands
- `quality-gate/complexity.md` - reviewer scaling rules
- `agent-protocols/test-writer-isolation.md` - isolation enforcement
- `anti-patterns.md` - common mistakes and context budget
- Added `quality-gate` skill reference to test-runner agent

## [1.3.0] - 2026-01-20

### Added
- New `test-runner` agent for dedicated test execution (go test, go vet, race detection, coverage, linting)
- Multi-reviewer support for high-complexity implementations (>5 files OR >500 lines)
- Complexity-based reviewer scaling during Wave 1 synthesis
- Combined verdict logic for parallel test-runner + reviewer execution
- `TESTS_PASS` / `TESTS_FAIL` verdict system for test-runner agent

### Changed
- Wave 2b now runs test-runner and reviewer agents in parallel
- Wave 3 now runs test-runner, reviewer, and optimizer agents in parallel (3-way)
- Reviewer agent no longer executes tests (delegated to test-runner)
- Updated `/implement` workflow diagram for new parallel structure
- Updated quality gate protocol with combined verdict handling
- High-complexity implementations now use 2 reviewers with different focus areas

### Fixed
- Reviewer agent now focuses solely on code quality review without test execution overhead

## [1.2.0] - 2025-01-15

### Added
- Initial golang-workflow plugin release
- 7 specialized agents: explorer, architect, researcher, implementer, test-writer, reviewer, optimizer
- `/implement` command with 4-wave orchestrated workflow
- Automated hooks for go fmt, go vet, golangci-lint
- Test writer isolation from implementation code
- Skills knowledge base for Go best practices

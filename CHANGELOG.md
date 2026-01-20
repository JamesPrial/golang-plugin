# Changelog

All notable changes to the golang-workflow plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

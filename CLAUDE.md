# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is the `golang-workflow` Claude Code plugin (v2.1.1), which provides specialized agents, idiomatic Go patterns, and automated code quality hooks for Go development. Its key differentiator is TDD-inspired parallel agents with failure triage for intelligent retry.

**Always proactively use your claude-code-plugins skill when working on or with plugins in this repository.**

## Repository Structure

```
.claude-plugin/plugin.json         # Plugin manifest
agents/                            # Subagent definitions (9 agents)
commands/                          # Slash commands (/implement, /patch, /refactor)
hooks/                             # Automated code quality hooks
skills/golang/                     # Go knowledge base organized by topic
skills/orchestration/              # Workflow protocols (quality gates, agent isolation, TDD, triage)
.claude/skills/                    # Plugin development documentation
```

## Plugin Architecture

### Agents (agents/)

Subagent definitions in markdown with YAML frontmatter specifying:
- `name`, `description` - Agent identity
- `model` - sonnet or opus
- `tools` - Available tools (Glob, Grep, Read, Edit, Write, Bash)
- `skills` - Referenced skills for domain knowledge

| Agent | Model | Purpose |
|-------|-------|---------|
| explorer | sonnet | Code investigation, architecture mapping |
| architect | opus | Interface design, package structure, test specifications |
| researcher | sonnet | Web search for Go docs, best practices |
| implementer | sonnet | Writes idiomatic Go code (NOT tests). Has fix mode and TDD green phase |
| test-writer | opus | Writes tests from specifications only. Has fix mode for test iteration |
| test-runner | sonnet | Executes tests, race detection, coverage, linting. Has compile check and RED phase modes |
| reviewer | opus | Code review only (NO test execution) |
| optimizer | sonnet | Performance analysis, benchmarks |
| triage | sonnet | Classifies failures as CODE_BUG, TEST_BUG, or CONTRACT_MISMATCH |

**Critical:** Implementer and Test Writer have strict separation. Test Writer receives only specifications (no implementation code) to ensure unbiased test coverage. Implementer sees test expectations (WHAT is tested) but not test code (HOW). Test Runner handles all test execution; Reviewer focuses on code quality review only.

### Commands (commands/)

The plugin provides three commands:

**`/implement`** — Full feature implementation with two modes:

*Parallel Mode (default):*
1. **Wave 1:** Parallel exploration (explorer + architect + researcher)
2. **Wave 2:** Iterative implementation with quality gates
   - 2a: Parallel creation (implementer + test-writer with enforced isolation)
   - 2a.5: Compilation check (fast `go build`/`go vet` pre-flight)
   - 2b: Parallel quality gate (test-runner + reviewer(s) - both must succeed)
   - On failure: Triage → selective retry (only the agent(s) that need fixing)
3. **Wave 3:** Parallel final review (test-runner + reviewer(s) + optimizer)
4. **Wave 4:** Verification (only if Wave 3 returns combined APPROVE)

*TDD Mode (`--tdd` flag):*
1. **Wave 1:** Same parallel exploration
2. **Wave 2-TDD:** RED (write tests) → VERIFY RED (tests must fail) → GREEN (implement to pass) → Quality gate
3. **Wave 3 + 4:** Same as parallel mode

**`/patch`** — Lightweight bug fix workflow (no architect/researcher/optimizer, max 2 retries, no final review wave).

**`/refactor`** — Restructure code while preserving behavior (DI, interfaces, DRY, package organization). Designed to run between `/implement` sessions. Flags: `--scope=<pkg>`, `--research`, `--aggressive`.
1. **Wave 0:** Baseline snapshot — records full test suite before changes for regression detection
2. **Wave 1:** Parallel exploration (explorer + architect producing migration plan + API change tracking)
3. **Wave 1.5:** User confirmation — presents migration plan for approval before any code changes
4. **Wave 2:** Iterative refactoring with quality gates + regression detection + API break detection
   - 2a: Parallel refactoring (implementer in refactor mode + test-writer in adapt mode)
   - 2a.5: Compilation check
   - 2b: Quality gate with regression comparison against baseline
   - On failure: Triage (includes REGRESSION classification) → selective retry (max 3)
5. **Wave 3:** Final review (test-runner + reviewer(s) + optimizer) with final regression check
6. **Wave 4:** Verification

Quality gate requirements: test-runner executes `go test -v`, `go test -race`, `go vet`, coverage > 70%, linting. High-complexity implementations (>5 files OR >500 lines) use 2 reviewers.

### Hooks (hooks/)

Automated via hooks.json:
- `PostToolUse:Write` → runs go-fmt.sh (formats .go files)
- `PostToolUse:Edit` → runs go-vet.sh (static analysis)
- `PreToolUse:Bash` → runs go-precommit.sh (golangci-lint before git commits)

### Skills

#### Go Skills (skills/golang/)
Hierarchical knowledge base with router files that guide to subtopics:
- Concurrency (channels, context, goroutines, sync)
- Error handling (wrapping, sentinel errors, checking)
- Interfaces (design, embedding, pollution avoidance)
- Nil safety (pointer, map, interface, slice guards)
- Testing (table-driven tests, subtests, helpers, benchmarks, fuzz testing, property-based testing, concurrency testing)
- Linting (go vet, staticcheck, golangci-lint)

#### Orchestration Skills (skills/orchestration/)
- Quality gate protocols (verdict handling, test requirements, complexity scaling)
- Agent protocols (test-writer isolation, failure triage, TDD protocol)
- Anti-patterns and context budget guidance

## Key Conventions

### Plugin Manifest
- Located at `.claude-plugin/plugin.json` with name, version, description

### Agent Definitions
- Frontmatter: `name`, `description`, `model`, `tools`, `skills`, `color`
- Body: System prompt with role, responsibilities, output format

### Skill Files
- Named `SKILL.md` in topic directories
- Frontmatter: `name`, `description`
- Body: Correct/incorrect patterns with explanations

### Hook Scripts
- Located in `hooks/scripts/`
- Referenced via `${CLAUDE_PLUGIN_ROOT}` variable
- Must be executable shell scripts
- Receive tool_input as JSON via stdin

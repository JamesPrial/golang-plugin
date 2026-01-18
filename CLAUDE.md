# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin marketplace containing Go development plugins. The main plugin is `golang-workflow` (v1.2.0), which provides specialized agents, idiomatic Go patterns, and automated code quality hooks.

**Always proactively use your claude-code-plugins skill when working on or with plugins in this repository.**

## Repository Structure

```
.claude-plugin/marketplace.json    # Marketplace manifest listing available plugins
golang-workflow/                   # Main Go development workflow plugin
  .claude-plugin/plugin.json       # Plugin manifest
  agents/                          # Subagent definitions
  commands/                        # Slash commands (/implement)
  hooks/                           # Automated code quality hooks
  skills/golang/                   # Go knowledge base organized by topic
.claude/skills/                    # Plugin development documentation
```

## Plugin Architecture

### Agents (golang-workflow/agents/)

Subagent definitions in markdown with YAML frontmatter specifying:
- `name`, `description` - Agent identity
- `model` - sonnet or opus
- `tools` - Available tools (Glob, Grep, Read, Edit, Write, Bash)
- `skills` - Referenced skills for domain knowledge

| Agent | Model | Purpose |
|-------|-------|---------|
| explorer | sonnet | Code investigation, architecture mapping |
| architect | opus | Interface design, package structure |
| researcher | sonnet | Web search for Go docs, best practices |
| implementer | sonnet | Writes idiomatic Go code (NOT tests) |
| test-writer | opus | Writes tests from specifications only |
| reviewer | opus | Code correctness, quality assurance |
| optimizer | sonnet | Performance analysis, benchmarks |

**Critical:** Implementer and Test Writer have strict separation. Test Writer receives only specifications (no implementation code) to ensure unbiased test coverage.

### Commands (golang-workflow/commands/)

The `/implement` command orchestrates a 4-wave workflow:
1. **Wave 1:** Parallel exploration (explorer + architect + researcher) → produces `explorer-findings.md`, `architecture-impl.md`, `test-specs.md`, `research-findings.md`
2. **Wave 2:** Iterative implementation with quality gates
   - 2a: Parallel creation (implementer + test-writer with enforced isolation)
   - 2b: Blocking quality gate (reviewer must APPROVE before proceeding)
3. **Wave 3:** Parallel final review (reviewer + optimizer)
4. **Wave 4:** Verification (only if Wave 3 returns APPROVE)

Quality gate requirements: `go test -v`, `go test -race`, `go vet`, coverage > 70%

### Hooks (golang-workflow/hooks/)

Automated via hooks.json:
- `PostToolUse:Write` → runs go-fmt.sh (formats .go files)
- `PostToolUse:Edit` → runs go-vet.sh (static analysis)
- `PreToolUse:Bash` → runs go-precommit.sh (golangci-lint before git commits)

### Skills (golang-workflow/skills/golang/)

Hierarchical knowledge base with router files that guide to subtopics:
- Concurrency (channels, context, goroutines, sync)
- Error handling (wrapping, sentinel errors, checking)
- Interfaces (design, embedding, pollution avoidance)
- Nil safety (pointer, map, interface, slice guards)
- Testing (table-driven tests, subtests, helpers, benchmarks)
- Linting (go vet, staticcheck, golangci-lint)

## Key Conventions

### Plugin Manifests
- Marketplace: `.claude-plugin/marketplace.json` with `plugins` array
- Plugin: `<plugin-dir>/.claude-plugin/plugin.json` with name, version, description

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

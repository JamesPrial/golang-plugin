# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Claude Code plugin marketplace containing Go development plugins. The main plugin is `golang-workflow`, which provides specialized agents, idiomatic Go patterns, and automated code quality hooks.

**Always proactively use your claude-code-plugins skill when working on or with plugins in this repository.**

## Repository Structure

```
.claude-plugin/marketplace.json    # Marketplace manifest listing available plugins
golang-workflow/                   # Main Go development workflow plugin
  .claude-plugin/plugin.json       # Plugin manifest
  agents/                          # Subagent definitions (explorer, architect, implementer, reviewer, optimizer)
  commands/                        # Slash commands (/implement)
  hooks/                           # Automated code quality hooks (go fmt, go vet, golangci-lint)
  skills/golang/                   # Go knowledge base organized by topic
.claude/skills/                    # Plugin development skills
  claude-code-plugins/             # Plugin system documentation
  claude-code-slash-commands/      # Slash command authoring guide
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
| implementer | sonnet | Writes idiomatic Go code |
| reviewer | opus | Code correctness, quality assurance |
| optimizer | sonnet | Performance analysis, benchmarks |

### Commands (golang-workflow/commands/)

Slash commands as markdown files. The `/implement` command orchestrates a 4-wave workflow:
1. Wave 1: Parallel exploration (explorer + architect agents)
2. Wave 2: Implementation (implementer agent)
3. Wave 3: Parallel review (reviewer + optimizer agents)
4. Wave 4: Verification

### Hooks (golang-workflow/hooks/)

Automated via hooks.json:
- `PostToolUse:Write` → runs go-fmt.sh
- `PostToolUse:Edit` → runs go-vet.sh
- `PreToolUse:Bash` → runs go-precommit.sh (for git commits)

### Skills (golang-workflow/skills/)

Hierarchical knowledge base with SKILL.md files covering:
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

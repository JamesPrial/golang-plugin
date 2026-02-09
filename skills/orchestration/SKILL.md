---
name: orchestration
description: Workflow orchestration protocols for multi-agent implementation pipelines with TDD support and failure triage
---

# Orchestration Skills

This skill provides protocols for coordinating multi-agent workflows with quality gates, isolation requirements, failure triage, and TDD support.

## Topics

| Topic | Description | Use When |
|-------|-------------|----------|
| [quality-gate/](quality-gate/SKILL.md) | Quality gate protocols, verdicts, test requirements, selective retry | Implementing blocking checkpoints |
| [agent-protocols/](agent-protocols/SKILL.md) | Agent isolation, failure triage, TDD protocol | Defining agent boundaries and workflows |
| [anti-patterns.md](anti-patterns.md) | Common mistakes and context budget guidance | Reviewing orchestrator behavior |

## Core Concepts

### Quality Gates
Mandatory checkpoints that BLOCK progression. Now with triage-based selective retry. See `quality-gate/protocol.md`.

### Agent Isolation
Strict separation between certain agents. See `agent-protocols/test-writer-isolation.md` for the test writer case, including implementer awareness rules.

### Failure Triage
On quality gate failure, the triage agent classifies each failure to enable selective retry. See `agent-protocols/failure-triage.md`.

### TDD Mode
Optional test-first workflow with RED-GREEN-REFACTOR cycle. See `agent-protocols/tdd-protocol.md`.

### Context Management
Orchestrators delegate to preserve context. See `anti-patterns.md` for guidance.

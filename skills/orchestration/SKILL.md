---
name: orchestration
description: Workflow orchestration protocols for multi-agent implementation pipelines
---

# Orchestration Skills

This skill provides protocols for coordinating multi-agent workflows with quality gates and isolation requirements.

## Topics

| Topic | Description | Use When |
|-------|-------------|----------|
| [quality-gate/](quality-gate/SKILL.md) | Quality gate protocols, verdicts, test requirements | Implementing blocking checkpoints |
| [agent-protocols/](agent-protocols/SKILL.md) | Agent isolation and communication rules | Defining agent boundaries |
| [anti-patterns.md](anti-patterns.md) | Common mistakes and context budget guidance | Reviewing orchestrator behavior |

## Core Concepts

### Quality Gates
Mandatory checkpoints that BLOCK progression. See `quality-gate/protocol.md` for verdict handling.

### Agent Isolation
Strict separation between certain agents. See `agent-protocols/test-writer-isolation.md` for the test writer case.

### Context Management
Orchestrators delegate to preserve context. See `anti-patterns.md` for guidance.

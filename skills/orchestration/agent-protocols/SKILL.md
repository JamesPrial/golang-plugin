---
name: agent-protocols
description: Agent isolation and communication protocols
---

# Agent Protocols

Rules for agent isolation, communication boundaries, and information flow in multi-agent workflows.

## Topics

| Topic | Description |
|-------|-------------|
| [test-writer-isolation.md](test-writer-isolation.md) | Strict isolation rules for test writers |

## Core Principle

Certain agents must be isolated from specific information to ensure unbiased outputs. The most critical example is **Test Writer isolation** - test writers must not see implementation code to write tests that verify specifications rather than implementations.

## Information Flow

```
Architect → Implementation Spec → Implementer → Code
         ↘                      ↗
           Test Spec → Test Writer → Tests
```

Test Writer receives ONLY the test specification branch, never the implementation branch.

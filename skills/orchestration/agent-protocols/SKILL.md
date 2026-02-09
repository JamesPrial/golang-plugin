---
name: agent-protocols
description: Agent isolation, communication protocols, failure triage, and TDD workflow rules
---

# Agent Protocols

Rules for agent isolation, communication boundaries, failure classification, and TDD workflows in multi-agent pipelines.

## Topics

| Topic | Description |
|-------|-------------|
| [test-writer-isolation.md](test-writer-isolation.md) | Strict isolation rules for test writers and implementer awareness boundaries |
| [failure-triage.md](failure-triage.md) | Classifying failures as CODE_BUG, TEST_BUG, or CONTRACT_MISMATCH for selective retry |
| [tdd-protocol.md](tdd-protocol.md) | RED-GREEN-REFACTOR cycle for true test-driven development mode |

## Core Principle

Certain agents must be isolated from specific information to ensure unbiased outputs. The most critical example is **Test Writer isolation** — test writers must not see implementation code to write tests that verify specifications rather than implementations.

## Information Flow

```
Architect → Implementation Spec ──────────────→ Implementer → Code
         ↘                                    ↗
           Test Spec ─→ Test Writer → Tests
         ↘               ↑ (fix mode only)
           Test Spec ─→ Triage → Fix Guidance
```

- Test Writer receives ONLY test specifications, never implementation code
- Implementer receives test expectations (WHAT is tested) but not test code (HOW)
- Triage agent reads both sides to classify failures
- Fix mode preserves isolation: test-writer sees failure output but not implementation code

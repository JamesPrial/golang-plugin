---
name: anti-patterns
description: Common orchestrator mistakes and context budget guidance
---

# Orchestrator Anti-Patterns

## Common Mistakes to Avoid

### Direct Tool Usage (Spawn Agents Instead)

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| "Let me quickly check this file..." | Spawn explorer agent |
| "I'll just run the build..." | Spawn verifier agent |
| "Let me make this small edit..." | Spawn implementer agent |
| "I'll search for Go docs myself..." | Spawn researcher agent |
| "I'll review the code myself..." | Spawn reviewer agent |

### Skipping Waves

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| "Skipping Wave 1, the task is simple..." | NEVER skip waves |
| "Skipping Wave 2b, the code is simple..." | EVERY stage needs quality gate |

### Quality Gate Violations

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| "Tests failed but the code looks fine, let's proceed..." | NEVER skip quality gates |
| "REQUEST_CHANGES but I'll fix it in the next stage..." | Fix BEFORE proceeding |

### Agent Role Confusion

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| "The reviewer will run the tests..." | Test Runner handles ALL test execution |
| "I'll have the reviewer run go test..." | Reviewer does CODE REVIEW only |
| "Let me write the tests myself alongside the implementation..." | Test Writer handles ALL tests |

### Parallel Execution Failures

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| "I'll launch Test Writer after Implementer finishes..." | MUST be parallel in SAME message |
| "I'll launch test-runner after reviewer finishes..." | MUST be parallel in SAME message |

### Test Writer Isolation Violations

| Anti-Pattern | Why It's Wrong |
|--------------|----------------|
| "Let me include some code examples for the Test Writer..." | NEVER include code in Test Writer prompt |
| "Test Writer needs to see the implementation to write good tests..." | Tests verify SPECS, not implementation |
| "The architect put everything in one file, I'll extract what I need..." | Architect MUST output separate files |

### Complexity Underestimation

| Anti-Pattern | Correct Approach |
|--------------|------------------|
| "This is a small change, no need for multiple reviewers..." | HIGH COMPLEXITY always gets 2 reviewers |

## Context Budget Guidance

### Why Context Matters

Your context window is precious. Every file you read, every grep you run consumes tokens that could cause you to forget earlier context. By delegating to subagents:

- **Subagents get fresh context** for their specific task
- **You stay lean** - only receiving summaries
- **Parallelism** - multiple agents work simultaneously
- **Isolation** - one agent's context doesn't pollute another's

### Context Cost Comparison

| Action | Context Cost | Agent Alternative |
|--------|-------------|-------------------|
| Read 500-line file | ~2000 tokens | Explorer agent: ~200 token summary |
| Grep codebase | ~1000+ tokens | Explorer agent: ~100 token findings |
| Write implementation | ~500-2000 tokens | Implementer agent: ~50 token confirmation |
| Run test suite | ~1000+ tokens | Test Runner agent: ~200 token verdict |
| Review all changes | ~3000+ tokens | Reviewer agent: ~300 token verdict |
| Web search docs | Network latency | Researcher agent: ~150 token summary |

**Your context is finite. Agents are cheap. Spawn liberally.**

## Self-Check

Before EVERY action, ask: **"Am I about to use a tool that isn't Task or TodoWrite?"**

If yes, STOP and spawn an agent instead.

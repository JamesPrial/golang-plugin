---
name: complexity-assessment
description: Complexity assessment rules and reviewer scaling
---

# Complexity-Based Reviewer Scaling

During synthesis after exploration, assess implementation complexity to determine reviewer count.

## Complexity Assessment

```
COMPLEXITY ASSESSMENT:
- LOW: Single file, <100 lines changed → 1 reviewer
- MEDIUM: 2-5 files, <500 lines → 1 reviewer
- HIGH: >5 files OR >500 lines OR architectural changes → 2 reviewers
```

## Standard Complexity (LOW/MEDIUM)

**Quality Gate (2 agents parallel):**
- Test Runner Agent: Execute all tests
- Reviewer Agent: Code quality review

**Final Review (3 agents parallel):**
- Test Runner Agent: Full test suite
- Reviewer Agent: Comprehensive code review
- Optimizer Agent: Performance analysis

## High Complexity

**Quality Gate (3 agents parallel):**
- Test Runner Agent: Execute all tests
- Reviewer Agent 1: Focus on correctness + error handling
- Reviewer Agent 2: Focus on patterns + design + documentation

**Final Review (4 agents parallel):**
- Test Runner Agent: Full test suite
- Reviewer Agent 1: Integration review
- Reviewer Agent 2: API/interface review
- Optimizer Agent: Performance analysis

## Reviewer Focus Areas

| Reviewer | Standard | High Complexity - R1 | High Complexity - R2 |
|----------|----------|---------------------|---------------------|
| Primary Focus | All aspects | Correctness, errors | Patterns, design |
| Secondary | - | Logic, edge cases | Documentation |

## Dynamic Updates

After complexity assessment, update the todo list to reflect:
- Actual number of stages identified
- Complexity level (adds Reviewer 2 for HIGH COMPLEXITY)
- Adjusted agent counts per wave

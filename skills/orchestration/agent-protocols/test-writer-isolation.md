---
name: test-writer-isolation
description: Strict isolation rules for test writer agents
---

# Test Writer Isolation

Test Writer agents must be strictly isolated from implementation details to ensure tests verify specifications, not implementations.

## PROHIBITED - Test Writer MUST NOT Receive

- Code examples or snippets from architect
- Implementation file contents (*.go excluding *_test.go)
- Internal data structures or algorithms
- Any content referencing HOW something is implemented
- Variable names from implementation
- Control flow details

## PERMITTED - Test Writer MAY ONLY Receive

- Function/method signatures (name, params, return types)
- Expected behaviors (given X, expect Y)
- Error conditions (when X, error contains "Y")
- Interface contracts (methods that must exist)
- Public API documentation
- Edge cases with expected outcomes

## Verification Question

Before launching Test Writer, ask yourself:

> **"If I gave this prompt to someone who has NEVER seen the implementation, could they write valid tests?"**

If **NO** → Remove implementation details from prompt.

## Why Isolation Matters

| With Isolation | Without Isolation |
|----------------|-------------------|
| Tests verify contract | Tests verify implementation details |
| Refactoring doesn't break tests | Refactoring breaks tests |
| Tests catch interface bugs | Tests miss interface bugs |
| Tests are specification | Tests are documentation of code |

## Parallel Launch Checklist

Before sending implementation wave, verify ALL conditions:

- [ ] Sending SINGLE message with BOTH Task tool calls
- [ ] Implementer prompt references implementation design
- [ ] Test Writer prompt references ONLY test specifications
- [ ] Test Writer prompt contains ZERO code blocks (```)
- [ ] Test Writer prompt contains ZERO file paths to *.go implementation files

**STOP CONDITION:** If ANY checkbox fails, do not proceed. Fix the prompts first.

## Test Specification Format

Test Writer should receive specifications in this format:

```markdown
## Test Specification: [Component]

### Function: [Name]
**Signature:** `func Name(params) (returns, error)`

| Scenario | Input | Expected Output |
|----------|-------|-----------------|
| happy path | valid input | success result |
| nil input | nil | error containing "X is required" |

**Error Conditions:**
- When [condition], returns error containing "[message]"

**Edge Cases:**
- [boundary condition] → [expected behavior]
```

Note: NO code examples, NO algorithms, NO internal structures.

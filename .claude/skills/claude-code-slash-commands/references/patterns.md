# Common Slash Command Patterns

Ready-to-use patterns for common Claude Code slash commands.

## Git Operations

### Commit Helper
```markdown
---
allowed-tools: Bash(git add:*), Bash(git status:*), Bash(git commit:*), Bash(git diff:*)
argument-hint: [optional message]
description: Create a well-formatted commit
---

## Current State
- Branch: !`git branch --show-current`
- Status: !`git status --short`
- Staged changes: !`git diff --cached --stat`

## Task
Create a commit for the staged changes.
If message provided: Use "$ARGUMENTS" as the commit message.
If no message: Generate a conventional commit message from the diff.

Follow conventional commits: type(scope): description
```

### PR Review
```markdown
---
allowed-tools: Bash(gh:*), Bash(git:*)
argument-hint: [pr-number]
description: Review a pull request
---

## PR Information
!`gh pr view $1 --json title,body,additions,deletions,changedFiles`

## Changed Files
!`gh pr diff $1 --name-only`

## Task
Review PR #$1 focusing on:
1. Code correctness
2. Security concerns
3. Performance implications
4. Test coverage
```

## Code Quality

### Security Scan
```markdown
---
argument-hint: [file or directory]
description: Security review of code
---

Perform a security review of @$1 checking for:

1. **Input Validation**: SQL injection, XSS, command injection
2. **Authentication**: Weak patterns, hardcoded credentials
3. **Data Exposure**: Logging sensitive data, insecure storage
4. **Dependencies**: Known vulnerable patterns

Format findings as:
- **[SEVERITY]** Issue description
  - Location: file:line
  - Recommendation: fix approach
```

### Performance Analysis
```markdown
---
argument-hint: [file]
description: Analyze code performance
---

Analyze @$1 for performance issues:

1. **Complexity**: O(n) analysis of loops/recursion
2. **Memory**: Allocations, leaks, large objects
3. **I/O**: Blocking calls, unnecessary operations
4. **Caching**: Missing memoization opportunities

Suggest concrete optimizations with code examples.
```

## Documentation

### Generate Docs
```markdown
---
argument-hint: [file]
description: Generate documentation
allowed-tools: Write
---

Generate comprehensive documentation for @$1:

1. **Overview**: Purpose and usage
2. **API Reference**: Functions/methods with params and returns
3. **Examples**: Common usage patterns
4. **Notes**: Edge cases and gotchas

Output as markdown to docs/ directory.
```

### Explain Code
```markdown
---
argument-hint: [file]
description: Explain code in plain language
---

Explain @$1 as if teaching a junior developer:

1. **Purpose**: What does this code accomplish?
2. **How It Works**: Step-by-step walkthrough
3. **Key Concepts**: Important patterns or techniques used
4. **Potential Issues**: Things to watch out for
```

## Testing

### Generate Tests
```markdown
---
argument-hint: [file]
description: Generate unit tests
allowed-tools: Write
---

Generate unit tests for @$1:

1. Analyze the code to identify testable units
2. Create tests covering:
   - Happy path scenarios
   - Edge cases
   - Error conditions
3. Use the project's existing test framework
4. Include meaningful test descriptions

Reference existing tests: @tests/
```

### Test Coverage Gap
```markdown
---
argument-hint: [source-file] [test-file]
description: Identify missing test coverage
---

Compare @$1 (source) with @$2 (tests).

Identify:
1. Functions/methods without test coverage
2. Code paths not exercised
3. Edge cases not tested
4. Error scenarios not verified

Prioritize by risk and suggest specific test cases.
```

## Refactoring

### Extract Function
```markdown
---
argument-hint: [file] [line-start] [line-end]
description: Extract code into a function
---

In @$1, extract lines $2-$3 into a well-named function:

1. Identify inputs (parameters needed)
2. Identify outputs (return value)
3. Choose descriptive name
4. Add appropriate documentation
5. Update the original location to call the new function
```

### Modernize Code
```markdown
---
argument-hint: [file]
description: Update to modern patterns
---

Modernize @$1 using current best practices:

1. Update deprecated APIs
2. Use modern language features
3. Improve type safety
4. Simplify with newer patterns
5. Maintain backward compatibility where needed

Explain each change and why it's better.
```

## Project Management

### Todo Summary
```markdown
---
description: Find and summarize TODOs
allowed-tools: Bash(grep:*), Bash(find:*)
---

## Current TODOs
!`grep -rn "TODO\|FIXME\|HACK\|XXX" --include="*.{js,ts,py,go,rs}" . 2>/dev/null | head -50`

## Task
Summarize the TODOs found:
1. Group by category (bug, feature, tech debt)
2. Prioritize by apparent urgency
3. Suggest which to address first
```

### Changelog Entry
```markdown
---
argument-hint: [version]
description: Generate changelog entry
allowed-tools: Bash(git:*)
---

## Recent Commits
!`git log --oneline --since="1 week ago"`

## Task
Generate a changelog entry for version $1:

## [$1] - {date}

### Added
- New features

### Changed  
- Changes to existing functionality

### Fixed
- Bug fixes

### Removed
- Removed features
```

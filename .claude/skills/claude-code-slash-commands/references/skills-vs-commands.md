# Skills vs Slash Commands

When to use each approach in Claude Code.

## Use Slash Commands For

**Quick, frequently-used prompts:**
- Simple prompt snippets you use often
- Quick templates or reminders
- Instructions that fit in one file

**Examples:**
- `/review` → "Review this code for bugs"
- `/explain` → "Explain this code simply"
- `/optimize` → "Analyze for performance"

## Use Skills For

**Comprehensive capabilities:**
- Complex multi-step workflows
- Capabilities requiring scripts or utilities
- Knowledge across multiple files
- Team workflows to standardize

**Examples:**
- PDF processing with form-filling scripts
- Data analysis with reference docs
- Documentation with style guides

## Comparison

| Aspect | Slash Commands | Skills |
|--------|---------------|--------|
| Complexity | Simple prompts | Complex capabilities |
| Structure | Single .md file | Directory with SKILL.md + resources |
| Discovery | Explicit (`/command`) | Automatic (context-based) |
| Files | One file only | Multiple files, scripts, templates |
| Scope | Project or personal | Project or personal |

## Example: Code Review

**As slash command:**
```markdown
# .claude/commands/review.md
Review this code for:
- Security vulnerabilities
- Performance issues
- Style violations
```
Usage: `/review` (manual)

**As skill:**
```
.claude/skills/code-review/
├── SKILL.md
├── SECURITY.md
├── PERFORMANCE.md
├── STYLE.md
└── scripts/run-linters.sh
```
Usage: "Review this code" (automatic)

## Decision Guide

**Use slash commands when:**
- Same prompt used repeatedly
- Fits in single file
- Want explicit control

**Use Skills when:**
- Auto-discovery preferred
- Multiple files/scripts needed
- Complex validation workflows
- Team needs detailed guidance

Both can coexist—use what fits your needs.

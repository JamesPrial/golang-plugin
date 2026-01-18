#!/usr/bin/env python3
"""
Slash Command Initializer - Creates a new Claude Code slash command from template

Usage:
    init_command.py <command-name> [--project | --user] [--with-tools]

Examples:
    init_command.py review --project
    init_command.py my-helper --user --with-tools
    init_command.py fix-issue --project
"""

import sys
import os
from pathlib import Path

SIMPLE_TEMPLATE = """---
argument-hint: {arg_hint}
description: {description}
---

{prompt_placeholder}
"""

TOOLS_TEMPLATE = """---
allowed-tools: {tools}
argument-hint: {arg_hint}
description: {description}
---

## Context

{context_placeholder}

## Task

{task_placeholder}
"""


def get_project_commands_dir():
    """Get the project commands directory (.claude/commands/)."""
    return Path.cwd() / '.claude' / 'commands'


def get_user_commands_dir():
    """Get the user commands directory (~/.claude/commands/)."""
    return Path.home() / '.claude' / 'commands'


def init_command(command_name, scope='project', with_tools=False):
    """
    Initialize a new slash command with template.
    
    Args:
        command_name: Name of the command (without .md)
        scope: 'project' or 'user'
        with_tools: Whether to include allowed-tools template
    
    Returns:
        Path to created command file, or None if error
    """
    # Determine target directory
    if scope == 'project':
        commands_dir = get_project_commands_dir()
    else:
        commands_dir = get_user_commands_dir()
    
    # Create directory if needed
    commands_dir.mkdir(parents=True, exist_ok=True)
    
    # Check for existing command
    command_path = commands_dir / f'{command_name}.md'
    if command_path.exists():
        print(f"❌ Error: Command already exists: {command_path}")
        return None
    
    # Generate template
    if with_tools:
        content = TOOLS_TEMPLATE.format(
            tools='Bash(command:*)',
            arg_hint='[arguments]',
            description=f'TODO: Describe what /{command_name} does',
            context_placeholder='- Current state: !`echo "TODO: Add context commands"`',
            task_placeholder='TODO: Describe the task using $ARGUMENTS or $1, $2, etc.'
        )
    else:
        content = SIMPLE_TEMPLATE.format(
            arg_hint='[arguments]',
            description=f'TODO: Describe what /{command_name} does',
            prompt_placeholder='TODO: Write your prompt here.\n\nUse $ARGUMENTS for all arguments, or $1, $2 for positional.\nReference files with @path/to/file.'
        )
    
    # Write command file
    try:
        command_path.write_text(content)
        print(f"✅ Created /{command_name} at {command_path}")
        print(f"\nNext steps:")
        print(f"1. Edit {command_path}")
        print(f"2. Update the description in frontmatter")
        print(f"3. Replace TODO placeholders with your prompt")
        if with_tools:
            print(f"4. Configure allowed-tools for your use case")
        return command_path
    except Exception as e:
        print(f"❌ Error creating command: {e}")
        return None


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command_name = sys.argv[1]
    scope = 'project'
    with_tools = False
    
    for arg in sys.argv[2:]:
        if arg == '--project':
            scope = 'project'
        elif arg == '--user':
            scope = 'user'
        elif arg == '--with-tools':
            with_tools = True
    
    # Validate command name
    if not command_name.replace('-', '').replace('_', '').isalnum():
        print("❌ Error: Command name should only contain letters, numbers, hyphens, and underscores")
        sys.exit(1)
    
    if command_name.endswith('.md'):
        command_name = command_name[:-3]
    
    result = init_command(command_name, scope, with_tools)
    sys.exit(0 if result else 1)


if __name__ == "__main__":
    main()

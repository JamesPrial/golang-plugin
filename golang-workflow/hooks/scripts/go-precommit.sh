#!/bin/bash
#
# go-precommit.sh - Run golangci-lint before git commit commands
# Reads tool_input JSON from stdin and checks for git commit operations
#

set -euo pipefail

# Read the entire stdin into a variable
input=$(cat)

# Extract command from JSON using jq (fallback to grep if jq unavailable)
# Hook input structure: {"tool_input": {"command": "..."}}
if command -v jq &> /dev/null; then
    command=$(echo "$input" | jq -r '.tool_input.command // empty')
else
    # Simple grep-based extraction as fallback
    command=$(echo "$input" | grep -oP '"command"\s*:\s*"\K[^"]+' || echo "")
fi

# Check if command is empty
if [ -z "$command" ]; then
    exit 0
fi

# Check if command contains "git commit"
if [[ ! "$command" =~ git[[:space:]]+commit ]]; then
    exit 0
fi

# Check if golangci-lint is available
if ! command -v golangci-lint &> /dev/null; then
    echo "Warning: golangci-lint not found, skipping lint check" >&2
    exit 0
fi

# Run golangci-lint
if ! output=$(golangci-lint run 2>&1); then
    echo "golangci-lint found issues:" >&2
    echo "$output" >&2
    echo "" >&2
    echo "Please fix the linting issues before committing." >&2
    exit 2
fi

exit 0

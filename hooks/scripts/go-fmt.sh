#!/bin/bash
#
# go-fmt.sh - Automatically format Go files after Write operations
# Reads tool_input JSON from stdin and runs go fmt on .go files
#

set -euo pipefail

# Read the entire stdin into a variable
input=$(cat)

# Extract file_path from JSON using jq (fallback to grep if jq unavailable)
# Hook input structure: {"tool_input": {"file_path": "..."}}
if command -v jq &> /dev/null; then
    file_path=$(echo "$input" | jq -r '.tool_input.file_path // empty')
else
    # Simple grep-based extraction as fallback
    file_path=$(echo "$input" | grep -oP '"file_path"\s*:\s*"\K[^"]+' || echo "")
fi

# Check if file_path is empty
if [ -z "$file_path" ]; then
    exit 0
fi

# Check if file exists and ends with .go
if [ ! -f "$file_path" ]; then
    exit 0
fi

if [[ ! "$file_path" =~ \.go$ ]]; then
    exit 0
fi

# Run go fmt on the file
if ! go fmt "$file_path" 2>&1; then
    echo "Error: go fmt failed for $file_path" >&2
    exit 2
fi

exit 0

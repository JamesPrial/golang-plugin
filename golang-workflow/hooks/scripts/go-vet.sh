#!/bin/bash
#
# go-vet.sh - Run go vet after Edit operations on Go files
# Reads tool_input JSON from stdin and runs go vet on the package
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

# Check if file ends with .go
if [[ ! "$file_path" =~ \.go$ ]]; then
    exit 0
fi

# Get the directory of the Go file
dir=$(dirname "$file_path")

# Run go vet on the entire package
if ! output=$(cd "$dir" && go vet ./... 2>&1); then
    echo "go vet found issues:" >&2
    echo "$output" >&2
    exit 2
fi

exit 0

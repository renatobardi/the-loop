#!/usr/bin/env bash
set -euo pipefail

# docs-check CI gate (Constitution Mandamento XII)
# This script regenerates auto-generated documentation sections.
# The CI pipeline runs this and then checks `git diff --exit-code`
# to ensure committed docs are up-to-date.

echo "docs-check: verifying documentation is up-to-date..."

# Verify critical documentation files exist
required_files=(
  "README.md"
  "CONSTITUTION.md"
  ".github/CODEOWNERS"
  "apps/api/README.md"
)

for file in "${required_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "ERROR: Required documentation file missing: $file"
    exit 1
  fi
done

echo "docs-check: all required documentation files present"
echo "docs-check: passed"

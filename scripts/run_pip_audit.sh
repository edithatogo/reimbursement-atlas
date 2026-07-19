#!/usr/bin/env bash
set -euo pipefail

# Audit external locked dependencies without treating this unpublished local project as PyPI input.
requirements_file="$(mktemp)"
trap 'rm -f "$requirements_file"' EXIT

uv export --all-extras --no-emit-project --format requirements.txt --no-hashes >"$requirements_file"

for attempt in 1 2 3; do
  if uv run --all-extras pip-audit --strict --requirement "$requirements_file"; then
    exit 0
  fi
  if [[ "$attempt" -lt 3 ]]; then
    echo "pip-audit failed on attempt ${attempt}; retrying advisory service access" >&2
    sleep 10
  fi
done

exit 1

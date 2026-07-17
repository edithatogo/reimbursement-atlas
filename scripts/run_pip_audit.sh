#!/usr/bin/env bash
set -euo pipefail

# Audit external locked dependencies without treating this unpublished local project as PyPI input.
requirements_file="$(mktemp)"
trap 'rm -f "$requirements_file"' EXIT

uv export --all-extras --no-emit-project --format requirements.txt --no-hashes >"$requirements_file"
uv run --all-extras pip-audit --strict --requirement "$requirements_file"

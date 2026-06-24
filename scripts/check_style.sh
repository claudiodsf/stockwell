#!/usr/bin/env bash
# Copyright (c) 2021-2026 Claudio Satriano <satriano@ipgp.fr>
# SPDX-License-Identifier: GPL-3.0-or-later

set -euo pipefail

usage() {
    cat <<'EOF'
Usage: scripts/check_style.sh [PATH ...]

Runs the local style checks used by repository agents and hooks.

Checks:
  - flake8 with the repository config
  - sourcery review on the repository
    - required flake8 plugins: flake8-quotes, flake8-docstrings

PATH:
  Optional Python file or directory paths for flake8. Default is the
  repository root.

When invoked by the git hook, it can receive the staged Python files and
will only check those paths.

Examples:
  scripts/check_style.sh
  scripts/check_style.sh tests
  scripts/check_style.sh requake tests
EOF
}

die() {
    echo "Error: $*" >&2
    exit 1
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "Required command not found: $1"
}

require_python_package() {
    python -m pip show "$1" >/dev/null 2>&1 || die \
        "Required Python package not found: $1"
}

case "${1:-}" in
    -h|--help)
        usage
        exit 0
        ;;
esac

require_cmd git
require_cmd python
require_cmd flake8
require_cmd sourcery
require_python_package flake8-quotes
require_python_package flake8-docstrings

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || die \
    "Not inside a git repository"
cd "$repo_root"

is_vendored_configobj_path() {
    local path="$1"
    [[ "$path" == requake/config/configobj/* ]]
}

if [[ $# -eq 0 ]]; then
    flake8_targets=(.)
else
    flake8_targets=()
    for path in "$@"; do
        if is_vendored_configobj_path "$path"; then
            continue
        fi
        flake8_targets+=("$path")
    done
fi

if [[ ${#flake8_targets[@]} -eq 0 ]]; then
    echo 'No non-vendored Python paths to check.'
    exit 0
fi

flake8 "${flake8_targets[@]}"
sourcery_output="$(sourcery review "${flake8_targets[@]}")"
printf '%s\n' "$sourcery_output"

actionable_issues="$(printf '%s\n' "$sourcery_output" |
    grep -E '^[^[:space:]].*:[0-9]+' |
    grep -v 'low-code-quality' || true)"
if [[ -n "$actionable_issues" ]]; then
    die "Sourcery found actionable issues"
fi

echo "Style checks passed."
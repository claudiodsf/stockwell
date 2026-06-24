#!/usr/bin/env bash
# Copyright (c) 2021-2026 Claudio Satriano <satriano@ipgp.fr>
# SPDX-License-Identifier: GPL-3.0-or-later

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null)" || {
    echo "Error: Not inside a git repository" >&2
    exit 1
}

cd "$repo_root"

mkdir -p .githooks

git config core.hooksPath .githooks
chmod +x .githooks/pre-commit scripts/check_style.sh

echo "Configured local git hooks in .githooks"
echo "Run scripts/check_style.sh to check style manually"
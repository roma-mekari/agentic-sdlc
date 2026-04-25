#!/usr/bin/env bash
# Set up git hooks for this repository.
#
# Usage: source tests/static/setup-hooks.sh
#    or: bash tests/static/setup-hooks.sh

set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"

if [ ! -d "$REPO_ROOT/.githooks" ]; then
    echo "❌ No .githooks directory found at $REPO_ROOT/.githooks"
    exit 1
fi

git config --local core.hooksPath .githooks
chmod +x "$REPO_ROOT/.githooks/pre-push"

echo "✅ Git hooks configured."
echo "   core.hooksPath = .githooks"
echo "   pre-push hook will run agent validation before allowing push."
echo ""
echo "To skip validation on a specific push: git push --no-verify"

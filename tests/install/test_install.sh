#!/usr/bin/env bash
# tests/install/test_install.sh — smoke + contract tests for install.sh.
#
# Runs install.sh into temp dirs for each target and asserts:
#   - file naming convention
#   - frontmatter shape (per-target)
#   - tool-name substitutions (Claude only)
#   - workflow_templates are copied
#   - dry-run does not write
#   - --agents filter narrows the set
#   - bad target / bad scope / unknown tool surface errors
#
# Pure bash + standard POSIX tools. No Python, no Node.
#
# Run: bash tests/install/test_install.sh

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
INSTALL="$REPO_ROOT/install.sh"

PASS=0
FAIL=0
FAILED_TESTS=()
CURRENT_TEST=""

tmpdir() { mktemp -d "/tmp/install-test-XXXXXX"; }

start() { CURRENT_TEST="$1"; printf '── %s\n' "$1"; }

ok() { PASS=$((PASS + 1)); printf '   ✓ %s\n' "$1"; }

fail() {
    FAIL=$((FAIL + 1))
    FAILED_TESTS+=("$CURRENT_TEST: $1")
    printf '   ✗ %s\n' "$1"
}

assert_file()        { [ -f "$1" ] && ok "exists: ${1##*/}"        || fail "missing file: $1"; }
assert_not_file()    { [ ! -f "$1" ] && ok "absent: ${1##*/}"      || fail "unexpected file: $1"; }
assert_dir()         { [ -d "$1" ] && ok "dir exists: ${1##*/}"    || fail "missing dir: $1"; }
assert_not_dir()     { [ ! -d "$1" ] && ok "dir absent: ${1##*/}"  || fail "unexpected dir: $1"; }

assert_grep() {
    local pattern=$1 file=$2 label=${3:-}
    if grep -qE "$pattern" "$file"; then
        ok "matches /${label:-$pattern}/ in ${file##*/}"
    else
        fail "pattern /${label:-$pattern}/ not found in $file"
    fi
}

assert_not_grep() {
    local pattern=$1 file=$2 label=${3:-}
    if ! grep -qE "$pattern" "$file"; then
        ok "no /${label:-$pattern}/ in ${file##*/}"
    else
        fail "pattern /${label:-$pattern}/ unexpectedly present in $file"
    fi
}

# ─────────────────────────────────────────────────────────────────────────────
start "Claude target: full install"
T=$(tmpdir)
bash "$INSTALL" claude --target-dir "$T" >/dev/null 2>&1

assert_dir  "$T/.claude/agents"
assert_dir  "$T/.github/workflow_templates"
assert_file "$T/.claude/agents/dev.md"
assert_file "$T/.claude/agents/sdlc-orchestrator.md"
assert_file "$T/.claude/agents/explorer.md"
assert_not_file "$T/.claude/agents/dev.agent.md"  # claude target drops .agent suffix

# Frontmatter shape: tools must be a comma-separated string, NOT a YAML array.
assert_grep '^tools: [A-Z][A-Za-z, ]+$' "$T/.claude/agents/dev.md" "tools: comma-string"
assert_grep '^model: inherit$' "$T/.claude/agents/dev.md" "model: inherit"
assert_grep '^name: dev$' "$T/.claude/agents/dev.md" "kebab name"

# Copilot-only fields must be stripped from Claude frontmatter.
# Restrict the check to the frontmatter block (first 20 lines).
head -20 "$T/.claude/agents/dev.md" > "$T/_fm.txt"
assert_not_grep '^argument-hint:'  "$T/_fm.txt" "argument-hint stripped"
assert_not_grep '^user-invocable:' "$T/_fm.txt" "user-invocable stripped"
assert_not_grep '^agents:'         "$T/_fm.txt" "agents stripped"

# Body substitutions
assert_grep '`AskUserQuestion`' "$T/.claude/agents/dev.md" "AskUserQuestion (sub)"
assert_grep '`Bash`'            "$T/.claude/agents/dev.md" "Bash (sub)"
assert_grep '`TodoWrite`'       "$T/.claude/agents/dev.md" "TodoWrite (sub)"
# `Edit` and `Read` show up as backtick tool references after substitution; the
# raw lowercase 'edit' / 'read' backticks should be gone (case-sensitive search).
assert_not_grep '`edit`'        "$T/.claude/agents/dev.md" "no lowercase \`edit\`"
assert_not_grep 'vscode/askQuestions' "$T/.claude/agents/dev.md" "vscode/askQuestions purged"

# Templates copied
assert_file "$T/.github/workflow_templates/REQUIREMENTS.md"
assert_file "$T/.github/workflow_templates/PLAN.md"
assert_file "$T/.github/workflow_templates/QA_REPORT.md"
assert_file "$T/.github/workflow_templates/ADR.md"

rm -rf "$T"

# ─────────────────────────────────────────────────────────────────────────────
start "Copilot target: identity copy"
T=$(tmpdir)
bash "$INSTALL" copilot --target-dir "$T" >/dev/null 2>&1

assert_file     "$T/.github/agents/dev.agent.md"
assert_not_file "$T/.github/agents/dev.md"
assert_file     "$T/.github/workflow_templates/PLAN.md"

# Copilot files must match the source byte-for-byte.
if diff -q "$REPO_ROOT/agents/dev.agent.md" "$T/.github/agents/dev.agent.md" >/dev/null; then
    ok "dev.agent.md identical to source"
else
    fail "dev.agent.md differs from source"
fi

# Original Copilot frontmatter should still be intact.
assert_grep '^tools: \[' "$T/.github/agents/dev.agent.md" "tools: [...] array"
assert_grep '^user-invocable:' "$T/.github/agents/dev.agent.md" "user-invocable kept"

rm -rf "$T"

# ─────────────────────────────────────────────────────────────────────────────
start "Dry run writes nothing"
T=$(tmpdir)
bash "$INSTALL" claude --target-dir "$T" --dry-run >/dev/null 2>&1

assert_not_dir "$T/.claude"
assert_not_dir "$T/.github"

rm -rf "$T"

# ─────────────────────────────────────────────────────────────────────────────
start "--agents filter installs only matching agents"
T=$(tmpdir)
bash "$INSTALL" claude --target-dir "$T" --agents dev,explorer --no-templates >/dev/null 2>&1

assert_file     "$T/.claude/agents/dev.md"
assert_file     "$T/.claude/agents/explorer.md"
assert_not_file "$T/.claude/agents/po.md"
assert_not_file "$T/.claude/agents/sdlc-orchestrator.md"
assert_not_dir  "$T/.github/workflow_templates"

rm -rf "$T"

# ─────────────────────────────────────────────────────────────────────────────
start "All agents transform without error"
T=$(tmpdir)
bash "$INSTALL" claude --target-dir "$T" --no-templates >/dev/null 2>&1

agent_count=$(find "$REPO_ROOT/agents" -maxdepth 1 -name '*.agent.md' | wc -l | tr -d ' ')
installed_count=$(find "$T/.claude/agents" -maxdepth 1 -name '*.md' | wc -l | tr -d ' ')

if [ "$agent_count" = "$installed_count" ]; then
    ok "all $agent_count agents installed"
else
    fail "expected $agent_count agents, got $installed_count"
fi

# Each transformed agent must have a non-empty tools line.
for f in "$T/.claude/agents"/*.md; do
    if grep -qE '^tools: [A-Z]' "$f"; then
        :
    else
        fail "$(basename "$f"): missing or malformed tools line"
    fi
done
ok "all transformed agents have a tools line"

rm -rf "$T"

# ─────────────────────────────────────────────────────────────────────────────
start "yq path matches awk fallback (when yq is available)"
if command -v yq >/dev/null 2>&1; then
    A=$(tmpdir); B=$(tmpdir)
    INSTALL_SH_NO_YQ=1 bash "$INSTALL" claude --target-dir "$A" --no-templates >/dev/null 2>&1
    bash "$INSTALL" claude --target-dir "$B" --no-templates >/dev/null 2>&1

    if diff -r "$A/.claude/agents" "$B/.claude/agents" >/dev/null; then
        ok "yq and awk-fallback produce identical output"
    else
        fail "yq path diverges from awk fallback"
        diff -r "$A/.claude/agents" "$B/.claude/agents" | head -20 >&2
    fi

    # Header line should advertise which parser is in use.
    hdr_yq=$(bash "$INSTALL" claude --target-dir "$(tmpdir)" --dry-run 2>&1 | grep 'yaml parser' || true)
    hdr_aw=$(INSTALL_SH_NO_YQ=1 bash "$INSTALL" claude --target-dir "$(tmpdir)" --dry-run 2>&1 | grep 'yaml parser' || true)
    case "$hdr_yq" in *yq*)  ok  "header reports yq when available" ;; *) fail "header missing yq marker" ;; esac
    case "$hdr_aw" in *awk*) ok  "header reports awk fallback with INSTALL_SH_NO_YQ=1" ;; *) fail "header missing awk marker" ;; esac

    rm -rf "$A" "$B"
else
    ok "skipped (yq not installed on this host)"
fi

# ─────────────────────────────────────────────────────────────────────────────
start "Error handling"

# Missing target arg
if bash "$INSTALL" >/dev/null 2>&1; then
    fail "should exit non-zero with no args"
else
    ok "exits non-zero with no args"
fi

# Unknown target
if bash "$INSTALL" cursor --target-dir /tmp >/dev/null 2>&1; then
    fail "should reject unknown target"
else
    ok "rejects unknown target"
fi

# Bad scope
if bash "$INSTALL" claude --scope global --target-dir /tmp >/dev/null 2>&1; then
    fail "should reject bad scope"
else
    ok "rejects bad scope"
fi

# Unknown agent in filter
T=$(tmpdir)
if bash "$INSTALL" claude --target-dir "$T" --agents nope --no-templates >/dev/null 2>&1; then
    fail "should fail when --agents matches nothing"
else
    ok "fails when --agents matches nothing"
fi
rm -rf "$T"

# Unknown Copilot tool in a fake agent should cause an error.
FAKE=$(tmpdir)
mkdir -p "$FAKE/agents" "$FAKE/workflow_templates"
cat > "$FAKE/agents/broken.agent.md" <<'EOF'
---
name: "Broken"
description: "uses an unknown tool"
tools: [read, mystery]
user-invocable: false
---

body
EOF
cp "$REPO_ROOT/install.sh" "$FAKE/install.sh"
chmod +x "$FAKE/install.sh"
T=$(tmpdir)
if bash "$FAKE/install.sh" claude --target-dir "$T" --no-templates >/dev/null 2>&1; then
    fail "should fail on unknown Copilot tool"
else
    ok "fails on unknown Copilot tool"
fi
rm -rf "$T" "$FAKE"

# ─────────────────────────────────────────────────────────────────────────────
echo ""
printf '── Summary ──\n'
printf '  %d passed, %d failed\n' "$PASS" "$FAIL"

if [ "$FAIL" -gt 0 ]; then
    echo ""
    echo "Failures:"
    for f in "${FAILED_TESTS[@]}"; do
        printf '  - %s\n' "$f"
    done
    exit 1
fi

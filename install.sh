#!/usr/bin/env bash
# install.sh — Install Agentic SDLC agents and templates into a target editor.
#
# Source format is the Copilot ".agent.md" set under agents/. This script either
# copies them as-is (for Copilot targets) or transforms them into Claude Code's
# agent format on the fly.
#
# Usage:
#   install.sh <target> [options]
#
# Targets:
#   copilot   GitHub Copilot Chat (VS Code) — .agent.md
#   claude    Claude Code — .md (frontmatter + tool refs rewritten)
#
# Options:
#   --scope <scope>       project | user                 (default: project)
#   --target-dir <dir>    Project root for --scope project (default: $PWD)
#   --agents <list>       Comma-separated agent stems to install (default: all)
#   --no-templates        Skip copying workflow_templates/ (project scope only)
#   --dry-run             Print what would happen; write nothing
#   -h, --help            Show this message
#
# Examples:
#   cd ~/my-project && bash ~/agentic-sdlc/install.sh claude
#   bash install.sh claude  --scope user
#   bash install.sh copilot --scope project --target-dir ~/my-project
#   bash install.sh claude  --agents dev,explorer --no-templates

set -euo pipefail

# ── Locate source repo ────────────────────────────────────────────────────────

SCRIPT_PATH="${BASH_SOURCE[0]}"
while [ -L "$SCRIPT_PATH" ]; do
    SCRIPT_DIR="$(cd -P "$(dirname "$SCRIPT_PATH")" && pwd)"
    SCRIPT_PATH="$(readlink "$SCRIPT_PATH")"
    [[ "$SCRIPT_PATH" != /* ]] && SCRIPT_PATH="$SCRIPT_DIR/$SCRIPT_PATH"
done
REPO_ROOT="$(cd -P "$(dirname "$SCRIPT_PATH")" && pwd)"

AGENTS_SRC="$REPO_ROOT/agents"
TEMPLATES_SRC="$REPO_ROOT/workflow_templates"

# ── Tool mapping (Copilot → space-separated Claude tools) ─────────────────────
# IMPORTANT: keep in sync with VALID_TOOLS in tests/static/validate_agents.py.

claude_tools_for() {
    case "$1" in
        read)                  echo "Read Glob" ;;
        edit)                  echo "Read Edit Write" ;;
        search)                echo "Grep Glob" ;;
        execute)               echo "Bash" ;;
        agent)                 echo "Task" ;;
        todo)                  echo "TodoWrite" ;;
        web)                   echo "WebFetch WebSearch" ;;
        vscode/askQuestions)   echo "AskUserQuestion" ;;
        *) return 1 ;;
    esac
}

# Body substitutions for Claude target. Tokens are backtick-wrapped to avoid
# collisions with prose (except vscode/askQuestions which is unique).
CLAUDE_BODY_SED=(
    -e 's|vscode/askQuestions|AskUserQuestion|g'
    -e 's|`runSubagent`|`Task`|g'
    -e 's|`execute`|`Bash`|g'
    -e 's|`edit`|`Edit`|g'
    -e 's|`read`|`Read`|g'
    -e 's|`search`|`Grep`|g'
    -e 's|`todo`|`TodoWrite`|g'
    -e 's|`web`|`WebFetch`|g'
    -e 's|`agent`|`Task`|g'
)

# ── Helpers ───────────────────────────────────────────────────────────────────

log()  { printf '%s\n' "$*" >&2; }
warn() { printf 'WARN: %s\n' "$*" >&2; }
die()  { printf 'ERROR: %s\n' "$*" >&2; exit 1; }

usage() { sed -n '2,/^set -euo/p' "$0" | sed -e '$d' -e 's/^# \{0,1\}//'; }

# ── yq detection ─────────────────────────────────────────────────────────────
# yq comes in two flavors with slightly different conventions:
#   - mikefarah (Go):  `yq '.k'`     prints scalars unquoted
#   - kislyuk (Python): `yq -r '.k'` prints scalars unquoted (with -r)
# Probe both. If neither works, or INSTALL_SH_NO_YQ=1, fall back to awk.

YQ_CMD=""   # empty = fall back; otherwise the command (e.g. "yq" or "yq -r")

detect_yq() {
    if [ "${INSTALL_SH_NO_YQ:-}" = "1" ]; then return 1; fi
    command -v yq >/dev/null 2>&1 || return 1

    local probe
    probe=$(printf 'k: x\n' | yq '.k' 2>/dev/null || true)
    if [ "$probe" = "x" ]; then YQ_CMD="yq"; return 0; fi

    probe=$(printf 'k: x\n' | yq -r '.k' 2>/dev/null || true)
    if [ "$probe" = "x" ]; then YQ_CMD="yq -r"; return 0; fi

    return 1
}
detect_yq || true

# Extract the YAML frontmatter block (between the first pair of `---` lines).
extract_frontmatter() {
    awk '/^---[[:space:]]*$/ { c++; if (c == 2) exit; next } c == 1' "$1"
}

# Pull a single scalar field from frontmatter. Strips surrounding quotes.
get_field() {
    local file=$1 field=$2
    if [ -n "$YQ_CMD" ]; then
        extract_frontmatter "$file" | $YQ_CMD ".${field} // \"\"" 2>/dev/null
        return
    fi
    awk -v f="$field" '
        /^---[[:space:]]*$/ { c++; if (c == 2) exit; next }
        c == 1 {
            prefix = f ":"
            if (index($0, prefix) == 1) {
                v = substr($0, length(prefix) + 1)
                sub(/^[[:space:]]+/, "", v)
                if (v ~ /^".*"$/) v = substr(v, 2, length(v) - 2)
                print v
                exit
            }
        }
    ' "$file"
}

# Parse `tools: [a, b, c]` into newline-separated tokens.
get_tools() {
    local file=$1
    if [ -n "$YQ_CMD" ]; then
        extract_frontmatter "$file" | $YQ_CMD '.tools[]' 2>/dev/null
        return
    fi
    awk '
        /^---[[:space:]]*$/ { c++; if (c == 2) exit; next }
        c == 1 && /^tools:/ {
            sub(/^tools:[[:space:]]*\[/, "")
            sub(/\][[:space:]]*$/, "")
            n = split($0, parts, /,/)
            for (i = 1; i <= n; i++) {
                gsub(/^[[:space:]]+|[[:space:]]+$/, "", parts[i])
                if (length(parts[i])) print parts[i]
            }
        }
    ' "$file"
}

# Print the body (everything after the second `---` line).
get_body() {
    awk '
        BEGIN { c = 0 }
        c == 2 { print; next }
        /^---[[:space:]]*$/ { c++; next }
    ' "$1"
}

# Map a newline-separated list of Copilot tools → comma-separated Claude tools.
# Uses a space-delimited sentinel string for dedupe (bash 3.2 compatible).
map_tools_to_claude() {
    local agent_label=$1
    local seen=" "
    local joined=""
    local tool mapped t
    while IFS= read -r tool; do
        [ -z "$tool" ] && continue
        if ! mapped=$(claude_tools_for "$tool"); then
            die "[$agent_label] unknown Copilot tool: '$tool' (add a mapping in install.sh)"
        fi
        for t in $mapped; do
            case "$seen" in
                *" $t "*) ;;
                *) seen="$seen$t "; joined="${joined:+$joined, }$t" ;;
            esac
        done
    done
    printf '%s' "$joined"
}

# ── Writers ───────────────────────────────────────────────────────────────────

write_copilot_agent() {
    local src=$1 dest=$2
    if $DRY_RUN; then
        log "  [dry-run] would copy $(basename "$src") → $dest"
        return
    fi
    cp "$src" "$dest"
}

write_claude_agent() {
    local src=$1 dest=$2
    local stem
    stem=$(basename "$src" .agent.md)

    local desc tools_str
    desc=$(get_field "$src" description)
    [[ -z "$desc" ]] && die "[$stem] missing description in frontmatter"

    tools_str=$(get_tools "$src" | map_tools_to_claude "$stem")
    [[ -z "$tools_str" ]] && die "[$stem] empty tools list after mapping"

    if $DRY_RUN; then
        log "  [dry-run] would write $stem.md ($tools_str)"
        return
    fi

    {
        printf -- '---\n'
        printf 'name: %s\n' "$stem"
        printf 'description: "%s"\n' "$desc"
        printf 'tools: %s\n' "$tools_str"
        printf 'model: inherit\n'
        printf -- '---\n\n'
        get_body "$src" | sed -E "${CLAUDE_BODY_SED[@]}"
    } > "$dest"
}

# ── Path resolution ───────────────────────────────────────────────────────────

resolve_agents_dest() {
    local target=$1 scope=$2 project_dir=$3
    case "$target:$scope" in
        copilot:project) echo "$project_dir/.github/agents" ;;
        copilot:user)
            case "$(uname -s)" in
                Darwin) echo "$HOME/Library/Application Support/Code/User/prompts" ;;
                Linux)  echo "$HOME/.config/Code/User/prompts" ;;
                *)      die "user scope not supported on $(uname -s) for Copilot — pass --target-dir explicitly" ;;
            esac
            ;;
        claude:project)  echo "$project_dir/.claude/agents" ;;
        claude:user)     echo "$HOME/.claude/agents" ;;
        *) die "unknown target/scope: $target/$scope" ;;
    esac
}

# ── Argument parsing ──────────────────────────────────────────────────────────

TARGET=""
SCOPE="project"
TARGET_DIR=""
AGENTS_FILTER=""
INSTALL_TEMPLATES=true
DRY_RUN=false

if [ $# -eq 0 ]; then usage; exit 1; fi

case "${1:-}" in
    -h|--help) usage; exit 0 ;;
    copilot|claude) TARGET=$1; shift ;;
    *) die "first argument must be 'copilot' or 'claude' (got '${1:-}')" ;;
esac

while [ $# -gt 0 ]; do
    case "$1" in
        --scope)        SCOPE=${2:?--scope requires a value}; shift 2 ;;
        --target-dir)   TARGET_DIR=${2:?--target-dir requires a value}; shift 2 ;;
        --agents)       AGENTS_FILTER=${2:?--agents requires a value}; shift 2 ;;
        --no-templates) INSTALL_TEMPLATES=false; shift ;;
        --dry-run)      DRY_RUN=true; shift ;;
        -h|--help)      usage; exit 0 ;;
        *) die "unknown option: $1" ;;
    esac
done

case "$SCOPE" in project|user) ;; *) die "--scope must be 'project' or 'user'" ;; esac

if [ "$SCOPE" = "project" ]; then
    : "${TARGET_DIR:=$PWD}"
    [ -d "$TARGET_DIR" ] || die "target dir does not exist: $TARGET_DIR"
fi

# ── Build agent list ──────────────────────────────────────────────────────────

[ -d "$AGENTS_SRC" ] || die "agents source dir not found: $AGENTS_SRC"

AGENT_FILES=()
while IFS= read -r f; do AGENT_FILES+=("$f"); done < <(find "$AGENTS_SRC" -maxdepth 1 -name '*.agent.md' | sort)
[ ${#AGENT_FILES[@]} -gt 0 ] || die "no *.agent.md files in $AGENTS_SRC"

if [ -n "$AGENTS_FILTER" ]; then
    # Build a space-delimited sentinel string of wanted stems.
    wanted=" $(printf '%s' "$AGENTS_FILTER" | tr ',' ' ' | tr -s ' ') "
    filtered=()
    for f in "${AGENT_FILES[@]}"; do
        stem=$(basename "$f" .agent.md)
        case "$wanted" in
            *" $stem "*) filtered+=("$f") ;;
        esac
    done
    [ ${#filtered[@]} -gt 0 ] || die "no agents matched filter: $AGENTS_FILTER"
    AGENT_FILES=("${filtered[@]}")
fi

# ── Install ───────────────────────────────────────────────────────────────────

AGENTS_DEST=$(resolve_agents_dest "$TARGET" "$SCOPE" "${TARGET_DIR:-}")

log "Agentic SDLC installer"
log "  target:        $TARGET"
log "  scope:         $SCOPE"
log "  source:        $REPO_ROOT"
log "  yaml parser:   ${YQ_CMD:-awk (fallback)}"
log "  agents → $AGENTS_DEST"
if [ "$SCOPE" = "project" ] && $INSTALL_TEMPLATES; then
    log "  templates → $TARGET_DIR/.github/workflow_templates"
fi
$DRY_RUN && log "  mode:          DRY RUN"
log ""

if ! $DRY_RUN; then mkdir -p "$AGENTS_DEST"; fi

log "Installing ${#AGENT_FILES[@]} agent(s)..."
for src in "${AGENT_FILES[@]}"; do
    stem=$(basename "$src" .agent.md)
    if [ "$TARGET" = "copilot" ]; then
        write_copilot_agent "$src" "$AGENTS_DEST/$stem.agent.md"
    else
        write_claude_agent  "$src" "$AGENTS_DEST/$stem.md"
    fi
done

if [ "$SCOPE" = "project" ] && $INSTALL_TEMPLATES; then
    tdest="$TARGET_DIR/.github/workflow_templates"
    log ""
    log "Installing workflow templates → $tdest"
    if ! $DRY_RUN; then mkdir -p "$tdest"; fi
    for f in "$TEMPLATES_SRC"/*.md; do
        [ -f "$f" ] || continue
        if $DRY_RUN; then
            log "  [dry-run] would copy $(basename "$f")"
        else
            cp "$f" "$tdest/"
        fi
    done
fi

log ""
log "Done."
if [ "$TARGET" = "copilot" ] && [ "$SCOPE" = "project" ]; then
    log "Next: in Copilot Chat, the @agent-name prefix should now resolve."
elif [ "$TARGET" = "claude" ] && [ "$SCOPE" = "project" ]; then
    log "Next: in Claude Code, run /agents to see the installed agents."
fi

#!/usr/bin/env bash
# Analyze exported VS Code Copilot chat sessions for SDLC workflow compliance.
#
# Usage:
#   ./analyze_session.sh <path-to-chat.json> [--score] [--verbose]
#
# Requires: jq (https://stedolan.github.io/jq/)
#
# This script extracts metrics from an exported chat session (chat.json)
# and produces a compliance report based on the SDLC workflow expectations.

set -euo pipefail

CHAT_JSON="${1:?Usage: $0 <path-to-chat.json> [--score] [--verbose]}"
SCORE_MODE=false
VERBOSE=false

for arg in "$@"; do
    case "$arg" in
        --score)   SCORE_MODE=true ;;
        --verbose) VERBOSE=true ;;
    esac
done

if ! command -v jq &>/dev/null; then
    echo "Error: jq is required. Install with: brew install jq" >&2
    exit 1
fi

if [ ! -f "$CHAT_JSON" ]; then
    echo "Error: File not found: $CHAT_JSON" >&2
    exit 1
fi

echo "── SDLC Session Analysis ──"
echo "File: $CHAT_JSON"
echo ""

# Extract basic session metadata
TOTAL_REQUESTS=$(jq '.requests | length' "$CHAT_JSON")
AGENT_MODE=$(jq -r '.requests[0].modeInfo.modeName // "unknown"' "$CHAT_JSON")
MODEL=$(jq -r '.requests[0].modelId // "unknown"' "$CHAT_JSON")
TOTAL_PROMPT_TOKENS=$(jq '[.requests[].result.metadata.promptTokens // 0] | add' "$CHAT_JSON")
TOTAL_OUTPUT_TOKENS=$(jq '[.requests[].result.metadata.outputTokens // 0] | add' "$CHAT_JSON")

echo "Session Metadata:"
echo "  User turns: $TOTAL_REQUESTS"
echo "  Agent mode: $AGENT_MODE"
echo "  Model: $MODEL"
echo "  Tokens: ${TOTAL_PROMPT_TOKENS} prompt / ${TOTAL_OUTPUT_TOKENS} output"
echo ""

# Count tool calls by category
echo "── Tool Call Inventory ──"

READ_TOOLS=$(jq '[.requests[].response[] | select(.kind == "toolInvocationSerialized") | .toolId // "" | select(test("copilot_readFile|copilot_listDirectory"))] | length' "$CHAT_JSON")
SEARCH_TOOLS=$(jq '[.requests[].response[] | select(.kind == "toolInvocationSerialized") | .toolId // "" | select(test("copilot_findTextInFiles|copilot_searchInFiles|grep_search|semantic_search|file_search"))] | length' "$CHAT_JSON")
EDIT_TOOLS=$(jq '[.requests[].response[] | select(.kind == "toolInvocationSerialized") | .toolId // "" | select(test("copilot_replaceString|copilot_multiReplaceString|replace_string_in_file|create_file"))] | length' "$CHAT_JSON")
EXECUTE_TOOLS=$(jq '[.requests[].response[] | select(.kind == "toolInvocationSerialized") | .toolId // "" | select(test("run_in_terminal|runTests"))] | length' "$CHAT_JSON")
DELEGATE_TOOLS=$(jq '[.requests[].response[] | select(.kind == "toolInvocationSerialized") | .toolId // "" | select(test("runSubagent"))] | length' "$CHAT_JSON")
HUMAN_GATES=$(jq '[.requests[].response[] | select(.kind == "toolInvocationSerialized") | .toolId // "" | select(test("vscode_askQuestions"))] | length' "$CHAT_JSON")

printf "  %-15s %s\n" "READ:" "$READ_TOOLS"
printf "  %-15s %s\n" "SEARCH:" "$SEARCH_TOOLS"
printf "  %-15s %s\n" "EDIT:" "$EDIT_TOOLS"
printf "  %-15s %s\n" "EXECUTE:" "$EXECUTE_TOOLS"
printf "  %-15s %s\n" "DELEGATE:" "$DELEGATE_TOOLS"
printf "  %-15s %s\n" "HUMAN GATE:" "$HUMAN_GATES"
echo ""

# Compliance checks
echo "── Compliance Checks ──"

ISSUES=0

# Check 1: Delegation ratio
if [ "$DELEGATE_TOOLS" -eq 0 ]; then
    echo "❌ CRITICAL: Zero runSubagent calls — orchestrator did all work itself"
    ISSUES=$((ISSUES + 1))
else
    echo "✅ Delegation count: $DELEGATE_TOOLS"
fi

# Check 2: Human gate presence
if [ "$HUMAN_GATES" -eq 0 ]; then
    echo "⚠️  WARNING: Zero askQuestions calls — no human review gates detected"
    ISSUES=$((ISSUES + 1))
else
    echo "✅ Human gates: $HUMAN_GATES"
fi

# Check 3: High edit count without delegation (orchestrator doing implementor's job)
if [ "$DELEGATE_TOOLS" -eq 0 ] && [ "$EDIT_TOOLS" -gt 3 ]; then
    echo "❌ CRITICAL: $EDIT_TOOLS edits with zero delegations — orchestrator edited files directly"
    ISSUES=$((ISSUES + 1))
fi

# Check 4: High execute count without delegation
if [ "$DELEGATE_TOOLS" -eq 0 ] && [ "$EXECUTE_TOOLS" -gt 0 ]; then
    echo "❌ CRITICAL: $EXECUTE_TOOLS terminal commands with zero delegations — orchestrator ran commands directly"
    ISSUES=$((ISSUES + 1))
fi

# Check 5: Thinking trace bypass signals (if verbose)
if [ "$VERBOSE" = true ]; then
    echo ""
    echo "── Thinking Trace Analysis ──"
    BYPASS_COUNT=$(jq '[.requests[].response[] | select(.kind == "thinking") | .value // "" | select(test("I should|I\'ll |let me |rather than|instead of|bypass|skip"; "i"))] | length' "$CHAT_JSON")
    echo "  Potential bypass signals: $BYPASS_COUNT"
fi

echo ""

# Score calculation
if [ "$SCORE_MODE" = true ]; then
    echo "── Health Score ──"

    TOTAL_ACTIONS=$((READ_TOOLS + SEARCH_TOOLS + EDIT_TOOLS + EXECUTE_TOOLS + DELEGATE_TOOLS + HUMAN_GATES))

    if [ "$TOTAL_ACTIONS" -gt 0 ]; then
        DELEGATION_PCT=$(( (DELEGATE_TOOLS * 100) / TOTAL_ACTIONS ))
        GATE_PCT=$(( (HUMAN_GATES * 100) / TOTAL_ACTIONS ))
    else
        DELEGATION_PCT=0
        GATE_PCT=0
    fi

    if [ "$ISSUES" -eq 0 ]; then
        HEALTH="HEALTHY"
    elif [ "$ISSUES" -le 2 ]; then
        HEALTH="DEGRADED"
    else
        HEALTH="UNHEALTHY"
    fi

    echo "  Delegation ratio: ${DELEGATION_PCT}%"
    echo "  Gate ratio: ${GATE_PCT}%"
    echo "  Issues: $ISSUES"
    echo "  Health: $HEALTH"
fi

echo ""
echo "── Verdict ──"
if [ "$ISSUES" -eq 0 ]; then
    echo "✅ COMPLIANT — No delegation or gating violations detected"
    exit 0
else
    echo "❌ NON-COMPLIANT — $ISSUES issue(s) detected"
    exit 1
fi

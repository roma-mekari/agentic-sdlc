#!/usr/bin/env bash
set -euo pipefail

HOOK_EVENT="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "$SCRIPT_DIR/trace_hook.py" --hook-event "$HOOK_EVENT"

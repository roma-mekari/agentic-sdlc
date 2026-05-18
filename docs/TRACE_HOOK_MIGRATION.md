# TRACE.jsonl Migration Strategy: Instruction-Based → Hook-Based

## Status

Proposed implementation plan for migrating `TRACE.jsonl` generation from orchestrator-managed `edit` calls to VS Code/Copilot lifecycle hooks.

## Goals

1. Preserve current `TRACE.jsonl` compatibility for Athena and existing analysis.
2. Add hook-native observability without breaking ongoing runs.
3. Support a **double-trigger** transition period where instruction logging and hook logging coexist safely.
4. End in a **hooks-only** model for runtime trace generation.

---

## 1) Recommended Strategy

Use a **hybrid event model**:

- Keep existing SDLC events as the **canonical semantic layer**:
  - `RUN_START`
  - `STAGE_START`
  - `DELEGATED`
  - `SUBAGENT_RETURNED`
  - `HUMAN_GATE`
  - `STAGE_COMPLETE`
  - `VIOLATION`
  - `ATHENA_TRIGGER`
  - `RUN_COMPLETE`
- Add hook-native events in a namespaced form for lower-level lifecycle visibility:
  - `HOOK_SESSION_START`
  - `HOOK_USER_PROMPT`
  - `HOOK_PRE_TOOL_USE`
  - `HOOK_POST_TOOL_USE`
  - `HOOK_PRE_COMPACT`
  - `HOOK_SUBAGENT_START`
  - `HOOK_SUBAGENT_STOP`
  - `HOOK_STOP`

### Why hybrid instead of hook-only names?

- Existing Athena/reporting already understands SDLC semantic events.
- Raw hook events are more granular but do **not** fully express business meaning.
- Some hooks map cleanly to existing events; others do not.
- Hybrid keeps backward compatibility while still capturing raw runtime behavior.

---

## 2) Hook → Trace Event Mapping

## Canonical rule

- If a hook has a clear SDLC meaning, emit the **existing canonical event**.
- Always include `hook_event` and `trace_source` on hook-generated rows.
- If a hook has no clean SDLC equivalent, emit a `HOOK_*` event.

## Mapping table

| Hook | Phase 1 (double-trigger) | Phase 2 (hooks-only) | Notes |
|---|---|---|---|
| `SessionStart` | `HOOK_SESSION_START` | `RUN_START` + `HOOK_SESSION_START` | Emit `RUN_START` only once run context is bound. If not yet bound, spool raw hook event. |
| `UserPromptSubmit` | `HOOK_USER_PROMPT` | `HOOK_USER_PROMPT`; optionally `HUMAN_GATE` when classified as approve/refine response | Do **not** assume every user prompt is a gate decision. |
| `PreToolUse` | `HOOK_PRE_TOOL_USE` | `HOOK_PRE_TOOL_USE`; may update stage/run state | Useful for path discovery, tool intent, gate detection. |
| `PostToolUse` | `HOOK_POST_TOOL_USE` | `HOOK_POST_TOOL_USE`; may emit `STAGE_COMPLETE`, `VIOLATION`, `ATHENA_TRIGGER` when classifier is confident | Better place than `PreToolUse` for outcome/result fields. |
| `PreCompact` | `HOOK_PRE_COMPACT` | `HOOK_PRE_COMPACT` | No clean existing equivalent. Keep hook-specific. |
| `SubagentStart` | `HOOK_SUBAGENT_START` | `DELEGATED` + `HOOK_SUBAGENT_START` | Best canonical match. Generate `delegation_id`. |
| `SubagentStop` | `HOOK_SUBAGENT_STOP` | `SUBAGENT_RETURNED` + `HOOK_SUBAGENT_STOP` | Pair with `delegation_id` from `SubagentStart`. |
| `Stop` | `HOOK_STOP` | `RUN_COMPLETE` + `HOOK_STOP` | Emit `RUN_COMPLETE` only if run is active/bound. |

## Specific answers to mapping questions

### `SubagentStart`

Map to **`DELEGATED`** as the canonical event.

Also record:

- `hook_event: "SubagentStart"`
- `event: "DELEGATED"`
- `trace_source: "hook"`
- `delegation_id`
- `agent`
- `prompt_summary` if available/derivable

### `SubagentStop`

Map to **`SUBAGENT_RETURNED`** as the canonical event.

### `SessionStart`

Do **not** map directly to `RUN_START` until the hook layer knows the run identity (`run_id`, `feature_slug`, final trace path). Before that, emit/spool `HOOK_SESSION_START`.

### `UserPromptSubmit`

Default to **new event** `HOOK_USER_PROMPT`.

Only elevate to `HUMAN_GATE` if all are true:

1. Session state says a human gate is pending.
2. Prompt shape matches approve/refine input.
3. Current stage is known.

---

## 3) Trace Schema Additions for Hook Mode

Keep all existing fields. Add these fields for hook-generated rows:

```json
{
  "trace_source": "instruction|hook",
  "hook_event": "SessionStart|UserPromptSubmit|PreToolUse|PostToolUse|PreCompact|SubagentStart|SubagentStop|Stop",
  "session_id": "host-session-id",
  "hook_seq": 12,
  "dedupe_key": "sha1-or-uuid",
  "raw_ref": ".agentic-sdlc/state/raw/<session>.jsonl:42"
}
```

Recommended new optional fields:

- `tool_name`
- `tool_call_id`
- `tool_input_summary`
- `tool_outcome`
- `stop_reason`
- `subagent_name`
- `subagent_session_id`

### Compatibility rule

Parsers must continue to treat `event` as primary. New fields are additive only.

---

## 4) File Structure Recommendation

## Recommendation: use workspace state directory

Plugin hooks write state to the user's workspace at `.agentic-sdlc/state/`.

### Why workspace state

- Hooks must write into the **workspace** (`docs/adr/.../TRACE.jsonl`)
- Hooks need session state persisted per repository/run
- State is created in the user's workspace, not the plugin repo
- Each workspace has its own independent state
- Plugin installations are global/managed by VS Code, not per-project

### Why not in plugin source

- Plugin source is read-only after installation
- Plugin is installed to VS Code's plugin cache, not the workspace
- Multiple workspaces would share state (incorrect)
- Team members would have conflicting state in a shared repo

## Proposed layout in user's workspace

```text
user-workspace/
├── .agentic-sdlc/              # Created by plugin (gitignored)
│   ├── .gitignore              # Auto-generated
│   └── state/                  # Runtime state
│       ├── sessions/            # Per-session state
│       │   └── <session-id>.json
│       ├── raw/                 # Early event spools
│       │   └── <session-id>.jsonl
│       └── validation_reports/  # Artifact validation
│           └── <timestamp>_<agent>.json
│
└── docs/adr/                   # Your project ADRs
    └── XXX-feature/
        └── TRACE.jsonl          # Canonical trace
```

## Plugin structure (for reference)

```
.plugin/
├── hooks.json                  # Hook configuration (shipped)
├── scripts/
│   ├── trace_hook.sh           # Hook wrapper (shipped)
│   └── trace_hook.py           # Hook implementation (shipped)
└── config/
    └── artifact_requirements.json
```

---

## 5) Script Design

## Recommendation: Python, with optional shell wrapper

Use **Python** for the real implementation.

Use shell only as a tiny launcher.

### Why Python

- Reliable JSON stdin parsing
- Easier state file management
- Easier dedupe logic
- Easier path resolution and spool flush
- Easier future classification logic (gate detection, stage inference)
- Easier file locking and atomic append

### Why not pure Bash

- JSON parsing is brittle
- State merging becomes painful
- Deduplication and correlation logic will grow quickly

## Dispatcher responsibilities

1. Read JSON from stdin.
2. Normalize host payload into an internal event shape.
3. Load session state from `.agentic-sdlc/state/sessions/<session-id>.json`.
4. Resolve run binding if possible (`run_id`, `feature_slug`, `trace_path`, `stage`).
5. Decide whether to:
   - append to canonical `TRACE.jsonl`, or
   - append only to raw spool because run is not yet bound.
6. Generate `dedupe_key`.
7. Append line atomically.
8. Update session state.
9. If run binding became available, flush raw spool into canonical trace.

## Session state shape

```json
{
  "session_id": "...",
  "run_id": "2026-04-30-user-auth",
  "feature_slug": "user-auth",
  "adr_dir": "docs/adr/001-user-auth",
  "trace_path": "docs/adr/001-user-auth/TRACE.jsonl",
  "workflow_mode": "full",
  "current_stage": "3",
  "stage_iteration": {"3": 2},
  "next_hook_seq": 18,
  "active_delegations": {
    "subagent-session-1": {
      "delegation_id": "d-12",
      "agent": "implementor",
      "stage": "3"
    }
  },
  "pending_gate": {
    "stage": "3",
    "gate_id": "g-4"
  },
  "migration_phase": "phase1"
}
```

---

## 6) Double-Trigger Phase: What it Means in Practice

The user statement is correct: **first run both systems, then remove instruction logging**.

## Phase 1 = both instruction and hook logging enabled

### Rule

- **Instruction layer remains canonical** for existing SDLC events.
- **Hook layer adds raw hook observability** and correlation data.

### Concretely

- Orchestrator keeps writing current events:
  - `STAGE_START`
  - `DELEGATED`
  - `SUBAGENT_RETURNED`
  - `HUMAN_GATE`
  - `STAGE_COMPLETE`
  - `VIOLATION`
  - `ATHENA_TRIGGER`
  - `RUN_COMPLETE` / `RUN_START` if added
- Hooks write only:
  - `HOOK_*` events
  - plus metadata fields like `session_id`, `tool_call_id`, `hook_seq`, `trace_source: "hook"`

### Why this is the safest Phase 1

- No canonical event duplication
- Athena keeps working unchanged
- You can compare instruction events vs hook raw events
- You can validate that hooks capture enough information before cutover

## Deduplication in Phase 1

Use a `dedupe_key` on every hook row, but **avoid semantic dedupe by design**:

- instruction rows own canonical SDLC events
- hook rows own `HOOK_*` events

So there is nothing to merge semantically yet.

## Phase 1 optional enhancement

If you want stronger comparison, add `canonical_candidate` on hook rows:

```json
{
  "event": "HOOK_SUBAGENT_START",
  "canonical_candidate": "DELEGATED"
}
```

That lets Athena/reporting compare expected future mapping without creating duplicate canonical rows.

---

## 7) Phase 2 = Hooks-Only

After Phase 1 proves parity, switch ownership:

- Hooks emit canonical SDLC events.
- Orchestrator stops appending to `TRACE.jsonl`.
- Orchestrator may still help with run binding if needed, but should no longer be the trace writer.

## Phase 2 ownership by event

| Event | Owner |
|---|---|
| `RUN_START` | hook layer |
| `STAGE_START` | hook layer or lightweight orchestrator state signal |
| `DELEGATED` | hook layer (`SubagentStart`) |
| `SUBAGENT_RETURNED` | hook layer (`SubagentStop`) |
| `HUMAN_GATE` | hook layer (`UserPromptSubmit` classifier) |
| `STAGE_COMPLETE` | hook layer (`PostToolUse`/stage transition classifier) |
| `VIOLATION` | hook layer when forbidden tool/workflow pattern detected |
| `ATHENA_TRIGGER` | hook layer or Athena integration point |
| `RUN_COMPLETE` | hook layer (`Stop`) |

## Important caveat

`STAGE_START`, `STAGE_COMPLETE`, `HUMAN_GATE`, `VIOLATION`, and `ATHENA_TRIGGER` are **semantic** events. Hooks can emit them only if there is enough local state/classification confidence.

If confidence is low, keep emitting raw `HOOK_*` plus a small helper state file from the orchestrator rather than guessing.

---

## 8) Migration Plan

## Phase 0 — Preparation

1. Add hook assets under `.github/hooks/trace/`.
2. Add hook state directory under `.agentic-sdlc/state/`.
3. Extend trace schema with additive hook fields.
4. Add `RUN_START` and `run_id` to instruction-mode trace if not already present.

## Phase 1 — Double Trigger

1. Keep orchestrator trace logic unchanged.
2. Turn on hooks writing `HOOK_*` events only.
3. Add parity checks:
   - every `DELEGATED` should have nearby `HOOK_SUBAGENT_START`
   - every `SUBAGENT_RETURNED` should have nearby `HOOK_SUBAGENT_STOP`
   - every run should have `HOOK_SESSION_START` and `HOOK_STOP`
4. Add Athena/report tooling to compare semantic parity.

**Exit criteria for Phase 1:**

- Hook data is captured for >95% of runs.
- `SubagentStart/SubagentStop` parity with `DELEGATED/SUBAGENT_RETURNED` is stable.
- Path binding works without manual repair.
- No corruption/race issues in `TRACE.jsonl`.

## Phase 2 — Hybrid Cutover

1. Turn on canonical hook emission for:
   - `RUN_START`
   - `DELEGATED`
   - `SUBAGENT_RETURNED`
   - `RUN_COMPLETE`
2. Keep orchestrator writing only the events hooks cannot yet derive reliably:
   - `STAGE_START`
   - `HUMAN_GATE`
   - `STAGE_COMPLETE`
   - `VIOLATION`
   - `ATHENA_TRIGGER`
3. Validate parity again.

## Phase 3 — Hooks Only

1. Remove orchestrator trace append instructions.
2. Keep a tiny orchestrator-side state signal only if needed for stage/gate binding.
3. Athena consumes one trace stream again.

---

## 9) Handling Unknown `feature_slug` in Early Hooks

This is the hardest part.

## Recommendation: two-stage write path

### Stage A: raw session spool

Before the final trace path is known, hooks write to:

```text
.agentic-sdlc/state/raw/<session-id>.jsonl
```

### Stage B: canonical trace append

After run binding is known, hooks append to:

```text
docs/adr/XXX-<feature-slug>/TRACE.jsonl
```

Then flush the raw spool into the canonical trace in original order.

## Binding resolution order

The hook script should resolve trace path using this order:

1. **Session state** already contains `trace_path`.
2. **Environment variables** if host supports them:
   - `AGENTIC_SDLC_RUN_ID`
   - `AGENTIC_SDLC_FEATURE_SLUG`
   - `AGENTIC_SDLC_TRACE_PATH`
   - `AGENTIC_SDLC_STAGE`
3. **Tool payload detection**:
   - if `PreToolUse`/`PostToolUse` touches `docs/adr/.../TRACE.jsonl`, bind immediately.
4. **Prompt parsing** from `UserPromptSubmit`:
   - detect explicit `001-user-auth`
   - detect feature slug patterns
5. **Run manifest file** written by orchestrator/helper:
   - `.agentic-sdlc/state/sessions/<session-id>.json`

## Best practical answer

Yes: **use a temp/spool location initially, then flush**.

Do **not** guess the final ADR path before you have a definitive signal.

---

## 10) Data Availability in Hooks

## Expectation management

Exact JSON fields available on stdin depend on the host implementation.

Assume only these are likely reliable:

- hook name / event name
- timestamp
- session id
- for tool hooks: tool name + input, maybe result metadata
- for subagent hooks: subagent name/session if host exposes them
- for stop hook: reason/status if host exposes it

## Do not assume hooks provide these directly

- `run_id`
- `feature_slug`
- `stage`
- ADR number/path
- semantic gate decision
- agent role in SDLC terms

Those should be derived from:

- persisted session state
- tool payload inspection
- prompt classification
- orchestrator helper state

## Recommendation

Treat stdin payload as **raw transport**, not complete business context.

Persist your own normalized state.

---

## 11) Recommended State + Correlation Model

## IDs

- `run_id`: once per SDLC run
- `session_id`: host chat session
- `delegation_id`: once per subagent start/stop pair
- `gate_id`: once per review gate
- `hook_seq`: monotonic per session
- `dedupe_key`: per emitted row

## Pairing logic

- `SubagentStart` creates `delegation_id`
- store by `subagent_session_id` or `tool_call_id`
- `SubagentStop` resolves same `delegation_id`
- `UserPromptSubmit` resolves `gate_id` only if `pending_gate` exists

---

## 12) Example Hook Config

> This is an implementation template. Adjust field names to the final VS Code/Copilot hook schema.

```json
{
  "hooks": {
    "SessionStart": [
      {
        "type": "command",
        "command": ".github/hooks/trace/trace_hook.sh SessionStart"
      }
    ],
    "UserPromptSubmit": [
      {
        "type": "command",
        "command": ".github/hooks/trace/trace_hook.sh UserPromptSubmit"
      }
    ],
    "PreToolUse": [
      {
        "type": "command",
        "command": ".github/hooks/trace/trace_hook.sh PreToolUse"
      }
    ],
    "PostToolUse": [
      {
        "type": "command",
        "command": ".github/hooks/trace/trace_hook.sh PostToolUse"
      }
    ],
    "PreCompact": [
      {
        "type": "command",
        "command": ".github/hooks/trace/trace_hook.sh PreCompact"
      }
    ],
    "SubagentStart": [
      {
        "type": "command",
        "command": ".github/hooks/trace/trace_hook.sh SubagentStart"
      }
    ],
    "SubagentStop": [
      {
        "type": "command",
        "command": ".github/hooks/trace/trace_hook.sh SubagentStop"
      }
    ],
    "Stop": [
      {
        "type": "command",
        "command": ".github/hooks/trace/trace_hook.sh Stop"
      }
    ]
  }
}
```

## Wrapper script

```bash
#!/usr/bin/env bash
set -euo pipefail

HOOK_EVENT="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

python3 "$SCRIPT_DIR/trace_hook.py" --hook-event "$HOOK_EVENT"
```

---

## 13) Example Python Implementation (practical skeleton)

```python
#!/usr/bin/env python3
import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path.cwd()
STATE_DIR = ROOT / ".github" / "hooks" / "state"
SESSIONS_DIR = STATE_DIR / "sessions"
RAW_DIR = STATE_DIR / "raw"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_stdin_json() -> dict:
    try:
        return json.load(os.sys.stdin)
    except Exception:
        return {}


def get_session_id(payload: dict) -> str:
    return (
        payload.get("sessionId")
        or payload.get("session_id")
        or payload.get("chatSessionId")
        or "unknown-session"
    )


def load_state(session_id: str) -> dict:
    path = SESSIONS_DIR / f"{session_id}.json"
    if path.exists():
        return json.loads(path.read_text())
    return {
        "session_id": session_id,
        "next_hook_seq": 1,
        "active_delegations": {},
        "stage_iteration": {},
    }


def save_state(state: dict) -> None:
    SESSIONS_DIR.mkdir(parents=True, exist_ok=True)
    path = SESSIONS_DIR / f"{state['session_id']}.json"
    path.write_text(json.dumps(state, indent=2, sort_keys=True))


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def compute_dedupe_key(row: dict) -> str:
    stable = "|".join(
        str(row.get(k, ""))
        for k in ["trace_source", "hook_event", "session_id", "hook_seq", "event", "agent", "stage"]
    )
    return hashlib.sha1(stable.encode("utf-8")).hexdigest()


def maybe_bind_run(state: dict, payload: dict) -> None:
    if state.get("trace_path"):
        return

    env_trace = os.getenv("AGENTIC_SDLC_TRACE_PATH")
    if env_trace:
        state["trace_path"] = env_trace
        state["run_id"] = os.getenv("AGENTIC_SDLC_RUN_ID")
        state["feature_slug"] = os.getenv("AGENTIC_SDLC_FEATURE_SLUG")
        return

    tool_input = payload.get("toolInput") or payload.get("tool_input") or {}
    text = json.dumps(tool_input)
    marker = "docs/adr/"
    if marker in text and "TRACE.jsonl" in text:
        # Real implementation should extract the exact path via regex.
        # This is left simplified here.
        state["trace_path"] = "docs/adr/XXX-feature-slug/TRACE.jsonl"


def to_rows(hook_event: str, payload: dict, state: dict) -> list[dict]:
    base = {
        "ts": now_iso(),
        "trace_source": "hook",
        "hook_event": hook_event,
        "session_id": state["session_id"],
        "hook_seq": state["next_hook_seq"],
        "run_id": state.get("run_id"),
        "feature_slug": state.get("feature_slug"),
        "stage": state.get("current_stage"),
    }

    rows = []

    if hook_event == "SessionStart":
        rows.append({**base, "event": "HOOK_SESSION_START"})

    elif hook_event == "UserPromptSubmit":
        text = payload.get("prompt") or payload.get("text") or ""
        rows.append({**base, "event": "HOOK_USER_PROMPT", "prompt_summary": text[:200]})
        if state.get("pending_gate") and text.lower().startswith(("approve", "refine")):
            rows.append({
                **base,
                "event": "HUMAN_GATE",
                "gate_id": state["pending_gate"]["gate_id"],
                "decision": "approve" if text.lower().startswith("approve") else "refine",
                "feedback_summary": text[:200],
            })

    elif hook_event == "SubagentStart":
        agent = payload.get("agent") or payload.get("subagent") or "unknown"
        delegation_id = f"d-{state['next_hook_seq']}"
        rows.append({
            **base,
            "event": "DELEGATED" if state.get("migration_phase") == "phase2" else "HOOK_SUBAGENT_START",
            "agent": agent,
            "delegation_id": delegation_id,
        })
        state["active_delegations"][agent] = {"delegation_id": delegation_id, "agent": agent}

    elif hook_event == "SubagentStop":
        agent = payload.get("agent") or payload.get("subagent") or "unknown"
        active = state.get("active_delegations", {}).get(agent, {})
        rows.append({
            **base,
            "event": "SUBAGENT_RETURNED" if state.get("migration_phase") == "phase2" else "HOOK_SUBAGENT_STOP",
            "agent": agent,
            "delegation_id": active.get("delegation_id"),
            "outcome": payload.get("outcome", "success"),
        })

    elif hook_event == "Stop":
        rows.append({**base, "event": "HOOK_STOP", "stop_reason": payload.get("reason")})
        if state.get("migration_phase") == "phase2" and state.get("run_id"):
            rows.append({**base, "event": "RUN_COMPLETE", "status": "success"})

    else:
        rows.append({**base, "event": f"HOOK_{hook_event.upper()}"})

    for row in rows:
        row["dedupe_key"] = compute_dedupe_key(row)

    return rows


def flush_raw_if_bound(state: dict) -> None:
    trace_path = state.get("trace_path")
    if not trace_path:
        return
    raw_path = RAW_DIR / f"{state['session_id']}.jsonl"
    if not raw_path.exists():
        return
    trace_file = ROOT / trace_path
    for line in raw_path.read_text().splitlines():
        trace_file.parent.mkdir(parents=True, exist_ok=True)
        with trace_file.open("a", encoding="utf-8") as f:
            f.write(line + "\n")
    raw_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hook-event", required=True)
    args = parser.parse_args()

    payload = load_stdin_json()
    session_id = get_session_id(payload)
    state = load_state(session_id)
    maybe_bind_run(state, payload)

    rows = to_rows(args.hook_event, payload, state)
    target = ROOT / state["trace_path"] if state.get("trace_path") else RAW_DIR / f"{session_id}.jsonl"
    for row in rows:
        append_jsonl(target, row)

    state["next_hook_seq"] += 1
    save_state(state)
    flush_raw_if_bound(state)


if __name__ == "__main__":
    main()
```

---

## 14) Practical Decisions for the Current Repo

## Recommended decisions

1. **Location**: runtime hooks live in `.github/hooks/trace/`.
2. **Language**: Python implementation + shell wrapper.
3. **Phase 1 behavior**: hooks append `HOOK_*` events only; orchestrator remains canonical writer.
4. **Phase 2 behavior**: hooks take over `RUN_START`, `DELEGATED`, `SUBAGENT_RETURNED`, `RUN_COMPLETE` first.
5. **Unknown path handling**: always spool to `.agentic-sdlc/state/raw/<session-id>.jsonl` until trace path is known.
6. **State model**: persist repo-local session state under `.agentic-sdlc/state/sessions/`.
7. **Trace schema**: add `trace_source`, `hook_event`, `session_id`, `hook_seq`, `dedupe_key`; keep all existing fields unchanged.

---

## 15) What Must Change in the Orchestrator

During migration, the orchestrator should be reduced from "trace writer" to "trace context producer".

## Phase 1

Keep current trace instructions, but add these improvements:

1. Emit `RUN_START` with `run_id`, `feature_slug`, `workflow_mode`, `expected_stages`.
2. Generate stable `delegation_id` and `gate_id` now.
3. Optionally write a small run manifest consumable by hooks.

Example manifest path:

```text
.agentic-sdlc/state/sessions/<session-id>.json
```

This is optional but greatly simplifies hook cutover.

## Phase 2+

Remove append-to-TRACE instructions and keep only:

- stage/gate/run context signaling if hooks still need help
- Athena behavior and human workflow semantics

---

## 16) Acceptance Criteria for Migration

Migration is complete when:

1. Hook-generated traces preserve all required Athena inputs.
2. `DELEGATED` ↔ `SUBAGENT_RETURNED` pairing is reliable.
3. Early-session events are never lost before feature slug/path resolution.
4. `TRACE.jsonl` remains append-only JSONL and backward compatible.
5. Double-trigger phase produces no canonical duplicate events.
6. Removing orchestrator trace edits does not reduce observability coverage.

---

## Final Recommendation

Implement this as a **3-step migration**:

1. **Phase 1:** instruction events remain canonical, hooks add `HOOK_*` events and state.
2. **Phase 2:** hooks take over the easy canonical lifecycle events (`RUN_START`, `DELEGATED`, `SUBAGENT_RETURNED`, `RUN_COMPLETE`).
3. **Phase 3:** hooks own `TRACE.jsonl`; orchestrator stops writing trace lines.

The key enabling pattern is:

- **repo-local hook runtime in `.github/hooks/`**
- **Python dispatcher**
- **session-state persistence**
- **raw spool before final path binding**
- **hybrid canonical + hook-native event model**

That gives a practical, low-risk path from the current instruction-based model to deterministic hook-based trace generation.

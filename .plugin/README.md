# Trace Generation Hooks

This directory contains VS Code Copilot Agent hooks for automatic trace.jsonl generation during the Agentic SDLC workflow.

## Overview

The hooks implement Phase 1 of the trace migration strategy:
- Hooks write `HOOK_*` events to TRACE.jsonl
- Orchestrator remains the canonical writer for SDLC semantic events
- This provides double-trigger observability during the migration period

**Artifact Validation**: Automatically validates that agents produce their required artifacts (e.g., PO → REQUIREMENTS.md, Architect → PLAN.md)

## File Structure

```
.plugin/
├── plugin.json              # Plugin manifest (registers hooks)
├── hooks.json               # Hook configuration for 8 lifecycle events
└── scripts/
    ├── trace_hook.sh        # Shell wrapper
    └── trace_hook.py        # Python dispatcher (main implementation)
```

## Supported Lifecycle Events

| Hook Event | Trace Event | Description |
|------------|-------------|-------------|
| SessionStart | HOOK_SESSION_START | When a new session begins |
| UserPromptSubmit | HOOK_USER_PROMPT | When user submits a prompt |
| PreToolUse | HOOK_PRE_TOOL_USE | Before a tool is invoked |
| PostToolUse | HOOK_POST_TOOL_USE | After a tool completes |
| PreCompact | HOOK_PRE_COMPACT | Before context compaction |
| SubagentStart | HOOK_SUBAGENT_START | When a subagent spawns |
| SubagentStop | HOOK_SUBAGENT_STOP | When a subagent completes |
| Stop | HOOK_STOP | When a session ends |

## Artifact Validation

When agents complete (SubagentStop), hooks automatically validate they produced required artifacts:

| Agent | Required Artifact | Validation Criteria |
|-------|-----------------|---------------------|
| PO | REQUIREMENTS.md | File exists, size > 100 bytes, has required sections |
| Architect | PLAN.md | File exists, size > 100 bytes, has required sections |
| Implementor | Code files | At least 1 code file, minimum total size |
| QA Lead | QA_REPORT.md | File exists, size > 100 bytes, has required sections |
| Tech Writer | ADR.md | File exists, size > 100 bytes, has required sections |
| CTO | PLAN.md approval | Contains approval marker (approved, ✓, etc.) |
| PR Reviewer | PR Feedback | File exists, size > 50 bytes |

**Configuration**: `.plugin/config/artifact_requirements.json`

**Documentation**: See [.plugin/docs/ARTIFACT_VALIDATION.md](docs/ARTIFACT_VALIDATION.md)

**Trace Event**: `ARTIFACT_VALIDATION` events logged to TRACE.jsonl with validation results

**Validation Reports**: Saved to `.agentic-sdlc/state/validation_reports/`

## Setup

### Prerequisites

1. **Python 3.8+** installed and available in PATH
2. **VS Code Copilot Agent Plugins** enabled
3. **Agentic SDLC plugin** installed

### Installation

The hooks are automatically registered when you install the agentic-sdlc plugin. No manual setup required.

### Verification

To verify hooks are running:

1. Start an SDLC run with the orchestrator agent
2. Check for hook-generated events in TRACE.jsonl:
   ```bash
   grep "HOOK_" docs/adr/*/TRACE.jsonl
   ```
3. Check session state in `.agentic-sdlc/state/sessions/`

## Troubleshooting

### Hooks not firing

**Symptom**: No HOOK_* events in TRACE.jsonl

**Solutions**:
1. Verify plugin is enabled in VS Code
2. Check `chat.plugins.enabled` setting is `true`
3. Look for errors in VS Code Output panel (Copilot channel)
4. Verify Python 3 is available: `python3 --version`

### Permission errors

**Symptom**: Hooks fail with "Permission denied"

**Solutions**:
1. Make scripts executable:
   ```bash
   chmod +x .plugin/scripts/trace_hook.sh
   ```
2. Check file permissions on `.agentic-sdlc/state/` directory

### Trace file not found

**Symptom**: Events written to raw spool instead of TRACE.jsonl

**Explanation**: This is expected behavior in Phase 1. Before the orchestrator binds the run (writes manifest), hooks write to:
```
.agentic-sdlc/state/raw/<session-id>.jsonl
```

**Solutions**:
1. Verify orchestrator is creating run manifest
2. Check environment variables are set (if using MCP mode)
3. Events will flush to canonical TRACE.jsonl once run is bound

### Missing Python

**Symptom**: "python3: command not found" errors

**Solutions**:
1. Install Python 3.8+ from [python.org](https://python.org)
2. Ensure Python is in your system PATH
3. On Windows, you may need to use `py` instead of `python3`

## State Files

The plugin creates state in the **user's workspace** at `.agentic-sdlc/state/`:

```
.agentic-sdlc/state/
├── sessions/
│   └── <session-id>.json        # Live session/run state
└── raw/
    └── <session-id>.jsonl       # Unbound hook events spool
```

**Important**: This directory is automatically ignored by Git. The plugin creates a `.gitignore` entry to ensure plugin state is never committed to the user's repository.

### Session State Format

```json
{
  "session_id": "...",
  "run_id": "2026-04-30-user-auth",
  "feature_slug": "user-auth",
  "trace_path": "docs/adr/001-user-auth/TRACE.jsonl",
  "workflow_mode": "full",
  "current_stage": "3",
  "stage_iteration": {"3": 2},
  "next_hook_seq": 18,
  "active_delegations": {},
  "pending_gate": {},
  "migration_phase": "phase1"
}
```

## Migration Phases

### Phase 1 (Current)
- Hooks write `HOOK_*` events
- Orchestrator writes canonical SDLC events
- Double-trigger for validation and parity checks

### Phase 2 (Future)
- Hooks take over canonical events: RUN_START, DELEGATED, SUBAGENT_RETURNED, RUN_COMPLETE
- Orchestrator reduces trace writing

### Phase 3 (Future)
- Hooks own all trace generation
- Orchestrator stops writing trace lines

See `docs/TRACE_HOOK_MIGRATION.md` for complete migration strategy.

## Trace Schema

Hook-generated events include these fields:

```json
{
  "ts": "2026-04-30T12:00:00.000Z",
  "event": "HOOK_SESSION_START",
  "trace_source": "hook",
  "hook_event": "SessionStart",
  "session_id": "sess_abc123",
  "hook_seq": 1,
  "run_id": "2026-04-30-user-auth",
  "feature_slug": "user-auth",
  "stage": "0",
  "dedupe_key": "abc123...",
  "cwd": "/workspace"
}
```

## Performance Impact

Minimal overhead:
- Hook execution: < 10ms per event
- File I/O: append-only, atomic
- No blocking of agent workflow

## Security Considerations

- Hooks run with same permissions as VS Code
- Only write to workspace directories
- No external network calls
- No execution of untrusted code

## Contributing

When modifying hooks:

1. Update this README
2. Update migration strategy document
3. Test with both instruction-only and MCP-integrated modes
4. Verify backward compatibility with Athena

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review `docs/TRACE_HOOK_MIGRATION.md`
3. Check VS Code Output panel for errors
4. Open an issue on GitHub

## Related Documentation

- [Trace Hook Migration Strategy](../docs/TRACE_HOOK_MIGRATION.md)
- [Observability Architecture](../docs/OBSERVABILITY.md)
- [VS Code Copilot Agent Plugins Documentation](https://code.visualstudio.com/docs/copilot/agent-plugins)

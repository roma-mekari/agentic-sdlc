# Manual Testing Guide for Phase 1 Hooks

This guide provides step-by-step instructions for manually testing the trace generation hooks in Phase 1.

## Prerequisites

1. **Python 3.8+** installed and available in PATH
2. **VS Code** with Copilot enabled
3. **Agentic SDLC plugin** installed from this repository
4. **Test workspace** with the plugin enabled

## Quick Validation (Before Manual Testing)

Run the automated validation script:

```bash
python3 tests/validate_hooks.py
```

All 7 checks should pass:
- ✓ Python syntax
- ✓ Hooks JSON
- ✓ Hook configuration
- ✓ Plugin manifest
- ✓ Script permissions
- ✓ Python version
- ✓ State directory

## Test 1: Plugin Installation

### Steps

1. **Install the plugin**:
   - Open VS Code Command Palette (Cmd+Shift+P / Ctrl+Shift+P)
   - Run `Chat: Install Plugin From Source`
   - Enter: `https://github.com/roma-mekari/agentic-sdlc`
   - Wait for installation to complete

2. **Verify plugin is enabled**:
   - Open Extensions view (Cmd+Shift+X / Ctrl+Shift+X)
   - Search for `@agentPlugins`
   - Verify `agentic-sdlc` appears in the list
   - Ensure it's enabled (not dimmed)

3. **Check plugin registration**:
   - Open Chat view
   - Run `Chat: Configure Skills`
   - Verify plugin skills/agents appear (if any are defined)
   - Run `MCP: List Servers` to check for any MCP servers

### Expected Results

- Plugin installs without errors
- Plugin appears in installed plugins list
- No error messages in VS Code Output panel

### Troubleshooting

**Issue**: Plugin doesn't appear in list
- Check `chat.plugins.enabled` setting is `true`
- Check for errors in VS Code Output → Copilot channel
- Verify plugin.json has valid `name` field (lowercase, kebab-case)

**Issue**: Installation fails
- Check network connectivity
- Verify repository URL is correct
- Check for permission errors

## Test 2: Basic Hook Execution

### Steps

1. **Start a new chat session**:
   - Open Chat view
   - Type a simple message: `Hello`

2. **Monitor VS Code Output**:
   - Open Output panel (View → Output)
   - Select "Copilot" channel
   - Watch for hook execution messages

3. **Check for state files**:
   ```bash
   ls -la .agentic-sdlc/state/sessions/
   ls -la .agentic-sdlc/state/raw/
   ```

### Expected Results

- Session state file created: `.agentic-sdlc/state/sessions/<session-id>.json`
- No raw spool yet (run not bound)
- No errors in Output panel
- Hook executed without blocking the response

### Validation

```bash
# Check session state exists
test -f .agentic-sdlc/state/sessions/*.json && echo "✓ Session state created"

# Check state has required fields
cat .agentic-sdlc/state/sessions/*.json | python3 -m json.tool

# Should see:
# {
#   "session_id": "...",
#   "next_hook_seq": 1,
#   "active_delegations": {},
#   "stage_iteration": {},
#   "migration_phase": "phase1"
# }
```

## Test 3: SDLC Workflow with Hooks

### Steps

1. **Initialize workspace** (if not already done):
   - Run `/init-workspace` skill
   - Verify directories are created

2. **Start SDLC orchestrator**:
   - Open Chat view
   - Invoke: `@sdlc-orchestrator`
   - Provide a simple feature request: "Add user authentication with login page"

3. **Let the workflow run through Stage 0** (Context Discovery):
   - Watch as orchestrator delegates to Explorer agent
   - Observe SubagentStart and SubagentStop hooks firing

4. **Check for hook events**:
   ```bash
   # Look for HOOK_* events in any TRACE.jsonl files
   find docs/adr -name "TRACE.jsonl" -exec grep "HOOK_" {} +

   # Check raw spool if run not yet bound
   cat .agentic-sdlc/state/raw/*.jsonl
   ```

### Expected Results

- HOOK_SESSION_START appears (session initialization)
- HOOK_USER_PROMPT appears (your feature request)
- HOOK_SUBAGENT_START appears (explorer delegation)
- HOOK_SUBAGENT_STOP appears (explorer completion)
- HOOK_PRE_TOOL_USE / HOOK_POST_TOOL_USE for tool calls
- Events appear in TRACE.jsonl if run bound, or in raw spool if not
- No duplicate canonical events (STAGE_START, DELEGATED, etc. come from orchestrator)

### Validation Commands

```bash
# Count hook events
HOOK_COUNT=$(find docs/adr -name "TRACE.jsonl" -exec grep -c "HOOK_" {} + 2>/dev/null | awk '{s+=$1} END {print s}')
echo "Hook events found: $HOOK_COUNT"

# Check for duplicate canonical events (should be 0)
DELEGATED_COUNT=$(find docs/adr -name "TRACE.jsonl" -exec grep -c '"event":"DELEGATED"' {} + 2>/dev/null | awk '{s+=$1} END {print s}')
HOOK_DELEGATED_COUNT=$(find docs/adr -name "TRACE.jsonl" -exec grep -c '"event":"DELEGATED".*"trace_source":"hook"' {} + 2>/dev/null | awk '{s+=$1} END {print s}')

if [ "$HOOK_DELEGATED_COUNT" -eq 0 ]; then
    echo "✓ No hook-generated DELEGATED events (correct for Phase 1)"
else
    echo "✗ Found $HOOK_DELEGATED_COUNT hook-generated DELEGATED events (should be 0)"
fi
```

## Test 4: Event Ordering and Completeness

### Steps

1. **Run a complete Stage 0 workflow** (as in Test 3)

2. **Extract and order events**:
   ```bash
   # Get all events from TRACE.jsonl
   cat docs/adr/*/TRACE.jsonl | jq -r '.event' | nl

   # Should see sequence like:
   # 1  HOOK_SESSION_START
   # 2  HOOK_USER_PROMPT
   # 3  RUN_START (from orchestrator)
   # 4  STAGE_START (from orchestrator)
   # 5  HOOK_SUBAGENT_START
   # 6  DELEGATED (from orchestrator)
   # 7  HOOK_SUBAGENT_STOP
   # 8  SUBAGENT_RETURNED (from orchestrator)
   ```

3. **Verify hook_seq is monotonic**:
   ```bash
   cat docs/adr/*/TRACE.jsonl | jq -r 'select(.hook_seq != null) | .hook_seq' | sort -n | uniq -d
   # Should return nothing (no duplicates)
   ```

### Expected Results

- Events are in chronological order
- hook_seq increases monotonically (no duplicates)
- HOOK_* events interleave appropriately with orchestrator events
- No events missing

## Test 5: Raw Spool Flush

### Steps

1. **Start a new session** (before orchestrator binds run):
   - Send a simple message
   - Check raw spool has events

2. **Let orchestrator bind the run**:
   - Run `/sdlc-orchestrator` with a feature
   - Wait for RUN_START to appear in TRACE.jsonl

3. **Check spool was flushed**:
   ```bash
   # Raw spool should be empty or deleted
   ls -la .agentic-sdlc/state/raw/

   # All events should now be in TRACE.jsonl
   cat docs/adr/*/TRACE.jsonl | grep "HOOK_SESSION_START"
   ```

### Expected Results

- Early events appear in raw spool initially
- After run binding, spool is flushed to TRACE.jsonl
- Raw spool file is deleted
- All events appear in canonical TRACE.jsonl in correct order

## Test 6: Error Resilience

### Steps

1. **Corrupt session state**:
   ```bash
   echo "invalid json" > .agentic-sdlc/state/sessions/test-corrupt.json
   ```

2. **Send a chat message**

3. **Verify hooks still work**:
   - Hook should not crash
   - New session state should be created (recovering from corruption)
   - Chat should respond normally

### Expected Results

- Hooks don't crash on corrupted state
- New valid state file is created
- Agent workflow continues normally
- Error logged in VS Code Output but doesn't block

## Test 7: Performance Check

### Steps

1. **Run a complete Stage 0** (as in Test 3)

2. **Measure hook execution time** (optional - add timing to trace_hook.py):
   - Add `import time` at top
   - Wrap main logic with timing
   - Log duration to stderr

3. **Check for perceptible delays**:
   - Observe if hooks cause noticeable lag
   - Compare to non-hooked agent responses

### Expected Results

- No perceptible lag in agent responses
- Hook execution < 10ms per event
- Total overhead < 100ms for typical workflow

## Test 8: All 8 Hook Events

### Steps

1. **Run a complete SDLC workflow** through at least one full stage

2. **Verify all 8 event types appear**:
   ```bash
   cat docs/adr/*/TRACE.jsonl | jq -r '.event' | grep "HOOK_" | sort | uniq -c
   ```

### Expected Output

```
      1 HOOK_POST_TOOL_USE
      2 HOOK_PRE_TOOL_USE
      1 HOOK_SESSION_START
      3 HOOK_SUBAGENT_START
      3 HOOK_SUBAGENT_STOP
      1 HOOK_STOP
      1 HOOK_USER_PROMPT
```

(Counts will vary based on workflow)

### Expected Results

- All 8 hook event types appear at least once
- HOOK_PRE_COMPACT appears if context compaction occurs
- Event counts match workflow behavior

## Test 9: Backward Compatibility

### Steps

1. **Run SDLC workflow with hooks enabled**

2. **Verify Athena can still parse TRACE.jsonl**:
   - If you have Athena integration, run post-run analysis
   - Check that Athena processes all events correctly

3. **Verify existing trace consumers work**:
   - Any tools/scripts that parse TRACE.jsonl should still work
   - HOOK_* events should be ignored or treated as additional metadata

### Expected Results

- Existing trace consumers don't break
- HOOK_* events are additive, not breaking
- Athena/reporting tools handle new fields gracefully

## Test 10: Multi-Session Isolation

### Steps

1. **Open two separate chat sessions** in VS Code (different tabs)

2. **Send messages in both**

3. **Verify state isolation**:
   ```bash
   ls -la .agentic-sdlc/state/sessions/
   # Should see two separate session files
   ```

4. **Check events go to correct traces**:
   - Each session should have its own session_id
   - Events shouldn't cross-contaminate

### Expected Results

- Each session has unique state file
- Events have correct session_id
- No cross-session contamination

## Cleanup After Testing

```bash
# Remove test state
rm -rf .agentic-sdlc/state/

# Remove test ADR directories (careful!)
# rm -rf docs/adr/

# Keep TRACE.jsonl for analysis
```

## Test Results Summary

Create a test report with:

```
Test Results Summary
===================

Test 1: Plugin Installation - PASSED / FAILED
Test 2: Basic Hook Execution - PASSED / FAILED
Test 3: SDLC Workflow - PASSED / FAILED
Test 4: Event Ordering - PASSED / FAILED
Test 5: Raw Spool Flush - PASSED / FAILED
Test 6: Error Resilience - PASSED / FAILED
Test 7: Performance - PASSED / FAILED
Test 8: All 8 Events - PASSED / FAILED
Test 9: Backward Compatibility - PASSED / FAILED
Test 10: Multi-Session - PASSED / FAILED

Overall: X/10 PASSED

Issues Found:
- [List any issues discovered]

Notes:
- [Any additional observations]
```

## Known Limitations in Phase 1

1. **Hooks write HOOK_* events only** - Canonical events still come from orchestrator
2. **Run binding relies on orchestrator** - Hooks can't fully determine run_id/feature_slug alone
3. **HUMAN_GATE detection not implemented** - Hooks emit raw USER_PROMPT, not classified gates
4. **No automatic stage detection** - Hooks don't infer current stage from tool usage

## Next Phase (Phase 2) Preparation

After Phase 1 passes all tests:

1. Enable hooks to emit canonical events (RUN_START, DELEGATED, SUBAGENT_RETURNED, RUN_COMPLETE)
2. Add HUMAN_GATE classification logic
3. Validate parity with orchestrator events
4. Remove orchestrator trace append instructions for migrated events

See `docs/TRACE_HOOK_MIGRATION.md` for Phase 2 details.

## Troubleshooting Common Issues

### Hooks not firing
- Check VS Code Output → Copilot for errors
- Verify plugin is enabled
- Check Python is in PATH

### Events in raw spool only
- Expected before run binding
- Check orchestrator creates run manifest
- Or set env vars: AGENTIC_SDLC_RUN_ID, AGENTIC_SDLC_TRACE_PATH

### Duplicate events
- Verify migration_phase is "phase1"
- Check hooks aren't set to emit canonical events

### State files not created
- Check write permissions on `.agentic-sdlc/state/`
- Verify hooks have execute permissions
- Check Python script syntax (run validator)

### Performance issues
- Profile hook execution time
- Check for file I/O bottlenecks
- Verify no blocking operations in hooks

## Support

If you encounter issues:
1. Run `python3 tests/validate_hooks.py`
2. Check VS Code Output panel
3. Review troubleshooting sections above
4. See `.plugin/README.md` for detailed setup guide
5. Open an issue on GitHub with test results

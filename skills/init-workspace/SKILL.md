---
name: "init-workspace"
description: "Initialize the current workspace for the Agentic SDLC workflow. Creates the required directory structure and workflow templates that the SDLC agents depend on."
---

# Initialize Workspace for Agentic SDLC

You are setting up the current workspace to work with the Agentic SDLC plugin. The SDLC agents expect certain files and directories to exist in the workspace.

## What to Create

### 1. Directory Structure

Create these directories if they don't exist:
- `docs/adr/` — where feature ADRs and supporting artifacts are stored
- `docs/athena/` — where Athena meta-analysis reflections and reports are stored

### 2. Workflow Templates

Verify that workflow templates are accessible from the plugin and copy them if needed.

The templates are:
- `REQUIREMENTS.md` — Used by the PO agent
- `PLAN.md` — Used by the Architect agent
- `QA_REPORT.md` — Used by the QA Lead agent
- `ADR.md` — Used by the Tech Writer agent
- `ATHENA_REPORT.md` — Used by the Athena agent
- `PR_FEEDBACK.md` — Used by the PR Reviewer agent
- `RFC.md` — Used by the RFC Writer agent
- `FEATURE_SPEC.md` — Used by the Tech Writer agent for living feature documentation

### 3. Copilot Settings (Optional)

If the team wants to recommend this plugin for all contributors, create `.github/copilot/settings.json`:

```json
{
  "enabledPlugins": {
    "agentic-sdlc": true
  }
}
```

## Process

1. **Check accessibility**:
   - Verify the `workflow_templates/` directory exists in the plugin source
   - Check that all 8 template files are present and readable
   - Report any missing or inaccessible files

2. **Create directories**:
   - Create `docs/adr/` if it doesn't exist
   - Create `docs/athena/` if it doesn't exist

3. **Verify template accessibility**:
   - Check if templates are accessible from the plugin
   - Test that files can be read and copied
   - Report any access issues

4. **Report status**:
   - List directories created
   - List accessible templates
   - List any issues or warnings
   - Provide next steps

## Note on Project Context

The SDLC workflow does NOT require a project configuration file. On each run, the orchestrator's Stage 0 uses the Explorer agent to automatically detect the project's language, framework, architecture, and conventions from the codebase. This context is passed to all subagents.

## Template Accessibility

Templates are provided by the plugin and should be accessible at runtime. If you encounter issues:
1. Verify the plugin is installed correctly
2. Check VS Code Output panel for plugin errors
3. Ensure `chat.plugins.enabled` is `true`
4. Try reinstalling the plugin

## Output

After setup, confirm:
```
Workspace initialized for Agentic SDLC.

Directories created:
✓ docs/adr/
✓ docs/athena/

Workflow templates accessibility:
✓ REQUIREMENTS.md - accessible
✓ PLAN.md - accessible
✓ QA_REPORT.md - accessible
✓ ADR.md - accessible
✓ ATHENA_REPORT.md - accessible
✓ PR_FEEDBACK.md - accessible
✓ RFC.md - accessible
✓ FEATURE_SPEC.md - accessible

Skipped (already exists): <list of existing files>
Issues/Warnings: <list of any problems>

Next step: Use @sdlc-orchestrator to start building features.
```

## Troubleshooting

### Templates not accessible

**Symptom**: Templates are listed as "not accessible" or "missing"

**Solutions**:
1. Verify plugin is installed and enabled
2. Check VS Code Output panel for plugin loading errors
3. Reinstall the plugin: `Chat: Install Plugin From Source`
4. Check plugin version is 0.3.0 or later

### Cannot create directories

**Symptom**: Permission denied when creating docs/adr/ or docs/athena/

**Solutions**:
1. Check write permissions on the workspace
2. Verify you're in a writable directory
3. Check if files are locked by another process

### Plugin hooks not working

**Symptom**: No TRACE.jsonl files being generated

**Solutions**:
1. Verify Python 3.8+ is available in PATH
2. Check VS Code Output → Copilot for hook errors
3. Look for .agentic-sdlc/state/ directory (should be created on first run)
4. See [Plugin Hooks README](.plugin/README.md) for detailed troubleshooting

## See Also

- [Plugin README](../.plugin/README.md) - Complete plugin documentation
- [Trace Hook Migration Strategy](../docs/TRACE_HOOK_MIGRATION.md) - Trace system design
- [Artifact Validation Guide](../.plugin/docs/ARTIFACT_VALIDATION.md) - Validation system details

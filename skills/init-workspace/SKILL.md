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
- `.github/workflow_templates/` — where workflow templates live

### 2. Workflow Templates

Copy each template from the plugin's `workflow_templates/` directory to `.github/workflow_templates/` in the workspace. The templates are:

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

1. Check which of the above already exist in the workspace — don't overwrite existing files.
2. Create missing directories.
3. Copy each missing workflow template from the plugin's `workflow_templates/` directory.
4. Report what was created and what was skipped.

## Note on Project Context

The SDLC workflow does NOT require a project configuration file. On each run, the orchestrator's Stage 0 uses the Explorer agent to automatically detect the project's language, framework, architecture, and conventions from the codebase. This context is passed to all subagents.

## Output

After setup, confirm:
```
Workspace initialized for Agentic SDLC.
Created: <list of files/dirs created>
Skipped (already exists): <list>
Next step: Use @sdlc-orchestrator to start building features.
```

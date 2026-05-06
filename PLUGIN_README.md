# Agentic SDLC Plugin v0.3.0

A VS Code Copilot Agent plugin that drives features from idea to merged, documented code with automatic trace generation and artifact validation.

## Quick Start

1. Install the plugin in VS Code:
   - Command Palette: `Chat: Install Plugin From Source`
   - Enter: `https://github.com/roma-mekari/agentic-sdlc`
2. Enable `chat.plugins.enabled` in VS Code settings
3. Start using the SDLC workflow with `@sdlc-orchestrator`

## What This Plugin Does

### 1. Trace Generation Hooks
Automatically logs 8 lifecycle events to TRACE.jsonl:
- SessionStart, UserPromptSubmit, PreToolUse, PostToolUse
- PreCompact, SubagentStart, SubagentStop, Stop

### 2. Artifact Validation
Validates that agents produce required artifacts:
- PO → REQUIREMENTS.md
- Architect → PLAN.md
- Implementor → Code files
- QA Lead → QA_REPORT.md
- Tech Writer → ADR.md
- CTO → PLAN.md approval
- PR Reviewer → PR Feedback

## What Gets Created in Your Workspace

When you install and use this plugin, it creates a `.agentic-sdlc/` directory in your workspace:

```
your-project/
├── .agentic-sdlc/              # Created by plugin (ignored by Git)
│   ├── .gitignore              # Auto-generated
│   └── state/                  # Plugin runtime state
│       ├── sessions/            # Session state files
│       │   └── <session-id>.json
│       ├── raw/                 # Event spools
│       │   └── <session-id>.jsonl
│       └── validation_reports/  # Artifact validation reports
│           └── <timestamp>_<agent>_validation.json
│
└── docs/adr/
    └── XXX-feature/
        └── TRACE.jsonl          # Canonical trace file (your project)
```

## Git Configuration

The plugin automatically creates a `.gitignore` entry to ignore the `.agentic-sdlc/` directory. This ensures:

- ✅ Plugin state files are never committed to your repo
- ✅ No merge conflicts from plugin-generated files
- ✅ Clean repository - only your code and docs are tracked

## Files in Your Plugin Installation

After installation, the plugin is installed to VS Code's plugin cache (not in your workspace). The plugin contains:

```
~/.config/Code/agentPlugins/github.com/roma-mekari/agentic-sdlc/
├── .plugin/
│   ├── plugin.json              # Plugin manifest
│   ├── hooks.json               # Hook configuration (8 lifecycle events)
│   ├── config/
│   │   └── artifact_requirements.json
│   ├── scripts/
│   │   ├── trace_hook.sh
│   │   ├── trace_hook.py
│   │   └── validate_artifacts.py
│   └── docs/
│       └── ARTIFACT_VALIDATION.md
```

## Documentation

- [Plugin Hooks README](.plugin/README.md) - Complete setup and troubleshooting
- [Trace Hook Migration Strategy](../docs/TRACE_HOOK_MIGRATION.md) - 3-phase migration plan
- [Artifact Validation Guide](.plugin/docs/ARTIFACT_VALIDATION.md) - Artifact validation system

## Troubleshooting

### Plugin not appearing
1. Check `chat.plugins.enabled` is `true`
2. Check VS Code Output panel (Copilot channel) for errors
3. Verify plugin.json has valid `name` field (kebab-case, no slashes)

### Hooks not firing
1. Verify Python 3.8+ is available in PATH
2. Check VS Code Output panel for hook errors
3. Look for HOOK_* events in TRACE.jsonl

### Validation errors
1. Check `.agentic-sdlc/state/validation_reports/` for detailed reports
2. Verify artifact paths match your project structure
3. Adjust `.plugin/config/artifact_requirements.json` if needed

## Support

For issues or questions:
1. Check [Plugin Hooks README](.plugin/README.md)
2. Review [Trace Hook Migration Strategy](../docs/TRACE_HOOK_MIGRATION.md)
3. Check VS Code Output panel for errors
4. Open an issue on GitHub

## License

See LICENSE file in the repository.

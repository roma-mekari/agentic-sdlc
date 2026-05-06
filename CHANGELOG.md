# Changelog

All notable changes to the Agentic SDLC plugin will be documented in this file.

## [0.3.0] - 2026-04-30

### Added
- **Automatic Trace Generation Hooks** - 8 lifecycle events automatically logged to TRACE.jsonl:
  - SessionStart, UserPromptSubmit, PreToolUse, PostToolUse
  - PreCompact, SubagentStart, SubagentStop, Stop
- **Artifact Validation System** - Automatic validation of agent outputs:
  - Validates required artifacts for PO, Architect, Implementor, QA Lead, Tech Writer, CTO, PR Reviewer
  - Checks file existence, size, and required sections
  - Detects approval markers for CTO validation
  - Generates detailed validation reports
- **Auto Git Ignore** - Plugin automatically creates `.gitignore` entry for `.agentic-sdlc/` directory
- **Documentation** - Comprehensive documentation for hooks, validation, and migration strategy

### Changed
- **Updated init-workspace skill** - Now checks template accessibility and reports on file access
- **Improved README** - Added sections for new features and setup instructions

### Fixed
- Corrected plugin structure - Hooks are in `.plugin/` (plugin root), not `.github/hooks/`
- Runtime state created in user's workspace at `.agentic-sdlc/state/` (not in plugin repo)
- All state files automatically gitignored

### Technical Details
- Plugin now uses OpenPlugin format (`.plugin/plugin.json`)
- Hooks configured in `.plugin/hooks.json`
- Scripts in `.plugin/scripts/`
- Artifact requirements in `.plugin/config/artifact_requirements.json`
- State management in user's workspace: `.agentic-sdlc/state/`

## [0.2.0] - Previous

### Initial Release
- SDLC orchestrator with 6-stage workflow
- Pre-SDLC agents (PRD Analyst, RFC Writer, Estimator)
- Athena agent for meta-analysis
- Dev agent for everyday tasks
- 13 specialized SDLC agents
- Multi-agent delegation system

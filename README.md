# Agentic SDLC Workflow

A VS Code Copilot agent plugin that drives features from raw idea to QA-verified, documented code — with full PR feedback integration. Install once, use in any project.

## Architecture Overview

```
User ──► SDLC Orchestrator
              │
              ├─ Stage 0: Context Detection (reads project-config.md)
              ├─ Stage 1: PO ──► REQUIREMENTS.md
              ├─ Stage 2: Explorer ─► Architect ──► PLAN.md
              ├─ Stage 3: CTO ──► APPROVED / REVISION REQUIRED
              ├─ Stage 4: Implementor ──► Code
              ├─ Stage 5: QA Lead ──► QA_REPORT.md
              │     └─ (auto) Athena ──► ATHENA_REPORT.md (after 2+ QA rejections)
              ├─ Stage 6: Tech Writer ──► ADR.md
              └─ Stage 7: PR Lifecycle
                    ├─ 7a: Human opens PR
                    ├─ 7b: PR Reviewer ──► PR_FEEDBACK.md (classifies comments)
                    ├─ 7c: Resolution ──► routes to PO/Architect/Implementor
                    ├─ 7d: QA Lead re-verifies (if needed)
                    ├─ 7e: Tech Writer updates ADR (if material changes)
                    └─ 7f: PR ready for merge
```

Every stage has a **human review gate** — the orchestrator pauses for approval before proceeding. Stage 7 supports **re-entry**: invoke the orchestrator with PR feedback at any time after a run completes.

## Installation

### Option A: Install as Plugin (Recommended)

Install directly from the Git repository in VS Code:

1. Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Run **Chat: Install Plugin From Source**
3. Enter the repository URL:
   ```
   https://github.com/roma-mekari/agentic-sdlc
   ```
4. The plugin's agents and skills are now available in Copilot Chat

Then initialize your workspace (see [Workspace Setup](#workspace-setup) below).

> **Note:** Requires `chat.plugins.enabled` to be `true` in VS Code settings. Agent plugins are currently a preview feature.

### Option B: Copy to Repository

If you prefer agents committed directly to your repo (for teams that can't use plugins):

```bash
# From your target repository root
mkdir -p .github/agents .github/workflow_templates

# Copy agents
cp /path/to/agentic-sdlc/agents/*.agent.md .github/agents/

# Copy templates and config
cp /path/to/agentic-sdlc/workflow_templates/* .github/workflow_templates/
cp /path/to/agentic-sdlc/project-config.md .github/project-config.md
```

### Option C: User-Level Prompts

For personal use across all repositories without committing to each:

```bash
# macOS / Linux
cp /path/to/agentic-sdlc/agents/*.agent.md \
  "$HOME/Library/Application Support/Code/User/prompts/"

# Windows
copy /path/to/agentic-sdlc/agents\*.agent.md \
  "%APPDATA%\Code\User\prompts\"
```

You still need `.github/workflow_templates/` and `.github/project-config.md` per repository.

## Workspace Setup

Regardless of installation method, each workspace needs template files and a project configuration. The plugin includes an **init-workspace** skill to set this up automatically:

```
Use the init-workspace skill to set up this project for the Agentic SDLC workflow
```

Or set up manually:

1. **Create directories:**
   ```bash
   mkdir -p .github/workflow_templates docs/adr docs/athena
   ```

2. **Copy workflow templates** from this repo's `workflow_templates/` to `.github/workflow_templates/` in your workspace.

3. **Create `.github/project-config.md`** — fill in your project's language, framework, architecture, build/test/lint commands, and code conventions. This is the single most impactful step for agent quality.

Your workspace should look like:
```
your-repo/
├── .github/
│   ├── workflow_templates/    # Templates for REQUIREMENTS.md, PLAN.md, etc.
│   └── project-config.md     # Your project's conventions ← FILL THIS IN
├── docs/
│   ├── adr/                   # Generated ADRs and artifacts
│   └── athena/                # Meta-analysis reports
└── (your existing code)
```

### Recommend the Plugin to Your Team

Add to `.github/copilot/settings.json` in your repo:

```json
{
  "enabledPlugins": {
    "agentic-sdlc": true
  }
}
```

Team members will be prompted to install the plugin when they open the project.

## Agent Roster

| Agent | Role | User-Invocable |
|-------|------|----------------|
| **SDLC Orchestrator** | Coordinates the full workflow, manages review gates and stage transitions | Yes |
| **PO** | Transforms raw task descriptions into structured REQUIREMENTS.md | No |
| **Architect** | Translates requirements into phased implementation plans | No |
| **CTO** | Reviews and approves/rejects architectural plans | No |
| **Implementor** | Writes production-ready code following the approved plan | No |
| **QA Lead** | Verifies implementation against requirements and produces QA reports | No |
| **Tech Writer** | Produces the permanent Architectural Decision Record (ADR) | No |
| **PR Reviewer** | Classifies PR feedback and routes fixes to the right agent | No |
| **Athena** | Reflects on every feedback event and proposes workflow improvements | Yes |
| **Explorer** | Read-only codebase investigator for tracing code paths and patterns | Yes |

## Quick Start

### 1. Build a feature

```
@sdlc-orchestrator Build a user authentication module with JWT tokens and role-based access control
```

The orchestrator walks through all stages, pausing for your review at each gate.

### 2. Process PR feedback

After Stage 6, the orchestrator prompts you to open a PR. Once you receive reviewer feedback:

```
@sdlc-orchestrator PR feedback for 001-auth-module:
- src/auth/handler.go:42 — "Missing rate limiting on login endpoint"
- src/auth/service.go:88 — "Why not use bcrypt instead of argon2?"
- src/auth/middleware.go:15 — "Rename `checkAuth` to `requireAuth` for clarity"
```

The PR Reviewer classifies each comment, routes fixes to the right agent, and re-verifies.

### 3. Investigate the codebase

```
@explorer How does the authentication middleware work? Trace from handler to database.
```

### 4. Invoke Athena

```
@athena Analyze the last SDLC run — the implementor kept failing QA on input validation
```

Athena also runs automatically as **micro-reflections** after every feedback event — capturing what went wrong so instruction quality improves continuously.

## Plugin Structure

```
agentic-sdlc/
├── plugin.json                  # Plugin manifest
├── agents/                      # Agent definitions
│   ├── sdlc-orchestrator.agent.md
│   ├── po.agent.md
│   ├── architect.agent.md
│   ├── cto.agent.md
│   ├── implementor.agent.md
│   ├── qa-lead.agent.md
│   ├── tech-writer.agent.md
│   ├── pr-reviewer.agent.md
│   ├── athena.agent.md
│   └── explorer.agent.md
├── skills/                      # Plugin skills
│   └── init-workspace/
│       └── SKILL.md             # Scaffolds workspace for SDLC workflow
├── workflow_templates/          # Source templates (copied to workspace .github/)
│   ├── REQUIREMENTS.md
│   ├── PLAN.md
│   ├── QA_REPORT.md
│   ├── ADR.md
│   ├── ATHENA_REPORT.md
│   └── PR_FEEDBACK.md
└── project-config.md            # Template for project-specific conventions
```

## How Athena Works

Athena is the continuous improvement meta-agent. It operates in two modes:

**Micro-reflections (frequent):** After every human feedback refinement or PR feedback round, the orchestrator invokes Athena for a lightweight reflection — capturing what the feedback revealed about gaps in the agent instructions. These accumulate in `docs/athena/reflections.jsonl`.

**Full reports (infrequent):** Triggered manually (`@athena`), after 2+ QA rejections, or when 5+ micro-reflections accumulate for the same agent. Produces a full diagnostic with before/after instruction diffs.

Athena is **advisory only** — it never edits agent files directly. All proposed changes are presented for human review.

## Design Principles

- **Agent isolation:** Each agent has a strict scope, fresh context, and cannot perform another agent's job
- **Human-in-the-loop:** Every stage requires human approval before proceeding
- **Language agnosticism:** All agents derive conventions from `project-config.md`, not hardcoded assumptions
- **Continuous improvement:** Athena reflects on every feedback event, not just failures
- **Explore before acting:** The Explorer investigates the codebase before other agents make assumptions
- **Circuit breakers:** Revision cycle caps and anti-loop detection prevent infinite feedback loops
- **PR feedback as re-entry:** PR review comments are classified, routed to the right agent, and re-verified
- **Artifact trail:** Every feature produces REQUIREMENTS.md → PLAN.md → Code → QA_REPORT.md → ADR.md → PR_FEEDBACK.md

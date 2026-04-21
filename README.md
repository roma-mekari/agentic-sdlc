# Agentic SDLC Workflow

A VS Code Copilot agent plugin that drives features from idea to merged, documented code. Agents advise, humans decide. Install once, use in any project.

## Architecture Overview

```
User ──► SDLC Orchestrator
              │
              Phase 1: Planning (interactive)
              ├─ Stage 0: Context Discovery (Explorer auto-detects project stack)
              ├─ Stage 1: PO suggests requirements ↔ Human decides ──► REQUIREMENTS.md
              ├─ Stage 2: Architect presents approaches with trade-offs ↔ Human chooses
              │            └─► CTO validates ──► PLAN.md
              │
              Phase 2: Implementation (loop)
              ├─ Stage 3: Implementor codes ↔ QA verifies ──► QA_REPORT.md
              │            └─ (auto) Athena micro-reflections on every feedback
              │
              Phase 3: PR Review (re-entrant)
              ├─ Stage 4: Human opens PR → PR Reviewer classifies feedback
              │            └─► Routes to PO/Architect/Implementor → re-verifies
              │
              Phase 4: Post-Merge Documentation
              └─ Stage 5: Tech Writer ──► ADR.md (after human confirms merge)
```

**Key design:** Agents suggest and present options. Humans make every product and engineering decision. Every stage has a review gate.

## Installation

### Option A: Install as Plugin (Recommended)

1. Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Run **Chat: Install Plugin From Source**
3. Enter the repository URL:
   ```
   https://github.com/roma-mekari/agentic-sdlc
   ```
4. The plugin's agents and skills are now available in Copilot Chat

Then initialize your workspace (see [Workspace Setup](#workspace-setup) below).

> **Note:** Requires `chat.plugins.enabled` to be `true` in VS Code settings. Agent plugins are a preview feature.

### Option B: Copy to Repository

For teams that can't use plugins:

```bash
# From your target repository root
mkdir -p .github/agents .github/workflow_templates

cp /path/to/agentic-sdlc/agents/*.agent.md .github/agents/
cp /path/to/agentic-sdlc/workflow_templates/* .github/workflow_templates/
```

### Option C: User-Level Prompts

For personal use across all repositories:

```bash
# macOS / Linux
cp /path/to/agentic-sdlc/agents/*.agent.md \
  "$HOME/Library/Application Support/Code/User/prompts/"
```

You still need `.github/workflow_templates/` per repository.

## Workspace Setup

Each workspace needs workflow template files. Use the **init-workspace** skill:

```
Use the init-workspace skill to set up this project for the Agentic SDLC workflow
```

Or set up manually:

1. **Create directories:**
   ```bash
   mkdir -p .github/workflow_templates docs/adr docs/athena
   ```

2. **Copy workflow templates** from this repo's `workflow_templates/` to `.github/workflow_templates/`.

Your workspace should look like:
```
your-repo/
├── .github/
│   └── workflow_templates/    # Templates for REQUIREMENTS.md, PLAN.md, etc.
├── docs/
│   ├── adr/                   # Generated ADRs and artifacts
│   └── athena/                # Micro-reflections and reports
└── (your existing code)
```

> **No project configuration file needed.** The orchestrator's Stage 0 uses the Explorer agent to auto-detect your project's language, framework, architecture, and conventions from the codebase.

### Recommend the Plugin to Your Team

Add to `.github/copilot/settings.json` in your repo:

```json
{
  "enabledPlugins": {
    "agentic-sdlc": true
  }
}
```

## Agent Roster

| Agent | Role | User-Invocable |
|-------|------|----------------|
| **SDLC Orchestrator** | Coordinates the full workflow, manages review gates and stage transitions | Yes |
| **PO** | Suggests user stories and acceptance criteria; asks human to decide | No |
| **Architect** | Presents 2-3 approaches with trade-offs; details the human's chosen approach | No |
| **CTO** | Reviews and approves/rejects architectural plans | No |
| **Implementor** | Writes production-ready code following the approved plan | No |
| **QA Lead** | Verifies implementation against requirements and produces QA reports | No |
| **Tech Writer** | Produces the permanent ADR after the feature is merged | No |
| **PR Reviewer** | Classifies PR feedback and routes fixes to the right agent | No |
| **Athena** | Reflects on every feedback event and proposes workflow improvements | Yes |
| **Explorer** | Read-only codebase investigator for tracing code paths and patterns | Yes |

## Quick Start

### 1. Build a feature

```
@sdlc-orchestrator Build a user authentication module with JWT tokens and role-based access control
```

The orchestrator:
- Auto-detects your project stack (Stage 0)
- PO suggests requirements with open questions for you to decide (Stage 1)
- Architect presents 2-3 approaches with trade-offs for you to choose (Stage 2)
- Implementor codes + QA verifies in a loop (Stage 3)
- Prompts you to open a PR (Stage 4)
- Creates the ADR after you confirm the merge (Stage 5)

### 2. Process PR feedback

After Stage 3, the orchestrator prompts you to open a PR. Once you receive reviewer feedback:

```
@sdlc-orchestrator PR feedback for 001-auth-module:
- src/auth/handler.go:42 — "Missing rate limiting on login endpoint"
- src/auth/service.go:88 — "Why not use bcrypt instead of argon2?"
- src/auth/middleware.go:15 — "Rename `checkAuth` to `requireAuth` for clarity"
```

### 3. Confirm merge (triggers documentation)

```
@sdlc-orchestrator Feature 001-auth-module has been merged
```

### 4. Investigate the codebase

```
@explorer How does the authentication middleware work? Trace from handler to database.
```

### 5. Invoke Athena

```
@athena Analyze the last SDLC run — the implementor kept failing QA on input validation
```

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
└── workflow_templates/          # Source templates (copied to workspace .github/)
    ├── REQUIREMENTS.md
    ├── PLAN.md
    ├── QA_REPORT.md
    ├── ADR.md
    ├── ATHENA_REPORT.md
    └── PR_FEEDBACK.md
```

## How Athena Works

Athena is the continuous improvement meta-agent, operating in two modes:

**Micro-reflections (frequent):** After every human "Refine" feedback or PR feedback round, Athena captures what the feedback reveals about instruction gaps. These accumulate in `docs/athena/reflections.jsonl`.

**Full reports (infrequent):** Triggered manually, after 2+ QA rejections, or when 5+ micro-reflections accumulate for the same agent. Produces a full diagnostic with root cause analysis and proposed instruction changes.

Athena is **advisory only** — it never edits agent files directly.

## Design Principles

- **Agents advise, humans decide:** Every stage presents suggestions, trade-offs, and options — the human makes the final call
- **Agent isolation:** Each agent has a strict scope, fresh context, and cannot perform another agent's job
- **Zero-config context:** Project conventions auto-detected via Explorer — no manual configuration file needed
- **Continuous improvement:** Athena reflects on every feedback event, not just failures
- **Explore before acting:** The Explorer investigates the codebase before agents make assumptions
- **Circuit breakers:** Revision caps and anti-loop detection prevent infinite feedback loops
- **Post-merge documentation:** Tech Writer triggers only after the feature is accepted, not prematurely
- **Artifact trail:** Every feature produces REQUIREMENTS.md → PLAN.md → Code → QA_REPORT.md → ADR.md

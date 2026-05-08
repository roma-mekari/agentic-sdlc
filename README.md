# Agentic SDLC Workflow

A VS Code Copilot agent plugin that drives features from idea to merged, documented code. Agents advise, humans decide. Install once, use in any project.

## Architecture Overview

```
User ──► Pre-SDLC Agents (standalone, user-invocable)
              ├─ PRD Analyst: Reviews PRD completeness & feasibility ──► PRD_REVIEW.md
              ├─ RFC Writer: Technical design doc with alternatives & rollout plan ──► RFC-XXX.md
              └─ Estimator: Story point ranges with risk multipliers ──► ESTIMATION.md

User ──► SDLC Orchestrator (auto-discovers pre-SDLC artifacts)
              │
              Phase 1: Planning (interactive)
              ├─ Stage 0: Context Discovery (Explorer auto-detects stack + tech debt scan)
              │            └─ Loads engineering principles from memory
              ├─ Stage 1: PO suggests requirements ↔ Human decides ──► REQUIREMENTS.md
              ├─ Stage 2: Architect presents approaches with trade-offs ↔ Human chooses
              │            ├─ Feature flag assessment for existing flow changes
              │            └─► CTO validates (incl. feature flag compliance) ──► PLAN.md
              │
              Phase 2: Implementation (loop)
              ├─ Stage 3: Implementor codes (tech debt aware) ↔ QA verifies
              │            ├─ QA produces test playbook (curls + backyard API suggestions)
              │            └─ (auto) Athena micro-reflections on every feedback
              │
              Phase 3: PR Review (re-entrant)
              ├─ Stage 4a: Tech Writer drafts ADR + PR description
              ├─ Stage 4b-e: Human opens PR → PR Reviewer classifies feedback
              │            └─► Routes to PO/Architect/Implementor → re-verifies
              │
              Phase 4: Post-Merge Documentation
              ├─ Stage 5: Tech Writer finalizes ADR (Proposed → Accepted)
              └─ Stage 6: Tech Writer updates living feature spec
```

**Key design:** Agents suggest and present options. Humans make every product and engineering decision. Every stage has a review gate.

## Installation

### Option A: Install as Plugin via Command Palette

1. Open the Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Run **Chat: Install Plugin From Source**
3. Enter the repository URL:
   ```
   https://github.com/roma-mekari/agentic-sdlc
   ```
4. The plugin's agents and skills are now available in Copilot Chat

Then initialize your workspace (see [Workspace Setup](#workspace-setup) below).

> **Note:** Requires `chat.plugins.enabled` to be `true` in VS Code settings. Agent plugins are a preview feature.

### Option B: Install as Plugin via Manual Clone (Recommended)

1. Clone the repository to a local directory:
   ```bash
   git clone https://github.com/roma-mekari/agentic-sdlc.git ~/agentic-sdlc
   ```

2. Open VS Code Settings (`Cmd+,` / `Ctrl+,`) and add the cloned path to `chat.plugins.localPaths`:
   ```json
   {
     "chat.plugins.enabled": true,
     "chat.plugins.localPaths": [
       "~/agentic-sdlc"
     ]
   }
   ```

3. Reload VS Code — all agents and skills are now available in Copilot Chat.

Then initialize your workspace (see [Workspace Setup](#workspace-setup) below).

> **Tip:** This approach makes it easy to `git pull` updates from the repository.

## New in v0.3.0: Automatic Trace Generation & Artifact Validation

The plugin now includes automatic observability features:

### Trace Generation Hooks
Automatically logs 8 lifecycle events to TRACE.jsonl for each SDLC run:
- **SessionStart** - When a session begins
- **UserPromptSubmit** - When you submit a prompt
- **PreToolUse/PostToolUse** - Before/after tool invocations
- **SubagentStart/SubagentStop** - When subagents spawn/complete
- **Stop** - When a session ends

**What gets created:**
- `docs/adr/XXX-feature/TRACE.jsonl` - Complete trace of the SDLC run
- `.agentic-sdlc/state/` - Plugin runtime state (gitignored, never committed)

### Artifact Validation
Automatically validates that agents produce their required artifacts:
- **PO** → `REQUIREMENTS.md` (with required sections)
- **Architect** → `PLAN.md` (with required sections)
- **Implementor** → Code files (minimum count/size)
- **QA Lead** → `QA_REPORT.md` (with required sections)
- **Tech Writer** → `ADR.md` (with required sections)
- **CTO** → `PLAN.md` approval
- **PR Reviewer** → PR feedback document

**What gets created:**
- `.agentic-sdlc/state/validation_reports/` - Detailed validation reports (gitignored)

### How It Works
1. Hooks run automatically when agents complete
2. Traces are written to `docs/adr/*/TRACE.jsonl`
3. Validation reports saved to `.agentic-sdlc/state/validation_reports/`
4. All plugin state is automatically gitignored
5. Your repository stays clean - only your code and artifacts are tracked

See [PLUGIN_README.md](PLUGIN_README.md) for complete details.

### Option C: Copy to Repository

For teams that can't use plugins:

```bash
# From your target repository root
mkdir -p .github/agents .github/workflow_templates

cp /path/to/agentic-sdlc/agents/*.agent.md .github/agents/
cp /path/to/agentic-sdlc/workflow_templates/* .github/workflow_templates/
```

### Option D: User-Level Prompts

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
   mkdir -p .github/workflow_templates docs/adr docs/athena docs/specs docs/rfcs docs/pre-sdlc
   ```

2. **Copy workflow templates** from this repo's `workflow_templates/` to `.github/workflow_templates/`.

Your workspace should look like:
```
your-repo/
├── .github/
│   └── workflow_templates/    # Templates for REQUIREMENTS.md, PLAN.md, RFC.md, etc.
├── docs/
│   ├── adr/                   # Generated ADRs and artifacts
│   ├── athena/                # Micro-reflections and reports
│   ├── specs/                 # Living feature specs
│   ├── rfcs/                  # Technical RFCs
│   └── pre-sdlc/             # PRD reviews, estimations
└── (your existing code)
```

> **No project configuration file needed.** The orchestrator's Stage 0 uses the Explorer agent to auto-detect your project's language, framework, architecture, and conventions from the codebase.

## New in v0.3.0

### Automatic Trace Generation
The plugin now includes hooks that automatically log 8 lifecycle events to TRACE.jsonl:
- **SessionStart** - When a session begins
- **UserPromptSubmit** - When you submit a prompt
- **PreToolUse/PostToolUse** - Before/after tool invocations
- **SubagentStart/SubagentStop** - When subagents spawn/complete
- **Stop** - When a session ends

This provides complete observability of your SDLC workflows without manual intervention.

### Artifact Validation
Automatically validates that agents produce their required artifacts:
- **PO** → `REQUIREMENTS.md` (with required sections)
- **Architect** → `PLAN.md` (with required sections)
- **Implementor** → Code files (minimum count/size)
- **QA Lead** → `QA_REPORT.md` (with required sections)
- **Tech Writer** → `ADR.md` (with required sections)
- **CTO** → `PLAN.md` approval
- **PR Reviewer** → PR feedback document

Validation results are logged to TRACE.jsonl and saved as detailed reports.

### How It Works
- Hooks run automatically when agents complete
- Traces are written to `docs/adr/*/TRACE.jsonl`
- Validation reports saved to `.agentic-sdlc/state/validation_reports/`
- All plugin state is automatically gitignored
- Your repository stays clean - only your code and artifacts are tracked

See [PLUGIN_README.md](PLUGIN_README.md) for complete details.

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
| **Dev** | General-purpose agent: plans, implements, and verifies in a continuous loop without SDLC ceremony | Yes |
| **SDLC Orchestrator** | Coordinates the full workflow, manages review gates and stage transitions | Yes |
| **PRD Analyst** | Reviews PRDs for completeness, ambiguity, and feasibility before SDLC starts | Yes |
| **RFC Writer** | Produces technical design docs with alternatives, cross-service impact, and rollout plans | Yes |
| **Estimator** | Story point estimation with ranges, risk multipliers, and codebase complexity analysis | Yes |
| **PO** | Suggests user stories and acceptance criteria; asks human to decide | No |
| **Architect** | Presents 2-3 approaches with trade-offs; assesses feature flag needs | No |
| **CTO** | Reviews and approves/rejects architectural plans (incl. feature flag compliance) | No |
| **Implementor** | Writes production-ready code following the approved plan; tech debt aware | No |
| **QA Lead** | Verifies implementation, produces QA reports with test playbooks and backyard API suggestions | No |
| **Tech Writer** | Drafts ADR + PR description, finalizes ADR post-merge, maintains feature specs | No |
| **PR Reviewer** | Classifies PR feedback and routes fixes to the right agent | No |
| **Athena** | Reflects on feedback events, routes findings to agent improvements or engineering principles | Yes |
| **Explorer** | Read-only codebase investigator for tracing code paths, patterns, and tech debt | Yes |

## Quick Start

### 0. Maintain this repo itself

```
@workflow-engineer Tighten the Dev agent's clarification flow, add boundary coverage, and sync the readmes.
```

The Workflow Engineer is the preferred driver when you are changing this repository's own agents, skills, workflow templates, tests, or docs. It lives only in `.github/agents/workflow-engineer.agent.md` in this repository, so it is not shipped as part of the distributable plugin agent set and does not get copied into implementation repositories by the standard `agents/*.agent.md` flows. It stays scoped to the instructions-based workflow surfaces, asks efficient clarification questions up front, treats test and README updates as part of done, and always ends by asking for user input.

### 1. Everyday development (no ceremony)

```
@dev Add pagination to the GET /api/v1/candidates endpoint with cursor-based navigation
```

The Dev agent:
- Explores the codebase for existing patterns (via Explorer subagent)
- Plans the changes and asks you to confirm
- Implements directly
- Runs parallel security review + verification subagents
- Fixes any issues and re-verifies until clean
- Asks if you need anything else (stays in session)

### 2. Build a feature (full SDLC ceremony)

```
@sdlc-orchestrator Build a user authentication module with JWT tokens and role-based access control
```

The orchestrator:
- Auto-detects your project stack (Stage 0)
- PO suggests requirements with open questions for you to decide (Stage 1)
- Architect presents 2-3 approaches with trade-offs for you to choose (Stage 2)
- Implementor codes + QA verifies in a loop (Stage 3)
- Prompts you to open a PR with a suggested PR description (Stage 4a)
- Creates the ADR after you confirm the merge (Stage 5)

### 3. Process PR feedback

After Stage 3, the orchestrator prompts you to open a PR. Once you receive reviewer feedback:

```
@sdlc-orchestrator PR feedback for 001-auth-module:
- src/auth/handler.go:42 — "Missing rate limiting on login endpoint"
- src/auth/service.go:88 — "Why not use bcrypt instead of argon2?"
- src/auth/middleware.go:15 — "Rename `checkAuth` to `requireAuth` for clarity"
```

### 4. Confirm merge (triggers documentation)

```
@sdlc-orchestrator Feature 001-auth-module has been merged
```

### 5. Investigate the codebase

```
@explorer How does the authentication middleware work? Trace from handler to database.
```

### 6. Analyze a PRD before starting

```
@prd-analyst Review this PRD for our new candidate bulk import feature: [paste PRD or link]
```

### 7. Write a technical RFC

```
@rfc-writer Design doc for adding real-time notifications to the recruitment pipeline
```

### 8. Estimate effort

```
@estimator How big is the candidate bulk import feature? Here's the PRD: [paste or link]
```

### 9. Invoke Athena

```
@athena Analyze the last SDLC run — the implementor kept failing QA on input validation
```

## Plugin Structure

```
agentic-sdlc/
├── .plugin/                     # Plugin root
│   ├── plugin.json             # Plugin manifest (v0.3.0)
│   ├── hooks.json              # Hook configuration (8 lifecycle events)
│   ├── config/
│   │   └── artifact_requirements.json  # Artifact validation rules
│   ├── scripts/
│   │   ├── trace_hook.sh       # Shell wrapper for hooks
│   │   ├── trace_hook.py       # Python dispatcher (trace generation + validation)
│   │   └── validate_artifacts.py # Standalone validation script
│   ├── docs/
│   │   └── ARTIFACT_VALIDATION.md
│   └── README.md               # Plugin technical documentation
│
├── agents/                      # Agent definitions
│   ├── dev.agent.md
│   ├── sdlc-orchestrator.agent.md
│   ├── po.agent.md
│   ├── architect.agent.md
│   ├── cto.agent.md
│   ├── implementor.agent.md
│   ├── qa-lead.agent.md
│   ├── tech-writer.agent.md
│   ├── pr-reviewer.agent.md
│   ├── athena.agent.md
│   ├── explorer.agent.md
│   ├── prd-analyst.agent.md
│   ├── rfc-writer.agent.md
│   └── estimator.agent.md
│
├── skills/                      # Plugin skills
│   └── init-workspace/
│       └── SKILL.md         # Scaffolds workspace for SDLC workflow
│
├── workflow_templates/          # Source templates
│   ├── REQUIREMENTS.md
│   ├── PLAN.md
│   ├── QA_REPORT.md
│   ├── ADR.md
│   ├── ATHENA_REPORT.md
│   ├── PR_FEEDBACK.md
│   ├── RFC.md
│   └── FEATURE_SPEC.md
│
├── docs/                        # Documentation
│   ├── TRACE_HOOK_MIGRATION.md
│   ├── OBSERVABILITY.md
│   └── CHANGELOG.md
│
└── PLUGIN_README.md            # User-facing plugin overview
```

### What Gets Created in Your Workspace

```
your-project/
├── .agentic-sdlc/              # Created by plugin (gitignored)
│   ├── .gitignore               # Auto-generated
│   └── state/
│       ├── sessions/            # Session state files
│       ├── raw/                 # Event spools before run binding
│       └── validation_reports/  # Artifact validation reports
│
├── docs/adr/
│   └── XXX-feature/
│       ├── REQUIREMENTS.md     # User artifacts
│       ├── PLAN.md
│       ├── QA_REPORT.md
│       ├── ADR.md
│       └── TRACE.jsonl         # Canonical trace (generated by hooks)
│
└── (your existing code)
```

## How Athena Works

Athena is the continuous improvement meta-agent, operating in four modes:

**Micro-reflections (frequent):** After every human "Refine" feedback or PR feedback round, Athena captures what the feedback reveals. Classifies findings as either agent/workflow improvements (logged to `docs/athena/reflections.jsonl`) or engineering principles (written to `/memories/repo/engineering-principles/`).

**Full reports (infrequent):** Triggered manually, after 2+ QA rejections, or when 5+ micro-reflections accumulate for the same agent. Produces a full diagnostic with root cause analysis and proposed instruction changes.

**Post-run analysis:** Triggered after every completed SDLC run to analyze TRACE.jsonl health metrics — delegation counts, human gate compliance, violation detection.

**Session analysis:** Parse exported chat sessions (chat.json) via the `parse-session` skill to detect delegation violations, thinking trace bypasses, and workflow compliance issues. The most powerful diagnostic mode.

Athena is **advisory only** — it never edits agent files directly.

## Design Principles

- **Agents advise, humans decide:** Every stage presents suggestions, trade-offs, and options — the human makes the final call
- **Agent isolation:** Each agent has a strict scope, fresh context, and cannot perform another agent's job
- **Zero-config context:** Project conventions auto-detected via Explorer — no manual configuration file needed
- **Continuous improvement:** Athena reflects on every feedback event, not just failures
- **Explore before acting:** The Explorer investigates the codebase before agents make assumptions
- **Circuit breakers:** Revision caps and anti-loop detection prevent infinite feedback loops
- **Post-merge documentation:** Tech Writer drafts ADR before PR review (reducing post-merge interaction) and finalizes after merge
- **Artifact trail:** Every feature produces REQUIREMENTS.md → PLAN.md → Code → QA_REPORT.md → ADR.md, with deferred items tracked across artifacts
- **Drift detection:** QA Lead checks if the implementation matches the plan; deviations are documented
- **Deferred items tracking:** Out-of-scope feedback flows from PR_FEEDBACK → QA_REPORT → ADR, with priority and impact assessment
- **Automatic observability:** Hooks automatically log lifecycle events to TRACE.jsonl without manual intervention
- **Artifact validation:** Automatic validation ensures agents produce required artifacts with proper structure
- **Clean repositories:** Plugin state is gitignored - only your code and artifacts are tracked

## Observability (v0.3.0+)

The plugin provides automatic observability for SDLC workflows:

### Trace Generation
- **8 lifecycle events** automatically logged: SessionStart, UserPromptSubmit, PreToolUse, PostToolUse, PreCompact, SubagentStart, SubagentStop, Stop
- **TRACE.jsonl** generated automatically in `docs/adr/XXX-feature/TRACE.jsonl`
- **Session state** managed in `.agentic-sdlc/state/sessions/`
- **Event correlation** via session IDs and hook sequences

### Artifact Validation
- **Automatic validation** after each agent completes
- **8 agents validated**: PO, Architect, CTO, Implementor, QA Lead, Tech Writer, PR Reviewer
- **Validation reports** saved to `.agentic-sdlc/state/validation_reports/`
- **Results logged** to TRACE.jsonl as `ARTIFACT_VALIDATION` events
- **Configurable rules** for file size, sections, patterns, and approvals

### See Also
- [TRACE_HOOK_MIGRATION.md](docs/TRACE_HOOK_MIGRATION.md) - Complete 3-phase migration strategy
- [PLUGIN_README.md](PLUGIN_README.md) - Plugin user guide
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes

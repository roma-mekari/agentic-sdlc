# Agentic SDLC Workflow

An autonomous software development lifecycle (SDLC) powered by specialized AI agents running in VS Code Copilot agent mode. A single orchestrator drives features from raw idea to QA-verified, documented code.

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

## Agent Roster

| Agent | Role | File | User-Invocable |
|-------|------|------|----------------|
| **SDLC Orchestrator** | Coordinates the full workflow, manages review gates and stage transitions | `.github/agents/sdlc-orchestrator.agent.md` | Yes |
| **PO** | Transforms raw task descriptions into structured REQUIREMENTS.md | `.github/agents/po.agent.md` | No |
| **Architect** | Translates requirements into phased implementation plans | `.github/agents/architect.agent.md` | No |
| **CTO** | Reviews and approves/rejects architectural plans | `.github/agents/cto.agent.md` | No |
| **Implementor** | Writes production-ready code following the approved plan | `.github/agents/implementor.agent.md` | No |
| **QA Lead** | Verifies implementation against requirements and produces QA reports | `.github/agents/qa-lead.agent.md` | No |
| **Tech Writer** | Produces the permanent Architectural Decision Record (ADR) | `.github/agents/tech-writer.agent.md` | No |
| **PR Reviewer** | Classifies PR feedback and routes fixes to the right agent | `.github/agents/pr-reviewer.agent.md` | No |
| **Athena** | Meta-agent that reflects on every feedback event and proposes workflow improvements | `.github/agents/athena.agent.md` | Yes |
| **Explorer** | Read-only codebase investigator for tracing code paths, mapping dependencies, and discovering patterns | `.github/agents/explorer.agent.md` | Yes |

## Quick Start

### 1. Configure your project

Fill in `.github/project-config.md` with your project's language, framework, architecture pattern, build/test commands, and code conventions. This file is read by all agents to adapt their behavior.

### 2. Run the orchestrator

In VS Code Copilot Chat, invoke the SDLC Orchestrator:

```
@sdlc-orchestrator Build a user authentication module with JWT tokens and role-based access control
```

The orchestrator will walk through all stages, pausing for your review at each gate.

### 3. Process PR feedback

After Stage 6, the orchestrator will prompt you to open a PR. Once you receive reviewer feedback, re-invoke the orchestrator:

```
@sdlc-orchestrator PR feedback for 001-auth-module:
- src/auth/handler.go:42 — "Missing rate limiting on login endpoint"
- src/auth/service.go:88 — "Why not use bcrypt instead of argon2?"
- src/auth/middleware.go:15 — "Rename `checkAuth` to `requireAuth` for clarity"
```

The PR Reviewer agent will classify each comment, route fixes to the right agent, and re-verify the result.

### 3. Investigate the codebase (optional)

Use the Explorer agent directly for ad-hoc codebase investigation:

```
@explorer How does the authentication middleware work? Trace the request flow from the HTTP handler to the database.
```

The Explorer is also invoked automatically by the orchestrator when agents need codebase context.

### 4. Invoke Athena (optional)

After a run that felt inefficient or had repeated QA rejections, invoke Athena manually:

```
@athena Analyze the last SDLC run — the implementor kept failing QA on input validation
```

Athena produces an advisory report with proposed instruction changes. Review and apply them manually.

Athena also runs automatically as a **micro-reflection** after every human feedback refinement and PR feedback round — capturing what went wrong and why, so instruction quality improves continuously.

## Directory Structure

```
.github/
├── agents/                      # Agent definitions (flat — all files must be here for VS Code visibility)
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
├── workflow_templates/          # Templates agents use to produce artifacts
│   ├── REQUIREMENTS.md
│   ├── PLAN.md
│   ├── QA_REPORT.md
│   ├── ADR.md
│   ├── ATHENA_REPORT.md
│   └── PR_FEEDBACK.md
└── project-config.md            # Project-specific conventions (language, framework, etc.)

docs/
├── adr/                         # Generated ADRs and supporting artifacts
│   └── XXX-feature-name/
│       ├── REQUIREMENTS.md
│       ├── PLAN.md
│       ├── QA_REPORT.md
│       └── PR_FEEDBACK.md
└── athena/                      # Athena meta-analysis reports
    └── YYYY-MM-DD-slug.md
```

## How Athena Works

Athena is the continuous improvement meta-agent. It operates in two modes:

**Manual trigger:** Invoke `@athena` anytime with a description of what went wrong. It reads the relevant artifacts and transcripts, diagnoses the root cause, and proposes targeted instruction changes.

**Auto-trigger (full report):** The orchestrator automatically invokes Athena for a full diagnostic when the QA Lead has rejected the implementation **2 or more times** in a single run.

**Micro-reflections:** After every human feedback refinement or PR feedback round, the orchestrator invokes Athena for a lightweight reflection — capturing what the feedback revealed about gaps in the agent instructions. These micro-reflections accumulate in `docs/athena/reflections.jsonl` and inform future full reports.

Athena is **advisory only** — it never edits agent files directly. All proposed changes are presented as before/after diffs for human review.

## Configuring for a New Project

There are two ways to integrate this workflow into your repository:

### Option A: Repository Configuration (Recommended for Teams)

Copy the `.github/` directory into your repository's root. This makes the agents available to anyone who opens the repo in VS Code with GitHub Copilot.

```bash
# From your target repository root
cp -r /path/to/agentic-sdlc/.github/agents .github/agents
cp -r /path/to/agentic-sdlc/.github/workflow_templates .github/workflow_templates
cp /path/to/agentic-sdlc/.github/project-config.md .github/project-config.md
```

Then configure:

1. **Edit `.github/project-config.md`** — fill in your project's language, framework, architecture, build/test/lint commands, and code conventions. This is the single most impactful step: explicit config produces significantly better results than agent inference.
2. **Create `docs/adr/`** — the agents will write artifacts here.
3. **Create `docs/athena/`** — for meta-analysis reports.
4. **Commit the `.github/` directory** to version control so the entire team shares the same agent definitions.

Directory layout after setup:

```
your-repo/
├── .github/
│   ├── agents/                  # All .agent.md files must be directly here
│   │   ├── sdlc-orchestrator.agent.md
│   │   ├── po.agent.md
│   │   ├── architect.agent.md
│   │   ├── cto.agent.md
│   │   ├── implementor.agent.md
│   │   ├── qa-lead.agent.md
│   │   ├── tech-writer.agent.md
│   │   ├── pr-reviewer.agent.md
│   │   ├── athena.agent.md
│   │   └── explorer.agent.md
│   ├── workflow_templates/
│   └── project-config.md       ← FILL THIS IN
├── docs/
│   ├── adr/
│   └── athena/
└── (your existing code)
```

### Option B: User-Level Configuration (For Personal Use)

If you want the agents available across all your repositories without committing them to each one, place them in your VS Code user-level prompt directory:

```bash
# macOS / Linux
mkdir -p "$HOME/Library/Application Support/Code/User/prompts"
cp -r /path/to/agentic-sdlc/.github/agents/* "$HOME/Library/Application Support/Code/User/prompts/"

# Windows
mkdir "%APPDATA%\Code\User\prompts"
copy /path/to/agentic-sdlc/.github/agents\* "%APPDATA%\Code\User\prompts\"
```

With user-level config:
- Agents are available in every workspace you open
- You still need `.github/project-config.md` **per repository** (the agents won't know your project's stack otherwise)
- You still need `.github/workflow_templates/` **per repository** (or the agents will fail to find templates)
- Workflow templates and project config must be committed to the repo

**Recommended approach:** Use Option A (repo config) for team projects. Use Option B only for personal tooling across many small repositories, and still commit `project-config.md` and `workflow_templates/` to each repo.

### Post-Setup Verification

To verify the setup works:

1. Open the repository in VS Code
2. Open Copilot Chat
3. Type `@` and check that `sdlc-orchestrator`, `athena`, and `explorer` appear as available agents
4. Run a quick test: `@explorer What is the primary language and framework of this project?`

If `project-config.md` is absent, agents will attempt to infer conventions from the codebase, but explicit configuration produces significantly better results.

## Design Principles

- **Agent isolation:** Each agent has a strict scope, fresh context, and cannot perform another agent's job (inspired by Hermes's delegate tool architecture)
- **Human-in-the-loop:** Every stage requires human approval before proceeding
- **Language agnosticism:** All agents derive conventions from `project-config.md`, not hardcoded assumptions
- **Advisory improvement:** Athena proposes changes but never applies them automatically
- **Behavioral self-improvement:** Agents flag gaps in instructions and templates during normal work, feeding Athena's analysis
- **Explore before acting:** The Explorer agent investigates the codebase with isolated context before other agents make assumptions about existing code
- **Circuit breakers:** Revision cycle caps and anti-loop detection prevent infinite feedback loops
- **Artifact trail:** Every feature produces REQUIREMENTS.md → PLAN.md → Code → QA_REPORT.md → ADR.md → PR_FEEDBACK.md
- **PR feedback as re-entry:** PR review comments are classified, routed to the right agent, and re-verified — closing the loop between code review and the SDLC workflow

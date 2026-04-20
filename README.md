# Agentic SDLC Workflow

An autonomous software development lifecycle (SDLC) powered by specialized AI agents running in VS Code Copilot agent mode. A single orchestrator drives features from raw idea to QA-verified, documented code.

## Architecture Overview

```
User ──► SDLC Orchestrator (Sisyphus)
              │
              ├─ Stage 0: Context Detection (reads project-config.md)
              ├─ Stage 1: PO ──► REQUIREMENTS.md
              ├─ Stage 2: Architect ──► PLAN.md
              ├─ Stage 3: CTO ──► APPROVED / REVISION REQUIRED
              ├─ Stage 4: Implementor ──► Code
              ├─ Stage 5: QA Lead ──► QA_REPORT.md
              │     └─ (auto) Athena ──► ATHENA_REPORT.md (after 2+ QA rejections)
              └─ Stage 6: Tech Writer ──► ADR.md
```

Every stage has a **human review gate** — the orchestrator pauses for approval before proceeding.

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
| **Athena** | Meta-agent that analyzes workflow failures and proposes instruction improvements | `.github/agents/athena.agent.md` | Yes |
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

## Directory Structure

```
.github/
├── agents/                      # Agent definitions
│   ├── sdlc-orchestrator.agent.md
│   ├── po.agent.md
│   ├── architect.agent.md
│   ├── cto.agent.md
│   ├── implementor.agent.md
│   ├── qa-lead.agent.md
│   ├── tech-writer.agent.md
│   ├── athena.agent.md
│   └── explorer.agent.md
├── workflow_templates/          # Templates agents use to produce artifacts
│   ├── REQUIREMENTS.md
│   ├── PLAN.md
│   ├── QA_REPORT.md
│   ├── ADR.md
│   └── ATHENA_REPORT.md
└── project-config.md            # Project-specific conventions (language, framework, etc.)

docs/
├── adr/                         # Generated ADRs and supporting artifacts
│   └── XXX-feature-name/
│       ├── REQUIREMENTS.md
│       ├── PLAN.md
│       └── QA_REPORT.md
└── athena/                      # Athena meta-analysis reports
    └── YYYY-MM-DD-slug.md
```

## How Athena Works

Athena is the continuous improvement meta-agent. It operates in two modes:

**Manual trigger:** Invoke `@athena` anytime with a description of what went wrong. It reads the relevant artifacts and transcripts, diagnoses the root cause, and proposes targeted instruction changes.

**Auto-trigger:** The orchestrator automatically invokes Athena when the QA Lead has rejected the implementation **2 or more times** in a single run. The report is surfaced to the human at the review gate alongside the QA rejection.

Athena is **advisory only** — it never edits agent files directly. All proposed changes are presented as before/after diffs for human review.

## Configuring for a New Project

1. Copy this `.github/` directory into your repository
2. Edit `.github/project-config.md` to match your project's stack:
   - Set language, framework, and runtime
   - Define build, test, and lint commands
   - Specify the architecture pattern and layer ordering
   - Document error handling, logging, and other conventions
3. Start using `@sdlc-orchestrator` to build features

If `project-config.md` is absent, agents will attempt to infer conventions from the codebase, but explicit configuration produces better results.

## Design Principles

- **Agent isolation:** Each agent has a strict scope, fresh context, and cannot perform another agent's job (inspired by Hermes's delegate tool architecture)
- **Human-in-the-loop:** Every stage requires human approval before proceeding
- **Language agnosticism:** All agents derive conventions from `project-config.md`, not hardcoded assumptions
- **Advisory improvement:** Athena proposes changes but never applies them automatically
- **Behavioral self-improvement:** Agents flag gaps in instructions and templates during normal work, feeding Athena's analysis
- **Explore before acting:** The Explorer agent investigates the codebase with isolated context before other agents make assumptions about existing code
- **Circuit breakers:** Revision cycle caps and anti-loop detection prevent infinite feedback loops
- **Artifact trail:** Every feature produces REQUIREMENTS.md → PLAN.md → Code → QA_REPORT.md → ADR.md

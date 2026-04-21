---
name: "init-workspace"
description: "Initialize the current workspace for the Agentic SDLC workflow. Creates the required directory structure, workflow templates, and project configuration file that the SDLC agents depend on."
---

# Initialize Workspace for Agentic SDLC

You are setting up the current workspace to work with the Agentic SDLC plugin. The SDLC agents expect certain files and directories to exist in the workspace.

## What to Create

### 1. Directory Structure

Create these directories if they don't exist:
- `.github/` — workspace configuration root
- `docs/adr/` — where feature ADRs and supporting artifacts are stored
- `docs/athena/` — where Athena meta-analysis reports are stored

### 2. Project Configuration

Create `.github/project-config.md` with the following template. Ask the user about their project to fill in as many fields as possible:

```markdown
# Project Configuration

> **Purpose:** This file defines the project's language, framework, architecture, and tooling conventions. All agents in the SDLC workflow read this file to adapt their behavior to the specific project. If this file is absent, agents should infer conventions from the codebase.

---

## Language & Runtime

- **Primary Language:** [e.g., Go, Python, TypeScript, Java]
- **Language Version:** [e.g., Go 1.22, Python 3.12, Node 20 LTS]
- **Runtime/Platform:** [e.g., Linux amd64, Docker, AWS Lambda]

---

## Framework & Architecture

- **Framework:** [e.g., Chi, FastAPI, Next.js, Spring Boot, or "None"]
- **Architecture Pattern:** [e.g., Clean Architecture, Hexagonal, MVC, Layered, Modular Monolith]
- **Layer Ordering:** [e.g., Domain → Port → Repository → Service → Handler]
  > List the layers from innermost (pure domain) to outermost (I/O / HTTP). The Architect and CTO agents use this ordering to structure implementation phases and validate dependency direction.

---

## Build & Test

- **Build Command:** [e.g., `go build ./...`, `npm run build`, `./gradlew build`]
- **Test Command:** [e.g., `go test ./... -cover`, `pytest --cov`, `npm test`]
- **Lint Command:** [e.g., `golangci-lint run`, `ruff check .`, `eslint .`]
- **Coverage Target:** [e.g., ≥80%]

---

## Code Conventions

- **Error Handling:** [e.g., "Wrap errors with context using fmt.Errorf + %w", "Raise domain exceptions", "Return Result<T, E>"]
- **Dependency Injection:** [e.g., "Constructor injection via interfaces", "Wire framework", "Manual"]
- **Configuration:** [e.g., "Environment variables via os.Getenv", ".env files", "Config structs"]
- **Logging:** [e.g., "Structured logging via slog", "Python logging module", "Winston"]
- **Context Propagation:** [e.g., "context.Context as first parameter", "Request-scoped DI", "AsyncLocalStorage"]

---

## Database

- **Database Engine:** [e.g., PostgreSQL 14.x, MySQL 8, MongoDB 7, SQLite, None]
- **Migration Tool:** [e.g., golang-migrate, Alembic, Prisma, Flyway]
- **Data Access Pattern:** [e.g., Repository pattern, ORM, Raw SQL with query builder]

---

## Security & Compliance

- **Input Validation Layer:** [e.g., "Handler/Controller layer before service calls", "Pydantic models", "Zod schemas"]
- **Secrets Management:** [e.g., "Environment variables — never hardcoded", "AWS Secrets Manager", "Vault"]
- **Auth Pattern:** [e.g., "JWT middleware", "Session-based", "OAuth2", "N/A"]

---

## Project-Specific Rules

> Add any additional conventions, constraints, or guidelines specific to this project that agents should follow.

- [e.g., "All new endpoints must have OpenAPI annotations"]
- [e.g., "No new external dependencies without team approval"]
- [e.g., "Follow the ADR process for architectural decisions"]
```

### 3. Workflow Templates

Create `.github/workflow_templates/` with these template files. Each template is used by a specific agent to produce structured artifacts.

**IMPORTANT:** Read each template from the plugin's `workflow_templates/` directory and copy it to `.github/workflow_templates/` in the workspace. The templates are:

- `REQUIREMENTS.md` — Used by the PO agent
- `PLAN.md` — Used by the Architect agent
- `QA_REPORT.md` — Used by the QA Lead agent
- `ADR.md` — Used by the Tech Writer agent
- `ATHENA_REPORT.md` — Used by the Athena agent
- `PR_FEEDBACK.md` — Used by the PR Reviewer agent

### 4. Copilot Settings (Optional)

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
3. For `project-config.md`: if it doesn't exist, ask the user about their project's language, framework, and conventions to fill in the template. If it exists, skip.
4. For workflow templates: copy each missing template from the plugin's `workflow_templates/` directory.
5. Report what was created and what was skipped.

## Output

After setup, confirm:
```
Workspace initialized for Agentic SDLC.
Created: <list of files/dirs created>
Skipped (already exists): <list>
Next step: Fill in .github/project-config.md with your project's specifics, then use @sdlc-orchestrator to start building features.
```

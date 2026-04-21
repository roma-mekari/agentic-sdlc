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

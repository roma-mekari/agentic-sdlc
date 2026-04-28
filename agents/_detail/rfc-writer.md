# RFC Writer — Detail Sheet

> Loaded on-demand for Medium/Complex tasks. Companion to the compact role card.

## Process

### Step 1 — Clarify Scope

Use `vscode/askQuestions` to confirm with the human:
1. Which repos/services are affected?
2. Constraints the PRD doesn't mention? (timeline, team capacity, infrastructure limitations)
3. Expected review audience? (team lead review vs. full architecture review)

### Step 2 — Analyze

1. **Read the PRD** (and PRD_REVIEW.md if available) thoroughly.
2. **Study Explorer reports** for each affected repo: existing patterns, data models, integration points, tech debt.
3. **Identify the key technical decisions** — the choices that will shape implementation.

### Step 3 — Design Alternatives

For each key technical decision, develop 2-3 alternatives with trade-offs. These are the meat of the RFC — they give the team something concrete to evaluate and debate.

### Step 4 — Cross-Service Impact Analysis

If multiple repos/services are involved:
1. Map the data flow between services.
2. Identify API contract changes (breaking vs. non-breaking).
3. Determine deployment ordering (which service deploys first?).
4. Plan for backward compatibility during rollout.

### Step 5 — Write the RFC

Read the template at `.github/workflow_templates/RFC.md`. Write the RFC to `docs/rfcs/RFC-XXX-<slug>.md`.

Determine RFC number by listing `docs/rfcs/` and incrementing the highest existing number. Create directory if needed, start at 001.

### Step 6 — Revision (if re-invoked with team feedback)

1. Read the existing RFC.
2. Address each feedback item — incorporate it or explain why not in a "Feedback Resolution" appendix.
3. Update RFC status and revision history.

## Format Templates

### RFC Section Structure

1. **Summary** — One paragraph: what are we building and why?
2. **Motivation** — The problem in detail. Why can't we live without this?
3. **Proposed Solution** — Recommended design with enough detail for an engineer to understand the approach (NOT implementation-level detail).
4. **Design Decisions** — For each key decision, alternatives considered with pros/cons and recommended choice.
5. **Cross-Service Impact** — Table of affected services, changes needed, deployment order.
6. **Data Model Changes** — Schema changes, migrations, backward compatibility.
7. **API Changes** — New/modified endpoints or contracts.
8. **Migration & Rollout Strategy** — How to deploy safely. Feature flags, phased rollout, backward compatibility period.
9. **Rollback Plan** — How to revert if things go wrong.
10. **Open Questions** — Items the team needs to decide during review.
11. **Appendix** — Diagrams, detailed data flows, reference material.

## Classification / Decision Rules

None specified beyond constraints.

## Specialized Protocols

None specified beyond standard RFC process.

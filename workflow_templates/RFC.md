---
Location: docs/rfcs/RFC-XXX-slug.md
Status: DRAFT | IN REVIEW | ACCEPTED | REJECTED | SUPERSEDED
Created by: RFC Writer Agent
Date: YYYY-MM-DD
summary:
  status: ""
  services_affected: []
  open_questions: []
  estimated_effort: ""
---

# RFC-XXX: [Title]

> **Status:** Draft  
> **Author:** [Name / Agent]  
> **Date:** YYYY-MM-DD  
> **Reviewers:** [Team members]  
> **PRD Reference:** [Link to PRD or PRD_REVIEW.md]  
> **Estimated effort:** [From Estimator, if available]  

---

## Summary

[One paragraph: What are we building, why, and at what level of ambition?]

---

## Motivation

### The Problem
[Detailed description of the problem. Why can't we live without this? What pain does it cause today?]

### Current State
[How does the system handle this today? What are the limitations?]

### Desired Outcome
[What does success look like? Reference PRD success metrics if available.]

---

## Proposed Solution

### High-Level Design
[2-3 paragraphs describing the recommended approach. Enough detail for an engineer to understand the direction, but NOT implementation-level specifics.]

### System Architecture
[How components interact. Describe the flow at a service/module level.]

```
[Optional: ASCII diagram or description of component interaction]
```

---

## Design Decisions

### Decision 1: [Decision Title]

**Context:** [Why this decision matters]

| Option | Pros | Cons | Effort |
|--------|------|------|--------|
| **Option A (Recommended)** | [Pros] | [Cons] | Low/Med/High |
| Option B | [Pros] | [Cons] | Low/Med/High |
| Option C | [Pros] | [Cons] | Low/Med/High |

**Recommendation:** Option A because [reasoning].

### Decision N: [Decision Title]
[Same structure]

---

## Cross-Service Impact

| Service/Repo | Impact Level | Changes Needed | Deployment Order |
|-------------|-------------|----------------|-----------------|
| [service-1] | High | [Brief description] | 1st |
| [service-2] | Medium | [Brief description] | 2nd |
| [service-3] | Low | [Brief description] | 3rd (after service-1 is live) |

### Data Flow Between Services
[Describe how data moves between services for this feature. Event-driven? Synchronous API? Shared DB?]

---

## Data Model Changes

### New Tables/Collections
```sql
-- [Table name and purpose]
CREATE TABLE ... (
  -- key columns only, not full DDL
);
```

### Modified Tables/Collections
| Table | Change | Backward Compatible? | Migration Strategy |
|-------|--------|---------------------|-------------------|
| [table] | [change] | Yes/No | [approach] |

### Data Migration
[Is there a backfill needed? How long will it take? Can it run online?]

---

## API Changes

### New Endpoints
| Method | Path | Description | Breaking? |
|--------|------|-------------|-----------|
| POST | `/api/v1/...` | [Description] | No (new) |

### Modified Endpoints
| Method | Path | Change | Breaking? | Compatibility |
|--------|------|--------|-----------|--------------|
| GET | `/api/v1/...` | [Change] | Yes/No | [How backward compat is maintained] |

---

## Feature Flag Strategy

> **Required section.** If no feature flag is needed, state: "No feature flag required — [reason, e.g., 'new additive endpoint, no existing flow modified']."

| Flag Name | Scope | Default | Description |
|-----------|-------|---------|-------------|
| `feature.<name>.enabled` | Per-tenant / Global | `false` | [What it controls] |

### Rollout Plan
1. Deploy with flag `off` (dark launch)
2. Enable for internal testing
3. Enable for beta tenants: [list]
4. Gradual rollout: [percentage ramp]
5. Full GA: remove flag after [stabilization period]

---

## Migration & Rollout Strategy

### Deployment Order
1. [Step 1: e.g., "Deploy schema migration"]
2. [Step 2: e.g., "Deploy service-1 with feature flag off"]
3. [Step N: e.g., "Enable feature flag for all tenants"]

### Backward Compatibility
[How will the system behave during partial rollout? Old clients + new server? New clients + old server?]

### Estimated Rollout Timeline
| Phase | Duration | What Happens |
|-------|----------|-------------|
| Dark launch | [X days] | Code deployed, flag off |
| Internal testing | [X days] | QA + internal validation |
| Beta | [X days] | Selected tenants |
| GA | — | Full rollout |

---

## Rollback Plan

### Triggers for Rollback
- [Condition 1: e.g., "Error rate > 1% on affected endpoints"]
- [Condition 2: e.g., "P0 bug reported by beta tenants"]

### Rollback Steps
1. [Step 1: e.g., "Disable feature flag"]
2. [Step 2: e.g., "Revert deployment of service-1"]
3. [Step 3: e.g., "Run reverse migration (if applicable)"]

### Data Recovery
[If a rollback happens after data has been written in the new format, how do we handle it?]

---

## Observability

### Key Metrics to Monitor
| Metric | Threshold | Alert |
|--------|-----------|-------|
| [Metric name] | [Normal range] | [When to alert] |

### Logging
[What new log entries will be added? At what level?]

---

## Open Questions

> Items requiring team decision during review. Each question should have enough context for reviewers to make a call.

1. **[Question]**: [Context and options]
2. **[Question]**: [Context and options]

---

## Revision History

| Date | Author | Changes |
|------|--------|---------|
| YYYY-MM-DD | [Name] | Initial draft |

---

## Appendix

### References
- [Link to PRD]
- [Link to related ADRs]
- [Link to relevant documentation]

### Feedback Resolution (populated during review)
| # | Reviewer | Feedback | Resolution |
|---|----------|----------|------------|
| 1 | [Name] | [Feedback] | [Incorporated / Declined — reason] |

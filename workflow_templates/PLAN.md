---
Location: docs/adr/XXX-feature-name/PLAN.md
Status: DRAFT | APPROVED | REVISED
Created by: Architect Agent
Reviewed by: CTO Agent
Date: YYYY-MM-DD
---

# 🏗️ Implementation Plan: [Feature Name]

---

## 1. Architectural Context

### Files to be Modified


### Affected Layers


### Architecture Compliance Checklist

---

## 2. The Implementation Plan

> **Note:** The phases below are examples based on a layered architecture. Adapt phase names, ordering, and count to match the project's architecture pattern.

### Phase 1: Data Layer
**Goal:** Define and migrate data structures (schemas, models, migrations)

---

### Phase 2: Domain Layer
**Goal:** Implement core business entities and rules

---

### Phase 3: Interface / Port Layer
**Goal:** Define interfaces, DTOs, and contracts between layers

---

### Phase 4: Data Access Layer
**Goal:** Implement data persistence (repositories, data mappers, query builders)

---

### Phase 5: Service / Use Case Layer
**Goal:** Orchestrate business logic and coordinate between layers

---

### Phase 6: Boundary Layer
**Goal:** Expose external interfaces (HTTP handlers, CLI commands, event consumers)

---

### Phase 7: Testing & Quality
**Goal:** Ensure reliability and maintainability

---

## 3. Feature Flag Strategy

> If this feature introduces new behavior to an existing flow, describe the feature flag approach. If no feature flag is needed, state why.

| Flag Name | Scope | Default | Controls |
|-----------|-------|---------|----------|
| `feature.<name>.enabled` | Per-tenant / Global | `false` | [What behavior it gates] |

### Flag Behavior
- **Flag OFF:** [Existing behavior preserved — describe]
- **Flag ON:** [New behavior — describe]
- **Check location:** [Which layer — handler, service, or domain]
- **Cleanup plan:** Remove flag after [stabilization period]

> If no feature flag is needed: "No feature flag required — [reason, e.g., 'new additive endpoint, no existing flow modified']."

---

## 4. Verification Strategy

### Unit Tests


### Manual Testing
- [ ] Test happy path scenarios
- [ ] Test error scenarios
- [ ] Test edge cases

### API Verification Examples
> Architect-provided sample API calls for manual verification. QA Lead will refine these with actual implemented details.

```bash
# Example: [endpoint description]
curl -X [METHOD] http://localhost:[PORT]/api/v1/[path] \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"field": "value"}'
```

### Suggested Backyard APIs
> If this feature involves complex multi-step processes, suggest dev-only endpoints for easier testing.

| Process | Suggested Endpoint | What It Simulates |
|---------|--------------------|-------------------|
| [Complex flow] | `POST /backyard/...` | [What it shortcuts] |

---

## 5. Risk Mitigation

### Technical Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk description] | High/Medium/Low | [Strategy] |

### Implementation Risks
| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk description] | High/Medium/Low | [Strategy] |

---

## 🛑 CTO FEEDBACK

### Round 1 (if any)
[CTO feedback will be added here during review]

### Resolution
[Architect's response and changes made]

---

**Status Update:** 
- [ ] Plan created by Architect
- [ ] Under CTO review
- [ ] CTO approved (Status: APPROVED)
- [ ] Ready for Human commit
- [ ] Implementation started

**Next Step:** Architect to request CTO review. Upon approval, request Human commit before Implementor starts.

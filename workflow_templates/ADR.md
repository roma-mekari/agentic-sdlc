# ADR-XXX: [Short Title]

> **Location:** This file should be created at `docs/adr/XXX-feature-name.md` (main ADR)  
> **Supporting Artifacts:** Located in `docs/adr/XXX-feature-name/` subdirectory  

## Status
**[Proposed | Accepted | Deprecated]** - [Status description and date]

---

## Context

### The Problem
[Describe the business problem or technical challenge that motivated this decision]

### Business Requirements
[Summarize key requirements from REQUIREMENTS.md - do NOT copy entire document]
- Requirement 1
- Requirement 2
- Requirement 3

**Full details:** See [`docs/adr/XXX-feature-name/REQUIREMENTS.md`](./XXX-feature-name/REQUIREMENTS.md)

### Technical Requirements
- Performance expectations
- Compatibility constraints
- Security requirements
- Quality standards

---

## Decision

### High-Level Approach
[Brief summary of the solution chosen]

### Architecture & Design
[Summarize key architectural decisions from PLAN.md - do NOT copy entire plan]

**Full implementation plan:** See [`docs/adr/XXX-feature-name/PLAN.md`](./XXX-feature-name/PLAN.md)

#### Key Components
1. **Component 1**: Brief description
2. **Component 2**: Brief description
3. **Component 3**: Brief description

#### Design Decisions
- **Decision Point 1**: Chose X over Y because...
- **Decision Point 2**: Chose A over B because...

### Implementation Highlights
```
// Show critical code snippets if necessary (keep minimal)
```

---

## Consequences

### Positive
1. **Benefit 1**: Description
2. **Benefit 2**: Description
3. **Benefit 3**: Description

### Negative
1. **Trade-off 1**: Description and mitigation
2. **Trade-off 2**: Description and mitigation

### Trade-offs Accepted
| Decision | Choice | Trade-off | Justification |
|----------|--------|-----------|---------------|
| Pattern A vs B | Chose A | Complexity | Better performance |

---

## Compliance

### Verification Status
- **Verified by QA Report on:** [Date]
- **QA Verdict:** [✅ APPROVED | ❌ REJECTED]
- **Overall Quality Score:** XX/100
- **Test Coverage:** XX%

**Full QA report:** See [`docs/adr/XXX-feature-name/QA_REPORT.md`](./XXX-feature-name/QA_REPORT.md)

### Requirements Traceability
- ✅ Requirement category 1: X/Y criteria met
- ✅ Requirement category 2: X/Y criteria met
- ✅ Requirement category 3: X/Y criteria met

### Architecture Compliance
- ✅ Project architecture pattern followed
- ✅ Code conventions adhered to
- ✅ Security best practices implemented
- ✅ Error handling follows project standards
- ✅ Input validation at boundary layer

---

## References

**Project Artifacts:**
- **Requirements:** [`docs/adr/XXX-feature-name/REQUIREMENTS.md`](./XXX-feature-name/REQUIREMENTS.md)
- **Implementation Plan:** [`docs/adr/XXX-feature-name/PLAN.md`](./XXX-feature-name/PLAN.md)
- **QA Verification:** [`docs/adr/XXX-feature-name/QA_REPORT.md`](./XXX-feature-name/QA_REPORT.md)

**Code References:**
- **Branch:** `[branch-name]`
- **Commit:** `[commit-hash]`

**Related Documentation:**
- **REQUIREMENTS.md:** [Link to requirements](./XXX-feature-name/REQUIREMENTS.md)
- **Related ADRs:** [ADR-YYY](./YYY-related-feature.md)

---

## Future Considerations

Potential enhancements not in current scope:
1. **Enhancement 1**: Description
2. **Enhancement 2**: Description
3. **Enhancement 3**: Description

These can be addressed in future ADRs if business value is identified.

---

*This ADR documents [one-sentence summary of the decision]. The decision was made to [primary objective] while [key constraints or principles maintained].*

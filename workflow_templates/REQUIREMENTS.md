---
summary:
  user_stories: []
  acceptance_criteria_count: 0
  scope_included: []
  scope_deferred: []
  open_questions: []
  assumptions: []
---

# 🎯 Requirements: [Feature Name]

> **Location:** This file should be created at `docs/adr/XXX-feature-name/REQUIREMENTS.md`  
> **Created by:** Product Owner Agent  
> **Date:** YYYY-MM-DD  
> **Status:** Draft | Approved | Revised  

---

## 1. Executive Summary
> A concise 1-2 sentence description of what we are building and why it matters to the business.

---

## 2. User Stories

### Primary User Stories
- [ ] As a **[User Role]**, I want to **[Action]**, so that **[Business Benefit]**.
- [ ] As a **[User Role]**, I want to **[Action]**, so that **[Business Benefit]**.

### Secondary User Stories
- [ ] As a **[User Role]**, I want to **[Action]**, so that **[Business Benefit]**.

---

## 3. Acceptance Criteria

The feature is considered "Done" when:

### Functional Requirements
1. [ ] **[Criterion 1]**: Specific measurable outcome
2. [ ] **[Criterion 2]**: Specific measurable outcome
3. [ ] **[Criterion 3]**: Specific measurable outcome

### Non-Functional Requirements
1. [ ] **Performance**: Response time < XXms under normal load
2. [ ] **Security**: [Specific security requirements]
3. [ ] **Reliability**: [Uptime or error rate requirements]

### Quality Requirements
1. [ ] **Code Quality**: Passes lint and static analysis checks without warnings
2. [ ] **Test Coverage**: Minimum XX% coverage for new code
3. [ ] **Documentation**: All public APIs documented

---

## 4. Technical Constraints

> **Note:** Derive these from the project's established conventions. The examples below are placeholders — replace them with the actual project conventions.

### Must Have
* **Architecture**: Follow the project's architecture pattern
* **Error Handling**: Use the project's prescribed error handling pattern
* **Conventions**: Adhere to all established code conventions

### Must Not Have
* **Breaking Changes**: No changes to existing public APIs
* **Dependencies**: No new external dependencies without approval
* **Secrets**: No hardcoded credentials or environment-specific values

### Out of Scope
* Feature X (deferred to Phase 2)
* Enhancement Y (separate ADR needed)

---

## 5. Success Metrics

How will we measure success?

1. **User Impact**: [Metric, e.g., "50% reduction in task completion time"]
2. **System Performance**: [Metric, e.g., "99.9% uptime"]
3. **Code Quality**: [Metric, e.g., "Zero critical security vulnerabilities"]

---

## 6. Dependencies

### Internal Dependencies
- Module A must be updated first
- Migration X must be applied before deployment

### External Dependencies
- Third-party service availability
- Database version compatibility

---

## 7. Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| [Risk 1] | High | Medium | [Strategy] |
| [Risk 2] | Medium | Low | [Strategy] |

---

## 8. Open Questions

1. **[Question 1]**: What is the expected behavior when...?
   - **Answer**: [To be determined by Human]

2. **[Question 2]**: Should we...?
   - **Answer**: [To be determined by Human]

---

**Next Step:** Product Owner to request Human review and commit before Architect begins planning.

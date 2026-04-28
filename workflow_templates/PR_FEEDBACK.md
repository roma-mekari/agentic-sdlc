---
summary:
  total_comments: 0
  actionable: 0
  informational: 0
  categories_breakdown:
    REQ_GAP: 0
    ARCH_CONCERN: 0
    CODE_FIX: 0
    STYLE_NIT: 0
    QUESTION: 0
    OUT_OF_SCOPE: 0
---

# 🔀 PR Feedback Resolution

> **Location:** This file should be created at `docs/adr/XXX-feature-name/PR_FEEDBACK.md`
> **Analyzed by:** PR Reviewer Agent
> **Date:** YYYY-MM-DD
> **PR:** [PR number or link]
> **Feature:** [Feature Name]
> **Feedback Round:** N

---

## Executive Summary

**Total Comments:** X
**Actionable:** Y (requiring code or artifact changes)
**Informational:** Z (questions + out-of-scope)

**Summary:** [1-2 sentences describing the overall PR feedback and its impact on the feature]

---

## 📋 Feedback Classification

### Requirement Gaps (`REQ_GAP`)

> These comments reveal missing or misunderstood requirements. Resolving them requires updating REQUIREMENTS.md → PLAN.md → Code.

| # | Comment | File / Line | Resolution Action | Status |
|---|---------|-------------|-------------------|--------|
| 1 | [Verbatim comment] | `path/to/file:L42` | [What needs to change] | ⬜ Pending |

---

### Architecture Concerns (`ARCH_CONCERN`)

> These comments identify design or structural issues. Resolving them requires updating PLAN.md → CTO review → Code changes.

| # | Comment | File / Line | Resolution Action | Status |
|---|---------|-------------|-------------------|--------|
| 1 | [Verbatim comment] | `path/to/file:L42` | [What needs to change] | ⬜ Pending |

---

### Code Fixes (`CODE_FIX`)

> These comments identify bugs, logic errors, or missing edge cases. Resolving them requires code changes + scoped QA re-verification.

| # | Comment | File / Line | Resolution Action | Status |
|---|---------|-------------|-------------------|--------|
| 1 | [Verbatim comment] | `path/to/file:L42` | [What needs to change] | ⬜ Pending |

---

### Style & Nits (`STYLE_NIT`)

> These comments are cosmetic — naming, formatting, readability. Batched together for a single Implementor pass. No re-verification needed.

| # | Comment | File / Line | Resolution Action | Status |
|---|---------|-------------|-------------------|--------|
| 1 | [Verbatim comment] | `path/to/file:L42` | [What needs to change] | ⬜ Pending |

---

### Questions (`QUESTION`)

> These comments ask for clarification. Surfaced to the human for response — no agent action needed.

| # | Comment | File / Line | Human Response |
|---|---------|-------------|----------------|
| 1 | [Verbatim comment] | `path/to/file:L42` | ⬜ Awaiting answer |

---

### Out of Scope (`OUT_OF_SCOPE`)

> These comments are valid but belong to a separate feature or follow-up ticket. Each item includes priority and consequences to ensure nothing falls through the cracks. These will be forwarded to the ADR's "Deferred Items" section.

| # | Comment | Reasoning | Priority | Impact if Not Addressed | Follow-up Action |
|---|---------|-----------|----------|------------------------|------------------|
| 1 | [Verbatim comment] | [Why it's out of scope] | High/Medium/Low | [What happens if not picked up — technical debt, risk, etc.] | [e.g., "Create ticket for..."] |

---

## 🗺️ Resolution Plan

### Execution Order

The following agents will be invoked in order to resolve all actionable feedback:

| Step | Agent | Scope | Feedback Items |
|------|-------|-------|----------------|
| 1 | PO | Update REQUIREMENTS.md for gaps | REQ_GAP #1, #2 |
| 2 | Architect | Revise PLAN.md for arch concerns | ARCH_CONCERN #1 |
| 3 | CTO | Re-review revised plan | — |
| 4 | Implementor | Apply code fixes + arch changes + nits | CODE_FIX #1-3, ARCH_CONCERN #1, STYLE_NIT #1-4 |
| 5 | QA Lead | Re-verify implementation | — |

> Steps are skipped if no feedback items require that agent. For example, if there are no `REQ_GAP` items, skip PO.

### Re-verification Scope

- **Full re-verification:** Required if any `REQ_GAP` or `ARCH_CONCERN` items exist
- **Scoped re-verification:** Required if only `CODE_FIX` items exist (QA checks only affected areas)
- **No re-verification:** Required if only `STYLE_NIT` items exist

---

## 📊 Resolution Tracking

| Round | Date | Comments Resolved | Comments Remaining | Status |
|-------|------|-------------------|--------------------|--------|
| 1 | YYYY-MM-DD | X/Y | Z | ⬜ In Progress |

---

## ✅ Final Status

- [ ] All `REQ_GAP` items resolved
- [ ] All `ARCH_CONCERN` items resolved
- [ ] All `CODE_FIX` items resolved
- [ ] All `STYLE_NIT` items resolved
- [ ] All `QUESTION` items answered
- [ ] QA re-verification passed (if required)
- [ ] ADR updated (if material changes were made)
- [ ] PR approved and ready to merge

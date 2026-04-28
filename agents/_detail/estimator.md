# Estimator — Detail Sheet

> Loaded on-demand for Medium/Complex tasks. Companion to the compact role card.

## Process

### Step 1 — Understand the Scope

1. Read the input document(s) thoroughly.
2. Identify all distinct work items (features, stories, tasks).
3. If PRD, decompose into implementable slices. If PRD_REVIEW.md exists, use its "Suggested SDLC Breakdown" as starting point.

### Step 2 — Analyze Codebase Complexity

If Explorer reports are provided:
1. **Existing patterns**: Does similar functionality already exist? Anchor to it. If no, add "new pattern" risk multiplier.
2. **Files to touch**: Count layers and files. More files = more integration effort.
3. **Test coverage**: Is affected area well-tested? Poor coverage = higher regression risk.
4. **Tech debt**: TECH_DEBT markers or known debt? Increases effort.
5. **Integration points**: External APIs, event systems, shared databases — each adds coordination cost.

If no Explorer report, flag estimates as **low-confidence**, PRD-only.

### Step 3 — Estimate Each Work Item

| Factor | Weight | Assessment |
|--------|--------|------------|
| Scope clarity | High | Is requirement unambiguous? |
| Pattern familiarity | High | Existing patterns or new ones? |
| Layer count | Medium | How many architectural layers touched? |
| Integration complexity | Medium | External dependencies, cross-service calls? |
| Data model changes | High | Schema migrations, data backfills? |
| Test effort | Medium | How much new test code needed? |
| Risk factors | High | What could go wrong? |

### Step 4 — Apply Risk Multipliers

| Risk Factor | Multiplier | Condition |
|-------------|-----------|-----------|
| New pattern (no existing analog) | 1.5x | No similar feature exists |
| Schema migration | 1.3x | ALTER TABLE or new tables |
| External API integration | 1.3x | New third-party dependency |
| Cross-service coordination | 1.5x | Changes span multiple repos/services |
| Ambiguous requirements | 1.3x | PRD has unresolved ambiguities |
| High tech debt in area | 1.2x | Explorer found significant debt |
| No existing test coverage | 1.3x | Poor test coverage in affected code |

Multiple risk multipliers stack (multiply, don't add).

### Step 5 — Produce Estimation

Use `vscode/askQuestions` to confirm: team's story point scale (Fibonacci vs linear), velocity context, whether to include QA/review time.

Write to `docs/pre-sdlc/ESTIMATION-<slug>.md`. Create `docs/pre-sdlc/` if it doesn't exist.

## Format Templates

### Full Estimation Output

```markdown
# Estimation: [Feature/PRD Title]

> **Estimated by:** Estimator Agent
> **Date:** YYYY-MM-DD
> **Input source:** [PRD / RFC / REQUIREMENTS.md / Raw task]
> **Codebase analyzed:** [Yes (with Explorer) / No (PRD-only)]
> **Confidence:** High / Medium / Low
> **Scale:** Fibonacci SP (1,2,3,5,8,13,21)

---

## Summary

| Metric | Value |
|--------|-------|
| Total stories | X |
| Total SP (optimistic) | X |
| Total SP (likely) | X |
| Total SP (pessimistic) | X |
| Key risks | [Brief list] |

---

## Detailed Breakdown

### Story 1: [Story Name]

**Description:** [What needs to be built]

| Factor | Assessment |
|--------|------------|
| Pattern | Existing / New |
| Layers touched | [List] |
| Integration points | [List or "None"] |
| Risk multipliers | [List applied] |

| Estimate | SP | Reasoning |
|----------|----|-----------|
| Optimistic | X | [Everything goes smoothly] |
| Likely | X | [Normal development] |
| Pessimistic | X | [Risk factors materialize] |

---

## Risk Register

| # | Risk | Impact on Estimate | Probability | Mitigation |
|---|------|-------------------|-------------|------------|
| 1 | [Risk] | +X SP | High/Med/Low | [How to reduce] |

## Assumptions

1. [Assumption 1] — If wrong, estimate changes by: [+/- X SP]

## Recommendations

- [Suggestions for reducing effort]
- [Suggested story ordering for risk reduction]
- [Items that could be deferred]
```

### Jira-Friendly Output

```
## Jira Import Ready

| Story | SP (Likely) | Priority | Dependencies | Notes |
|-------|------------|----------|-------------|-------|
| [Story 1] | X | High/Med/Low | [Story N] | [Brief note] |
```

## Classification / Decision Rules

None specified beyond risk multiplier table.

## Specialized Protocols

None specified beyond estimation philosophy.

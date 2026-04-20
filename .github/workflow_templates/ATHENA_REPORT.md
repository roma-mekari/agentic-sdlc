# 🦉 Athena Meta-Analysis Report

> **Location:** This file should be created at `docs/athena/YYYY-MM-DD-<slug>.md`  
> **Analyzed by:** Athena Meta-Architect Agent  
> **Date:** YYYY-MM-DD  
> **Trigger:** [Manual | Auto-triggered after QA rejection cycle N]  
> **Analyzed Run:** [Feature slug or description of the workflow run]  

---

## Executive Summary

**Issues Found:** X total (Y critical, Z high)

**Summary:** [1-3 sentences describing what went wrong and the overall health of the agent workflow]

---

## 📊 Agent Performance Analysis

### Per-Agent Assessment

| Agent | Instruction Adherence | Tool Usage | Context Retention | Issues Found |
|-------|----------------------|------------|-------------------|--------------|
| SDLC Orchestrator | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | X |
| PO | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | X |
| Architect | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | X |
| CTO | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | X |
| Implementor | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | X |
| QA Lead | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | X |
| Tech Writer | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | X |

---

## 🔍 Root Cause Analysis

### Issue 1: [Short description]

- **Severity:** CRITICAL | HIGH | MEDIUM | LOW
- **Agent:** [Which agent]
- **Category:** [Workflow Friction | Instruction Violation | Tool Misuse | Context Loss | Quality Gap]
- **What happened:** [Factual description of the failure]
- **Root cause:** [Which instruction (or lack thereof) allowed this]
- **Evidence:** [Quote from transcript or artifact]

---

### Issue N: [Short description]

_(Repeat the above structure for each issue)_

---

## 🔧 Proposed Instruction Changes

### Change 1: [Agent Name] — [Brief description]

**Severity:** CRITICAL | HIGH | MEDIUM | LOW

**File:** `.github/agents/[agent-name].agent.md`

**Before:**
```markdown
[Exact current text from the agent's instruction file]
```

**After:**
```markdown
[Proposed replacement text]
```

**Rationale:** [Why this change prevents the identified failure]

---

### Change N: [Agent Name] — [Brief description]

_(Repeat the above structure for each proposed change)_

---

## 🪞 Self-Assessment (Athena)

### Did this analysis miss anything?
[Honest assessment of blind spots or limitations in this analysis]

### Proposed self-improvement

**File:** `.github/agents/athena.agent.md`

**Before:**
```markdown
[Current text, or "N/A — new addition"]
```

**After:**
```markdown
[Proposed text]
```

**Rationale:** [Why this makes future analyses better]

_(If no self-improvement needed, state: "No self-improvement proposals. Current instructions adequately covered this scenario.")_

---

## 📈 Trend Analysis

> This section is populated when multiple Athena reports exist in `docs/athena/`. Skip on first run.

### Recurring Patterns
- [Pattern 1]: Seen in X/Y reports. Status: [Addressed | Still occurring]
- [Pattern 2]: Seen in X/Y reports. Status: [Addressed | Still occurring]

### Improvement Trajectory
- **Previous run score:** [if available]
- **This run score:** [subjective 1-10 rating of workflow health]
- **Trend:** Improving | Stable | Degrading

---

## Action Items

| # | Action | Agent | Severity | Status |
|---|--------|-------|----------|--------|
| 1 | [Specific change to make] | [Agent name] | CRITICAL | ⬜ Pending human review |
| 2 | [Specific change to make] | [Agent name] | HIGH | ⬜ Pending human review |

> **Reminder:** All changes are advisory. A human must review and apply each proposed instruction change.

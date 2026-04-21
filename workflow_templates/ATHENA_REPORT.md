# 🦉 Athena Meta-Analysis Report

> **Location:** This file should be created at `docs/athena/YYYY-MM-DD-<slug>.md`  
> **Analyzed by:** Athena Meta-Architect Agent  
> **Date:** YYYY-MM-DD  
> **Trigger:** [Manual | Auto-triggered after QA rejection cycle N | Auto-triggered after reflection accumulation (N reflections for agent X)]  
> **Analyzed Run:** [Feature slug or description of the workflow run]  
> **Micro-reflections consumed:** X entries from `docs/athena/reflections.jsonl`

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
| PR Reviewer | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | ✅ / ⚠️ / ❌ | X |

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

**File:** `agents/[agent-name].agent.md`

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

**File:** `agents/athena.agent.md`

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

## � Session Analysis (Session Analysis Mode Only)

> Include this section only when analyzing an exported chat session. Remove if not applicable.

### Delegation Audit Summary

| Metric | Count |
|--------|-------|
| Total actions in session | X |
| Correct delegations (`runSubagent` used) | X |
| Missing delegations (should have delegated) | X |
| Skipped human review gates | X |
| VIOLATION trace entries | X |

### Action-by-Action Breakdown

| # | Action | Tool Used | Classification | Expected Agent | Notes |
|---|--------|-----------|----------------|----------------|-------|
| 1 | [Description] | [Tool] | CORRECT_DELEGATION / MISSING_DELEGATION / SKIPPED_GATE | [Agent] | [Brief note] |

### Thinking Trace Violations

> These are the highest-signal findings — moments where the model explicitly decided to bypass delegation.

#### Violation 1: [Description]

**Thinking trace quote:**
> "[Exact quote from the model's thinking that shows the bypass decision]"

**Expected behavior:** [What the orchestrator should have done instead]
**Root cause in instructions:** [Which instruction was too weak to prevent this]

### Workflow Stage Compliance

| Stage | Expected | Actual | Status |
|-------|----------|--------|--------|
| Stage 0: Context Discovery | Delegate to `explorer` | [What actually happened] | ✅ / ❌ |
| Stage 1: Requirements | Delegate to `po` | [What actually happened] | ✅ / ❌ |
| Stage 2: Architecture | Delegate to `architect` + `cto` | [What actually happened] | ✅ / ❌ |
| Stage 3: Implementation | Delegate to `implementor` + `qa-lead` | [What actually happened] | ✅ / ❌ |
| Human review gates | Present after each stage | [What actually happened] | ✅ / ❌ |
| Trace logging | Maintain TRACE.jsonl | [What actually happened] | ✅ / ❌ |

---

## �📝 Micro-Reflections Consumed

> List the micro-reflection entries from `docs/athena/reflections.jsonl` that were analyzed and incorporated into this report. This allows the human to mark them as addressed.

| Date | Agent | Signal Type | Feedback Summary | Incorporated Into |
|------|-------|-------------|------------------|-------------------|
| YYYY-MM-DD | [Agent] | [Type] | [Summary] | Issue #N above |

> After applying the changes from this report, update the `applied` field in `reflections.jsonl` for these entries.

---

## Action Items

| # | Action | Agent | Severity | Status |
|---|--------|-------|----------|--------|
| 1 | [Specific change to make] | [Agent name] | CRITICAL | ⬜ Pending human review |
| 2 | [Specific change to make] | [Agent name] | HIGH | ⬜ Pending human review |

> **Reminder:** All changes are advisory. A human must review and apply each proposed instruction change.

# QA Lead — Detail Sheet

> Loaded on-demand for Medium/Complex tasks. Companion to the compact role card.

## Process

1. **Read the templates**: Load `.github/workflow_templates/QA_REPORT.md`. Also load `.github/workflow_templates/REQUIREMENTS.md` and `.github/workflow_templates/PLAN.md` to understand the expected structure of the artifacts you are verifying against.
2. **Read REQUIREMENTS.md** and extract all acceptance criteria (functional, non-functional, quality).
3. **Read PLAN.md** and extract all implementation phases and their completion criteria.
4. **Inspect the implementation**:
   - Verify each file listed in PLAN.md exists and contains the described logic.
   - Run the test suite using the test command from the project context.
   - Check test coverage meets the requirement stated in REQUIREMENTS.md.
   - Review code for obvious security issues (unvalidated input at boundary layer, hardcoded secrets, injection patterns).
5. **Plan Drift Detection**: Compare the actual implementation against PLAN.md:
   - Are there files or functions that weren't in the plan?
   - Were any planned steps skipped or implemented differently?
   - Were there manual edits or changes since the last Implementor run?
   - Note deviations in the "Plan Drift Detection" section of QA_REPORT.md with severity (None / Minor / Moderate / Major).
6. **Deferred Items**: Identify items that are valid quality concerns but out-of-scope:
   - Edge cases not covered but acceptable for now
   - Performance optimizations that could be deferred
   - Test coverage gaps in non-critical paths
   - Note these in the "Deferred & Out-of-Scope Items" section with priority and impact.
7. **Tech Debt Assessment**: Identify tech debt in the implemented code:
   - Scan for `TECH_DEBT()` markers left by the Implementor
   - Check if the Implementor flagged any tech debt items in their output
   - Identify additional debt: missing abstractions, duplicated logic, overly complex functions
   - Note these in the "Tech Debt Assessment" section with priority and suggested action (fix now vs. defer).
8. **Developer/QA Test Playbook**: Generate a practical test playbook for humans:
   - **API endpoints**: For every new or modified endpoint, generate actual curl commands derived from the implemented route definitions, handler signatures, and request/response types. Include headers, auth tokens (as placeholders), and realistic sample payloads.
   - **Error scenarios**: Include curls for validation failures, auth errors, not-found cases.
   - **Backyard API suggestions**: For complex processes (multi-step workflows, async operations, third-party integrations), suggest creating a "backyard" endpoint — a dev/staging-only API that simulates or fast-forwards the process.
   - **Browser/UI test steps**: For UI-facing features, provide step-by-step manual test flows with expected outcomes.
   - Base ALL curls and test data on actual code — never fabricate endpoints or payloads.
9. **Write QA_REPORT.md** at `docs/adr/XXX-<feature-slug>/QA_REPORT.md` filling every section:
   - Executive Summary with overall verdict and quality score (0–100)
   - Requirements Verification table (each criterion: PASS / PARTIAL / FAIL)
   - Plan Completion Verification table (each phase step: Complete / Partial / Incomplete)
   - Plan Drift Detection (new)
   - Deferred & Out-of-Scope Items (new)
   - Testing Verification (test output, coverage, per-category checklist)
   - Code Quality Assessment
   - Security Review
   - Final Recommendation

## Format Templates

```bash
# Create Job Listing (happy path)
curl -X POST http://localhost:8080/api/v1/job-listings \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"title": "Software Engineer", "department_id": 1, ...}'

# Expected: 201 Created with job listing ID
```

```
### Suggested Backyard APIs
| Process | Suggested Endpoint | What It Simulates | Why Useful |
|---------|-------------------|-------------------|------------|
| Candidate hiring flow | POST /backyard/candidates/:id/fast-hire | Skips assessment + interview, moves directly to hired | Testing downstream effects of hire without full flow |
```

QA_REPORT.md sections:
- Executive Summary with overall verdict and quality score (0–100)
- Requirements Verification table (each criterion: PASS / PARTIAL / FAIL)
- Plan Completion Verification table (each phase step: Complete / Partial / Incomplete)
- Plan Drift Detection
- Deferred & Out-of-Scope Items
- Testing Verification (test output, coverage, per-category checklist)
- Code Quality Assessment
- Security Review
- Final Recommendation

```
VERDICT: APPROVED | APPROVED WITH NOTES | REJECTED
Quality Score: XX/100
QA_REPORT.md created: docs/adr/XXX-<feature-slug>/QA_REPORT.md
Blockers: <only if REJECTED — list specifically>
```

## Classification / Decision Rules

## Scoring

Calculate the quality score as:
```
score = (requirements_pass% * 0.4) + (plan_complete% * 0.3) + (test_coverage% * 0.2) + (security_pass% * 0.1)
```

## Verdict Rules

| Verdict | Condition |
|---------|-----------|
| ✅ APPROVED | Score ≥ 80 AND no FAIL items in requirements AND no critical security issues |
| ⚠️ APPROVED WITH NOTES | Score 60–79 OR PARTIAL items exist but no blockers |
| ❌ REJECTED | Score < 60 OR any FAIL in acceptance criteria OR any critical security issue |

## Specialized Protocols

## Plan Drift Detection

Compare the actual implementation against PLAN.md:
- Are there files or functions that weren't in the plan?
- Were any planned steps skipped or implemented differently?
- Were there manual edits or changes since the last Implementor run?
- Note deviations in the "Plan Drift Detection" section of QA_REPORT.md with severity (None / Minor / Moderate / Major).

## Deferred Items

Identify items that are valid quality concerns but out-of-scope:
- Edge cases not covered but acceptable for now
- Performance optimizations that could be deferred
- Test coverage gaps in non-critical paths
- Note these in the "Deferred & Out-of-Scope Items" section with priority and impact.

## Tech Debt Assessment

Identify tech debt in the implemented code:
- Scan for `TECH_DEBT()` markers left by the Implementor
- Check if the Implementor flagged any tech debt items in their output
- Identify additional debt: missing abstractions, duplicated logic, overly complex functions
- Note these in the "Tech Debt Assessment" section with priority and suggested action (fix now vs. defer).

## Developer/QA Test Playbook

- **API endpoints**: For every new or modified endpoint, generate actual curl commands derived from the implemented route definitions, handler signatures, and request/response types. Include headers, auth tokens (as placeholders), and realistic sample payloads.
- **Error scenarios**: Include curls for validation failures, auth errors, not-found cases.
- **Backyard API suggestions**: For complex processes (multi-step workflows, async operations, third-party integrations), suggest creating a "backyard" endpoint — a dev/staging-only API that simulates or fast-forwards the process.
- **Browser/UI test steps**: For UI-facing features, provide step-by-step manual test flows with expected outcomes.
- Base ALL curls and test data on actual code — never fabricate endpoints or payloads.

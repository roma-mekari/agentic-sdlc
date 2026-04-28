# CTO — Detail Sheet

> Loaded on-demand for Medium/Complex tasks. Companion to the compact role card.

## Process

### Review Checklist

Evaluate the plan against **all** of the following:

#### Alignment
- [ ] Every acceptance criterion in REQUIREMENTS.md is addressed by at least one phase in PLAN.md
- [ ] Technical constraints (Must Have / Must Not Have) are respected
- [ ] Out-of-scope items are not included in the plan

#### Completeness
- [ ] All implementation phases have specific file paths, not vague descriptions
- [ ] Testing strategy covers unit and integration tests with measurable targets
- [ ] Risk Mitigation table is populated and credible

#### Architecture Quality
- [ ] The plan follows the project's architecture pattern
- [ ] Dependency direction is respected (inner layers do not depend on outer layers)
- [ ] Data access follows the project's established data access pattern
- [ ] No unnecessary new external dependencies introduced

#### Security
- [ ] Input validation is planned at the boundary layer
- [ ] No hardcoded credentials or secrets in the plan
- [ ] Error responses do not leak internal details

#### Feature Flag Compliance
- [ ] If the plan introduces new behavior to an existing flow, a feature flag strategy is included
- [ ] Feature flag scope is appropriate (per-tenant for multi-tenant, global for single-tenant)
- [ ] The plan specifies behavior for BOTH flag-on and flag-off states
- [ ] Flag cleanup is planned (not left as permanent tech debt)
- [ ] If an RFC exists, the feature flag strategy aligns with the RFC's rollout plan
- [ ] If no feature flag is needed, the plan explicitly states why (e.g., "new additive endpoint, no existing flow modified")

#### Feasibility
- [ ] The phased approach is logically ordered (no phase depends on a later phase)
- [ ] The plan is implementable by a single engineer without undefined prerequisites

## Format Templates

### APPROVED Output

```
VERDICT: APPROVED
Checklist passed: X/Y items
Issues:
- <none>
```

### REVISION REQUIRED Output

```
VERDICT: REVISION REQUIRED
Checklist passed: X/Y items
Issues:
- [Phase X / Section Y]: <what is wrong and what is expected instead>
```

## Classification / Decision Rules

None specified beyond checklist.

## Specialized Protocols

None specified beyond standard review process.

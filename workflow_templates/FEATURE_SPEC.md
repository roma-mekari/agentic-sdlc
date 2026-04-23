# Feature Spec: [Feature Name]

> **Location:** `docs/specs/<feature-slug>.md`  
> **Last updated:** YYYY-MM-DD  
> **Last updated by:** ADR-XXX  
> **Status:** Draft | Active | Deprecated  

---

## Overview

[1-2 paragraph description of this feature — what it does, who uses it, why it exists]

---

## Sub-Features

> Each sub-feature represents a distinct capability within this feature area. Organized by user-facing function.

### [Sub-Feature Name] (e.g., "Index Page", "Create", "Filter")

**Description:** [What this sub-feature does]

**User Flow:**
1. [Step 1]
2. [Step 2]
3. [Step N]

**API Endpoints:**
| Method | Path | Description | Auth Required |
|--------|------|-------------|---------------|
| GET | `/api/v1/...` | [Description] | Yes |

**Key Business Rules:**
- [Rule 1]
- [Rule 2]

**Data Model:**
- [Entity/field relationships relevant to this sub-feature]

**ADR References:**
- ADR-XXX: [What it changed about this sub-feature]

---

## Integration Points

| System | Direction | Protocol | Description |
|--------|-----------|----------|-------------|
| [External system] | Inbound/Outbound | REST/Event/etc. | [What data flows] |

---

## Configuration & Feature Flags

| Config Key | Type | Default | Description |
|------------|------|---------|-------------|
| `feature.x.enabled` | bool | true | [What it controls] |

---

## Known Limitations & Tech Debt

| # | Description | Priority | Source ADR | Date Identified |
|---|-------------|----------|-----------|-----------------|
| 1 | [Limitation] | High/Medium/Low | ADR-XXX | YYYY-MM-DD |

---

## Change History

| Date | ADR | Change Summary |
|------|-----|----------------|
| YYYY-MM-DD | ADR-XXX | Initial spec created |
| YYYY-MM-DD | ADR-YYY | Added [sub-feature] |

---

*This spec is the living truth for [feature name]. Individual ADRs document why changes were made; this document reflects the current state.*

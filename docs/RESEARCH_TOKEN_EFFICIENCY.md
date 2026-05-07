# Token Efficiency: Concrete Implementation Guide

> **Status**: Refocused — concrete designs for immediate implementation
> **Corrected baseline**: ~32K tokens in agent files (not 67K), ~9.4K in templates (not 33K)
> **Principle**: No MCP required for savings. Instruction-only changes deliver 60-80% reduction.

---

## The Real Numbers

### Agent Files (Actual Count)

| Agent | Lines | Est. Tokens | Essential? |
|---|---:|---:|---|
| sdlc-orchestrator | 446 | 6,164 | Core — stays loaded |
| athena | 357 | 5,134 | On-demand only |
| tech-writer | 250 | 2,724 | Role card candidate |
| dev | 238 | 2,586 | Role card candidate |
| estimator | 203 | 2,037 | Role card candidate |
| prd-analyst | 179 | 1,802 | Role card candidate |
| architect | 158 | 1,674 | Role card candidate |
| explorer | 147 | 1,745 | Role card candidate |
| qa-lead | 137 | 1,767 | Role card candidate |
| rfc-writer | 119 | 1,406 | Role card candidate |
| po | 117 | 1,188 | Role card candidate |
| pr-reviewer | 106 | 1,272 | Role card candidate |
| implementor | 108 | 1,409 | Role card candidate |
| cto | 105 | 995 | Role card candidate |
| **Total** | **2,670** | **~31,900** | |

### What's Actually in Each Agent File

Every agent has this structure — and ~50-60% is boilerplate:

```
Frontmatter (6 lines)        — essential, can't compress
Role Boundary (8-12 lines)   — SAME pattern across all 14 files
Invocation Verification (6 lines) — same pattern, slightly different inputs
Input section (4-8 lines)    — slightly different per agent
Process (20-60 lines)        — THE UNIQUE VALUE, must keep
Constraints (6-10 lines)     — SAME "DO NOT" pattern across all
Output Format (8-15 lines)   — template reference, could be external
```

**The compression target**: Extract the shared boilerplate into one "Core Runtime Contract" (~500 tokens), keep only the unique Process + specific inputs per agent.

### Templates (Actual Count)

| Template | Lines | Est. Tokens |
|---|---:|---:|
| QA_REPORT.md | 333 | 2,040 |
| RFC.md | 210 | 1,373 |
| ATHENA_REPORT.md | 188 | 1,509 |
| ADR.md | 165 | 1,234 |
| PLAN.md | 143 | 882 |
| PR_FEEDBACK.md | 125 | 1,114 |
| REQUIREMENTS.md | 108 | 780 |
| FEATURE_SPEC.md | 79 | 477 |
| **Total** | **1,351** | **~9,400** |

### Corrected Cost Profile

| Component | Tokens | Per Run | Notes |
|---|---:|---:|---|
| Orchestrator (always loaded) | 6,164 | 6.2K | Only agent that stays in context |
| Subagent instruction (1 of 13) | 1,000-5,100 | 2.4K avg × 8 invocations = 19K | Loaded once per invocation |
| Project context (re-sent each invocation) | ~3,000 | 3K × 8 = 24K | **Biggest waste** |
| Workflow template (loaded per stage) | ~1,200 avg | 1.2K × 6 = 7.2K | |
| Generated artifacts (cumulative reads) | ~5,000 | 5K × 5 = 25K | Grows each stage |
| Orchestrator accumulated context | variable | 15-40K | Re-sent on every turn |
| Human gate interactions | variable | 10-30K | Full context re-sent |
| **Estimated total** | | **~110-150K** | (Not 180-320K as previously claimed) |

---

## Pillar 1: Two-Layer Instruction Architecture

### Source Pattern: oh-my-agent (810★)

**Their architecture:**
- Layer 1: SKILL.md (~800 bytes / ~900 tokens) — always loaded, contains core rules + references
- Layer 2: resources/ directory — execution-protocol.md, examples.md, tech-stack.md, etc. — loaded on-demand by difficulty
- Difficulty assessed at Step 0: Simple/Medium/Complex → different resource loading
- **Verified savings: 72-78%** (6,660 tokens → 1,469 tokens for a Simple frontend task)

### Our Adaptation

**Current**: 14 `.agent.md` files, each a full persona (avg 2,100 tokens).

**Target**: One shared Core Contract + 14 compact Role Cards + on-demand Detail Sheets.

```
agents/
├── _core.md                    # Shared contract (~500 tokens, always loaded)
├── architect.md                # Role card (~300 tokens)
├── implementor.md              # Role card (~250 tokens)
├── qa-lead.md                  # Role card (~250 tokens)
├── ... (11 more role cards)
└── _detail/                    # On-demand detail sheets
    ├── architect-full.md       # Full process (~1,500 tokens)
    ├── implementor-full.md     # Full process (~1,200 tokens)
    └── ...
```

### The Core Runtime Contract (_core.md)

Shared by ALL agents. Replaces the repeated Role Boundary, Invocation Verification, Constraints, and Output Format boilerplate.

```markdown
# SDLC Agent Core Contract

## Universal Rules
- You are a specialist. Do ONLY your role. Refuse out-of-scope requests.
- Read ONLY what your role requires. Do NOT read source code unless your role allows it.
- Edit ONLY what your role produces. Do NOT touch other agents' files.
- Be terse. Drop filler, hedging, pleasantries. State decisions and data. [caveman mode]
- Use `vscode/askQuestions` to resolve ambiguities BEFORE producing output.

## Required Inputs (verify before starting)
- Project context from orchestrator (language, framework, conventions)
- Input artifacts for your stage
- On revision: feedback/human decisions from prior attempt

If required inputs missing → report what's missing, stop. Do NOT guess.

## Constraints
- DO NOT make decisions outside your domain.
- DO NOT skip template sections. If N/A, state why.
- DO NOT leave placeholder text.
- DO NOT modify files not listed in your role.

## Output Format
Return structured output to orchestrator. State: what was produced, where, revision count.
```

**Token cost: ~500 tokens.** Currently each of 14 agents has ~400 tokens of overlapping boilerplate. Savings: 14 × 400 - 500 = **5,100 tokens eliminated**.

### Role Card Template

Each agent gets a compact card following this structure:

```markdown
---
name: "Architect"
description: "Presents 2-3 approaches with trade-offs, then produces PLAN.md"
tools: [read, edit, search, vscode/askQuestions]
detail: "_detail/architect-full.md"
---

## Your Role
Present architectural options → human chooses → detail into PLAN.md.

## Inputs
- REQUIREMENTS.md (required)
- Explorer report (required)
- On revision: CTO feedback or chosen approach

## Process
1. Read REQUIREMENTS.md + Explorer report
2. Present 2-3 approaches (each: description, pros, cons, effort, key files)
3. Recommend one, flag key decisions
4. On revision: read PLAN.md template, write PLAN.md with chosen approach

## Output
First invocation: approaches with trade-offs
Revision: `PLAN.md created: docs/adr/XXX-slug/PLAN.md`

## Role Boundaries
NO code. NO requirements. ONLY PLAN.md. NO tests.
```

**Token cost: ~250-350 tokens per card.**

### Before/After: Architect Agent

**Before** (1,674 est. tokens, 158 lines):
```
- Full role boundary section (8 lines)
- Invocation verification (6 lines)
- Clarification protocol (5 lines)
- Input section (5 lines)
- Process — approaches (42 lines with format template)
- Feature flag assessment (26 lines)
- Codebase investigation (2 lines)
- Constraints (5 lines)
- Output (6 lines)
```

**After** (~300 tokens in role card + ~1,200 tokens in detail sheet loaded on-demand):
```
Role card: ~300 tokens (above)
Detail sheet (_detail/architect-full.md): ~1,200 tokens
  - Feature flag assessment matrix
  - Approach format template
  - Clarification protocol
```

**Savings: 1,674 → 300 tokens loaded = 82% reduction** for the typical invocation. Detail sheet loaded only on Complex tasks.

### Difficulty Classification (per oh-my-agent)

The orchestrator assesses difficulty before delegating:

| Difficulty | Criteria | What's Loaded | Tokens |
|---|---|---|---|
| **Simple** | Bug fix, single file, clear requirements | Core + Role Card | ~800 |
| **Medium** | 2-3 files, some design decisions | Core + Role Card + Detail Sheet | ~1,500-2,000 |
| **Complex** | 4+ files, architecture decisions, multi-phase | Core + Role Card + Detail Sheet + Examples | ~2,500-3,500 |

**Per-invocation savings**:
- Simple: 2,100 → 800 = **62% reduction**
- Medium: 2,100 → 1,750 = **17% reduction**
- Complex: 2,100 → 2,800 = **slight increase** (but higher quality due to examples)

**Across a full run** (8 invocations, typical mix: 2 simple + 4 medium + 2 complex):
- Current: 8 × 2,100 = 16,800 tokens of instructions
- Target: 500 (core) + 2×800 + 4×1,750 + 2×2,800 = 15,300 tokens
- **Savings: ~9%** on instructions alone

Wait — that's not much. The bigger win is **context deduplication**, which we address in Pillar 2.

### The REAL Win: Context Deduplication

The bigger instruction-level savings comes from **not re-sending project context**:

**Current**: Orchestrator sends ~3,000 tokens of project context verbatim with every delegation (8-10 times per run) = **24,000-30,000 tokens of duplicated context**.

**Target**: Send a 2-line reference instead:

```markdown
## Project Context
Stack: Go 1.22, gin, gorm, postgres. Clean architecture (handler→service→repo).
Conventions: errors.Wrap, unit tests per file, lint: golangci-lint.
Full context: docs/adr/XXX-auth/.sdlc/context.json
```

**Savings: ~3,000 × 8 → ~150 × 8 = 22,800 tokens saved per run.**

Combined with role card compression: **~30% reduction on total run tokens** from Pillar 1 alone.

---

## Pillar 2: Summary-First Artifacts

### Source Pattern: bonsai-memory + claude-cartographer

**bonsai-memory**: Hierarchical file tree with trunk index (~400 tokens boot, 81% reduction).
**claude-cartographer**: Three-tier code database (compact 50 tokens / summary 200 / full compressed): 95% savings.

### Our Adaptation: YAML Frontmatter Summaries

Add a summary block to the top of every generated artifact. Downstream agents read the summary first, fetch full content only when needed.

**Add to every workflow template:**

```yaml
---
# AUTO-GENERATED SUMMARY — do not edit this section manually
summary:
  status: draft | approved
  key_decisions: []
  affected_files: []
  open_issues: []
  quality_score: null
  next_stage: ""
  token_count_full: 0
  token_count_summary: 0
---
```

### Template-by-Template Design

#### REQUIREMENTS.md Template Addition

```yaml
---
summary:
  status: draft
  user_stories: []
  acceptance_criteria_count: 0
  scope_included: []
  scope_deferred: []
  open_questions: []
  assumptions: []
---
```

**Downstream reader**: Architect reads summary first (~200 tokens). If they need specific acceptance criteria, they read the relevant section.

#### PLAN.md Template Addition

```yaml
---
summary:
  chosen_approach: ""
  phases_count: 0
  files_to_create: []
  files_to_modify: []
  feature_flags_needed: false
  risk_level: low | medium | high
  key_design_decisions: []
---
```

**Downstream reader**: Implementor reads summary + phases list (~300 tokens) instead of full plan (~5,000 tokens). Fetches individual phase details as needed.

#### QA_REPORT.md Template Addition

```yaml
---
summary:
  verdict: PASS | FAIL | CONDITIONAL
  tests_run: 0
  tests_passed: 0
  tests_failed: 0
  coverage_pct: 0
  critical_issues: []
  quality_score: 0
  out_of_scope_items: []
---
```

**Downstream reader**: Orchestrator reads summary (~150 tokens) to present to human. No need to read full QA report.

### Concrete Savings Calculation

| Stage | Current (reads full) | Target (reads summary) | Savings |
|---|---|---|---|
| Stage 2 (Architect reads REQUIREMENTS) | 3,000 | 200 | 93% |
| Stage 2 (CTO reads REQUIREMENTS + PLAN) | 3,000 + 5,000 | 200 + 300 | 94% |
| Stage 3 (Implementor reads PLAN) | 5,000 | 300 | 94% |
| Stage 3 (QA reads REQUIREMENTS + PLAN) | 3,000 + 5,000 | 200 + 300 | 94% |
| Stage 4 (PR Reviewer reads REQ+PLAN+QA) | 3,000 + 5,000 + 4,000 | 200 + 300 + 150 | 96% |
| Stage 4 (Tech Writer reads all prior) | 17,000 | 850 | 95% |
| **Per-run cumulative artifact reads** | **~37,000** | **~2,000** | **~95%** |

### Implementation

**Step 1**: Update all 8 workflow templates to include the summary YAML frontmatter.

**Step 2**: Add to each agent's instructions (in role card, not detail sheet):

```markdown
## Reading Artifacts
When reading artifacts produced by prior stages, read ONLY the YAML summary block first.
If you need specific details, read individual sections. NEVER read full artifacts when summary suffices.
```

**Step 3**: The orchestrator's delegation prompt changes from:

```markdown
## Input Artifacts
docs/adr/XXX-auth/REQUIREMENTS.md — requirements for user auth
docs/adr/XXX-auth/PLAN.md — implementation plan
```

To:

```markdown
## Input Artifacts
Read YAML summaries first. Fetch details on demand.
- docs/adr/XXX-auth/REQUIREMENTS.md (summary: 4 user stories, 12 AC, 3 open Qs)
- docs/adr/XXX-auth/PLAN.md (summary: approach B, 4 phases, 8 files to modify)
```

The orchestrator reads the summary (not the full artifact) to populate the delegation prompt. **This alone saves ~3,000-5,000 tokens per delegation.**

---

## Pillar 3: Code Intelligence via Serena MCP (External, No Work For Us)

This is the Serena MCP companion server — already documented in the architecture. No instruction changes needed in our repo beyond the recommendation in /sdlc-doctor.

**Savings**: 97-99% on code exploration (LSP queries vs file reads). But this is Serena's value, not ours.

---

## Pillar 4: Output Compression

### Source Pattern: caveman (verified 65% output reduction)

**Their core prompt** (copy-paste ready):
```
Respond terse like smart caveman. All technical substance stay. Only fluff die.
Drop: articles, filler, pleasantries, hedging.
Fragments OK. Pattern: [thing] [action] [reason]. [next step].
```

**Verified results** (Claude API, 10 dev questions):
- Average output: 1,214 → 294 tokens = **65% reduction**
- Best case (explain bug): 1,180 → 159 = **87% reduction**
- Input compression: 898 → 481 tokens = **46% reduction**

### Our Adaptation: 3 Lines Per Agent

Add to the Core Runtime Contract (already included in the _core.md above):

```markdown
## Output Style
Be terse. Drop filler, hedging, pleasantries. State decisions and data.
Fragments OK. Pattern: [thing] [action] [reason]. [next step].
Code unchanged. Verbose only for security warnings or irreversible actions.
```

**This goes in `_core.md` once, not in every agent file.** All 14 agents inherit it.

### Before/After: Implementor Output

**Before** (typical):
```
Implementation complete. I have successfully implemented all the phases as described 
in the PLAN.md. The implementation includes the following changes:

Files created:
- src/auth/handler.go — This is the HTTP handler for authentication endpoints
- src/auth/service.go — The authentication service layer with JWT token generation
- src/auth/repository.go — Database operations for user management
- tests/auth/handler_test.go — Unit tests for the auth handler

Files modified:
- src/routes.go — Added auth routes to the router

All tests pass. The test suite ran 24 tests with 100% success rate.
No issues were encountered during implementation.
```
(~130 tokens)

**After (caveman)**:
```
Implementation complete. Revision: 1.

Files created: src/auth/{handler,service,repository}.go, tests/auth/handler_test.go
Files modified: src/routes.go (added auth routes)

Tests: 24/24 pass. No issues.
```
(~30 tokens — **77% reduction**)

### Savings Per Run

| Component | Current | Compressed | Savings |
|---|---|---|---|
| Agent output × 8 invocations | ~800 avg × 8 = 6,400 | ~250 avg × 8 = 2,000 | 69% |
| Artifact content (produced) | ~30,000 | ~12,000 | 60% |
| Orchestrator summaries to human | ~5,000 | ~2,000 | 60% |
| **Total output savings** | **~41,400** | **~16,000** | **~61%** |

---

## Pillar 5: RTK for Shell Output (External Tool)

Already documented. Suggested CLI tool, not in our scope.

---

## Combined Savings: What Can We Actually Deliver?

| Pillar | Mechanism | Tokens Saved | Needs MCP? | Effort |
|---|---|---|---|---|
| **1. Two-layer instructions** | Core contract + role cards + context reference | ~25,000 per run | No | 3-4 days |
| **2. Summary-first artifacts** | YAML frontmatter + read-summary-first instructions | ~35,000 per run | No | 1-2 days |
| **4. Output compression** | 3 lines in core contract | ~25,000 per run | No | 1 hour |
| **Context dedup** | Send reference instead of verbatim context | ~23,000 per run | No | 1 day |
| **Total** | | **~108,000 → ~35,000** | | **~6-8 days** |

**Projected run cost: ~110-150K → ~35-55K tokens = ~60-70% reduction**

No MCP server needed. No Serena dependency. Pure instruction changes.

---

## Implementation Priority

### Week 1: Immediate Wins (2 days)

1. **Add output compression to orchestrator** — add 3 caveman lines to `sdlc-orchestrator.agent.md`
2. **Add summary frontmatter to all 8 templates** — update `workflow_templates/*.md`
3. **Change context passing** — orchestrator sends 2-line reference instead of verbatim context

### Week 2: Role Cards (4-5 days)

4. **Create `_core.md`** — extract shared boilerplate from all 14 agents
5. **Create compact role cards** — rewrite each `.agent.md` to ~250-350 tokens
6. **Create `_detail/` sheets** — move expanded protocols to on-demand files
7. **Test with 2-3 real features** — measure actual vs. estimated savings

### Validation

8. **Run 3 features on current system** — export chat.json, count actual tokens per stage
9. **Run 3 features on new system** — compare token counts
10. **Update estimation constants** — calibrate proxy formula with real data

---

## See Also

- **docs/OBSERVABILITY.md** — Observability architecture, TRACE schema, metrics, MCP server design (split from this doc)
- **docs/model-routing.md** — Multi-model routing matrix (to be created, 1 day)
- **mekari-mcp/sdlc/REQUIREMENTS.md** — SDLC MCP server requirements (measurement infrastructure)
- **.research-repos/oh-my-agent/** — Source of two-layer architecture pattern
- **.research-repos/caveman/** — Source of output compression pattern, verified benchmarks

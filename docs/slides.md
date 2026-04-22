---
marp: true
theme: default
paginate: true
backgroundColor: #1a1a2e
color: #eaeaea
style: |
  section {
    font-family: 'Inter', 'Segoe UI', sans-serif;
  }
  h1 {
    color: #00d4aa;
  }
  h2 {
    color: #00d4aa;
  }
  h3 {
    color: #7b68ee;
  }
  strong {
    color: #ff6b6b;
  }
  em {
    color: #ffd93d;
    font-style: normal;
  }
  code {
    background: #16213e;
    color: #00d4aa;
  }
  a {
    color: #4fc3f7;
  }
  table {
    font-size: 0.8em;
  }
  th {
    background: #16213e;
    color: #00d4aa;
  }
  td {
    background: #0f3460;
  }
  blockquote {
    border-left: 4px solid #7b68ee;
    background: #16213e;
    padding: 0.5em 1em;
    font-size: 0.9em;
  }
  section.lead h1 {
    font-size: 2.5em;
  }
  section.invert {
    background: #0f3460;
  }
  .columns {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5em;
  }
  .red { color: #ff6b6b; }
  .green { color: #00d4aa; }
  .yellow { color: #ffd93d; }
---

<!-- _class: lead -->

# Agentic SDLC

### Why spec-anchored, multi-agent workflows beat plan-and-implement

<!--
Opening slide. Set the stage: we all use Copilot's built-in Plan → Implement. 
Let's talk about where it breaks and what we can do about it.
-->

---

# The Status Quo

## Built-in 2-Phase: Plan → Implement

```
User ──► "Plan Agent" ──► Plan ──► "Agent Mode" ──► Code
               ▲                         │
               └─── (maybe) feedback ────┘
```

- Phase 1: Copilot plans what to build
- Phase 2: Copilot implements the plan
- **That's it.** No spec. No QA. No trace.

<!--
This is the default workflow most teams use today.
Two phases, one context window, ship and pray.
-->

---

# Problem #1

## Back-to-Back Planning → Expensive

![bg right:35% fit](https://img.icons8.com/fluency/512/money-bag.png)

- Every "Plan" call uses the **full context window**
- Iterating on the plan = re-sending everything
- Multiple plan revisions = **multiplied token cost**
- No reusable artifact — the plan lives only in chat memory

> *"We're paying premium tokens for a plan nobody can reference later."*

<!--
Token costs add up fast when you iterate on plans in a single conversation.
There's no persistent artifact — it's gone when the chat session ends.
-->

---

# Problem #2

## No Spec Enforcement → No History

![bg right:35% fit](https://img.icons8.com/fluency/512/document.png)

- Plan is a **suggestion in chat**, not a versioned document
- No requirements doc → no acceptance criteria to verify against
- No architecture decision record → *"why was it built this way?"*
- 6 months later: **nobody knows why** a decision was made

> *"The best time to document a decision is when you make it. The second best time doesn't exist in chat history."*

<!--
Chat sessions are ephemeral. Without persistent artifacts,
institutional knowledge evaporates.
-->

---

# Problem #3

## Single Agent → Context Bloat & Pollution

![bg right:35% fit](https://img.icons8.com/fluency/512/brain.png)

- One agent holds **everything**: requirements, architecture, code, tests
- Context window fills up → earlier instructions get **pushed out**
- Agent starts mixing concerns: architecture leaks into code, code into QA
- **No isolation** = no accountability for which "hat" the agent wears

> *"When one agent does everything, nothing gets done well."*

<!--
This is the fundamental scaling problem. A single agent context
can't hold an entire feature's lifecycle without degradation.
-->

---

# Problem #4

## No Verification Loop → Ship and Pray

![bg right:35% fit](https://img.icons8.com/fluency/512/error.png)

- Implementation is **never verified** against the plan
- Drift between what was planned and what was built is **invisible**
- No QA step → bugs discovered in PR review (or production)
- No drift detection → **silent spec violations**

> *"The code compiles. Ship it. What could go wrong?"*

<!--
Without a QA agent checking the implementation against the spec,
drift is the default outcome.
-->

---

<!-- _class: lead -->

# The Agentic SDLC Approach

### Specialized agents. Persistent specs. Human decisions.

---

# Architecture: 10 Specialist Agents

```
User ──► SDLC Orchestrator (coordinator only — never codes)
              │
              ├─ Explorer       → auto-detect project stack
              ├─ PO             → requirements + acceptance criteria
              ├─ Architect      → 2-3 approaches with trade-offs
              ├─ CTO            → validates architecture plan
              ├─ Implementor    → writes code per approved plan
              ├─ QA Lead        → verifies code vs. spec + drift detection
              ├─ Tech Writer    → ADR + PR description
              ├─ PR Reviewer    → classifies & routes PR feedback
              └─ Athena         → continuous improvement meta-agent
```

Each agent runs with **fresh, isolated context**. No pollution.

<!--
This is the core idea: specialist agents with strict boundaries.
The orchestrator coordinates but NEVER does the work itself.
-->

---

# How It Works

```
Phase 1: Planning (interactive)
├── Stage 0: Explorer auto-detects project stack
├── Stage 1: PO suggests requirements ↔ Human decides  ──► REQUIREMENTS.md
├── Stage 2: Architect presents approaches ↔ Human picks
│            └─ CTO validates                           ──► PLAN.md

Phase 2: Implementation (loop)
├── Stage 3: Implementor codes ↔ QA verifies            ──► QA_REPORT.md

Phase 3: PR Review (re-entrant)
├── Stage 4: Tech Writer drafts ADR + PR description
│            └─ PR Reviewer routes feedback to right agent

Phase 4: Post-Merge
└── Stage 5: Tech Writer finalizes ADR                  ──► ADR.md
```

**Every stage has a human review gate.** Agents suggest, humans decide.

---

# Solution #1

## Persistent, Versioned Artifacts

<div class="columns">
<div>

### ❌ Built-in

- Plan lives in chat
- Gone when session ends
- No traceability
- No acceptance criteria

</div>
<div>

### ✅ Agentic SDLC

- `REQUIREMENTS.md` — what & why
- `PLAN.md` — how & where
- `QA_REPORT.md` — verified?
- `ADR.md` — decision history
- `TRACE.jsonl` — full audit log

</div>
</div>

> Every feature produces: **Requirements → Plan → Code → QA Report → ADR**

<!--
Artifacts live in the repo. They're versioned with git.
6 months later, you read the ADR and know exactly what happened.
-->

---

# Solution #2

## Agent Isolation → Clean Context

<div class="columns">
<div>

### ❌ Single Agent

- One agent, one context window
- Requirements + architecture + code + tests + docs
- **Context overflow** on large features
- Role confusion

</div>
<div>

### ✅ Specialist Agents

- Each agent gets **only what it needs**
- PO sees task + project context
- Architect sees requirements + codebase
- Implementor sees plan + project context
- QA sees requirements + plan + code
- **No cross-contamination**

</div>
</div>

> Fresh context per delegation = **better output quality at every stage**

---

# Solution #3

## Built-in QA & Drift Detection

```
Implementor produces code
         │
         ▼
QA Lead verifies against:
  ├── REQUIREMENTS.md  (acceptance criteria)
  ├── PLAN.md          (architectural compliance)
  └── Actual code      (implementation correctness)
         │
         ▼
    ┌─────────┐
    │  PASS?  │──► Yes ──► Continue to PR
    └─────────┘
         │
        No ──► Feedback to Implementor ──► Re-implement ──► Re-verify
                    (max 3 cycles — circuit breaker)
```

**Drift between plan and code is caught before PR review.**

---

# Solution #4

## Humans Decide, Agents Advise

| Stage | What the Agent Does | What the Human Decides |
|-------|--------------------|-----------------------|
| Requirements | Suggests user stories + criteria | Confirms scope, answers questions |
| Architecture | Presents 2-3 approaches + trade-offs | Chooses the approach |
| CTO Review | Validates or flags risks | Approves or sends back |
| Implementation | Writes code per plan | Reviews QA report |
| PR Review | Classifies feedback by type | Accepts/rejects fixes |
| Documentation | Drafts ADR | Confirms merge |

> **No autonomous decisions.** Every stage pauses for human approval.

---

# Solution #5

## Self-Improving Workflow (Athena)

Athena runs in **4 modes:**

1. **Micro-reflections** — after every human "Refine" feedback
2. **Full reports** — after 2+ QA rejections or 5+ micro-reflections
3. **Post-run analysis** — analyzes `TRACE.jsonl` health metrics
4. **Session analysis** — parses exported chat sessions for violations

```json
// docs/athena/reflections.jsonl
{"ts":"2026-04-22T10:00:00Z","agent":"implementor","gap":"missed input validation",
 "suggestion":"Add validation checklist to implementor instructions"}
```

> Athena is **advisory only** — it never edits agent files directly.

<!--
This is the continuous improvement loop. Athena learns from every run
and proposes concrete changes to agent instructions.
-->

---

# Side-by-Side Comparison

| Dimension | Built-in Plan+Implement | Agentic SDLC |
|-----------|------------------------|--------------|
| **Agents** | 1 (does everything) | 10 specialists |
| **Context** | Single, shared window | Isolated per agent |
| **Artifacts** | Chat memory only | Versioned markdown files |
| **Requirements** | Implicit in plan | Explicit REQUIREMENTS.md |
| **QA** | None | Automated verify loop |
| **Drift Detection** | None | QA checks code vs. plan |
| **Decision History** | Lost with chat | ADR in repo |
| **Self-Improvement** | None | Athena meta-agent |
| **Human Control** | Start + end | Every stage gate |
| **Cost Efficiency** | Full context per call | Scoped context per agent |

---

<!-- _class: invert -->

# The Artifact Trail

```
docs/adr/001-auth-module/
├── REQUIREMENTS.md     ← What we're building & why
├── PLAN.md             ← How we're building it
├── QA_REPORT.md        ← Verification results
├── ADR.md              ← Architecture decision record
└── TRACE.jsonl         ← Full execution audit log
```

**6 months from now**, anyone can read these files and understand:
- What was the requirement?
- What approaches were considered?
- Why was this approach chosen?
- Was the implementation verified?
- What trade-offs were accepted?

---

# When to Use What

<div class="columns">
<div>

### Use Built-in Plan+Implement

- Quick prototypes
- Throwaway scripts
- Simple bug fixes
- Solo experiments
- Learning/exploration

</div>
<div>

### Use Agentic SDLC

- Production features
- Team codebases
- Features needing review
- Compliance requirements
- Anything you'll maintain
- Anything needing an audit trail

</div>
</div>

> **Not a replacement** — a complement for when quality and traceability matter.

---

# Getting Started

### Install as a VS Code Copilot Plugin

```
Cmd+Shift+P → "Chat: Install Plugin From Source"
→ https://github.com/roma-mekari/agentic-sdlc
```

### Initialize your workspace

```
@sdlc-orchestrator Use the init-workspace skill to set up this project
```

### Build your first feature

```
@sdlc-orchestrator Build a user authentication module with JWT tokens
```

**Zero config.** Explorer auto-detects your stack. Templates are copied automatically.

---

<!-- _class: lead -->

# Key Takeaway

### The built-in workflow is great for speed.
### The Agentic SDLC is for when **decisions need to survive the chat session.**

<br>

Agents advise. Humans decide. Artifacts persist.

---

<!-- _class: lead -->

# Questions?

<br>

github.com/roma-mekari/agentic-sdlc

<br>

*Agents advise, humans decide.*

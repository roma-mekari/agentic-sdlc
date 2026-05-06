# Observability & MCP Architecture

> **Status**: Architecture Document — split from RESEARCH_TOKEN_EFFICIENCY.md
> **Context**: Agentic SDLC needs observability regardless of token efficiency. This document covers how we measure workflow health, the two-mode architecture (instruction-only vs MCP-integrated), and the SDLC MCP server design.

## Part 3: Observability Architecture

### Two Modes of Operation

The agentic-sdlc repo supports two modes, detected automatically at run start:

| | **Instruction-Only** | **MCP-Integrated** |
|---|---|---|
| **Trace source** | Orchestrator writes TRACE.jsonl via `edit` tool | MCP server writes TRACE via `sdlc_log_*` tools |
| **Artifact management** | Loose files, orchestrator reads them directly | MCP server stores + versions + summarizes |
| **Context passing** | Verbatim in delegation prompt | Subagent calls `sdlc_get_context(view="summary")` |
| **Trace quality** | Best-effort (LLM-maintained) | Deterministic (server-maintained) |
| **Metrics** | Proxy behavioral metrics from TRACE | Exact metrics + behavioral metrics + token counts from MCP |
| **Code intelligence** | File reads (Explorer agent) | LSP queries via Serena (symbol search, references, overview) |
| **Token visibility** | Estimated from proxies | Actual tiktoken counts per artifact/delegation |
| **Memory** | File-based, `/memories/repo/` | Serena memory (cross-run persistence, independent MCP server) |
| **Setup** | Zero config — just the plugin | Requires mekari-mcp `sdlc` provider; Serena MCP recommended alongside |
| **Works on** | Copilot, Claude Code, Cursor, any harness | Any harness with MCP client support |

**Detection**: At run start, orchestrator attempts `sdlc_begin_run`. If available → MCP-integrated mode for the entire run. If the tool is not found → instruction-only mode with direct TRACE.jsonl maintenance. No user configuration needed — progressive enhancement.

### MCP Server: mekari-mcp/sdlc (Standalone, Serena as Companion)

The SDLC MCP server lives in the [mekari-mcp](https://github.com/roma-mekari/agentic-sdlc/.research-repos/mekari-mcp) monorepo as a new provider (`sdlc/`). Full requirements at `mekari-mcp/sdlc/REQUIREMENTS.md`.

**Two independent MCP servers, zero coupling:**

```
Agent Harness (agentic-sdlc)
    │
    │  "Recommended: Serena + SDLC MCP"
    │
    ├──► Serena MCP (independent, unmodified)
    │    Code intelligence: symbol search, references, diagnostics
    │    LSP for 40+ languages, project memory
    │
    └──► SDLC MCP (independent, in mekari-mcp)
         Run lifecycle, stages, gates, artifacts, traces, metrics
         No Serena dependency — follows Serena's architectural patterns
```

**Why two independent servers:**
- Serena and SDLC MCP do different things — code intelligence vs. workflow orchestration
- Zero coupling: no shared imports, no version conflicts, no coordination tax
- Graceful degradation: SDLC MCP works without Serena (agents fall back to file reads)
- Serena works without SDLC MCP (code intelligence is useful standalone)
- Each server has its own lifecycle, config, and deployment

**SDLC MCP tool surface (16 tools):**

| Group | Tools | Purpose |
|-------|-------|---------|
| Run lifecycle | `sdlc_begin_run`, `sdlc_end_run`, `sdlc_get_run_status`, `sdlc_resume_run` | Run state management |
| Stage tracking | `sdlc_begin_stage`, `sdlc_end_stage`, `sdlc_log_delegation`, `sdlc_log_delegation_result`, `sdlc_log_event` | Delegation & stage tracking |
| Human gates | `sdlc_log_gate` | Gate decision logging |
| Artifacts | `sdlc_put_artifact`, `sdlc_get_artifact`, `sdlc_list_artifacts`, `sdlc_get_artifact_diff` | Versioned artifact storage with summaries + tiktoken counts |
| Observability | `sdlc_get_metrics`, `sdlc_get_trace`, `sdlc_get_run_history` | Metrics computation & trace export |
| Context | `sdlc_get_context`, `sdlc_set_context`, `sdlc_get_model_recommendations` | Project context management |

**Serena MCP provides code intelligence (Pillar 3) as a separate server:**

| Serena Tool | What It Replaces | Token Savings |
|---|---|---|
| `find_symbol` | Grep codebase (15K tokens) | 98% |
| `search_for_symbol` | Read full files | 99% |
| `get_diagnostics` | Read + mentally parse | 99% |
| `read_file` (Serena's) | Raw file reads with structure awareness | Varies |

**New capabilities vs. instruction-only mode:**

| Capability | Instruction-Only | MCP-Integrated |
|---|---|---|
| Token counting per artifact | ❌ Not available | ✅ tiktoken in SDLC MCP |
| Code intelligence | ❌ File reads only | ✅ Serena MCP (independent server) |
| Cross-run memory | ❌ File-based, manual | ✅ Serena memory (independent server) |
| Artifact versioning + diff | ❌ Loose files | ✅ SDLC MCP versioned storage |
| Workflow observability | ❌ Proxy only | ✅ SDLC MCP deterministic traces |

### The Fundamental Constraint (Instruction-Only Mode)

In instruction-only mode, agents are instruction sets that guide an LLM inside a host (VS Code Copilot, Claude Code, etc.). The harness has **no runtime, no API instrumentation, and no access to token counters**.

What we **can** observe automatically:
- ✅ Orchestrator's own actions — delegations, gates, violations, stage transitions (via TRACE.jsonl)
- ✅ Artifact production — file sizes, counts, paths (via file system after each stage)
- ✅ Iteration patterns — rejections, refinement cycles, QA loops (via TRACE.jsonl)
- ✅ Delegation compliance — whether the orchestrator followed its role boundary (via TRACE.jsonl violations)

What we **cannot** observe in instruction-only mode:
- ❌ Token counts per request — not exposed to agents by any harness
- ❌ Model used per request — only visible after manual chat.json export
- ❌ Context window state — agents can't see how full their context is
- ❌ Exact per-subagent attribution — subagents run in isolated sessions

**Design decision: chat.json is a debug tool, not an observability pipeline.** It requires manual export from VS Code Copilot. We use it for forensic debugging when something goes wrong, not for routine metrics.

### Approach: Proxy Metrics (Instruction-Only) + Exact Metrics (MCP-Integrated)

In instruction-only mode, we measure **behaviors that correlate with token waste**. In MCP-integrated mode, the MCP server provides exact data for stages, delegations, artifacts, and timing.

### Core Metrics (Available in Both Modes)

| Metric | Instruction-Only (Proxy) | MCP-Integrated (Exact) | What It Measures |
|--------|--------------------------|------------------------|------------------|
| **Stage Iteration Count** | `count(LOOP events)` from TRACE | `sdlc_get_metrics` from server | Rework waste |
| **Delegation Compliance** | `1 - violations/delegations` from TRACE | Same, but deterministic | Orchestrator overreach |
| **Artifact Yield** | File sizes from TRACE + filesystem | `sdlc_get_metrics` with exact sizes | Output efficiency |
| **Gate Efficiency** | `refines/gates` from TRACE | Same, but deterministic | Instruction quality |
| **Artifact Accumulation** | Bytes per stage from file system | `sdlc_list_artifacts` with summaries | Context bloat |
| **QA Rejection Rate** | Rejections from TRACE | Same, but deterministic | Implementation quality |
| **Stage Duration** | ❌ Not available | `sdlc_get_metrics` with timing | Latency tracking |
| **Run Duration** | ❌ Not available | `sdlc_end_run` timestamp diff | Overall throughput |
| **Artifact Version History** | ❌ Not available | `sdlc_get_artifact_diff` | Iteration cost tracking |
| **Token Count per Artifact** | ❌ Not available | `sdlc_list_artifacts` with tiktoken counts | Exact token visibility |
| **Token Count per Delegation** | ❌ Not available | `sdlc_get_metrics` with delegation token totals | Exact token visibility |
| **Summary Savings %** | ❌ Not available | `sdlc_get_metrics` summary_savings_pct | Compression effectiveness |

**Why these proxies work:**
- Rework (iterations, QA rejections, gate refines) is the biggest token waste source. Each iteration re-sends accumulated context. 2 QA rejections roughly doubles Stage 3 token cost.
- Delegation violations mean the orchestrator did work in-context instead of delegating — this is invisible work that bloats the orchestrator's session.
- Artifact accumulation directly measures the cumulative read problem — by Stage 4, reading 5 documents means 5× the artifact bytes in context.
- Gate refine ratio correlates with instruction quality — if agents consistently need 2+ refinements, their instructions need improvement.

### TRACE.jsonl Schema Extension

**In MCP-integrated mode**, TRACE.jsonl is generated by the MCP server — deterministic, complete, no LLM involvement. Call `sdlc_get_trace` to retrieve.

**In instruction-only mode**, TRACE.jsonl is self-reported by the orchestrator (current behavior). The extended schema below improves what the orchestrator logs.

Both modes produce the same TRACE.jsonl format for compatibility with `analyze_session.sh` and `parse-session`:

```json
{"event":"RUN_START","run_id":"2026-04-25-auth","feature_slug":"user-auth","workflow_mode":"full","expected_stages":["0","1","2","3","4a","5","6"]}
{"event":"STAGE_START","run_id":"2026-04-25-auth","stage":"3","iteration":1}
{"event":"DELEGATED","run_id":"2026-04-25-auth","stage":"3","iteration":1,"delegation_id":"d-12","agent":"implementor","input_artifacts":["PLAN.md"],"expected_outputs":["code","tests"]}
{"event":"SUBAGENT_RETURNED","run_id":"2026-04-25-auth","stage":"3","iteration":1,"delegation_id":"d-12","agent":"implementor","outcome":"success","artifact_sizes":{"src/auth.go":2400,"tests/auth_test.go":1800}}
{"event":"HUMAN_GATE","run_id":"2026-04-25-auth","stage":"3","iteration":1,"gate_id":"g-4","decision":"refine","reason_code":"missing-tests","feedback_summary":"..."}
{"event":"LOOP","run_id":"2026-04-25-auth","stage":"3","iteration":2,"reason":"qa_rejected"}
{"event":"RUN_COMPLETE","run_id":"2026-04-25-auth","status":"success","total_stages_completed":7}
```

**New fields vs. current schema:**

| Field | Why | Orchestrator Can Report? |
|-------|-----|:-----------------------:|
| `run_id` | Join key across all events for a single run | ✅ Generated at run start |
| `feature_slug` | Cross-run comparison of similar features | ✅ From user input |
| `workflow_mode` | `full`, `bugfix-fast-track`, `pr-feedback` — needed for fair coverage scoring | ✅ Orchestrator decides |
| `expected_stages` | Enables coverage calculation | ✅ From workflow mode |
| `iteration` | Tracks rework loops within a stage | ✅ Orchestrator counts |
| `delegation_id` | Tracks delegation→return pairs | ✅ Orchestrator generates |
| `gate_id` | Tracks gate decisions across iterations | ✅ Orchestrator generates |
| `reason_code` | Machine-readable reason for refine/reject/loop | ✅ From gate/QA feedback |
| `artifact_sizes` | Enables artifact yield metric | ✅ Orchestrator reads file sizes |
| `input_artifacts` / `expected_outputs` | Tracks what went in and what should come out | ✅ From delegation prompt |

**Key: every new field is self-reported by the orchestrator during the run.** No manual export, no external tooling, no chat.json dependency.

### Efficiency Scoring Formula

Since we use proxy metrics, the formula measures **behavioral waste** rather than token waste:

```text
coverage_factor = completed_required_stages / expected_required_stages

quality_factor = clamp(
    1
    - 0.20 × min(1, violations / 2)
    - 0.15 × min(1, skipped_gates / 2)
    - 0.10 × min(1, extra_qa_cycles / 3)
    - 0.10 × min(1, extra_human_refines_after_stage3 / 3),
    0, 1
)

if final_qa_verdict != "PASS":
    quality_factor = min(quality_factor, 0.25)

waste_ratio =
    0.35 × (total_iterations - total_stages) / total_iterations   // rework ratio
  + 0.25 × violations / max(delegations, 1)                       // delegation slip
  + 0.20 × avg_refine_ratio                                        // gate efficiency (refines/gates)
  + 0.20 × qa_rejection_rate                                       // QA rejection rate

efficiency_score = round(100 × (1 - min(waste_ratio, 1)) × coverage_factor × quality_factor)
```

**Interpretation:**

| Score | Rating | Meaning |
|-------|--------|---------|
| 80–100 | Efficient | Low rework, good delegation, quality maintained |
| 60–79 | Acceptable | Some rework or minor quality issues |
| <60 | Wasteful | Significant rework, delegation failures, or poor quality |
| N/A | Not comparable | Coverage < 1.0 or final QA failed — score shown but labeled |

**Design rationale:**
- Score is about **behavioral waste**, not token counts. A run with 0 rejections, 0 violations, and 1 iteration per stage is efficient regardless of absolute token count.
- Quality is a hard gate — a fast but broken implementation scores low.
- Coverage prevents gaming by skipping stages.
- Proxy metrics are **always available** — no manual export needed.

### Calibration: Estimating Token Costs from Proxies

For teams that want approximate dollar figures, provide a calibration table (derived from empirical observation of 5–10 real runs):

```text
estimated_tokens ≈
    base_tokens_per_stage × stages_completed
  + rework_tokens × (total_iterations - total_stages)
  + context_growth_per_stage × stages_completed²  // cumulative artifact reads
  + gate_tokens × gate_count

Where (calibrated from observed runs):
  base_tokens_per_stage ≈ 25,000     // agent instructions + delegation prompt + output
  rework_tokens         ≈ 35,000     // full context re-sent on iteration
  context_growth        ≈  5,000     // additional artifact bytes read per stage
  gate_tokens           ≈  8,000     // accumulated context re-sent on gate
```

**Important:** These constants are estimates. Calibrate by running 3–5 features, exporting chat.json (manually, for calibration only), and computing actual vs. estimated. Update the constants once, then use proxy-based estimates going forward.

**Example:**
```text
Run: user-auth, full workflow
Stages completed: 7
Iterations: 10 (3 rework cycles in Stage 3)
Gates: 6

Estimated tokens = 25K × 7 + 35K × 3 + 5K × 7² + 8K × 6
                 = 175K + 105K + 245K + 48K
                 = 573K input tokens (rough upper bound)

At Sonnet pricing: ~$1.72 input
```

### Athena Integration

Extend Athena's signal types with efficiency signals:

```json
{
  "signal_type": "WORKFLOW_EFFICIENCY",
  "stage": "3",
  "agent": "implementor",
  "metric": "qa_rejection_rate",
  "value": 0.67,
  "threshold": 0.25,
  "severity": "HIGH",
  "optimization_suggested": "Implementor triggers QA rejection in 67% of runs. Tighten test coverage requirements in Implementor role card."
}
```

Athena should also flag **observability defects** — missing TRACE fields, absent `RUN_START` events — as distinct from workflow defects.

### Observability Gaps

| Gap | Impact | Fix |
|-----|--------|-----|
| No durable `run_id` for cross-event joins | Can't compute per-run metrics | Add `RUN_START` event with `run_id` |
| No iteration tracking within stages | Can't compute rework ratio | Add `iteration` + `LOOP` event |
| No artifact size tracking | Can't compute artifact yield or accumulation rate | Add `artifact_sizes` to `SUBAGENT_RETURNED` |
| No workflow mode declaration | Can't score coverage fairly | Add `workflow_mode` to `RUN_START` |
| No delegation ID | Can't match DELEGATED → SUBAGENT_RETURNED pairs | Add `delegation_id` to both events |
| No gate ID | Can't track refine/reject reasons across iterations | Add `gate_id` + `reason_code` to `HUMAN_GATE` |

### Phase 4.1: Two-Mode Detection — Orchestrator Changes

**Detection mechanism**: At the start of every run, the orchestrator probes for MCP availability:

```
Step 1: Attempt to call sdlc_begin_run with feature_slug and workflow_mode.
Step 2: If the call succeeds → MCP-integrated mode for the entire run.
Step 3: If the tool is not found or errors → instruction-only mode.
        Log the mode decision. Proceed with current behavior.
```

**The mode is determined once at run start and does not change mid-run.**

#### Orchestrator Instruction Changes

The orchestrator `.agent.md` needs these additions/changes:

##### A. New Section: Mode Detection (before Workflow section)

Add a "Mode Detection" section after "Invocation Verification":

```markdown
## Mode Detection

At the start of every run, BEFORE Stage 0, detect which mode to use:

1. Attempt to call `sdlc_begin_run` with:
   - `feature_slug`: derived from the user's task description
   - `workflow_mode`: "full" (default) or "bugfix-fast-track" if bug fix detected
   - `description`: the user's original task description
2. If `sdlc_begin_run` returns a `run_id` → **MCP-integrated mode**
3. If the tool is not available → **Instruction-only mode**

Store the mode as `{mcp_mode: true|false}` for the rest of the run.
Log the mode in TRACE.jsonl: `{"event": "RUN_START", "mode": "mcp-integrated|instruction-only", ...}`

**MCP-integrated mode changes your behavior:**
- Use `sdlc_log_event` instead of writing TRACE.jsonl via `edit`
- Use `sdlc_log_delegation` / `sdlc_log_delegation_result` for delegations
- Use `sdlc_log_gate` for human gates
- Use `sdlc_begin_stage` / `sdlc_end_stage` for stage transitions
- Use `sdlc_get_artifact(name, view="summary")` instead of reading artifact files directly
- Use `sdlc_set_context` after Stage 0, then reference it via `sdlc_get_context(view="summary")`
- At run end, call `sdlc_end_run` with final status

**Instruction-only mode behavior is unchanged from current workflow.**
```

##### B. Trace Protocol Changes (conditional)

In MCP-integrated mode, the trace protocol changes from LLM-maintained to MCP-maintained:

| Event | Instruction-Only (Current) | MCP-Integrated (New) |
|---|---|---|
| RUN_START | Write JSON line to TRACE.jsonl via `edit` | Call `sdlc_begin_run` → server creates trace |
| STAGE_START | Write JSON line to TRACE.jsonl via `edit` | Call `sdlc_begin_stage` |
| DELEGATED | Write JSON line to TRACE.jsonl via `edit` | Call `sdlc_log_delegation` → returns `delegation_id` |
| SUBAGENT_RETURNED | Write JSON line to TRACE.jsonl via `edit` | Call `sdlc_log_delegation_result` |
| HUMAN_GATE | Write JSON line to TRACE.jsonl via `edit` | Call `sdlc_log_gate` → returns `gate_id` |
| STAGE_COMPLETE | Write JSON line to TRACE.jsonl via `edit` | Call `sdlc_end_stage` |
| LOOP / VIOLATION / ATHENA_TRIGGER | Write JSON line to TRACE.jsonl via `edit` | Call `sdlc_log_event` |
| RUN_COMPLETE | Write JSON line to TRACE.jsonl via `edit` | Call `sdlc_end_run` |

**Key change in MCP mode: The orchestrator never writes to TRACE.jsonl directly.** The MCP server maintains it. The orchestrator calls `sdlc_get_trace` if it needs to read past events.

##### C. Role Boundary Update

In MCP-integrated mode, the "ONLY file you may edit" rule changes:

```markdown
**The ONLY file you may edit** is `TRACE.jsonl` (instruction-only mode).
In MCP-integrated mode, you do NOT edit any files — all state goes through MCP tools.
```

##### D. Delegation Protocol Update

In MCP-integrated mode, delegation prompts can reference MCP tools:

```markdown
## Project Context
MCP-integrated mode. Project context available via `sdlc_get_context(view="summary")`.
Input artifacts available via `sdlc_get_artifact(name, view="summary")`.
```

Instead of embedding the full context, pass the MCP tool references. The subagent (if it has MCP access) calls the tools directly. This is the key token savings — context is loaded on-demand, not verbatim.

##### E. Artifact Reading Update

In MCP-integrated mode, replace direct file reads with MCP calls:

```markdown
Instead of: Read docs/adr/XXX-auth/REQUIREMENTS.md to summarize for human
Use: Call sdlc_get_artifact(name="REQUIREMENTS.md", view="summary")
```

This saves ~94% of artifact tokens (summary ~300 tokens vs full ~5000 tokens).

##### F. End-of-Run Changes

In MCP-integrated mode, the orchestrator calls `sdlc_end_run` instead of just writing a final TRACE entry:

```markdown
At run completion:
- MCP-integrated: Call sdlc_end_run(status="completed"). Then call sdlc_get_metrics
  and include the efficiency score in the run summary.
- Instruction-only: Write RUN_COMPLETE to TRACE.jsonl. Include proxy efficiency estimate.
```

## Part 7: Watch Out For

1. **chat.json is debug-only.** Never depend on manual exports for routine observability. TRACE.jsonl is the primary data source because it's automatically maintained by the orchestrator during every run.

2. **Proxy metrics are approximations, not exact.** Behavioral metrics (iterations, violations, rejections) correlate with token waste but don't measure it directly. Calibrate periodically with chat.json exports to keep estimates reasonable.

3. **TRACE is best-effort.** The orchestrator is an LLM maintaining a log. It may miss entries or write imprecise summaries. If TRACE completeness is low (missing stages, gaps), flag it as low confidence rather than inventing numbers.

4. **Human gates are governance, not waste.** Skipping gates reduces quality. Don't overweight gate count in the efficiency score — a run with 6 gates and 0 refines is efficient.

7. **If you need exact per-agent billing or automatic model switching**, an instructions-only harness is no longer sufficient. That requires a custom runtime or separate sessions per stage.

---

## Appendix A: Tool & Integration Reference

| Integration | Purpose | Type | Status |
|------|---------|-----------------|----------|
| **mekari-mcp/sdlc** | SDLC MCP server — 16 tools for run lifecycle, stages, gates, artifacts, observability, context | MCP server in mekari-mcp monorepo | **Planned** (requirements complete) |
| **Serena MCP** | Code intelligence — LSP (40+ languages), symbol search, references, diagnostics, project memory | Independent MCP server (companion to SDLC MCP) | **Recommended** (run alongside SDLC MCP) |

---

See [RESEARCH_TOKEN_EFFICIENCY.md](RESEARCH_TOKEN_EFFICIENCY.md) for the token optimization strategy.
See [mekari-mcp/sdlc/REQUIREMENTS.md](mekari-mcp/sdlc/REQUIREMENTS.md) for the full SDLC MCP requirements.

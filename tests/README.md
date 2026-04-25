# Agentic SDLC Test Harness

Three-layer testing system for verifying agent definitions and behavior.

## Layer 1: Static Validation (Zero cost, runs in CI)

Validates `.agent.md` files for structural correctness without using any LLM.

```bash
# Run all checks (requires uv — https://docs.astral.sh/uv/)
uv run tests/static/validate_agents.py

# Treat warnings as errors
uv run tests/static/validate_agents.py --strict

# Custom paths
uv run tests/static/validate_agents.py --agents-dir ./agents --templates-dir ./workflow_templates
```

**Prerequisites:** [uv](https://docs.astral.sh/uv/) (recommended) or python3 + pyyaml as fallback.

## Layer 2: Behavioral Tests (LLM cost, manual/scheduled trigger)

Uses [promptfoo](https://github.com/promptfoo/promptfoo) to verify agents follow their instructions when invoked against a real LLM.

```bash
# Install promptfoo
npm install -g promptfoo

# Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# Run individual agent tests
promptfoo eval -c tests/behavioral/architect.boundary.yaml
promptfoo eval -c tests/behavioral/cto.boundary.yaml
promptfoo eval -c tests/behavioral/po.boundary.yaml
promptfoo eval -c tests/behavioral/implementor.boundary.yaml
promptfoo eval -c tests/behavioral/qa-lead.boundary.yaml
promptfoo eval -c tests/behavioral/explorer.boundary.yaml
promptfoo eval -c tests/behavioral/orchestrator.workflow.yaml

# Run adversarial red-team tests
promptfoo eval -c tests/behavioral/red-team/role-escape.yaml
```

**What it tests:**
- Role boundary enforcement (agent refuses out-of-scope work)
- Correct output format (verdicts, approaches, structured reports)
- Instruction adherence (follows constraints in .agent.md)
- Adversarial robustness (resists prompt injection)

## Layer 3: Session Analysis (Post-hoc, zero cost)

Analyzes exported VS Code Copilot chat sessions for workflow compliance.

```bash
# Make executable
chmod +x tests/session/analyze_session.sh

# Analyze a session export
./tests/session/analyze_session.sh path/to/chat.json

# With health scoring
./tests/session/analyze_session.sh path/to/chat.json --score

# Verbose (includes thinking trace analysis)
./tests/session/analyze_session.sh path/to/chat.json --score --verbose
```

**Requires:** [jq](https://stedolan.github.io/jq/)

**What it checks:**
- Delegation count (orchestrator should delegate, not do work itself)
- Human review gates (askQuestions calls between stages)
- Edit/execute without delegation (violation signal)
- Overall workflow health score

## CI Integration

Static validation runs automatically on PRs that touch agent/template files:

```yaml
# .github/workflows/test-agents.yaml
# Static validation: every PR
# Behavioral tests: manual trigger only (costs LLM tokens)
```

To run behavioral tests in CI, trigger the workflow with `run_behavioral: true`.

## Git Pre-Push Hook

Static validation runs automatically before `git push` when agent/template files are changed.

```bash
# One-time setup (after cloning):
bash tests/static/setup-hooks.sh

# Bypass for a single push:
git push --no-verify
```

The hook prefers `uv run` (auto-resolves pyyaml via PEP 723 inline metadata) and falls back to `python3` if pyyaml is already installed. It only runs when files in `agents/`, `workflow_templates/`, `skills/`, `.plugin/`, or `tests/static/validate_agents.py` are included in the push.

## Adding Tests for New Agents

1. **Static:** Add expectations to `validate_agents.py`:
   - `STAGE_EXPECTATIONS` — stage number mapping
   - `AGENT_TOOL_RULES` — required/forbidden tools
   - `TEMPLATE_REFS_TO_VALIDATE` — expected template references
   - `USER_INVOCABLE_AGENTS` — if user-invocable

2. **Behavioral:** Create `tests/behavioral/<agent-name>.boundary.yaml`:
   - Define tests for role boundaries, output format, instruction adherence
   - Follow existing test files as templates

3. **Session:** No changes needed — session analysis works generically

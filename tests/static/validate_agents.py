#!/usr/bin/env python3
"""Static validation for Agentic SDLC agent definitions.

Validates .agent.md files for structural correctness, tool declarations,
role boundaries, template references, stage numbers, and cross-agent consistency.

Usage:
    python validate_agents.py [--agents-dir AGENTS_DIR] [--templates-dir TEMPLATES_DIR] [--skills-dir SKILLS_DIR]

Exit codes:
    0 — All checks passed (warnings may exist)
    1 — One or more ERROR-level findings
"""

from __future__ import annotations

import re
import sys
import yaml
import argparse
from dataclasses import dataclass, field
from pathlib import Path

# ── Constants ──────────────────────────────────────────────────────────────────

VALID_TOOLS = {
    "read",
    "edit",
    "search",
    "execute",
    "vscode/askQuestions",
    "todo",
    "web",
    "agent",
}

REQUIRED_FRONTMATTER_FIELDS = {"name", "description", "tools"}

REQUIRED_SECTIONS = {
    "all": ["Role Boundary"],
    "non_explorer": ["Invocation Verification"],
}

TEMPLATE_REFS_TO_VALIDATE = {
    "Architect": [".github/workflow_templates/PLAN.md"],
    "PO": [".github/workflow_templates/REQUIREMENTS.md"],
    "QA Lead": [
        ".github/workflow_templates/QA_REPORT.md",
        ".github/workflow_templates/PLAN.md",
        ".github/workflow_templates/REQUIREMENTS.md",
    ],
    "Tech Writer": [
        ".github/workflow_templates/ADR.md",
        ".github/workflow_templates/FEATURE_SPEC.md",
    ],
    "PR Reviewer": [".github/workflow_templates/PR_FEEDBACK.md"],
    "Athena": [".github/workflow_templates/ATHENA_REPORT.md"],
    "RFC Writer": [".github/workflow_templates/RFC.md"],
}

# Stage number expectations (agent_name -> expected "Stage N" in description)
STAGE_EXPECTATIONS = {
    "PO": "Stage 1",
    "Architect": "Stage 2",
    "CTO": "Stage 2",
    "Implementor": "Stage 3",
    "QA Lead": "Stage 3",
    "Tech Writer": "Stage 4",
    "PR Reviewer": "Stage 4",
}

# Per-agent tool expectations
AGENT_TOOL_RULES = {
    "CTO": {
        "must_have": ["read", "search"],
        "must_not_have": ["edit", "execute"],
        "reason": "CTO is read-only reviewer, should not edit files or run commands",
    },
    "Explorer": {
        "must_have": ["read", "search"],
        "must_not_have": ["edit", "execute"],
        "reason": "Explorer is strictly read-only",
    },
    "PR Reviewer": {
        "must_have": ["read", "search"],
        "must_not_have": ["execute"],
        "reason": "PR Reviewer classifies feedback, does not run commands",
    },
    "Athena": {
        "must_not_have": ["execute"],
        "reason": "Athena is advisory, does not run terminal commands",
    },
    "PRD Analyst": {
        "must_not_have": ["edit", "execute"],
        "reason": "PRD Analyst reviews only, should not write or execute",
    },
    "Estimator": {
        "must_not_have": ["edit", "execute"],
        "reason": "Estimator sizes work, does not implement",
    },
}

# User-invocable expectations
USER_INVOCABLE_AGENTS = {
    "Dev",
    "SDLC Orchestrator",
    "PRD Analyst",
    "RFC Writer",
    "Estimator",
    "Athena",
    "Explorer",
}

# Delegation targets (agents that orchestrator should be able to delegate to)
ORCHESTRATOR_DELEGATION_TARGETS = {
    "Explorer",
    "PO",
    "Architect",
    "CTO",
    "Implementor",
    "QA Lead",
    "Tech Writer",
    "PR Reviewer",
    "Athena",
    "PRD Analyst",
    "RFC Writer",
    "Estimator",
    "Dev",
}


# ── Data classes ───────────────────────────────────────────────────────────────


@dataclass
class Finding:
    severity: str  # ERROR, WARNING, INFO
    agent: str
    check: str
    message: str
    detail: str = ""


@dataclass
class AgentFile:
    path: Path
    name: str  # From frontmatter
    frontmatter: dict
    body: str
    raw_content: str


# ── Parsing ────────────────────────────────────────────────────────────────────

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)


def parse_agent_md(filepath: Path) -> AgentFile | None:
    """Parse frontmatter and body from a .agent.md file."""
    content = filepath.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(content)
    if not match:
        return None

    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None

    if not isinstance(frontmatter, dict):
        return None

    body = content[match.end() :]
    name = frontmatter.get("name", filepath.stem.replace(".agent", ""))

    return AgentFile(
        path=filepath,
        name=str(name),
        frontmatter=frontmatter,
        body=body,
        raw_content=content,
    )


# ── Validation checks ─────────────────────────────────────────────────────────


def validate_frontmatter(agent: AgentFile) -> list[Finding]:
    """Validate required frontmatter fields exist and have correct types."""
    findings = []
    fm = agent.frontmatter

    for field_name in REQUIRED_FRONTMATTER_FIELDS:
        if field_name not in fm:
            findings.append(
                Finding(
                    "ERROR",
                    agent.name,
                    "frontmatter",
                    f"Missing required field: {field_name}",
                )
            )
        elif not fm[field_name]:
            findings.append(
                Finding(
                    "ERROR",
                    agent.name,
                    "frontmatter",
                    f"Empty required field: {field_name}",
                )
            )

    # tools must be a list
    if "tools" in fm and not isinstance(fm["tools"], list):
        findings.append(
            Finding(
                "ERROR",
                agent.name,
                "frontmatter",
                f"'tools' must be a list, got {type(fm['tools']).__name__}",
            )
        )

    # user-invocable must be boolean if present
    if "user-invocable" in fm and not isinstance(fm["user-invocable"], bool):
        findings.append(
            Finding(
                "WARNING",
                agent.name,
                "frontmatter",
                f"'user-invocable' should be boolean, got {type(fm['user-invocable']).__name__}",
            )
        )

    return findings


def validate_tools(agent: AgentFile) -> list[Finding]:
    """Validate tool declarations are valid VS Code tool names."""
    findings = []
    tools = agent.frontmatter.get("tools", [])

    if not isinstance(tools, list):
        return findings

    # Check each tool is a known valid name
    for tool in tools:
        if tool not in VALID_TOOLS:
            findings.append(
                Finding(
                    "ERROR",
                    agent.name,
                    "tools",
                    f"Unknown tool: '{tool}'",
                    f"Valid tools: {sorted(VALID_TOOLS)}",
                )
            )

    # Per-agent tool rules
    rules = AGENT_TOOL_RULES.get(agent.name, {})
    if "must_have" in rules:
        for tool in rules["must_have"]:
            if tool not in tools:
                findings.append(
                    Finding(
                        "ERROR",
                        agent.name,
                        "tools",
                        f"Missing expected tool: '{tool}'",
                        rules.get("reason", ""),
                    )
                )
    if "must_not_have" in rules:
        for tool in rules["must_not_have"]:
            if tool in tools:
                findings.append(
                    Finding(
                        "ERROR",
                        agent.name,
                        "tools",
                        f"Should NOT have tool: '{tool}'",
                        rules.get("reason", ""),
                    )
                )

    return findings


def validate_sections(agent: AgentFile) -> list[Finding]:
    """Validate required sections exist in agent body."""
    findings = []
    body = agent.body

    # All agents must have Role Boundary section
    if "Role Boundary" not in body:
        findings.append(
            Finding("ERROR", agent.name, "sections", "Missing 'Role Boundary' section")
        )

    # Non-explorer agents must have Invocation Verification
    if agent.name != "Explorer":
        if "Invocation Verification" not in body:
            findings.append(
                Finding(
                    "WARNING",
                    agent.name,
                    "sections",
                    "Missing 'Invocation Verification' section (recommended for all non-explorer agents)",
                )
            )

    # Agents with edit/execute tools should have Constraints section
    tools = agent.frontmatter.get("tools", [])
    if ("edit" in tools or "execute" in tools) and "Constraints" not in body:
        findings.append(
            Finding(
                "WARNING",
                agent.name,
                "sections",
                "Agent has edit/execute tools but no 'Constraints' section",
            )
        )

    return findings


def validate_template_refs(agent: AgentFile, templates_dir: Path) -> list[Finding]:
    """Validate references to workflow templates in agent body."""
    findings = []

    if agent.name not in TEMPLATE_REFS_TO_VALIDATE:
        return findings

    for ref in TEMPLATE_REFS_TO_VALIDATE[agent.name]:
        if ref not in agent.body and ref not in agent.raw_content:
            findings.append(
                Finding(
                    "WARNING",
                    agent.name,
                    "template_refs",
                    f"Expected reference to '{ref}' not found in agent body",
                )
            )

        # Check the template file actually exists
        template_path = templates_dir / Path(ref).name
        if not template_path.exists():
            findings.append(
                Finding(
                    "ERROR",
                    agent.name,
                    "template_refs",
                    f"Referenced template does not exist: {template_path}",
                )
            )

    return findings


def validate_stage_numbers(agent: AgentFile) -> list[Finding]:
    """Validate stage numbers mentioned in agent descriptions."""
    findings = []

    if agent.name not in STAGE_EXPECTATIONS:
        return findings

    expected = STAGE_EXPECTATIONS[agent.name]
    description = str(agent.frontmatter.get("description", ""))

    # Find "Stage N" patterns in description
    stage_mentions = re.findall(r"[Ss]tage\s+(\d+)", description)

    if not stage_mentions:
        # No stage mentioned at all — might be intentional, but worth flagging
        return findings

    for mention in stage_mentions:
        actual = f"Stage {mention}"
        if actual != expected:
            findings.append(
                Finding(
                    "ERROR",
                    agent.name,
                    "stage_number",
                    f"Description says '{actual}' but expected '{expected}'",
                    f"Full description: {description[:200]}",
                )
            )

    return findings


def validate_user_invocable(agent: AgentFile) -> list[Finding]:
    """Validate user-invocable flag matches expectations."""
    findings = []
    is_invocable = agent.frontmatter.get("user-invocable", None)

    if is_invocable is None:
        return findings

    if agent.name in USER_INVOCABLE_AGENTS:
        if not is_invocable:
            findings.append(
                Finding(
                    "WARNING",
                    agent.name,
                    "user_invocable",
                    f"Expected user-invocable=true for {agent.name}",
                )
            )
    else:
        if is_invocable:
            findings.append(
                Finding(
                    "WARNING",
                    agent.name,
                    "user_invocable",
                    f"Expected user-invocable=false for {agent.name} (non-user-invocable agent)",
                )
            )

    return findings


def validate_init_workspace_skill(
    agents_dir: Path, templates_dir: Path, skills_dir: Path
) -> list[Finding]:
    """Validate init-workspace skill references all templates."""
    findings = []

    skill_path = skills_dir / "init-workspace" / "SKILL.md"
    if not skill_path.exists():
        findings.append(
            Finding(
                "ERROR", "init-workspace", "skill", "init-workspace SKILL.md not found"
            )
        )
        return findings

    skill_content = skill_path.read_text(encoding="utf-8")

    # Find all template files
    template_files = sorted(templates_dir.glob("*.md"))
    for template in template_files:
        if template.name not in skill_content:
            findings.append(
                Finding(
                    "ERROR",
                    "init-workspace",
                    "skill",
                    f"Template '{template.name}' not listed in init-workspace SKILL.md",
                    f"Template exists at: {template}",
                )
            )

    return findings


def validate_cross_agent(agents: list[AgentFile]) -> list[Finding]:
    """Cross-agent consistency checks."""
    findings = []
    agent_names = {a.name for a in agents}
    agent_map = {a.name: a for a in agents}

    # Check all non-invocable agents are referenced by the orchestrator
    orchestrator = agent_map.get("SDLC Orchestrator")
    if orchestrator:
        for name in ORCHESTRATOR_DELEGATION_TARGETS:
            if name in agent_names and name != "SDLC Orchestrator":
                # Accept both display name ("PRD Analyst") and kebab-case ID ("prd-analyst")
                kebab = name.lower().replace(" ", "-")
                if name not in orchestrator.body and kebab not in orchestrator.body:
                    findings.append(
                        Finding(
                            "WARNING",
                            "SDLC Orchestrator",
                            "cross_agent",
                            f"Orchestrator does not reference agent '{name}'",
                        )
                    )

    # Check for duplicate agent names
    names_seen = {}
    for agent in agents:
        if agent.name in names_seen:
            findings.append(
                Finding(
                    "ERROR",
                    agent.name,
                    "cross_agent",
                    f"Duplicate agent name in {agent.path} and {names_seen[agent.name]}",
                )
            )
        names_seen[agent.name] = agent.path

    # Check all agents have unique file names
    files_seen = {}
    for agent in agents:
        fname = agent.path.name
        if fname in files_seen:
            findings.append(
                Finding(
                    "ERROR",
                    agent.name,
                    "cross_agent",
                    f"Duplicate agent file name: {fname}",
                )
            )
        files_seen[fname] = agent.path

    return findings


# ── Output ─────────────────────────────────────────────────────────────────────


def format_findings(findings: list[Finding]) -> str:
    """Format findings as a readable report."""
    if not findings:
        return "✅ All checks passed."

    lines = []
    errors = [f for f in findings if f.severity == "ERROR"]
    warnings = [f for f in findings if f.severity == "WARNING"]
    infos = [f for f in findings if f.severity == "INFO"]

    lines.append(
        f"❌ {len(errors)} error(s), ⚠️ {len(warnings)} warning(s), ℹ️ {len(infos)} info"
    )
    lines.append("")

    for finding in sorted(
        findings,
        key=lambda f: (
            0 if f.severity == "ERROR" else 1 if f.severity == "WARNING" else 2,
            f.agent,
        ),
    ):
        icon = {"ERROR": "❌", "WARNING": "⚠️", "INFO": "ℹ️"}[finding.severity]
        line = f"{icon} [{finding.agent}] {finding.check}: {finding.message}"
        if finding.detail:
            line += f"\n   {finding.detail}"
        lines.append(line)

    return "\n".join(lines)


# ── Main ───────────────────────────────────────────────────────────────────────


def main():
    repo_root = Path(__file__).resolve().parent.parent.parent
    default_agents = repo_root / "agents"
    default_templates = repo_root / "workflow_templates"
    default_skills = repo_root / "skills"

    parser = argparse.ArgumentParser(
        description="Validate Agentic SDLC agent definitions"
    )
    parser.add_argument(
        "--agents-dir",
        type=Path,
        default=default_agents,
        help="Directory containing .agent.md files",
    )
    parser.add_argument(
        "--templates-dir",
        type=Path,
        default=default_templates,
        help="Directory containing workflow templates",
    )
    parser.add_argument(
        "--skills-dir",
        type=Path,
        default=default_skills,
        help="Directory containing skills",
    )
    parser.add_argument(
        "--strict", action="store_true", help="Treat warnings as errors"
    )
    args = parser.parse_args()

    all_findings: list[Finding] = []

    # Parse all agents
    agent_files = sorted(args.agents_dir.glob("*.agent.md"))
    if not agent_files:
        print(f"❌ No .agent.md files found in {args.agents_dir}")
        sys.exit(1)

    agents: list[AgentFile] = []
    for fp in agent_files:
        agent = parse_agent_md(fp)
        if agent is None:
            all_findings.append(
                Finding(
                    "ERROR", fp.name, "parse", f"Could not parse frontmatter from {fp}"
                )
            )
            continue
        agents.append(agent)

    print(f"Validating {len(agents)} agents from {args.agents_dir}...\n")

    # Per-agent validation
    for agent in agents:
        all_findings.extend(validate_frontmatter(agent))
        all_findings.extend(validate_tools(agent))
        all_findings.extend(validate_sections(agent))
        all_findings.extend(validate_template_refs(agent, args.templates_dir))
        all_findings.extend(validate_stage_numbers(agent))
        all_findings.extend(validate_user_invocable(agent))

    # Cross-agent validation
    all_findings.extend(validate_cross_agent(agents))

    # Skill validation
    all_findings.extend(
        validate_init_workspace_skill(
            args.agents_dir, args.templates_dir, args.skills_dir
        )
    )

    # Output report
    print(format_findings(all_findings))

    # Summary per agent
    print("\n── Per-Agent Summary ──")
    for agent in agents:
        agent_findings = [f for f in all_findings if f.agent == agent.name]
        errors = sum(1 for f in agent_findings if f.severity == "ERROR")
        warnings = sum(1 for f in agent_findings if f.severity == "WARNING")
        status = "✅" if errors == 0 else "❌"
        print(f"  {status} {agent.name}: {errors} error(s), {warnings} warning(s)")

    # Exit code
    has_errors = any(f.severity == "ERROR" for f in all_findings)
    has_warnings = any(f.severity == "WARNING" for f in all_findings)

    if args.strict:
        sys.exit(1 if (has_errors or has_warnings) else 0)
    else:
        sys.exit(1 if has_errors else 0)


if __name__ == "__main__":
    main()

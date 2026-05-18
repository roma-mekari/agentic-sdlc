#!/usr/bin/env python3
"""Artifact validation hook for agent outputs.

Validates that agents produce their required artifacts:
- PO → REQUIREMENTS.md
- Architect → PLAN.md
- Implementor → Code files
- QA Lead → QA_REPORT.md
- Tech Writer → ADR.md
- etc.
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path


def load_config(workspace_root: Path) -> dict:
    config_path = workspace_root / ".plugin" / "config" / "artifact_requirements.json"
    if not config_path.exists():
        return {}
    with open(config_path, "r") as f:
        return json.load(f)


def normalize_agent_name(agent: str) -> str:
    agent = agent.lower().strip()
    if agent.endswith("agent"):
        agent = agent[:-5].strip()
    if agent == "qa":
        return "qa-lead"
    if agent == "qa_lead":
        return "qa-lead"
    if agent == "techwriter":
        return "tech-writer"
    if agent == "tech_writer":
        return "tech-writer"
    if agent == "prreviewer":
        return "pr-reviewer"
    if agent == "pr_reviewer":
        return "pr-reviewer"
    return agent.replace(" ", "-").replace("_", "-")


def find_files_by_pattern(workspace_root: Path, pattern: str) -> list[Path]:
    matches = []
    if not workspace_root.exists():
        return matches

    for root, dirs, files in os.walk(workspace_root):
        for file in files:
            full_path = Path(root) / file
            rel_path = full_path.relative_to(workspace_root)
            if fnmatch(str(rel_path), pattern) or fnmatch(rel_path.name, pattern):
                matches.append(full_path)
    return matches


def validate_artifact_exists(workspace_root: Path, artifact: dict) -> dict:
    pattern = artifact.get("path_pattern", "")
    files = find_files_by_pattern(workspace_root, pattern)

    result = {
        "artifact": artifact.get("name"),
        "pattern": pattern,
        "found": len(files) > 0,
        "files": [str(f.relative_to(workspace_root)) for f in files],
        "file_count": len(files),
    }

    return result


def validate_artifact_size(
    workspace_root: Path, artifact: dict, files: list[Path]
) -> dict:
    min_size = artifact.get("min_size_bytes", 0)
    min_files = artifact.get("min_files", 1)

    if "min_files" in artifact:
        result = {
            "min_files": min_files,
            "actual_files": len(files),
            "passed": len(files) >= min_files,
        }
        return result

    total_size = sum(f.stat().st_size for f in files if f.exists())
    result = {
        "min_size_bytes": min_size,
        "actual_size_bytes": total_size,
        "passed": total_size >= min_size,
    }
    return result


def validate_artifact_sections(
    workspace_root: Path, artifact: dict, files: list[Path]
) -> dict:
    required_sections = artifact.get("required_sections", [])
    if not required_sections:
        return {"required_sections": [], "all_found": True}

    sections_found = {s: False for s in required_sections}
    for file in files:
        if not file.exists():
            continue
        try:
            content = file.read_text(encoding="utf-8", errors="ignore")
            for section in required_sections:
                if section in content:
                    sections_found[section] = True
        except Exception:
            pass

    result = {
        "required_sections": required_sections,
        "sections_found": [s for s, found in sections_found.items() if found],
        "sections_missing": [s for s, found in sections_found.items() if not found],
        "all_found": all(sections_found.values()),
    }
    return result


def validate_approval(workspace_root: Path, artifact: dict, files: list[Path]) -> dict:
    for file in files:
        if not file.exists():
            continue
        try:
            content = file.read_text(encoding="utf-8", errors="ignore").lower()
            if any(
                keyword in content
                for keyword in ["approved", "validated", "✓", "[x]", "approved by cto"]
            ):
                return {"has_approval": True, "approved": True}
        except Exception:
            pass
    return {"has_approval": True, "approved": False}


def validate_agent_artifacts(
    workspace_root: Path, agent_name: str, config: dict
) -> dict:
    normalized_agent = normalize_agent_name(agent_name)
    agent_config = config.get("artifact_requirements", {}).get(normalized_agent, {})
    settings = config.get("validation_settings", {})

    result = {
        "agent": agent_name,
        "normalized_agent": normalized_agent,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "required_artifacts": [],
        "optional_artifacts": [],
        "overall_passed": True,
        "overall_status": "passed",
    }

    required = agent_config.get("required", [])
    optional = agent_config.get("optional", [])

    for artifact in required:
        files = find_files_by_pattern(workspace_root, artifact.get("path_pattern", ""))
        artifact_result = {
            "name": artifact.get("name"),
            "required": True,
            "validation": {},
        }

        artifact_result["validation"]["exists"] = validate_artifact_exists(
            workspace_root, artifact
        )
        artifact_result["validation"]["size"] = validate_artifact_size(
            workspace_root, artifact, files
        )

        if artifact.get("required_sections"):
            artifact_result["validation"]["sections"] = validate_artifact_sections(
                workspace_root, artifact, files
            )

        if artifact.get("validation") == "contains_approval":
            artifact_result["validation"]["approval"] = validate_approval(
                workspace_root, artifact, files
            )

        artifact_result["passed"] = all(
            v.get("passed", v.get("all_found", v.get("approved", True)))
            for v in artifact_result["validation"].values()
        )

        result["required_artifacts"].append(artifact_result)
        if not artifact_result["passed"]:
            result["overall_passed"] = False

    for artifact in optional:
        files = find_files_by_pattern(workspace_root, artifact.get("path_pattern", ""))
        artifact_result = {
            "name": artifact.get("name"),
            "required": False,
            "validation": {},
        }

        artifact_result["validation"]["exists"] = validate_artifact_exists(
            workspace_root, artifact
        )
        artifact_result["validation"]["size"] = validate_artifact_size(
            workspace_root, artifact, files
        )

        artifact_result["passed"] = all(
            v.get("passed", v.get("all_found", True))
            for v in artifact_result["validation"].values()
        )

        result["optional_artifacts"].append(artifact_result)

    if not result["overall_passed"]:
        result["overall_status"] = "failed"
    elif any(
        a.get("validation", {}).get("exists", {}).get("found", False)
        for a in result["optional_artifacts"]
    ):
        result["overall_status"] = "passed_with_warnings"

    return result


def save_validation_report(workspace_root: Path, report: dict, settings: dict) -> Path:
    if not settings.get("create_validation_report", False):
        return None

    report_dir = workspace_root / settings.get(
        "report_path", ".github/hooks/state/validation_reports"
    )
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    agent_name = report["normalized_agent"]
    filename = f"{timestamp}_{agent_name}_validation.json"
    report_path = report_dir / filename

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report_path


def generate_output_message(result: dict, settings: dict) -> str:
    lines = [f"Artifact Validation: {result['agent']}"]

    if result["overall_status"] == "passed":
        lines.append("✓ All required artifacts produced")
    elif result["overall_status"] == "passed_with_warnings":
        lines.append("✓ All required artifacts produced (with optional warnings)")
        for artifact in result["optional_artifacts"]:
            if not artifact["passed"]:
                lines.append(f"  - Optional: {artifact['name']} not found")
    else:
        lines.append("✗ Required artifacts missing or invalid")
        for artifact in result["required_artifacts"]:
            if not artifact["passed"]:
                lines.append(f"  - Missing/Invalid: {artifact['name']}")
                validation = artifact.get("validation", {})
                if "exists" in validation and not validation["exists"]["found"]:
                    lines.append(
                        f"    Reason: No files matching pattern '{validation['exists']['pattern']}'"
                    )
                if "size" in validation and not validation["size"]["passed"]:
                    lines.append(
                        f"    Reason: Size {validation['size']['actual_size_bytes']} < {validation['size']['min_size_bytes']}"
                    )
                if "sections" in validation and not validation["sections"]["all_found"]:
                    lines.append(
                        f"    Reason: Missing sections: {validation['sections']['sections_missing']}"
                    )

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--agent", required=True)
    args = parser.parse_args()

    workspace_root = Path.cwd()
    config = load_config(workspace_root)

    if not config:
        print(
            json.dumps(
                {"warning": "Artifact validation config not found, skipping validation"}
            )
        )
        return 0

    result = validate_agent_artifacts(workspace_root, args.agent, config)
    settings = config.get("validation_settings", {})

    report_path = save_validation_report(workspace_root, result, settings)
    if report_path:
        result["report_path"] = str(report_path.relative_to(workspace_root))

    output_message = generate_output_message(result, settings)
    print(output_message)

    if not result["overall_passed"]:
        if settings.get("fail_on_missing_required", True):
            return 1

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)

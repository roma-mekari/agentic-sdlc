#!/usr/bin/env python3
"""Trace generation dispatcher for VS Code Copilot hooks.

Phase 1 implementation: Hooks write HOOK_* events only.
Orchestrator remains the canonical writer for SDLC semantic events.
"""

import argparse
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from fnmatch import fnmatch
from pathlib import Path


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_stdin_json() -> dict:
    try:
        raw = sys.stdin.read().strip()
        if not raw:
            return {}
        return json.loads(raw)
    except Exception:
        return {}


def get_session_id(payload: dict) -> str:
    return (
        payload.get("sessionId")
        or payload.get("session_id")
        or payload.get("chatSessionId")
        or "unknown-session"
    )


def get_cwd(payload: dict) -> str:
    return payload.get("cwd") or str(Path.cwd())


def load_state(session_id: str, workspace_root: Path) -> dict:
    sessions_dir = workspace_root / ".agentic-sdlc" / "state" / "sessions"
    path = sessions_dir / f"{session_id}.json"
    if path.exists():
        try:
            return json.loads(path.read_text())
        except Exception:
            pass
    return {
        "session_id": session_id,
        "next_hook_seq": 1,
        "active_delegations": {},
        "stage_iteration": {},
        "migration_phase": "phase1",
    }


def ensure_gitignore(workspace_root: Path) -> None:
    gitignore_path = workspace_root / ".agentic-sdlc" / ".gitignore"
    gitignore_path.parent.mkdir(parents=True, exist_ok=True)

    if not gitignore_path.exists():
        gitignore_path.write_text("# Agentic SDLC Plugin State\n*\n")

    root_gitignore = workspace_root / ".gitignore"
    if root_gitignore.exists():
        content = root_gitignore.read_text()
        if ".agentic-sdlc/" not in content:
            with open(root_gitignore, "a") as f:
                f.write("\n# Agentic SDLC Plugin State\n.agentic-sdlc/\n")
    else:
        root_gitignore.write_text("# Agentic SDLC Plugin State\n.agentic-sdlc/\n")


def save_state(state: dict, workspace_root: Path) -> None:
    sessions_dir = workspace_root / ".agentic-sdlc" / "state" / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    path = sessions_dir / f"{state['session_id']}.json"
    path.write_text(json.dumps(state, indent=2, sort_keys=True))


def append_jsonl(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")


def compute_dedupe_key(row: dict) -> str:
    stable = "|".join(
        str(row.get(k, ""))
        for k in ["trace_source", "hook_event", "session_id", "hook_seq", "event"]
    )
    return hashlib.sha1(stable.encode("utf-8")).hexdigest()


def maybe_bind_run(state: dict, payload: dict, workspace_root: Path) -> None:
    if state.get("trace_path"):
        return

    env_trace = os.getenv("AGENTIC_SDLC_TRACE_PATH")
    if env_trace:
        state["trace_path"] = env_trace
        state["run_id"] = os.getenv("AGENTIC_SDLC_RUN_ID")
        state["feature_slug"] = os.getenv("AGENTIC_SDLC_FEATURE_SLUG")
        return

    sessions_dir = workspace_root / ".agentic-sdlc" / "state" / "sessions"
    manifest_path = sessions_dir / f"{state['session_id']}.manifest.json"
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text())
            state["trace_path"] = manifest.get("trace_path")
            state["run_id"] = manifest.get("run_id")
            state["feature_slug"] = manifest.get("feature_slug")
            state["adr_dir"] = manifest.get("adr_dir")
            return
        except Exception:
            pass

    tool_input = payload.get("toolInput") or payload.get("tool_input") or {}
    text = json.dumps(tool_input)
    if "docs/adr/" in text and "TRACE.jsonl" in text:
        pass


def to_rows(
    hook_event: str, payload: dict, state: dict, workspace_root: Path
) -> list[dict]:
    base = {
        "ts": now_iso(),
        "trace_source": "hook",
        "hook_event": hook_event,
        "session_id": state["session_id"],
        "hook_seq": state["next_hook_seq"],
        "run_id": state.get("run_id"),
        "feature_slug": state.get("feature_slug"),
        "stage": state.get("current_stage"),
        "cwd": get_cwd(payload),
    }

    rows = []

    if hook_event == "SessionStart":
        rows.append({**base, "event": "HOOK_SESSION_START"})

    elif hook_event == "UserPromptSubmit":
        text = payload.get("prompt") or payload.get("text") or ""
        rows.append(
            {
                **base,
                "event": "HOOK_USER_PROMPT",
                "prompt_length": len(text),
                "prompt_preview": text[:200] if text else "",
            }
        )

    elif hook_event == "PreToolUse":
        tool_name = payload.get("toolName") or payload.get("tool_name") or "unknown"
        rows.append(
            {
                **base,
                "event": "HOOK_PRE_TOOL_USE",
                "tool_name": tool_name,
                "tool_use_id": payload.get("toolUseId") or payload.get("tool_use_id"),
            }
        )

    elif hook_event == "PostToolUse":
        tool_name = payload.get("toolName") or payload.get("tool_name") or "unknown"
        tool_response = payload.get("toolResponse") or {}
        output_bytes = (
            len(json.dumps(tool_response).encode("utf-8")) if tool_response else 0
        )
        rows.append(
            {
                **base,
                "event": "HOOK_POST_TOOL_USE",
                "tool_name": tool_name,
                "tool_use_id": payload.get("toolUseId") or payload.get("tool_use_id"),
                "output_title": tool_response.get("title"),
                "output_bytes": output_bytes,
            }
        )

    elif hook_event == "PreCompact":
        rows.append({**base, "event": "HOOK_PRE_COMPACT"})

    elif hook_event == "SubagentStart":
        agent = payload.get("agent") or payload.get("subagent") or "unknown"
        subagent_session_id = payload.get("subagentSessionId") or payload.get(
            "subagent_session_id"
        )
        rows.append(
            {
                **base,
                "event": "HOOK_SUBAGENT_START",
                "agent": agent,
                "subagent_session_id": subagent_session_id,
            }
        )

    elif hook_event == "SubagentStop":
        agent = payload.get("agent") or payload.get("subagent") or "unknown"
        subagent_session_id = payload.get("subagentSessionId") or payload.get(
            "subagent_session_id"
        )
        rows.append(
            {
                **base,
                "event": "HOOK_SUBAGENT_STOP",
                "agent": agent,
                "subagent_session_id": subagent_session_id,
                "outcome": payload.get("outcome", "success"),
            }
        )

    elif hook_event == "Stop":
        rows.append(
            {
                **base,
                "event": "HOOK_STOP",
                "stop_reason": payload.get("reason"),
            }
        )

    else:
        rows.append({**base, "event": f"HOOK_{hook_event.upper()}"})

    for row in rows:
        row["dedupe_key"] = compute_dedupe_key(row)

    return rows


def flush_raw_if_bound(state: dict, workspace_root: Path) -> None:
    trace_path = state.get("trace_path")
    if not trace_path:
        return

    raw_dir = workspace_root / ".agentic-sdlc" / "state" / "raw"
    raw_path = raw_dir / f"{state['session_id']}.jsonl"
    if not raw_path.exists():
        return

    trace_file = workspace_root / trace_path
    try:
        lines = raw_path.read_text().splitlines()
        trace_file.parent.mkdir(parents=True, exist_ok=True)
        with trace_file.open("a", encoding="utf-8") as f:
            for line in lines:
                if line.strip():
                    f.write(line + "\n")
        raw_path.unlink()
    except Exception:
        pass


def load_artifact_config(workspace_root: Path) -> dict:
    config_path = workspace_root / ".plugin" / "config" / "artifact_requirements.json"
    if not config_path.exists():
        return {}
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


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


def validate_artifacts(workspace_root: Path, agent_name: str, config: dict) -> dict:
    normalized_agent = normalize_agent_name(agent_name)
    agent_config = config.get("artifact_requirements", {}).get(normalized_agent, {})
    settings = config.get("validation_settings", {})

    result = {
        "agent": agent_name,
        "normalized_agent": normalized_agent,
        "timestamp": now_iso(),
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

        artifact_result["validation"]["exists"] = {
            "found": len(files) > 0,
            "file_count": len(files),
            "files": [str(f.relative_to(workspace_root)) for f in files],
        }

        if "min_size_bytes" in artifact or "min_files" in artifact:
            min_size = artifact.get("min_size_bytes", 0)
            min_files = artifact.get("min_files", 1)

            if "min_files" in artifact:
                total_size = sum(f.stat().st_size for f in files if f.exists())
                artifact_result["validation"]["size"] = {
                    "min_files": min_files,
                    "actual_files": len(files),
                    "passed": len(files) >= min_files,
                }
            else:
                total_size = sum(f.stat().st_size for f in files if f.exists())
                artifact_result["validation"]["size"] = {
                    "min_size_bytes": min_size,
                    "actual_size_bytes": total_size,
                    "passed": total_size >= min_size,
                }

        if artifact.get("required_sections"):
            required_sections = artifact.get("required_sections", [])
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

            artifact_result["validation"]["sections"] = {
                "required_sections": required_sections,
                "sections_found": [s for s, found in sections_found.items() if found],
                "sections_missing": [
                    s for s, found in sections_found.items() if not found
                ],
                "all_found": all(sections_found.values()),
            }

        if artifact.get("validation") == "contains_approval":
            approved = False
            for file in files:
                if not file.exists():
                    continue
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore").lower()
                    if any(
                        keyword in content
                        for keyword in [
                            "approved",
                            "validated",
                            "✓",
                            "[x]",
                            "approved by cto",
                        ]
                    ):
                        approved = True
                        break
                except Exception:
                    pass
            artifact_result["validation"]["approval"] = {
                "has_approval": True,
                "approved": approved,
            }

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

        artifact_result["validation"]["exists"] = {
            "found": len(files) > 0,
            "file_count": len(files),
            "files": [str(f.relative_to(workspace_root)) for f in files],
        }

        if "min_size_bytes" in artifact or "min_files" in artifact:
            min_size = artifact.get("min_size_bytes", 0)
            min_files = artifact.get("min_files", 0)

            if min_files > 0:
                artifact_result["validation"]["size"] = {
                    "min_files": min_files,
                    "actual_files": len(files),
                    "passed": len(files) >= min_files,
                }
            else:
                total_size = sum(f.stat().st_size for f in files if f.exists())
                artifact_result["validation"]["size"] = {
                    "min_size_bytes": min_size,
                    "actual_size_bytes": total_size,
                    "passed": total_size >= min_size,
                }

        artifact_result["passed"] = all(
            v.get("passed", True) for v in artifact_result["validation"].values()
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
        "report_path", ".agentic-sdlc/state/validation_reports"
    )
    report_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    agent_name = report["normalized_agent"]
    filename = f"{timestamp}_{agent_name}_validation.json"
    report_path = report_dir / filename

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    return report_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hook-event", required=True)
    args = parser.parse_args()

    payload = load_stdin_json()
    workspace_root = Path.cwd()

    ensure_gitignore(workspace_root)

    session_id = get_session_id(payload)
    state = load_state(session_id, workspace_root)

    maybe_bind_run(state, payload, workspace_root)

    rows = to_rows(args.hook_event, payload, state, workspace_root)

    if state.get("trace_path"):
        target = workspace_root / state["trace_path"]
    else:
        raw_dir = workspace_root / ".agentic-sdlc" / "state" / "raw"
        target = raw_dir / f"{session_id}.jsonl"

    for row in rows:
        append_jsonl(target, row)

    artifact_config = load_artifact_config(workspace_root)
    settings = artifact_config.get("validation_settings", {})

    if args.hook_event == "SubagentStop" and artifact_config:
        agent = payload.get("agent") or payload.get("subagent") or "unknown"
        validation_result = validate_artifacts(workspace_root, agent, artifact_config)

        validation_report_path = save_validation_report(
            workspace_root, validation_result, settings
        )

        validation_row = {
            "ts": now_iso(),
            "trace_source": "hook",
            "hook_event": "SubagentStop",
            "event": "ARTIFACT_VALIDATION",
            "session_id": session_id,
            "hook_seq": state["next_hook_seq"],
            "agent": agent,
            "validation_status": validation_result["overall_status"],
            "validation_passed": validation_result["overall_passed"],
            "required_artifacts_count": len(validation_result["required_artifacts"]),
            "required_passed": sum(
                1 for a in validation_result["required_artifacts"] if a["passed"]
            ),
            "optional_artifacts_count": len(validation_result["optional_artifacts"]),
            "optional_passed": sum(
                1 for a in validation_result["optional_artifacts"] if a["passed"]
            ),
            "report_path": str(validation_report_path.relative_to(workspace_root))
            if validation_report_path
            else None,
            "run_id": state.get("run_id"),
            "feature_slug": state.get("feature_slug"),
            "stage": state.get("current_stage"),
            "cwd": get_cwd(payload),
            "dedupe_key": compute_dedupe_key(
                {
                    "trace_source": "hook",
                    "hook_event": "SubagentStop",
                    "session_id": session_id,
                    "hook_seq": state["next_hook_seq"],
                    "event": "ARTIFACT_VALIDATION",
                }
            ),
        }

        append_jsonl(target, validation_row)
        state["next_hook_seq"] += 1

        if not validation_result["overall_passed"]:
            if settings.get("fail_on_missing_required", True):
                print(
                    f"Artifact validation failed for {agent}. "
                    f"See {validation_report_path} for details."
                )

    state["next_hook_seq"] += 1
    save_state(state, workspace_root)
    flush_raw_if_bound(state, workspace_root)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        sys.exit(0)

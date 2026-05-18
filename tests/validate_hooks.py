#!/usr/bin/env python3
"""Validation script for trace generation hooks.

Validates:
- Python script syntax
- JSON configuration structure
- File permissions
- Required dependencies
"""

import json
import os
import sys
from pathlib import Path


def check_python_syntax(script_path: Path) -> bool:
    try:
        import py_compile

        py_compile.compile(str(script_path), doraise=True)
        print(f"✓ {script_path.name}: Valid Python syntax")
        return True
    except Exception as e:
        print(f"✗ {script_path.name}: Syntax error - {e}")
        return False


def check_json_syntax(json_path: Path) -> bool:
    try:
        with open(json_path, "r") as f:
            json.load(f)
        print(f"✓ {json_path.name}: Valid JSON")
        return True
    except Exception as e:
        print(f"✗ {json_path.name}: Invalid JSON - {e}")
        return False


def check_hook_config(hooks_json: Path) -> bool:
    try:
        with open(hooks_json, "r") as f:
            config = json.load(f)

        required_hooks = [
            "SessionStart",
            "UserPromptSubmit",
            "PreToolUse",
            "PostToolUse",
            "PreCompact",
            "SubagentStart",
            "SubagentStop",
            "Stop",
        ]

        hooks = config.get("hooks", {})
        missing = [h for h in required_hooks if h not in hooks]

        if missing:
            print(f"✗ {hooks_json.name}: Missing hooks: {', '.join(missing)}")
            return False

        for hook_name, hook_configs in hooks.items():
            if not hook_configs:
                print(f"✗ {hooks_json.name}: Empty config for {hook_name}")
                return False

            for cfg in hook_configs:
                if cfg.get("type") != "command":
                    print(f"✗ {hooks_json.name}: {hook_name} has non-command type")
                    return False

                command = cfg.get("command", "")
                if "trace_hook.sh" not in command:
                    print(
                        f"✗ {hooks_json.name}: {hook_name} command doesn't call trace_hook.sh"
                    )
                    return False

        print(f"✓ {hooks_json.name}: All 8 hooks configured correctly")
        return True
    except Exception as e:
        print(f"✗ {hooks_json.name}: Config validation failed - {e}")
        return False


def check_plugin_manifest(manifest_path: Path) -> bool:
    try:
        with open(manifest_path, "r") as f:
            config = json.load(f)

        if "hooks" not in config:
            print(f"✗ {manifest_path.name}: Missing 'hooks' field")
            return False

        hooks_config = config["hooks"]
        if hooks_config != "hooks.json":
            print(
                f"✗ {manifest_path.name}: hooks field should be 'hooks.json', got '{hooks_config}'"
            )
            return False

        if not (manifest_path.parent / hooks_config).exists():
            print(f"✗ {manifest_path.name}: Referenced hooks.json doesn't exist")
            return False

        print(f"✓ {manifest_path.name}: Correctly registers hooks.json")
        return True
    except Exception as e:
        print(f"✗ {manifest_path.name}: Manifest validation failed - {e}")
        return False


def check_file_permissions(script_path: Path) -> bool:
    if not script_path.exists():
        print(f"✗ {script_path.name}: File not found")
        return False

    if os.name == "posix":
        if not os.access(script_path, os.X_OK):
            print(f"✗ {script_path.name}: Not executable (run: chmod +x {script_path})")
            return False

    print(f"✓ {script_path.name}: Correct permissions")
    return True


def check_dependencies() -> bool:
    try:
        import sys

        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            print(
                f"✗ Python: Requires 3.8+, found {version.major}.{version.minor}.{version.micro}"
            )
            return False
        print(f"✓ Python: {version.major}.{version.minor}.{version.micro}")
        return True
    except Exception as e:
        print(f"✗ Python check failed: {e}")
        return False


def check_state_directory_structure() -> bool:
    # In plugin repo, we don't have .agentic-sdlc/ directory
    # It's created at runtime in user's workspace
    # So we just verify the plugin doesn't have it
    if Path(".agentic-sdlc").exists():
        print(
            f"✗ .agentic-sdlc/ should not exist in plugin repo (only in user workspace)"
        )
        return False

    print(f"✓ State directory structure correct (no .agentic-sdlc/ in plugin repo)")
    return True


def main() -> int:
    print("Validating Agentic SDLC Trace Hooks\n")
    print("=" * 50)

    plugin_root = Path(".plugin")
    if not plugin_root.exists():
        plugin_root = Path.cwd()

    checks = [
        (
            "Python syntax",
            lambda: check_python_syntax(plugin_root / "scripts/trace_hook.py"),
        ),
        ("Hooks JSON", lambda: check_json_syntax(plugin_root / "hooks.json")),
        ("Hook configuration", lambda: check_hook_config(plugin_root / "hooks.json")),
        ("Plugin manifest", lambda: check_plugin_manifest(plugin_root / "plugin.json")),
        (
            "Script permissions",
            lambda: check_file_permissions(plugin_root / "scripts/trace_hook.sh"),
        ),
        ("Python version", check_dependencies),
        ("State directory", check_state_directory_structure),
    ]

    results = []
    for name, check_fn in checks:
        print(f"\n{name}:")
        results.append(check_fn())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"\nValidation: {passed}/{total} checks passed")

    if all(results):
        print("\n✓ All validations passed! Hooks are ready for testing.")
        return 0
    else:
        print("\n✗ Some validations failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

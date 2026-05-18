# Artifact Validation System

Automatically validates that SDLC agents produce their required artifacts.

## Overview

When an agent completes (SubagentStop hook), the artifact validation system checks:
- **PO Agent**: Produced REQUIREMENTS.md with required sections
- **Architect Agent**: Produced PLAN.md with required sections
- **Implementor Agent**: Produced code files (minimum count/size)
- **QA Lead Agent**: Produced QA_REPORT.md with required sections
- **Tech Writer Agent**: Produced ADR.md with required sections
- **CTO Agent**: Approved PLAN.md (contains approval marker)
- **PR Reviewer Agent**: Produced PR feedback document

## Configuration

**File**: `.plugin/config/artifact_requirements.json`

### Agent → Artifact Mapping

```json
{
  "artifact_requirements": {
    "po": {
      "required": [
        {
          "name": "REQUIREMENTS.md",
          "path_pattern": "docs/adr/*/REQUIREMENTS.md",
          "min_size_bytes": 100,
          "required_sections": ["## Requirements", "## User Stories", "## Acceptance Criteria"]
        }
      ]
    },
    "architect": {
      "required": [
        {
          "name": "PLAN.md",
          "path_pattern": "docs/adr/*/PLAN.md",
          "min_size_bytes": 100,
          "required_sections": ["## Design Approach", "## Trade-offs", "## Implementation Plan"]
        }
      ]
    }
  }
}
```

### Validation Settings

```json
{
  "validation_settings": {
    "fail_on_missing_required": true,
    "fail_on_invalid_content": true,
    "fail_on_missing_sections": true,
    "warn_on_missing_optional": true,
    "create_validation_report": true,
    "report_path": ".agentic-sdlc/state/validation_reports"
  }
}
```

## Validation Criteria

### 1. File Existence
Checks if files matching the `path_pattern` exist in the workspace.

### 2. File Size
Validates:
- `min_size_bytes`: Minimum file size in bytes
- `min_files`: Minimum number of files matching pattern

### 3. Required Sections
For markdown files, checks if required sections exist:
- Example: `["## Requirements", "## User Stories"]`
- Uses substring matching (case-insensitive)

### 4. Approval Markers
For approval-based artifacts (e.g., CTO approval of PLAN.md):
- Searches for keywords: "approved", "validated", "✓", "[x]", "approved by cto"
- Case-insensitive matching

## Validation Report

**Location**: `.agentic-sdlc/state/validation_reports/`

**Filename**: `YYYYMMDD_HHMMSS_<agent>_validation.json`

**Format**:
```json
{
  "agent": "PO",
  "normalized_agent": "po",
  "timestamp": "2026-04-30T12:00:00.000Z",
  "required_artifacts": [
    {
      "name": "REQUIREMENTS.md",
      "required": true,
      "passed": true,
      "validation": {
        "exists": {
          "found": true,
          "file_count": 1,
          "files": ["docs/adr/001-auth/REQUIREMENTS.md"]
        },
        "size": {
          "min_size_bytes": 100,
          "actual_size_bytes": 2048,
          "passed": true
        },
        "sections": {
          "required_sections": ["## Requirements", "## User Stories", "## Acceptance Criteria"],
          "sections_found": ["## Requirements", "## User Stories", "## Acceptance Criteria"],
          "sections_missing": [],
          "all_found": true
        }
      }
    }
  ],
  "optional_artifacts": [],
  "overall_passed": true,
  "overall_status": "passed"
}
```

## Trace Event

Validation results are logged to TRACE.jsonl:

```json
{
  "ts": "2026-04-30T12:00:00.000Z",
  "event": "ARTIFACT_VALIDATION",
  "trace_source": "hook",
  "hook_event": "SubagentStop",
  "session_id": "sess_abc123",
  "hook_seq": 15,
  "agent": "PO",
  "validation_status": "passed",
  "validation_passed": true,
  "required_artifacts_count": 1,
  "required_passed": 1,
  "optional_artifacts_count": 0,
  "optional_passed": 0,
  "report_path": ".agentic-sdlc/state/validation_reports/20260430_120000_po_validation.json",
  "run_id": "2026-04-30-user-auth",
  "feature_slug": "user-auth",
  "stage": "1"
}
```

## Validation Status

| Status | Meaning | Behavior |
|--------|---------|----------|
| `passed` | All required artifacts valid | No action |
| `passed_with_warnings` | All required valid, some optional missing | Warning logged |
| `failed` | Required artifacts missing or invalid | Fails hook (blocks agent completion if enabled) |

## Supported Agents

| Agent | Required Artifacts | Optional Artifacts |
|-------|-------------------|-------------------|
| **PO** | REQUIREMENTS.md | - |
| **Architect** | PLAN.md | - |
| **CTO** | PLAN.md (approval) | - |
| **Implementor** | Code files (min 1) | Tests (optional) |
| **QA Lead** | QA_REPORT.md | - |
| **Tech Writer** | ADR.md | PR Description, Feature Spec |
| **PR Reviewer** | PR Feedback (PR_FEEDBACK.md) | - |
| **Athena** | - | Athena Report |
| **Explorer** | - | - |

## Agent Name Normalization

The system normalizes various agent name formats:

| Input | Normalized |
|-------|-----------|
| PO | po |
| po | po |
| PO Agent | po |
| po-agent | po |
| QA | qa-lead |
| qa_lead | qa-lead |
| TechWriter | tech-writer |
| tech_writer | tech-writer |
| PR Reviewer | pr-reviewer |
| pr_reviewer | pr-reviewer |

## Configuration Examples

### Strict Validation

```json
{
  "validation_settings": {
    "fail_on_missing_required": true,
    "fail_on_invalid_content": true,
    "fail_on_missing_sections": true,
    "warn_on_missing_optional": false
  }
}
```

### Lenient Validation

```json
{
  "validation_settings": {
    "fail_on_missing_required": false,
    "fail_on_invalid_content": false,
    "fail_on_missing_sections": false,
    "warn_on_missing_optional": true
  }
}
```

### Custom Artifact Pattern

```json
{
  "artifact_requirements": {
    "implementor": {
      "required": [
        {
          "name": "TypeScript Code",
          "path_pattern": "src/**/*.ts",
          "min_files": 2,
          "min_total_size_bytes": 500
        }
      ]
    }
  }
}
```

## Testing

### Manual Test

```bash
# Test validation for a specific agent
cd /path/to/workspace
python3 .plugin/scripts/validate_artifacts.py --agent "PO"
```

### Verify Validation Report

```bash
# Check latest validation reports
ls -lt .agentic-sdlc/state/validation_reports/

# View specific report
cat .agentic-sdlc/state/validation_reports/20260430_120000_po_validation.json | jq
```

### Check Trace Event

```bash
# Find validation events in TRACE.jsonl
grep "ARTIFACT_VALIDATION" docs/adr/*/TRACE.jsonl | jq
```

## Troubleshooting

### Validation Always Passes

**Issue**: Validation reports `passed` even when artifacts are missing

**Causes**:
1. Agent name not matching configuration (check normalization)
2. `path_pattern` not matching actual file location
3. `min_size_bytes` set too low

**Solutions**:
1. Check agent name in validation report: `"normalized_agent"`
2. Verify file paths: `ls -la docs/adr/*/`
3. Increase `min_size_bytes` if artifacts are small

### Validation Always Fails

**Issue**: Validation reports `failed` even when artifacts exist

**Causes**:
1. Missing required sections in markdown files
2. File size below minimum threshold
3. Pattern not matching due to path differences

**Solutions**:
1. Check validation report for specific failure reason
2. Verify artifact content has required sections
3. Adjust `path_pattern` to match actual file locations
4. Lower `min_size_bytes` if threshold is too high

### Validation Not Running

**Issue**: No ARTIFACT_VALIDATION events in TRACE.jsonl

**Causes**:
1. Artifact config file missing
2. Validation disabled in settings
3. SubagentStop hook not firing

**Solutions**:
1. Verify `.plugin/config/artifact_requirements.json` exists
2. Check `validation_settings.create_validation_report` is `true`
3. Verify hooks are registered in `.plugin/hooks.json`
4. Check VS Code Output panel for hook errors

### Agent Name Not Recognized

**Issue**: Agent appears as "unknown" in validation report

**Causes**:
1. Agent name not in configuration
2. Agent name format not supported

**Solutions**:
1. Add agent to `artifact_requirements` in config
2. Check agent name in hook payload: `payload.get("agent")`

## Performance

- Validation time: < 500ms for typical workspace
- File system walks: cached per validation run
- Report generation: < 50ms
- Trace logging: < 10ms

## Security

- Only reads workspace files
- No external network calls
- No execution of untrusted code
- Validation reports stored locally

## Integration with Hooks

Artifact validation is automatically triggered on `SubagentStop` events:

1. Agent completes execution
2. SubagentStop hook fires
3. Trace hook logs HOOK_SUBAGENT_STOP event
4. Artifact validation runs automatically
5. ARTIFACT_VALIDATION event logged to TRACE.jsonl
6. Validation report saved to disk
7. If validation fails, hook may block (depending on settings)

## Customization

### Adding New Agent Artifacts

Edit `.plugin/config/artifact_requirements.json`:

```json
{
  "artifact_requirements": {
    "my-custom-agent": {
      "required": [
        {
          "name": "Custom Artifact",
          "path_pattern": "custom/**/*.md",
          "min_size_bytes": 50,
          "required_sections": ["## Section 1", "## Section 2"]
        }
      ]
    }
  }
}
```

### Adding Custom Validation Rules

Extend `validate_artifacts()` in `trace_hook.py` to add:
- Content validation (e.g., check for specific patterns)
- Structural validation (e.g., JSON schema validation)
- Quality checks (e.g., code linting results)

## Related Documentation

- [Trace Hook Migration Strategy](../../docs/TRACE_HOOK_MIGRATION.md)
- [Plugin Hooks README](../.plugin/README.md)
- [Manual Testing Guide](../../tests/MANUAL_TESTING_GUIDE.md)

---
name: contextual-commit
description: >
  Smart git commit that groups related changes contextually, stages only relevant files,
  runs tests, and never commits unrelated/untracked files. Produces atomic, well-described commits.
  Use when user asks to commit, save changes, or make a commit. Triggers: 'commit', 'commit these changes',
  'make a commit', 'save and commit', 'stage and commit'.
---

# Contextual Commit — Smart Git Commit Workflow

Never `git add .` or `git commit -a`. Every commit is atomic, tested, and contains only related changes.

## Workflow

### Step 1: Assess Current State

Run in parallel:
```bash
git status --porcelain
git diff --stat HEAD
git log --oneline -5
```

Identify:
- **Staged changes** (already in index)
- **Unstaged changes** (modified but not staged)
- **Untracked files** (new, not tracked)

### Step 2: Classify Changes

Group files by logical concern. Common patterns:

| Pattern | Example |
|---------|---------|
| Feature implementation | New agent + its detail sheet + template changes |
| Bug fix | Single file or small set of related files |
| Refactor | Files across same module with structural changes |
| Documentation | Only docs/ or *.md files |
| Test updates | Only test files |
| Config | Config files only |

**Never group unrelated changes** — if agent files AND research docs changed, those are separate commits.

**Untracked files are SUSPECT** — never `git add` untracked files without explicit confirmation. They might be:
- Temporary build artifacts
- Research materials
- Scratch files
- Files the user doesn't want tracked

### Step 3: Run Tests FIRST

**Before staging anything**, verify the project isn't broken.

#### Discovery — find the test command for THIS repo

Do NOT assume a test framework. Discover it:

```bash
# 1. Check package.json scripts
cat package.json 2>/dev/null | grep -A5 '"scripts"'

# 2. Check Makefile targets
grep -E '^[a-z].*test' Makefile 2>/dev/null

# 3. Check CI config for how tests run in automation
cat .github/workflows/*.yaml 2>/dev/null | grep -B2 -A5 'test\|check\|validate'

# 4. Check pre-commit/pre-push hooks (shows what the repo already validates)
cat .githooks/pre-push 2>/dev/null
cat .git/hooks/pre-push 2>/dev/null

# 5. Probe for common test runners
ls pytest.ini setup.cfg pyproject.toml tox.ini 2>/dev/null   # Python/pytest
ls go.mod 2>/dev/null                                          # Go
ls Cargo.toml 2>/dev/null                                      # Rust
ls pom.xml build.gradle 2>/dev/null                            # Java
ls Makefile justfile 2>/dev/null                               # Task runners
```

Use the **CI config as source of truth** — if `.github/workflows/*.yaml` shows how tests run, use that exact command. CI is the canonical test definition.

If multiple test commands exist (e.g., lint + unit tests + integration), run the fastest one that covers the changed files. Full suites can be deferred to CI.

**If tests fail**: STOP. Report failures. Do NOT commit broken code.
**If no tests found**: Proceed but note it in commit message body.

### Step 4: Stage Only Related Files

Stage files by logical group. Be precise:

```bash
# Good: specific files by logical group
git add src/auth/handler.go src/auth/handler_test.go

# Bad: everything
git add .                          # NEVER
git commit -a                      # NEVER
git add -A                         # NEVER
```

**After staging**, verify with `git status` that ONLY the intended files are staged.

### Step 5: Write Commit Message

Follow repository convention (check `git log --oneline -10`).

**Format** (conventional commits):
```
<type>(<scope>): <short description>

<optional body explaining why, not what>

<optional footer>
```

**Types**: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `perf`, `style`

**Rules**:
- Subject ≤ 72 chars
- Subject uses imperative mood ("add" not "added")
- Body explains WHY, not WHAT (what is visible in diff)
- Reference issue/PR numbers if applicable
- Note test results in body if applicable

### Step 6: Commit and Verify

```bash
git commit -m "..."
git status   # Verify clean state
git log --oneline -3  # Verify commit landed
```

### Step 7: Generate PR Description (If Branch Diverged from Base)

After committing, check if the branch has diverged from its base branch:

```bash
# Find the base branch
git remote show origin 2>/dev/null | grep 'HEAD branch'
git log --oneline main..HEAD 2>/dev/null || git log --oneline master..HEAD 2>/dev/null
```

If there are commits on this branch not in the base, generate a PR description the human can copy-paste. Gather context:

```bash
# Full diff of everything on this branch vs base
git diff main...HEAD --stat
git log main..HEAD --oneline
```

**PR description format:**

```markdown
## What this PR does
[1-2 paragraphs summarizing the purpose and approach. Written for a reviewer
who has zero context. Derived from commit messages + diff analysis.]

## Key changes
| Area | Files | What changed |
|------|-------|-------------|
| [Layer/Module] | `path/to/file` | [Brief description] |

## How to review
[Suggested review order — files to read first for context, then details.
E.g., "Start with agents/_core.md for the shared contract, then check
individual role cards for agent-specific changes."]

## Test results
- **Static validation:** [0 errors, N warnings / skipped — no tests found]
- **Test suite:** [N passed, M failed / skipped]

## Checklist
- [ ] Changes are atomic and related to a single concern
- [ ] No secrets or credentials included
- [ ] Tests pass (or pre-existing failures noted)
```

**Rules:**
- Generate from the **branch diff**, not just the last commit — PRs often contain multiple commits
- Keep "What this PR does" concise — reviewers scan this first
- "How to review" should suggest a reading order, not just list files
- Include test results from Step 3
- If the branch has only 1 commit, the PR description can be shorter (skip the table if trivial)

## Safety Rules

1. **NEVER** `git add .` / `git add -A` / `git commit -a`
2. **NEVER** commit files with secrets (.env, credentials, API keys)
3. **NEVER** commit without running tests first (if they exist)
4. **NEVER** push unless user explicitly asks
5. **NEVER** use `--no-verify` or `--force`
6. **ALWAYS** verify staged files match intent before committing
7. **ALWAYS** leave unrelated untracked files alone
8. **ALWAYS** check git log for commit style conventions

## Edge Cases

### Mixed changes (feature + docs + unrelated)

Split into multiple commits:
```
Commit 1: feat: add new agent
Commit 2: docs: update README with new agent
(skipped: .research-repos/ is unrelated)
```

### User says "commit all"

Interpret as "commit all related changes" not `git add .`:
1. Classify all changes into logical groups
2. Ask which groups to commit (if ambiguous)
3. Commit each group separately

### Staged changes from before

If `git status` shows already-staged changes:
1. Check what's staged with `git diff --cached --stat`
2. If unrelated to current work, ask user before including
3. Never unstage user's prior work without asking

### Pre-commit hooks modify files

If pre-commit hook auto-modifies files:
1. The commit may fail — that's expected
2. Do NOT use `--no-verify`
3. Check what the hook changed
4. Stage the hook's changes
5. Commit again with same message

## Output

After successful commit, report:
```
Committed: <short hash>
Branch: <branch>
Files: <count> changed (<insertions>+, <deletions>-)
Tests: passed / skipped (no tests found)
Unstaged: <count> unrelated files remain
```

If the branch has diverged from base, ALSO output:
```
📋 PR Description (copy-paste ready):
---
[Generated PR description from Step 7]
---
```

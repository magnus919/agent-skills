# Principles-Based Code Assessment Workflow

A reusable workflow for auditing a codebase (default branch + one open PR) against
programming-principles books and producing structured, deduplicated, prioritized findings.

## When to use

- User asks for a "code review", "code assessment", "architecture review", or
  "code quality audit" referencing books like Clean Code, APoSD, WELC, Release It!, DDIA.
- User wants findings that go beyond surface lint — structural, design, reliability,
  data-consistency, and architectural observations.
- The task involves a repo with existing issues and PRs that must be checked for overlap.

## Workflow

### 1. Load the evaluation frameworks

Load the relevant skills in parallel:

```markdown
skill_view(name='programming-principles')
skill_view(name='codebase-inspection')
```

The `programming-principles` skill provides the per-book rule catalogs
(Clean Code, APoSD, WELC, Release It!, DDIA) and cross-cutting principles.
The `codebase-inspection` skill provides the LOC metrics and the systematic
audit bug-class catalog.

### 2. Understand the codebase

- If the repo is local, use `find`/`git log`/`git branch -a` to map the tree.
- If remote, use `gh repo clone` or `web_extract`.
- Get a directory tree: `find <repo> -type f | grep -v '.git/' | head -100`.
- Read every source file. Read key ones first, but do not skip small files —
  bugs cluster in overlooked files (configs, scripts, templates).

### 3. Read the GitHub context

This is critical for deduplication. Before writing findings:

- `gh pr view <N> --json title,body,files,additions,deletions,state` — for each
  open PR. Understand what the PR changes and what it does not change.
- `gh issue list --state open --json number,title,body --limit 10` — list all
  open issues. Read each one to understand what is already tracked.
- Cross-reference: a finding that overlaps an existing issue or PR is
  **not** a new finding. Note the overlap and move on.

### 4. Apply the evaluation framework

For each finding, identify:

| Attribute | What |
|-----------|------|
| **File** | Exact path, line range |
| **Function/context** | Named function or logical block |
| **Book principle** | Which book(s) the finding violates. Use the task-to-book mapping from the programming-principles skill. |
| **Principle quote** | The specific rule from the book (e.g., "Functions should do one thing" — Clean Code) |
| **Impact** | Data loss, silent failure, incorrect behavior, maintainability drag |
| **Priority** | P1 (data loss/security/runtime failure), P2 (structural/maintainability), P3 (design concern, notification) |
| **Merits issue?** | Yes/No — an issue describes the problem and suggests a fix. Not everything needs an issue. |
| **Already covered?** | Check against open issues and PRs. If yes, exclude from the deliverable. |

### 5. Organize findings

Group by priority, then by book. Each finding should have:

```
### N. Title
**File:** `path/to/file.mjs`, lines X–Y
**Book:** Book Name (principle)
**Priority:** P1/P2/P3

Description of the problem, evidence from the code, and why it matters.

🟡 Merits issue #N: `tag: short description of fix`
```

### 6. Maintain an exclusion log

For things you explicitly chose not to flag, note why:

| Topic | Why excluded |
|-------|-------------|
| Missing X | Already covered by issue #N |
| Y pattern | Below actionable threshold for an audit |

This shows the reader you considered the space systematically.

## Common pitfalls

- **Don't stop after one file.** Read *every* source file — bugs hide in small scripts,
  test helpers, and configuration templates.
- **Don't skip the PR branch.** The PR is the "planned implementation" the user asked
  about. Read its new files from a worktree or diff to understand what changes.
- **Don't flag what's already tracked.** Reading issues and PRs first prevents wasted
  effort and shows the user respect for their existing tracking.
- **Don't over-file.** A filing for every code smell produces noise. Issue findings when
  the problem has real impact (data loss, security, structural friction that blocks
  future changes). Minor things get a note but not an issue.
- **Don't forget to validate findings against both branches.** A finding may exist on
  main but be fixed in the PR, or be introduced by the PR. Call out the delta.
- **Prefer exact line numbers.** Vague "file X has a problem" is not actionable.
  Every finding needs exact file + function + line range.

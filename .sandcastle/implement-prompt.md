# TASK

Fix issue {{TASK_ID}}: {{ISSUE_TITLE}}

Pull in the issue with `gh issue view {{TASK_ID}}`. If it references a parent PRD/epic,
read that too. Work **only** on this issue.

Work on branch {{BRANCH}}. Make commits and run tests.

# PROJECT PROCESS — defer to canonical docs

This repository's process is authoritative. Read and follow them; do not restate or
invent your own rules:

- `CONTRIBUTING.md` — branch naming, **Conventional Commits**, code review and merge
  discipline, and the required pre-PR checks.
- `TRIAGE.md` — issue priority and pull order.

# CONTEXT

Recent commits:

<recent-commits>

!`git log -n 10 --format="%H%n%ad%n%B---" --date=short`

</recent-commits>

# EXPLORATION

Explore the repo and load the context you need. Pay special attention to the test files
covering the code you will touch.

# EXECUTION — Red/Green/Refactor

1. RED: write one failing test.
2. GREEN: implement until it passes.
3. REPEAT until the issue is resolved.
4. REFACTOR.

# FEEDBACK LOOPS

Before each commit, run the repository's checks (see `CONTRIBUTING.md`). For a Python /
`axctl`-style repo these are:

!`true`

```
uv run pytest tests/ -v --tb=short
ruff check
ruff format --check
```

Fix failures before committing.

# COMMIT

Make focused git commits using **Conventional Commits** (`feat:`, `fix:`, `docs:`,
`test:`, `chore:`, `ci:`), per `CONTRIBUTING.md`. Do **not** use a `RALPH:` or any
non-conventional prefix. Each commit message should state what changed and why, note key
decisions, and reference the issue.

# THE ISSUE

If the task is not complete, leave a comment on the issue describing what was done.
Do **not** close the issue — merge handling is governed by `CONTRIBUTING.md`.

Once complete, output <promise>COMPLETE</promise>.

# FINAL RULES

ONLY WORK ON A SINGLE ISSUE.

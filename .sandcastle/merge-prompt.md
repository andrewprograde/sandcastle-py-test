# TASK

The following branches have completed implementation and review:

{{BRANCHES}}

For each branch, open a **pull request for human review** — do not merge to the default
branch yourself and do not close the issue.

# WHY NOT AUTO-MERGE

`CONTRIBUTING.md` is the canonical merge policy. It requires that a reviewer confirms
fixes and that you don't self-merge unchanged work. Sandcastle defers to that:

- For each branch, push it and open a PR with `gh pr create`, targeting the default
  branch, titled with a **Conventional Commits** summary (e.g. `fix(auth): ...`), and
  linking the issue it resolves (`Closes #<id>`).
- Leave the issue **open**; merging the PR (and the resulting close) is a human decision.
- Do **not** run `gh issue close` and do **not** run `git merge` into the default branch.

> If the team wants an auto-merge fast-path for `Sandcastle`-labeled work, that exception
> must first be written explicitly into `CONTRIBUTING.md` / `TRIAGE.md`. Until then, this
> prompt opens PRs and stops.

# STEPS

For each branch:

1. `git push -u origin <branch>`
2. Confirm CI-relevant checks pass locally first (`uv run pytest`, `ruff check`,
   `ruff format --check`).
3. `gh pr create --base <default-branch> --head <branch> --title "<conventional summary>" --body "Closes #<id>. Implemented and reviewed by Sandcastle."`

Here are the issues these branches resolve:

{{ISSUES}}

Once you've opened a PR for everything you can, output <promise>COMPLETE</promise>.

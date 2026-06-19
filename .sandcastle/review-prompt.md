# TASK

Review the changes on branch `{{BRANCH}}` and improve clarity, consistency, and
maintainability **without changing behavior**.

# CONTEXT

## Branch diff

!`git diff {{TARGET_BRANCH}}...{{BRANCH}}`

## Commits on this branch

!`git log {{TARGET_BRANCH}}..{{BRANCH}} --oneline`

# STANDARDS — defer to canonical docs

Apply the review criteria and coding standards in `CONTRIBUTING.md` and the target repo's
linter config (`pyproject.toml` `[tool.ruff]`). Do not maintain a separate standards list.

# REVIEW PROCESS

1. **Understand the change** from the diff and commits above.
2. **Improve quality** where warranted:
   - reduce unnecessary complexity and nesting;
   - remove redundant code and obvious comments;
   - clarify names; consolidate related logic;
   - prefer explicit control flow over clever one-liners.
3. **Check correctness**:
   - does it match the issue intent? are edge cases handled?
   - are new/changed behaviors covered by tests?
   - missing type hints, unjustified `# type: ignore`, broad `except`, or unchecked
     assumptions?
   - any injection vulnerabilities, credential leaks, or unsafe subprocess/shell usage?
4. **Stay balanced** — don't over-simplify, over-abstract, or combine unrelated concerns.
5. **Preserve functionality** — change only *how* the code works, never *what* it does.

# EXECUTION

If you find improvements:

1. Make them directly on this branch.
2. Run the repository checks (`uv run pytest`, `ruff check`, `ruff format --check`).
3. Commit with a Conventional Commit message describing the refinement.

If the code is already clean, do nothing.

Once complete, output <promise>COMPLETE</promise>.

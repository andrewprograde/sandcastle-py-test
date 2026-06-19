# ISSUES

Here are the open issues opted in to automation (label `Sandcastle`):

<issues-json>

!`gh issue list --state open --label Sandcastle --limit 100 --json number,title,body,labels,comments --jq '[.[] | {number, title, body, labels: [.labels[].name], comments: [.comments[].body]}]'`

</issues-json>

# ALREADY IN REVIEW

These issues already have an **open pull request** (head branch `sandcastle/issue-<id>`)
and are awaiting human merge — their work is done, do **not** pull them again:

<open-prs-json>

!`gh pr list --state open --limit 100 --json number,title,headRefName --jq '[.[] | {number, title, branch: .headRefName}]'`

</open-prs-json>

# TASK

Select the issues to work on this cycle and build a dependency graph so independent
work can run in parallel.

## Priority — defer to TRIAGE.md

Order candidate issues using the repository's canonical triage rubric in `TRIAGE.md`.
Do **not** invent your own heuristic. The pull order is top-down:

1. **`P0` (commitment-blocking)** first — drop-everything work.
2. Otherwise honor the lane/severity order: `roadmap` minimum, then bugs by severity
   `P1` → `P2` → `P3` → `P4` → `P5`.
3. An issue with no pipeline label is awaiting grooming — **do not pull it**.
4. An issue whose branch `sandcastle/issue-<id>` appears in **ALREADY IN REVIEW** above
   already has an open PR — **do not pull it**; it is waiting on a human to merge.

## Dependencies

Within the prioritized set, determine whether each issue **blocks** or **is blocked by**
another open issue. Issue B is blocked by A if:

- B requires code or infrastructure A introduces;
- B and A modify overlapping files/modules (concurrent work would conflict);
- B depends on a decision or API shape A establishes.

An issue is **unblocked** if it has zero blocking dependencies on other open issues.

For each unblocked issue, assign a branch name in the exact format `sandcastle/issue-{id}`
(no slug). This is deterministic so re-planning the same issue reuses its branch and
accumulated progress.

# OUTPUT

Output your plan as JSON wrapped in `<plan>` tags, highest TRIAGE priority first:

<plan>
{"issues": [{"id": "42", "title": "Fix auth bug", "branch": "sandcastle/issue-42"}]}
</plan>

Include only unblocked issues. If every issue is blocked, include the single
highest-priority candidate. Always emit the `<plan>` tags, even when empty:
`<plan>{"issues": []}</plan>`.

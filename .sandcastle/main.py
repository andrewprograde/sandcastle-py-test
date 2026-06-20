"""Parallel planner with review — four-phase orchestration loop (Python port of main.mts).

  Phase 1 (Plan):            a planner agent reads the open `Sandcastle` issues, builds a
                             dependency graph, and emits a <plan> JSON of unblocked issues.
  Phase 2 (Execute+Review):  per issue, a sandbox runs the implementer, then (if it made
                             commits) a reviewer on the same branch. All issues run
                             concurrently, bounded by MAX_PARALLEL.
  Phase 3 (Merge):           one agent opens a PR per completed branch (human merges).

The outer loop repeats up to MAX_ITERATIONS so newly unblocked issues get picked up.

Run with:  sandcastle run --repo /path/to/target-repo
       or:  dotenvx run -f .env.sandcastle -- python .sandcastle/main.py
"""

from __future__ import annotations

import asyncio
import os
import subprocess

from pydantic import BaseModel

import sandcastle
from sandcastle.sandboxes.base import MountConfig
from sandcastle.sandboxes.docker import docker

# --- configuration ----------------------------------------------------------

MAX_ITERATIONS = 10
MAX_PARALLEL = 4

# The repo Sandcastle operates on (Galpin's "point it at a target repo"). Defaults to cwd.
REPO = os.path.abspath(os.environ.get("SANDCASTLE_TARGET_REPO", os.getcwd()))

AGENT_MODEL = "openai-codex/gpt-5.5"


def repo_default_branch() -> str:
    """The repo's default branch — the base for every issue worktree, regardless of
    which branch the repo happens to be checked out on. Pinning this avoids
    `worktree add -B` failing when the repo is left on a feature branch (e.g. after a
    prior run pushed one)."""
    try:
        out = subprocess.run(
            ["git", "-C", REPO, "symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        if out:
            return out.split("/", 1)[-1]  # "origin/main" -> "main"
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass
    for candidate in ("main", "master"):
        if (
            subprocess.run(
                ["git", "-C", REPO, "rev-parse", "--verify", candidate], capture_output=True
            ).returncode
            == 0
        ):
            return candidate
    head = subprocess.run(
        ["git", "-C", REPO, "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True, text=True
    ).stdout.strip()
    return head or "main"


class Issue(BaseModel):
    id: str
    title: str
    branch: str


class Plan(BaseModel):
    issues: list[Issue]


def build_sandbox_env() -> dict[str, str]:
    env: dict[str, str] = {}
    name = os.environ.get("SANDCASTLE_GIT_USER_NAME")
    email = os.environ.get("SANDCASTLE_GIT_USER_EMAIL")
    if name:
        env["SANDCASTLE_GIT_USER_NAME"] = name
        env["GIT_AUTHOR_NAME"] = name
        env["GIT_COMMITTER_NAME"] = name
    if email:
        env["SANDCASTLE_GIT_USER_EMAIL"] = email
        env["GIT_AUTHOR_EMAIL"] = email
        env["GIT_COMMITTER_EMAIL"] = email
    # Pass encrypted-.env keys through so dotenvx can decrypt inside the sandbox too.
    for key, value in os.environ.items():
        if key == "DOTENV_PRIVATE_KEY" or key.startswith("DOTENV_PRIVATE_KEY_"):
            env[key] = value
    # Forward GitHub + provider credentials so `gh` (planner/merge) and the agent can
    # authenticate inside the sandbox. Without GH_TOKEN the planner's `gh issue list`
    # returns nothing and the merge phase cannot push or open PRs.
    for key in ("GH_TOKEN", "GITHUB_TOKEN", "OPENAI_API_KEY"):
        if key in os.environ:
            env[key] = os.environ[key]
    return env


def sandbox_provider() -> sandcastle.SandboxProvider:
    pi_state = MountConfig(
        host_path=os.path.abspath(".sandcastle/pi"),
        sandbox_path="/home/agent/.pi/agent",
    )
    # Pin the image to the one `sandcastle docker build-image` built (named after the
    # repo). Isolated-worktree sandboxes otherwise derive the image name from the
    # worktree folder (e.g. sandcastle:sandcastle-issue-1) and fail to find it.
    return docker(
        image_name=f"sandcastle:{os.path.basename(REPO)}",
        mounts=[pi_state],
        env=build_sandbox_env(),
    )


def log_event(ev: object) -> None:
    """Stream the agent's activity so a long implement phase isn't a silent black box."""
    t = getattr(ev, "type", "")
    if t == "tool_call":
        print(f"    · tool {ev.name} {ev.args[:80]}", flush=True)  # type: ignore[attr-defined]
    elif t == "text":
        line = " ".join(ev.text.split())  # type: ignore[attr-defined]
        if line:
            print(f"    · {line[:140]}", flush=True)
    elif t == "result":
        print(f"    · result: {' '.join(ev.result.split())[:140]}", flush=True)  # type: ignore[attr-defined]


AGENT = sandcastle.pi(AGENT_MODEL, thinking="low")


async def work_issue(issue: Issue, semaphore: asyncio.Semaphore, base_branch: str) -> dict | None:
    """Implement then review a single issue in its own sandbox."""
    async with semaphore:
        async with await sandcastle.create_sandbox(
            branch=issue.branch, sandbox=sandbox_provider(), repo=REPO, base_branch=base_branch
        ) as sandbox:
            implement = await sandbox.run(
                agent=AGENT,
                prompt_file=".sandcastle/implement-prompt.md",
                max_iterations=100,
                prompt_args={
                    "TASK_ID": issue.id,
                    "ISSUE_TITLE": issue.title,
                    "BRANCH": issue.branch,
                },
                on_event=log_event,
            )
            if not implement.commits:
                return None
            await sandbox.run(
                agent=AGENT,
                prompt_file=".sandcastle/review-prompt.md",
                max_iterations=1,
                prompt_args={"BRANCH": issue.branch},
                on_event=log_event,
            )
            return {"id": issue.id, "title": issue.title, "branch": issue.branch}


async def main() -> None:
    for iteration in range(1, MAX_ITERATIONS + 1):
        print(f"\n=== Iteration {iteration}/{MAX_ITERATIONS} ===\n")

        plan_result = await sandcastle.run(
            agent=AGENT,
            sandbox=sandbox_provider(),
            repo=REPO,
            max_iterations=1,
            prompt_file=".sandcastle/plan-prompt.md",
            output=sandcastle.Output.object(tag="plan", schema=Plan),
        )
        plan: Plan = plan_result.output  # type: ignore[assignment]

        if not plan.issues:
            print("No unblocked issues to work on. Exiting.")
            break

        print(f"Planning complete. {len(plan.issues)} issue(s) in parallel:")
        for issue in plan.issues:
            print(f"  {issue.id}: {issue.title} -> {issue.branch}")

        base_branch = repo_default_branch()
        semaphore = asyncio.Semaphore(MAX_PARALLEL)
        outcomes = await asyncio.gather(
            *(work_issue(issue, semaphore, base_branch) for issue in plan.issues),
            return_exceptions=True,
        )

        completed: list[dict] = []
        for issue, outcome in zip(plan.issues, outcomes, strict=True):
            if isinstance(outcome, Exception):
                print(f"  x {issue.id} ({issue.branch}) failed: {outcome}")
            elif outcome is not None:
                completed.append(outcome)

        if not completed:
            print("No commits produced. Nothing to merge.")
            continue

        branches = "\n".join(f"- {c['branch']}" for c in completed)
        issues_md = "\n".join(f"- {c['id']}: {c['title']}" for c in completed)
        print(f"\n{len(completed)} branch(es) ready; opening PRs.")

        await sandcastle.run(
            agent=AGENT,
            sandbox=sandbox_provider(),
            repo=REPO,
            max_iterations=1,
            prompt_file=".sandcastle/merge-prompt.md",
            prompt_args={"BRANCHES": branches, "ISSUES": issues_md},
            on_event=log_event,
            # Run the merge agent in an isolated worktree, NOT on the host working tree.
            # The docker provider defaults to the head strategy (operates on the repo
            # itself); the merge agent's `git checkout`/`git stash -u` would then mutate
            # the repo's branch and sweep the untracked .sandcastle/ dir into a stash,
            # breaking the next iteration. An isolated worktree confines those ops.
            branch_strategy=sandcastle.MergeToHeadStrategy(),
        )

    print("\nAll done.")


if __name__ == "__main__":
    asyncio.run(main())

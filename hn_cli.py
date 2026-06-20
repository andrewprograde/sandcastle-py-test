from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

DEFAULT_LIMIT = 10
DEFAULT_TIMEOUT = 10
HN_API = "https://hacker-news.firebaseio.com/v0"
HN_DISCUSSION_URL = "https://news.ycombinator.com/item?id={story_id}"
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ORANGE = "\033[38;5;208m"
CYAN = "\033[36m"


@dataclass(frozen=True)
class Post:
    title: str
    url: str
    score: int
    by: str
    descendants: int


def _load_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> Any:
    with urlopen(url, timeout=timeout) as response:
        return json.load(response)


def _post_from_item(item: dict[str, Any], story_id: int) -> Post:
    return Post(
        title=item.get("title") or "Untitled",
        url=item.get("url") or HN_DISCUSSION_URL.format(story_id=story_id),
        score=int(item.get("score") or 0),
        by=item.get("by") or "unknown",
        descendants=int(item.get("descendants") or 0),
    )


def fetch_top_posts(
    limit: int = DEFAULT_LIMIT, timeout: int = DEFAULT_TIMEOUT
) -> list[Post]:
    """Fetch the current top Hacker News posts."""
    story_ids = _load_json(f"{HN_API}/topstories.json", timeout=timeout)[:limit]
    posts: list[Post] = []

    for story_id in story_ids:
        item = _load_json(f"{HN_API}/item/{story_id}.json", timeout=timeout) or {}
        posts.append(_post_from_item(item, story_id))

    return posts


def _value(post: Post | dict[str, Any], key: str) -> Any:
    if isinstance(post, Post):
        return getattr(post, key)
    return post.get(key)


def _truncate(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    return value[: max(0, width - 1)] + "…"


def _link(url: str, label: str) -> str:
    # OSC-8 hyperlinks are clickable in macOS Terminal/iTerm2 and many terminals.
    return f"\033]8;;{url}\033\\{label}\033]8;;\033\\"


def format_posts(posts: list[Post | dict[str, Any]], url_width: int = 72) -> str:
    lines = [f"{BOLD}{ORANGE}Top 10 Hacker News Posts{RESET}", ""]

    for index, post in enumerate(posts, start=1):
        title = str(_value(post, "title") or "Untitled")
        url = str(_value(post, "url") or "")
        score = int(_value(post, "score") or 0)
        by = str(_value(post, "by") or "unknown")
        comments = int(_value(post, "descendants") or 0)
        label = _truncate(url, url_width)

        lines.append(f"{BOLD}{index:>2}. {title}{RESET}")
        lines.append(
            f"    {ORANGE}{score} points{RESET} {DIM}by {by} • "
            f"{comments} comments{RESET}"
        )
        lines.append(f"    {CYAN}{_link(url, label)}{RESET}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="hn", description="Show the top 10 Hacker News posts."
    )
    parser.add_argument(
        "--limit", type=int, default=DEFAULT_LIMIT, help="number of posts to show"
    )
    parser.add_argument(
        "--timeout", type=int, default=DEFAULT_TIMEOUT, help="HTTP timeout in seconds"
    )
    args = parser.parse_args(argv)

    try:
        posts = fetch_top_posts(limit=args.limit, timeout=args.timeout)
    except (OSError, URLError, json.JSONDecodeError) as exc:
        print(f"hn: failed to fetch Hacker News posts: {exc}", file=sys.stderr)
        return 1

    print(format_posts(posts), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

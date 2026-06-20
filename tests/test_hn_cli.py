from __future__ import annotations

import json
from io import BytesIO

from hn_cli import fetch_top_posts, format_posts


class _Response(BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return None


def test_fetch_top_posts_loads_first_10_hacker_news_items(monkeypatch):
    def fake_urlopen(url, timeout=10):
        if url.endswith("/topstories.json"):
            return _Response(json.dumps(list(range(1, 13))).encode())
        item_id = int(url.rsplit("/", 1)[-1].split(".")[0])
        return _Response(
            json.dumps(
                {
                    "id": item_id,
                    "title": f"Story {item_id}",
                    "url": f"https://example.com/articles/{item_id}",
                    "score": item_id * 10,
                    "by": "alice",
                    "descendants": item_id,
                }
            ).encode()
        )

    monkeypatch.setattr("hn_cli.urlopen", fake_urlopen)

    posts = fetch_top_posts(limit=10)

    assert len(posts) == 10
    assert posts[0].title == "Story 1"
    assert posts[-1].url == "https://example.com/articles/10"


def test_format_posts_uses_clickable_full_url_and_truncated_label():
    long_url = "https://example.com/" + "very-long-path/" * 8
    output = format_posts(
        [
            {
                "title": "A useful post",
                "url": long_url,
                "score": 42,
                "by": "bob",
                "descendants": 7,
            }
        ],
        url_width=35,
    )

    assert "Top 10 Hacker News Posts" in output
    assert "A useful post" in output
    assert long_url in output  # OSC-8 target remains the full URL.
    assert "…" in output
    assert "\x1b]8;;" in output

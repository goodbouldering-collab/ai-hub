import unittest
from types import SimpleNamespace
from unittest.mock import patch

from core.collector import fetch_rss


class CollectorTitleFilterTests(unittest.TestCase):
    def test_source_can_exclude_codex_prereleases_without_hiding_stable_release(self):
        feed = SimpleNamespace(
            entries=[
                SimpleNamespace(
                    title="0.150.0-alpha.6",
                    link="https://github.com/openai/codex/releases/tag/rust-v0.150.0-alpha.6",
                    summary="Preview build",
                    published="Fri, 22 Aug 2026 00:00:00 GMT",
                    published_parsed=None,
                    updated_parsed=None,
                ),
                SimpleNamespace(
                    title="0.149.0",
                    link="https://github.com/openai/codex/releases/tag/rust-v0.149.0",
                    summary="Stable build",
                    published="Thu, 21 Aug 2026 00:00:00 GMT",
                    published_parsed=None,
                    updated_parsed=None,
                ),
            ]
        )
        source = {
            "name": "OpenAI Codex Releases",
            "url": "https://github.com/openai/codex/releases.atom",
            "category": "AI公式",
            "limit": 15,
            "exclude_title_regex": r"(?i)(?:^|[-.])(?:alpha|beta|rc)(?:[-.]|$)",
        }

        with patch("core.collector.feedparser.parse", return_value=feed):
            articles = fetch_rss(source)

        self.assertEqual(["0.149.0"], [article.title for article in articles])

    def test_feed_timestamp_is_normalized_so_freshness_ranking_can_use_it(self):
        feed = SimpleNamespace(
            entries=[
                SimpleNamespace(
                    title="Fresh release",
                    link="https://example.com/releases/fresh",
                    summary="A fresh release",
                    published="Sat, 22 Aug 2026 00:00:00 GMT",
                    published_parsed=(2026, 8, 22, 0, 0, 0, 5, 234, 0),
                    updated_parsed=None,
                )
            ]
        )
        source = {
            "name": "Official feed",
            "url": "https://example.com/feed.xml",
            "category": "AI公式",
        }

        with patch("core.collector.feedparser.parse", return_value=feed):
            articles = fetch_rss(source)

        self.assertEqual("2026-08-22T00:00:00+00:00", articles[0].published)


if __name__ == "__main__":
    unittest.main()

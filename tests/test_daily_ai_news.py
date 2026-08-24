import json
import importlib.util
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

from core.collector import Article
from core.exporter import _japan_today, export_daily_ai_news_snapshot
from core.ranker import rank_articles
from core.daily_news import prepend_daily_ai_news, render_daily_ai_news


ROOT = Path(__file__).resolve().parents[1]


def load_site_builder():
    spec = importlib.util.spec_from_file_location(
        "build_site_for_daily_ai_news",
        ROOT / "site" / "build_site.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = load_site_builder()


def make_article(index: int, *, source: str = "Source", category: str = "AIニュース") -> Article:
    return Article(
        source=source,
        category=category,
        title=f"Article {index}",
        url=f"https://example.com/articles/{index}",
        body=f"Body {index}",
        published="2026-08-22T00:00:00+00:00",
        fetched_at="2026-08-22 09:00:00",
    )


def make_summary(
    index: int,
    *,
    score: int = 70,
    japan_relevance: int = 70,
    codex_relevance: int = 0,
) -> dict:
    return {
        "title_ja": f"ニュース{index}",
        "summary": f"ニュース{index}の要点です。",
        "plain_summary": f"ニュース{index}をわかりやすく説明します。",
        "story_example": f"たとえば、ニュース{index}を仕事で試す場面です。",
        "genre": "ai_business",
        "score": score,
        "japan_relevance": japan_relevance,
        "codex_relevance": codex_relevance,
    }


class DailyNewsRankingTests(unittest.TestCase):
    def test_japan_and_codex_relevance_win_while_one_source_is_capped(self):
        articles = []
        summaries = {}

        for index in range(5):
            article = make_article(index, source="Repeated Foreign Blog")
            articles.append(article)
            summaries[article.hash] = make_summary(index, score=95, japan_relevance=5)

        for index in range(5, 13):
            source = f"Trusted Source {index}"
            category = "AI国内" if index in {5, 6} else "AI公式"
            article = make_article(index, source=source, category=category)
            articles.append(article)
            summaries[article.hash] = make_summary(
                index,
                score=76 if index == 7 else 80,
                japan_relevance=95 if index in {5, 6, 7} else 70,
                codex_relevance=100 if index == 7 else 0,
            )

        with tempfile.TemporaryDirectory() as tmp:
            ranked, ranked_summaries = rank_articles(
                articles,
                summaries,
                Path(tmp) / "preferences.json",
                top_n=10,
            )

        self.assertEqual(10, len(ranked))
        self.assertEqual("Article 7", ranked[0].title)
        self.assertLessEqual(
            sum(article.source == "Repeated Foreign Blog" for article in ranked),
            2,
        )
        codex_breakdown = ranked_summaries[ranked[0].hash]["breakdown"]
        self.assertGreater(codex_breakdown["codex_relevance"], 0)
        self.assertGreater(codex_breakdown["japan_relevance"], 0)


class DailyNewsSnapshotTests(unittest.TestCase):
    def test_japan_today_does_not_require_an_external_timezone_database(self):
        self.assertIsInstance(_japan_today(), date)

    def test_writes_ten_valid_plain_explanations_and_story_examples(self):
        articles = [make_article(index, source=f"Source {index}") for index in range(10)]
        summaries = {article.hash: make_summary(index) for index, article in enumerate(articles)}

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "daily-ai-news.json"
            result = export_daily_ai_news_snapshot(
                articles,
                summaries,
                target,
                today=date(2026, 8, 22),
            )
            payload = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(target, result)
        self.assertEqual("2026-08-22", payload["date"])
        self.assertEqual(10, len(payload["items"]))
        self.assertEqual("ニュース0をわかりやすく説明します。", payload["items"][0]["plain_summary"])
        self.assertEqual("たとえば、ニュース0を仕事で試す場面です。", payload["items"][0]["story_example"])

    def test_invalid_run_keeps_last_successful_snapshot(self):
        articles = [make_article(index) for index in range(10)]
        summaries = {article.hash: make_summary(index) for index, article in enumerate(articles)}
        summaries[articles[4].hash]["plain_summary"] = ""

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "daily-ai-news.json"
            target.write_text("last-successful-snapshot", encoding="utf-8")
            result = export_daily_ai_news_snapshot(
                articles,
                summaries,
                target,
                today=date(2026, 8, 22),
            )

            self.assertIsNone(result)
            self.assertEqual("last-successful-snapshot", target.read_text(encoding="utf-8"))

    def test_uses_lower_ranked_valid_candidate_when_one_summary_failed(self):
        articles = [make_article(index) for index in range(11)]
        summaries = {article.hash: make_summary(index) for index, article in enumerate(articles)}
        summaries[articles[2].hash]["plain_summary"] = ""

        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "daily-ai-news.json"
            result = export_daily_ai_news_snapshot(
                articles,
                summaries,
                target,
                today=date(2026, 8, 22),
            )
            payload = json.loads(target.read_text(encoding="utf-8"))

        self.assertEqual(target, result)
        self.assertEqual(10, len(payload["items"]))
        self.assertNotIn("https://example.com/articles/2", [item["url"] for item in payload["items"]])
        self.assertIn("https://example.com/articles/10", [item["url"] for item in payload["items"]])


class DailyNewsRenderingTests(unittest.TestCase):
    def make_payload(self) -> dict:
        items = []
        for index in range(10):
            items.append(
                {
                    "title": "<script>alert(1)</script>" if index == 0 else f"ニュース{index + 1}",
                    "url": f"https://example.com/news/{index + 1}",
                    "source": f"情報元{index + 1}",
                    "published": "2026-08-22T00:00:00+00:00",
                    "plain_summary": f"わかりやすい説明{index + 1}",
                    "story_example": f"たとえば、使いどころ{index + 1}です。",
                }
            )
        return {"date": "2026-08-22", "items": items}

    def test_renders_exactly_ten_safe_ranked_news_cards(self):
        rendered = render_daily_ai_news(self.make_payload())

        self.assertIn("今日のAIニュース10", rendered)
        self.assertEqual(10, rendered.count("class='daily-ai-news__item'"))
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", rendered)
        self.assertNotIn("<script>alert(1)</script>", rendered)
        self.assertIn("たとえば、使いどころ1です。", rendered)
        self.assertNotIn("小学生向け", rendered)
        self.assertNotIn("日本との関係", rendered)

    def test_fuses_explanation_and_use_example_without_labels(self):
        rendered = render_daily_ai_news(self.make_payload())

        self.assertEqual(10, rendered.count("class='daily-ai-news__summary'"))
        self.assertNotIn("<strong>わかりやすく</strong>", rendered)
        self.assertNotIn("<strong>使う場面</strong>", rendered)
        self.assertNotIn("class='daily-ai-news__story'", rendered)
        self.assertIn(
            "<p class='daily-ai-news__summary'>"
            "わかりやすい説明1たとえば、使いどころ1です。</p>",
            rendered,
        )

    def test_invalid_url_fails_closed(self):
        payload = self.make_payload()
        payload["items"][3]["url"] = "javascript:alert(1)"
        self.assertEqual("", render_daily_ai_news(payload))

    def test_only_codex_update_series_gets_news_before_article_body(self):
        body = "<p id='codex-current'>Codex update</p>"
        rendered = prepend_daily_ai_news(
            {"content_series": "codex-update-log"},
            body,
            self.make_payload(),
        )
        other = prepend_daily_ai_news({"content_series": "another"}, body, self.make_payload())

        self.assertLess(rendered.index("今日のAIニュース10"), rendered.index("codex-current"))
        self.assertEqual(body, other)


class DailyNewsBuildIntegrationTests(unittest.TestCase):
    def test_blog_build_reads_snapshot_and_prepends_it_only_to_codex_article(self):
        payload = DailyNewsRenderingTests().make_payload()
        original_blog_dir = builder.BLOG_DIR
        original_dist = builder.DIST
        original_snapshot = builder.DAILY_AI_NEWS_JSON

        with tempfile.TemporaryDirectory() as tmp:
            temp_root = Path(tmp)
            blog_dir = temp_root / "blog"
            blog_dir.mkdir()
            snapshot = temp_root / "daily-ai-news.json"
            snapshot.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
            (blog_dir / "codex-update-log.md").write_text(
                "---\ntitle: Codex更新\ndate: 2026-08-22\n"
                "content_series: codex-update-log\n---\n"
                "## Codex本文\n更新内容です。\n",
                encoding="utf-8",
            )
            (blog_dir / "other.md").write_text(
                "---\ntitle: 別の記事\ndate: 2026-08-22\n---\n"
                "## 別の本文\nニュース欄は不要です。\n",
                encoding="utf-8",
            )
            try:
                builder.BLOG_DIR = blog_dir
                builder.DIST = temp_root / "dist"
                builder.DAILY_AI_NEWS_JSON = snapshot
                builder.build_blog()
                codex_page = (builder.DIST / "blog" / "codex-update-log.html").read_text(
                    encoding="utf-8"
                )
                other_page = (builder.DIST / "blog" / "other.html").read_text(encoding="utf-8")
            finally:
                builder.BLOG_DIR = original_blog_dir
                builder.DIST = original_dist
                builder.DAILY_AI_NEWS_JSON = original_snapshot

        self.assertEqual(1, codex_page.count("今日のAIニュース10"))
        self.assertLess(codex_page.index("今日のAIニュース10"), codex_page.index("Codex本文"))
        self.assertNotIn("今日のAIニュース10", other_page)


class DailyNewsWorkflowTests(unittest.TestCase):
    def test_daily_workflow_stages_thumbnail_cache_before_rebase(self):
        workflow = (ROOT / ".github" / "workflows" / "daily.yml").read_text(encoding="utf-8")

        self.assertIn("data/history.db data/thumb_cache.json", workflow)
        self.assertIn("git restore --worktree -- site/dist", workflow)
        self.assertIn("git pull --rebase origin main", workflow)


if __name__ == "__main__":
    unittest.main()

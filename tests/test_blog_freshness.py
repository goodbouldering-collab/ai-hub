import importlib.util
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from datetime import date, datetime, timedelta, timezone

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))

from blog_freshness import (  # noqa: E402
    BLOG_NEW_WINDOW_DAYS,
    blog_date_label,
    effective_blog_date,
    is_new_blog,
)


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = _load_module("build_site_for_freshness", ROOT / "site" / "build_site.py")
portal = _load_module("build_portal_for_freshness", ROOT / "site" / "build_portal.py")
BLOG_DIR = ROOT / "content" / "blog"
CODEX_UPDATE_ARTICLE = BLOG_DIR / "codex-update-log.md"


class BlogFreshnessTest(unittest.TestCase):
    def test_last_update_controls_new_status_through_day_seven(self) -> None:
        meta = {"date": "2026-07-01", "date_modified": "2026-08-21"}

        self.assertEqual(BLOG_NEW_WINDOW_DAYS, 7)
        self.assertEqual(effective_blog_date(meta, today=date(2026, 8, 28)), date(2026, 8, 21))
        self.assertTrue(is_new_blog(meta, today=date(2026, 8, 28)))
        self.assertFalse(is_new_blog(meta, today=date(2026, 8, 29)))
        self.assertEqual(blog_date_label(meta, today=date(2026, 8, 28)), "8月21日更新")

    def test_publish_date_is_used_when_there_is_no_update(self) -> None:
        meta = {"date": "2026-08-21"}

        self.assertEqual(effective_blog_date(meta, today=date(2026, 8, 21)), date(2026, 8, 21))
        self.assertTrue(is_new_blog(meta, today=date(2026, 8, 21)))
        self.assertEqual(blog_date_label(meta, today=date(2026, 8, 21)), "8月21日公開")

    def test_invalid_or_future_update_falls_back_to_publish_date(self) -> None:
        today = date(2026, 8, 21)

        self.assertFalse(is_new_blog({}, today=today))
        self.assertFalse(is_new_blog({"date": "not-a-date"}, today=today))
        self.assertFalse(is_new_blog({"date": "2026-08-22"}, today=today))
        for modified in ("not-a-date", "2026-08-22"):
            meta = {"date": "2026-08-20", "date_modified": modified}
            self.assertEqual(effective_blog_date(meta, today=today), date(2026, 8, 20))
            self.assertTrue(is_new_blog(meta, today=today))
            self.assertEqual(blog_date_label(meta, today=today), "8月20日公開")

    def test_iso_datetime_is_converted_to_japan_date(self) -> None:
        meta = {"date_modified": "2026-08-20T15:30:00+00:00"}

        self.assertEqual(
            effective_blog_date(meta, today=date(2026, 8, 21)),
            date(2026, 8, 21),
        )
        self.assertEqual(blog_date_label(meta, today=date(2026, 8, 21)), "8月21日更新")

    def test_fresh_blog_page_puts_new_and_update_date_with_the_title(self) -> None:
        today = datetime.now(timezone(timedelta(hours=9))).date()
        meta = {"date": "2026-01-01", "date_modified": today.isoformat()}

        page = builder.render_content_page(
            "常時更新の記事",
            meta,
            "<p>本文</p>",
            "<nav></nav>",
            kind="blog",
        )

        self.assertIn(
            "<div class='blog-title-line'><h1>常時更新の記事</h1>"
            "<span class='blog-new-badge'>NEW</span>"
            f"<span class='blog-update-label'>{blog_date_label(meta)}</span></div>",
            page,
        )

        jsonld_match = re.search(
            r"<script type='application/ld\+json'>(.*?)</script>",
            page,
            re.DOTALL,
        )
        self.assertIsNotNone(jsonld_match)
        jsonld = json.loads(jsonld_match.group(1))
        self.assertEqual(jsonld["datePublished"], "2026-01-01")
        self.assertEqual(jsonld["dateModified"], today.isoformat())

        old_page = builder.render_content_page(
            "古い記事",
            {"date": "2026-01-01"},
            "<p>本文</p>",
            "<nav></nav>",
            kind="blog",
        )
        self.assertNotIn("<span class='blog-new-badge'>NEW</span>", old_page)

    def test_blog_index_orders_by_update_and_marks_only_fresh_title(self) -> None:
        today = datetime.now(timezone(timedelta(hours=9))).date()
        original_blog_dir = builder.BLOG_DIR
        original_dist = builder.DIST
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            blog_dir = temp_root / "blog-source"
            blog_dir.mkdir()
            (blog_dir / "z-old-file-name.md").write_text(
                "---\ntitle: 古い記事\ndate: 2026-01-01\n---\n本文",
                encoding="utf-8",
            )
            (blog_dir / "a-evergreen.md").write_text(
                "---\ntitle: 更新した記事\ndate: 2026-01-01\n"
                f"date_modified: {today.isoformat()}\n---\n本文",
                encoding="utf-8",
            )
            try:
                builder.BLOG_DIR = blog_dir
                builder.DIST = temp_root / "dist"
                builder.build_blog()
                index = (builder.DIST / "blog" / "index.html").read_text(encoding="utf-8")
            finally:
                builder.BLOG_DIR = original_blog_dir
                builder.DIST = original_dist

        self.assertLess(index.index("更新した記事"), index.index("古い記事"))
        self.assertEqual(index.count("<span class='blog-new-badge'>NEW</span>"), 1)
        self.assertIn(blog_date_label({"date_modified": today.isoformat()}), index)

    def test_home_blog_cards_order_by_update_and_mark_the_title(self) -> None:
        today = datetime.now(timezone(timedelta(hours=9))).date()
        original_blog_dir = portal.BLOG_DIR
        with tempfile.TemporaryDirectory() as temp_dir:
            blog_dir = Path(temp_dir)
            (blog_dir / "z-old-file-name.md").write_text(
                "---\ntitle: 古い記事\ndate: 2026-01-01\n---\n本文",
                encoding="utf-8",
            )
            (blog_dir / "a-evergreen.md").write_text(
                "---\ntitle: 更新した記事\ndate: 2026-01-01\n"
                f"date_modified: {today.isoformat()}\n---\n本文",
                encoding="utf-8",
            )
            try:
                portal.BLOG_DIR = blog_dir
                posts = portal._load_recent_blog_posts(limit=2)
            finally:
                portal.BLOG_DIR = original_blog_dir

        self.assertEqual([post["title"] for post in posts], ["更新した記事", "古い記事"])
        card = portal._render_blog_card(posts[0])
        self.assertIn(
            "<div class='blog-card-title-row'><h3>更新した記事</h3>"
            "<span class='blog-new-badge'>NEW</span></div>",
            card,
        )
        self.assertIn(blog_date_label(posts[0]), card)

    def test_codex_updates_use_one_stable_article(self) -> None:
        series_articles: list[Path] = []
        for article in BLOG_DIR.glob("*.md"):
            meta, _ = builder._parse_frontmatter(article.read_text(encoding="utf-8"))
            if meta.get("content_series") == "codex-update-log":
                series_articles.append(article)

        self.assertEqual(series_articles, [CODEX_UPDATE_ARTICLE])
        meta, body = builder._parse_frontmatter(CODEX_UPDATE_ARTICLE.read_text(encoding="utf-8"))
        self.assertIsInstance(date.fromisoformat(str(meta["date_modified"])), date)
        self.assertEqual(
            meta["title"],
            "今日のAIニュースと新機能活用術",
        )
        self.assertEqual(meta["image"], "/img/blog-codex-update-log-hero-20260822.png")
        self.assertTrue(meta["hero_image"])
        self.assertEqual(body.count("<!-- CODEX_UPDATE_CURRENT:BEGIN -->"), 1)
        self.assertEqual(body.count("<!-- CODEX_UPDATE_CURRENT:END -->"), 1)
        self.assertEqual(body.count("<!-- CODEX_UPDATE_ARCHIVE:BEGIN -->"), 1)
        self.assertEqual(body.count("<!-- CODEX_UPDATE_ARCHIVE:END -->"), 1)
        self.assertIn("過去のアップデート要約", body)
        self.assertIn("2026年8月7日｜CLI 0.147.0", body)
        self.assertNotIn("2026年8月13日｜CLI 0.147.0", body)
        self.assertIn("https://learn.chatgpt.com/docs/changelog", body)
        current = body.split("<!-- CODEX_UPDATE_CURRENT:BEGIN -->", 1)[1].split(
            "<!-- CODEX_UPDATE_CURRENT:END -->", 1
        )[0]
        feature_sections = re.split(r"(?m)^## \d+\. ", current)[1:]
        self.assertGreaterEqual(len(feature_sections), 1)
        self.assertLessEqual(len(feature_sections), 4)
        self.assertNotIn("**使い方：**", current)
        self.assertNotIn('class="codex-command-callout"', current)
        self.assertNotIn('class="codex-use-story"', current)
        self.assertIn("## 1. 普段のブラウザから頼む｜`Use your browser`", current)
        self.assertIn("## 2. サイトの操作を使う｜`Site tools (WebMCP)`", current)
        self.assertIn("## 3. クラウド作業へ安全にログインする｜`Web sign-in`", current)
        self.assertIn("## 4. レビューを合図に動かす｜`Event-triggered tasks`", current)
        self.assertIn(
            "地域団体のサイト修正でGitHubのプルリクエストに指摘が届いた時は、"
            "レビュー内容の要約と修正案の準備を自動で始められます。",
            current,
        )
        for section in feature_sections:
            self.assertRegex(
                section,
                r"\[公式情報\]\(https://(?:learn\.chatgpt\.com|developers\.openai\.com|github\.com/openai/)",
            )
        image_path = ROOT / "site" / "static" / str(meta["image"]).lstrip("/")
        with Image.open(image_path) as hero:
            self.assertGreaterEqual(hero.width, 1200)
            self.assertGreater(hero.width, hero.height)
            self.assertGreater(hero.width / hero.height, 1.8)

    def test_codex_update_article_renders_a_plain_story_format_without_japan_label(self) -> None:
        raw = CODEX_UPDATE_ARTICLE.read_text(encoding="utf-8")
        meta, body = builder._parse_frontmatter(raw)
        markdown = builder._load_markdown()
        body_html = markdown.markdown(body, extensions=["extra", "sane_lists", "attr_list"])
        body_html = builder.prepend_daily_ai_news(
            meta,
            body_html,
            builder.load_daily_ai_news(builder.DAILY_AI_NEWS_JSON),
        )
        page = builder.render_content_page(
            str(meta["title"]),
            meta,
            body_html,
            "<nav></nav>",
            page_path="blog/codex-update-log.html",
            kind="blog",
        )

        self.assertIn("<title>今日のAIニュースと新機能活用術 | AIclimb（AI相談）</title>", page)
        self.assertIn("content-wrap--codex-update", page)
        self.assertIn("今日のCodex新機能と活用術", page)
        self.assertIn("たとえば、", page)
        self.assertNotIn("小学生向け", page)
        self.assertNotIn("日本との関係", page)

        guide = portal._render_codex_update_guide()
        self.assertIn("使う場面", guide)
        self.assertNotIn("日本との関係", guide)

    def test_codex_update_toc_does_not_add_a_second_number_to_feature_titles(self) -> None:
        page = builder.render_content_page(
            "今日のAIニュースと新機能活用術",
            {"content_series": "codex-update-log"},
            (
                "<h2>今日のAIニュース10</h2>"
                "<h2 class='codex-feature-title'>1. codex queue｜追加で頼む</h2>"
                "<h2 class='codex-feature-title'>2. codex doctor｜状態を調べる</h2>"
            ),
            "<nav></nav>",
            kind="blog",
        )

        toc_start = page.index("<div class='content-toc'")
        toc = page[toc_start : toc_start + 1000]
        self.assertIn("<ul>", toc)
        self.assertNotIn("<ol>", toc)
        self.assertIn("1. codex queue｜追加で頼む", toc)


if __name__ == "__main__":
    unittest.main()

import importlib.util
from datetime import date, timedelta
from pathlib import Path
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "site"))

from blog_freshness import is_new_blog  # noqa: E402


def _load_site_builder():
    path = ROOT / "site" / "build_site.py"
    spec = importlib.util.spec_from_file_location("build_site_for_platform_blog", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


builder = _load_site_builder()
ARTICLE = ROOT / "content" / "blog" / "2026-07-25-sites-vs-vercel-safe-migration.md"


class SitesCloudflareVercelBlogTest(unittest.TestCase):
    def test_optimized_title_leads_with_platforms_and_states_github_principle(self) -> None:
        meta, _ = builder._parse_frontmatter(ARTICLE.read_text(encoding="utf-8"))
        title = str(meta["title"])

        self.assertTrue(title.startswith("ChatGPT Sites"))
        self.assertLessEqual(len(title), 50)
        for term in ("クラウドフレア", "Vercel比較", "サイト公開の極意", "GitHubを残す"):
            with self.subTest(term=term):
                self.assertIn(term, title)

    def test_rewrite_uses_a_newer_update_date_and_is_new_on_that_day(self) -> None:
        meta, _ = builder._parse_frontmatter(ARTICLE.read_text(encoding="utf-8"))

        published = date.fromisoformat(str(meta["date"]))
        modified = date.fromisoformat(str(meta["date_modified"]))

        self.assertGreater(modified, published)
        self.assertTrue(is_new_blog(meta, today=modified))

    def test_rewrite_compares_all_three_publishers_and_separates_github(self) -> None:
        meta, body = builder._parse_frontmatter(ARTICLE.read_text(encoding="utf-8"))
        searchable = f"{meta.get('title', '')}\n{meta.get('summary', '')}\n{body}"

        for term in ("ChatGPT Sites", "Cloudflare", "Vercel", "GitHub"):
            with self.subTest(term=term):
                self.assertIn(term, searchable)

    def test_updated_article_sorts_ahead_of_previous_day(self) -> None:
        meta, _ = builder._parse_frontmatter(ARTICLE.read_text(encoding="utf-8"))
        modified = date.fromisoformat(str(meta["date_modified"]))
        original_blog_dir = builder.BLOG_DIR
        original_dist = builder.DIST

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_root = Path(temp_dir)
            blog_dir = temp_root / "blog-source"
            blog_dir.mkdir()
            (blog_dir / ARTICLE.name).write_text(ARTICLE.read_text(encoding="utf-8"), encoding="utf-8")
            (blog_dir / "previous-day.md").write_text(
                "---\ntitle: 前日の記事\n"
                f"date: {(modified - timedelta(days=1)).isoformat()}\n---\n本文",
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

        self.assertLess(index.index(str(meta["title"])), index.index("前日の記事"))


if __name__ == "__main__":
    unittest.main()

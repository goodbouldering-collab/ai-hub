from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TITLE = "AIClimb｜AIで仕事を軽くする実践相談・伴走支援【彦根・滋賀】"

ADMIN_TITLE_FILES = [
    ROOT / "admin" / "static" / "index.html",
    ROOT / "api" / "admin" / "docs" / "index.ts",
    ROOT / "api" / "admin" / "login.ts",
    ROOT / "site" / "static" / "admin" / "apps" / "blog.html",
    ROOT / "site" / "static" / "admin" / "apps" / "reel.html",
    ROOT / "site" / "static" / "admin" / "blog.html",
    ROOT / "site" / "static" / "admin" / "chat.html",
    ROOT / "site" / "static" / "admin" / "gubble-sns.html",
    ROOT / "site" / "static" / "admin" / "hub.html",
    ROOT / "site" / "static" / "admin" / "index.html",
    ROOT / "site" / "static" / "admin" / "sns-cross-media-dashboard.html",
    ROOT / "site" / "static" / "admin" / "sns-post.html",
    ROOT / "site" / "static" / "ops" / "index.html",
]


class SiteTitleSyncTest(unittest.TestCase):
    def test_public_title_and_social_metadata_are_synchronized(self) -> None:
        source = (ROOT / "site" / "build_portal.py").read_text(encoding="utf-8")
        index = (ROOT / "site" / "dist" / "index.html").read_text(encoding="utf-8")

        self.assertIn(f'SITE_BROWSER_TITLE = "{TITLE}"', source)
        self.assertIn(f"<title>{TITLE}</title>", index)
        self.assertIn(f"<meta property='og:title' content='{TITLE}'>", index)
        self.assertIn(f"<meta name='twitter:title' content='{TITLE}'>", index)
        self.assertIn(f"<meta property='og:image:alt' content='{TITLE}'>", index)

    def test_admin_and_ops_titles_are_synchronized(self) -> None:
        for path in ADMIN_TITLE_FILES:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(f"<title>{TITLE}</title>", path.read_text(encoding="utf-8"))

        blog_admin = (ROOT / "site" / "static" / "admin" / "blog.html").read_text(encoding="utf-8")
        self.assertIn(f'document.title = "{TITLE}";', blog_admin)

    def test_short_brand_name_uses_aiclimb(self) -> None:
        index = (ROOT / "site" / "dist" / "index.html").read_text(encoding="utf-8")

        self.assertIn("<meta name='application-name' content='AIClimb'>", index)
        self.assertIn("<meta name='apple-mobile-web-app-title' content='AIClimb'>", index)
        self.assertIn("<meta property='og:site_name' content='AIClimb'>", index)


if __name__ == "__main__":
    unittest.main()

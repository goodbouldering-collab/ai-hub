import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SITE_BUILDER_PATH = ROOT / "site" / "build_site.py"
PORTAL_PATH = ROOT / "site" / "build_portal.py"
NAVIGATION_PATH = ROOT / "site" / "public_navigation.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AiAppSitePagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site_builder = load_module("site_builder_ai_app_site_under_test", SITE_BUILDER_PATH)
        cls.portal = load_module("portal_ai_app_site_under_test", PORTAL_PATH)
        cls.navigation = load_module("navigation_ai_app_site_under_test", NAVIGATION_PATH)

    def test_builder_creates_the_main_service_page_and_five_solution_pages(self):
        expected_pages = {
            "ai-app-site": ("その仕事、", "サイトにやらせませんか？"),
            "ai-estimate": "AI見積もり",
            "ai-inquiry": "AI問い合わせ",
            "ai-reservation": "AI予約受付",
            "ai-shift": "AIシフト",
            "ai-blog": "AIブログ",
        }
        original_dist = self.site_builder.DIST
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self.site_builder.DIST = Path(tmp)
                build_pages = getattr(self.site_builder, "build_ai_app_site_pages", None)
                if callable(build_pages):
                    build_pages()

                for route, customer_question in expected_pages.items():
                    target = Path(tmp) / route / "index.html"
                    rendered = target.read_text(encoding="utf-8") if target.exists() else ""
                    questions = (customer_question,) if isinstance(customer_question, str) else customer_question
                    for question in questions:
                        self.assertIn(question, rendered)
                    self.assertIn("無料相談", rendered)
                    self.assertIn(self.portal.DIAGNOSIS_FREE_CONSULT_BOOK_URL, rendered)

                flagship = Path(tmp) / "ai-app-site" / "index.html"
                flagship_html = flagship.read_text(encoding="utf-8") if flagship.exists() else ""
                self.assertIn("AIアプリサイト Lite", flagship_html)
                self.assertIn("無料", flagship_html)
                self.assertIn("11,000円〜", flagship_html)
                self.assertIn("99,000円〜", flagship_html)
                self.assertIn("198,000円〜", flagship_html)
                self.assertIn("500,000円〜", flagship_html)
                self.assertIn("AIアプリサイト保守・改善", flagship_html)
                self.assertIn("9,800円〜/月", flagship_html)
        finally:
            self.site_builder.DIST = original_dist

    def test_builder_adds_canonical_service_routes_to_the_sitemap(self):
        original_dist = self.site_builder.DIST
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self.site_builder.DIST = Path(tmp)
                (Path(tmp) / "index.html").write_text("home", encoding="utf-8")
                build_pages = getattr(self.site_builder, "build_ai_app_site_pages", None)
                if callable(build_pages):
                    build_pages()
                self.site_builder.build_sitemap_and_robots()
                sitemap = (Path(tmp) / "sitemap.xml").read_text(encoding="utf-8")
                for route in ("ai-app-site", "ai-estimate", "ai-inquiry", "ai-reservation", "ai-shift", "ai-blog"):
                    self.assertIn(f"<loc>https://aiclimb.vercel.app/{route}/</loc>", sitemap)
                    self.assertNotIn(f"/{route}/index.html</loc>", sitemap)
        finally:
            self.site_builder.DIST = original_dist

    def test_homepage_leads_with_the_problem_solving_offer_and_free_consultation(self):
        page = self.portal.render_portal([], [])

        self.assertIn("AI相談 × AIアプリサイト", page)
        self.assertIn("相談だけで終わらない。", page)
        self.assertIn("AIで、仕事の仕組みまでつくる。", page)
        self.assertIn("その仕事、サイトにやらせませんか？", page)
        self.assertIn("href='/ai-app-site/'", page)
        self.assertIn(self.portal.DIAGNOSIS_FREE_CONSULT_BOOK_URL, page)
        self.assertLess(page.index("<section class='focus-hero'"), page.index("id='ai-app-site'"))
        self.assertLess(page.index("id='ai-app-site'"), page.index("<section class='readiness-guide readiness-guide--compact'"))

    def test_shared_navigation_gives_the_service_its_own_public_entry(self):
        desktop = self.navigation.render_desktop_navigation(current_id="app-site")
        mobile = self.navigation.render_mobile_navigation(current_id="app-site")

        self.assertIn("href='/ai-app-site/'", desktop)
        self.assertIn(">AIアプリサイト</a>", desktop)
        self.assertIn("aria-current='page'", desktop)
        self.assertIn("href='/ai-app-site/'", mobile)
        self.assertIn(">AIアプリサイト</span>", mobile)

    def test_free_consultation_sheet_is_built_as_a_public_material(self):
        original_dist = self.site_builder.DIST
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self.site_builder.DIST = Path(tmp)
                self.site_builder.build_lectures()
                target = Path(tmp) / "lectures" / "2026-08-ai-app-site-consult-sheet.html"
                rendered = target.read_text(encoding="utf-8") if target.exists() else ""
                self.assertIn("AIアプリサイト無料相談シート", rendered)
                self.assertIn("いちばん時間がかかる作業", rendered)
                self.assertIn("小さく作る", rendered)
        finally:
            self.site_builder.DIST = original_dist

    def test_consultation_sheet_is_not_ignored_from_static_deployment(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        public_sheet = ROOT / "site" / "dist" / "lectures" / "2026-08-ai-app-site-consult-sheet.html"

        self.assertIn("!site/dist/lectures/", gitignore)
        self.assertIn("site/dist/lectures/*", gitignore)
        self.assertIn("!site/dist/lectures/2026-08-ai-app-site-consult-sheet.html", gitignore)
        self.assertTrue(public_sheet.exists())

    def test_homepage_distinguishes_app_site_support_from_six_month_project(self):
        page = self.portal.render_portal([], [])

        self.assertIn("AIアプリサイト保守・改善", page)
        self.assertIn("9,800円〜/月", page)
        self.assertIn("AI導入伴走支援（6ヶ月プロジェクト）", page)
        self.assertIn("月額10万円", page)
        self.assertIn("6ヶ月", page)
        self.assertIn("無料相談で、仕事を整理する", page)
        self.assertIn(self.portal.DIAGNOSIS_FREE_CONSULT_BOOK_URL, page)


if __name__ == "__main__":
    unittest.main()

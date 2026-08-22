import importlib.util
from pathlib import Path
import tempfile
import unittest

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


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


def launch_chromium(playwright):
    try:
        return playwright.chromium.launch()
    except PlaywrightError as default_error:
        for executable in (
            Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
            Path("C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"),
            Path("/usr/bin/google-chrome"),
            Path("/usr/bin/chromium"),
            Path("/usr/bin/chromium-browser"),
            Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"),
        ):
            if executable.exists():
                return playwright.chromium.launch(executable_path=str(executable))
        raise default_error


class AiAppSitePagesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.site_builder = load_module("site_builder_ai_app_site_under_test", SITE_BUILDER_PATH)
        cls.portal = load_module("portal_ai_app_site_under_test", PORTAL_PATH)
        cls.navigation = load_module("navigation_ai_app_site_under_test", NAVIGATION_PATH)

    def test_builder_creates_the_main_service_page_and_five_solution_pages(self):
        expected_pages = {
            "ai-app-site": ("相談だけで終わらない。", "AIで、仕事の仕組みまでつくる。"),
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
                    self.assertIn("99,000円", rendered)
                    self.assertIn(self.portal.DIAGNOSIS_FREE_CONSULT_BOOK_URL, rendered)

                flagship = Path(tmp) / "ai-app-site" / "index.html"
                flagship_html = flagship.read_text(encoding="utf-8") if flagship.exists() else ""
                self.assertIn("AIアプリサイト Lite", flagship_html)
                self.assertIn("99,000円〜", flagship_html)
                self.assertIn('"@type": "Service"', flagship_html)
                self.assertNotIn("AI APP SITE · SELF BUILD", flagship_html)
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

    def test_homepage_separates_ordered_service_from_selfbuild_course(self):
        page = self.portal.render_portal([], [])
        section_id = page.index("id='ai-app-site'")
        section_start = page.rfind("<section", 0, section_id)
        section_end = page.index("</section>", section_id) + len("</section>")
        app_site_guide = page[section_start:section_end]

        self.assertIn("AIエージェントで", page)
        self.assertIn("できることを100倍に", page)
        self.assertIn("迷ったら60秒診断をはじめる", page)
        self.assertNotIn("相談だけで終わらない。", page)
        self.assertNotIn("AIで、仕事の仕組みまでつくる。", page)
        self.assertIn("AI APP SITE · DONE FOR YOU", app_site_guide)
        self.assertIn(
            "<section class='readiness-guide readiness-guide--compact home-app-site-guide' id='ai-app-site'",
            app_site_guide,
        )
        self.assertIn("AIアプリが動くサイトを、まるごと制作。", app_site_guide)
        self.assertIn("AIアプリサイト制作", app_site_guide)
        self.assertIn("99,000円〜", app_site_guide)
        self.assertIn("ホームページ＋AI機能1つ", app_site_guide)
        self.assertIn("AIアプリを、すぐ使える形でサイト内に組み込み", app_site_guide)
        self.assertIn("別アプリを増やさず、新規制作・リニューアル・移行まで対応", app_site_guide)
        self.assertIn("社内で保守・改善・バージョンアップ", app_site_guide)
        self.assertIn("必要な部分だけこちらへ任せる", app_site_guide)
        self.assertIn("自由に選べます", app_site_guide)
        self.assertIn("class='readiness-guide__inner'", app_site_guide)
        self.assertIn("class='readiness-guide__intro'", app_site_guide)
        self.assertIn(
            "class='readiness-guide__questions home-app-site-capabilities'",
            app_site_guide,
        )
        self.assertIn("class='readiness-guide__actions'", app_site_guide)
        self.assertEqual(5, app_site_guide.count("<span aria-hidden='true'>?</span>"))
        self.assertEqual(5, app_site_guide.count("class='home-app-site-card'"))
        for feature in ("AI見積もり", "AI問い合わせ", "AI予約受付", "AIシフト", "AIブログ"):
            self.assertIn(f"<strong>{feature}</strong>", app_site_guide)
        self.assertNotIn("見積もり → 自動作成", app_site_guide)
        self.assertNotIn("できることを見る", app_site_guide)
        self.assertNotIn("home-app-site-path", app_site_guide)
        self.assertIn("AIアプリサイト制作を無料相談する", app_site_guide)
        self.assertIn(self.portal.DIAGNOSIS_FREE_CONSULT_BOOK_URL, app_site_guide)
        self.assertNotIn("SELF BUILD", app_site_guide)
        self.assertNotIn("AIアプリサイト自作", app_site_guide)
        self.assertNotIn(self.portal.AI_APP_SELFBUILD_BOOK_URL, app_site_guide)
        self.assertIn("<h3>AI自作講習</h3>", page)
        self.assertIn("制作を任せたい方は、上の「AIアプリサイト制作」へ。", page)
        self.assertIn(self.portal.AI_APP_SELFBUILD_BOOK_URL, page)
        self.assertLess(page.index("<section class='focus-hero'"), page.index("id='ai-app-site'"))
        self.assertLess(page.index("id='ai-app-site'"), page.index("<section class='readiness-guide readiness-guide--compact'"))

    def test_homepage_mobile_feature_links_form_one_vertical_column(self):
        rendered = self.portal.render_portal([], [])

        with sync_playwright() as playwright:
            browser = launch_chromium(playwright)
            try:
                for width in (604, 390):
                    with self.subTest(width=width):
                        page = browser.new_page(viewport={"width": width, "height": 900})
                        try:
                            page.set_content(rendered)
                            cards = page.locator(".home-app-site-card")
                            boxes = [cards.nth(index).bounding_box() for index in range(cards.count())]

                            self.assertEqual(5, len(boxes))
                            self.assertTrue(all(box is not None for box in boxes))
                            self.assertLess(max(box["x"] for box in boxes) - min(box["x"] for box in boxes), 1)
                            self.assertTrue(
                                all(box["height"] >= 44 for box in boxes),
                                "5機能はリンク自体に44px以上のタップ領域を持つ",
                            )
                            for index, box in enumerate(boxes):
                                row_box = cards.nth(index).locator("xpath=..").bounding_box()
                                self.assertIsNotNone(row_box)
                                self.assertLessEqual(abs(box["width"] - row_box["width"]), 2)
                                self.assertLessEqual(abs(box["height"] - row_box["height"]), 2)
                            self.assertTrue(
                                all(upper["y"] < lower["y"] for upper, lower in zip(boxes, boxes[1:]))
                            )
                        finally:
                            page.close()
            finally:
                browser.close()

    def test_shared_navigation_gives_the_service_its_own_public_entry(self):
        desktop = self.navigation.render_desktop_navigation(current_id="app-site")
        mobile = self.navigation.render_mobile_navigation(current_id="app-site")

        self.assertIn("href='/ai-app-site/'", desktop)
        self.assertIn(">AIアプリサイト</a>", desktop)
        self.assertIn("aria-current='page'", desktop)
        self.assertIn("href='/ai-app-site/'", mobile)
        self.assertIn(">AIアプリサイト</span>", mobile)

    def test_selfbuild_preparation_sheet_is_built_as_a_public_material(self):
        source = (ROOT / "content" / "lectures" / "2026-08-ai-app-site-consult-sheet.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("listed: false", source)

        original_dist = self.site_builder.DIST
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self.site_builder.DIST = Path(tmp)
                self.site_builder.build_lectures()
                target = Path(tmp) / "lectures" / "2026-08-ai-app-site-consult-sheet.html"
                rendered = target.read_text(encoding="utf-8") if target.exists() else ""
                self.assertIn("AIアプリサイト自作講習・相談 準備シート", rendered)
                self.assertIn("いちばん時間がかかる作業", rendered)
                self.assertIn("自分で試作する", rendered)
        finally:
            self.site_builder.DIST = original_dist

    def test_consultation_sheet_is_not_ignored_from_static_deployment(self):
        gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        public_sheet = ROOT / "site" / "dist" / "lectures" / "2026-08-ai-app-site-consult-sheet.html"

        self.assertIn("!site/dist/lectures/", gitignore)
        self.assertIn("site/dist/lectures/*", gitignore)
        self.assertIn("!site/dist/lectures/2026-08-ai-app-site-consult-sheet.html", gitignore)
        self.assertTrue(public_sheet.exists())

    def test_paid_consultation_is_merged_into_the_selfbuild_course(self):
        page = self.portal.render_portal([], [])

        self.assertIn("AI伴走支援", page)
        self.assertIn("月額88,000円", page)
        self.assertIn("6ヶ月", page)
        self.assertIn("AI自作講習を予約する（120分・11,000円）", page)
        self.assertNotIn("AI個別相談", page)
        self.assertIn(self.portal.AI_APP_SELFBUILD_BOOK_URL, page)
        self.assertIn(self.portal.MONTHLY_SUPPORT_BOOK_URL, page)


if __name__ == "__main__":
    unittest.main()

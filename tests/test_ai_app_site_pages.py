import importlib.util
from pathlib import Path
import re
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
                self.assertIn("AIアプリサイト制作を無料相談する", flagship_html)
                self.assertIn(self.portal.DIAGNOSIS_FREE_CONSULT_BOOK_URL, flagship_html)
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

    def test_homepage_places_app_site_service_last_in_the_shared_course_card_grid(self):
        page = self.portal.render_portal([], [])
        cards = re.findall(
            r"<article class='compact-course-card offer-card'[^>]*>.*?</article>",
            page,
            re.DOTALL,
        )
        app_site_card = next(card for card in cards if "id='ai-app-site'" in card)

        self.assertEqual(6, len(cards))
        self.assertEqual(app_site_card, cards[-1])
        self.assertNotIn("home-app-site-guide", page)
        self.assertNotIn("AIアプリサイト制作を無料相談する", page)
        self.assertNotIn("相談だけで終わらない。", page)
        self.assertNotIn("AIで、仕事の仕組みまでつくる。", page)
        self.assertIn(
            "<span class='offer-role-badge'>代行</span>"
            "<span class='offer-role-note'>AIアプリサイト</span>",
            app_site_card,
        )
        self.assertNotIn("DONE FOR YOU", app_site_card)
        self.assertIn(
            "<div class='compact-course-heading'><h3 id='home-app-site-title'>AIアプリサイト制作</h3>"
            "<span class='offer-audience'",
            app_site_card,
        )
        self.assertIn(
            "<span class='offer-audience-label'>制作方法</span><strong>代行</strong>",
            app_site_card,
        )
        self.assertIn("99,000円〜", app_site_card)
        self.assertIn("ホームページ＋AI機能1つ", app_site_card)
        self.assertIn("AIアプリを、すぐ使える形でサイト内に組み込み", app_site_card)
        self.assertIn("別アプリを増やさず、新規制作・リニューアル・移行まで対応", app_site_card)
        self.assertIn("社内で保守・改善・バージョンアップ", app_site_card)
        self.assertIn("必要な部分だけこちらへ任せる", app_site_card)
        self.assertIn("自由に選べます", app_site_card)
        self.assertIn("代行作成で、自由に瞬時に変更できるAIサイトへ移行できます。", app_site_card)
        self.assertIn("class='home-app-site-capabilities'", app_site_card)
        self.assertEqual(5, app_site_card.count("class='home-app-site-card'"))
        for feature in ("AI見積もり", "AI問い合わせ", "AI予約受付", "AIシフト", "AIブログ"):
            self.assertIn(f"<strong>{feature}</strong>", app_site_card)
        self.assertIn("href='/ai-app-site/'", app_site_card)
        self.assertIn("制作内容・料金を見る", app_site_card)
        self.assertNotIn(self.portal.DIAGNOSIS_FREE_CONSULT_BOOK_URL, app_site_card)
        self.assertNotIn("SELF BUILD", app_site_card)
        self.assertNotIn("AIアプリサイト自作", app_site_card)
        self.assertNotIn(self.portal.AI_CODING_BOOK_URL, app_site_card)
        self.assertIn("<h3>AIコーディング講習</h3>", page)
        self.assertIn("制作を任せるなら「AIアプリサイト制作」", page)
        self.assertIn(self.portal.AI_CODING_BOOK_URL, page)
        self.assertLess(page.index("<section class='focus-hero'"), page.index("id='ai-app-site'"))
        self.assertLess(page.index("id='packages'"), page.index("id='ai-app-site'"))
        self.assertLess(page.index("id='seven-day-courses'"), page.index("id='ai-app-site'"))
        self.assertLess(page.index("id='ai-app-site'"), page.index("class='course-venue-common'"))
        self.assertLess(page.index("id='ai-app-site'"), page.index("id='lectures'"))

    def test_homepage_mobile_feature_links_use_two_columns_with_a_balanced_last_row(self):
        rendered = self.portal.render_portal([], [])

        with sync_playwright() as playwright:
            browser = launch_chromium(playwright)
            try:
                for width in (604, 390, 320, 305):
                    with self.subTest(width=width):
                        page = browser.new_page(viewport={"width": width, "height": 900})
                        try:
                            page.set_content(rendered)
                            app_card = page.locator("#ai-app-site")
                            app_card.locator(
                                ".compact-course-details:not(.compact-course-testimonials)"
                            ).evaluate(
                                "element => { element.open = true; }"
                            )
                            feature_list = app_card.locator(".home-app-site-capabilities")
                            cards = app_card.locator(".home-app-site-card")
                            boxes = [cards.nth(index).bounding_box() for index in range(cards.count())]
                            list_box = feature_list.bounding_box()
                            first_title_line = page.locator(".focus-title-first").bounding_box()
                            second_title_line = page.locator(".focus-title-line").bounding_box()
                            app_title = page.locator("#home-app-site-title")
                            app_title_box = app_title.bounding_box()
                            app_card_box = app_card.bounding_box()

                            self.assertEqual(5, len(boxes))
                            self.assertTrue(all(box is not None for box in boxes))
                            self.assertIsNotNone(list_box)
                            self.assertIsNotNone(first_title_line)
                            self.assertIsNotNone(second_title_line)
                            self.assertIsNotNone(app_title_box)
                            self.assertIsNotNone(app_card_box)
                            self.assertEqual("AIアプリサイト制作", app_title.text_content())
                            self.assertLessEqual(
                                app_title.evaluate(
                                    "element => element.scrollWidth - element.clientWidth"
                                ),
                                1,
                                "サービス見出しを320pxでもカード内に収める",
                            )
                            self.assertLessEqual(
                                app_title_box["x"] + app_title_box["width"],
                                app_card_box["x"] + app_card_box["width"] + 1,
                                "サービス見出しをカードからはみ出させない",
                            )
                            self.assertLessEqual(
                                second_title_line["height"],
                                first_title_line["height"] * 1.35,
                                "ヒーローの青い見出しは最後の1文字だけを次行へ送らない",
                            )
                            self.assertLess(abs(boxes[0]["y"] - boxes[1]["y"]), 2)
                            self.assertLess(abs(boxes[2]["y"] - boxes[3]["y"]), 2)
                            self.assertGreater(abs(boxes[0]["x"] - boxes[1]["x"]), 10)
                            self.assertGreater(abs(boxes[2]["x"] - boxes[3]["x"]), 10)
                            self.assertLess(boxes[0]["y"], boxes[2]["y"])
                            self.assertLess(boxes[2]["y"], boxes[4]["y"])
                            self.assertLessEqual(abs(boxes[4]["width"] - list_box["width"]), 2)
                            self.assertTrue(
                                all(box["height"] >= 44 for box in boxes),
                                "5機能はリンク自体に44px以上のタップ領域を持つ",
                            )
                            for index, box in enumerate(boxes):
                                row_box = cards.nth(index).locator("xpath=..").bounding_box()
                                self.assertIsNotNone(row_box)
                                self.assertLessEqual(abs(box["width"] - row_box["width"]), 2)
                                self.assertLessEqual(abs(box["height"] - row_box["height"]), 2)
                            self.assertLessEqual(
                                page.evaluate(
                                    "document.documentElement.scrollWidth - "
                                    "document.documentElement.clientWidth"
                                ),
                                1,
                                "2列化してもモバイルで横スクロールを出さない",
                            )
                        finally:
                            page.close()
            finally:
                browser.close()

    def test_homepage_service_title_fits_with_a_reserved_scrollbar_at_320px(self):
        rendered = self.portal.render_portal([], [])

        with sync_playwright() as playwright:
            browser = launch_chromium(playwright)
            try:
                page = browser.new_page(viewport={"width": 320, "height": 900})
                try:
                    page.set_content(rendered)
                    page.evaluate(
                        "document.body.style.width = 'calc(100% - 15px)'"
                    )
                    title_line = page.locator("#home-app-site-title")

                    self.assertEqual(320, page.evaluate("window.innerWidth"))
                    self.assertAlmostEqual(
                        305,
                        page.locator("body").bounding_box()["width"],
                        delta=1,
                    )
                    self.assertLessEqual(
                        title_line.evaluate(
                            "element => element.scrollWidth - element.clientWidth"
                        ),
                        1,
                        "スクロールバーを差し引いた有効幅でも見出しを切らない",
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

    def test_coding_course_preparation_sheet_is_built_as_a_public_material(self):
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
                self.assertIn("AIコーディング講習 準備シート", rendered)
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

    def test_individual_and_coding_courses_are_separate_paid_offers(self):
        page = self.portal.render_portal([], [])

        self.assertIn("AI伴走支援", page)
        self.assertIn("月額88,000円", page)
        self.assertIn("6ヶ月", page)
        self.assertIn("個別講習を予約 →", page)
        self.assertIn("AIコーディングを予約 →", page)
        self.assertIn(self.portal.INDIVIDUAL_COURSE_BOOK_URL, page)
        self.assertIn(self.portal.AI_CODING_BOOK_URL, page)
        self.assertIn(self.portal.MONTHLY_SUPPORT_BOOK_URL, page)


if __name__ == "__main__":
    unittest.main()

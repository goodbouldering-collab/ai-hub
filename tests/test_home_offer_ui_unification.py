import importlib.util
from pathlib import Path
import re
import unittest

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"


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


class HomeOfferUiUnificationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.portal = load_module("portal_home_offer_ui_under_test", PORTAL_PATH)
        cls.home = cls.portal.render_portal([], [])

    def test_service_and_diagnostics_share_one_guide_structure(self):
        expected_sections = (
            ("ai-app-site", "home-app-site-guide"),
            ("readiness-guide-title", "readiness-guide--compact"),
            ("seo-llmo-guide-title", "seo-llmo-guide"),
        )
        for guide_id, modifier in expected_sections:
            with self.subTest(guide_id=guide_id):
                id_index = self.home.index(f"id='{guide_id}'")
                section_start = self.home.rfind("<section", 0, id_index)
                section_end = self.home.index("</section>", id_index)
                section = self.home[section_start:section_end]

                self.assertIn("readiness-guide readiness-guide--compact", section)
                self.assertIn(modifier, section)
                self.assertIn("class='readiness-guide__inner'", section)
                self.assertIn("class='readiness-guide__intro'", section)
                self.assertIn("class='readiness-guide__questions", section)
                self.assertIn("class='readiness-guide__actions'", section)
                self.assertIn("class='readiness-guide__cta", section)

        self.assertEqual(3, self.home.count("class='readiness-guide__inner'"))
        self.assertEqual(3, self.home.count("class='readiness-guide__intro'"))
        self.assertEqual(3, self.home.count("class='readiness-guide__questions"))
        self.assertEqual(3, self.home.count("class='readiness-guide__actions'"))
        self.assertGreaterEqual(self.home.count("offer-panel"), 3)
        self.assertIn("<span class='offer-role-badge'>代行</span>", self.home)
        self.assertEqual(2, self.home.count("<span class='offer-role-badge'>診断</span>"))
        self.assertEqual(3, self.home.count("<span class='offer-role-badge'>学ぶ</span>"))
        self.assertEqual(3, self.home.count("class='compact-course-card offer-card'"))
        self.assertGreaterEqual(self.home.count("offer-action"), 5)

        css = self.portal.FOCUSED_PORTAL_CSS
        self.assertRegex(css, r"\.offer-panel\s*\{[^}]*border-radius:")
        self.assertRegex(css, r"\.offer-role-badge\s*\{[^}]*border-radius:\s*999px")
        self.assertRegex(css, r"\.offer-action\s*\{[^}]*min-height:\s*46px")

    def test_three_guides_share_grid_and_question_row_format(self):
        with sync_playwright() as playwright:
            browser = launch_chromium(playwright)
            try:
                desktop = browser.new_page(viewport={"width": 1280, "height": 1000})
                desktop.set_content(self.home)
                guide_inners = desktop.locator(
                    "#ai-app-site .readiness-guide__inner, "
                    "section[aria-labelledby='readiness-guide-title'] .readiness-guide__inner, "
                    "section[aria-labelledby='seo-llmo-guide-title'] .readiness-guide__inner"
                )
                self.assertEqual(3, guide_inners.count())
                grid_templates = [
                    guide_inners.nth(index).evaluate(
                        "element => getComputedStyle(element).gridTemplateColumns"
                    )
                    for index in range(guide_inners.count())
                ]
                self.assertEqual(1, len(set(grid_templates)))

                question_rows = desktop.locator(
                    "#ai-app-site .readiness-guide__questions li, "
                    "section[aria-labelledby='readiness-guide-title'] .readiness-guide__questions li, "
                    "section[aria-labelledby='seo-llmo-guide-title'] .readiness-guide__questions li"
                )
                self.assertEqual(11, question_rows.count())
                for index in range(question_rows.count()):
                    row = question_rows.nth(index)
                    self.assertEqual("grid", row.evaluate("element => getComputedStyle(element).display"))
                    marker = row.locator(":scope > span").first
                    marker_box = marker.bounding_box()
                    self.assertIsNotNone(marker_box)
                    self.assertLess(abs(marker_box["width"] - marker_box["height"]), 1)
                    self.assertEqual("?", marker.text_content().strip())
                desktop.close()

                mobile = browser.new_page(viewport={"width": 375, "height": 1000})
                mobile.set_content(self.home)
                mobile_inners = mobile.locator(".readiness-guide__inner")
                self.assertEqual(3, mobile_inners.count())
                for index in range(mobile_inners.count()):
                    inner_box = mobile_inners.nth(index).bounding_box()
                    panel_box = mobile_inners.nth(index).locator("xpath=..").bounding_box()
                    self.assertIsNotNone(inner_box)
                    self.assertIsNotNone(panel_box)
                    self.assertEqual(
                        1,
                        mobile_inners.nth(index).evaluate(
                            "element => getComputedStyle(element).gridTemplateColumns.split(' ').length"
                        ),
                    )
                    self.assertLessEqual(
                        inner_box["x"] + inner_box["width"],
                        panel_box["x"] + panel_box["width"] + 1,
                        "共通ガイドの内容はiPhone幅でもカード右端から張り出さない",
                    )
                    columns = mobile_inners.nth(index).locator(":scope > *")
                    for column_index in range(columns.count()):
                        column_box = columns.nth(column_index).bounding_box()
                        self.assertIsNotNone(column_box)
                        self.assertLessEqual(
                            column_box["x"] + column_box["width"],
                            panel_box["x"] + panel_box["width"] + 1,
                            "共通ガイドの各列はiPhone幅でもカード右端から張り出さない",
                        )
                self.assertLessEqual(
                    mobile.evaluate(
                        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
                    ),
                    1,
                )
                mobile.close()
            finally:
                browser.close()

    def test_course_cards_show_the_requested_participation_scale(self):
        cards = re.findall(
            r"<article class='compact-course-card offer-card'.*?</article>",
            self.home,
            re.DOTALL,
        )
        self.assertEqual(3, len(cards))

        expected = (
            ("AIエージェント講習", "少数"),
            ("AI自作講習", "個別"),
            ("AI伴走支援", "組織"),
        )
        for card, (title, scale) in zip(cards, expected, strict=True):
            with self.subTest(title=title):
                self.assertIn(
                    f"<div class='compact-course-heading'><h3>{title}</h3>"
                    "<span class='offer-audience'",
                    card,
                )
                self.assertIn("<span class='offer-audience-label'>受講人数</span>", card)
                self.assertIn(f"<strong>{scale}</strong>", card)
                self.assertLess(card.index("offer-role-row"), card.index("compact-course-visual"))
                self.assertLess(card.index("compact-course-visual"), card.index(f"<h3>{title}</h3>"))
                self.assertLess(card.index(f"<h3>{title}</h3>"), card.index("offer-audience"))

        support_card = cards[2]
        self.assertIn(
            "組織がAIアプリサイトを自作・改善・運用できるまで学ぶ6ヶ月",
            support_card,
        )
        self.assertIn("上のAIアプリサイト制作", support_card)

    def test_three_courses_are_equal_columns_on_desktop_and_stack_on_mobile(self):
        with sync_playwright() as playwright:
            browser = launch_chromium(playwright)
            try:
                desktop = browser.new_page(viewport={"width": 1280, "height": 900})
                desktop.set_content(self.home)
                desktop_cards = desktop.locator(".compact-course-card")
                desktop_boxes = [
                    desktop_cards.nth(index).bounding_box()
                    for index in range(desktop_cards.count())
                ]
                self.assertEqual(3, len(desktop_boxes))
                self.assertTrue(all(box is not None for box in desktop_boxes))
                self.assertLess(
                    max(box["width"] for box in desktop_boxes)
                    - min(box["width"] for box in desktop_boxes),
                    1,
                )
                self.assertLess(
                    max(box["y"] for box in desktop_boxes)
                    - min(box["y"] for box in desktop_boxes),
                    1,
                )
                self.assertLessEqual(
                    desktop.evaluate(
                        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
                    ),
                    1,
                )
                for index in range(desktop_cards.count()):
                    self.assertGreaterEqual(
                        desktop_cards.nth(index)
                        .locator(".compact-course-action")
                        .evaluate("element => parseFloat(getComputedStyle(element).minHeight)"),
                        46,
                    )
                desktop.close()

                mobile = browser.new_page(viewport={"width": 390, "height": 900})
                mobile.set_content(self.home)
                mobile_cards = mobile.locator(".compact-course-card")
                mobile_boxes = [
                    mobile_cards.nth(index).bounding_box()
                    for index in range(mobile_cards.count())
                ]
                self.assertEqual(3, len(mobile_boxes))
                self.assertTrue(all(box is not None for box in mobile_boxes))
                self.assertLess(
                    max(box["x"] for box in mobile_boxes)
                    - min(box["x"] for box in mobile_boxes),
                    1,
                )
                self.assertTrue(
                    all(upper["y"] < lower["y"] for upper, lower in zip(mobile_boxes, mobile_boxes[1:]))
                )
                self.assertLessEqual(
                    mobile.evaluate(
                        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
                    ),
                    1,
                )
                mobile.close()

                narrow = browser.new_page(viewport={"width": 320, "height": 900})
                narrow.set_content(self.home)
                self.assertLessEqual(
                    narrow.evaluate(
                        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
                    ),
                    1,
                )
                narrow_headings = narrow.locator(".compact-course-heading")
                self.assertEqual(3, narrow_headings.count())
                for index in range(narrow_headings.count()):
                    self.assertEqual(
                        "nowrap",
                        narrow_headings.nth(index).evaluate(
                            "element => getComputedStyle(element).flexWrap"
                        ),
                    )
                    title_box = narrow_headings.nth(index).locator("h3").bounding_box()
                    audience_box = narrow_headings.nth(index).locator(".offer-audience").bounding_box()
                    self.assertIsNotNone(title_box)
                    self.assertIsNotNone(audience_box)
                    self.assertLess(
                        abs(title_box["y"] - audience_box["y"]),
                        8,
                        "受講人数は320px幅でも講習名のすぐ横に表示する",
                    )
                narrow.close()
            finally:
                browser.close()

    def test_offer_headings_do_not_leave_one_character_on_a_new_desktop_line(self):
        self.assertIn(
            "aria-label='AIアプリが動くサイトを、まるごと制作。'",
            self.home,
        )
        self.assertIn(
            "<span class='home-app-site-title-line'>AIアプリが動く<br class='home-app-site-title-narrow-break'>サイトを、</span>",
            self.home,
        )
        self.assertIn(
            "<span class='home-app-site-title-line'>まるごと制作。</span>",
            self.home,
        )

        with sync_playwright() as playwright:
            browser = launch_chromium(playwright)
            try:
                page = browser.new_page(viewport={"width": 1440, "height": 1000})
                page.set_content(self.home)

                service_lines = page.locator(
                    "#home-app-site-title .home-app-site-title-line"
                )
                self.assertEqual(2, service_lines.count())
                for index in range(service_lines.count()):
                    self.assertEqual(
                        1,
                        service_lines.nth(index).evaluate(
                            """element => {
                              const range = document.createRange();
                              range.selectNodeContents(element);
                              return new Set(
                                [...range.getClientRects()]
                                  .filter(rect => rect.width > 0)
                                  .map(rect => Math.round(rect.top))
                              ).size;
                            }"""
                        ),
                    )

                for selector in ("#readiness-guide-title", "#seo-llmo-guide-title"):
                    with self.subTest(selector=selector):
                        line_count = page.locator(selector).evaluate(
                            """element => {
                              const range = document.createRange();
                              range.selectNodeContents(element);
                              return new Set(
                                [...range.getClientRects()]
                                  .filter(rect => rect.width > 0)
                                  .map(rect => Math.round(rect.top))
                              ).size;
                            }"""
                        )
                        self.assertEqual(1, line_count)
                page.close()

                narrow = browser.new_page(viewport={"width": 320, "height": 900})
                narrow.set_content(self.home)
                narrow_line_widths = narrow.locator("#home-app-site-title").evaluate(
                    """element => {
                      const range = document.createRange();
                      range.selectNodeContents(element);
                      return [...range.getClientRects()]
                        .filter(rect => rect.width > 0)
                        .map(rect => rect.width);
                    }"""
                )
                narrow_font_size = narrow.locator("#home-app-site-title").evaluate(
                    "element => parseFloat(getComputedStyle(element).fontSize)"
                )
                self.assertTrue(narrow_line_widths)
                self.assertGreaterEqual(min(narrow_line_widths), narrow_font_size * 2.5)
                narrow.close()
            finally:
                browser.close()


if __name__ == "__main__":
    unittest.main()

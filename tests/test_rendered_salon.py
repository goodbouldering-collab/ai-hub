from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"


class RenderedSalonTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_square_monthly_salon_copy_and_private_line_boundary(self) -> None:
        self.assertIn("月額2,200円（税込）", self.html)
        self.assertIn("毎月自動更新", self.html)
        self.assertIn("AIオンラインサロン｜近日開始", self.html)
        self.assertIn("現在は仮運用中", self.html)
        self.assertIn("Squareで決済して仮運用に参加", self.html)
        self.assertEqual(self.html.count("action='/api/square/ai-salon-checkout'"), 1)
        self.assertNotIn("/api/stripe/ai-salon", self.html)
        self.assertNotRegex(self.html, r"https://(?:line\.me|lin\.ee)/")
        self.assertNotIn("LINE参加パスワード", self.html)

    def test_salon_and_app_site_are_complete_last_cards_before_the_venue_map(self) -> None:
        cards = re.findall(
            r"<article class='compact-course-card[^']*'.*?</article>",
            self.html,
            re.DOTALL,
        )
        self.assertEqual(len(cards), 6)
        salon_cards = [card for card in cards if "AIオンラインサロン｜近日開始" in card]
        app_site_cards = [card for card in cards if "id='ai-app-site'" in card]
        self.assertEqual(len(salon_cards), 1)
        self.assertEqual(len(app_site_cards), 1)
        self.assertEqual(cards[-2], salon_cards[0])
        self.assertEqual(cards[-1], app_site_cards[0])
        salon = salon_cards[0]
        self.assertIn(
            "<p>正式開始に向けて仮運用中です。Square決済後、毎週火曜21時のLINEライブトークへご案内します。</p>",
            salon,
        )
        self.assertNotIn("登録中の方にはテスト運用へご協力いただいています", salon)
        self.assertIn("class='course-menu-unified'", self.html)
        self.assertIn("aria-label='講習・相談・制作の全6メニュー'", self.html)
        self.assertNotIn("course-menu-unified-head", self.html)
        self.assertNotIn("上の4カードと下のオンラインサロンから選べます", self.html)
        self.assertRegex(self.html, r"class='course-menu-unified'[^>]*>\s*<div class='compact-course-grid'")
        self.assertIn("class='compact-course-card offer-card' id='seven-day-courses'", self.html)
        self.assertIn("class='offer-role-row offer-role-row--course'", salon)
        self.assertIn("class='compact-course-visual'", salon)
        self.assertIn("class='compact-course-heading'", salon)
        self.assertIn("class='offer-audience'", salon)
        self.assertIn("class='compact-course-meta'", salon)
        self.assertIn("class='compact-course-details'", salon)
        self.assertIn("class='compact-course-checkout'", salon)
        self.assertIn("class='offer-action compact-course-action'", salon)
        self.assertIn("class='compact-course-material-row'", salon)
        self.assertNotIn("compact-course-card--salon", salon)
        self.assertNotIn("salon-panel", salon)
        self.assertNotIn("salon-card-overview", salon)
        self.assertNotIn("salon-main-visual", salon)
        self.assertNotIn("salon-value-list", salon)
        visual = salon.index("class='compact-course-visual'")
        title = salon.index("id='salon-title'", visual)
        details = salon.index("class='compact-course-details'", title)
        testimonial = salon.index("compact-course-testimonials", details)
        checkout = salon.index("class='compact-course-checkout'", testimonial)
        material = salon.index("class='compact-course-material-row'", checkout)
        self.assertLess(visual, title)
        self.assertLess(title, details)
        self.assertLess(details, testimonial)
        self.assertLess(testimonial, checkout)
        self.assertLess(checkout, material)
        self.assertNotIn(" open", salon[details:salon.index(">", details)])
        self.assertEqual(self.html.count("id='seven-day-courses'"), 1)
        salon_start = self.html.index("id='seven-day-courses'")
        salon_end = self.html.index("</article>", salon_start)
        app_site_start = self.html.index("id='ai-app-site'", salon_end)
        app_site_end = self.html.index("</article>", app_site_start)
        venue_map = self.html.index("class='course-venue-map'", app_site_end)
        self.assertLess(salon_start, salon_end)
        self.assertLess(salon_end, app_site_start)
        self.assertLess(app_site_start, app_site_end)
        self.assertLess(app_site_end, venue_map)
        self.assertIn("メリット・内容・参加方法を見る", self.html)
        self.assertIn(
            "class='compact-course-material' href='/lectures/2026-07-ai-online-salon-practice.html'",
            self.html,
        )
        self.assertIn("オンラインサロン受講資料を見る", self.html)
        self.assertIn("LINEライブ", self.html)
        self.assertIn("聞くだけOK", self.html)

    def test_course_menu_has_no_outer_visual_frame(self) -> None:
        declarations = re.findall(
            r"\.course-menu-unified\s*\{([^}]*)\}",
            self.html,
            re.DOTALL,
        )

        self.assertGreaterEqual(len(declarations), 1)
        for rule in declarations:
            for property_name in (
                "padding",
                "border",
                "border-radius",
                "background",
                "box-shadow",
            ):
                with self.subTest(property_name=property_name, rule=rule):
                    self.assertNotRegex(
                        rule,
                        rf"(?:^|\s){re.escape(property_name)}\s*:",
                    )

    def test_hero_and_menu_order(self) -> None:
        hero_start = self.html.index("class='focus-hero'")
        hero_end = self.html.index("</section>", hero_start)
        hero = self.html[hero_start:hero_end]
        self.assertIn("<small><strong>始めるなら今。</strong></small>", hero)
        self.assertNotIn("まだまだこれから！", hero)
        self.assertNotIn("<strong>5,500円から</strong>", hero)
        self.assertNotIn("<strong>相談5,500円/回</strong>", hero)
        self.assertNotIn("<strong>利用率6%</strong>", hero)
        self.assertIn("始めるなら今。", self.html)
        self.assertIn("hero-advantage-equation", self.html)
        nav = re.search(
            r"<nav class='site-nav'[^>]*>(.*?)</nav>",
            self.html,
            re.DOTALL,
        )
        self.assertIsNotNone(nav)
        assert nav is not None
        self.assertGreater(nav.group(1).rfind("サロン"), nav.group(1).rfind("個別相談"))

    def test_course_cards_stack_without_horizontal_flip(self) -> None:
        tablet = re.search(
            r"@media \(max-width:1100px\).*?"
            r"\.compact-course-grid\s*\{([^}]*)\}",
            self.html,
            re.DOTALL,
        )
        mobile = re.search(
            r"@media \(max-width:720px\).*?"
            r"\.compact-course-grid\s*\{([^}]*)\}",
            self.html,
            re.DOTALL,
        )
        self.assertIsNotNone(tablet)
        self.assertIsNotNone(mobile)
        assert tablet is not None
        assert mobile is not None
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", tablet.group(1))
        self.assertIn("align-items:start", tablet.group(1))
        self.assertIn("grid-template-columns:1fr", mobile.group(1))
        for declarations in (tablet.group(1), mobile.group(1)):
            self.assertNotIn("grid-auto-flow:column", declarations)
            self.assertNotIn("overflow-x:auto", declarations)
            self.assertNotIn("scroll-snap-type", declarations)

    def test_course_cards_have_no_recommendation_badge(self) -> None:
        self.assertNotIn("一番基本・おすすめ", self.html)
        self.assertNotIn("compact-course-recommend", self.html)


if __name__ == "__main__":
    unittest.main()

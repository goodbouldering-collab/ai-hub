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
        self.assertIn("Squareで決済して参加", self.html)
        self.assertEqual(self.html.count("action='/api/square/ai-salon-checkout'"), 1)
        self.assertNotIn("/api/stripe/ai-salon", self.html)
        self.assertNotRegex(self.html, r"https://(?:line\.me|lin\.ee)/")
        self.assertNotIn("LINE参加パスワード", self.html)

    def test_salon_is_one_complete_menu_before_the_venue_map(self) -> None:
        cards = re.findall(
            r"<article class='compact-course-card[^']*'.*?</article>",
            self.html,
            re.DOTALL,
        )
        self.assertEqual(len(cards), 4)
        salon_cards = [card for card in cards if ">AIオンラインサロン</h3>" in card]
        self.assertEqual(len(salon_cards), 0)
        self.assertNotIn("compact-course-card--salon", self.html)
        self.assertNotIn("id='salon-menu-card'", self.html)
        self.assertIn("class='course-menu-unified'", self.html)
        self.assertIn("aria-label='講習・相談の全5メニュー'", self.html)
        self.assertIn("上の4カードと下のオンラインサロンから選べます", self.html)
        self.assertIn("<div class='salon-panel'>", self.html)
        self.assertNotIn("class='salon-simple-head'", self.html)
        self.assertIn("class='salon-intro salon-intro--fused salon-card-overview'", self.html)
        self.assertIn("class='salon-all-details salon-all-details--complete'", self.html)
        visual = self.html.index("class='salon-main-visual'")
        title = self.html.index("id='salon-title'", visual)
        details = self.html.index("class='salon-all-details salon-all-details--complete'", title)
        checkout = self.html.index("class='compact-course-checkout salon-card-checkout'", details)
        material = self.html.index("class='compact-course-material salon-material-link'", checkout)
        self.assertLess(visual, title)
        self.assertLess(title, details)
        self.assertLess(details, checkout)
        self.assertLess(checkout, material)
        self.assertNotIn(" open", self.html[details:self.html.index(">", details)])
        self.assertEqual(self.html.count("id='seven-day-courses'"), 1)
        salon_start = self.html.index("id='seven-day-courses'")
        salon_end = self.html.index("</section>", salon_start)
        venue_map = self.html.index("class='course-venue-map'", salon_end)
        self.assertLess(salon_start, salon_end)
        self.assertLess(salon_end, venue_map)
        self.assertIn("8つのメリット・内容・参加方法を見る", self.html)
        self.assertIn(
            "class='compact-course-material salon-material-link' href='/lectures/2026-07-ai-online-salon-practice.html'",
            self.html,
        )
        self.assertIn("オンラインサロン受講資料を見る", self.html)
        self.assertIn("LINEライブ", self.html)
        self.assertIn("聞くだけOK", self.html)

    def test_hero_and_menu_order(self) -> None:
        self.assertIn("利用率6%", self.html)
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
        self.assertIn("align-items:stretch", tablet.group(1))
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

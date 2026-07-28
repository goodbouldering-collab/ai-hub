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
        self.assertGreaterEqual(
            self.html.count("action='/api/square/ai-salon-checkout'"),
            2,
        )
        self.assertNotIn("/api/stripe/ai-salon", self.html)
        self.assertNotRegex(self.html, r"https://(?:line\.me|lin\.ee)/")

    def test_card_links_to_single_salon_detail_section(self) -> None:
        self.assertIn(
            "href='#seven-day-courses'>サロンの内容・参加方法を見る",
            self.html,
        )
        self.assertEqual(self.html.count("id='seven-day-courses'"), 1)
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


if __name__ == "__main__":
    unittest.main()

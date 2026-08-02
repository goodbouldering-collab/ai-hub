from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
SOURCE = ROOT / "site" / "build_portal.py"
BACKGROUND_NAME = "ai-consult-soft-editorial-bg-20260802.webp"


class SoftEditorialDesignTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX.read_text(encoding="utf-8")
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_selected_visual_direction_is_rendered(self) -> None:
        self.assertIn("class='focus-hero-media fade-up d2'", self.html)
        self.assertIn("src='/img/hero-ai-consult-hikone.png'", self.html)
        self.assertIn("fetchpriority='high'", self.html)
        self.assertIn(f"url('/img/{BACKGROUND_NAME}')", self.html)
        self.assertNotIn("class='hero-orb", self.html)

    def test_copy_and_conversion_hierarchy_are_preserved(self) -> None:
        self.assertEqual(self.html.count("<h1 class='focus-title'>"), 1)
        self.assertIn("AIエージェントを、", self.html)
        self.assertIn("強力なスタッフに。", self.html)
        self.assertIn("講習・個別相談を見る", self.html)
        self.assertIn("無料相談する", self.html)
        self.assertIn("受講資料", self.html)

    def test_shared_palette_and_background_asset_exist(self) -> None:
        for token in (
            "--focus-blue: #5a6de4",
            "--focus-peach: #f3c6b5",
            "--focus-ivory: #fffdfa",
            "--focus-ink: #101b31",
        ):
            self.assertIn(token, self.source)

        for folder in (ROOT / "site" / "static" / "img", ROOT / "site" / "dist" / "img"):
            asset = folder / BACKGROUND_NAME
            self.assertTrue(asset.exists(), asset)
            self.assertGreater(asset.stat().st_size, 1_000)


if __name__ == "__main__":
    unittest.main()

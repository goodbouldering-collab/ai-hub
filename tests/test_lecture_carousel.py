from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"


class LectureCarouselTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_lecture_cards_use_the_shared_horizontal_carousel(self) -> None:
        section = re.search(
            r"<section class='focus-block soft' id='lectures'>(.*?)</section>",
            self.html,
            re.DOTALL,
        )
        self.assertIsNotNone(section)
        assert section is not None
        markup = section.group(1)
        self.assertIn("class='pf-carousel-wrap lecture-carousel-wrap'", markup)
        self.assertIn("class='pf-carousel lecture-carousel'", markup)
        self.assertIn("id='lecture-carousel'", markup)
        self.assertIn("aria-label='前の受講資料へ'", markup)
        self.assertIn("aria-label='次の受講資料へ'", markup)
        self.assertGreater(markup.count("class='lecture-card'"), 1)
        self.assertNotIn("class='lecture-grid'", markup)


if __name__ == "__main__":
    unittest.main()

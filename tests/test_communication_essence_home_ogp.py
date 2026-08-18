from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
STATIC_IMAGE = ROOT / "site" / "static" / "img" / "aiclimb-communication-essence-20260819.jpg"
DIST_IMAGE = ROOT / "site" / "dist" / "img" / "aiclimb-communication-essence-20260819.jpg"
ARTICLE_PATH = "/blog/2026-08-14-communication-essence-ai-consult.html"
IMAGE_PATH = "/img/aiclimb-communication-essence-20260819.jpg"
IMAGE_URL = "https://aiclimb.vercel.app" + IMAGE_PATH


class CommunicationEssenceHomeOgpTest(unittest.TestCase):
    def setUp(self) -> None:
        self.index = INDEX.read_text(encoding="utf-8")

    def test_homepage_shows_the_communication_article_share_image_above_the_main_content(self) -> None:
        feature = re.search(
            r"<section class='communication-essence-feature'.*?</section>",
            self.index,
            re.DOTALL,
        )

        self.assertIsNotNone(feature)
        self.assertIn(ARTICLE_PATH, feature.group(0))
        self.assertIn(f"src='{IMAGE_PATH}'", feature.group(0))
        self.assertIn("伝える技術の本質", feature.group(0))
        self.assertTrue(STATIC_IMAGE.is_file())
        self.assertTrue(DIST_IMAGE.is_file())

    def test_homepage_ogp_uses_the_same_supplied_share_image(self) -> None:
        self.assertIn(f"<meta property='og:image' content='{IMAGE_URL}'>", self.index)
        self.assertIn("<meta property='og:image:width' content='1254'>", self.index)
        self.assertIn("<meta property='og:image:height' content='1254'>", self.index)
        self.assertIn(f"<meta name='twitter:image' content='{IMAGE_URL}'>", self.index)


if __name__ == "__main__":
    unittest.main()

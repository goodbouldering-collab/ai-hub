import importlib.util
from pathlib import Path
import tempfile
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "site" / "build_site.py"
ARTICLE_PATH = ROOT / "content" / "blog" / "2026-08-14-communication-essence-ai-consult.md"
VIDEO_PATH = ROOT / "site" / "static" / "media" / "reels" / "2026-08-14-communication-essence.mp4"
COVER_PATH = ROOT / "site" / "static" / "img" / "reel-communication-essence-cover-20260814.webp"

SPEC = importlib.util.spec_from_file_location("build_site", BUILDER_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


class FeaturedBlogReelTest(unittest.TestCase):
    def test_featured_reel_source_and_generated_blog_index_stay_in_sync(self) -> None:
        frontmatter = ARTICLE_PATH.read_text(encoding="utf-8").split("---", 2)[1]
        meta = yaml.safe_load(frontmatter)

        self.assertTrue(meta["blog_index_featured_reel"])
        self.assertEqual(meta["video"], "/media/reels/2026-08-14-communication-essence.mp4")
        self.assertEqual(meta["video_poster"], "/img/reel-communication-essence-cover-20260814.webp")
        self.assertTrue(VIDEO_PATH.is_file())
        self.assertTrue(COVER_PATH.is_file())

        original_dist = builder.DIST
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                builder.DIST = Path(temp_dir)
                builder.build_blog()
                index = (builder.DIST / "blog" / "index.html").read_text(encoding="utf-8")
            finally:
                builder.DIST = original_dist

        self.assertIn("blog-reel-feature", index)
        self.assertIn(meta["video"], index)
        self.assertIn(meta["video_poster"], index)
        self.assertIn("伝える技術の本質", index)
        self.assertLess(
            index.index("<section class='blog-reel-feature'"),
            index.index("<div class='tr-grid'>"),
        )

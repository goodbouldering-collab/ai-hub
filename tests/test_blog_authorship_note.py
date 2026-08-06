import importlib.util
import hashlib
import json
from pathlib import Path
import re
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "site" / "build_site.py"
ARTICLE_PATH = ROOT / "content" / "blog" / "2026-08-06-ai-work-design-future.md"
FINAL_TITLE = "AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」"
APPROVED_AUTHORSHIP_NOTE = "AIを思考整理の補助に使い、運営者自身の経験と考えをもとに丁寧にまとめた記事です。"
ARTICLE_BODY_SHA256 = "1d5651056547a7beb4b5c1c2625be3abe33af4663f71d6678b08eb829fd9e2f6"
SPEC = importlib.util.spec_from_file_location("build_site", BUILDER_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def load_article() -> tuple[dict, str]:
    frontmatter, body = ARTICLE_PATH.read_text(encoding="utf-8").split("---", 2)[1:]
    return yaml.safe_load(frontmatter), body.lstrip("\r\n")


class BlogAuthorshipNoteTest(unittest.TestCase):
    def test_blog_note_is_between_header_and_video(self) -> None:
        note = "Example authorship note"
        page = builder.render_content_page(
            "Article title",
            {"authorship_note": note, "video": "/video/example.mp4"},
            "<p>Body</p>",
            "<nav></nav>",
            kind="blog",
        )

        self.assertLess(page.index("</header>"), page.index(note))
        self.assertLess(page.index(note), page.index("article-video"))
        self.assertLess(page.index("article-video"), page.index("<p>Body</p>"))

    def test_blog_note_escapes_html(self) -> None:
        page = builder.render_content_page(
            "Article title",
            {"authorship_note": "AI < person", "video": "/video/example.mp4"},
            "<p>Body</p>",
            "<nav></nav>",
            kind="blog",
        )

        self.assertIn("AI &lt; person", page)
        self.assertNotIn("<p>AI < person</p>", page)

    def test_lecture_page_omits_blog_note(self) -> None:
        note = "Lecture pages omit this note"
        page = builder.render_content_page(
            "Lecture title",
            {"authorship_note": note},
            "<p>Body</p>",
            "<nav></nav>",
            kind="lecture",
        )

        self.assertNotIn(note, page)

    def test_article_metadata_uses_the_approved_title_note_and_reel_duration(self) -> None:
        meta, _ = load_article()
        page = builder.render_content_page(
            meta["title"], meta, "<p>Body</p>", "<nav></nav>", kind="blog"
        )
        jsonld = json.loads(re.search(
            r"<script type='application/ld\+json'>(.*?)</script>", page
        ).group(1))

        self.assertEqual(meta["title"], FINAL_TITLE)
        self.assertEqual(meta["authorship_note"], APPROVED_AUTHORSHIP_NOTE)
        self.assertIn("約29秒", meta["video_label"])
        self.assertIn("女性ナレーション", meta["video_label"])
        self.assertIn("軽いBGM", meta["video_caption"])
        self.assertIn(f"<title>{FINAL_TITLE} | AI相談</title>", page)
        self.assertIn(f"<meta property='og:title' content='{FINAL_TITLE}'>", page)
        self.assertEqual(jsonld["headline"], FINAL_TITLE)

    def test_article_body_checksum_prevents_unintended_content_changes(self) -> None:
        _, body = load_article()
        actual = hashlib.sha256(body.encode("utf-8")).hexdigest()

        self.assertEqual(
            actual,
            ARTICLE_BODY_SHA256,
            "Article body checksum changed: review unintended body, H2, image, or slug edits.",
        )


if __name__ == "__main__":
    unittest.main()

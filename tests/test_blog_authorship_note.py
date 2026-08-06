import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "site" / "build_site.py"
SPEC = importlib.util.spec_from_file_location("build_site", BUILDER_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


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


if __name__ == "__main__":
    unittest.main()

import importlib.util
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

from PIL import Image
import yaml


ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = ROOT / "site" / "build_site.py"
ARTICLE_PATH = ROOT / "content" / "blog" / "2026-08-06-ai-work-design-future.md"
FINAL_TITLE = "AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」"
APPROVED_AUTHORSHIP_NOTE = "AIを思考整理の補助に使い、運営者自身の経験と考えをもとに丁寧にまとめた記事です。"
ARTICLE_BODY_SHA256 = "c88fcb045f69a40a8e990e75a77254954368f72ea41151387d9071899ff0f351"
ARTICLE_HERO_IMAGE = "/img/blog-ai-work-design-hero-20260806.webp"
ARTICLE_HERO_IMAGE_ALT = "AIが生み出した多くの案を、チームが目的、優先順位、責任に分けて一つの方向へ整理する様子"
ARTICLE_IMAGE_SHA256 = {
    "/img/blog-ai-work-design-hero-20260806.webp": "9272401fd416b6aa79f639b5c612db44a7d6f71fbdc77f200bab9ead2a31bb0b",
    "/img/blog-ai-work-design-speed-20260806.webp": "5f75e67c3f96f514b5a77eaf23474149f562e8678dfcd62ce7431ddfb885a7d9",
    "/img/blog-ai-work-design-system-20260806.webp": "ad3fbd4f9bea514b7a73ea4c747e1972e71737912208e9a1ddb4c45f0c150ab1",
    "/img/blog-ai-work-design-experience-20260806.webp": "0de5d77048546638eec258b6e5c709ab1025d4c602597b4b53e1d6a872160935",
    "/img/blog-ai-work-design-three-lanes-20260806.webp": "07af19a77327c18e5a558052d48e893e937192ee7b4e4dcf37924aa2a2c3c662",
}
SPEC = importlib.util.spec_from_file_location("build_site", BUILDER_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


def load_article() -> tuple[dict, str]:
    frontmatter, body = ARTICLE_PATH.read_text(encoding="utf-8").split("---", 2)[1:]
    return yaml.safe_load(frontmatter), body.lstrip("\r\n")


def render_article() -> str:
    meta, body = load_article()
    markdown = builder._load_markdown()
    body_html = markdown.markdown(body, extensions=["extra", "sane_lists", "attr_list"])
    return builder.render_content_page(
        meta["title"],
        meta,
        body_html,
        "<nav></nav>",
        page_path="blog/2026-08-06-ai-work-design-future.html",
        kind="blog",
    )


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

    def test_article_hero_image_metadata_prevents_unintended_asset_changes(self) -> None:
        meta, _ = load_article()

        self.assertEqual(
            meta["image"],
            ARTICLE_HERO_IMAGE,
            "Article hero image changed: preserve the approved image asset path.",
        )
        self.assertEqual(
            meta["image_alt"],
            ARTICLE_HERO_IMAGE_ALT,
            "Article hero image alt changed: preserve the approved accessible description.",
        )

    def test_rendered_article_keeps_approved_title_note_video_hero_body_order(self) -> None:
        page = render_article()
        markers = [
            f"<h1>{FINAL_TITLE}</h1>",
            "class='blog-authorship-note'",
            "class='article-video article-video--portrait'",
            'src="/img/blog-ai-work-design-hero-20260806.webp"',
            "<p>AIで資料も、Webサイトも、業務アプリも、驚くほど早く形になります。",
        ]

        positions = [page.index(marker) for marker in markers]

        self.assertEqual(positions, sorted(positions))

    def test_every_blog_img_reference_exists_and_is_git_tracked(self) -> None:
        missing: list[str] = []
        untracked: list[str] = []
        for article in sorted((ROOT / "content" / "blog").glob("*.md")):
            references = sorted(set(re.findall(r"/img/[A-Za-z0-9_.-]+", article.read_text(encoding="utf-8"))))
            for reference in references:
                asset = ROOT / "site" / "static" / reference.lstrip("/")
                if not asset.is_file():
                    missing.append(f"{article.name}: {reference}")
                    continue
                relative = asset.relative_to(ROOT).as_posix()
                tracked = subprocess.run(
                    ["git", "ls-files", "--error-unmatch", "--", relative],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                )
                if tracked.returncode != 0:
                    untracked.append(relative)

        self.assertEqual(missing, [], "Missing /img/ assets:\n" + "\n".join(missing))
        self.assertEqual(untracked, [], "Untracked /img/ assets:\n" + "\n".join(untracked))

    def test_approved_article_webp_assets_keep_format_dimensions_and_hashes(self) -> None:
        for reference, expected_sha256 in ARTICLE_IMAGE_SHA256.items():
            asset = ROOT / "site" / "static" / reference.lstrip("/")
            self.assertTrue(asset.is_file(), reference)
            self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(), expected_sha256, reference)
            with Image.open(asset) as image:
                self.assertEqual(image.format, "WEBP", reference)
                self.assertEqual(image.size, (1672, 941), reference)


if __name__ == "__main__":
    unittest.main()

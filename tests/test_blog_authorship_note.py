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
PORTAL_PATH = ROOT / "site" / "build_portal.py"
ARTICLE_PATH = ROOT / "content" / "blog" / "2026-08-06-ai-work-design-future.md"
EXPERIENCE_ARTICLE_PATH = ROOT / "content" / "blog" / "2026-08-09-ai-experience-3d-reality.md"
BLOG_DIR = ROOT / "content" / "blog"
LECTURE_DIR = ROOT / "content" / "lectures"
FINAL_TITLE = "AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」"
EXPERIENCE_TITLE = "経験が10倍になる？AI時代、経験者が再び強くなる理由"
CANONICAL_AUTHORSHIP_NOTE = "※内容は運営者が考え、AIで整えています。"
APPROVED_AUTHORSHIP_NOTE = CANONICAL_AUTHORSHIP_NOTE
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
PORTAL_SPEC = importlib.util.spec_from_file_location("build_portal", PORTAL_PATH)
assert PORTAL_SPEC and PORTAL_SPEC.loader
portal = importlib.util.module_from_spec(PORTAL_SPEC)
PORTAL_SPEC.loader.exec_module(portal)


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
    def test_blog_note_is_plain_body_text_between_header_and_video(self) -> None:
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
        self.assertIn(
            f"</header><p>{note}</p><div class='content-wrap'>",
            page,
        )
        self.assertNotIn("blog-authorship-note", page)
        self.assertNotIn("この記事について", page)

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
        self.assertIn("<p>AI &lt; person</p>", page)
        self.assertNotIn("blog-authorship-note", page)

    def test_blog_lead_quote_appears_before_hero_and_table_of_contents(self) -> None:
        page = builder.render_content_page(
            "Article title",
            {
                "authorship_note": CANONICAL_AUTHORSHIP_NOTE,
                "lead_quote": "First line\nSecond line",
                "hero_image": True,
                "image": "/img/example.png",
            },
            "<h2>One</h2><p>A</p><h2>Two</h2><p>B</p><h2>Three</h2><p>C</p>",
            "<nav></nav>",
            kind="blog",
        )

        markers = [
            CANONICAL_AUTHORSHIP_NOTE,
            "<blockquote class='article-lead-quote'>First line<br>Second line</blockquote>",
            "<figure class='article-hero'>",
            "<div class='content-toc'",
            "<h2 id='one'>One</h2>",
        ]
        positions = [page.index(marker) for marker in markers]
        self.assertEqual(positions, sorted(positions))

    def test_blog_lead_quote_escapes_html(self) -> None:
        page = builder.render_content_page(
            "Article title",
            {"lead_quote": "AI < person"},
            "<p>Body</p>",
            "<nav></nav>",
            kind="blog",
        )

        self.assertIn(
            "<blockquote class='article-lead-quote'>AI &lt; person</blockquote>",
            page,
        )
        self.assertNotIn("<blockquote class='article-lead-quote'>AI < person", page)

    def test_lecture_page_renders_note_between_title_and_cover(self) -> None:
        note = "Lecture authorship note"
        page = builder.render_content_page(
            "Lecture title",
            {"authorship_note": note},
            "<p>Body</p>",
            "<nav></nav>",
            kind="lecture",
        )

        self.assertIn(
            f"</header><p>{note}</p><div class='content-wrap lecture-content'",
            page,
        )

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
        self.assertEqual(
            meta["video_label"],
            "AIでデザイナーの仕事がどう広がるかを約25秒・女性ナレーション・軽いBGMで整理する動画",
        )
        self.assertEqual(
            meta["video_caption"],
            "ロゴ、サイト、資料へ。AIがデザイナーの仕事を広げる理由を、女性ナレーションと軽いBGMで伝える約25秒リールです。",
        )
        self.assertIn(f"<title>{FINAL_TITLE} | AIClimb（AI相談）</title>", page)
        self.assertIn(f"<meta property='og:title' content='{FINAL_TITLE}'>", page)
        self.assertEqual(jsonld["headline"], FINAL_TITLE)

    def test_every_current_blog_source_uses_the_canonical_authorship_note(self) -> None:
        articles = sorted(BLOG_DIR.glob("*.md"))
        self.assertGreater(len(articles), 0)

        for article in articles:
            frontmatter = article.read_text(encoding="utf-8").split("---", 2)[1]
            meta = yaml.safe_load(frontmatter)
            self.assertEqual(
                meta.get("authorship_note"),
                CANONICAL_AUTHORSHIP_NOTE,
                article.name,
            )

    def test_every_current_lecture_source_uses_the_canonical_authorship_note(self) -> None:
        lectures = sorted(LECTURE_DIR.glob("*.md"))
        self.assertGreater(len(lectures), 0)

        for lecture in lectures:
            frontmatter = lecture.read_text(encoding="utf-8").split("---", 2)[1]
            meta = yaml.safe_load(frontmatter)
            self.assertEqual(
                meta.get("authorship_note"),
                CANONICAL_AUTHORSHIP_NOTE,
                lecture.name,
            )

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
            APPROVED_AUTHORSHIP_NOTE,
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


class ExperienceArticleTitleTest(unittest.TestCase):
    def test_title_is_shared_by_article_heading_and_search_metadata(self) -> None:
        frontmatter, _ = EXPERIENCE_ARTICLE_PATH.read_text(encoding="utf-8").split("---", 2)[1:]
        meta = yaml.safe_load(frontmatter)
        page = builder.render_content_page(
            meta["title"],
            meta,
            "<p>本文</p>",
            "<nav></nav>",
            page_path="blog/2026-08-09-ai-experience-3d-reality.html",
            kind="blog",
        )
        jsonld_match = re.search(
            r"<script type='application/ld\+json'>(.*?)</script>", page
        )
        self.assertIsNotNone(jsonld_match)
        assert jsonld_match is not None
        jsonld = json.loads(jsonld_match.group(1))

        self.assertEqual(meta["title"], EXPERIENCE_TITLE)
        self.assertIn(f"<h3>{EXPERIENCE_TITLE}</h3>", portal._render_blog_teaser())
        self.assertIn(f"<h1>{EXPERIENCE_TITLE}</h1>", page)
        self.assertIn(f"<title>{EXPERIENCE_TITLE} | AIClimb（AI相談）</title>", page)
        self.assertIn(f"<meta property='og:title' content='{EXPERIENCE_TITLE}'>", page)
        self.assertEqual(jsonld["headline"], EXPERIENCE_TITLE)

class VercelSupabaseBoundariesBlogTest(unittest.TestCase):
    ARTICLE_PATH = ROOT / "content" / "blog" / "2026-08-08-vercel-supabase-d1-r2-boundaries.md"
    FINAL_TITLE = "サイト公開から本格稼働させるには、データをどこに置くのが正解？──Sites・GitHub＋Vercel＋Supabaseの選び方"
    EXPECTED_HEADINGS = [
        "最初の判断軸は「容量」ではなく、共有・復旧・バックアップ",
        "Sitesは、限定公開の試作・デモに向く",
        "GitHub＋Vercelは、複数PCでも開発を続けるための土台",
        "顧客・会計・書類を扱うなら、Supabaseを加えて復元まで運用する",
        "Climbは、容量ではなく基幹業務の要件で選ぶ",
    ]
    SAFE_AUTHORSHIP_NOTE = CANONICAL_AUTHORSHIP_NOTE
    HERO_IMAGE = "/img/blog-sites-runtime-data-decision-hero-20260810.png"

    @classmethod
    def load_article(cls) -> tuple[dict, str]:
        frontmatter, body = cls.ARTICLE_PATH.read_text(encoding="utf-8").split("---", 2)[1:]
        return yaml.safe_load(frontmatter), body.lstrip("\r\n")

    def test_article_metadata_and_section_assets_are_complete(self) -> None:
        meta, body = self.load_article()

        self.assertEqual(
            meta["title"],
            self.FINAL_TITLE,
        )
        self.assertIn("共有・復旧・バックアップ", meta["summary"])
        self.assertIn("データの置き場所", meta["goal"])
        self.assertEqual(meta["authorship_note"], self.SAFE_AUTHORSHIP_NOTE)
        self.assertEqual(meta["image"], self.HERO_IMAGE)

        headings = re.findall(r"^## (.+)$", body, flags=re.MULTILINE)
        self.assertEqual(headings, self.EXPECTED_HEADINGS)

        references = sorted(set(re.findall(r"/img/[A-Za-z0-9_.-]+", body)))
        self.assertGreaterEqual(len(references), 5)
        for reference in references:
            self.assertTrue((ROOT / "site" / "static" / reference.lstrip("/")).is_file(), reference)

        self.assertEqual(body.count('<div class="publishing-table-scroll"'), 1)

    def test_rendered_article_has_one_note_and_blogposting_schema(self) -> None:
        meta, _ = self.load_article()
        page = builder.render_content_page(
            meta["title"],
            meta,
            "<p>本文</p>",
            "<nav></nav>",
            page_path="blog/2026-08-08-vercel-supabase-d1-r2-boundaries.html",
            kind="blog",
        )

        title_index = page.index(f"<h1>{meta['title']}</h1>")
        note_index = page.index(self.SAFE_AUTHORSHIP_NOTE)
        content_index = page.index("<div class='content-wrap'>")
        self.assertLess(title_index, note_index)
        self.assertLess(note_index, content_index)
        self.assertEqual(page.count(self.SAFE_AUTHORSHIP_NOTE), 1)
        self.assertIn(
            f"</header><p>{self.SAFE_AUTHORSHIP_NOTE}</p><div class='content-wrap'>",
            page,
        )
        self.assertNotIn("blog-authorship-note", page)
        self.assertNotIn("この記事について", page)

        jsonld_match = re.search(
            r"<script type='application/ld\+json'>(.*?)</script>", page
        )
        self.assertIsNotNone(jsonld_match)
        jsonld = json.loads(jsonld_match.group(1))
        self.assertEqual(jsonld["@type"], "BlogPosting")
        self.assertEqual(jsonld["headline"], meta["title"])
        self.assertEqual(jsonld["datePublished"], "2026-08-10")
        self.assertEqual(jsonld["image"], builder.SITE_URL + self.HERO_IMAGE)


if __name__ == "__main__":
    unittest.main()

import html
import importlib.util
import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from unittest.mock import patch

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
LECTURES = ROOT / "content" / "lectures"
TARGET_COVER_RATIO = 1200 / 630
RASTER_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".webp"}


def load_site_builder():
    spec = importlib.util.spec_from_file_location("site_builder_lecture_media", ROOT / "site" / "build_site.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def load_portal_builder():
    spec = importlib.util.spec_from_file_location("portal_builder_lecture_media", ROOT / "site" / "build_portal.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def source_image_path(image_url: str) -> Path:
    if image_url.startswith("/lectures/assets/"):
        return LECTURES / image_url.removeprefix("/lectures/")
    if image_url.startswith("/img/"):
        return ROOT / "site" / "static" / image_url.removeprefix("/")
    raise AssertionError(f"受講資料の画像はサイト内の固定URLを使ってください: {image_url}")


class LectureMediaContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_site_builder()
        cls.portal = load_portal_builder()
        cls.sources = sorted(LECTURES.glob("*.md"))
        cls.records = []
        for source in cls.sources:
            meta, _body = cls.builder._parse_frontmatter(source.read_text(encoding="utf-8"))
            cls.records.append((source, meta))

    def test_every_lecture_has_an_accessible_landscape_cover(self):
        """Removing a cover, alt text, or wide source image must break the lecture contract."""
        self.assertGreater(len(self.records), 0)

        for source, meta in self.records:
            with self.subTest(source=source.name):
                image_url = str(meta.get("image") or "").strip()
                image_alt = str(meta.get("image_alt") or "").strip()
                self.assertTrue(image_url, f"{source.name}: image がありません")
                self.assertTrue(image_alt, f"{source.name}: image_alt がありません")

                image_path = source_image_path(image_url)
                self.assertTrue(image_path.is_file(), f"{source.name}: 画像が見つかりません: {image_path}")
                with Image.open(image_path) as cover:
                    width, height = cover.size

                self.assertGreater(width, height, f"{source.name}: 画像は必ず横長にしてください ({width}x{height})")
                self.assertAlmostEqual(
                    width / height,
                    TARGET_COVER_RATIO,
                    delta=0.01,
                    msg=f"{source.name}: カバー比率を1200:630へ揃えてください ({width}x{height})",
                )

    def test_every_lecture_image_asset_is_landscape(self):
        """Adding a portrait image to the lecture asset library must fail."""
        image_assets = sorted(
            path
            for path in (LECTURES / "assets").rglob("*")
            if path.suffix.lower() in RASTER_SUFFIXES | {".svg"}
        )
        self.assertGreater(len(image_assets), 0)

        for image_path in image_assets:
            with self.subTest(image=image_path.relative_to(ROOT)):
                if image_path.suffix.lower() == ".svg":
                    root = ET.parse(image_path).getroot()
                    view_box = root.attrib.get("viewBox", "").split()
                    self.assertEqual(len(view_box), 4, f"{image_path.name}: SVGにviewBoxがありません")
                    width, height = float(view_box[2]), float(view_box[3])
                else:
                    with Image.open(image_path) as image:
                        width, height = image.size
                self.assertGreater(width, height, f"{image_path.name}: 画像は必ず横長にしてください")

    def test_every_rendered_lecture_uses_one_shared_cover_and_one_h1(self):
        """A lecture missing the shared cover or adding a second H1 must fail in rendered HTML."""
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            with patch.object(self.builder, "DIST", dist):
                built = self.builder.build_lectures()

            self.assertEqual(built, len(self.records))
            for source, meta in self.records:
                with self.subTest(source=source.name):
                    rendered = (dist / "lectures" / f"{source.stem}.html").read_text(encoding="utf-8")
                    self.assertEqual(len(re.findall(r"<h1\b", rendered, flags=re.I)), 1)
                    self.assertEqual(rendered.count("<figure class='lecture-cover'>"), 1)
                    self.assertIn(f"src='{html.escape(str(meta['image']), quote=True)}'", rendered)
                    self.assertIn(f"alt='{html.escape(str(meta['image_alt']), quote=True)}'", rendered)
                    self.assertIn("width='1200' height='630'", rendered)

    def test_lecture_index_cards_use_the_same_cover_contract(self):
        """Listed materials must reuse their cover and alt text on the lecture index."""
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            with patch.object(self.builder, "DIST", dist):
                self.builder.build_lectures()
            rendered = (dist / "lectures" / "index.html").read_text(encoding="utf-8")

        for source, meta in self.records:
            with self.subTest(source=source.name):
                href = f"href='./{source.stem}.html'"
                listed = meta.get("listed", True) is not False
                if not listed:
                    self.assertNotIn(href, rendered)
                    continue

                image_url = html.escape(str(meta["image"]), quote=True)
                image_alt = html.escape(str(meta["image_alt"]), quote=True)
                card_pattern = re.compile(
                    rf"<a class='tr-card' {re.escape(href)}>.*?"
                    rf"<span class='tr-card-media'><img src='{re.escape(image_url)}' "
                    rf"alt='{re.escape(image_alt)}' width='1200' height='630'",
                    flags=re.S,
                )
                self.assertRegex(rendered, card_pattern)

    def test_instructor_resources_are_always_visible_without_an_accordion(self):
        """Making the instructor resources collapsible must break the public index contract."""
        with tempfile.TemporaryDirectory() as tmp:
            dist = Path(tmp)
            with patch.object(self.builder, "DIST", dist):
                self.builder.build_lectures()
            rendered = (dist / "lectures" / "index.html").read_text(encoding="utf-8")

        instructor_group = re.search(
            r"<(?P<tag>section|details)\b[^>]*\bid='sec-講師用・詳しく学ぶ資料'",
            rendered,
        )
        self.assertIsNotNone(instructor_group)
        self.assertEqual("section", instructor_group.group("tag"))

    def test_home_lecture_cards_use_the_same_cover_contract(self):
        """The actual home lecture carousel must reuse every listed material's wide cover."""
        rendered = self.portal._render_lectures_section()

        for source, meta in self.records:
            with self.subTest(source=source.name):
                href = f"href='/lectures/{source.stem}.html'"
                listed = meta.get("listed", True) is not False
                if not listed:
                    self.assertNotIn(href, rendered)
                    continue

                image_url = html.escape(str(meta["image"]), quote=True)
                image_alt = html.escape(str(meta["image_alt"]), quote=True)
                card_pattern = re.compile(
                    rf"<a class='lecture-card' {re.escape(href)}>.*?"
                    rf"<span class='lecture-card-media'><img src='{re.escape(image_url)}' "
                    rf"alt='{re.escape(image_alt)}' width='1200' height='630'",
                    flags=re.S,
                )
                self.assertRegex(rendered, card_pattern)

        self.assertRegex(
            rendered,
            re.compile(
                r"<a class='lecture-card' href='/programming-map\.html'>.*?"
                r"<span class='lecture-card-media'><img src='/img/course-path-coding\.webp' .*?"
                r"width='1200' height='630'",
                flags=re.S,
            ),
        )


if __name__ == "__main__":
    unittest.main()

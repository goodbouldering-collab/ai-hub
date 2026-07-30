from pathlib import Path
import json
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
PROGRAMMING_MAP = ROOT / "site" / "dist" / "programming-map.html"
STATIC_IMG = ROOT / "site" / "static" / "img"


SECTION_IMAGES = {
    "「AIで作れた」と「仕事で使える」は別です": "ai-coding-00-work-ready.webp",
    "エンジニアのレベルは、使うツールではなく任せられる範囲で見る": "ai-coding-01-level-map.webp",
    "作ったものを、相手が判断できる言葉で説明する": "ai-coding-02-explain.webp",
    "4つの道具を、相談・制作・記録・確認で使い分ける": "ai-coding-03-tools.webp",
    "入口から応用まで、1段階ずつ進める": "ai-coding-04-learning-path.webp",
    "まず「内容・見た目・動き・データ・履歴・設定」を分ける": "ai-coding-05-components.webp",
    "AIへの依頼は「場所・変更・条件・確認」の4点で伝える": "ai-coding-06-request-loop.webp",
    "公開は「本番で見る・秘密を守る・戻し方を持つ」まで": "ai-coding-07-safe-publish.webp",
    "Web、資料、発信、事務作業でも進め方は同じ": "ai-coding-08-work-applications.webp",
    "必要な人だけ、Codexの公式情報を確認する": "ai-coding-09-official-info.webp",
    "だんだん作れるようになる総合演習": "ai-coding-10-exercises.webp",
}


class CodingLectureVisualsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index_html = INDEX.read_text(encoding="utf-8")
        cls.material_html = PROGRAMMING_MAP.read_text(encoding="utf-8")

    def test_learning_material_card_has_the_course_cover(self) -> None:
        cards = re.findall(
            r"<a class='lecture-card'[^>]*>.*?</a>",
            self.index_html,
            re.DOTALL,
        )
        coding_card = next(
            (card for card in cards if "AIコーディング講習 120分" in card),
            "",
        )
        self.assertTrue(coding_card)
        self.assertIn("href='/programming-map.html'", coding_card)
        self.assertIn("class='lecture-card-media'", coding_card)
        self.assertIn("src='/img/course-path-coding.webp'", coding_card)
        self.assertIn(
            "AIが変更したコードを人が確認し、安全にWebサイトを公開するAIコーディング講習",
            coding_card,
        )

    def test_course_cover_is_shared_by_card_hero_and_social_metadata(self) -> None:
        self.assertIn('src="./img/course-path-coding.webp"', self.material_html)
        self.assertIn(
            '<meta property="og:image" content="https://ai-hub-jp.vercel.app/img/course-path-coding.webp">',
            self.material_html,
        )
        self.assertIn(
            '<meta name="twitter:image" content="https://ai-hub-jp.vercel.app/img/course-path-coding.webp">',
            self.material_html,
        )
        self.assertNotIn("./img/hero-ai-hub-studio.png", self.material_html)
        self.assertNotIn("./img/hero-ai-lesson-line.png", self.material_html)

    def test_every_course_h2_is_immediately_followed_by_its_figure(self) -> None:
        self.assertEqual(self.material_html.count('class="pm-section-figure"'), 11)
        for heading, filename in SECTION_IMAGES.items():
            with self.subTest(heading=heading):
                pattern = (
                    rf"<h2>{re.escape(heading)}</h2>\s*"
                    rf'<figure class="pm-section-figure">\s*'
                    rf'<img src="\./img/{re.escape(filename)}"'
                )
                self.assertRegex(self.material_html, pattern)

    def test_section_images_exist_and_have_accessible_captions(self) -> None:
        for filename in SECTION_IMAGES.values():
            with self.subTest(filename=filename):
                asset = STATIC_IMG / filename
                self.assertTrue(asset.is_file())
                self.assertGreater(asset.stat().st_size, 40_000)
        self.assertEqual(self.material_html.count("<figcaption>"), 11)
        self.assertEqual(self.material_html.count("</figcaption>"), 11)
        self.assertEqual(self.material_html.count('loading="lazy" decoding="async"'), 11)

    def test_learning_resource_json_ld_uses_the_course_cover(self) -> None:
        match = re.search(
            r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>',
            self.material_html,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        payload = json.loads(match.group(1))
        self.assertEqual(payload["@type"], "LearningResource")
        self.assertEqual(payload["timeRequired"], "PT120M")
        self.assertEqual(
            payload["image"]["contentUrl"],
            "https://ai-hub-jp.vercel.app/img/course-path-coding.webp",
        )


if __name__ == "__main__":
    unittest.main()

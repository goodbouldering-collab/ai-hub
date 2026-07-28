from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content" / "lectures" / "2026-05-climbing-history.md"
INDEX = ROOT / "site" / "dist" / "index.html"
MATERIAL = ROOT / "site" / "dist" / "lectures" / "2026-05-climbing-history.html"
AGENT_MATERIAL = ROOT / "site" / "dist" / "lectures" / "2026-04-ai-kihon.html"


class ClimbingMaterialExampleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.source = SOURCE.read_text(encoding="utf-8")
        cls.index_html = INDEX.read_text(encoding="utf-8")
        cls.material_html = MATERIAL.read_text(encoding="utf-8")
        cls.agent_html = AGENT_MATERIAL.read_text(encoding="utf-8")

    def test_source_is_positioned_as_an_ai_material_example(self) -> None:
        self.assertIn(
            "title: AI資料作成例 — クライミングはどう広がった？",
            self.source,
        )
        self.assertIn("category: climbing", self.source)
        self.assertIn("AIだけで完成させた歴史資料ではありません", self.source)

    def test_rendered_page_explains_ai_and_human_roles(self) -> None:
        self.assertIn(
            "<h1>AI資料作成例 — クライミングはどう広がった？</h1>",
            self.material_html,
        )
        self.assertIn("AIで、知識を「伝わる資料」にする5ステップ", self.material_html)
        self.assertIn("公開前の事実確認、表現の判断、最終承認は人が行っています", self.material_html)
        self.assertIn("/slides/climbing-history-1.html", self.material_html)
        self.assertIn("/slides/climbing-history-2.pdf", self.material_html)

    def test_home_material_card_uses_the_ai_example_label(self) -> None:
        self.assertIn("AI資料作成例", self.index_html)
        self.assertIn(
            "/lectures/2026-05-climbing-history.html",
            self.index_html,
        )
        self.assertIn(
            "AI資料作成例 · 制作例 · 目安 約15分",
            self.index_html,
        )
        self.assertNotIn(
            "AI講座例向け · 入門 · 目安 約15分",
            self.index_html,
        )

    def test_agent_course_links_to_the_completed_example(self) -> None:
        self.assertIn(
            'href="./2026-05-climbing-history.html">AIで作った資料の完成例を見る',
            self.agent_html,
        )


if __name__ == "__main__":
    unittest.main()

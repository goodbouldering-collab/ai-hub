from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
PROGRAMMING_MAP = ROOT / "site" / "dist" / "programming-map.html"


class CourseMaterialMappingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index_html = INDEX.read_text(encoding="utf-8")
        cls.material_html = PROGRAMMING_MAP.read_text(encoding="utf-8")

    def test_programming_map_is_ai_coding_material(self) -> None:
        self.assertIn(
            "<title>AIコーディング講習｜Codex・Claude Code実践 | AI相談</title>",
            self.material_html,
        )
        self.assertIn("AIコーディング講習 / Codex + Claude Code", self.material_html)
        self.assertIn("AIコーディングを、", self.material_html)
        self.assertNotIn("AIエージェント講習のビジュアル", self.material_html)

    def test_shared_navigation_uses_ai_coding_label(self) -> None:
        for html in (self.index_html, self.material_html):
            self.assertRegex(
                html,
                r"href=['\"]/programming-map\.html['\"][^>]*>AIコーディング講習<",
            )

    def test_course_cards_link_to_the_matching_material(self) -> None:
        cards = re.findall(
            r"<article class='compact-course-card[^']*'.*?</article>",
            self.index_html,
            re.DOTALL,
        )
        coding_card = next((card for card in cards if ">AIコーディング講習</h3>" in card), "")
        agent_card = next((card for card in cards if ">AIエージェント講習</h3>" in card), "")
        self.assertTrue(coding_card)
        self.assertTrue(agent_card)
        self.assertIn("href='/programming-map.html'", coding_card)
        self.assertIn("AIコーディング講習の受講資料を見る", coding_card)
        self.assertNotIn("href='/programming-map.html'", agent_card)
        self.assertIn(
            "href='/blog/2026-07-14-ai-agent-course-codex-claude-code.html'",
            agent_card,
        )


if __name__ == "__main__":
    unittest.main()

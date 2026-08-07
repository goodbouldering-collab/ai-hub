from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
PROGRAMMING_MAP = ROOT / "site" / "dist" / "programming-map.html"
AGENT_MATERIAL = ROOT / "site" / "dist" / "lectures" / "2026-04-ai-kihon.html"
AGENT_ARTICLE = ROOT / "site" / "dist" / "blog" / "2026-07-14-ai-agent-course-codex-claude-code.html"


class CourseMaterialMappingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index_html = INDEX.read_text(encoding="utf-8")
        cls.material_html = PROGRAMMING_MAP.read_text(encoding="utf-8")
        cls.agent_html = AGENT_MATERIAL.read_text(encoding="utf-8")
        cls.article_html = AGENT_ARTICLE.read_text(encoding="utf-8")

    def test_programming_map_is_ai_coding_material(self) -> None:
        self.assertIn(
            "<title>AIコーディング講習｜Codex・Claude Code実践 | AI相談</title>",
            self.material_html,
        )
        self.assertIn("AIコーディング講習 / Codex + Claude Code", self.material_html)
        self.assertIn("AIコーディングを、", self.material_html)
        self.assertNotIn("AIエージェント講習のビジュアル", self.material_html)

    def test_ai_agent_material_is_the_canonical_beginner_course(self) -> None:
        self.assertIn(
            "<title>AIエージェント講習 120分 — Codexで頼む・確かめる・残す | AI相談</title>",
            self.agent_html,
        )
        self.assertIn("目安 120分", self.agent_html)
        self.assertIn("AIエージェント依頼カード", self.agent_html)
        self.assertIn('<h2 id="codex-beginner">', self.agent_html)
        self.assertIn("Codex初級：安全な作業場所を選ぶ", self.agent_html)
        self.assertIn("https://goodbouldering.com/?pid=188553378", self.agent_html)
        self.assertNotIn("はじめてのAI — 困りごとを1つ、下書きにする", self.agent_html)

    def test_shared_navigation_uses_ai_agent_material(self) -> None:
        for html in (self.index_html, self.agent_html, self.material_html, self.article_html):
            self.assertRegex(
                html,
                r"href=['\"]/lectures/2026-04-ai-kihon\.html['\"][^>]*>AIエージェント講習<",
            )

    def test_only_agent_material_marks_agent_navigation_current(self) -> None:
        self.assertRegex(
            self.agent_html,
            r"class='nav-link nav-essential nav-current' "
            r"href='/lectures/2026-04-ai-kihon\.html' aria-current='page'",
        )
        self.assertNotRegex(
            self.material_html,
            r"href='/lectures/2026-04-ai-kihon\.html' aria-current='page'",
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
            "href='/lectures/2026-04-ai-kihon.html'",
            agent_card,
        )
        self.assertIn("AIエージェント講習の受講資料を見る", agent_card)
        self.assertNotIn(
            "href='/blog/2026-07-14-ai-agent-course-codex-claude-code.html'",
            agent_card,
        )
        self.assertIn(
            "<p class='compact-course-material-row'><a class='compact-course-material' "
            "href='/lectures/2026-04-ai-kihon.html'>AIエージェント講習の受講資料を見る →</a></p>",
            agent_card,
        )
        self.assertIn(".compact-course-material-row {", self.index_html)
        self.assertNotIn(
            "</a><a class='compact-course-material' href='/lectures/2026-04-ai-kihon.html'>",
            agent_card,
        )

    def test_agent_article_links_to_the_course_material(self) -> None:
        self.assertIn(
            'href="/lectures/2026-04-ai-kihon.html">AIエージェント講習の受講資料を見る',
            self.article_html,
        )

    def test_quick_diagnosis_describes_the_agent_course(self) -> None:
        self.assertIn(
            "実際の仕事を1つ選び、Codexへ小さく頼み、変更点を人が確認・修正し、"
            "次回も使える手順として残す120分の初級実践です。",
            self.index_html,
        )
        self.assertNotIn(
            "name: 'AIエージェント講習 120分',\n"
            "        desc: 'Codex導入、Claude Code併用",
            self.index_html,
        )


if __name__ == "__main__":
    unittest.main()

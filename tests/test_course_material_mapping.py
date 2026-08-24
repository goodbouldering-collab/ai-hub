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
            "<title>AIコーディング講習｜Codex・Claude Code実践 | AIclimb（AI相談）</title>",
            self.material_html,
        )
        self.assertIn("AIコーディング講習 / Codex + Claude Code", self.material_html)
        self.assertIn("AIコーディングを、", self.material_html)
        self.assertIn("仕事で使える", self.material_html)
        self.assertNotIn("AIエージェント講習のビジュアル", self.material_html)

    def test_ai_agent_material_is_the_canonical_beginner_course(self) -> None:
        self.assertIn(
            "<title>AIエージェント講習 120分 — Codexで頼む・確かめる・残す | AIclimb（AI相談）</title>",
            self.agent_html,
        )
        self.assertIn("目安 120分", self.agent_html)
        self.assertIn("AIエージェント依頼カード", self.agent_html)
        self.assertIn('<h2 id="codex-beginner">', self.agent_html)
        self.assertIn("Codex初級：安全な作業場所を選ぶ", self.agent_html)
        self.assertIn("https://goodbouldering.com/?pid=188553378", self.agent_html)
        self.assertNotIn("はじめてのAI — 困りごとを1つ、下書きにする", self.agent_html)

    def test_agent_course_remains_a_contextual_cta_not_global_navigation(self) -> None:
        self.assertIn("href='/lectures/2026-04-ai-kihon.html'", self.index_html)
        self.assertIn('href="/lectures/2026-04-ai-kihon.html"', self.article_html)
        for html in (self.index_html, self.agent_html, self.material_html, self.article_html):
            header = re.search(
                r"<header\b[^>]*class='[^']*site-header[^']*'[^>]*>.*?</header>",
                html,
                re.DOTALL,
            )
            self.assertIsNotNone(header)
            self.assertNotIn("href='/lectures/2026-04-ai-kihon.html'", header.group(0))

    def test_agent_material_has_no_removed_header_item_to_mark_current(self) -> None:
        header = re.search(
            r"<header\b[^>]*class='[^']*site-header[^']*'[^>]*>.*?</header>",
            self.agent_html,
            re.DOTALL,
        )
        self.assertIsNotNone(header)
        self.assertNotRegex(
            header.group(0),
            r"href='/lectures/2026-04-ai-kihon\.html'[^>]*aria-current='page'",
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
        self.assertRegex(
            self.index_html,
            r"\.compact-course-material-row\s*\{[^}]*text-align:center;",
        )
        self.assertNotIn(
            "</a><a class='compact-course-material' href='/lectures/2026-04-ai-kihon.html'>",
            agent_card,
        )

    def test_agent_article_links_to_the_course_material(self) -> None:
        self.assertIn(
            'href="/lectures/2026-04-ai-kihon.html">AIエージェント講習の受講資料を見る',
            self.article_html,
        )

    def test_quick_diagnosis_routes_work_problem_results_to_course_selection(self) -> None:
        self.assertIn(
            "告知・集客の型を一つ作る",
            self.index_html,
        )
        self.assertIn(
            'href="#packages" data-close-diag>講習・相談コースを見る</a>',
            self.index_html,
        )


if __name__ == "__main__":
    unittest.main()

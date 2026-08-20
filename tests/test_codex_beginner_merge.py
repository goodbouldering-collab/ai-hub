import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
AGENT = ROOT / "site" / "dist" / "lectures" / "2026-04-ai-kihon.html"
LEGACY = ROOT / "site" / "dist" / "lectures" / "2026-05-claude-code-features.html"
LEGACY_SOURCE = ROOT / "content" / "lectures" / "2026-05-claude-code-features.md"
LECTURE_INDEX = ROOT / "site" / "dist" / "lectures" / "index.html"
HOME = ROOT / "site" / "dist" / "index.html"
SITEMAP = ROOT / "site" / "dist" / "sitemap.xml"
VERCEL = ROOT / "vercel.json"


class CodexBeginnerMergeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.agent_html = AGENT.read_text(encoding="utf-8")
        cls.legacy_html = LEGACY.read_text(encoding="utf-8")
        cls.legacy_source = LEGACY_SOURCE.read_text(encoding="utf-8")
        cls.lecture_index = LECTURE_INDEX.read_text(encoding="utf-8")
        cls.home = HOME.read_text(encoding="utf-8")
        cls.sitemap = SITEMAP.read_text(encoding="utf-8")

    def test_canonical_agent_course_contains_codex_beginner_anchor(self) -> None:
        self.assertIn(
            "<title>AIエージェント講習 120分 — Codexで頼む・確かめる・残す | AI相談</title>",
            self.agent_html,
        )
        self.assertRegex(self.agent_html, r'id=["\']codex-beginner["\']')
        self.assertIn("60〜70分｜Codex初級：安全な作業場所を選ぶ", self.agent_html)
        self.assertIn("ChatGPTデスクトップアプリへサインイン", self.agent_html)
        self.assertIn("https://learn.chatgpt.com/docs/app", self.agent_html)
        self.assertIn('"dateModified": "2026-07-28"', self.agent_html)
        self.assertNotIn("Claude Codeに小さな修正を任せる", self.agent_html)
        self.assertNotIn("claude --version", self.agent_html)

    def test_legacy_source_is_hidden_but_generated_as_fallback(self) -> None:
        self.assertIn("listed: false", self.legacy_source)
        self.assertTrue(LEGACY.exists())
        self.assertIn("Codex初級はAIエージェント講習へ統合しました", self.legacy_html)
        self.assertIn(
            'href="./2026-04-ai-kihon.html#codex-beginner"',
            self.legacy_html,
        )
        self.assertNotIn("Claude Codeに小さな修正を任せる", self.legacy_html)

    def test_indexes_only_show_the_merged_course(self) -> None:
        self.assertIn("1. AIエージェント講習とCodex初級", self.lecture_index)
        self.assertIn("<b>5</b><span>受講資料</span>", self.lecture_index)
        self.assertIn("<b>4</b><span>目的別の学び方</span>", self.lecture_index)
        for html in (self.lecture_index, self.home):
            self.assertNotIn("/lectures/2026-05-claude-code-features.html", html)
        self.assertNotIn("3. AIと一緒に作る", self.lecture_index)
        self.assertIn("Codexを初めて使う人の基本講習", self.home)

    def test_permanent_redirect_points_to_existing_anchor_and_sitemap_is_canonical(self) -> None:
        redirects = json.loads(VERCEL.read_text(encoding="utf-8"))["redirects"]
        matched = [
            item
            for item in redirects
            if item.get("source") == "/lectures/2026-05-claude-code-features.html"
        ]
        self.assertEqual(len(matched), 1)
        self.assertEqual(
            matched[0]["destination"],
            "/lectures/2026-04-ai-kihon.html#codex-beginner",
        )
        self.assertIs(matched[0]["permanent"], True)
        fragment = matched[0]["destination"].split("#", 1)[1]
        self.assertRegex(self.agent_html, rf'id=["\']{re.escape(fragment)}["\']')
        self.assertNotIn(
            "https://aiclimb.vercel.app/lectures/2026-05-claude-code-features.html",
            self.sitemap,
        )
        self.assertIn(
            "https://aiclimb.vercel.app/lectures/2026-04-ai-kihon.html",
            self.sitemap,
        )


if __name__ == "__main__":
    unittest.main()

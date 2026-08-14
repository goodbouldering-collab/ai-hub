import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = ROOT / "site" / "ai_agent_readiness.py"
SITE_BUILDER_PATH = ROOT / "site" / "build_site.py"
PORTAL_PATH = ROOT / "site" / "build_portal.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AiAgentReadinessPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = load_module("ai_agent_readiness_under_test", RENDERER_PATH)
        cls.site_builder = load_module("site_builder_readiness_under_test", SITE_BUILDER_PATH)
        cls.portal = load_module("portal_readiness_under_test", PORTAL_PATH)
        cls.html = cls.renderer.render_ai_agent_readiness_page(
            site_url="https://aiclimb.vercel.app",
            nav_html="<header class='site-header'>共通ナビ</header>",
            favicon_html="<link rel='icon' href='/favicon.svg'>",
            shared_header_css=".site-header{position:fixed}",
        )

    def test_page_has_clickable_bilingual_product_name_and_100_point_promise(self):
        self.assertIn("AI Agent Readiness Compass", self.html)
        self.assertIn("AIエージェント実践力診断", self.html)
        self.assertIn("あなたはAIに聞く人か、任せて確かめる人か。", self.html)
        self.assertIn("20の仕事場面", self.html)
        self.assertIn("100点", self.html)
        self.assertIn("約4分", self.html)

    def test_page_explains_privacy_validity_and_future_indicator_boundaries(self):
        self.assertIn("回答はこのブラウザ内だけで計算", self.html)
        self.assertIn("サーバーへ送信しません", self.html)
        self.assertIn("学習用セルフチェック", self.html)
        self.assertIn("資格認定", self.html)
        self.assertIn("採用・適職判定", self.html)
        self.assertIn("未来予測ではありません", self.html)

    def test_page_has_accessible_assessment_shell_and_local_module_assets(self):
        self.assertIn("id='assessment-app'", self.html)
        self.assertIn("aria-live='polite'", self.html)
        self.assertIn("<progress", self.html)
        self.assertIn("<fieldset", self.html)
        self.assertIn("type='module' src='/ai-agent-readiness/app.mjs'", self.html)
        self.assertIn("href='/ai-agent-readiness/styles.css'", self.html)
        self.assertIn("<noscript>", self.html)

    def test_youtube_is_curated_and_loaded_only_after_a_click(self):
        self.assertIn("2gtWv3iib8M", self.html)
        self.assertIn("PLOI7QjtBx9_yavYb1jZZwQXgEa2HALAKQ", self.html)
        self.assertIn("K6KX41tLH2s", self.html)
        self.assertIn("px7XlbYgk7I", self.html)
        self.assertIn("OhI005_aJkA", self.html)
        self.assertIn("2026-08-13", self.html)
        self.assertIn("人気は正確性を保証しません", self.html)
        self.assertIn("data-video-consent", self.html)
        self.assertNotIn("<iframe", self.html)

    def test_primary_sources_are_linked_and_reference_video_is_not_a_scoring_source(self):
        self.assertIn("oecd.org", self.html)
        self.assertIn("unesco.org", self.html)
        self.assertIn("nist.gov", self.html)
        self.assertIn("anthropic.com/engineering/building-effective-agents", self.html)
        self.assertIn("openai.com/business/guides-and-resources/a-practical-guide", self.html)
        self.assertIn("ilo.org", self.html)
        self.assertIn("個別の主張や予測を、正答や閾値には使いません", self.html)

    def test_results_disclose_scoring_limits_and_own_service_relationship(self):
        self.assertIn("100点への追加点ではありません", self.html)
        self.assertIn("領域ごとに設問数は異なります", self.html)
        self.assertIn("統計的に標準化された基準ではありません", self.html)
        self.assertIn("AI相談が提供する自社サービス", self.html)
        self.assertIn("購入は任意", self.html)
        self.assertIn("90日行動は無料でも実践できます", self.html)

    def test_builder_writes_standalone_route_and_sitemap_includes_it(self):
        original_dist = self.site_builder.DIST
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self.site_builder.DIST = Path(tmp)
                self.assertTrue(self.site_builder.build_ai_agent_readiness_page())
                target = Path(tmp) / "ai-agent-readiness" / "index.html"
                self.assertTrue(target.exists())
                self.assertIn("AI Agent Readiness Compass", target.read_text(encoding="utf-8"))

                (Path(tmp) / "index.html").write_text("home", encoding="utf-8")
                self.site_builder.build_sitemap_and_robots()
                sitemap = (Path(tmp) / "sitemap.xml").read_text(encoding="utf-8")
                self.assertIn("<loc>https://aiclimb.vercel.app/ai-agent-readiness/</loc>", sitemap)
                self.assertNotIn("/ai-agent-readiness/index.html</loc>", sitemap)
        finally:
            self.site_builder.DIST = original_dist

    def test_homepage_keeps_quick_diagnosis_and_adds_full_readiness_route(self):
        hero = self.portal._render_hero_focused()
        self.assertIn("迷ったら60秒診断をはじめる", hero)
        self.assertIn("href='/ai-agent-readiness/'", hero)
        self.assertIn("AI Agent Readiness Compass", hero)
        self.assertIn("100点", hero)

    def test_deployable_readiness_bundle_is_not_ignored(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("!site/dist/ai-agent-readiness/", ignore)
        self.assertIn("!site/dist/ai-agent-readiness/**", ignore)


if __name__ == "__main__":
    unittest.main()

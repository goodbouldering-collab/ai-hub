import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
RENDERER_PATH = ROOT / "site" / "seo_llmo_diagnosis.py"
SITE_BUILDER_PATH = ROOT / "site" / "build_site.py"
PORTAL_PATH = ROOT / "site" / "build_portal.py"
STYLES_PATH = ROOT / "site" / "static" / "seo-llmo-diagnosis" / "styles.css"
APP_PATH = ROOT / "site" / "static" / "seo-llmo-diagnosis" / "app.mjs"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SeoLlmoDiagnosisPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.renderer = load_module("seo_llmo_diagnosis_under_test", RENDERER_PATH)
        cls.site_builder = load_module("site_builder_seo_llmo_under_test", SITE_BUILDER_PATH)
        cls.portal = load_module("portal_seo_llmo_under_test", PORTAL_PATH)
        cls.html = cls.renderer.render_seo_llmo_diagnosis_page(
            site_url="https://aiclimb.vercel.app",
            nav_html="<header class='site-header'>共通ナビ</header>",
            favicon_html="<link rel='icon' href='/favicon.svg'>",
            shared_header_css=".site-header{position:fixed}",
        )

    def test_public_page_leads_with_the_customer_question_and_clear_limit(self):
        self.assertIn("SEO・LLMO診断", self.html)
        self.assertIn("あなたのサイトは、検索とAIに正しく伝わっていますか？", self.html)
        self.assertIn("URLを入れて約1分", self.html)
        self.assertIn("検索順位やAI回答への掲載を保証するものではありません", self.html)
        self.assertIn("検索とAIに伝わる土台", self.html)

    def test_form_collects_only_public_site_context_and_posts_to_the_fixed_api(self):
        self.assertIn("id='seo-audit-form'", self.html)
        self.assertIn("name='url'", self.html)
        self.assertIn("name='audience'", self.html)
        self.assertIn("name='problem'", self.html)
        self.assertIn("name='desiredAction'", self.html)
        self.assertIn("name='isLocalBusiness'", self.html)
        self.assertIn("data-audit-endpoint='/api/seo-llmo-audit'", self.html)
        self.assertIn("個人情報や管理画面のURLは入力しないでください", self.html)
        self.assertIn("公開診断では入力内容を継続保存しません", self.html)
        self.assertIn("Codex深掘りを実行した場合のみ", self.html)
        self.assertIn("保護された中継キューへ一時保存", self.html)
        self.assertNotIn("name='prompt'", self.html)
        self.assertNotIn("name='cwd'", self.html)
        self.assertNotIn("name='skillPath'", self.html)

    def test_results_are_accessible_reusable_and_include_the_owner_only_codex_boundary(self):
        self.assertIn("id='audit-results'", self.html)
        self.assertIn("id='audit-result-title' tabindex='-1'", self.html)
        self.assertIn("aria-live='polite'", self.html)
        self.assertIn("id='copy-audit-result'", self.html)
        self.assertIn("id='print-audit-result'", self.html)
        self.assertIn("管理者向け：Codexで改善計画を深掘り", self.html)
        self.assertIn("管理者ログインと、このPCのbridge接続が必要", self.html)
        self.assertIn("data-relay-endpoint='/api/admin/command-center/relay'", self.html)
        self.assertIn("App Server自体は公開しません", self.html)
        self.assertIn("href='/admin/command-center/studio'", self.html)

        app = APP_PATH.read_text(encoding="utf-8")
        self.assertIn("item.evidence", app)
        self.assertIn("item.impact", app)
        self.assertIn("result.limitations", app)

    def test_result_supporting_text_uses_the_verified_contrast_color(self):
        styles = STYLES_PATH.read_text(encoding="utf-8")
        self.assertIn(".audit-priority__number { color: #52647a;", styles)
        self.assertIn("align-items: center; color: #52647a;", styles)

    def test_primary_sources_explain_normal_seo_and_openai_crawler_boundaries(self):
        self.assertIn("developers.google.com/search/docs/essentials", self.html)
        self.assertIn("developers.google.com/search/docs/appearance/ai-features", self.html)
        self.assertIn("developers.google.com/search/docs/fundamentals/ai-optimization-guide", self.html)
        self.assertIn("help.openai.com/en/articles/12627856", self.html)
        self.assertIn("OAI-SearchBot", self.html)
        self.assertIn("GPTBot", self.html)
        self.assertIn("AI専用ファイルを必須点にはしません", self.html)

    def test_builder_writes_the_route_and_sitemap_includes_it(self):
        original_dist = self.site_builder.DIST
        try:
            with tempfile.TemporaryDirectory() as tmp:
                self.site_builder.DIST = Path(tmp)
                self.assertTrue(self.site_builder.build_seo_llmo_diagnosis_page())
                target = Path(tmp) / "seo-llmo-diagnosis" / "index.html"
                self.assertTrue(target.exists())
                self.assertIn("SEO・LLMO診断", target.read_text(encoding="utf-8"))

                (Path(tmp) / "index.html").write_text("home", encoding="utf-8")
                self.site_builder.build_sitemap_and_robots()
                sitemap = (Path(tmp) / "sitemap.xml").read_text(encoding="utf-8")
                self.assertIn("<loc>https://aiclimb.vercel.app/seo-llmo-diagnosis/</loc>", sitemap)
                self.assertNotIn("/seo-llmo-diagnosis/index.html</loc>", sitemap)
        finally:
            self.site_builder.DIST = original_dist

    def test_homepage_places_the_seo_question_immediately_after_ai_readiness(self):
        home = self.portal.render_portal([], [])
        readiness = home.index("<section class='readiness-guide readiness-guide--compact'")
        seo = home.index("<section class='seo-llmo-guide'")
        main_course = home.index("<section class='focus-block main-course'")

        self.assertLess(readiness, seo)
        self.assertLess(seo, main_course)
        self.assertIn("あなたのサイトは、検索とAIに正しく伝わっていますか？", home)
        self.assertIn("href='/seo-llmo-diagnosis/'", home)
        self.assertIn("SEO・LLMO診断をはじめる", home)
        self.assertIn("aria-label='AI相談彦根 トップへ'", home)

        subpage_nav = self.site_builder.render_top_nav(path_prefix="../", include_run=False)
        self.assertIn("aria-label='AI相談彦根 トップへ'", subpage_nav)
        self.assertNotIn("aria-label='AI相談 彦根 トップへ'", subpage_nav)

    def test_deployable_bundle_is_not_ignored(self):
        ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("!site/dist/seo-llmo-diagnosis/", ignore)
        self.assertIn("!site/dist/seo-llmo-diagnosis/**", ignore)


if __name__ == "__main__":
    unittest.main()

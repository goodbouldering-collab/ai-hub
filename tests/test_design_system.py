import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SITE_DIR = ROOT / "site"
if str(SITE_DIR) not in sys.path:
    sys.path.insert(0, str(SITE_DIR))

import build_portal  # noqa: E402
import build_site  # noqa: E402


class DesignSystemBuildTests(unittest.TestCase):
    def test_public_top_loads_canonical_tokens_before_page_styles(self):
        html = build_portal.render_portal([], [])
        token_index = html.index("/design-system/tokens.css")
        inline_style_index = html.index("<style>")

        self.assertLess(token_index, inline_style_index)
        self.assertIn("<main", html)
        self.assertIn("迷ったら60秒診断をはじめる", html)

    def test_static_build_packages_the_design_reference_and_tokens(self):
        original_dist = build_site.DIST
        try:
            with tempfile.TemporaryDirectory() as directory:
                build_site.DIST = Path(directory)
                build_site.copy_static()

                reference = build_site.DIST / "design-system" / "index.html"
                tokens = build_site.DIST / "design-system" / "tokens.css"
                stylesheet = build_site.DIST / "design-system" / "design-system.css"

                self.assertTrue(reference.is_file())
                self.assertTrue(tokens.is_file())
                self.assertTrue(stylesheet.is_file())
                self.assertIn("AI相談 統合デザインシステム", reference.read_text(encoding="utf-8"))
        finally:
            build_site.DIST = original_dist

    def test_public_checkout_actions_use_the_shared_minimum_tap_size(self):
        self.assertIn(
            ".compact-course-checkout button {",
            build_portal.FOCUSED_PORTAL_CSS,
        )
        self.assertIn(
            "min-height:var(--ai-size-tap,44px);",
            build_portal.FOCUSED_PORTAL_CSS,
        )


if __name__ == "__main__":
    unittest.main()

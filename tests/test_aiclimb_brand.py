import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"


def load_portal():
    spec = importlib.util.spec_from_file_location("portal_aiclimb_brand", PORTAL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AIclimbBrandTest(unittest.TestCase):
    def test_homepage_makes_aiclimb_the_visible_brand_and_keeps_ai_consultation_searchable(self):
        portal = load_portal()

        homepage = portal.render_portal([], [])

        self.assertEqual(portal.SITE_BRAND, "AIclimb")
        self.assertIn("AIclimb（エーアイクライム）", homepage)
        self.assertIn(
            "<h1 class='focus-title'><span class='focus-title-first'>使えるAI、教えます。</span>"
            "<br><span class='focus-title-line'><strong>講習・導入・代行</strong></span></h1>",
            homepage,
        )
        self.assertIn("AI相談・業務改善・伴走支援", homepage)
        self.assertIn("まずは困っている仕事を相談する", homepage)

    def test_metadata_keeps_aiclimb_and_ai_consultation_together(self):
        portal = load_portal()

        metadata = portal._build_jsonld_website()

        self.assertIn('"name": "AIclimb"', metadata)
        self.assertIn('"AI相談"', metadata)


if __name__ == "__main__":
    unittest.main()

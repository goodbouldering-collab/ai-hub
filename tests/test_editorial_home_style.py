import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"


def load_portal():
    spec = importlib.util.spec_from_file_location("editorial_home_portal", PORTAL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class EditorialHomeStyleTests(unittest.TestCase):
    def test_rendered_top_keeps_the_approved_photo_under_the_editorial_skin(self):
        page = load_portal().render_portal([], [])

        self.assertIn("url('/img/hero-ai-consult-hikone.png')", page)
        self.assertIn("--editorial-paper:#fbfaf4;", page)
        self.assertIn("font-family:'Noto Serif JP'", page)

    def test_editorial_skin_keeps_primary_actions_and_mobile_hero_layout(self):
        page = load_portal().render_portal([], [])

        self.assertIn("まずは困っている仕事を相談する", page)
        self.assertIn("AIエージェント講習を見る", page)
        self.assertIn(".editorial-home-skin .focus-hero-shell", page)
        self.assertIn("grid-template-columns:1fr;", page)


if __name__ == "__main__":
    unittest.main()

import importlib.util
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "site" / "build_portal.py"
SPEC = importlib.util.spec_from_file_location("natural_scroll_portal", MODULE_PATH)
portal = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(portal)


class NaturalPageScrollTest(unittest.TestCase):
    def test_root_uses_one_native_vertical_scroll(self) -> None:
        css = portal.PORTAL_CSS + portal.FOCUSED_PORTAL_CSS

        self.assertRegex(
            css,
            r"html, body\s*\{[^}]*overflow-x:\s*clip[^}]*overflow-y:\s*visible",
        )
        self.assertNotRegex(css, r"html\s*\{\s*scroll-behavior:\s*smooth")
        self.assertNotRegex(
            css,
            r"(?:html|body)[^{]*\{[^}]*scroll-snap-type:\s*y",
        )

    def test_hero_is_ready_without_an_entrance_pause(self) -> None:
        hero = portal._render_hero_focused()

        self.assertIn("class='focus-hero-copy focus-hero-copy--app-site'", hero)
        self.assertNotIn("class='focus-hero-copy fade-up'", hero)

    def test_page_does_not_add_wheel_or_touch_scroll_interception(self) -> None:
        page = portal.render_portal([], [])

        self.assertIsNone(re.search(r"addEventListener\(['\"](?:wheel|touchmove)", page))


if __name__ == "__main__":
    unittest.main()

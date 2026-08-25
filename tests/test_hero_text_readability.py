import importlib.util
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "site" / "build_portal.py"
OUTPUT = ROOT / "site" / "dist" / "index.html"


def load_portal():
    spec = importlib.util.spec_from_file_location("portal_hero_copy", SOURCE)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class HeroTextReadabilityTests(unittest.TestCase):
    def assert_typography_contract(self, css: str) -> None:
        expected_rules = (
            r"\.focus-trust\s*\{[^}]*font-size:15px;[^}]*line-height:1\.5;",
            r"\.hero-advantage-number span\s*\{[^}]*font-size:13px;[^}]*line-height:1\.2;",
            r"\.hero-advantage-copy small\s*\{[^}]*font:900 13px/1\.35",
            r"\.hero-advantage-copy p\s*\{[^}]*font-size:clamp\(22px,2\.1vw,28px\);",
            r"\.hero-advantage-pillars li\s*\{[^}]*font-size:14px;[^}]*line-height:1\.45;",
            r"\.focus-trust\s*\{[^}]*font-size:14px;[^}]*line-height:1\.5;",
            r"\.hero-advantage-number span\s*\{[^}]*font-size:12px;[^}]*line-height:1\.2;",
            r"\.hero-advantage-copy small\s*\{[^}]*font-size:11px;[^}]*line-height:1\.3;",
            r"\.hero-advantage-copy p\s*\{[^}]*font-size:clamp\(18px,4\.8vw,20px\);",
            r"\.hero-advantage-pillars li\s*\{[^}]*font-size:12px;[^}]*line-height:1\.45;",
        )
        for pattern in expected_rules:
            with self.subTest(pattern=pattern):
                self.assertRegex(css, re.compile(pattern, re.DOTALL))

    def test_source_keeps_annotated_hero_text_readable(self) -> None:
        self.assert_typography_contract(SOURCE.read_text(encoding="utf-8"))

    def test_generated_homepage_keeps_annotated_hero_text_readable(self) -> None:
        self.assert_typography_contract(OUTPUT.read_text(encoding="utf-8"))

    def test_homepage_uses_short_online_availability_copy(self) -> None:
        homepage = load_portal().render_portal([], [])

        self.assertIn("<li>対面・オンライン可</li>", homepage)
        self.assertNotIn("<li>対面・オンライン対応</li>", homepage)


if __name__ == "__main__":
    unittest.main()

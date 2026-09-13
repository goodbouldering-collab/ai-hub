import importlib.util
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


portal = load_module("speaker_achievements_portal", ROOT / "site" / "build_portal.py")
site_builder = load_module("speaker_achievements_site", ROOT / "site" / "build_site.py")


class SpeakerAchievementsTest(unittest.TestCase):
    def test_home_instructor_link_opens_the_career_section(self):
        rendered = portal._render_focused_main()

        self.assertIn("href='/speaker.html#career'", rendered)
        self.assertIn("講師のプロフィールを見る", rendered)

    def test_speaker_page_shows_career_without_duplicate_achievements(self):
        self.assertTrue(site_builder.build_speaker_page())
        rendered = (ROOT / "site" / "dist" / "speaker.html").read_text(encoding="utf-8")

        self.assertIn('id="career"', rendered)
        self.assertIn("href='#career'", rendered)
        self.assertIn("製造業で、現場を変える仕組みづくり", rendered)
        self.assertNotIn("id='achievements'", rendered)
        self.assertNotIn("href='#achievements'", rendered)
        self.assertNotIn("公開中の実績サイト", rendered)


if __name__ == "__main__":
    unittest.main()

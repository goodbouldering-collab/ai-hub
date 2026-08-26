import importlib.util
from pathlib import Path
import unittest


PORTAL_PATH = Path(__file__).resolve().parents[1] / "site" / "build_portal.py"
SPEC = importlib.util.spec_from_file_location("build_portal", PORTAL_PATH)
build_portal = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(build_portal)


class FocusHeroInstructorAchievementsLinkTest(unittest.TestCase):
    def test_instructor_section_links_to_the_existing_speaker_page(self):
        rendered = build_portal._render_focused_main()

        self.assertIn("href='/speaker.html'", rendered)
        self.assertNotIn("href='/speaker.html#career'", rendered)
        self.assertIn("講師の実績を見る", rendered)

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
    def test_home_instructor_link_opens_the_achievements_section(self):
        rendered = portal._render_focused_main()

        self.assertIn("href='/speaker.html#achievements'", rendered)
        self.assertIn("講師の実績を見る", rendered)

    def test_speaker_page_links_to_curated_public_achievements(self):
        self.assertTrue(site_builder.build_speaker_page())
        rendered = (ROOT / "site" / "dist" / "speaker.html").read_text(encoding="utf-8")

        self.assertIn("id='achievements'", rendered)
        self.assertIn("公開中の実績サイト", rendered)
        self.assertIn("href='/#all-works'", rendered)
        for url in (
            "https://minnanowa.net",
            "https://n-design.work",
            "https://business21.aiclimb.workers.dev",
            "https://notesthe.com",
            "https://shoes.goodbouldering.com",
            "https://fadie.aiclimb.workers.dev",
        ):
            with self.subTest(url=url):
                self.assertIn(f"href='{url}'", rendered)


if __name__ == "__main__":
    unittest.main()

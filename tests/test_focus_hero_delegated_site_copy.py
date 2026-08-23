import unittest
from pathlib import Path


class FocusHeroDelegatedSiteCopyTest(unittest.TestCase):
    def test_focus_hero_mentions_delegated_ai_site_migration(self):
        portal_source = (Path(__file__).resolve().parents[1] / "site" / "build_portal.py").read_text(encoding="utf-8")

        self.assertIn("代行作成も対応。自由に変えられるAIサイトへ。", portal_source)
        self.assertIn("代行作成で、自由に瞬時に変更できるAIサイトへ移行できます。", portal_source)
        self.assertIn("focus-delegated-note", portal_source)

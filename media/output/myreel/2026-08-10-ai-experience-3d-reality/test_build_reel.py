from __future__ import annotations

import importlib.util
import hashlib
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_reel.py")


class ExperienceRealityReelContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("build_reel", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load {MODULE_PATH}")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_five_scenes_match_the_article_and_full_narration(self) -> None:
        expected = [
            ["ブログ", "AI時代、経験者が再び強くなる理由"],
            ["AIは", "仮説を速くつくれる"],
            ["現実で試し、", "確かめるのは人間"],
            ["経験は、AIの答えを", "使える形へ直す"],
            ["AIと人間と現実", "この往復が仕事を強くする"],
        ]

        self.assertEqual(self.module.BLOG_URL, "https://ai-hub-jp.vercel.app/blog/2026-08-09-ai-experience-3d-reality.html")
        self.assertEqual(self.module.ACCOUNT, "@climbingconsul")
        self.assertEqual(self.module.ARTICLE_TITLE, "AI時代、経験者が再び強くなる理由")
        self.assertEqual([beat["text"] for beat in self.module.BEATS], expected)
        self.assertEqual(len(self.module.BEATS), 5)
        self.assertEqual(self.module.VOICE_RATE, "+0%")

        for beat in self.module.BEATS:
            self.assertLessEqual(len(beat["text"]), 3)
            self.assertEqual(
                self.module.spoken_words("".join(beat["text"])),
                self.module.spoken_words(beat["narration"]),
            )

    def test_original_bgm_and_voice_ducking_contract_are_preserved(self) -> None:
        self.assertTrue(callable(self.module.create_background_music))
        self.assertEqual(self.module.MUSIC_RIGHTS_BASIS, "self-generated/no external samples")
        self.assertGreaterEqual(self.module.estimated_ducking_db(-16.0), 5.0)
        self.assertLessEqual(self.module.estimated_ducking_db(-16.0), 7.0)

    def test_same_completed_mp4_is_registered_at_the_article_top(self) -> None:
        reel_root = MODULE_PATH.parent
        repo_root = self.module.REPO
        article_source = (repo_root / "content/blog/2026-08-09-ai-experience-3d-reality.md").read_text(encoding="utf-8")
        self.assertIn("video: /media/ai-experience-3d-20260810/reel.mp4", article_source)
        self.assertIn("video_poster: /media/ai-experience-3d-20260810/cover.png", article_source)
        self.assertIn("video_orientation: portrait", article_source)

        pairs = (
            (reel_root / "reel.mp4", repo_root / "site/static/media/ai-experience-3d-20260810/reel.mp4"),
            (reel_root / "cover.png", repo_root / "site/static/media/ai-experience-3d-20260810/cover.png"),
        )
        for package_asset, site_asset in pairs:
            self.assertTrue(package_asset.is_file(), package_asset)
            self.assertTrue(site_asset.is_file(), site_asset)
            self.assertEqual(
                hashlib.sha256(package_asset.read_bytes()).hexdigest(),
                hashlib.sha256(site_asset.read_bytes()).hexdigest(),
                package_asset.name,
            )


if __name__ == "__main__":
    unittest.main()

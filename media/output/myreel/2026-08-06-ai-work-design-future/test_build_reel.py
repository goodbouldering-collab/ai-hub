from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_reel.py")


class ReelContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("build_reel", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load {MODULE_PATH}")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_six_scenes_read_all_center_text_without_time_compression(self) -> None:
        self.assertEqual(len(self.module.BEATS), 6)
        self.assertAlmostEqual(sum(beat["duration_seconds"] for beat in self.module.BEATS), 28.8)
        for beat in self.module.BEATS:
            self.assertEqual(
                self.module.spoken_words("".join(beat["text"])),
                self.module.spoken_words(beat["narration"]),
            )
        self.assertEqual(self.module.VOICE_RATE, "+0%")

    def test_background_music_generator_and_center_text_line_limit_exist(self) -> None:
        self.assertTrue(callable(self.module.create_background_music))
        self.assertTrue(all(len(beat["text"]) <= 3 for beat in self.module.BEATS))

    def test_existing_five_center_text_scenes_are_unchanged(self) -> None:
        self.assertEqual(
            [beat["text"] for beat in self.module.BEATS[-5:]],
            [
                ["AIで仕事が", "速くなったのに", "なぜ決められない？"],
                ["AIが得意なのは", "作る・並べる", "選択肢を増やす"],
                ["人が担うのは", "目的・優先順位", "最後の責任"],
                ["これはデザインだけでなく", "すべての仕事の", "ワークデザイン"],
                ["任せる・決める・確かめる", "3つに分けて", "明日から使おう"],
            ],
        )

    def test_tts_punctuation_keeps_every_word_without_extra_long_pauses(self) -> None:
        narration = self.module.BEATS[0]["narration"]
        tts_text = self.module.tts_text(narration)
        self.assertEqual(tts_text, "AI時代にデザインは不要になるのか、仕事設計の視点から考えます")
        self.assertEqual(self.module.spoken_words(tts_text), self.module.spoken_words(narration))

    def test_sidechain_settings_target_about_six_decibels_of_ducking(self) -> None:
        reduction = self.module.estimated_ducking_db(-16.0)
        self.assertGreaterEqual(reduction, 5.0)
        self.assertLessEqual(reduction, 7.0)

    def test_review_metadata_is_consistent_in_every_generated_text_asset(self) -> None:
        expected_title = "AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」"
        expected_review_state = "約28.8秒 / 6場面 / review_ready_waiting_final_approval / 未投稿"
        self.assertEqual(self.module.ARTICLE_TITLE, expected_title)
        self.assertEqual(self.module.review_metadata_line(), expected_review_state)

        original_root = self.module.ROOT
        with tempfile.TemporaryDirectory() as temporary_directory:
            self.module.ROOT = Path(temporary_directory)
            try:
                self.module.write_text_assets({"checks": {}})
                for filename in (
                    "README.md",
                    "captions.md",
                    "narration.md",
                    "pre-post-confirmation.md",
                    "posting-manifest.json",
                    "qa.json",
                    "story.md",
                    "review.html",
                ):
                    generated = (self.module.ROOT / filename).read_text(encoding="utf-8")
                    self.assertIn(expected_title, generated, filename)
                    self.assertIn(expected_review_state, generated, filename)
            finally:
                self.module.ROOT = original_root


if __name__ == "__main__":
    unittest.main()

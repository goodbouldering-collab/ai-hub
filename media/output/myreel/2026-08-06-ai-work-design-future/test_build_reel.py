from __future__ import annotations

import importlib.util
import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


MODULE_PATH = Path(__file__).with_name("build_reel.py")


class ReelContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        spec = importlib.util.spec_from_file_location("build_reel", MODULE_PATH)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"Could not load {MODULE_PATH}")
        cls.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.module)

    def test_five_scenes_use_approved_designer_copy_at_normal_speed(self) -> None:
        expected = [
            ["AIでデザイナーは", "いらなくなる？"],
            ["AIなら", "ロゴもサイトも", "すぐ作れる"],
            ["人が担うのは", "お客様の話を聞き", "何を作るか決めること"],
            ["デザインを頼む人は", "サイトや資料も", "まとめて頼みたい"],
            ["AIはデザイナーの", "仕事を広げる", "最強の武器になる"],
        ]
        self.assertEqual([beat["text"] for beat in self.module.BEATS], expected)
        self.assertEqual(len(self.module.BEATS), 5)
        self.assertAlmostEqual(sum(beat["duration_seconds"] for beat in self.module.BEATS), 25.4)
        for beat in self.module.BEATS:
            self.assertEqual(
                self.module.spoken_words("".join(beat["text"])),
                self.module.spoken_words(beat["narration"]),
            )
        self.assertEqual(self.module.VOICE_RATE, "+0%")

    def test_background_music_generator_and_center_text_line_limit_exist(self) -> None:
        self.assertTrue(callable(self.module.create_background_music))
        self.assertTrue(all(len(beat["text"]) <= 3 for beat in self.module.BEATS))

    def test_third_scene_uses_hito_pronunciation_only_for_tts(self) -> None:
        beat = self.module.BEATS[2]
        self.assertEqual(beat["text"][0], "人が担うのは")
        self.assertIn("人が担う", beat["narration"])
        self.assertTrue(self.module.tts_input(beat).startswith("ひとがになうのは"))
        self.assertNotIn("にんがになう", self.module.tts_input(beat))

    def test_tts_punctuation_keeps_every_word_without_extra_long_pauses(self) -> None:
        narration = self.module.BEATS[0]["narration"]
        tts_text = self.module.tts_text(narration)
        self.assertEqual(tts_text, "AIでデザイナーはいらなくなる")
        self.assertEqual(self.module.spoken_words(tts_text), self.module.spoken_words(narration))

    def test_sidechain_settings_target_about_six_decibels_of_ducking(self) -> None:
        reduction = self.module.estimated_ducking_db(-16.0)
        self.assertGreaterEqual(reduction, 5.0)
        self.assertLessEqual(reduction, 7.0)

    def test_locate_ffmpeg_prefers_explicit_accessible_binary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            expected = Path(temporary_directory) / "ffmpeg.exe"
            expected.write_bytes(b"MZ")
            with patch.dict(os.environ, {"FFMPEG_BINARY": str(expected)}):
                try:
                    actual = self.module.locate_ffmpeg()
                except OSError as error:
                    self.fail(f"Explicit FFmpeg should bypass inaccessible fallback paths: {error}")
            self.assertEqual(actual, expected)

    def test_generated_audio_qa_records_measured_levels_rights_and_threshold_results(self) -> None:
        qa = json.loads(MODULE_PATH.with_name("qa.json").read_text(encoding="utf-8"))
        manifest = json.loads(MODULE_PATH.with_name("posting-manifest.json").read_text(encoding="utf-8"))
        measured = qa["audio_measurements"]

        self.assertEqual(measured["measurement_method"], "ffmpeg_volumedetect_rms_dbfs")
        self.assertEqual(measured["rights_basis"], "self-generated/no external samples")
        self.assertAlmostEqual(measured["music_input_gain_db"], -13.15, delta=0.1)
        self.assertGreaterEqual(
            measured["measured_ducking_db"],
            measured["thresholds"]["minimum_ducking_db"],
        )
        self.assertGreaterEqual(
            measured["narration_over_ducked_bgm_db"],
            measured["thresholds"]["minimum_narration_over_bgm_db"],
        )
        self.assertLessEqual(
            measured["ducked_bgm_mean_dbfs"],
            measured["thresholds"]["maximum_ducked_bgm_mean_dbfs"],
        )
        self.assertTrue(all(measured["checks"].values()))
        self.assertEqual(manifest["reel"]["audio"]["measured_qa"], measured)

        fresh = self.module.measure_audio_qa(
            MODULE_PATH.with_name("narration.m4a"),
            MODULE_PATH.with_name("background-music.wav"),
            MODULE_PATH.with_name("music-bed.wav"),
            MODULE_PATH.with_name("ducked-background-music.wav"),
            qa["narration"]["beats"],
        )
        for key in (
            "narration_mean_dbfs",
            "music_source_mean_dbfs",
            "music_bed_mean_dbfs",
            "ducked_bgm_mean_dbfs",
            "music_input_gain_db",
            "measured_ducking_db",
            "narration_over_ducked_bgm_db",
        ):
            self.assertAlmostEqual(fresh[key], measured[key], places=2, msg=key)

    def test_generated_package_matches_site_assets_and_all_machine_checks_pass(self) -> None:
        qa = json.loads(MODULE_PATH.with_name("qa.json").read_text(encoding="utf-8"))
        reel_root = MODULE_PATH.parent
        repo_root = self.module.REPO

        pairs = (
            (reel_root / "reel.mp4", repo_root / "site/static/video/blog-ai-work-design-future-20260806.mp4"),
            (reel_root / "cover.png", repo_root / "site/static/img/blog-ai-work-design-reel-cover-20260806.png"),
        )
        for package_asset, site_asset in pairs:
            self.assertTrue(package_asset.is_file(), package_asset)
            self.assertTrue(site_asset.is_file(), site_asset)
            self.assertEqual(
                hashlib.sha256(package_asset.read_bytes()).hexdigest(),
                hashlib.sha256(site_asset.read_bytes()).hexdigest(),
                package_asset.name,
            )

        expected_frames = [f"frame-{index:02d}.png" for index in range(1, 6)]
        expected_voice = [f"beat-{index:02d}-raw.mp3" for index in range(1, 6)]
        self.assertEqual(sorted(path.name for path in (reel_root / "frames").glob("frame-*.png")), expected_frames)
        self.assertEqual(sorted(path.name for path in (reel_root / "voice").glob("beat-*-raw.mp3")), expected_voice)

        self.assertEqual(qa["scene_count"], 5)
        self.assertAlmostEqual(qa["duration_seconds"], 25.4, places=2)
        self.assertTrue(all(qa["checks"].values()))

    def test_review_metadata_is_consistent_in_every_generated_text_asset(self) -> None:
        expected_title = "AI時代にデザインは不要になるのか？ むしろ必要になる「経験」と「仕事をデザインする力」"
        expected_review_state = "約25.4秒 / 5場面 / review_ready_waiting_final_approval / 未投稿"
        self.assertEqual(self.module.ARTICLE_TITLE, expected_title)
        self.assertEqual(self.module.review_metadata_line(), expected_review_state)

        original_root = self.module.ROOT
        audio_measurements = json.loads(MODULE_PATH.with_name("qa.json").read_text(encoding="utf-8"))[
            "audio_measurements"
        ]
        with tempfile.TemporaryDirectory() as temporary_directory:
            self.module.ROOT = Path(temporary_directory)
            try:
                self.module.write_text_assets(
                    {"checks": {}, "audio_measurements": audio_measurements}
                )
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

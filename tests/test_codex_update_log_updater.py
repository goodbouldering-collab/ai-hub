import importlib.util
from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
UPDATER_PATH = ROOT / "scripts" / "update_codex_update_log.py"


def _load_updater():
    spec = importlib.util.spec_from_file_location("codex_update_log_updater", UPDATER_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SOURCE_CURRENT = """# What's new

This weekly digest highlights ChatGPT and Codex features that can change how you work.

## August 17-21, 2026

### Share and continue Codex work

- **Shared thread snapshots:** [Share a read-only snapshot](https://learn.chatgpt.com/docs/use-chatgpt#share-a-read-only-snapshot-of-a-codex-thread) from the desktop app.
- **Unified pinned threads:** Keep pinned Codex chats in sync between desktop and iOS.

## August 10-14, 2026

### Earlier update

- **Import:** Bring existing setup into Codex.
"""

SOURCE_NEXT = """# What's new

This weekly digest highlights ChatGPT and Codex features that can change how you work.

## August 24-28, 2026

### Guide work from anywhere

- **Remote review:** [Review a Codex task from your phone](https://learn.chatgpt.com/docs/remote) and send follow-up instructions.
- **Safer sharing:** [Review shared content](https://learn.chatgpt.com/docs/use-chatgpt) before publishing a thread snapshot.

## August 17-21, 2026

### Share and continue Codex work

- **Shared thread snapshots:** [Share a read-only snapshot](https://learn.chatgpt.com/docs/use-chatgpt) from the desktop app.
"""

SOURCE_MISSED_WEEKS = """# What's new

This weekly digest highlights ChatGPT and Codex features that can change how you work.

## September 7-11, 2026

### Review Codex work remotely

- **Remote review:** [Review a Codex task from your phone](https://learn.chatgpt.com/docs/remote) and send follow-up instructions.
- **Safer sharing:** [Review shared content](https://learn.chatgpt.com/docs/use-chatgpt) before publishing a thread snapshot.

## August 24-28, 2026

### Guide Codex work from anywhere

- **Remote review:** [Review a Codex task from your phone](https://learn.chatgpt.com/docs/remote) and send follow-up instructions.
- **Safer sharing:** [Review shared content](https://learn.chatgpt.com/docs/use-chatgpt) before publishing a thread snapshot.

## August 17-21, 2026

### Share and continue Codex work

- **Shared thread snapshots:** [Share a read-only snapshot](https://learn.chatgpt.com/docs/use-chatgpt) from the desktop app.
"""

SOURCE_ROLLBACK = """# What's new

This weekly digest highlights ChatGPT and Codex features that can change how you work.

## August 10-14, 2026

### Earlier Codex work

- **Import:** [Bring existing setup into Codex](https://learn.chatgpt.com/docs/import) and continue the work with a reviewed configuration.
"""

CLI_RELEASE_CURRENT = """## Latest stable Codex CLI release

- **Codex CLI 0.149.0:** [Open the official release](https://github.com/openai/codex/releases/tag/rust-v0.149.0).
- Added `codex agents`, `codex queue`, and expanded `codex doctor` diagnostics for practical task management.
"""

CLI_RELEASE_NEXT = """## Latest stable Codex CLI release

- **Codex CLI 0.150.0:** [Open the official release](https://github.com/openai/codex/releases/tag/rust-v0.150.0).
- Added safer remote review and clearer diagnostics for practical Codex task management.
"""


def article_for(
    source_text: str,
    *,
    supplemental_source: str = "",
    supplemental_id: str = "",
) -> str:
    updater = _load_updater()
    period, block = updater.extract_latest_digest(source_text)
    combined = updater.combine_source_block(block, supplemental_source)
    fingerprint = updater.digest_fingerprint(combined)
    release_meta = f'\nsource_release_tag: "{supplemental_id}"' if supplemental_id else ""
    return f'''---
title: "Codexアップデート｜新機能とすぐ使える使い方【常時更新】"
date: "2026-08-21"
date_modified: "2026-08-21"
content_series: codex-update-log
source_period: "{period}"
source_fingerprint: "{fingerprint}"{release_meta}
image: "/img/blog-codex-update-log-hero-20260821.webp"
image_alt: "Codexの更新を仕事へつなぐ知的な観測装置"
hero_image: true
---

<!-- CODEX_UPDATE_CURRENT:BEGIN -->
<!-- source-fingerprint: {fingerprint} -->
Codexアップデートで、共有と並行作業が使いやすくなりました。

## 1. 作業内容を安全に共有

読み取り専用リンクで共有できます。

**使い方：** スレッドの共有を選びます。

**利用例：** 公開前に担当者へ確認してもらう。
<!-- CODEX_UPDATE_CURRENT:END -->

## 過去のアップデート要約

<!-- CODEX_UPDATE_ARCHIVE:BEGIN -->
<!-- source-fingerprint: seed-cli-0.148.0 -->
### 2026年8月18日｜CLI 0.148.0

会話の出力と分岐に対応し、長い作業を再利用しやすくなりました。
<!-- CODEX_UPDATE_ARCHIVE:END -->
'''


def next_editorial() -> dict:
    return {
        "hook": "Codexアップデートで、外出先からも作業を確認して続きを頼めるようになりました。",
        "summary": [
            "スマートフォンから進行中の作業を確認できます。",
            "共有前の確認手順も分かりやすくなりました。",
        ],
        "features": [
            {
                "title": "外出先から作業を確認",
                "what_changed": "進行中のCodexタスクをスマートフォンから確認できます。",
                "how_to": "Codex Remoteを開き、対象タスクを選びます。",
                "use_case": "移動中にサイト修正の進み具合を確認し、追加指示を送る。",
                "availability": "利用できる端末やプランは公式案内を確認してください。",
                "source_scope": "weekly",
                "source_evidence": "Review a Codex task from your phone",
                "source_url": "https://learn.chatgpt.com/docs/remote",
            },
            {
                "title": "共有前に内容を確認",
                "what_changed": "共有するスレッドの確認手順が整理されました。",
                "how_to": "共有画面で機密情報やファイルパスを見直します。",
                "use_case": "学校や施設の担当者へ、安全に作業結果を見せる。",
                "availability": "共有範囲はアカウント種別で異なります。",
                "source_scope": "weekly",
                "source_evidence": "Review shared content",
                "source_url": "https://learn.chatgpt.com/docs/use-chatgpt",
            },
        ],
        "other_updates": [],
        "previous_archive": {
            "title": "2026年8月21日｜共有と並行作業",
            "summary": "読み取り専用共有と複数作業の管理が加わり、確認と追加指示がしやすくなりました。",
        },
    }


class FakeResponse:
    def __init__(
        self,
        body: bytes,
        *,
        url: str = "https://learn.chatgpt.com/docs/whats-new.md",
        content_type: str = "text/markdown; charset=utf-8",
        status_code: int = 200,
    ) -> None:
        self.body = body
        self.url = url
        self.headers = {"Content-Type": content_type}
        self.status_code = status_code

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return False

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size: int):
        for index in range(0, len(self.body), chunk_size):
            yield self.body[index : index + chunk_size]


class CodexUpdateLogUpdaterTest(unittest.TestCase):
    def test_japan_today_does_not_depend_on_system_timezone_data(self) -> None:
        updater = _load_updater()

        self.assertEqual(updater.JAPAN_TIMEZONE.utcoffset(None), timedelta(hours=9))
        self.assertEqual(
            updater._japan_today(datetime(2026, 8, 20, 15, 30, tzinfo=timezone.utc)),
            date(2026, 8, 21),
        )

    def test_extracts_only_the_latest_weekly_digest(self) -> None:
        updater = _load_updater()

        period, block = updater.extract_latest_digest(SOURCE_CURRENT)

        self.assertEqual(period, "August 17-21, 2026")
        self.assertEqual(updater.parse_period_end(period), date(2026, 8, 21))
        self.assertIn("Shared thread snapshots", block)
        self.assertNotIn("Earlier update", block)

    def test_parses_weekly_periods_that_cross_new_year(self) -> None:
        updater = _load_updater()

        self.assertEqual(
            updater.parse_period_end("December 28-January 1, 2027"),
            date(2027, 1, 1),
        )
        self.assertEqual(
            updater.parse_period_end("December 28, 2026-January 1, 2027"),
            date(2027, 1, 1),
        )

    def test_skips_non_period_h2_before_the_latest_week(self) -> None:
        updater = _load_updater()
        prefaced = SOURCE_CURRENT.replace(
            "## August 17-21, 2026",
            "## About this digest\n\nCodex editorial notes with an official URL "
            "https://learn.chatgpt.com/docs/whats-new and enough explanatory text "
            "to exceed the old loose length guard safely.\n\n## August 17-21, 2026",
        )

        period, block = updater.extract_latest_digest(prefaced)

        self.assertEqual(period, "August 17-21, 2026")
        self.assertNotIn("About this digest", block)

    def test_older_official_period_is_rejected_without_writing(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            with self.assertRaises(ValueError):
                updater.update_article(
                    article_path,
                    SOURCE_ROLLBACK,
                    lambda *_: next_editorial(),
                    today=date(2026, 8, 22),
                )

            self.assertEqual(article_path.read_text(encoding="utf-8"), original)

    def test_catches_up_every_missed_week_from_oldest_to_newest(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        calls: list[str] = []

        def editor(_current: str, period: str, _block: str, _archive: bool) -> dict:
            calls.append(period)
            editorial = next_editorial()
            if period == "August 24-28, 2026":
                editorial["previous_archive"]["title"] = "2026年8月21日｜共有機能"
            else:
                editorial["previous_archive"]["title"] = "2026年8月28日｜遠隔確認"
            return editorial

        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            changed = updater.update_article(
                article_path,
                SOURCE_MISSED_WEEKS,
                editor,
                today=date(2026, 9, 12),
            )

            updated = article_path.read_text(encoding="utf-8")
            self.assertTrue(changed)
            self.assertEqual(calls, ["August 24-28, 2026", "September 7-11, 2026"])
            self.assertIn('source_period: "September 7-11, 2026"', updated)
            self.assertEqual(updated.count("2026年8月21日｜共有機能"), 1)
            self.assertEqual(updated.count("2026年8月28日｜遠隔確認"), 1)
            self.assertLess(
                updated.index("2026年8月28日｜遠隔確認"),
                updated.index("2026年8月21日｜共有機能"),
            )

    def test_missing_saved_period_stops_instead_of_silently_dropping_history(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        source_with_gap = SOURCE_MISSED_WEEKS.split("## August 17-21, 2026", 1)[0]
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            with self.assertRaises(ValueError):
                updater.update_article(
                    article_path,
                    source_with_gap,
                    lambda *_: next_editorial(),
                    today=date(2026, 9, 12),
                )

            self.assertEqual(article_path.read_text(encoding="utf-8"), original)

    def test_same_digest_is_a_byte_for_byte_no_op_and_skips_editor(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            changed = updater.update_article(
                article_path,
                SOURCE_CURRENT,
                lambda *_: self.fail("editor must not run for an unchanged digest"),
                today=date(2026, 8, 29),
            )

            self.assertFalse(changed)
            self.assertEqual(article_path.read_text(encoding="utf-8"), original)

    def test_new_digest_replaces_current_and_archives_previous_once(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            changed = updater.update_article(
                article_path,
                SOURCE_NEXT,
                lambda *_: next_editorial(),
                today=date(2026, 8, 29),
            )

            updated = article_path.read_text(encoding="utf-8")
            self.assertTrue(changed)
            self.assertIn('date_modified: "2026-08-29"', updated)
            self.assertIn('source_period: "August 24-28, 2026"', updated)
            self.assertIn('date: "2026-08-21"', updated)
            self.assertIn("content_series: codex-update-log", updated)
            self.assertIn('image: "/img/blog-codex-update-log-hero-20260821.webp"', updated)
            self.assertIn("## 1. 外出先から作業を確認", updated)
            self.assertEqual(updated.count("**利用例：**"), 2)
            self.assertEqual(updated.count("2026年8月21日｜共有と並行作業"), 1)
            self.assertLess(
                updated.index("2026年8月21日｜共有と並行作業"),
                updated.index("2026年8月18日｜CLI 0.148.0"),
            )

            changed_again = updater.update_article(
                article_path,
                SOURCE_NEXT,
                lambda *_: self.fail("editor must not run twice"),
                today=date(2026, 8, 30),
            )
            self.assertFalse(changed_again)
            self.assertEqual(article_path.read_text(encoding="utf-8"), updated)

    def test_same_period_refreshes_current_without_archiving_it(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        corrected = SOURCE_CURRENT.replace("desktop app.", "desktop app with a review step.")
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            editorial = next_editorial()
            editorial["features"] = [
                {
                    "title": "作業内容を安全に共有",
                    "what_changed": "Codexの作業を読み取り専用リンクで共有できます。",
                    "how_to": "デスクトップアプリで対象スレッドの共有を選びます。",
                    "use_case": "サイト修正を公開前に担当者へ確認してもらう。",
                    "availability": "共有前に機密情報が残っていないか確認してください。",
                    "source_scope": "weekly",
                    "source_evidence": "Share a read-only snapshot",
                    "source_url": "https://learn.chatgpt.com/docs/use-chatgpt#share-a-read-only-snapshot-of-a-codex-thread",
                }
            ]
            editorial["previous_archive"] = None
            changed = updater.update_article(
                article_path,
                corrected,
                lambda *_: editorial,
                today=date(2026, 8, 22),
            )

            updated = article_path.read_text(encoding="utf-8")
            self.assertTrue(changed)
            self.assertNotIn("2026年8月21日｜共有と並行作業", updated)
            self.assertIn("2026年8月18日｜CLI 0.148.0", updated)

    def test_dash_style_change_is_the_same_period_not_a_new_archive(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        corrected = SOURCE_CURRENT.replace("August 17-21", "August 17–21").replace(
            "desktop app.", "desktop app after a review step."
        )
        editorial = next_editorial()
        editorial["features"] = [
            {
                "title": "作業内容を安全に共有",
                "what_changed": "Codexの作業を読み取り専用リンクで共有できます。",
                "how_to": "デスクトップアプリで対象スレッドの共有を選びます。",
                "use_case": "サイト修正を公開前に担当者へ確認してもらう。",
                "availability": "共有前に機密情報が残っていないか確認してください。",
                "source_scope": "weekly",
                "source_evidence": "Share a read-only snapshot",
                "source_url": "https://learn.chatgpt.com/docs/use-chatgpt#share-a-read-only-snapshot-of-a-codex-thread",
            }
        ]
        editorial["previous_archive"] = None
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            updater.update_article(
                article_path,
                corrected,
                lambda *_: editorial,
                today=date(2026, 8, 22),
            )

            updated = article_path.read_text(encoding="utf-8")
            self.assertNotIn("2026年8月21日｜共有と並行作業", updated)

    def test_cli_release_change_triggers_update_and_archives_current(self) -> None:
        updater = _load_updater()
        original = article_for(
            SOURCE_CURRENT,
            supplemental_source=CLI_RELEASE_CURRENT,
            supplemental_id="rust-v0.149.0",
        )
        editorial = next_editorial()
        editorial["features"] = [
            {
                "title": "新しいCLI更新を試す",
                "what_changed": "Codex CLIの安定版に実用的な改善が加わりました。",
                "how_to": "公式リリースを確認してからCodex CLIを更新します。",
                "use_case": "地域事業者の作業環境で更新内容を一つずつ試す。",
                "availability": "安定版を利用する人が対象です。",
                "source_scope": "cli_release",
                "source_evidence": "Added safer remote review and clearer diagnostics",
                "source_url": "https://github.com/openai/codex/releases/tag/rust-v0.150.0",
            }
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            changed = updater.update_article(
                article_path,
                SOURCE_CURRENT,
                lambda *_: editorial,
                today=date(2026, 8, 22),
                supplemental_source=CLI_RELEASE_NEXT,
                supplemental_id="rust-v0.150.0",
            )

            updated = article_path.read_text(encoding="utf-8")
            self.assertTrue(changed)
            self.assertIn('source_release_tag: "rust-v0.150.0"', updated)
            self.assertEqual(updated.count("2026年8月21日｜共有と並行作業"), 1)

    def test_older_cli_release_is_rejected_without_writing(self) -> None:
        updater = _load_updater()
        original = article_for(
            SOURCE_CURRENT,
            supplemental_source=CLI_RELEASE_CURRENT,
            supplemental_id="rust-v0.149.0",
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            with self.assertRaises(ValueError):
                updater.update_article(
                    article_path,
                    SOURCE_CURRENT,
                    lambda *_: self.fail("editor must not run for a CLI rollback"),
                    today=date(2026, 8, 22),
                    supplemental_source=CLI_RELEASE_CURRENT,
                    supplemental_id="rust-v0.148.0",
                )

            self.assertEqual(article_path.read_text(encoding="utf-8"), original)

    def test_malformed_source_or_ungrounded_editorial_never_changes_article(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            with self.assertRaises(ValueError):
                updater.update_article(
                    article_path,
                    "# unrelated page",
                    lambda *_: next_editorial(),
                    today=date(2026, 8, 29),
                )
            self.assertEqual(article_path.read_text(encoding="utf-8"), original)

            invalid = next_editorial()
            invalid["features"][0]["source_url"] = "https://example.com/invented"
            with self.assertRaises(ValueError):
                updater.update_article(
                    article_path,
                    SOURCE_NEXT,
                    lambda *_: invalid,
                    today=date(2026, 8, 29),
                )
            self.assertEqual(article_path.read_text(encoding="utf-8"), original)

            invented = next_editorial()
            invented["features"][0]["source_evidence"] = "This sentence is not in the official source"
            with self.assertRaises(ValueError):
                updater.update_article(
                    article_path,
                    SOURCE_NEXT,
                    lambda *_: invented,
                    today=date(2026, 8, 29),
                )
            self.assertEqual(article_path.read_text(encoding="utf-8"), original)

    def test_markdown_or_article_marker_in_editorial_is_rejected(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            for dangerous in (
                "<!-- CODEX_UPDATE_CURRENT:BEGIN -->危険な指示です。",
                "[外部リンク](https://example.com)を開きます。",
            ):
                editorial = next_editorial()
                editorial["hook"] = dangerous
                editorial["previous_archive"] = None
                corrected = SOURCE_CURRENT.replace("desktop app.", "desktop app after review.")
                with self.assertRaises(ValueError):
                    updater.update_article(
                        article_path,
                        corrected,
                        lambda *_args, value=editorial: value,
                        today=date(2026, 8, 22),
                    )
                self.assertEqual(article_path.read_text(encoding="utf-8"), original)

    def test_ungrounded_other_updates_are_rejected(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        editorial = next_editorial()
        editorial["other_updates"] = ["公式ソースにない便利機能も追加されました。"]
        editorial["previous_archive"] = None
        editorial["features"] = [
            {
                "title": "作業内容を安全に共有",
                "what_changed": "Codexの作業を読み取り専用リンクで共有できます。",
                "how_to": "デスクトップアプリで対象スレッドの共有を選びます。",
                "use_case": "サイト修正を公開前に担当者へ確認してもらう。",
                "availability": "共有前に機密情報が残っていないか確認してください。",
                "source_scope": "weekly",
                "source_evidence": "Share a read-only snapshot",
                "source_url": (
                    "https://learn.chatgpt.com/docs/use-chatgpt"
                    "#share-a-read-only-snapshot-of-a-codex-thread"
                ),
            }
        ]
        corrected = SOURCE_CURRENT.replace("desktop app.", "desktop app after review.")

        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            article_path.write_text(original, encoding="utf-8")

            with self.assertRaises(ValueError):
                updater.update_article(
                    article_path,
                    corrected,
                    lambda *_: editorial,
                    today=date(2026, 8, 22),
                )

            self.assertEqual(article_path.read_text(encoding="utf-8"), original)

    def test_duplicate_markers_or_fingerprints_are_rejected_before_editing(self) -> None:
        updater = _load_updater()
        original = article_for(SOURCE_CURRENT)
        fingerprint = updater.digest_fingerprint(
            updater.combine_source_block(updater.extract_latest_digest(SOURCE_CURRENT)[1])
        )
        corruptions = (
            original.replace(
                "<!-- CODEX_UPDATE_CURRENT:END -->",
                "<!-- CODEX_UPDATE_CURRENT:BEGIN -->\n<!-- CODEX_UPDATE_CURRENT:END -->",
            ),
            original.replace(
                "<!-- CODEX_UPDATE_ARCHIVE:BEGIN -->",
                f"<!-- CODEX_UPDATE_ARCHIVE:BEGIN -->\n<!-- source-fingerprint: {fingerprint} -->",
            ),
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            article_path = Path(temp_dir) / "codex-update-log.md"
            for corrupted in corruptions:
                article_path.write_text(corrupted, encoding="utf-8")
                with self.assertRaises(ValueError):
                    updater.update_article(
                        article_path,
                        SOURCE_NEXT,
                        lambda *_: self.fail("editor must not run for corrupt article"),
                        today=date(2026, 8, 29),
                    )
                self.assertEqual(article_path.read_text(encoding="utf-8"), corrupted)

    def test_fetches_and_validates_latest_stable_cli_release(self) -> None:
        updater = _load_updater()
        payload = {
            "tag_name": "rust-v0.149.0",
            "html_url": "https://github.com/openai/codex/releases/tag/rust-v0.149.0",
            "published_at": "2026-08-20T21:04:55Z",
            "draft": False,
            "prerelease": False,
            "body": "## New Features\n\n- Added practical Codex task management and diagnostics. " * 3,
        }

        tag, block = updater.fetch_latest_cli_release(
            requester=lambda *_args, **_kwargs: FakeResponse(
                json.dumps(payload).encode(),
                url="https://api.github.com/repos/openai/codex/releases/latest",
                content_type="application/json; charset=utf-8",
            )
        )

        self.assertEqual(tag, "rust-v0.149.0")
        self.assertIn(payload["html_url"], block)
        self.assertIn("Added practical Codex", block)

        payload["prerelease"] = True
        with self.assertRaises(ValueError):
            updater.fetch_latest_cli_release(
                requester=lambda *_args, **_kwargs: FakeResponse(
                    json.dumps(payload).encode(),
                    url="https://api.github.com/repos/openai/codex/releases/latest",
                    content_type="application/json",
                )
            )

    def test_fetch_rejects_unofficial_redirect_html_and_oversized_sources(self) -> None:
        updater = _load_updater()

        with self.assertRaises(ValueError):
            updater.fetch_source(
                requester=lambda *_args, **_kwargs: FakeResponse(
                    SOURCE_CURRENT.encode(), url="https://example.com/redirected"
                )
            )

        with self.assertRaises(ValueError):
            updater.fetch_source(
                requester=lambda *_args, **_kwargs: FakeResponse(
                    SOURCE_CURRENT.encode(), content_type="text/html"
                )
            )

        with self.assertRaises(ValueError):
            updater.fetch_source(
                requester=lambda *_args, **_kwargs: FakeResponse(
                    b"x" * (updater.MAX_SOURCE_BYTES + 1)
                )
            )

    def test_scheduled_workflow_is_scoped_to_the_fixed_article(self) -> None:
        workflow = (ROOT / ".github" / "workflows" / "codex-update-log.yml").read_text(
            encoding="utf-8"
        )

        self.assertIn("schedule:", workflow)
        self.assertIn("workflow_dispatch:", workflow)
        self.assertIn("permissions:\n  contents: write", workflow)
        self.assertIn("python scripts/update_codex_update_log.py", workflow)
        self.assertIn("ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}", workflow)
        self.assertIn("git add content/blog/codex-update-log.md", workflow)
        self.assertIn("python scripts/verify_codex_update_production.py", workflow)
        self.assertIn("tests.test_codex_update_production_verifier", workflow)
        self.assertIn("fetch-depth: 0\n          ref: main", workflow)
        self.assertNotIn("if: steps.commit.outputs.changed == 'true'", workflow)
        self.assertNotIn("git add -A", workflow)
        self.assertNotIn("site/static/img", workflow)
        self.assertNotIn("actions: write", workflow)


if __name__ == "__main__":
    unittest.main()

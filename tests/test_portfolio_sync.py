import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sync_portfolio import (  # noqa: E402
    choose_canonical_url,
    deduplicate_items,
    normalize_identity,
    upsert_item,
)


class PortfolioSyncTests(unittest.TestCase):
    def test_name_normalization_ignores_width_spaces_and_punctuation(self):
        self.assertEqual(normalize_identity("Ｎ-デザイン"), normalize_identity("N デザイン"))

    def test_same_name_replaces_url_and_keeps_old_url_as_alias(self):
        items = [{"name": "トラスト", "slug": "trust", "url": "https://old.example"}]
        action, item = upsert_item(
            items,
            {"name": "トラスト", "slug": "trust", "url": "https://new.example", "status": "live"},
        )
        self.assertEqual(action, "updated")
        self.assertEqual(item["url"], "https://new.example")
        self.assertIn("https://old.example", item["aliases"])
        self.assertEqual(len(items), 1)

    def test_new_name_adds_one_item(self):
        items = []
        action, item = upsert_item(
            items,
            {"name": "新サイト", "slug": "new-site", "url": "https://new.example", "status": "live"},
        )
        self.assertEqual(action, "added")
        self.assertEqual(item["slug"], "new-site")
        self.assertEqual(len(items), 1)

    def test_source_id_updates_renamed_project_without_duplicate(self):
        items = [
            {
                "name": "旧名称",
                "slug": "old-name",
                "url": "https://old.example",
                "source_id": "prj_same",
            }
        ]
        action, item = upsert_item(
            items,
            {
                "name": "新名称",
                "slug": "new-name",
                "url": "https://new.example",
                "source_id": "prj_same",
            },
        )
        self.assertEqual(action, "updated")
        self.assertEqual(item["name"], "新名称")
        self.assertEqual(len(items), 1)

    def test_manual_hook_preserves_existing_vercel_identity(self):
        items = [
            {
                "name": "既存サイト",
                "slug": "existing",
                "url": "https://existing.example",
                "source": "vercel",
                "source_id": "prj_existing",
            }
        ]
        _, item = upsert_item(
            items,
            {
                "name": "既存サイト",
                "slug": "existing",
                "url": "https://existing.example",
                "source": "site-published-hook",
            },
        )
        self.assertEqual(item["source"], "vercel")
        self.assertEqual(item["source_id"], "prj_existing")

    def test_custom_domain_is_preferred_over_vercel_alias(self):
        url = choose_canonical_url(
            ["sample.vercel.app", "www.example.jp", "example.jp"],
            "sample",
        )
        self.assertEqual(url, "https://example.jp")

    def test_duplicate_name_is_merged(self):
        result, removed = deduplicate_items(
            [
                {"name": "同じサイト", "slug": "same", "url": "https://one.example"},
                {"name": "同じサイト", "slug": "same-2", "url": "https://two.example"},
            ]
        )
        self.assertEqual(removed, 1)
        self.assertEqual(len(result), 1)
        self.assertIn("https://two.example", result[0]["aliases"])


if __name__ == "__main__":
    unittest.main()

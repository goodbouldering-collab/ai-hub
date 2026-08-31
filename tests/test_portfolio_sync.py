import sys
import unittest
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

CLOUDFLARE_PUBLIC_URLS = {
    "ambassador": ("ambassador-roi", "https://ambassador.aiclimb.workers.dev"),
    "business21": ("business21", "https://business21.aiclimb.workers.dev"),
    "climbhero": ("climbhero", "https://project-02ceb497.pages.dev"),
    "fadie-v2": ("fadie", "https://fadie.aiclimb.workers.dev"),
    "hyrox-hongo": ("hyrox-hongo", "https://hyrox-hongo.aiclimb.workers.dev"),
    "japan-plogging-championship": (
        "japan-plogging-championship",
        "https://jpc.aiclimb.workers.dev",
    ),
    "nokosu": ("nokosu", "https://nokosu.aiclimb.workers.dev"),
    "profit-hikone": ("profit-hikone", "https://profit-hikone.aiclimb.workers.dev"),
    "rebuildmatch": ("rebuildmatch", "https://site-shindan.aiclimb.workers.dev"),
    "trusthikone": ("trust", "https://trusthikone.aiclimb.workers.dev"),
    "yamani": ("yamani", "https://yamani.aiclimb.workers.dev"),
    "yomogihikone": ("junpa", "https://junpa.aiclimb.workers.dev"),
}

LEGACY_PUBLIC_URLS = {
    "ambassador-roi": "https://ambassador-ashen.vercel.app",
    "business21": "https://business21.vercel.app",
    "climbhero": "https://climbhero.vercel.app",
    "fadie": "https://fadie-v2.vercel.app",
    "hyrox-hongo": "https://hyrox-zeta.vercel.app",
    "japan-plogging-championship": "https://japan-plogging-championship.vercel.app",
    "junpa": "https://yomogihikone.vercel.app",
    "nokosu": "https://nokosu-ten.vercel.app",
    "profit-hikone": "https://profit-hikone.vercel.app",
    "rebuildmatch": "https://site-shindan.vercel.app",
    "trust": "https://trusthikone.vercel.app",
    "yamani": "https://yamani.vercel.app",
}

from sync_portfolio import (  # noqa: E402
    choose_canonical_url,
    deduplicate_items,
    normalize_identity,
    upsert_item,
)


class PortfolioSyncTests(unittest.TestCase):
    def test_migrated_projects_use_cloudflare_public_urls_in_sync_config(self):
        config = yaml.safe_load((ROOT / "config" / "portfolio-sync.yaml").read_text(encoding="utf-8"))
        projects = config["vercel"]["projects"]

        for project_name, (_, expected_url) in CLOUDFLARE_PUBLIC_URLS.items():
            with self.subTest(project=project_name):
                self.assertEqual(projects[project_name]["canonical_url"], expected_url)

    def test_public_portfolio_uses_cloudflare_urls_and_keeps_previous_urls_as_aliases(self):
        data = yaml.safe_load((ROOT / "config" / "portfolio.yaml").read_text(encoding="utf-8"))
        items = {item["slug"]: item for item in data["portfolio"]}

        expected_urls = {slug: url for slug, url in CLOUDFLARE_PUBLIC_URLS.values()}
        for slug, expected_url in expected_urls.items():
            with self.subTest(slug=slug):
                item = items[slug]
                self.assertEqual(item["url"], expected_url)
                self.assertIn(LEGACY_PUBLIC_URLS[slug], item.get("aliases", []))

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

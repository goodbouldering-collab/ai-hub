import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"
APP_SITE_PATH = ROOT / "site" / "ai_app_site.py"

CODING_SQUARE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH"
)
INDIVIDUAL_COURSE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP"
)
FREE_CONSULT_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/AW5G3WME6GPYEI6ZCNHXLARH"
)
SUPPORT_SQUARE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/V57YTNICA2KV2TN7ENARAVQE"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AiAppSelfbuildOfferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.portal = load_module("portal_ai_app_selfbuild_under_test", PORTAL_PATH)
        cls.app_site = load_module("ai_app_selfbuild_page_under_test", APP_SITE_PATH)
        cls.page = cls.portal.render_portal([], [])

    def test_homepage_restores_separate_individual_and_coding_courses(self) -> None:
        cards = re.findall(
            r"<article class='compact-course-card[^']*'.*?</article>",
            self.page,
            re.DOTALL,
        )
        individual_card = next(card for card in cards if INDIVIDUAL_COURSE_URL in card)
        coding_card = next(card for card in cards if CODING_SQUARE_URL in card)

        self.assertEqual(6, len(cards))
        self.assertIn("<h3>AI個別講習</h3>", individual_card)
        self.assertIn("仕事に合うAIの使い方と、確認・運用の手順を整理します。", individual_card)
        self.assertIn("<h3>AIコーディング講習</h3>", coding_card)
        self.assertIn("AIが作ったコードを読み、直し、確認して公開する", coding_card)
        self.assertNotIn("AI自作講習", self.page)

    def test_support_card_restores_the_existing_square_booking_url(self) -> None:
        support_card = next(card for card in re.findall(
            r"<article class='compact-course-card[^']*'.*?</article>",
            self.page,
            re.DOTALL,
        ) if "<h3>AI伴走支援</h3>" in card)

        self.assertIn(f"href='{SUPPORT_SQUARE_URL}'", support_card)
        self.assertIn("伴走支援を申し込む", support_card)
        self.assertNotIn("/api/stripe/monthly-support", self.page)

    def test_structured_data_has_both_restored_offers_and_square_support(self) -> None:
        match = re.search(
            r"<script type='application/ld\+json'>(.*?)</script>",
            self.page,
            re.DOTALL,
        )
        self.assertIsNotNone(match)
        graph = json.loads(match.group(1))["@graph"]
        offers = {
            item["name"]: item
            for item in graph
            if item.get("@type") in ("Course", "Service")
        }

        self.assertEqual(
            INDIVIDUAL_COURSE_URL,
            offers["AI個別講習 60分"]["offers"]["url"],
        )
        self.assertEqual(
            CODING_SQUARE_URL,
            offers["AIコーディング講習 120分"]["offers"]["url"],
        )
        self.assertEqual(
            SUPPORT_SQUARE_URL,
            offers["AI伴走支援 いっしょに導入"]["offers"]["url"],
        )

    def test_ai_app_site_is_the_done_for_you_service_page(self) -> None:
        rendered = self.app_site.render_ai_app_site_page(
            "ai-app-site",
            "https://aiclimb.aiclimb.workers.dev",
            "<nav></nav>",
            "",
            "",
            FREE_CONSULT_URL,
        )

        self.assertIn("相談だけで終わらない。<br>AIで、仕事の仕組みまでつくる。", rendered)
        self.assertIn("99,000円〜", rendered)
        self.assertIn("AIアプリサイト Lite", rendered)
        self.assertIn(FREE_CONSULT_URL, rendered)
        self.assertNotIn("AI APP SITE · SELF BUILD", rendered)


if __name__ == "__main__":
    unittest.main()

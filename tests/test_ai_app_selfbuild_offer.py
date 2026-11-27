import importlib.util
import json
from pathlib import Path
import re
import unittest

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"
APP_SITE_PATH = ROOT / "site" / "ai_app_site.py"

RECORDING_SQUARE_URL = (
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

    def test_homepage_separates_individual_consultation_and_recording(self) -> None:
        cards = BeautifulSoup(self.page, "html.parser").select("#packages .compact-course-card")
        self.assertEqual(7, len(cards))
        individual = cards[0]
        self.assertEqual("AI個別相談120分｜AI時代のなんでも相談", individual.h3.get_text())
        self.assertEqual(INDIVIDUAL_COURSE_URL, individual.select_one("a.compact-course-action")["href"])
        self.assertIn("今知りたいAIの使い方と、その先の活用法", individual.get_text())
        recording = next(card for card in cards if card.get("id") == "voice-memo-course")
        self.assertEqual("AI録音講座｜音声から自動で顧客メモやスケジュール", recording.h3.get_text())
        self.assertEqual(RECORDING_SQUARE_URL, recording.select_one("a.compact-course-action")["href"])
        self.assertIn("自分のPCで動く小さなアプリ", recording.get_text())
        self.assertNotIn("AI自作講習", self.page)

    def test_support_card_keeps_its_existing_square_booking_url(self) -> None:
        cards = BeautifulSoup(self.page, "html.parser").select("#packages .compact-course-card")
        support = next(card for card in cards if card.h3.get_text().startswith("AI事業導入相談30分"))
        action = support.select_one("a.compact-course-action")
        self.assertEqual(SUPPORT_SQUARE_URL, action["href"])
        self.assertIn("初回無料・30分の相談を予約", action.get_text())
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
            offers["AI個別相談 120分"]["offers"]["url"],
        )
        self.assertEqual(
            RECORDING_SQUARE_URL,
            offers["AI録音講座｜音声から自動で顧客メモやスケジュール"]["offers"]["url"],
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

import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"
APP_SITE_PATH = ROOT / "site" / "ai_app_site.py"

SELFBUILD_SQUARE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH"
)
FREE_CONSULT_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/AW5G3WME6GPYEI6ZCNHXLARH"
)
SUPPORT_SQUARE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/V57YTNICA2KV2TN7ENARAVQE"
)
RETIRED_INDIVIDUAL_SQUARE_SERVICE_ID = "TO3XHZT6XP3OM4QBDYMW7TZP"


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

    def test_homepage_merges_paid_consultation_into_one_selfbuild_course(self) -> None:
        cards = re.findall(
            r"<article class='compact-course-card[^']*'.*?</article>",
            self.page,
            re.DOTALL,
        )
        selfbuild_card = next(card for card in cards if SELFBUILD_SQUARE_URL in card)

        self.assertEqual(4, len(cards))
        self.assertIn("<h3>AI自作講習</h3>", selfbuild_card)
        self.assertIn("サイトやアプリを自分で作って直せるようになる。", selfbuild_card)
        self.assertIn("公開できるまで個別に進めます。", selfbuild_card)
        self.assertIn("制作サービスと同じ流れを、自分で進める", selfbuild_card)
        for step in (
            "課題と完成形を決める",
            "画面と機能を設計する",
            "AIへ制作を依頼する",
            "変更を自分で確かめる",
            "直したい点をAIへ伝える",
            "公開前の安全確認をする",
            "本番へ公開する",
            "次も自分で直せる形に残す",
        ):
            self.assertIn(step, selfbuild_card)
        self.assertNotIn("<h3>AIアプリサイト自作講習・相談</h3>", self.page)
        self.assertNotIn("<h3>AI個別相談</h3>", self.page)
        self.assertNotIn("AI個別相談を予約", self.page)
        self.assertNotIn(RETIRED_INDIVIDUAL_SQUARE_SERVICE_ID, self.page)
        self.assertIn(SELFBUILD_SQUARE_URL, self.page)

    def test_support_card_restores_the_existing_square_booking_url(self) -> None:
        support_card = next(card for card in re.findall(
            r"<article class='compact-course-card[^']*'.*?</article>",
            self.page,
            re.DOTALL,
        ) if "<h3>AI伴走支援</h3>" in card)

        self.assertIn(f"href='{SUPPORT_SQUARE_URL}'", support_card)
        self.assertIn("伴走支援を申し込む", support_card)
        self.assertNotIn("/api/stripe/monthly-support", self.page)

    def test_structured_data_has_one_merged_offer_and_square_support(self) -> None:
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

        self.assertNotIn("AI個別相談 しっかり60分", offers)
        self.assertEqual(
            SELFBUILD_SQUARE_URL,
            offers["AIアプリサイト自作講習・相談 120分"]["offers"]["url"],
        )
        self.assertEqual(
            SUPPORT_SQUARE_URL,
            offers["AI伴走支援 いっしょに導入"]["offers"]["url"],
        )

    def test_ai_app_site_is_the_done_for_you_service_page(self) -> None:
        rendered = self.app_site.render_ai_app_site_page(
            "ai-app-site",
            "https://aiclimb.vercel.app",
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

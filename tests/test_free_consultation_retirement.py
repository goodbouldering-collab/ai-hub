import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
REMOTE_BLOG = ROOT / "site" / "dist" / "blog" / "2026-07-27-codex-remote-ssh-rdp.html"
SELFBUILD_CONSULT_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH"
)
FREE_CONSULT_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"
)
AI_AGENT_COURSE_URL = "https://goodbouldering.com/?pid=188553378"


class FreeConsultationRetirementTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.index_html = INDEX.read_text(encoding="utf-8")
        cls.remote_blog_html = REMOTE_BLOG.read_text(encoding="utf-8")
        modal_match = re.search(
            r"<div class='diagnose-modal'.*?</div></div>",
            cls.index_html,
            re.DOTALL,
        )
        if modal_match is None:
            raise AssertionError("Diagnosis modal was not generated")
        script_match = re.search(
            r"// ---- 迷ったら60秒診断.*?^  \}\)\(\);",
            cls.index_html,
            re.DOTALL | re.MULTILINE,
        )
        if script_match is None:
            raise AssertionError("Diagnosis script was not generated")
        app_site_match = re.search(
            r"<section class='home-app-site-guide'.*?</section>",
            cls.index_html,
            re.DOTALL,
        )
        if app_site_match is None:
            raise AssertionError("AI app site service section was not generated")
        cls.diagnosis_context = modal_match.group(0) + script_match.group(0)
        cls.app_site_context = app_site_match.group(0)
        cls.page_without_diagnosis_or_app_site = (
            cls.index_html.replace(modal_match.group(0), "")
            .replace(script_match.group(0), "")
            .replace(app_site_match.group(0), "")
        )
        json_ld_match = re.search(
            r"<script type='application/ld\+json'>(.*?)</script>",
            cls.index_html,
            re.DOTALL,
        )
        if json_ld_match is None:
            raise AssertionError("Homepage JSON-LD was not generated")
        cls.json_ld = json.loads(json_ld_match.group(1))

    def test_free_consultation_is_limited_to_diagnosis_and_ordered_app_site_intake(self) -> None:
        self.assertNotIn("無料相談", self.page_without_diagnosis_or_app_site)
        self.assertNotIn(FREE_CONSULT_URL, self.page_without_diagnosis_or_app_site)
        self.assertNotIn("無料相談", self.remote_blog_html)
        self.assertNotIn(FREE_CONSULT_URL, self.remote_blog_html)
        self.assertIn("無料相談", self.app_site_context)
        self.assertIn(FREE_CONSULT_URL, self.app_site_context)
        self.assertIn("無料相談で入口を整理したい", self.diagnosis_context)
        self.assertIn("free: {", self.diagnosis_context)
        self.assertIn(FREE_CONSULT_URL, self.diagnosis_context)

    def test_structured_data_lists_only_paid_entry_offers(self) -> None:
        paid_entries = [
            item
            for item in self.json_ld["@graph"]
            if item.get("@type") in ("Course", "Service")
        ]
        names = {entry["name"] for entry in paid_entries}
        self.assertNotIn("AI無料相談 入口整理", names)
        self.assertNotIn("0", [entry.get("offers", {}).get("price") for entry in paid_entries])

        selfbuild = next(
            entry
            for entry in paid_entries
            if entry["name"] == "AIアプリサイト自作講習・相談 120分"
        )
        self.assertEqual("11000", selfbuild["offers"]["price"])
        self.assertEqual(SELFBUILD_CONSULT_URL, selfbuild["offers"]["url"])
        self.assertNotIn("AI個別相談 しっかり60分", names)

        agent = next(
            entry
            for entry in paid_entries
            if entry["name"] == "AIエージェント講習 120分"
        )
        self.assertEqual(AI_AGENT_COURSE_URL, agent["offers"]["url"])

    def test_diagnosis_results_have_the_five_approved_routes(self) -> None:
        expected_routes = {
            "start": ("AIアプリサイト自作講習・相談を予約する", SELFBUILD_CONSULT_URL),
            "promotion": ("AIエージェント講習を予約する", AI_AGENT_COURSE_URL),
            "office": ("AIアプリサイト自作講習・相談を予約する", SELFBUILD_CONSULT_URL),
            "flow": ("AIアプリサイト自作講習・相談を予約する", SELFBUILD_CONSULT_URL),
            "free": ("無料相談の日程を選ぶ", FREE_CONSULT_URL),
        }
        for key, (label, url) in expected_routes.items():
            result_match = re.search(
                rf"{key}: \{{(?P<body>.*?)\n      \}},?",
                self.diagnosis_context,
                re.DOTALL,
            )
            self.assertIsNotNone(result_match, key)
            result_body = result_match.group("body")
            self.assertIn(f"bookingLabel: '{label}'", result_body)
            self.assertIn(f"bookingUrl: '{url}'", result_body)


if __name__ == "__main__":
    unittest.main()

import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
REMOTE_BLOG = ROOT / "site" / "dist" / "blog" / "2026-07-27-codex-remote-ssh-rdp.html"
INDIVIDUAL_CONSULT_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP"
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
        cls.diagnosis_context = modal_match.group(0) + script_match.group(0)
        cls.page_without_diagnosis = cls.index_html.replace(modal_match.group(0), "").replace(
            script_match.group(0), ""
        )
        json_ld_match = re.search(
            r"<script type='application/ld\+json'>(.*?)</script>",
            cls.index_html,
            re.DOTALL,
        )
        if json_ld_match is None:
            raise AssertionError("Homepage JSON-LD was not generated")
        cls.json_ld = json.loads(json_ld_match.group(1))

    def test_free_consultation_is_limited_to_the_diagnosis(self) -> None:
        self.assertNotIn("無料相談", self.page_without_diagnosis)
        self.assertNotIn(FREE_CONSULT_URL, self.page_without_diagnosis)
        self.assertNotIn("無料相談", self.remote_blog_html)
        self.assertNotIn(FREE_CONSULT_URL, self.remote_blog_html)
        self.assertIn("無料相談で入口を整理したい", self.diagnosis_context)
        self.assertIn("free: {", self.diagnosis_context)
        self.assertIn(FREE_CONSULT_URL, self.diagnosis_context)

    def test_structured_data_lists_only_paid_entry_offers(self) -> None:
        services = [
            item
            for item in self.json_ld["@graph"]
            if item.get("@type") == "Service"
        ]
        names = {service["name"] for service in services}
        self.assertNotIn("AI無料相談 入口整理", names)
        self.assertNotIn("0", [service.get("offers", {}).get("price") for service in services])

        individual = next(
            service
            for service in services
            if service["name"] == "AI個別相談 しっかり60分"
        )
        self.assertEqual("5500", individual["offers"]["price"])
        self.assertEqual(INDIVIDUAL_CONSULT_URL, individual["offers"]["url"])

        agent = next(
            service
            for service in services
            if service["name"] == "AIエージェント講習 120分"
        )
        self.assertEqual(AI_AGENT_COURSE_URL, agent["offers"]["url"])

    def test_diagnosis_results_have_the_five_approved_routes(self) -> None:
        expected_routes = {
            "start": ("AI個別相談を予約する", INDIVIDUAL_CONSULT_URL),
            "promotion": ("AIエージェント講習を予約する", AI_AGENT_COURSE_URL),
            "office": ("AI個別相談を予約する", INDIVIDUAL_CONSULT_URL),
            "flow": ("AI個別相談を予約する", INDIVIDUAL_CONSULT_URL),
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

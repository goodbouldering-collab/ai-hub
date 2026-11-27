import importlib.util
import json
from pathlib import Path
import re
import unittest

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"
PROGRAMMING_MAP = ROOT / "site" / "static" / "programming-map.html"
INDIVIDUAL_COURSE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP"
)
RECORDING_COURSE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH"
)


def load_portal():
    spec = importlib.util.spec_from_file_location("course_card_restoration_portal", PORTAL_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CourseCardRestorationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.page = load_portal().render_portal([], [])
        cls.cards = BeautifulSoup(cls.page, "html.parser").select("#packages .compact-course-card")

    def test_individual_courses_keep_their_audience_price_and_details(self) -> None:
        self.assertEqual(7, len(self.cards))
        self.assertEqual("individual-consultation", self.cards[0]["id"])
        self.assertEqual("AIエージェント講習", self.cards[1].h3.get_text())
        for card, title, audience, summaries in (
            (self.cards[0], "AI個別相談120分｜AI時代のなんでも相談", "お一人",
             ["メリット・内容・参加方法を見る", "受講された方の感想を見る"]),
            (self.cards[3], "AI録音講座｜音声から自動で顧客メモやスケジュール", "個別",
             ["メリット・120分の内容を見る", "受講後にできることを見る"]),
        ):
            with self.subTest(title=title):
                self.assertEqual(title, card.select_one(".compact-course-heading h3").get_text())
                self.assertEqual("受講人数", card.select_one(".offer-audience-label").get_text())
                self.assertEqual(audience, card.select_one(".offer-audience strong").get_text())
                self.assertEqual(["8,800円", "120分"], list(card.select_one(".compact-course-meta").stripped_strings))
                self.assertEqual(summaries, [node.get_text() for node in card.select("summary")])
        self.assertNotIn("AI自作講習", self.page)

    def test_course_descriptions_details_and_links(self) -> None:
        individual, recording = self.cards[0], self.cards[3]
        for text in ("企業支援と事業運営の経験を持つ講師", "最初にやる仕事が決まる",
                     "道具選びで迷わなくなる", "安全に使う範囲が分かる", "自分向けの進め方が残る", "こんな方におすすめ"):
            self.assertIn(text, individual.get_text())
        for text in ("自分のPCで動く小さなアプリ", "記録の書き直しを減らす", "次の対応を思い出しやすくする",
                     "自分の仕事に合わせて育てる", "録音は相手の同意を得て行い", "実際の顧客情報は講習に持ち込まない"):
            self.assertIn(text, recording.get_text())
        for card, booking, label, material in (
            (individual, INDIVIDUAL_COURSE_URL, "個別相談を予約", "/lectures/2026-04-ai-kangaekata.html"),
            (recording, RECORDING_COURSE_URL, "AI録音講座を予約", "/blog/2026-10-24-recording-customer-timeline.html"),
        ):
            with self.subTest(label=label):
                self.assertEqual(booking, card.select_one("a.compact-course-action")["href"])
                self.assertIn(label, card.select_one("a.compact-course-action").get_text())
                self.assertEqual(material, card.select_one("a.compact-course-material")["href"])

    def test_structured_data_and_mobile_cta_use_the_restored_courses(self) -> None:
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

        individual = offers["AI個別相談 120分"]
        recording = offers["AI録音講座｜音声から自動で顧客メモやスケジュール"]
        self.assertEqual("Course", individual["@type"])
        self.assertEqual("PT2H", individual["timeRequired"])
        self.assertEqual("8800", individual["offers"]["price"])
        self.assertEqual(INDIVIDUAL_COURSE_URL, individual["offers"]["url"])
        self.assertEqual("Course", recording["@type"])
        self.assertEqual("PT2H", recording["timeRequired"])
        self.assertEqual("8800", recording["offers"]["price"])
        self.assertEqual(RECORDING_COURSE_URL, recording["offers"]["url"])
        self.assertNotIn("AIアプリサイト自作講習・相談 120分", offers)

        sticky = re.search(
            r"<nav class='sticky-cta'.*?</nav>",
            self.page,
            re.DOTALL,
        )
        self.assertIsNotNone(sticky)
        self.assertIn("AI個別相談", sticky.group(0))
        self.assertIn("120分・8,800円", sticky.group(0))
        self.assertIn(f"href='{INDIVIDUAL_COURSE_URL}'", sticky.group(0))
        self.assertNotIn("AIコーディング講習120分｜AI時代の専門技術を伝授", sticky.group(0))
        self.assertNotIn("AI自作講習", sticky.group(0))

    def test_restores_the_ai_coding_course_material_name_and_learning_goal(self) -> None:
        material = PROGRAMMING_MAP.read_text(encoding="utf-8")

        self.assertIn(
            "<title>AIコーディング講習｜Codex・Claude Code実践 | AIclimb（AI相談）</title>",
            material,
        )
        self.assertIn("AIコーディング講習 / Codex + Claude Code", material)
        self.assertIn(
            '<h1><span class="mobile-line">AIコーディングを、</span>'
            '<span class="mobile-line">仕事で使える</span>'
            '<span class="mobile-line">力へ。</span></h1>',
            material,
        )
        self.assertIn("AIコーディング講習を予約する", material)
        self.assertNotIn("AIアプリサイト自作講習・相談", material)


if __name__ == "__main__":
    unittest.main()

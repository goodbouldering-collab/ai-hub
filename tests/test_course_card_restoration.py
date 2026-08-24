import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PORTAL_PATH = ROOT / "site" / "build_portal.py"
PROGRAMMING_MAP = ROOT / "site" / "static" / "programming-map.html"
INDIVIDUAL_COURSE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP"
)
CODING_COURSE_URL = (
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
        cls.cards = re.findall(
            r"<article class='compact-course-card offer-card[^']*'.*?</article>",
            cls.page,
            re.DOTALL,
        )

    def card_named(self, title: str) -> str:
        return next((card for card in self.cards if f">{title}</h3>" in card), "")

    def assert_individual_course_format(
        self,
        card: str,
        *,
        title: str,
        price: str,
        duration: str,
    ) -> None:
        self.assertTrue(card, f"{title} card is missing")
        self.assertIn(
            f"<div class='compact-course-heading'><h3>{title}</h3>"
            "<span class='offer-audience'",
            card,
        )
        self.assertIn("<span class='offer-audience-label'>受講人数</span>", card)
        self.assertIn("<strong>個別</strong></span>", card)
        self.assertIn(
            f"<div class='compact-course-meta'><strong>{price}</strong><span>{duration}</span></div>",
            card,
        )
        self.assertIn("メリット・内容・参加方法を見る", card)
        self.assertIn("受講された方の感想を見る", card)

    def test_restores_both_individual_courses_with_the_shared_card_format(self) -> None:
        individual = self.card_named("AI個別講習")
        coding = self.card_named("AIコーディング講習")

        self.assertEqual(6, len(self.cards))
        self.assert_individual_course_format(
            individual,
            title="AI個別講習",
            price="5,500円",
            duration="60分",
        )
        self.assert_individual_course_format(
            coding,
            title="AIコーディング講習",
            price="11,000円",
            duration="120分",
        )
        self.assertNotIn("AI自作講習", self.page)

    def test_restores_the_previous_course_descriptions_details_and_links(self) -> None:
        individual = self.card_named("AI個別講習")
        coding = self.card_named("AIコーディング講習")

        self.assertIn(
            "仕事に合うAIの使い方と、確認・運用の手順を整理します。",
            individual,
        )
        for text in (
            "最初にやる仕事が決まる",
            "道具選びで迷わなくなる",
            "安全に使う範囲が分かる",
            "自分向けの進め方が残る",
            "こんな方におすすめ",
        ):
            self.assertIn(text, individual)
        self.assertIn(f"href='{INDIVIDUAL_COURSE_URL}'", individual)
        self.assertIn("個別講習を予約", individual)
        self.assertIn("href='/lectures/2026-04-ai-kangaekata.html'", individual)

        self.assertIn(
            "AIが作ったコードを読み、直し、確認して公開するところまで体系的に学びます。",
            coding,
        )
        for text in (
            "小さくても動くものを作る",
            "AIが変えた場所を読める",
            "安全な任せ方が分かる",
            "エラーを直す順番が分かる",
            "公開前の確認ができる",
            "再利用できる開発資産が残る",
        ):
            self.assertIn(text, coding)
        self.assertIn(f"href='{CODING_COURSE_URL}'", coding)
        self.assertIn("AIコーディングを予約", coding)
        self.assertIn("href='/programming-map.html'", coding)

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

        individual = offers["AI個別講習 60分"]
        coding = offers["AIコーディング講習 120分"]
        self.assertEqual("Course", individual["@type"])
        self.assertEqual("PT1H", individual["timeRequired"])
        self.assertEqual("5500", individual["offers"]["price"])
        self.assertEqual(INDIVIDUAL_COURSE_URL, individual["offers"]["url"])
        self.assertEqual("Course", coding["@type"])
        self.assertEqual("PT2H", coding["timeRequired"])
        self.assertEqual("11000", coding["offers"]["price"])
        self.assertEqual(CODING_COURSE_URL, coding["offers"]["url"])
        self.assertNotIn("AIアプリサイト自作講習・相談 120分", offers)

        sticky = re.search(
            r"<nav class='sticky-cta'.*?</nav>",
            self.page,
            re.DOTALL,
        )
        self.assertIsNotNone(sticky)
        self.assertIn("AI個別講習", sticky.group(0))
        self.assertIn("60分・5,500円", sticky.group(0))
        self.assertIn(f"href='{INDIVIDUAL_COURSE_URL}'", sticky.group(0))
        self.assertNotIn("AIコーディング講習", sticky.group(0))
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

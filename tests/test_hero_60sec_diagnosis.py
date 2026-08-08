from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
INDIVIDUAL_CONSULT_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/TO3XHZT6XP3OM4QBDYMW7TZP"
)
FREE_CONSULT_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/AW5O5XSBHLEHYUBHLZUGFKYE"
)
AI_AGENT_COURSE_URL = "https://goodbouldering.com/?pid=188553378"


class Hero60SecondDiagnosisTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index_html = INDEX.read_text(encoding="utf-8")
        hero_match = re.search(
            r"<section class='focus-hero'.*?</section>", cls.index_html, re.DOTALL
        )
        if hero_match is None:
            raise AssertionError("Focused hero section was not generated")
        cls.hero_html = hero_match.group(0)

    def test_hero_makes_diagnosis_the_primary_next_step(self):
        self.assertIn("彦根・滋賀の中小事業者向け", self.hero_html)
        self.assertIn("AIエージェントを、", self.hero_html)
        self.assertIn("強力なスタッフに。", self.hero_html)
        self.assertIn("6%", self.hero_html)
        self.assertIn("何から始めるか、1分で見える。", self.hero_html)
        self.assertIn("迷ったら60秒診断をはじめる →", self.hero_html)
        self.assertIn(
            "3問で完了。結果を見てから、予約するか決められます。",
            self.hero_html,
        )
        self.assertRegex(
            self.hero_html,
            re.escape(AI_AGENT_COURSE_URL)
            + r"' target='_blank' rel='noopener'>AIエージェント講習を見る</a>",
        )
        self.assertNotIn("AI個別相談の日程を選ぶ", self.hero_html)

    def test_hero_copy_makes_the_customer_problem_clear(self):
        self.assertIn(
            "AIが気になるけれど、何から始めるか迷う方へ。3つの質問で、いまの仕事に合う次の一歩を提案します。",
            self.hero_html,
        )

    def test_diagnosis_has_accessible_output_and_no_javascript_fallback(self):
        self.assertIn("aria-labelledby='diagnose-title'", self.index_html)
        self.assertIn("aria-live='polite'", self.index_html)
        self.assertRegex(
            self.hero_html,
            r"class='focus-btn primary hero-diagnose-button diagnose-open' href='#packages'",
        )

    def test_legacy_duplicate_diagnosis_triggers_are_absent(self):
        self.assertNotIn("60秒診断｜無料相談・個別相談・講習・伴走のどれ？", self.index_html)
        self.assertNotIn(
            "<button type='button' class='compact-diagnose diagnose-open'>迷ったら60秒診断</button>",
            self.index_html,
        )

    def test_diagnosis_results_use_purpose_specific_booking_actions(self):
        self.assertNotIn("data-focus-level", self.index_html)
        self.assertNotIn("この講座を見る →", self.index_html)
        self.assertIn("start: {", self.index_html)
        self.assertIn("bookingLabel: 'AI個別相談を予約する'", self.index_html)
        self.assertIn(
            "bookingUrl: '" + INDIVIDUAL_CONSULT_URL + "'",
            self.index_html,
        )
        self.assertIn(
            "bookingUrl: '" + AI_AGENT_COURSE_URL + "'",
            self.index_html,
        )
        self.assertIn(
            "bookingUrl: '" + FREE_CONSULT_URL + "'",
            self.index_html,
        )
        self.assertIn(
            'href="#packages" data-close-diag>講習・相談コースを見る</a>',
            self.index_html,
        )


if __name__ == "__main__":
    unittest.main()

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

    def test_hero_makes_free_consultation_the_primary_next_step(self):
        self.assertIn("AI相談 × AIアプリサイト", self.hero_html)
        self.assertIn("相談だけで終わらない。", self.hero_html)
        self.assertIn("AIで、仕事の仕組みまでつくる。", self.hero_html)
        self.assertIn("まずは無料相談", self.hero_html)
        self.assertIn("AIアプリサイトを見る", self.hero_html)
        self.assertIn(FREE_CONSULT_URL, self.hero_html)
        self.assertLess(
            self.hero_html.index("まずは無料相談"),
            self.hero_html.index("AIアプリサイトを見る"),
        )
        self.assertNotIn("AI個別相談の日程を選ぶ", self.hero_html)

    def test_hero_copy_makes_the_customer_problem_clear(self):
        self.assertIn("見積もり、予約、顧客管理、シフト、ブログ、問い合わせ対応。", self.hero_html)
        self.assertIn("その仕事、<br>サイトにやらせませんか？", self.hero_html)
        self.assertIn("見積もり <b>→ 自動作成</b>", self.hero_html)
        self.assertIn("予約 <b>→ 自動受付</b>", self.hero_html)
        self.assertIn("問い合わせ <b>→ AI回答</b>", self.hero_html)
        self.assertIn("ブログ <b>→ AI下書き</b>", self.hero_html)
        self.assertIn("シフト <b>→ 自動作成</b>", self.hero_html)
        self.assertIn("報告書 <b>→ PDF生成</b>", self.hero_html)

    def test_diagnosis_remains_accessible_without_taking_over_the_hero(self):
        self.assertIn("aria-labelledby='diagnose-title'", self.index_html)
        self.assertIn("aria-live='polite'", self.index_html)
        self.assertNotIn("diagnose-open", self.hero_html)
        self.assertRegex(self.hero_html, re.escape("class='focus-btn primary' href='" + FREE_CONSULT_URL))

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

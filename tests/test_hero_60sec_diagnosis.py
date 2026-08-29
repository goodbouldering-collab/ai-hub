from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
CODING_COURSE_URL = (
    "https://book.squareup.com/appointments/zymaszkc9pdwq2/"
    "location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH"
)
INDIVIDUAL_COURSE_URL = (
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
        self.assertIn("AI導入120分で", self.hero_html)
        self.assertIn("やりたいことが動き出す", self.hero_html)
        self.assertNotIn("AIエージェントで", self.hero_html)
        self.assertNotIn("できることを100倍に", self.hero_html)
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
        self.assertIn("<span>AI利用率</span><strong>6%</strong>", self.hero_html)
        self.assertIn("<small><strong>始めるなら今。</strong></small>", self.hero_html)
        self.assertNotIn("まだまだこれから！", self.hero_html)
        self.assertIn(
            "<span class='hero-advantage-equation'><strong>AI</strong><span>×</span><strong>経験 = 影響力</strong></span>",
            self.hero_html,
        )
        self.assertIn("経験者から学ぶことが大切", self.hero_html)
        self.assertIn("<li>初心者OK</li>", self.hero_html)
        self.assertIn("講習・導入支援・制作代行", self.hero_html)
        self.assertNotIn("もう高いパッケージは負け組", self.hero_html)
        self.assertNotIn("「こんなことできたら」がすぐ叶う", self.hero_html)
        self.assertNotIn("目的さえあればだれでも使える", self.hero_html)
        self.assertNotIn("思い描けば現実になる！", self.hero_html)
        self.assertIn("<li><b>01</b>試しに作る</li>", self.hero_html)
        self.assertIn("<li><b>02</b>素早く修正</li>", self.hero_html)
        self.assertIn("<li><b>03</b>仕組み化する</li>", self.hero_html)
        self.assertIn(
            "告知・事務・集客に追われる方へ。AI相談・業務改善・伴走支援で、AIが分からない不安を今日から使える一歩に変えます。",
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
        self.assertIn("bookingLabel: 'AI個別講習を予約する'", self.index_html)
        self.assertIn(
            "bookingUrl: '" + INDIVIDUAL_COURSE_URL + "'",
            self.index_html,
        )
        self.assertIn("bookingLabel: 'AIコーディング講習を予約する'", self.index_html)
        self.assertIn(
            "bookingUrl: '" + CODING_COURSE_URL + "'",
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

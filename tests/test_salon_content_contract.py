import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"


class SalonContentContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = INDEX.read_text(encoding="utf-8")
        match = re.search(
            r"<div class='salon-panel'>(.*?)</section>",
            cls.html,
            re.DOTALL,
        )
        if match is None:
            raise AssertionError("AIオンラインサロンの詳細パネルが見つかりません")
        cls.panel = match.group(1)

    def test_every_reader_facing_detail_remains_in_the_panel(self) -> None:
        expected_in_order = (
            "月額2,200円（税込）・毎週火曜21:00",
            "AIオンラインサロン",
            "AIの最新を、仕事の次の一手に。",
            "全部を追わず、新機能と一流の活用事例から、今試すことを短く整理します。",
            "UPDATE",
            "新機能を毎週知る",
            "BEST PRACTICE",
            "一流の活用事例を聞く",
            "NEXT ACTION",
            "次に試すことを決める",
            "WHEN",
            "火曜21:00",
            "PLACE",
            "LINEライブ",
            "FEE",
            "月2,200円",
            "STYLE",
            "聞くだけOK",
            "マイクOFFで参加できます",
            "LINE LIVE TALK",
            "聞くだけOK。話すときだけ挙手",
            "Squareで月額決済",
            "月額2,200円・毎月自動更新",
            "火曜21時に入室",
            "ライブトークを開く",
            "聞くだけ／挙手",
            "話すときだけマイクON",
            "マイクOFF・途中参加・途中退出OK",
            "決済確認後にLINE参加案内を表示",
            "60 MINUTES",
            "火曜21時の流れ",
            "21:00",
            "今週の変化",
            "21:05",
            "使えるか判断",
            "21:15",
            "仕事で実践",
            "21:40",
            "次の一歩",
            "参加できない週も安心。",
            "火曜AIノート",
            "Squareで決済して参加",
            "月額2,200円（税込）・毎月自動更新。決済確認後にLINE参加案内を表示します",
        )
        cursor = -1
        for text in expected_in_order:
            with self.subTest(text=text):
                next_cursor = self.panel.find(text, cursor + 1)
                self.assertGreater(next_cursor, cursor)
                cursor = next_cursor

    def test_structured_detail_counts_and_checkout_contract_remain_intact(self) -> None:
        self.assertEqual(self.panel.count("class='salon-value'"), 3)
        self.assertEqual(self.panel.count("class='salon-fact'"), 4)
        self.assertEqual(self.panel.count("class='salon-run-cell'"), 4)
        self.assertEqual(self.panel.count("<li><b>"), 3)
        self.assertIn("method='post'", self.panel)
        self.assertIn("action='/api/square/ai-salon-checkout'", self.panel)
        self.assertIn(
            "src='/img/ai-salon-live-talk-guide-20260722.svg'",
            self.panel,
        )

    def test_mobile_value_labels_are_not_visually_truncated(self) -> None:
        rule = re.search(
            r"@media \(max-width:720px\).*?"
            r"\.salon-panel \.salon-value small\s*\{([^}]*)\}",
            self.html,
            re.DOTALL,
        )
        self.assertIsNotNone(rule)
        assert rule is not None
        declarations = rule.group(1)
        self.assertIn("overflow:visible", declarations)
        self.assertIn("text-overflow:clip", declarations)
        self.assertIn("white-space:normal", declarations)
        self.assertRegex(
            self.html,
            re.compile(
                r"@media \(max-width:720px\).*?"
                r"\.salon-participation \.salon-live-figure figcaption\s*"
                r"\{[^}]*display:block;",
                re.DOTALL,
            ),
        )


if __name__ == "__main__":
    unittest.main()

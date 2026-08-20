import importlib.util
import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "dist" / "index.html"
MODULE_PATH = ROOT / "site" / "build_portal.py"
SPEC = importlib.util.spec_from_file_location("salon_content_portal", MODULE_PATH)
portal = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(portal)


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
        expected_details = (
            "SQUARE MONTHLY",
            "現在は仮運用中",
            "毎週火曜にLINEライブトークでAIの今と次の一手を整理するオンラインサロン",
            "仕事で次に試すことを、一緒に決める60分",
            "月額2,200円（税込）",
            "毎週火曜21:00",
            "AIオンラインサロン｜近日開始",
            "AIの最新も疑問もその場で解決できる。",
            "正式開始に向けて現在は仮運用中です。登録中の方にはテスト運用へご協力いただいています。Squareで月額決済後、LINEライブトークの参加案内を表示します。",
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
            "メリット・内容・参加方法を見る",
            "このサロンに参加するメリット",
            "AI情報を全部追わなくていい",
            "増え続ける新機能や発表から、地域事業や日々の仕事に関係する変化だけを短く整理します。",
            "今やる・待つを判断できる",
            "新しいから飛びつくのではなく、今すぐ試すもの、様子を見るもの、使わないものを実例で分けます。",
            "実際の仕事で確かめられる",
            "参加者の告知、資料、事務、Web改善などを題材に、AIへの依頼、確認、修正まで画面を見ながら進めます。",
            "ほかの人の事例も学びになる",
            "自分とは違う業種の困りごとや改善例から、自分の仕事へ応用できるヒントを持ち帰れます。",
            "その場で質問できる",
            "一人で調べ続けず、分からない点や導入の迷いを質問し、次に試す小さな一歩を決められます。",
            "忙しい週は聞くだけでOK",
            "LINEライブトークはマイクOFF、途中参加、途中退出に対応。発言したいときだけ挙手できます。",
            "終了後も要点を見返せる",
            "講師が内容を確認した「火曜AIノート」で、重要点と次の行動を振り返れます。",
            "参加方法",
            "Squareで月額2,200円を決済後、表示される招待URLからLINEへ進みます。毎週火曜21時の案内から参加できます。",
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
            "オンラインサロン受講資料を見る",
            "Squareで決済して仮運用に参加",
            "月額2,200円（税込）・毎月自動更新。決済確認後にLINE参加案内を表示します",
        )
        for text in expected_details:
            with self.subTest(text=text):
                self.assertIn(text, self.panel)
        self.assertNotIn(
            "全部を追わず、新機能と一流の活用事例から、今試すことを短く整理します。",
            self.panel,
        )

    def test_structured_data_matches_the_trial_operation_status(self) -> None:
        graph = json.loads(portal._build_jsonld_website())["@graph"]
        salon = next(
            node
            for node in graph
            if node.get("name") == "AIオンラインサロン｜近日開始"
        )

        self.assertEqual("CommunityService", salon["serviceType"])
        self.assertIn("正式開始に向けて現在は仮運用中", salon["description"])
        self.assertIn("テスト運用へご協力", salon["description"])
        self.assertEqual(portal.SITE_URL + portal.AI_SALON_CHECKOUT_URL, salon["url"])
        self.assertEqual("2200", salon["offers"]["price"])
        self.assertEqual("P1M", salon["offers"]["priceSpecification"]["billingDuration"])

    def test_page_description_does_not_claim_the_salon_has_formally_started(self) -> None:
        self.assertIn("AIオンラインサロンは近日開始・現在仮運用中", self.html)
        self.assertNotIn("有料オンラインサロンを開催しています", self.html)

    def test_structured_detail_counts_and_checkout_contract_remain_intact(self) -> None:
        self.assertEqual(self.panel.count("class='salon-value'"), 3)
        self.assertEqual(self.panel.count("class='salon-fact'"), 4)
        self.assertEqual(self.panel.count("class='salon-benefit'"), 8)
        self.assertEqual(self.panel.count("<li><b>"), 3)
        self.assertIn("method='post'", self.panel)
        self.assertIn("action='/api/square/ai-salon-checkout'", self.panel)
        self.assertIn("class='compact-course-checkout salon-card-checkout'", self.panel)
        self.assertIn(
            "class='compact-course-material salon-material-link' href='/lectures/2026-07-ai-online-salon-practice.html'",
            self.panel,
        )
        self.assertIn(
            "src='/img/blog-ai-agent-course-section-4-20260714.webp'",
            self.panel,
        )
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

import importlib.util
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "site" / "build_portal.py"
SPEC = importlib.util.spec_from_file_location("course_testimonials_portal", MODULE_PATH)
portal = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(portal)


EXPECTED_GROUPS = (
    (
        "ai-agent",
        "AIエージェント講習",
        "voice-ai-agent",
        "ゼロからでも、AIエージェントが仕事の相棒になった",
        (
            ("インストールから、実際に作れるところまで", "インストールから一つずつ説明してもらい、IDEもAIエージェントもゼロから触れました。最後は自分で実際に作れるところまで進めたので、とても分かりやすかったです。"),
            ("基礎がストーリーでつながり、記憶に残った", "本当に使えるレベルになるには基礎が大事だと、ストーリー仕立てでみっちり教えてもらえました。覚えやすい言い回しも面白く、内容がすっと頭に入りました。"),
            ("使うほど、手になじむ感覚があった", "エンジニア向けに見えるツールなのに、楽しみながら使えました。使うほど手になじみ、自分の仕事でも続けられそうだと感じました。"),
        ),
    ),
    (
        "ai-consultation",
        "AI個別相談",
        "voice-ai-consultation",
        "その場で悩みがほどけ、明日から使える形になった",
        (
            ("会社の業務を、そのまま相談できた", "会社で使っているツールと実際の業務をそのまま相談でき、疑問点を一つずつ整理しながら、その場で解決策を見つけられたのがよかったです。"),
            ("「役立ちそう」ではなく、その場で成果が見えた", "これまでAIが実際の業務に役立つと感じたことはありませんでしたが、今回は本当に使える成果を見せてもらえました。作業のスピード感もあり、すぐに導入したいと思いました。"),
            ("社内に導入できる形まで落とし込めた", "解決策が事業の中で形になっていくのを実感できました。会社へ導入しやすいところまで整理でき、今度は自分がほかの人へ伝えられることも増えたと思います。"),
        ),
    ),
    (
        "ai-support",
        "AI伴走支援",
        "voice-ai-support",
        "社内の理解が進み、AI導入が動き出した",
        (
            ("上司への説明まで支えてもらい、導入が早まった", "会社の上司との話し合いにも入っていただき、新しい提案を分かりやすく説明してもらえたので、社内でのAI導入がとても早く進みました。"),
            ("自分たちでは見えなかった問題を洗い出せた", "私たちだけでは気づけなかった問題点を見つけてもらい、何から解決するかまで整理できました。社内でAIを活用できる可能性が見えたことがうれしかったです。"),
            ("明日やることが増えた分、仕事が前へ進み始めた", "YouTubeで見るだけとは違い、目の前で問題が解決していく様子は見ていて気持ちがよかったです。明日からやることは増えましたが、その分、業務がどんどん進む感覚がありました。"),
        ),
    ),
    (
        "ai-coding",
        "AIコーディング講習",
        "voice-ai-coding",
        "コードを書く人から、AIとチームを動かす人へ",
        (
            ("手打ちより、仕様と順序が効率を決めると分かった", "これまではコードを手で打つことに集中していましたが、プロジェクトの目的や仕様書に沿って進めることが、結果的に大きな効率化につながると分かりました。"),
            ("設計・セキュリティ・公開工程まで見えた", "AIはコードを書くだけでなく、ワークフローやデザイン、必要なデータ、セキュリティ、公開までの順序も提案できると知りました。プロの進め方を一つずつ理解できました。"),
            ("チーム開発と採用にも使える、新しい進め方だった", "部下と共同作業するときのAI活用フローがとても分かりやすかったです。GitHubやワークツリー、低コストのクラウドサービスも学べて、自動化や費用削減だけでなく、今後の採用にも役立つと感じました。"),
        ),
    ),
)


class CourseTestimonialsTest(unittest.TestCase):
    def test_renders_four_course_groups_and_twelve_real_reviews(self) -> None:
        render = getattr(portal, "_render_course_testimonials", None)
        self.assertTrue(callable(render), "感想セクションのレンダー関数が必要です")
        rendered = render()

        self.assertIn("<h2 id='course-voices-title'>受講された方の感想</h2>", rendered)
        self.assertIn("個人が特定されないよう一部表現を整えて掲載しています", rendered)
        for _, course_name, anchor_id, heading, testimonials in EXPECTED_GROUPS:
            self.assertIn(f"id='{anchor_id}'", rendered)
            self.assertIn(course_name, rendered)
            self.assertIn(heading, rendered)
            for title, body in testimonials:
                self.assertIn(title, rendered)
                self.assertIn(body, rendered)
        self.assertEqual(12, rendered.count("<figure class='course-voice-card'>"))
        self.assertEqual(12, rendered.count("受講者（匿名）"))

    def test_every_course_card_links_to_its_matching_voice_group(self) -> None:
        cards = portal._render_compact_course_cards()

        for _, _, anchor_id, _, _ in EXPECTED_GROUPS:
            self.assertIn(f"href='#{anchor_id}'", cards)
        self.assertEqual(4, cards.count("このコースを受講した方の感想を見る"))

    def test_jsonld_links_visible_reviews_to_four_stable_nodes(self) -> None:
        graph = json.loads(portal._build_jsonld_website())["@graph"]
        nodes = {node.get("@id"): node for node in graph if node.get("@id")}
        expected_nodes = (
            (portal.SITE_URL + "/#course-ai-agent", "Course", EXPECTED_GROUPS[0]),
            (portal.SITE_URL + "/#service-ai-consultation", "Service", EXPECTED_GROUPS[1]),
            (portal.SITE_URL + "/#service-ai-support", "Service", EXPECTED_GROUPS[2]),
            (portal.SITE_URL + "/#course-ai-coding", "Course", EXPECTED_GROUPS[3]),
        )

        for node_id, node_type, expected_group in expected_nodes:
            self.assertIn(node_id, nodes)
            node = nodes[node_id]
            self.assertEqual(node_type, node["@type"])
            self.assertEqual(expected_group[1], node["name"].removesuffix(" 120分").removesuffix(" しっかり60分").removesuffix(" いっしょに導入"))
            expected_reviews = expected_group[4]
            self.assertEqual(3, len(node["review"]))
            self.assertEqual(
                [title for title, _ in expected_reviews],
                [review["name"] for review in node["review"]],
            )
            self.assertEqual(
                [body for _, body in expected_reviews],
                [review["reviewBody"] for review in node["review"]],
            )
            for review in node["review"]:
                self.assertEqual("Review", review["@type"])
                self.assertEqual(
                    {"@type": "Person", "name": "受講者（匿名）"},
                    review["author"],
                )

    def test_course_jsonld_describes_duration_mode_language_and_learning(self) -> None:
        graph = json.loads(portal._build_jsonld_website())["@graph"]
        courses = [node for node in graph if node.get("@type") == "Course"]

        self.assertEqual(2, len(courses))
        for course in courses:
            self.assertEqual("PT2H", course["timeRequired"])
            self.assertEqual(["onsite", "online"], course["courseMode"])
            self.assertEqual("ja", course["inLanguage"])
            self.assertTrue(course["teaches"])
            self.assertEqual("Offer", course["offers"]["@type"])

    def test_jsonld_does_not_invent_ratings(self) -> None:
        payload = portal._build_jsonld_website()

        self.assertNotIn("reviewRating", payload)
        self.assertNotIn("aggregateRating", payload)

    def test_legacy_voice_helper_reuses_real_testimonials_not_samples(self) -> None:
        self.assertFalse(portal.VOICES_ARE_SAMPLE)
        rendered = portal._render_voices()

        self.assertEqual(12, rendered.count("<figure class='voice-card'>"))
        for _, _, _, _, testimonials in EXPECTED_GROUPS:
            for title, body in testimonials:
                self.assertIn(title, rendered)
                self.assertIn(body, rendered)

    def test_full_page_places_voices_after_courses_and_before_venue(self) -> None:
        page = portal.render_portal([], [])

        self.assertIn("id='course-voices'", page)
        self.assertLess(
            page.index("class='course-menu-unified'"),
            page.index("id='course-voices'"),
        )
        self.assertLess(
            page.index("id='course-voices'"),
            page.index("class='course-venue-common'"),
        )

    def test_course_voice_layout_is_two_columns_and_mobile_one_column(self) -> None:
        css = portal.FOCUSED_PORTAL_CSS

        self.assertRegex(
            css,
            r"\.course-voices-grid\s*\{[^}]*grid-template-columns:\s*repeat\(2,\s*minmax\(0,\s*1fr\)\)",
        )
        mobile_block = re.search(
            r"@media\s*\(max-width:\s*760px\)\s*\{(?P<body>[\s\S]*?)\n\}",
            css,
        )
        self.assertIsNotNone(mobile_block)
        self.assertRegex(
            mobile_block.group("body"),
            r"\.course-voices-grid\s*\{[^}]*grid-template-columns:\s*1fr",
        )


if __name__ == "__main__":
    unittest.main()

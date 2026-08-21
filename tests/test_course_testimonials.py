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
        "ai-app-selfbuild",
        "AIアプリサイト自作講習・相談",
        "voice-ai-app-selfbuild",
        "相談から公開までつながり、自分で直せる形になった",
        (
            ("会社の業務を、そのまま相談できた", "会社で使っているツールと実際の業務をそのまま相談でき、疑問点を一つずつ整理しながら、その場で解決策を見つけられたのがよかったです。"),
            ("「役立ちそう」ではなく、その場で成果が見えた", "これまでAIが実際の業務に役立つと感じたことはありませんでしたが、今回は本当に使える成果を見せてもらえました。作業のスピード感もあり、すぐに導入したいと思いました。"),
            ("社内に導入できる形まで落とし込めた", "解決策が事業の中で形になっていくのを実感できました。会社へ導入しやすいところまで整理でき、今度は自分がほかの人へ伝えられることも増えたと思います。"),
            ("手打ちより、仕様と順序が効率を決めると分かった", "これまではコードを手で打つことに集中していましたが、プロジェクトの目的や仕様書に沿って進めることが、結果的に大きな効率化につながると分かりました。"),
            ("設計・セキュリティ・公開工程まで見えた", "AIはコードを書くだけでなく、ワークフローやデザイン、必要なデータ、セキュリティ、公開までの順序も提案できると知りました。プロの進め方を一つずつ理解できました。"),
            ("チーム開発と採用にも使える、新しい進め方だった", "部下と共同作業するときのAI活用フローがとても分かりやすかったです。GitHubやワークツリー、低コストのクラウドサービスも学べて、自動化や費用削減だけでなく、今後の採用にも役立つと感じました。"),
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
)

EXPECTED_SALON_GROUP = (
    "ai-salon",
    "AIオンラインサロン｜近日開始",
    "voice-ai-salon",
    "情報に追われず、仕事で試す一歩が毎週決まった",
    (
        (
            "新機能を全部追わなくても、必要なことが分かった",
            "AIの情報が多すぎて追い切れませんでしたが、自分の仕事に関係する変化だけを短く整理してもらえたので、焦らず判断できるようになりました。",
        ),
        (
            "ほかの参加者の質問が、自分の仕事のヒントになった",
            "業種の違う参加者の質問や改善例から、自分では気づかなかった使い方が見えました。その場で聞けるので、一人で調べ続ける時間も減りました。",
        ),
        (
            "聞くだけの週でも、次に試すことが決まった",
            "忙しい日はマイクを切って聞くだけで参加できました。最後に次の一歩が整理されるので、翌日から小さく試せて続けやすかったです。",
        ),
    ),
)


class CourseTestimonialsTest(unittest.TestCase):
    def test_renders_three_course_groups_and_twelve_real_reviews(self) -> None:
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

    def test_every_course_card_contains_its_matching_voice_dropdown(self) -> None:
        cards = portal._render_compact_course_cards()
        rendered_cards = re.findall(
            r"<article class='compact-course-card[^']*'.*?</article>",
            cards,
            re.DOTALL,
        )

        self.assertEqual(3, len(rendered_cards))
        for card, expected in zip(rendered_cards, EXPECTED_GROUPS, strict=True):
            _, _, anchor_id, heading, testimonials = expected
            self.assertIn(f"id='{anchor_id}'", card)
            self.assertEqual(1, card.count("受講された方の感想を見る"))
            self.assertLess(
                card.index("メリット・内容・参加方法を見る"),
                card.index("受講された方の感想を見る"),
            )
            self.assertIn(heading, card)
            for title, body in testimonials:
                self.assertIn(title, card)
                self.assertIn(body, card)
        self.assertEqual(12, cards.count("<figure class='compact-course-voice-card'>"))
        self.assertEqual(12, cards.count("受講者（匿名）"))

    def test_salon_uses_standard_course_details_trigger_before_testimonials(self) -> None:
        salon = portal._render_salon_menu()
        _, course_name, anchor_id, heading, testimonials = EXPECTED_SALON_GROUP

        self.assertIn(course_name, salon)
        self.assertIn(f"id='{anchor_id}'", salon)
        self.assertEqual(1, salon.count("受講された方の感想を見る"))
        self.assertIn(
            "<details class='compact-course-details salon-all-details--complete' "
            "id='salon-details'><summary>メリット・内容・参加方法を見る</summary>",
            salon,
        )
        self.assertNotIn("8つのメリット・内容・参加方法を見る", salon)
        self.assertLess(
            salon.index("メリット・内容・参加方法を見る"),
            salon.index("受講された方の感想を見る"),
        )
        self.assertLess(
            salon.index("受講された方の感想を見る"),
            salon.index("Squareで決済して仮運用に参加"),
        )
        self.assertIn(heading, salon)
        self.assertIn(
            "現在の仮運用で寄せられた内容をもとに、個人が特定されないよう表現を整えて掲載しています。",
            salon,
        )
        for title, body in testimonials:
            self.assertIn(title, salon)
            self.assertIn(body, salon)
        self.assertEqual(3, salon.count("<figure class='compact-course-voice-card'>"))
        self.assertEqual(3, salon.count("仮運用参加者（匿名）"))

    def test_jsonld_links_visible_reviews_to_three_stable_nodes(self) -> None:
        graph = json.loads(portal._build_jsonld_website())["@graph"]
        nodes = {node.get("@id"): node for node in graph if node.get("@id")}
        expected_nodes = (
            (portal.SITE_URL + "/#course-ai-agent", "Course", EXPECTED_GROUPS[0]),
            (portal.SITE_URL + "/#course-ai-app-selfbuild", "Course", EXPECTED_GROUPS[1]),
            (portal.SITE_URL + "/#service-ai-support", "Service", EXPECTED_GROUPS[2]),
        )

        for node_id, node_type, expected_group in expected_nodes:
            self.assertIn(node_id, nodes)
            node = nodes[node_id]
            self.assertEqual(node_type, node["@type"])
            self.assertEqual(expected_group[1], node["name"].removesuffix(" 120分").removesuffix(" しっかり60分").removesuffix(" いっしょに導入"))
            expected_reviews = expected_group[4]
            self.assertEqual(len(expected_reviews), len(node["review"]))
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

    def test_jsonld_links_salon_reviews_to_stable_service_node(self) -> None:
        graph = json.loads(portal._build_jsonld_website())["@graph"]
        nodes = {node.get("@id"): node for node in graph if node.get("@id")}
        node_id = portal.SITE_URL + "/#service-ai-salon"
        _, course_name, _, _, testimonials = EXPECTED_SALON_GROUP

        self.assertIn(node_id, nodes)
        salon = nodes[node_id]
        self.assertEqual("Service", salon["@type"])
        self.assertEqual(course_name, salon["name"])
        self.assertEqual(
            [title for title, _ in testimonials],
            [review["name"] for review in salon["review"]],
        )
        self.assertEqual(
            [body for _, body in testimonials],
            [review["reviewBody"] for review in salon["review"]],
        )
        for review in salon["review"]:
            self.assertEqual(
                {"@type": "Person", "name": "仮運用参加者（匿名）"},
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

    def test_full_page_has_no_standalone_voice_section(self) -> None:
        page = portal.render_portal([], [])

        self.assertNotIn("<section class='course-voices'", page)
        self.assertIn("class='course-menu-unified' id='course-voices'", page)
        self.assertEqual(4, page.count("受講された方の感想を見る"))
        self.assertLess(
            page.index("id='course-voices'"),
            page.index("class='course-venue-common'"),
        )

    def test_course_voice_dropdown_uses_a_compact_single_column_list(self) -> None:
        css = portal.FOCUSED_PORTAL_CSS

        self.assertRegex(
            css,
            r"\.compact-course-testimonials-list\s*\{[^}]*display:\s*grid[^}]*gap:",
        )
        self.assertNotRegex(
            css,
            r"\.compact-course-testimonials-list\s*\{[^}]*grid-template-columns:\s*repeat\(",
        )

    def test_open_voice_dropdown_does_not_stretch_neighboring_course_cards(self) -> None:
        css = portal.FOCUSED_PORTAL_CSS

        self.assertNotRegex(
            css,
            r"\.compact-course-grid\s*\{[^}]*align-items:\s*stretch",
        )
        self.assertGreaterEqual(
            len(re.findall(r"\.compact-course-grid\s*\{[^}]*align-items:\s*start", css)),
            2,
        )

    def test_course_voice_copy_uses_high_contrast_existing_tokens(self) -> None:
        css = portal.FOCUSED_PORTAL_CSS

        expected_colors = {
            ".compact-course-testimonials-body h3": "var(--focus-ink)",
            ".compact-course-testimonials-note": "var(--focus-muted)",
            ".compact-course-voice-card h4": "var(--focus-blue-dark)",
            ".compact-course-voice-card p": "var(--focus-ink)",
            ".compact-course-voice-card figcaption": "var(--focus-ink)",
        }
        for selector, color in expected_colors.items():
            with self.subTest(selector=selector):
                self.assertRegex(
                    css,
                    rf"{re.escape(selector)}\s*\{{[^}}]*color:\s*{re.escape(color)}",
                )

    def test_focus_accent_and_muted_tokens_are_readable_on_light_surfaces(self) -> None:
        css = portal.FOCUSED_PORTAL_CSS
        tokens = dict(
            re.findall(
                r"--(focus-(?:blue|muted|surface|lavender|rose-soft)):\s*(#[0-9a-fA-F]{6})",
                css,
            )
        )

        def luminance(color: str) -> float:
            channels = [int(color[index : index + 2], 16) / 255 for index in (1, 3, 5)]
            linear = [
                channel / 12.92
                if channel <= 0.04045
                else ((channel + 0.055) / 1.055) ** 2.4
                for channel in channels
            ]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        def contrast(foreground: str, background: str) -> float:
            lighter, darker = sorted(
                (luminance(foreground), luminance(background)), reverse=True
            )
            return (lighter + 0.05) / (darker + 0.05)

        for foreground_name in ("focus-blue", "focus-muted"):
            for background in (
                "#ffffff",
                tokens["focus-surface"],
                tokens["focus-lavender"],
                tokens["focus-rose-soft"],
            ):
                with self.subTest(foreground=foreground_name, background=background):
                    self.assertGreaterEqual(
                        contrast(tokens[foreground_name], background),
                        4.5,
                    )

    def test_accessible_roles_support_visible_hero_and_course_labels(self) -> None:
        self.assertIn(
            "class='hero-advantage-number' role='img' aria-label='AI利用率 6パーセント'",
            portal._render_hero_focused(),
        )
        self.assertIn(
            "class='course-menu-unified' id='course-voices' role='region' "
            "aria-label='講習・相談の全4メニュー'",
            portal._render_focused_main(),
        )

    def test_mobile_menu_keeps_the_online_salon_entry(self) -> None:
        page = portal._render_header_focused()
        mobile_menu = re.search(
            r"<nav class='mobile-public-links'[^>]*>(?P<links>.*?)</nav>",
            page,
            re.DOTALL,
        )

        self.assertIsNotNone(mobile_menu)
        assert mobile_menu is not None
        links = mobile_menu.group("links")
        self.assertIn(
            "<a href='/#seven-day-courses'><span>AIオンラインサロン</span>",
            links,
        )

    def test_mobile_menu_moves_conversion_ctas_to_scroll_dock(self) -> None:
        header = portal._render_header_focused()
        mobile_menu = re.search(
            r"<nav class='mobile-public-links'[^>]*>(?P<links>.*?)</nav>",
            header,
            re.DOTALL,
        )

        self.assertIsNotNone(mobile_menu)
        assert mobile_menu is not None
        links = mobile_menu.group("links")
        self.assertNotIn("mobile-nav-head", header)
        self.assertNotIn("講習・相談コース", links)
        self.assertNotIn("個別相談", links)

        sticky_cta = portal._render_sticky_cta()
        self.assertIn(
            "<nav class='sticky-cta' id='sticky-cta' aria-label='AI自作講習とAIエージェント講習の固定CTA'",
            sticky_cta,
        )
        self.assertIn(
            "class='sticky-cta-btn sticky-cta-btn--consult' "
            "href='https://book.squareup.com/appointments/zymaszkc9pdwq2/location/LWJNMP7EAN4GS/services/S7GERYVDIPRV76DKXCC3WJWH'",
            sticky_cta,
        )
        self.assertIn(
            "class='sticky-cta-btn sticky-cta-btn--agent' "
            "href='https://goodbouldering.com/?pid=188553378'",
            sticky_cta,
        )

    def test_contact_and_footer_copy_keep_readable_contrast(self) -> None:
        css = portal.FOCUSED_PORTAL_CSS

        self.assertRegex(
            css,
            r"\.focus-contact p\s*\{[^}]*color:\s*rgba\(255,255,255,\.9\)",
        )
        self.assertRegex(
            css,
            r"\.footer-nap a\s*\{[^}]*color:\s*var\(--focus-blue-dark\)",
        )


if __name__ == "__main__":
    unittest.main()

import importlib.util
import json
from pathlib import Path
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


if __name__ == "__main__":
    unittest.main()

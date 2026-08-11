# Course Testimonials SEO/LLMO Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AI相談トップの4コースへ実在する匿名感想を3件ずつ掲載し、可視HTMLとJSON-LDを一致させて本番公開する。

**Architecture:** `site/build_portal.py`内の`COURSE_TESTIMONIALS`を唯一のデータ源にし、コースカードのアンカー、感想セクション、Course/Serviceの`review` JSON-LDを生成する。表示と構造化データを別々に手書きせず、同じ12件から出力することでSEO・LLMO上の意味と画面表示の乖離を防ぐ。

**Tech Stack:** Python 3.12、標準`unittest`、静的HTML/CSS、Schema.org JSON-LD、Playwright、Git/GitHub、Vercel

## Global Constraints

- 対象はAIエージェント講習、AI個別相談、AI伴走支援、AIコーディング講習の4つだけ。
- 各コース3件、合計12件の実在感想を匿名化・読みやすく編集して掲載する。
- 原文にない星評価、氏名、会社名、業種、年代、効果数値は追加しない。
- `reviewRating`と`aggregateRating`は出力しない。
- 画面上の`reviewBody`とJSON-LDの`reviewBody`を完全一致させる。
- 既存の料金、予約URL、決済、資料、AIオンラインサロン、会場案内を変更しない。
- PC 1440pxとiPhone 390pxで読みやすさ、CTA、アンカー、コントラスト、横方向のはみ出しを確認する。
- 公開完了はmainへの反映、Vercel READY、本番URLの表示・JSON-LD・ブラウザ確認までとする。

---

## File Structure

- Create: `tests/test_course_testimonials.py` — 4コース、12件、アンカー、可視HTML、JSON-LDの契約テスト。
- Modify: `site/build_portal.py` — 感想データ、レンダー、カードリンク、CSS、Course/Service/Review JSON-LD。
- Regenerate: `site/dist/index.html` — 本番配信されるトップページ生成物。
- Modify: `docs/superpowers/plans/2026-08-12-course-testimonials-seo-llmo.md` — 実行チェックを更新する。

---

### Task 1: 感想データと可視HTMLの契約

**Files:**
- Create: `tests/test_course_testimonials.py`
- Modify: `site/build_portal.py:11465-11615`

**Interfaces:**
- Produces: `COURSE_TESTIMONIALS: tuple[dict, ...]`
- Produces: `_render_course_testimonials() -> str`
- Consumes: `html.escape`、既存の`_render_compact_course_cards() -> str`
- Later tasks consume: `COURSE_TESTIMONIALS`の`key`、`course_name`、`anchor_id`、`heading`、`testimonials`

- [x] **Step 1: 失敗するHTML契約テストを書く**

`tests/test_course_testimonials.py`を次の構造で作る。

```python
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


EXPECTED_HEADINGS = {
    "ai-agent": "ゼロからでも、AIエージェントが仕事の相棒になった",
    "ai-consultation": "その場で悩みがほどけ、明日から使える形になった",
    "ai-support": "社内の理解が進み、AI導入が動き出した",
    "ai-coding": "コードを書く人から、AIとチームを動かす人へ",
}


class CourseTestimonialsTest(unittest.TestCase):
    def test_four_courses_have_three_real_testimonials_each(self) -> None:
        groups = portal.COURSE_TESTIMONIALS
        self.assertEqual(4, len(groups))
        self.assertEqual(12, sum(len(group["testimonials"]) for group in groups))
        self.assertEqual(EXPECTED_HEADINGS, {group["key"]: group["heading"] for group in groups})

    def test_visible_section_contains_course_names_titles_bodies_and_disclosure(self) -> None:
        rendered = portal._render_course_testimonials()
        self.assertIn("<h2 id='course-voices-title'>受講された方の感想</h2>", rendered)
        self.assertIn("個人が特定されないよう一部表現を整えて掲載しています", rendered)
        for group in portal.COURSE_TESTIMONIALS:
            self.assertIn(f"id='{group['anchor_id']}'", rendered)
            self.assertIn(group["course_name"], rendered)
            self.assertIn(group["heading"], rendered)
            for testimonial in group["testimonials"]:
                self.assertIn(testimonial["title"], rendered)
                self.assertIn(testimonial["body"], rendered)
        self.assertEqual(12, rendered.count("<figure class='course-voice-card'>"))

    def test_every_course_card_links_to_its_voice_group(self) -> None:
        cards = portal._render_compact_course_cards()
        for group in portal.COURSE_TESTIMONIALS:
            self.assertIn(f"href='#{group['anchor_id']}'", cards)
        self.assertEqual(4, cards.count("このコースを受講した方の感想を見る"))
```

- [x] **Step 2: テストが意図どおり失敗することを確認する**

Run:

```powershell
& '.\.venv\Scripts\python.exe' -m unittest tests.test_course_testimonials -v
```

Expected: `COURSE_TESTIMONIALS`または`_render_course_testimonials`が未定義でFAIL。

- [x] **Step 3: 4コース×3件のデータを定義する**

`site/build_portal.py`のコースレンダーより前に、設計書の確定原稿を次のキー構造で追加する。

```python
COURSE_TESTIMONIALS: tuple[dict, ...] = (
    {
        "key": "ai-agent",
        "course_name": "AIエージェント講習",
        "anchor_id": "voice-ai-agent",
        "heading": "ゼロからでも、AIエージェントが仕事の相棒になった",
        "testimonials": (
            {"title": "インストールから、実際に作れるところまで", "body": "インストールから一つずつ説明してもらい、IDEもAIエージェントもゼロから触れました。最後は自分で実際に作れるところまで進めたので、とても分かりやすかったです。"},
            {"title": "基礎がストーリーでつながり、記憶に残った", "body": "本当に使えるレベルになるには基礎が大事だと、ストーリー仕立てでみっちり教えてもらえました。覚えやすい言い回しも面白く、内容がすっと頭に入りました。"},
            {"title": "使うほど、手になじむ感覚があった", "body": "エンジニア向けに見えるツールなのに、楽しみながら使えました。使うほど手になじみ、自分の仕事でも続けられそうだと感じました。"},
        ),
    },
    {
        "key": "ai-consultation",
        "course_name": "AI個別相談",
        "anchor_id": "voice-ai-consultation",
        "heading": "その場で悩みがほどけ、明日から使える形になった",
        "testimonials": (
            {"title": "会社の業務を、そのまま相談できた", "body": "会社で使っているツールと実際の業務をそのまま相談でき、疑問点を一つずつ整理しながら、その場で解決策を見つけられたのがよかったです。"},
            {"title": "「役立ちそう」ではなく、その場で成果が見えた", "body": "これまでAIが実際の業務に役立つと感じたことはありませんでしたが、今回は本当に使える成果を見せてもらえました。作業のスピード感もあり、すぐに導入したいと思いました。"},
            {"title": "社内に導入できる形まで落とし込めた", "body": "解決策が事業の中で形になっていくのを実感できました。会社へ導入しやすいところまで整理でき、今度は自分がほかの人へ伝えられることも増えたと思います。"},
        ),
    },
    {
        "key": "ai-support",
        "course_name": "AI伴走支援",
        "anchor_id": "voice-ai-support",
        "heading": "社内の理解が進み、AI導入が動き出した",
        "testimonials": (
            {"title": "上司への説明まで支えてもらい、導入が早まった", "body": "会社の上司との話し合いにも入っていただき、新しい提案を分かりやすく説明してもらえたので、社内でのAI導入がとても早く進みました。"},
            {"title": "自分たちでは見えなかった問題を洗い出せた", "body": "私たちだけでは気づけなかった問題点を見つけてもらい、何から解決するかまで整理できました。社内でAIを活用できる可能性が見えたことがうれしかったです。"},
            {"title": "明日やることが増えた分、仕事が前へ進み始めた", "body": "YouTubeで見るだけとは違い、目の前で問題が解決していく様子は見ていて気持ちがよかったです。明日からやることは増えましたが、その分、業務がどんどん進む感覚がありました。"},
        ),
    },
    {
        "key": "ai-coding",
        "course_name": "AIコーディング講習",
        "anchor_id": "voice-ai-coding",
        "heading": "コードを書く人から、AIとチームを動かす人へ",
        "testimonials": (
            {"title": "手打ちより、仕様と順序が効率を決めると分かった", "body": "これまではコードを手で打つことに集中していましたが、プロジェクトの目的や仕様書に沿って進めることが、結果的に大きな効率化につながると分かりました。"},
            {"title": "設計・セキュリティ・公開工程まで見えた", "body": "AIはコードを書くだけでなく、ワークフローやデザイン、必要なデータ、セキュリティ、公開までの順序も提案できると知りました。プロの進め方を一つずつ理解できました。"},
            {"title": "チーム開発と採用にも使える、新しい進め方だった", "body": "部下と共同作業するときのAI活用フローがとても分かりやすかったです。GitHubやワークツリー、低コストのクラウドサービスも学べて、自動化や費用削減だけでなく、今後の採用にも役立つと感じました。"},
        ),
    },
)
```

- [x] **Step 4: 感想セクションとカードアンカーを最小実装する**

`_render_course_testimonials()`は`html.escape`を通し、外枠`<section class='course-voices' id='course-voices' aria-labelledby='course-voices-title'>`、4パネル、12の`figure/blockquote/figcaption`を返す。各コースカードのitemへ`voice_anchor`を加え、資料リンクとは別の`.compact-course-voice-row`として「このコースを受講した方の感想を見る →」を出す。

- [x] **Step 5: HTML契約テストを通す**

Run:

```powershell
& '.\.venv\Scripts\python.exe' -m unittest tests.test_course_testimonials -v
```

Expected: 3 tests PASS。

- [x] **Step 6: Task 1をコミットする**

```powershell
git add tests/test_course_testimonials.py site/build_portal.py
git commit -m "feat: add course testimonial content"
```

---

### Task 2: Course / Service / Review JSON-LD

**Files:**
- Modify: `tests/test_course_testimonials.py`
- Modify: `site/build_portal.py:198-337`

**Interfaces:**
- Consumes: `COURSE_TESTIMONIALS`
- Produces: `_testimonial_reviews(course_key: str) -> list[dict]`
- Produces: `_build_jsonld_website() -> str`内の安定したCourse/Serviceノード

- [x] **Step 1: 失敗するJSON-LD契約テストを追加する**

```python
    def test_jsonld_links_visible_reviews_to_four_stable_nodes(self) -> None:
        graph = json.loads(portal._build_jsonld_website())["@graph"]
        nodes = {node.get("@id"): node for node in graph if node.get("@id")}
        expected = {
            portal.SITE_URL + "/#course-ai-agent": "Course",
            portal.SITE_URL + "/#service-ai-consultation": "Service",
            portal.SITE_URL + "/#service-ai-support": "Service",
            portal.SITE_URL + "/#course-ai-coding": "Course",
        }
        rendered = portal._render_course_testimonials()
        for node_id, node_type in expected.items():
            node = nodes[node_id]
            self.assertEqual(node_type, node["@type"])
            self.assertEqual(3, len(node["review"]))
            for review in node["review"]:
                self.assertEqual("Review", review["@type"])
                self.assertIn(review["name"], rendered)
                self.assertIn(review["reviewBody"], rendered)
                self.assertEqual("受講者（匿名）", review["author"]["name"])

    def test_jsonld_does_not_invent_ratings(self) -> None:
        payload = portal._build_jsonld_website()
        self.assertNotIn("reviewRating", payload)
        self.assertNotIn("aggregateRating", payload)
```

- [x] **Step 2: JSON-LDテストの失敗を確認する**

Run: `& '.\.venv\Scripts\python.exe' -m unittest tests.test_course_testimonials -v`

Expected: 安定`@id`または`review`が存在せずFAIL。

- [x] **Step 3: 既存Serviceループを型別ノードへ更新する**

AIエージェント講習とAIコーディング講習を`Course`として出力し、`timeRequired: PT2H`、`courseMode: ["onsite", "online"]`、`inLanguage: ja`、`provider`、`offers`、`teaches`、`review`を付ける。AI個別相談とAI伴走支援は`Service`のまま安定`@id`と`review`を付ける。オンラインサロンは既存Serviceのまま変更しない。

`_testimonial_reviews()`は同一データから次を返す。

```python
{
    "@type": "Review",
    "name": testimonial["title"],
    "reviewBody": testimonial["body"],
    "author": {"@type": "Person", "name": "受講者（匿名）"},
}
```

- [x] **Step 4: JSON-LD契約テストを通す**

Run: `& '.\.venv\Scripts\python.exe' -m unittest tests.test_course_testimonials -v`

Expected: 全5テストPASS。

- [x] **Step 5: Task 2をコミットする**

```powershell
git add tests/test_course_testimonials.py site/build_portal.py
git commit -m "feat: add testimonial course schema"
```

---

### Task 3: レスポンシブ表示と生成HTML

**Files:**
- Modify: `tests/test_course_testimonials.py`
- Modify: `site/build_portal.py:12591-14520`
- Modify: `site/build_portal.py:14613-14626`
- Regenerate: `site/dist/index.html`

**Interfaces:**
- Consumes: `_render_course_testimonials() -> str`
- Produces: `#course-voices`を含む最終トップHTML

- [x] **Step 1: 生成HTMLとCSSの失敗テストを追加する**

```python
    def test_full_page_places_voices_after_course_menu(self) -> None:
        page = portal.render_portal([], [])
        self.assertIn("id='course-voices'", page)
        self.assertLess(page.index("course-menu-unified"), page.index("id='course-voices'"))
        self.assertLess(page.index("id='course-voices'"), page.index("course-venue-common"))
        self.assertIn(".course-voices-grid", page)
        self.assertIn("grid-template-columns:repeat(2,minmax(0,1fr))", page)
        self.assertRegex(page, r"@media \(max-width: 760px\)[\s\S]*?\.course-voices-grid\s*\{\s*grid-template-columns:1fr")
```

- [x] **Step 2: テストがCSS・挿入位置不足で失敗することを確認する**

Run: `& '.\.venv\Scripts\python.exe' -m unittest tests.test_course_testimonials -v`

- [x] **Step 3: CSSと最終ページ挿入を実装する**

`FOCUSED_PORTAL_CSS`へ`.course-voices`、`.course-voices-grid`、`.course-voice-group`、`.course-voice-card`、`.compact-course-voice-row`を追加する。パネルは既存の白背景・青緑CTA・境界色を再利用し、新色を増やさない。アンカー先には`scroll-margin-top: 96px`、PCは2列、760px以下は1列を設定する。

`_render_focused_main()`では`course-menu-unified`を閉じた直後、`course-venue-common`より前へ`_render_course_testimonials()`を挿入する。

- [x] **Step 4: 生成HTMLを更新する**

Run:

```powershell
& '.\.venv\Scripts\python.exe' site\build_site.py
```

Expected: `site/dist/index.html`に4グループ、12件、JSON-LDが生成される。

- [x] **Step 5: 対象テストと既存コーステストを通す**

```powershell
& '.\.venv\Scripts\python.exe' -m unittest tests.test_course_testimonials tests.test_course_material_mapping tests.test_hero_60sec_diagnosis tests.test_hero_text_readability -v
```

Expected: 全件PASS。

- [x] **Step 6: Task 3をコミットする**

```powershell
git add tests/test_course_testimonials.py site/build_portal.py
git add -f site/dist/index.html
git commit -m "feat: publish responsive course testimonials"
```

---

### Task 4: ローカル回帰・PC/iPhone QA

**Files:**
- Verify: `site/dist/index.html`
- Verify: `tests/test_course_testimonials.py`

**Interfaces:**
- Consumes: 完成した静的サイト
- Produces: ローカル検証証跡

- [x] **Step 1: Pillowを隔離環境だけに追加しPython回帰を実行する**

```powershell
& '.\.venv\Scripts\python.exe' -m pip install Pillow
& '.\.venv\Scripts\python.exe' -m unittest discover -s tests -p 'test_*.py'
```

Expected: PythonテストPASS。依存導入は`.venv`内だけで、`requirements.txt`は今回変更しない。

- [x] **Step 2: Node回帰を実行し既存基準との差分を確認する**

```powershell
npm.cmd run bridge:test
$commandCenterTests = Get-ChildItem -LiteralPath 'tests' -Filter '*.test.mjs' | ForEach-Object { $_.FullName }
node --test $commandCenterTests
```

Expected: Bridge 11件PASS。Command Center期限テストの既存1件以外に新しい失敗がない。

- [x] **Step 3: ローカルサーバーでPC 1440pxを確認する**

`site/dist`をHTTP配信し、トップの4コースカード、各感想リンク、4パネル、12件、予約CTA、会場案内を確認する。本文が読みやすく、2列パネルが不自然に伸びず、リンク先が固定ヘッダーで隠れないことを確認する。

- [x] **Step 4: iPhone 390pxを確認する**

感想パネルが1列、カード本文が切れない、横スクロールがない、ハンバーガーメニュー・予約CTA・資料リンクが操作できることを確認する。

- [x] **Step 5: ブラウザ状態を確認する**

コンソールエラー0、失敗ネットワーク0、`document.documentElement.scrollWidth === document.documentElement.clientWidth`、全画像`naturalWidth > 0`を確認する。

---

### Task 5: GitHub統合・Vercel本番公開

**Files:**
- Verify: scoped Git diff and commits
- Deploy: `main` through GitHub/Vercel

**Interfaces:**
- Consumes: 検証済みfeature branch
- Produces: 本番URLと本番検証証跡

- [x] **Step 1: 最終差分を限定確認する**

```powershell
git status --short --branch
git diff origin/main...HEAD --check
git diff origin/main...HEAD --stat
```

Expected: 設計書、計画書、`site/build_portal.py`、対象テスト、`site/dist/index.html`だけ。

- [x] **Step 2: 最新mainへ追随し回帰を再実行する**

`git fetch origin main`後、競合がなければfeature branchを最新`origin/main`へrebaseする。対象テストとビルドをもう一度実行する。

- [ ] **Step 3: feature branchをpushしてmainへ統合する**

```powershell
git push -u origin feat/course-testimonials-20260812
```

PRを作成し、変更範囲と検証結果を記載してmainへマージする。既存の未関連作業や元mainのdirty状態には触れない。

- [ ] **Step 4: Vercel READYを確認する**

mainのマージコミットに対応するVercel Production Deploymentが`READY`になるまで確認し、推測URLではなく`https://ai-hub-jp.vercel.app`を開く。

- [ ] **Step 5: 本番HTML・JSON-LD・PC/iPhoneを再確認する**

本番で次を確認する。

- `https://ai-hub-jp.vercel.app/#course-voices`が200で表示される。
- 4コース、12件、匿名編集注記、4アンカーが存在する。
- JSON-LDにCourse 2件、Service 2件、Review 12件があり、星評価がない。
- PC 1440pxとiPhone 390pxでCTA、ナビ、感想、コントラスト、横幅、画像、コンソールが正常。
- Vercelの対象時間帯に新しいerrorログがない。

- [ ] **Step 6: 完了報告を行う**

本番URL、確認したページ、テスト件数、コミット/PR/マージ、既存のCommand Center期限テスト1件の状況を分けて報告する。

---

## Plan Self-Review

- 設計書の4コース、12件、匿名編集、画面・JSON-LD一致、星評価禁止をTask 1とTask 2で網羅した。
- PC/iPhone、アクセシビリティ、アンカー、コントラスト、横方向のはみ出しをTask 3とTask 4で網羅した。
- commit、push、main統合、Vercel READY、本番URL、ログをTask 5で分離した。
- 関数名、定数名、anchor ID、JSON-LD IDは全Taskで統一した。
- 未確定の実装箇所や後回しの項目はない。

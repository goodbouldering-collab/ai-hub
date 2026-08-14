# コース感想プルダウン・サロン仮運用・自然スクロール Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 4コースの感想を各カード内へ移し、AIオンラインサロンを近日開始・仮運用中と正確に表示し、ヒーローから自然に縦スクロールできるトップページを本番公開する。

**Architecture:** `COURSE_TESTIMONIALS`を表示とJSON-LDの単一データ源として維持し、コースキーを受け取る小さなレンダーヘルパーで各カード内の`<details>`を生成する。サロンの公開文、FAQ、JSON-LDは同じ状態説明へそろえ、スクロールはルートCSSをブラウザ標準へ戻して解決する。

**Tech Stack:** Python 3.12、標準`unittest`、静的HTML/CSS、JSON-LD、Node.js bridge tests、Playwright + Chrome、GitHub CLI、Vercel。

## Global Constraints

- 既存の感想12件のタイトル、本文、匿名表記を変更しない。
- Review JSON-LDは12件を維持し、`reviewRating`と`aggregateRating`を追加しない。
- サロンの月額2,200円、毎月自動更新、`POST /api/square/ai-salon-checkout`、決済後のLINE参加案内を維持する。
- サロンの正式開始前状態を `AIオンラインサロン｜近日開始`、`現在は仮運用中`、登録者によるテスト運用協力として表示・FAQ・JSON-LDで一致させる。
- 縦方向のスナップ、wheel/touchの横取り、強制スクロールJavaScriptを追加しない。
- `#course-voices`と4つの`#voice-*`アンカーを維持する。
- PC 1440×900とiPhone 390×844で表示、操作、横オーバーフロー、縦スクロールを確認する。

---

### Task 1: 感想を各コースカード内のプルダウンへ移す

**Files:**
- Modify: `tests/test_course_testimonials.py`
- Modify: `site/build_portal.py:11537-11831`
- Modify: `site/build_portal.py:13049-13220`
- Modify: `site/build_portal.py:14910-14955`

**Interfaces:**
- Consumes: `COURSE_TESTIMONIALS: tuple[dict, ...]`。各要素は`key`、`course_name`、`anchor_id`、`heading`、`testimonials`を持つ。
- Produces: `_render_course_testimonial_details(course_key: str) -> str`。該当コースの感想3件を含む閉じた`<details>`を返す。
- Produces: `_render_compact_course_cards() -> str`。各カード内で既存詳細の直後に感想詳細を置く。

- [ ] **Step 1: カード内配置を要求する失敗テストへ更新する**

```python
def test_every_course_card_contains_its_matching_voice_dropdown(self) -> None:
    cards = portal._render_compact_course_cards()
    rendered_cards = re.findall(
        r"<article class='compact-course-card[^']*'.*?</article>",
        cards,
        re.DOTALL,
    )
    self.assertEqual(4, len(rendered_cards))
    for card, expected in zip(rendered_cards, EXPECTED_GROUPS, strict=True):
        key, _, anchor_id, heading, testimonials = expected
        self.assertIn(f"id='{anchor_id}'", card)
        self.assertEqual(1, card.count("受講された方の感想を見る"))
        self.assertLess(card.index("メリット・内容・参加方法を見る"), card.index("受講された方の感想を見る"))
        self.assertIn(heading, card)
        for title, body in testimonials:
            self.assertIn(title, card)
            self.assertIn(body, card)

def test_full_page_has_no_standalone_voice_section(self) -> None:
    page = portal.render_portal([], [])
    self.assertNotIn("<section class='course-voices'", page)
    self.assertIn("class='course-menu-unified' id='course-voices'", page)
    self.assertEqual(4, page.count("受講された方の感想を見る"))
```

- [ ] **Step 2: 対象テストを実行して旧配置で失敗することを確認する**

Run: `C:\Project\AI相談\_worktrees\course-testimonials-20260812\.venv\Scripts\python.exe -m unittest tests.test_course_testimonials -v`

Expected: カード内の`<details>`がなく、独立`<section class='course-voices'>`が残るためFAIL。

- [ ] **Step 3: コース別感想ヘルパーを実装する**

```python
def _render_course_testimonial_details(course_key: str) -> str:
    group = next(item for item in COURSE_TESTIMONIALS if item["key"] == course_key)
    cards = "".join(
        "<figure class='compact-course-voice-card'>"
        f"<blockquote><h4>{html.escape(item['title'])}</h4><p>{html.escape(item['body'])}</p></blockquote>"
        "<figcaption>受講者（匿名）</figcaption></figure>"
        for item in group["testimonials"]
    )
    return (
        f"<details class='compact-course-details compact-course-testimonials' id='{html.escape(group['anchor_id'], quote=True)}'>"
        "<summary>受講された方の感想を見る</summary>"
        "<div class='compact-course-testimonials-body'>"
        f"<h3>{html.escape(group['heading'])}</h3>"
        "<p class='compact-course-testimonials-note'>個人が特定されないよう一部表現を整えて掲載しています。</p>"
        f"<div class='compact-course-testimonials-list'>{cards}</div></div></details>"
    )
```

`_render_compact_course_cards()`で各itemに`testimonial_key`を持たせ、既存詳細の直後に`_render_course_testimonial_details(item["testimonial_key"])`を追加する。旧`.compact-course-voice-row`リンクは削除する。`_render_focused_main()`から`_render_course_testimonials()`呼出しを削除し、`course-menu-unified`へ`id='course-voices'`を付ける。

- [ ] **Step 4: 既存詳細と同じ操作感のCSSを追加する**

```css
.compact-course-testimonials { margin-top:10px; }
.compact-course-testimonials-body { padding:0 14px 14px; }
.compact-course-testimonials-body h3 { margin:2px 0 7px; color:var(--focus-ink); font-size:16px; line-height:1.5; }
.compact-course-testimonials-note { margin:0 0 10px; color:var(--focus-muted); font-size:11px; line-height:1.6; }
.compact-course-testimonials-list { display:grid; gap:9px; }
.compact-course-voice-card { margin:0; padding:12px; border:1px solid var(--focus-line); border-radius:10px; background:#fff; }
.compact-course-voice-card blockquote { margin:0; }
.compact-course-voice-card h4 { margin:0 0 6px; color:var(--focus-blue-dark); font-size:13px; line-height:1.5; }
.compact-course-voice-card p { margin:0; color:var(--focus-ink); font-size:12px; line-height:1.75; }
.compact-course-voice-card figcaption { margin-top:7px; color:var(--focus-ink); font-size:10px; font-weight:800; }
```

- [ ] **Step 5: 対象テストを再実行して通過を確認する**

Run: `C:\Project\AI相談\_worktrees\course-testimonials-20260812\.venv\Scripts\python.exe -m unittest tests.test_course_testimonials -v`

Expected: PASS。4カード、各3件、12件、アンカー、JSON-LDがすべて一致する。

- [ ] **Step 6: Task 1をコミットする**

```powershell
git add -- site/build_portal.py tests/test_course_testimonials.py
git commit -m "feat: 各AIコース内に感想プルダウンを配置"
```

### Task 2: オンラインサロンを近日開始・仮運用中として表示する

**Files:**
- Modify: `tests/test_salon_content_contract.py`
- Modify: `tests/test_rendered_salon.py`
- Modify: `site/build_portal.py:250-378`
- Modify: `site/build_portal.py:11857-11917`
- Modify: `site/build_portal.py:14910-14980`

**Interfaces:**
- Consumes: `AI_SALON_CHECKOUT_URL = "/api/square/ai-salon-checkout"`。
- Produces: `_render_salon_menu() -> str`。近日開始・仮運用中の説明と、既存POST決済フォームを返す。
- Produces: `_build_jsonld_website() -> str`。サロンService説明だけを現状へ合わせ、Offer URLと価格は維持する。

- [ ] **Step 1: 新しい公開状態と決済継続の失敗テストを追加する**

```python
def test_salon_is_coming_soon_but_accepts_trial_operation_payment(self) -> None:
    self.assertIn("AIオンラインサロン｜近日開始", self.panel)
    self.assertIn("現在は仮運用中", self.panel)
    self.assertIn("登録中の方にはテスト運用へご協力いただいています", self.panel)
    self.assertIn("Squareで決済して仮運用に参加", self.panel)
    self.assertIn("action='/api/square/ai-salon-checkout'", self.panel)
    self.assertIn("月額2,200円（税込）", self.panel)
    self.assertIn("毎月自動更新", self.panel)
```

`tests/test_rendered_salon.py`の旧CTA期待値を`Squareで決済して仮運用に参加`へ変更し、フォーム数が1である検証を残す。

- [ ] **Step 2: 対象テストを実行して旧文言で失敗することを確認する**

Run: `C:\Project\AI相談\_worktrees\course-testimonials-20260812\.venv\Scripts\python.exe -m unittest tests.test_salon_content_contract tests.test_rendered_salon -v`

Expected: 近日開始、仮運用、テスト協力、仮運用CTAが未出力のためFAIL。

- [ ] **Step 3: サロンカード、FAQ、メタ説明、JSON-LDを同じ状態へ更新する**

```python
salon_title = "AIオンラインサロン｜近日開始"
salon_description = (
    "月額2,200円（税込）。正式開始に向けて現在は仮運用中で、"
    "登録中の方にはテスト運用へご協力いただいています。"
    "Square決済後にLINE参加案内を表示します。"
)
```

カード状態ラベルは`現在は仮運用中`、見出しは`AIオンラインサロン｜近日開始`、説明は設計書の2文、CTAは`Squareで決済して仮運用に参加 →`とする。FAQとページdescriptionも正式運用中と読める箇所を同じ表現へ更新する。

- [ ] **Step 4: 対象テストとJSON-LD検証を通す**

Run: `C:\Project\AI相談\_worktrees\course-testimonials-20260812\.venv\Scripts\python.exe -m unittest tests.test_salon_content_contract tests.test_rendered_salon tests.test_course_testimonials -v`

Expected: PASS。サロンOfferの価格、URL、POSTフォーム、LINE境界も維持される。

- [ ] **Step 5: Task 2をコミットする**

```powershell
git add -- site/build_portal.py tests/test_salon_content_contract.py tests/test_rendered_salon.py
git commit -m "feat: AIオンラインサロンの近日開始と仮運用を明記"
```

### Task 3: ヒーローからの縦スクロールをブラウザ標準へ戻す

**Files:**
- Create: `tests/test_natural_page_scroll.py`
- Modify: `site/build_portal.py:624-625`
- Modify: `site/build_portal.py:12816-12820`
- Modify: `site/build_portal.py:14868-14890`

**Interfaces:**
- Consumes: `PORTAL_CSS`と`FOCUSED_PORTAL_CSS`。
- Produces: 生成HTML内のルートCSS `overflow-x: clip; overflow-y: visible; scroll-behavior: auto;`。
- Produces: `_render_hero_focused()`の完成状態の本文。初期`fade-up`を持たない。

- [ ] **Step 1: 自然スクロールのCSS契約を表す失敗テストを作る**

```python
import importlib.util
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("natural_scroll_portal", ROOT / "site" / "build_portal.py")
portal = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(portal)

class NaturalPageScrollTest(unittest.TestCase):
    def test_root_uses_single_native_vertical_scroll(self) -> None:
        css = portal.PORTAL_CSS + portal.FOCUSED_PORTAL_CSS
        self.assertRegex(css, r"html, body\s*\{[^}]*overflow-x:\s*clip")
        self.assertRegex(css, r"html, body\s*\{[^}]*overflow-y:\s*visible")
        self.assertNotRegex(css, r"html\s*\{\s*scroll-behavior:\s*smooth")
        self.assertNotRegex(css, r"(?:html|body)[^{]*\{[^}]*scroll-snap-type:\s*y")

    def test_hero_is_ready_without_entrance_pause(self) -> None:
        hero = portal._render_hero_focused()
        self.assertIn("class='focus-hero-copy'", hero)
        self.assertNotIn("class='focus-hero-copy fade-up'", hero)
```

- [ ] **Step 2: 新規テストを実行して現状で失敗することを確認する**

Run: `C:\Project\AI相談\_worktrees\course-testimonials-20260812\.venv\Scripts\python.exe -m unittest tests.test_natural_page_scroll -v`

Expected: `overflow-x: hidden`、`scroll-behavior: smooth`、ヒーロー`fade-up`のためFAIL。

- [ ] **Step 3: ルートCSSとヒーロー初期クラスを最小変更する**

```css
html, body { margin:0; padding:0; overflow-x:clip; overflow-y:visible; }
html { scroll-behavior:auto; }
```

FOCUSED_PORTAL_CSS側の重複指定も`scroll-behavior:auto`へそろえる。`_render_hero_focused()`の`<div class='focus-hero-copy fade-up'>`を`<div class='focus-hero-copy'>`へ変更する。横カルーセルの`scroll-snap-type:x mandatory`は変更しない。

- [ ] **Step 4: 新規テストを通す**

Run: `C:\Project\AI相談\_worktrees\course-testimonials-20260812\.venv\Scripts\python.exe -m unittest tests.test_natural_page_scroll -v`

Expected: PASS。

- [ ] **Step 5: Task 3をコミットする**

```powershell
git add -- site/build_portal.py tests/test_natural_page_scroll.py
git commit -m "fix: ヒーローから自然に縦スクロールできるよう調整"
```

### Task 4: 生成、全テスト、実画面検証、本番公開

**Files:**
- Modify: `site/dist/index.html`
- Verify: `site/build_portal.py`
- Verify: `tests/*.py`

**Interfaces:**
- Consumes: Task 1〜3のソースとテスト。
- Produces: 本番配信用`site/dist/index.html`、GitHub PR、mainコミット、Vercel Production deployment。

- [ ] **Step 1: 静的サイトを再生成する**

Run: `C:\Project\AI相談\_worktrees\course-testimonials-20260812\.venv\Scripts\python.exe site\build_site.py`

Expected: `site/dist/index.html`が新しい感想配置、サロン状態、スクロールCSSで更新される。

- [ ] **Step 2: PythonとNodeの全テストを実行する**

```powershell
& 'C:\Project\AI相談\_worktrees\course-testimonials-20260812\.venv\Scripts\python.exe' -m unittest discover -s tests -p 'test_*.py'
npm.cmd run bridge:test
```

Expected: Python全件PASS、bridge 11件PASS。

- [ ] **Step 3: ローカル画面をPC・iPhoneで検証する**

Chrome/Playwrightで1440×900と390×844を確認する。

- 4カードに感想プルダウンが各1つあり、閉じた状態はコンパクト。
- 各プルダウンに3件だけ表示される。
- サロンに近日開始、仮運用、テスト協力、決済CTAが表示される。
- Squareフォームのactionは`/api/square/ai-salon-checkout`。
- 最初のwheelまたはtouch swipeで`scrollY > 0`となり、連続入力で単調増加する。
- `document.documentElement.scrollWidth <= innerWidth`。
- コンソールerrorが0件。
- JSON-LDのCourseが2、Service対象が2、Reviewが12、評価点が0。

- [ ] **Step 4: 生成物をコミットする**

```powershell
git add -- site/dist/index.html
git commit -m "build: 公開トップを再生成"
```

- [ ] **Step 5: ブランチをpushしてPRを作成する**

```powershell
git push -u origin codex/course-testimonial-dropdowns-20260812
gh pr create --base main --head codex/course-testimonial-dropdowns-20260812 --title "コース感想をカード内へ移動しサロン仮運用を明記" --body "## 変更\n- 各AIコース内に感想プルダウンを配置\n- AIオンラインサロンの近日開始・仮運用を明記しSquare決済を維持\n- ヒーローからの縦スクロールを自然な挙動へ修正\n\n## 確認\n- Python全テスト\n- bridge 11テスト\n- PC 1440x900 / iPhone 390x844\n- Review JSON-LD 12件・評価点なし"
```

PR本文には変更3点、テスト結果、PC/iPhone結果、感想と決済条件を維持したことを書く。

- [ ] **Step 6: PRをmainへ反映しVercel Productionを確認する**

mainの自動デプロイを待ち、Project ID `prj_e7vh73eF0KZpm8C49esnILvHO98o`の最新ProductionがREADYであることを確認する。

- [ ] **Step 7: 本番URLを再検証する**

Verify: `https://aiclimb.vercel.app/`

ローカルと同じPC/iPhone操作、4つの感想、サロン状態、Squareフォームaction、12 Review、横オーバーフロー、縦スクロール、コンソールerrorを確認する。

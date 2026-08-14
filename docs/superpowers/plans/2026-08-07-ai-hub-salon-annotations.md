# AI相談トップページ注釈反映 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (- [ ]) syntax for tracking.

**Goal:** 講習資料リンク、AIオンラインサロンの説明・決済導線、ヒーローの料金表示を、ユーザー指定の文言と順序へ安全に更新し、本番で確認する。

**Architecture:** 公開トップページは site/build_portal.py がHTML/CSSを一体で生成し、site/dist/index.html は生成物として公開される。講習資料リンクはカード直下の共通ボタンセレクタからHTML構造で分離し、サロンはDOM順そのものを変更して視覚順・読み上げ順を一致させる。文言変更は既存の要素とスタイルを再利用する。

**Tech Stack:** Python 3.12、静的HTML/CSS生成、Python unittest、GitHub、Vercel

## Global Constraints

- 公開トップページの変更元は site/build_portal.py、生成先は site/dist/index.html とする。
- 料金、Square決済URL、月額課金、LINE参加ゲート、講習資料のURL、予約導線は変更しない。
- 資料リンクは全講習カードで下線付き通常リンクに統一し、横幅いっぱいの疑似ボタンにしない。
- サロンの注記はDOM上でもSquare決済フォームの直前に置く。
- サロンの新しいタグラインは AIの最新も疑問もその場で解決できる。 と完全一致させる。
- ヒーローの料金表示は 相談5,500円/回 と完全一致させ、大きな「6%」・AI利用率表示・既存のバッジスタイルは維持する。
- PC幅（1294px前後）とスマホ幅（390px前後）の両方で、横スクロールなく確認する。
- 既存の未整理変更には触れず、C:/tmp/ai-consult-salon-annotations-20260807 の隔離ブランチだけを変更する。

---

### Task 1: 講習カードの資料導線を通常リンクに分離する

**Files:**
- Modify: site/build_portal.py:11554-11560,13029-13031
- Modify: tests/test_course_material_mapping.py:68-94
- Generated: site/dist/index.html

**Interfaces:**
- Consumes: _render_compact_course_cards() の各 item が持つ material_url と material_cta。
- Produces: 各講習カードに p.compact-course-material-row > a.compact-course-material を出力する。予約CTAの直接子aと資料リンクを別DOM階層にする。

- [ ] **Step 1: 資料リンク用の失敗する回帰テストを書く**

tests/test_course_material_mapping.py の test_course_cards_link_to_the_matching_material に、AIエージェント講習カードについて次の構造を検証するアサーションを追加する。

~~~python
self.assertIn(
    "<p class='compact-course-material-row'><a class='compact-course-material' "
    "href='/lectures/2026-04-ai-kihon.html'>AIエージェント講習の受講資料を見る →</a></p>",
    agent_card,
)
self.assertIn(".compact-course-material-row {", self.index_html)
self.assertNotIn(
    "</a><a class='compact-course-material' href='/lectures/2026-04-ai-kihon.html'>",
    agent_card,
)
~~~

- [ ] **Step 2: テストが失敗することを確認する**

~~~powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_course_material_mapping
~~~

期待結果: compact-course-material-row が未出力のため失敗する。

- [ ] **Step 3: 最小限のHTML/CSSを実装する**

site/build_portal.py の material_html を次の構造へ置き換える。

~~~python
material_html = (
    "<p class='compact-course-material-row'>"
    f"<a class='compact-course-material' href='{html.escape(material_url, quote=True)}'{material_target_attr}>"
    f"{html.escape(item['material_cta'])} →</a>"
    "</p>"
    if material_url else ""
)
~~~

カード直下の旧セレクタを削除し、次の専用スタイルを同じCSSブロックへ置く。

~~~css
.compact-course-material-row { margin:7px 0 0; }
.compact-course-card .compact-course-material {
  display:inline;
  padding:0;
  color:var(--focus-blue);
  background:transparent;
  border-radius:0;
  font-size:11px;
  font-weight:800;
  line-height:1.5;
  text-decoration:underline;
  text-underline-offset:3px;
}
.compact-course-card .compact-course-material:hover {
  color:var(--focus-blue-dark);
  background:transparent;
}
~~~

- [ ] **Step 4: 生成してテストを通す**

~~~powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' site\build_portal.py
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_course_material_mapping
~~~

期待結果: 資料URL・文言を保ったまま、追加アサーションを含むテストが成功する。

- [ ] **Step 5: ソースとテストをコミットする**

~~~powershell
git add site/build_portal.py tests/test_course_material_mapping.py
git commit -m "fix: render course materials as text links"
~~~

### Task 2: サロンの説明文と決済注記の順序を更新する

**Files:**
- Modify: site/build_portal.py:11661-11678,13102-13107,13498,13588-13591,13870-13875,14074,14109-14112
- Modify: tests/test_rendered_salon.py:31-65
- Modify: tests/test_salon_content_contract.py:26-116
- Generated: site/dist/index.html

**Interfaces:**
- Consumes: サロン詳細、p.salon-simple-note、form.compact-course-checkout.salon-card-checkout、受講資料リンク。
- Produces: details → salon-simple-note → checkout form → salon material link のDOM順。salon-intro-summary は出力しない。

- [ ] **Step 1: サロン文言とDOM順の失敗するテストを書く**

tests/test_rendered_salon.py の test_salon_is_one_complete_menu_before_the_venue_map に次を追加する。

~~~python
note = self.html.index("class='salon-simple-note'", details)
self.assertLess(details, note)
self.assertLess(note, checkout)
~~~

tests/test_salon_content_contract.py に次を追加する。

~~~python
self.assertIn("AIの最新も疑問もその場で解決できる。", self.panel)
self.assertNotIn(
    "全部を追わず、新機能と一流の活用事例から、今試すことを短く整理します。",
    self.panel,
)
~~~

同じテストの expected_details では、旧タグラインを新タグラインへ置き換え、旧要約文の項目を削除する。

~~~diff
- "AIの最新を、仕事の次の一手に。",
+ "AIの最新も疑問もその場で解決できる。",
- "全部を追わず、新機能と一流の活用事例から、今試すことを短く整理します。",
~~~

- [ ] **Step 2: テストが失敗することを確認する**

~~~powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_rendered_salon tests.test_salon_content_contract
~~~

期待結果: 旧タグライン、要約文、注記の決済後DOM順が残っているため失敗する。

- [ ] **Step 3: サロン出力を最小限更新する**

サロン紹介HTMLを次の順序へ調整する。要約段落は完全に削除する。

~~~python
"<p class='salon-intro-tagline'>AIの最新も疑問もその場で解決できる。</p>"
"<p class='salon-intro-description'>Squareで月額決済後、LINEライブトークの参加案内を表示します。仕事で次に試すことを一緒に決めます。聞くだけOK。</p>"
"</div></details>"
"<p class='salon-simple-note'>月額2,200円（税込）・毎月自動更新。決済確認後にLINE参加案内を表示します</p>"
f"<form class='compact-course-checkout salon-card-checkout' method='post' action='{html.escape(AI_SALON_CHECKOUT_URL, quote=True)}'><button type='submit'>Squareで決済して参加 →</button></form>"
"<p class='salon-material-row'><a class='compact-course-material salon-material-link' href='/lectures/2026-07-ai-online-salon-practice.html'>オンラインサロン受講資料を見る →</a></p>"
~~~

salon-intro-summary のPC・タブレット・モバイル用スタイルを削除し、注記の余白を次にする。

~~~css
.salon-simple-note {
  margin:12px 0 7px;
  color:var(--focus-muted);
  font-size:9.5px;
  text-align:center;
}
~~~

- [ ] **Step 4: 生成してサロン契約テストを通す**

~~~powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' site\build_portal.py
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_rendered_salon tests.test_salon_content_contract
~~~

期待結果: Square決済URL、LINE参加ゲート、詳細数を保ったまま、新文言とDOM順のテストが成功する。

- [ ] **Step 5: ソースとテストをコミットする**

~~~powershell
git add site/build_portal.py tests/test_rendered_salon.py tests/test_salon_content_contract.py
git commit -m "fix: clarify salon copy and payment order"
~~~

### Task 3: ヒーローの料金表示を指定文言へ置き換える

**Files:**
- Modify: site/build_portal.py:14573-14575
- Modify: tests/test_rendered_salon.py:67-70
- Generated: site/dist/index.html

**Interfaces:**
- Consumes: aside#advantage .hero-advantage-copy small strong の既存バッジとレスポンシブCSS。
- Produces: 同じstrong要素に 相談5,500円/回 を出力する。レイアウト用クラス・CSSは変えない。

- [ ] **Step 1: ヒーロー料金表示の失敗するテストを書く**

tests/test_rendered_salon.py の test_hero_and_menu_order でヒーロー範囲を取り出し、次を検証する。

~~~python
hero_start = self.html.index("class='focus-hero'")
hero_end = self.html.index("</section>", hero_start)
hero = self.html[hero_start:hero_end]
self.assertIn("<strong>相談5,500円/回</strong>", hero)
self.assertNotIn("<strong>利用率6%</strong>", hero)
~~~

- [ ] **Step 2: テストが失敗することを確認する**

~~~powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_rendered_salon
~~~

期待結果: 旧バッジ文言が生成HTMLに残っているため失敗する。

- [ ] **Step 3: 同じバッジ要素の文言だけを置き換える**

site/build_portal.py のヒーロー出力を次の文字列にする。

~~~python
"<div class='hero-advantage-copy'><small><strong>相談5,500円/回</strong><span>始めるなら今。</span></small><p id='hero-advantage-title'><span class='hero-advantage-equation'><strong>経験</strong><span>×</span><strong>AI</strong></span><span class='hero-advantage-outcome'>で、仕事を一歩先へ。</span></p></div>"
~~~

- [ ] **Step 4: 生成してテストを通す**

~~~powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' site\build_portal.py
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_rendered_salon tests.test_hero_text_readability
~~~

期待結果: 新しい料金表示がヒーロー内にあり、CSSの可読性契約を維持してテストが成功する。

- [ ] **Step 5: ソースとテストをコミットする**

~~~powershell
git add site/build_portal.py tests/test_rendered_salon.py
git commit -m "fix: clarify hero consultation price"
~~~

### Task 4: 生成物・ブラウザ・本番を検証して公開する

**Files:**
- Modify: site/dist/index.html (生成物)
- Verify: site/build_portal.py, site/build_site.py, tests/test_course_material_mapping.py, tests/test_rendered_salon.py, tests/test_salon_content_contract.py, tests/test_hero_text_readability.py

**Interfaces:**
- Consumes: Tasks 1〜3のソース・回帰テスト。
- Produces: 本番 https://aiclimb.vercel.app/index.html に反映された5点の画面変更と、確認済みの公開URL。

- [ ] **Step 1: 生成物を完全に再構築する**

~~~powershell
$env:AIWATCH_PORTFOLIO_NO_FETCH = '1'
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' site\build_portal.py
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' site\build_site.py
~~~

- [ ] **Step 2: 関連テストと生成物の文言を確認する**

~~~powershell
& 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -m unittest tests.test_course_material_mapping tests.test_rendered_salon tests.test_salon_content_contract tests.test_hero_text_readability
rg -n "相談5,500円/回|AIの最新も疑問もその場で解決できる。|salon-simple-note|compact-course-material-row" site\dist\index.html
$oldSummary = rg -n "salon-intro-summary|全部を追わず、新機能と一流の活用事例から、今試すことを短く整理します。" site\dist\index.html
if ($LASTEXITCODE -eq 0) { throw "削除対象のサロン要約が生成物に残っています: $oldSummary" }
git diff --check
~~~

期待結果: 全テスト成功。新しい2文言と新しい資料リンク行・注記が存在し、削除対象の salon-intro-summary は存在しない。

- [ ] **Step 3: 生成済みトップページをコミットする**

~~~powershell
git add -f site/dist/index.html
git commit -m "chore: regenerate homepage annotations"
~~~

- [ ] **Step 4: ローカルでPC・スマホ表示を確認する**

次のサーバーで site/dist/index.html を開く。

~~~powershell
Start-Process -FilePath 'C:\Users\yui\AppData\Local\Programs\Python\Python312\python.exe' -ArgumentList @('-m','http.server','4173','--bind','127.0.0.1') -WorkingDirectory 'C:\tmp\ai-consult-salon-annotations-20260807\site\dist' -WindowStyle Hidden
~~~

http://127.0.0.1:4173/index.html を1294px前後と390px前後で確認し、次を満たす。

~~~text
- .compact-course-card--main .compact-course-material は下線付きテキストで、カード幅より短く、青い塗りボタンでない。
- .salon-simple-note は .salon-card-checkout より上にあり、DOM順も同じである。
- 旧要約文は存在せず、タグラインは指定文言である。
- #advantage .hero-advantage-copy small strong は「相談5,500円/回」である。
- document.documentElement.scrollWidth === window.innerWidth がPC・スマホともに成り立つ。
~~~

- [ ] **Step 5: ブランチを公開して本番反映を確認する**

~~~powershell
git push -u origin codex/salon-annotation-polish-20260807
gh pr create --base main --head codex/salon-annotation-polish-20260807 --title "fix: AI相談トップページの注釈を反映" --body "講習資料リンク、サロンの説明・決済注記、ヒーロー料金表示を更新します。"
gh pr merge --merge --delete-branch
~~~

Vercelのデプロイ成功後、https://aiclimb.vercel.app/index.html を1294px前後と390px前後で再確認し、Step 4の5条件と予約・Square決済・受講資料リンク先を確認する。

# AIアプリサイト サービス実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** AI相談の無料相談から、業務をAIアプリサイトへ変えるサービス導線を公開する。

**Architecture:** `site/ai_app_site.py` が主サービスページと5つの用途別ページを静的HTMLとして返す。`site/build_site.py` がページ群とサイトマップを生成し、`site/build_portal.py` と `site/public_navigation.py` がトップと公開メニューから同じ導線へつなぐ。

**Tech Stack:** Python静的サイトジェネレータ、HTML/CSS、unittest、Vercel static hosting。

**Spec:** `docs/superpowers/specs/2026-08-20-ai-app-site-service-design.md`

## Global Constraints

- 新規の対外文言は「AI相談」に統一し、技術名ではなく業務結果から伝える。
- すべての無料相談CTAは既存の `DIAGNOSIS_FREE_CONSULT_BOOK_URL` を使う。
- SNSへの実投稿、広告出稿、価格決済、個人情報送信は行わない。
- 公開ナビはPCとモバイルで同一項目にし、390pxで横overflowを出さない。
- `site/dist` はVercel静的配信用のため、追加ルートを追跡対象にする。

---

### Task 1: サービスページの契約テストを追加する

**Files:**
- Create: `tests/test_ai_app_site_pages.py`
- Modify: `tests/test_public_navigation_parity.py`

**Interfaces:**
- Consumes: `site.build_site.build_ai_app_site_pages()`, `site.build_portal.render_portal()`, `site.public_navigation.render_desktop_navigation()`。
- Produces: サービスページ、サイトマップ、トップCTA、ナビの公開契約を検証するテスト。

- [ ] **Step 1: Write the failing test**

```python
with tempfile.TemporaryDirectory() as tmp:
    site_builder.DIST = Path(tmp)
    site_builder.build_ai_app_site_pages()
    html = (Path(tmp) / "ai-app-site" / "index.html").read_text(encoding="utf-8")
assert "その仕事、サイトにやらせませんか？" in html
assert "AIアプリサイト Lite" in html
assert "99,000円〜" in html
```

- [ ] **Step 2: Run test to verify it fails**

Run: `.venv\\Scripts\\python.exe -m unittest tests.test_ai_app_site_pages -v`

Expected: FAIL because `build_ai_app_site_pages` does not exist and the new route is absent.

- [ ] **Step 3: Extend navigation test**

```python
PUBLIC_LINKS = [
    ("/#top", "ホーム"),
    ("/ai-app-site/", "AIアプリサイト"),
    ("/#all-works", "実績"),
]
```

- [ ] **Step 4: Run the focused test group**

Run: `.venv\\Scripts\\python.exe -m unittest tests.test_ai_app_site_pages tests.test_public_navigation_parity -v`

Expected: FAIL because the current menu has no AIアプリサイト item.

### Task 2: 専用サービスページ群と生成処理を実装する

**Files:**
- Create: `site/ai_app_site.py`
- Modify: `site/build_site.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: `site_url`, `nav_html`, `favicon_html`, `shared_header_css`, `DIAGNOSIS_FREE_CONSULT_BOOK_URL`。
- Produces: `build_ai_app_site_pages()` が `site/dist/<route>/index.html` を作成する。

- [ ] **Step 1: Implement the route renderer**

```python
def render_ai_app_site_page(slug, site_url, nav_html, favicon_html, shared_header_css, free_consult_url):
    return "<!doctype html>..."

def render_all_ai_app_site_pages(...):
    return {"ai-app-site": render_ai_app_site_page("ai-app-site", ...)}
```

- [ ] **Step 2: Add the builder hook and sitemap entries**

```python
def build_ai_app_site_pages() -> int:
    pages = render_all_ai_app_site_pages(...)
    for route, document in pages.items():
        (DIST / route / "index.html").write_text(document, encoding="utf-8")
    return len(pages)
```

- [ ] **Step 3: Keep built routes deployable**

```gitignore
!site/dist/ai-app-site/
!site/dist/ai-app-site/**
!site/dist/ai-estimate/
!site/dist/ai-estimate/**
```

- [ ] **Step 4: Run the focused tests**

Run: `.venv\\Scripts\\python.exe -m unittest tests.test_ai_app_site_pages -v`

Expected: PASS with all six routes and canonical sitemap URLs.

### Task 3: トップと共通メニューを無料相談導線へ更新する

**Files:**
- Modify: `site/public_navigation.py`
- Modify: `site/build_portal.py`

**Interfaces:**
- Consumes: `DIAGNOSIS_FREE_CONSULT_BOOK_URL` and the `/ai-app-site/` route.
- Produces: ヒーロー、サービス案内、最終CTA、PC/モバイルナビ。

- [ ] **Step 1: Add the shared navigation item**

```python
("app-site", "AIアプリサイト", "/ai-app-site/"),
```

- [ ] **Step 2: Replace the hero's primary offer**

```html
<p class='focus-kicker'>AI相談 × AIアプリサイト</p>
<h1>相談だけで終わらない。<br>AIで、仕事の仕組みまでつくる。</h1>
<a href='DIAGNOSIS_FREE_CONSULT_BOOK_URL'>まずは無料相談</a>
```

- [ ] **Step 3: Add the service card section after the hero**

```html
<section id='ai-app-site'>
  <h2>その仕事、サイトにやらせませんか？</h2>
  <a href='/ai-estimate/'>見積もり → 自動作成</a>
</section>
```

- [ ] **Step 4: Run page and navigation tests**

Run: `.venv\\Scripts\\python.exe -m unittest tests.test_ai_app_site_pages tests.test_public_navigation_parity -v`

Expected: PASS with the new service route in both menus and a free-consult CTA on the home page.

### Task 4: 相談資料と広告原稿を再利用資産として追加する

**Files:**
- Create: `content/lectures/2026-08-ai-app-site-consult-sheet.md`
- Create: `content/campaigns/2026-08-20-ai-app-site-service/README.md`
- Create: `content/campaigns/2026-08-20-ai-app-site-service/service-offer.md`
- Create: `content/campaigns/2026-08-20-ai-app-site-service/ad-copy.md`

**Interfaces:**
- Consumes: 公開済みの価格表、無料相談の進め方、用途別サービスページ。
- Produces: 無料相談で使う資料と、Facebook・Instagramで転用する未投稿原稿。

- [ ] **Step 1: Add the consultation sheet**

```markdown
## 無料相談で持ってくる3つ
1. いちばん時間がかかる作業
2. 今の手順がわかる紙・Excel・URL
3. 月に何回、何分かかるか
```

- [ ] **Step 2: Add ad copy variants**

```markdown
見出し: 毎月10時間やっているその作業、10分にできるかもしれません。
行動: 無料相談で、まず一つの作業から整理する。
```

- [ ] **Step 3: Run the material build test**

Run: `.venv\\Scripts\\python.exe -m unittest tests.test_ai_app_site_pages -v`

Expected: PASS with the consultation sheet generated under `lectures/`.

### Task 5: 完全ビルドと公開検証を行う

**Files:**
- Modify: generated `site/dist/ai-app-site/**`, `site/dist/ai-estimate/**`, `site/dist/ai-inquiry/**`, `site/dist/ai-reservation/**`, `site/dist/ai-shift/**`, `site/dist/ai-blog/**`

**Interfaces:**
- Consumes: 全サービスソース、静的アセット、Vercelのmainブランチデプロイ。
- Produces: 本番で到達できる公開URL。

- [ ] **Step 1: Build and run all tests**

Run: `.venv\\Scripts\\python.exe site/build_site.py`, `.venv\\Scripts\\python.exe -m unittest discover -s tests -p 'test_*.py'`, `node --test tests/*.test.mjs`

Expected: Build exit 0, Python and Node suites pass.

- [ ] **Step 2: Run syntax and diff checks**

Run: `npx.cmd tsc --noEmit`, `git diff --check`

Expected: exit 0 with no whitespace errors.

- [ ] **Step 3: Verify PC and iPhone viewports**

Run: local browser checks at 1280px and 390px for `/`, `/ai-app-site/`, and one solution page.

Expected: meaningful content, no console errors, no horizontal overflow, and a usable free-consult CTA.

- [ ] **Step 4: Commit, push, and verify production**

Run: `git commit`, `git push origin HEAD:main`, then browser checks against the Vercel production URL.

Expected: deployment reaches READY and the public service route is reachable.

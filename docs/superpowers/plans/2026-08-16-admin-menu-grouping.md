# Admin Menu Grouping Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 管理メニューを用途別グループに整理し、PCと390pxで短く分かりやすく表示する。

**Architecture:** `admin-menu.js` の単一データモデルからPC用ドロップダウンとモバイル用折りたたみを生成する。`admin-common.css` の管理ヘッダー境界にだけ新しいコンポーネントCSSを追加する。

**Tech Stack:** Vanilla JavaScript, HTML details/summary, CSS, Node test runner, Playwright

## Global Constraints

- 公開側メニューは変更しない。
- 既存管理URLと共通タイトルを維持する。
- PC幅と390px、44px操作領域、Esc、フォーカス、横はみ出しを検証する。
- 元の未コミット変更には触れない。

---

### Task 1: 情報階層の回帰テスト

**Files:**
- Modify: `tests/admin-menu-unification.test.mjs`

**Interfaces:**
- Consumes: `site/static/admin/admin-menu.js` が生成する共有ヘッダーHTML
- Produces: 5グループ、説明、現在地、折りたたみ構造の契約

- [x] 新構造を要求するテストを追加する。
- [x] `node --test tests/admin-menu-unification.test.mjs` を実行し、旧フラットメニューで失敗することを確認する。

### Task 2: 共通メニュー実装

**Files:**
- Modify: `site/static/admin/admin-menu.js`
- Modify: `site/static/admin/admin-common.css`

**Interfaces:**
- Consumes: 現在の `window.location.pathname`
- Produces: `menuGroups` から生成した `.admin-menu-desktop-group` と `.admin-menu-mobile-group`

- [x] PC用detailsドロップダウンと説明付きリンクを生成する。
- [x] モバイル用details折りたたみを同じデータから生成する。
- [x] 1グループだけ開く、外側クリック、Esc、リンク選択、721px以上へのリサイズで閉じる処理を実装する。
- [x] 共有ヘッダー内だけにレイアウト、現在地、フォーカス、レスポンシブCSSを追加する。
- [x] 対象テストを再実行して通過させる。

### Task 3: 検証と公開

**Files:**
- Test: `tests/admin-menu-unification.test.mjs`
- Test: `tests/test_admin_menu_css_parity.py`

**Interfaces:**
- Consumes: 本番ビルドとVercel管理画面URL
- Produces: PC／390pxの表示証拠と本番URL

- [x] Node、Python、TypeScript、サイトビルドを実行する。
- [x] PCと390pxで主要管理画面、ドロップダウン、現在地、Esc、横はみ出し、コンソールを確認する。
- [ ] commitして`main`へpushし、Vercel Readyと本番表示を確認する。

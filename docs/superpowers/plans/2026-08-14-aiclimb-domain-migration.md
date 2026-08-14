# AI相談 aiclimb ドメイン統一 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 現行の公開トップ、管理画面、SEOメタデータ、APIの戻り先、生成済み公開物を `https://aiclimb.vercel.app` に統一する。

**Architecture:** URLの既定値をビルド層で統一し、API・ブリッジ・設定のフォールバックも同じ本番オリジンへ変更する。静的サイトは再ビルドして canonical、OG、JSON-LD、sitemap を再生成し、追跡対象の現行コンテンツから旧ホストをなくす。

**Tech Stack:** Python 静的サイトビルダー、TypeScript Vercel Functions、Node.js テスト、Vercel Git連携

## Global Constraints

- 本番正本は `https://aiclimb.vercel.app` とする。
- 管理画面、公開トップ、SEO、APIフォールバック、ブリッジ許可オリジンを同じホストに揃える。
- 他作業の未コミット変更には触れず、専用ワークツリーのみで作業する。
- 公開確認はPC幅とiPhone幅、トップと管理画面を含める。

---

### Task 1: 本番オリジンの回帰テスト

**Files:**
- Modify: `bridge/bridge.test.mjs`
- Create: `tests/test_production_domain.py`

**Interfaces:**
- Consumes: `bridge/bridge.mjs` の `isAllowedOrigin()` と `site/build_site.py` の実ビルド
- Produces: 新ホストのみを許可し、生成物に新ホストを出力する回帰テスト

- [x] **Step 1: 新ホストを期待する失敗テストを書く**
- [x] **Step 2: 対象テストを実行し、旧ホスト実装により失敗することを確認する**
- [x] **Step 3: フォールバック・許可オリジン・ビルド既定値を新ホストへ変更する**
- [x] **Step 4: テストを再実行し、成功することを確認する**

### Task 2: 公開コンテンツと生成物のURL置換

**Files:**
- Modify: `api/**`, `bridge/**`, `config/**`, `content/**`, `media/output/**`, `site/**`, `AGENTS.md`, `CLAUDE.md`, `docs/**`, `tests/**`

**Interfaces:**
- Consumes: 新しい本番オリジン
- Produces: 公開・生成・運用コンテンツ内で旧ホストを含まない追跡済みファイル群

- [x] **Step 1: 追跡済みテキスト全体の旧ホスト出現箇所を再確認する**
- [x] **Step 2: 旧ホストを新ホストへ機械置換する**
- [x] **Step 3: 静的サイトを再ビルドする**
- [x] **Step 4: 追跡済みテキストを再検索し、旧ホストが残らないことを確認する**

### Task 3: リリースと実表示確認

**Files:**
- Verify: `site/dist/index.html`, `site/dist/sitemap.xml`, `/`, `/admin`

**Interfaces:**
- Consumes: GitHub main の対象コミットとVercel本番ドメイン
- Produces: 新ドメインで到達できる公開トップ・認証付き管理画面・SEOメタデータ

- [x] **Step 1: Python/Node/TypeScript検査と差分検査を実行する**
- [ ] **Step 2: コミットしてmainへ反映する**
- [ ] **Step 3: Vercel本番URLでトップと管理画面を確認する**
- [ ] **Step 4: PC/iPhone幅で横スクロール、メニュー、console errorを確認する**

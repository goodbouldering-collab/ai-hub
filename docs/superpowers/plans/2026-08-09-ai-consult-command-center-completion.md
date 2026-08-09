# AI相談 実行司令室移行完了 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:executing-plans` to execute this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 実行司令室の管理機能・移行要件・安全な設定を AI相談の管理ログイン配下へ取り込み、課題期限と Google の予定件数を AI相談のカレンダーで確認できる状態にする。

**Architecture:** `origin/main` を土台に、検証済みの移行ブランチから依存順で8コミットを取り込む。AI相談の `withAdmin` をすべての新規画面/APIに適用し、Google Calendar は `busy_only` の日別件数に限定する。課題期限は保護済みのダッシュボードデータから同じカレンダーへ重ね、予定名などの ICS 情報は表示しない。

**Tech Stack:** Vercel Functions (TypeScript), 静的 HTML/CSS/JavaScript, Node.js test runner, Supabase SQL migration/RLS, Vercel, Google Calendar ICS.

## Global Constraints

- 新規の画面/APIは既存 `withAdmin` を必ず通し、未認証HTMLはログインへ遷移、未認証APIは401を返す。
- Google Calendar は `busy_only` の日別件数だけを返す。予定名、本文、参加者、場所、URL、ICS原文は保存・表示しない。
- 課題タイトル・期限は管理ログイン後だけに表示し、公開トップや未認証レスポンスへ出さない。
- `command_center` スキーマの PostgREST 公開設定、実データ移行、移行用環境変数の投入は、セキュリティ境界の明示承認と接続情報の確認なしに実行しない。
- 顧客情報、認証情報、APIキー、移行トークンを Git、静的HTML、ログ、検証記録に含めない。
- 旧 Sites プロジェクトと `C:\Project\実行司令室` は、本番のデータ照合・復元可能なバックアップ・明示的な削除承認がそろうまで削除しない。

---

### Task 1: 移行済み要件・API・管理ページを AI相談ブランチへ取り込む

**Files:**

- Create: `docs/superpowers/specs/2026-08-08-execution-command-room-migration-design.md`
- Create: `docs/superpowers/plans/2026-08-08-execution-command-room-migration.md`
- Create: `api/_lib/command-center-*.ts`, `api/admin/command-center-*.ts`, `site/static/admin/command-center.*`
- Create: `supabase/migrations/20260808_command_center.sql`, `bridge/*`, `tests/command-center-*.test.mjs`
- Modify: `.env.example`, `.gitignore`, `api/_lib/auth.ts`, `site/static/admin/admin-menu.js`, `vercel.json`, `package.json`

**Interfaces:**

- Consumes: existing AI相談 `withAdmin` session and Vercel rewrites.
- Produces: `/admin/command-center` と7つの独立子画面、保護された管理API、移行設計・実行計画・設定見本。

- [ ] **Step 1: 依存順の移行コミットを取り込む**

  Run:

  ```powershell
  git cherry-pick 09cfce9 d89a60d 4480fe0 02aed6a b94a9b3 63e2ba5 630ccd1 57fe800
  ```

  Expected: すべての `.md` 要件、保護API、カレンダー、管理ページ、Codex bridge、環境設定例が同じブランチへ入り、秘密値は追加されない。

- [ ] **Step 2: 競合が起きた場合は最新 `origin/main` の既存機能を優先して解消する**

  `api/_lib/auth.ts`、`site/static/admin/admin-menu.js`、`vercel.json`、`package.json` の競合は、AI相談の現行ログイン・既存管理メニュー・既存rewriteを残しつつ、実行司令室だけの新規ルートを足す。旧Sites URL、公開API、サービス用共有トークンを復活させない。

- [ ] **Step 3: 取り込み直後の契約テストを実行する**

  Run:

  ```powershell
  node --test tests/command-center-contract.test.mjs tests/command-center-migration.test.mjs tests/command-center-api-contract.test.mjs tests/command-center-rendered-html.test.mjs
  ```

  Expected: 8画面、認証境界、`busy_only`、旧URL不在の契約がPASS。

### Task 2: 課題期限をカレンダーへ重ねる回帰テストと最小実装

**Files:**

- Create: `tests/command-center-calendar-deadline.test.mjs`
- Modify: `site/static/admin/command-center.js`

**Interfaces:**

- Consumes: `state.dashboard.tasks[]` の `dueDate`, `title`, `status` と、`/api/admin/command-center/calendar` の `{ privacy: "busy_only", days[] }`。
- Produces: 日別セルの Google予定件数と課題期限件数、課題期限の一覧。ICSの予定名は返さない。

- [ ] **Step 1: 課題期限を表示しない現在のカレンダーを再現する失敗テストを書く**

  `tests/command-center-calendar-deadline.test.mjs` は、保護された画面の実行スクリプトを読み、期限日が `state.dashboard.tasks` から日別に集計され、カレンダーのセルに「期限」として表示される利用者向け挙動を検査する。Google側には `busyCount` しか使わず、`SUMMARY`、`DESCRIPTION`、`ATTENDEE` を使わないことも検査する。

- [ ] **Step 2: 失敗することを確認する**

  Run:

  ```powershell
  node --test tests/command-center-calendar-deadline.test.mjs
  ```

  Expected: 現状の `renderCalendar` は `state.dashboard.tasks` を期限日別に描画しないためFAIL。

- [ ] **Step 3: `renderCalendar` に期限集計と表示を最小追加する**

  `dueDate` が選択範囲内で `status !== "done"` の課題だけを日別に集計する。各日セルは「予定なし / N件 忙しい」に加え「期限 N件」を表示し、カレンダー下部に日付・課題タイトル・状態の期限一覧を表示する。エスケープ処理を維持し、Google ICSからタイトル等を取得・描画しない。

- [ ] **Step 4: 回帰テストを再実行する**

  Run:

  ```powershell
  node --test tests/command-center-calendar-deadline.test.mjs
  ```

  Expected: PASS。期限表示を削除する変更、または ICSの詳細を描画する変更で失敗する。

### Task 3: ローカル統合・表示検証

**Files:**

- Test: `tests/command-center-*.test.mjs`
- Test: `vercel.json`, `site/static/admin/command-center.*`

**Interfaces:**

- Consumes: 管理画面HTML、Vercel rewrites、管理APIの認証ラッパー。
- Produces: ビルド可能な管理画面と、デスクトップ/iPhoneで読めるカレンダー表示。

- [ ] **Step 1: TypeScript、Node契約テスト、差分検査を実行する**

  Run:

  ```powershell
  npx.cmd tsc --noEmit -p tsconfig.json
  node --test tests/command-center-*.test.mjs
  git diff --check
  ```

  Expected: すべてPASS。既存の無関係なテスト失敗は別問題として分離する。

- [ ] **Step 2: Vercel build を実行する**

  Run:

  ```powershell
  npx.cmd vercel build
  ```

  Expected: rewrites と Functions が解決し、管理ページの静的資産を含む。

- [ ] **Step 3: 管理ログイン済みブラウザで確認する**

  Desktop と 390px 幅で `/admin/command-center/calendar` を開き、日別の忙しさ件数、課題期限件数、期限一覧、メニュー、横スクロール、エラー表示を確認する。未認証の同URLはログインへ遷移し、未認証APIは401であることを別途確認する。

### Task 4: 本番反映とデータ境界の報告

**Files:**

- Create: `docs/superpowers/verification/2026-08-09-command-center-production-check.md`

**Interfaces:**

- Consumes: 検証済みコミット、Vercel deployment、管理ログイン済みブラウザ。
- Produces: 本番URL・到達画面・認証結果・PC/iPhone表示結果を秘密値なしで記録する検証メモ。

- [ ] **Step 1: 関連ファイルのみをコミット・pushする**

  Run:

  ```powershell
  git add docs/superpowers api/_lib/command-center-* api/admin/command-center-* bridge supabase/migrations/20260808_command_center.sql site/static/admin/command-center.* site/static/admin/admin-menu.js site/static/admin/admin-common.css tests/command-center-* vercel.json package.json .env.example .gitignore
  git commit -m "feat: move command center into AI consultation admin"
  git push -u origin codex/command-center-migration-20260809
  ```

- [ ] **Step 2: Vercel preview と本番を同一コミットで確認する**

  `/admin/command-center/calendar`、`/api/admin/command-center/calendar`、`/api/admin/command-center/data` を確認し、管理ログイン後の画面・未認証の境界・PC/iPhone表示を記録する。

- [ ] **Step 3: 実データ移行とSupabase設定を分離して報告する**

  `command_center` のPostgREST公開設定やD1実データ移行を実行していない場合は、画面移行とデータ移行を混同せず、必要な明示承認・環境設定・照合手順を記録する。旧プロジェクトや旧フォルダは削除しない。

## Self-review checklist

- [ ] 移行設計 `.md`、実行計画 `.md`、環境設定例、ブリッジ設定例を AI相談に含めた。
- [ ] 8つの独立管理画面と、管理メニューからの導線を含めた。
- [ ] カレンダーが Google の予定詳細を漏らさず、予定件数と課題期限を表示する。
- [ ] DB/PostgREST のセキュリティ境界と実データ移行を、コード取り込み・画面公開と区別した。
- [ ] PC/iPhone、本番URL、管理ログイン、未認証APIを確認してから完了を報告する。

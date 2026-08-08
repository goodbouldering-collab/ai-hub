# 実行司令室からAI相談管理ページへの完全移行 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 実行司令室の課題・AI指示・実行履歴・Google予定件数・相場羅針盤・制作導線・PC上のCodex連携をAI相談の保護された独立管理ページへ移し、データ照合と本番確認後に旧Sitesプロジェクトとローカルフォルダを安全に削除する。

**Architecture:** AI相談側の既存 `withAdmin` 認証をすべての管理HTML/APIに適用し、管理API専用のSupabaseスキーマへ旧D1の永続6テーブルを冪等移行する。旧D1には一時的な読み取り専用エクスポートAPIだけを追加し、AI相談側の管理APIがサーバー間で取得して取り込む。CodexブリッジはAI相談側のAPIへHMAC接続し、旧Sitesリレーを参照しない。

**Tech Stack:** Vercel Functions (Node.js/TypeScript), 静的HTML/CSS/JavaScript管理画面, `@supabase/supabase-js` service-role server client, Supabase SQL migrations/RLS, Cloudflare D1旧API, Node.js test runner, Vercel CLI, Sites hosting connector.

## Global Constraints

- AI相談側の管理HTML/APIは既存 `withAdmin` を必ず通し、未認証HTMLはログインへ遷移、未認証APIは401を返す。
- 顧客情報、認証情報、APIキー、移行用トークンは公開ソース、静的HTML、Git履歴、ログへ含めない。
- D1の永続対象は `projects`, `tasks`, `directives`, `directive_executions`, `trades`, `trade_plans` とし、Codexブリッジのペアリング・nonce・待機リクエストは移行せず新環境で再生成する。
- Googleカレンダーは `busy_only` の日別件数だけを返し、予定名・本文・参加者・場所・URL・ICS原文を保存・表示しない。
- 市場データとAIプロバイダーのキーは環境変数だけで扱い、画面には接続状態のみを表示する。
- 既存のAI相談の顧客・認証系Supabaseテーブルには変更を加えず、管理API専用スキーマを作る。
- `/admin/status` を新しいメニューへ追加せず、`/admin/command-center` は管理導線と必要な操作の入口に限定する。
- 旧D1と旧フォルダはデータ照合・本番確認・復元用バックアップ・削除直前の対象確認が終わるまで削除しない。
- 旧プロジェクト削除操作がSitesで提供されない場合は停止またはアクセス無効化までとし、削除済みとは報告しない。

---

### Task 1: 移行作業の隔離と契約テストの骨格

**Files:**
- Create: `tests/command-center-contract.test.mjs`
- Create: `tests/command-center-migration.test.mjs`
- Create (旧実行司令室 worktree): `tests/command-center-export-contract.test.mjs`

**Interfaces:**
- Produces: 新管理ルート、移行スナップショット、認証ヘッダーの契約テスト。後続タスクはこのテストでルート名・JSON形状を固定する。

- [ ] **Step 1: 旧実行司令室を汚さない作業worktreeを作る**

  `C:\Project\実行司令室` の現在の未保存変更には触れず、現在のHEADから `C:\tmp\command-room-migration-source-20260808` を作る。AI相談は既存の `C:\tmp\ai-consult-admin-pages-all-20260805` を使う。

- [ ] **Step 2: 新管理ページのルート契約を失敗するテストとして追加する**

  `tests/command-center-contract.test.mjs` で次を検査する。

  ```js
  import test from "node:test";
  import assert from "node:assert/strict";
  import { readFile } from "node:fs/promises";

  test("command center routes are protected and independent", async () => {
    const vercel = JSON.parse(await readFile(new URL("../vercel.json", import.meta.url), "utf8"));
    const sources = vercel.rewrites.map((item) => item.source);
    for (const route of [
      "/admin/command-center",
      "/admin/command-center/calendar",
      "/admin/command-center/tasks",
      "/admin/command-center/businesses",
      "/admin/command-center/directives",
      "/admin/command-center/studio",
      "/admin/command-center/tools",
      "/admin/command-center/trade",
    ]) assert.ok(sources.includes(route), route);
    assert.equal(sources.includes("/admin/status"), false);
  });
  ```

- [ ] **Step 3: 旧エクスポートのJSON契約を失敗するテストとして追加する**

  旧側のテストは、スナップショットが `schemaVersion`, `generatedAt`, `source`, `tables` を持ち、6テーブルすべてが配列であること、認証ヘッダーがない場合に保護されることを固定する。

- [ ] **Step 4: 契約テストを実行して失敗を確認する**

  実行: `node --test tests/command-center-contract.test.mjs tests/command-center-migration.test.mjs`

  期待値: 新ルート・スナップショット実装がないためFAIL。失敗理由がルートやファイル欠落であることを確認する。

- [ ] **Step 5: 契約テストだけをコミットする**

  ```powershell
  git add tests/command-center-contract.test.mjs tests/command-center-migration.test.mjs tests/command-center-export-contract.test.mjs
  git commit -m "test: define command center migration contracts"
  ```

### Task 2: 旧D1の読み取り専用エクスポート

**Files:**
- Create (旧実行司令室): `app/api/_lib/migration-auth.ts`
- Create (旧実行司令室): `app/api/migration/export/route.ts`
- Modify (旧実行司令室): `lib/store.ts`
- Modify (旧実行司令室): `tests/command-center-export-contract.test.mjs`

**Interfaces:**
- Consumes: D1 binding `DB`, `COMMAND_CENTER_MIGRATION_TOKEN` environment variable, header `x-command-room-migration-token`.
- Produces: `GET /api/migration/export` JSON snapshot with all rows from six durable tables; no write endpoint and no public UI link.

- [ ] **Step 1: 認証ヘルパーの失敗テストを書く**

  `migration-auth.ts` の契約を次で固定する。

  ```ts
  export const MIGRATION_TOKEN_HEADER = "x-command-room-migration-token";
  export function requireMigrationToken(request: Request): Response | null;
  ```

  トークン未設定は503、ヘッダー欠落は401、不一致は403、成功時はnullを返す。比較は一定時間比較を使い、値をエラー本文へ含めない。

- [ ] **Step 2: D1スナップショット取得関数を追加する**

  `lib/store.ts` に次の戻り値を追加する。各テーブルは全列を取得し、並び順をIDまたは作成日時で固定する。

  ```ts
  export type CommandCenterSnapshot = {
    schemaVersion: 1;
    generatedAt: string;
    source: "execution-command-room-d1";
    tables: {
      projects: ProjectRow[];
      tasks: TaskRow[];
      directives: DirectiveRow[];
      directive_executions: ExecutionRow[];
      trades: TradeRow[];
      trade_plans: TradePlanRow[];
    };
  };

  export async function exportCommandCenterSnapshot(): Promise<CommandCenterSnapshot>;
  ```

  `directive_executions` は `owner_id` を含め、既存の画面用件数制限（20件、100件、30件）を使わない。

- [ ] **Step 3: 認証付きGETルートを実装する**

  `GET /api/migration/export` は `requireMigrationToken` が成功した場合だけD1を読み、`cache-control: no-store` と `content-type: application/json` を設定する。POST、PUT、DELETE、未認証GETは拒否する。

- [ ] **Step 4: 旧側の契約テストを通す**

  実行: `node --test tests/command-center-export-contract.test.mjs tests/service-auth.test.mjs`

  期待値: 認証境界、6テーブル、制限なしの全件取得、秘密値非表示がPASS。

- [ ] **Step 5: 旧側の変更をコミットする**

  ```powershell
  git add app/api/_lib/migration-auth.ts app/api/migration/export/route.ts lib/store.ts tests/command-center-export-contract.test.mjs
  git commit -m "feat: add protected command center export"
  ```

### Task 3: AI相談側の管理API専用Supabaseスキーマとリポジトリ

**Files:**
- Create: `supabase/migrations/20260808_command_center.sql`
- Create: `api/_lib/command-center-types.ts`
- Create: `api/_lib/command-center-db.ts`
- Create: `tests/command-center-db-contract.test.mjs`

**Interfaces:**
- Consumes: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` through existing `api/_lib/supa.ts`.
- Produces: typed functions `loadCommandCenter`, `updateCommandCenterTask`, `createCommandCenterTask`, `createCommandCenterDirective`, `recordCommandCenterExecution`, `createTradePlan`, `updateTradePlan`, `createTrade`, `closeTrade`, `deleteClosedTrade`, `upsertCommandCenterSnapshot`.

- [ ] **Step 1: Supabase migrationのセキュリティ契約をテストに書く**

  `command-center-db-contract.test.mjs` はSQLに `create schema command_center`, 各6テーブル、RLS有効化、公開ロールへのGRANTがないこと、サービスロールのみを想定するコメントがあることを検査する。

- [ ] **Step 2: 管理API専用スキーマを作る**

  `command_center` スキーマに以下を作る。IDと旧日時は保持し、`directive_executions.owner_id` と全取引系の `owner_id` を必須にする。

  ```sql
  create schema if not exists command_center;
  create table command_center.projects (... primary key ...);
  create table command_center.tasks (... primary key ...);
  create table command_center.directives (... primary key ...);
  create table command_center.directive_executions (... primary key ...);
  create table command_center.trades (... primary key ...);
  create table command_center.trade_plans (... primary key ...);
  ```

  実際の列は旧D1スナップショットの全列と一致させ、`created_at`, `updated_at` の索引を作る。スキーマはData APIへ公開せず、サービスロール接続だけを使用する。

- [ ] **Step 3: 型とDBリポジトリを実装する**

  旧スナップショットとAPIレスポンスの型を `command-center-types.ts` に集約する。`command-center-db.ts` はSQL文字列をAPIハンドラへ漏らさず、すべての更新関数で入力を型・長さ・許可値検査する。取得関数は画面用の `DashboardData` と移行照合用の全件スナップショットを分ける。

- [ ] **Step 4: スキーマとリポジトリの契約テストを通す**

  実行: `node --test tests/command-center-db-contract.test.mjs`

  期待値: SQLの6テーブル、RLS境界、全関数名、画面用件数制限と移行用全件取得の分離がPASS。

- [ ] **Step 5: SupabaseのDDLを適用し、アドバイザーを確認する**

  Supabaseの現在のプロジェクト参照をAI Hubの環境設定と照合した後、SQLを適用する。適用後にテーブル一覧、RLS、security advisor、performance advisorを確認し、公開ロールのアクセスがないことを記録する。既存の顧客・認証系テーブルへSQLを実行しない。

- [ ] **Step 6: 変更をコミットする**

  ```powershell
  git add supabase/migrations/20260808_command_center.sql api/_lib/command-center-types.ts api/_lib/command-center-db.ts tests/command-center-db-contract.test.mjs
  git commit -m "feat: add private command center storage"
  ```

### Task 4: AI相談側の保護API、カレンダー、市場、Codexリレー

**Files:**
- Create: `api/admin/command-center-data.ts`
- Create: `api/admin/command-center-calendar.ts`
- Create: `api/admin/command-center-market.ts`
- Create: `api/admin/command-center-brief.ts`
- Create: `api/admin/command-center-rankings.ts`
- Create: `api/admin/command-center-migrate.ts`
- Create: `api/admin/command-center-relay.ts`
- Create: `tests/command-center-api-contract.test.mjs`
- Modify: `api/_lib/auth.ts`

**Interfaces:**
- Consumes: `withAdmin`, `command-center-db.ts`, `COMMAND_CENTER_MIGRATION_TOKEN`, `COMMAND_ROOM_MIGRATION_URL`, `GOOGLE_CALENDAR_ICS_URL`, existing AI/market environment variables.
- Produces: `/api/admin/command-center/data`, `/calendar`, `/market`, `/brief`, `/rankings`, `/migrate`, `/relay`.

- [ ] **Step 1: 管理APIの未認証契約をテストに追加する**

  `command-center-api-contract.test.mjs` は各APIソースが `withAdmin` または同等のHMACリレー検証を呼ぶこと、公開の旧 `/api/dashboard` を新UIから呼ばないこと、応答ヘッダーに `cache-control: no-store` を含めることを検査する。

- [ ] **Step 2: データAPIを実装する**

  `command-center-data.ts` はGETで画面用データを返し、POSTで次の action だけを許可する。

  ```ts
  type CommandCenterAction =
    | "update_task" | "create_task" | "create_directive"
    | "record_execution" | "create_trade" | "create_trade_plan"
    | "approve_trade_plan" | "cancel_trade_plan"
    | "execute_trade_plan" | "close_trade" | "delete_trade";
  ```

  既存の旧D1アクションと同じ許可値・文字数上限・日付検査を再利用し、未知actionは400で拒否する。更新後は最新の画面用データだけを返す。

- [ ] **Step 3: カレンダーAPIを実装する**

  `command-center-calendar.ts` は `from` と `to` をISO日付として検査し、62日以内に制限する。ICSをサーバー側で解析して日別件数へ変換し、レスポンスに `privacy: "busy_only"` を含める。イベントオブジェクト、タイトル、参加者、本文を返さない。

- [ ] **Step 4: 市場・AI APIを管理境界へ移す**

  `command-center-market.ts`, `command-center-brief.ts`, `command-center-rankings.ts` は既存処理を管理ログイン下へ移し、APIキーの値を返さない。プロバイダー失敗時は利用可能状態と安全な短いエラーコードだけを返す。

- [ ] **Step 5: 一回限りの移行APIを実装する**

  `command-center-migrate.ts` は管理ログイン必須で、サーバー側の `COMMAND_ROOM_MIGRATION_URL` と `COMMAND_CENTER_MIGRATION_TOKEN` を使用して旧エクスポートを取得する。受信したスナップショットのschemaVersion、テーブル名、必須列、ID重複、正規化ハッシュを検査し、差分がある場合は書き込まずエラーにする。成功時は冪等upsertと件数・ハッシュ結果だけを返し、行データをレスポンスやログへ出さない。実行済みフラグを管理API専用テーブルに記録し、2回目以降は明示的な再照合だけを許可する。

- [ ] **Step 6: Codexリレーを移す**

  `command-center-relay.ts` はブラウザ操作を `withAdmin` で保護し、PCブリッジのheartbeat/completeだけをHMAC、timestamp、nonceで受ける。旧リレーのパスやOriginを許可せず、要求のmethod/pathを明示的allowlistで検査する。一時リレー状態は新Supabase領域に保存し、期限切れ行を削除する。

- [ ] **Step 7: API契約テストを通す**

  実行: `node --test tests/command-center-api-contract.test.mjs tests/service-auth.test.mjs tests/google-calendar-contract.test.mjs`

  期待値: 認証、action検査、busy-only、秘密値非表示、移行差分停止、HMAC nonce再利用拒否がPASS。

- [ ] **Step 8: 変更をコミットする**

  ```powershell
  git add api/admin/command-center-*.ts api/_lib/auth.ts tests/command-center-api-contract.test.mjs
  git commit -m "feat: add protected command center APIs"
  ```

### Task 5: 独立管理ページ、メニュー、レスポンシブ表示

**Files:**
- Create: `site/static/admin/command-center.html`
- Create: `site/static/admin/command-center.css`
- Create: `site/static/admin/command-center.js`
- Modify: `site/static/admin/admin-menu.js`
- Modify: `site/static/admin/admin-common.css`
- Modify: `vercel.json`
- Create: `tests/command-center-rendered-html.test.mjs`

**Interfaces:**
- Consumes: `/api/admin/command-center/*` and `data-view` route parameter.
- Produces: 8 independent protected URLs with shared visual shell, keyboard操作、横スクロール可能な表、モバイルメニュー。

- [ ] **Step 1: HTMLの表示契約テストを追加する**

  `command-center-rendered-html.test.mjs` はHTMLに管理ログイン、ページ見出し、カレンダー、課題、AI指示、制作、取引、Codex接続の入口があること、顧客情報・token文字列・古いSites URLがないことを検査する。

- [ ] **Step 2: HTML/CSSの共有シェルを作る**

  `command-center.html` は `data-view` に応じてページ見出しと本文を切り替える。各画面の操作は同じHTMLを複製せず、ページ固有のsectionを1つだけ表示する。表は狭い画面で親要素を横スクロールできるようにし、フォーカスリング、aria-label、エラー・空状態を含める。

- [ ] **Step 3: JavaScriptで管理APIを接続する**

  `command-center.js` は相対URLのfetchだけを使い、未認証の303/401をログインへ引き渡す。GETの結果は画面状態へ描画し、POST後は再取得する。Codex接続はペアリングコードを画面へ表示するだけで、cookieや秘密値をlocalStorageへ保存しない。

- [ ] **Step 4: 管理メニューへ独立リンクを追加する**

  `admin-menu.js` の管理グループに「実行司令室」を追加し、8ルートをモバイルメニューからも選択できるようにする。`/admin/status` と旧Sites URLは追加しない。

- [ ] **Step 5: Vercel rewriteを追加する**

  `/admin/command-center`, `/admin/command-center/:view` と各APIを、それぞれ保護されたFunctionへrewriteする。`functions.includeFiles` に静的HTML/CSS/JSが含まれることを確認する。

- [ ] **Step 6: HTML・メニュー・レスポンシブ契約を通す**

  実行: `node --test tests/command-center-rendered-html.test.mjs tests/admin-navigation.test.mjs`

  期待値: 8ルート、メニュー表示、古いURL不在、モバイルメニューの横幅制約がPASS。

- [ ] **Step 7: 変更をコミットする**

  ```powershell
  git add site/static/admin/command-center.html site/static/admin/command-center.css site/static/admin/command-center.js site/static/admin/admin-menu.js site/static/admin/admin-common.css vercel.json tests/command-center-rendered-html.test.mjs
  git commit -m "feat: add independent command center admin pages"
  ```

### Task 6: PC上のCodexブリッジをAI相談側へ移す

**Files:**
- Create: `app-server/bridge.mjs`
- Create: `app-server/contracts.mjs`
- Create: `app-server/README.md`
- Create: `app-server/projects.example.json`
- Modify: `.gitignore`
- Modify: `app-server/bridge.mjs`
- Create: `tests/command-center-bridge-contract.test.mjs`

**Interfaces:**
- Consumes: `COMMAND_ROOM_BRIDGE_AUTH_SECRET`, `COMMAND_ROOM_OWNER_EMAIL`, `COMMAND_ROOM_PROJECTS_ROOT`, `COMMAND_ROOM_BRIDGE_PORT`, `CODEX_COMMAND` from local environment.
- Produces: local bridge that sends signed requests only to AI相談 `/api/admin/command-center/relay` and does not load protected tokens into Codex child processes.

- [ ] **Step 1: ブリッジ契約テストを失敗する状態で追加する**

  旧Origin、旧relay path、`COMMAND_CENTER_SERVICE_TOKEN` の子プロセス引き渡しがないこと、AI相談relay pathが設定可能であることを検査する。

- [ ] **Step 2: ブリッジコードを移し、秘密設定をローカル専用にする**

  `bridge.mjs` の固定Originを環境変数またはAI相談の既定値へ変更する。実データを含む `businesses.json`, `projects.local.json`, `.local/*` はコピーせず、`projects.example.json` と `.gitignore` だけをGitへ置く。ローカル実行時に実設定がない場合は、許可プロジェクトなしで安全に停止する。

- [ ] **Step 3: Codex子プロセスの環境境界を確認する**

  `COMMAND_ROOM_BRIDGE_AUTH_SECRET`, `COMMAND_CENTER_SERVICE_TOKEN`, 移行トークンを子プロセス環境から削除し、テストで継承されないことを確認する。

- [ ] **Step 4: ブリッジのスモークテストを通す**

  実行: `npm.cmd run bridge:smoke`、`npm.cmd run bridge:auto-smoke`、`node --test tests/command-center-bridge-contract.test.mjs app-server/bridge.test.mjs`

  期待値: HMAC、Origin、ペアリング、実行、承認、割り込み、完了応答がPASS。

- [ ] **Step 5: 変更をコミットする**

  ```powershell
  git add app-server .gitignore tests/command-center-bridge-contract.test.mjs
  git commit -m "feat: move codex bridge to ai hub"
  ```

### Task 7: 移行用環境設定、D1からSupabaseへの実データ移行

**Files:**
- Modify (Sites環境): `COMMAND_CENTER_MIGRATION_TOKEN`
- Modify (Vercel環境): `COMMAND_ROOM_MIGRATION_URL`, `COMMAND_CENTER_MIGRATION_TOKEN`
- Create: `docs/superpowers/verification/2026-08-08-command-center-migration-record.md`

**Interfaces:**
- Consumes: 旧エクスポートAPI、新移行API、管理ログイン済みAI相談環境。
- Produces: 件数・ID・ハッシュの照合記録と、秘密値を含まない移行結果。

- [ ] **Step 1: 移行トークンを生成する**

  1回だけランダム値を生成し、SitesとVercelの環境変数へ直接設定する。値をファイル、コマンド履歴、Git、画面、チャットへ保存しない。既存のサービストークンを読み出したり表示したりしない。

- [ ] **Step 2: 旧エクスポートをデプロイして到達性を確認する**

  旧側の検証済みコミットをSitesへ保存・デプロイする。`GET /api/migration/export` は未認証で401/503、正しいサーバー間呼び出しで200となることだけを確認し、本文をログ出力しない。

- [ ] **Step 3: AI相談側の管理APIをデプロイする**

  Supabase migration適用後のAI相談ブランチをVercel previewへデプロイし、管理ログイン経由で移行APIへ到達できることを確認する。

- [ ] **Step 4: 一回限りの実データ移行を実行する**

  管理ログイン済みのAI相談画面から移行APIを実行する。結果はテーブル件数、ID集合の一致、正規化ハッシュ、一時テーブルを移行しなかったことだけを記録する。差分が出た場合はデータを書き込まず停止する。

- [ ] **Step 5: 移行APIを再実行不可または無効化する**

  検証完了後に移行用環境変数を削除し、移行APIを管理ログインでも再実行できない状態にする。旧エクスポートAPIも同時に無効化する。

- [ ] **Step 6: 移行記録をコミットする**

  `docs/superpowers/verification/2026-08-08-command-center-migration-record.md` には日時、環境、テーブルごとの件数、照合結果、API無効化結果だけを書き、行データ・秘密値・tokenは書かない。

  ```powershell
  git add docs/superpowers/verification/2026-08-08-command-center-migration-record.md
  git commit -m "docs: record command center data migration"
  ```

### Task 8: 完全検証、Vercel本番反映、Codex経路確認

**Files:**
- Modify: `tests/command-center-contract.test.mjs`
- Modify: `tests/command-center-migration.test.mjs`
- Create: `docs/superpowers/verification/2026-08-08-command-center-production-check.md`

**Interfaces:**
- Consumes: AI相談 preview、本番URL、移行記録、管理ログイン済みブラウザ、ローカルCodexブリッジ。
- Produces: 本番到達性、認証境界、レスポンシブ表示、API、Codex連携の検証記録。

- [ ] **Step 1: AI相談の静的・型・契約検証を実行する**

  実行: `npx.cmd tsc --noEmit`、`node --test tests/*.test.mjs`、`git diff --check`。既存の `npm.cmd test` にtest scriptがない場合は既存設定を変更せず、実行結果を記録する。

- [ ] **Step 2: Vercel previewをビルドする**

  `vercel build` またはリモートLinuxビルドで生成物を確認する。Windows symlink権限によるローカル失敗は、リモートビルド成功をもって代替し、原因を記録する。

- [ ] **Step 3: 管理ログイン前のHTTP契約を確認する**

  `/admin/command-center` と8独立URLが303でログインへ遷移し、各APIが401を返すことを確認する。公開トップページから管理データが出ないことを確認する。

- [ ] **Step 4: 管理ログイン後のブラウザ検証を行う**

  390px幅とデスクトップ幅でメニュー、カレンダー、課題、AI指示、制作、取引、Codex接続を確認する。横溢れ、コンソールエラー、秘密値の表示がないことを確認する。

- [ ] **Step 5: Vercel本番へデプロイする**

  検証済みでコミット・push済みの同一コミットをVercel本番へ反映し、デプロイID、URL、主要HTML/APIのステータスを記録する。

- [ ] **Step 6: 本番APIを検証する**

  未認証の管理URL/API、認証後の全管理API、Googleカレンダーの `busy_only`、市場データ、Codexリレーのレスポンスを確認する。旧Sites URLへの外向き参照がないことを再検索する。

- [ ] **Step 7: 本番検証記録をコミットする**

  本番URL、検証日時、HTTP結果、ブラウザ幅、データ照合結果、旧URL依存なしの結果だけを記録する。顧客情報、認証情報、行データは記録しない。

### Task 9: 旧環境の停止、最終バックアップ、削除

**Files:**
- Create outside both deletion targets: `command-room-migration-backup-20260808` archive
- Create: `docs/superpowers/verification/2026-08-08-command-center-deletion-record.md`

**Interfaces:**
- Consumes: 本番検証記録、データ移行記録、旧Sites project metadata、旧ローカルフォルダの絶対パス。
- Produces: 復元用バックアップ、旧Sites停止/削除結果、ローカル削除結果。削除対象以外には触れない。

- [ ] **Step 1: 旧側の新規書き込みを停止する**

  旧D1 APIとCodexリレーを無効化し、旧公開URLが管理データを返さないことを確認する。旧URLはAI相談の管理ログインへ案内するだけにする。

- [ ] **Step 2: 最終バックアップを作る**

  旧ソースのコミット、未保存変更のパッチ、D1スナップショット、移行記録を旧フォルダ外の保護領域へ保存する。秘密値は除外し、バックアップに含まれるファイル一覧とSHA-256を記録する。

- [ ] **Step 3: 削除対象を再解決する**

  Sites project IDが `appgprj_6a55fc699ca08191af60b3d6490a9233`、ローカル絶対パスが `C:\Project\実行司令室` であることを再確認する。別のプロジェクト、親フォルダ、AI相談フォルダを削除対象にしない。

- [ ] **Step 4: Sitesプロジェクトを削除または停止する**

  Sitesで削除操作が提供されていれば対象IDだけを削除する。提供されていなければアクセス無効化または停止までに留め、削除済みと記録しない。

- [ ] **Step 5: ローカルフォルダを削除する**

  バックアップの存在とパス検査が成功した後、`Remove-Item -LiteralPath 'C:\Project\実行司令室' -Recurse -Force` を一度だけ実行する。完了後にパスが存在しないことを確認し、親の `C:\Project` やAI相談フォルダに触れない。

- [ ] **Step 6: 削除結果を記録する**

  削除記録には対象ID、対象絶対パス、実行日時、Sitesの結果、バックアップ参照、ローカルパス不存在確認だけを書く。復元可能性と、Sites操作が停止に留まった場合の状態を明記する。

## Self-review checklist

- [ ] 6つの永続テーブル、busy-only、market/AI、Codex、独立ページ、認証、レスポンシブ、本番確認、バックアップ、Sites/ローカル削除をすべてタスクへ割り当てた。
- [ ] 未確定のplaceholder語、抽象的な実装指示、具体性のないテスト指示を計画本文に残していない。
- [ ] Task 3の `command-center-db.ts` 関数名とTask 4のAPI呼び出し名を一致させた。
- [ ] 移行用APIは旧側の全件取得と新側の冪等取り込みを分離し、差分時に書き込まない。
- [ ] 旧プロジェクト・旧フォルダの削除は最後の独立タスクであり、未検証の削除を許可していない。

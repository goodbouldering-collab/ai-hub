# Supabase補助経路の監査（2026-10-11）

現在のaiclimb WorkerにSupabaseへの実接続は検出されなかった。ただし、収集履歴3件と指令室9表30件が旧Supabaseに残っており、事業全体の移行完了ではない。

## 現行Worker

- 台帳の公開元は `work/genspark-profile-edit/cloudflare-runtime`、設定は `wrangler-profile-release.jsonc`、実配信モジュールは `../deployment/admin-workspace/published-worker.mjs`。
- 正本モジュール: 4,181,534 bytes、SHA256 `6573af7470b8e4b8fc6a887c47b5fd5dd8c8b82c5aaebfb839428922b4e6fade`。本番APIから得たmultipart全体のハッシュとは比較しない。実moduleの照合は全事業監査で扱う。
- `supabase` の477件は、管理資料の文字列465件と、管理HTML6画面の状態表示 `flag("Supabase", env.hasSupabase)` 各2件。サーバ実行コード内0件、Supabase project URL形式0件、JWT形式0件、Supabaseを読む外部scriptタグ0件。
- import経路は admin-workspace → my-workflows → ai-news の既存Worker。旧 `api/_lib/{supa,storage,supabase-portal,command-center-db}.ts` は、この配備モジュールへ取り込まれていない。
- `/api/content-studio/*` は既存管理認証後、許可済み経路だけをCloudflareの `business-content-app-server` へ中継。キー保存は暗号化Cookie。今回、その先のWorker実装全体は監査対象外。
- 指令室の共有保存・同期、SNS投稿・履歴、AIチャット等は `pendingApi` で認証後503。画面移行とAPI移行は別状態。

## 残るデータと到達条件

| 対象 | 件数 | 現行経路 | 次の作業 |
|---|---:|---|---|
| `ai_watch.articles` | 3行 | `core/differ.py` はURLとservice role環境変数の両方がある時だけSupabase。標準daily workflowに設定なし、通常はSQLite | D1保存先・履歴移行・重複判定を実装し、旧3件との照合後に切替 |
| `command_center` | 9表30行 | 旧APIのみ。現行Workerの対象APIは接続待ち | 共有保存用D1 target/bindingと認証境界を確定し、9表をmigration管理 |
| `portal.sns_posts` | 両Supabase projectで表未検出 | 旧コードのみ、現行SNS APIは接続待ち | 利用開始前にD1実装。表未検出を「履歴0件」とは同一視しない |
| 旧画像Storage API | 1補助モジュール | 現行画像コードは `ARTICLE_IMAGES`/公開URL待ち。台帳targetにR2 bindingなし | 公開画像のR2/URLを台帳へ登録してから切替 |

指令室の内訳: projects 15、tasks 8、directives 5、directive_executions 2、relay_nonces/relay_requests/relay_state/trade_plans/trades 各0。件数だけをSELECTし、行本文・秘密値は取得していない。確認先は既存b21 project。もう一方の共有projectでは上記3スキーマの表を検出しなかった。

`ai-hub-public` 内の画像6件はすべて `colorme-groups` 配下で、グッぼる告知スクリプトの対象。AI相談と二重集計しない。詳細はグッぼるの同日監査を参照。

今回、既存DB、Storage、認証、DNS、SNS、本番Workerは変更していない。ローカルSQLiteへの保存をCloudflare移行完了とは扱わない。機械集計は [JSON](supabase-aux-audit-20261011.json)。

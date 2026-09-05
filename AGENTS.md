<!-- browser-account-policy:v1 -->
ブラウザ作業前は、必ず[事業別ブラウザの共通ルール](C:/Project/docs/browser-account-policy.md)を適用する（閲覧・検証・投稿を含む）。
<!-- /browser-account-policy:v1 -->

# AGENTS.md — AI相談

## Cloudflareデプロイ境界（最優先）

- GitHubからの本番デプロイ先はCloudflareのみ。Vercelへ再接続・deploy・自動deployしない。
- 公開先の唯一の正本は中央台帳 `C:\Project\docs\cloudflare-targets.json`。`.github/deployment-platform.json` はGitHub側の対応表として台帳と照合する。`partial_migration` の残作業はActionsの警告を解消してから完了扱いにする。
- 既存Vercelプロジェクトは移管確認用の読取専用。削除、DNS、認証・個人情報の移管は別途承認を得る。

**AI相談** は「自分のAIをひとつに集める場所」をテーマにした個人ポートフォリオ兼マイページ。
作品（アプリ集）・講師紹介・受講資料を見せる**フロント面**と、AI/SNS関連情報をRSSから自動収集・要約してNotebookLMに流し込む**バックエンドのパイプライン**を1つのサイトに同居させている。

## リポジトリ名の正規化

- プロジェクト名: **AI相談**（旧称: AIハブ / AI Hub、 AI-watch、AI情報収集、cclimb-intel、ai-info）
- GitHub: `goodbouldering-collab/ai-hub`
- **本番ホスティング正本**: **Cloudflare Workers**。管理画面・APIのVercel残存部分は移管中として警告し、新規変更・再デプロイはしない
- **本番URL**: https://aiclimb.aiclimb.workers.dev
- Vercel Project ID: `prj_e7vh73eF0KZpm8C49esnILvHO98o`
- GitHub Pages: `https://goodbouldering-collab.github.io/ai-hub/`（参考・残置）
- Supabase: 既存の共有プロジェクト `zrawhzwtppmlxyhngnju` の `ai_watch.*` スキーマ（旧 `public.ai_watch_*` から移管。テーブル名は履歴互換のため維持。なお `zrawhzwtppmlxyhngnju.ai_watch` は Vercel 移行後ほぼ未使用、次回掃除候補）

新規で文言を書くときは「AI相談」に揃える。過去ログ（`outputs/notebooklm/*`）と Supabase テーブル名は改名しない（NotebookLM 側のソース参照と既存データ互換のため）。

## ディレクトリ

| パス | 役割 |
|---|---|
| `run.py` | エントリーポイント。収集→要約→出力→サイト生成まで一気通貫 |
| `core/` | 収集・差分・要約・ランキング・サムネ・書き出し |
| `config/sources.yaml` | 収集対象 RSS。追加するだけで増やせる |
| `config/genres.yaml` | ジャンル（AI業務活用 / SNSアルゴリズム 等）の定義 |
| `config/support_sns.yaml` | サポートSNSアカウントリスト |
| `config/portfolio.yaml` | トップに並べる作品カードの定義 |
| `config/top_buttons.yaml` | トップ上部のクイックリンクボタン |
| `site/build_site.py` | `outputs/top10.json` から静的 HTML を生成 |
| `site/dist/` | サイト生成物。公開用の正本・配置先は中央台帳のworkingDirectoryに従う |
| `outputs/notebooklm/` | NotebookLM 用 Markdown/TXT（日次） |
| `outputs/full/` | 週次フル版 TXT |
| `data/history.db` | SQLite の既取得ログ（差分検出の土台） |
| `admin/server.py` | FastAPI 管理画面（ローカル 3010）。Shopify Admin API 操作タブも内蔵 |
| `core/shopify_admin.py` | Shopify Admin REST クライアント。`.env` の `SHOPIFY_ACCESS_TOKEN` / `SHOPIFY_STORE_DOMAIN` を読む |
| `scripts/migrate_sqlite_to_supabase.py` | SQLite → Supabase へのマイグレーション |
| `content/speaker.md` | 講師紹介（由井辰美）の編集ソース。ビルドで `speaker.html` になる |
| `content/lectures/*.md` | 受講資料の編集ソース。ビルドで `lectures/<slug>.html` になる |
| `content/assets/` | 画像・PDF。`./assets/xxx` で参照 |

## デプロイ構成（**Cloudflare公開 + Vercel動的処理**）

- **GitHub Actions `daily.yml`**: JST 07:00 に `run.py` を実行し、`outputs/` と `data/history.db` を main に commit back
- **GitHub Actions `pages.yml`**: `main` への push で `site/build_site.py` を叩いて GitHub Pages に配布（参考・残置）
- **Cloudflare Workers**（**公開正本**）: 中央台帳のworkingDirectoryにあるStatic Assetsを配信。旧ルートの `site/dist/` やWorker設定から公開元を推測しない
  - 本番 URL: https://aiclimb.aiclimb.workers.dev
- **Vercel**（**管理画面・API・決済の移管元**）: 読取専用。旧 `main` push / PR連携による自動デプロイを起こす操作は禁止
  - 動的処理 URL: https://aiclimb.vercel.app
  - Project ID: `prj_e7vh73eF0KZpm8C49esnILvHO98o`
- **Supabase**: `ai_watch_articles` テーブルに差分保存（`SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` が env にあれば書き込む）

### 撤収済み

| プラットフォーム | 状態 | 備考 |
|---|---|---|
| ~~Render Static Site (`ai-hub`)~~ | 撤収済 | Vercel 集約に伴い廃止 |
| ~~Cloudflare Worker `ai-hub`~~ | 撤収済（2026-05-05） | `wrangler delete --name ai-hub` 実行済。`wrangler.toml` / `cloudflare-pages.yml` も削除済 |
| Cloudflare Worker `aiclimb` | 公開正本 | 公開静的ファイルを配信。管理画面・API・大容量動画は認証情報を中継せずVercelへ直接移動。URLは `https://aiclimb.aiclimb.workers.dev` |
| GitHub Pages (`goodbouldering-collab.github.io/ai-hub/`) | 残置 | 参考用 |

## コマンド

```bash
python run.py                 # 日次ダイジェスト (直近24h の diff モード)
python run.py --full          # 週次フル版も生成
python run.py --no-summary    # Codex API をスキップ
python site/build_site.py     # サイトだけ再ビルド
uvicorn admin.server:app --port 3010 --reload   # 管理画面
```

VSCode で `clients.code-workspace` を開けば「AI相談起動」タスクで `http://localhost:3010/admin` が立ち上がる。

## 守るべきルール

- ソース追加は `config/sources.yaml` に 1 ブロック足すだけ。コードは触らない
- 実績サイトは `config/portfolio.yaml` が正本。公開直後は `portfolio-sync.yml` を実行し、手作業で重複カードを増やさない
- RSS 以外（X API・スクレイピング等）を増やすときは `core/collector.py` の `DISPATCH` に関数を追加する
- 日付入りの出力ファイルは上書きしない（NotebookLM 側がソースとして保持しているため）
- `data/history.db` は commit back される前提。`.gitignore` で除外しない
- 文字化け防止: グッぼる本店など EUC-JP ソースを HTML で取り込む場合は親 `AGENTS.md` のルールに従って `iconv` 変換層を挟む
- Supabase テーブル名 `ai_watch_*` は**改名しない**（旧名のまま運用継続）

## 実績サイト自動同期

以下のフックはCloudflareだけへ反映する経路と中央台帳の検証が確認できた場合に実行する。`portfolio-sync.yml` やcommit backがVercel自動デプロイを起こす間は起動せず、入力資料の準備までに留める。

- 全事業の本番公開完了フックは `.github/workflows/portfolio-sync.yml` へ確認済みURLとサイト情報を渡し、AI相談トップの「すべての実績」へURLとサイト画面付きで同期する。
- workflowは起動のたびに公開中の全URLを撮影して `site/static/img/portfolio/` へ保存し、カードは保存済みの最新スクリーンショットを使う。外部MShots画像へ戻さない。
- 同名・同slug・同URL・同Vercel project IDは既存カードを更新し、旧URLを `aliases` に残す。重複カードは作らない。
- 管理API、社内資料、契約上非公開など掲載禁止のものだけ `config/portfolio-sync.yaml` に `include: false` と理由を書く。その他の完成・公開サイトは掲載対象とする。
- サイトを本番公開してURL確認が済んだ時点で、ホスティング先に関係なくworkflow inputsへ `name` / `url` / `slug` / `category` / `tech` / `summary` を渡して実行する。入力なしで終わらせない。
- 日次処理は台帳・画像出力・重複を再検証する。Vercel全体の自動探索は、管理者がGitHub Actionsへ `VERCEL_TOKEN` を明示設定した場合だけ補助的に動かし、ローカル認証を自動移送しない。
- 詳しい運用とコマンドは `docs/portfolio-auto-sync.md` を参照する。

## デザイン更新の共通ルール

- 固定メニューは基本的に2種類だけにする: 公開トップ用メニューと管理画面用メニュー。新しい管理ページを増やすときも、管理画面用の共通ヘッダーと共通CSSを使い回す。
- ブラウザの `<title>` は公開トップと管理画面で同じ文字列にそろえる。個別ページ名を増やしたい場合も、まず共通タイトルの方針を崩さない。
- CSSは個別ページへ足す前に、`site/build_portal.py` の公開トップ用CSSと `site/static/admin/admin-common.css` の管理画面共通CSSで共有できるか確認する。
- 色数は増やしすぎない。背景色、メニュー背景、文字色、CTA色は明示的な組み合わせで定義し、白背景に白文字などの低コントラストを出さない。
- デザイン変更後は必ずPC幅とiPhone幅で固定メニュー、ハンバーガーメニュー、管理メニューの背景色と文字色を確認する。見た目の整合性と読みやすさを優先する。

## 管理画面について

AI相談には**2系統の管理画面**がある:

### 1. ローカル管理画面 (`admin/server.py`)

FastAPI ベースの**ローカル専用** UI。記事収集ジョブの状態確認・受講資料の編集・Shopify Admin 操作などに使う。
ローカルで `uvicorn admin.server:app --port 3010 --reload` で起動 → `http://localhost:3010/admin`。
運用（記事収集）は GitHub Actions 任せで、ここは手元確認用。

### 2. クラウド管理画面（Vercel移管元の認証構成）

**パスワードログイン付きの Web 管理画面** (Vercel Serverless Functions + 静的 HTML)。
グッぼる（カラーミー）のグループ追加・AI記事生成・トップページ最上部への記事公開を担う。

- URL: https://aiclimb.vercel.app/admin
- 認証: パスワードのみの管理ログイン (`ADMIN_PASS` を Vercel env)
- API:
  - `/api/admin/ping` 接続/環境変数チェック
  - `/api/admin/generate-articles` Codex で複数案生成
  - `/api/admin/revise-article` 既存案を AI で修正
  - `/api/admin/generate-image` DALL-E 3 で画像生成 → Supabase Storage アップロード
  - `/api/admin/groups` カラーミー `/v1/groups` の GET / POST / PUT
  - `/api/admin/publish-article` テンプレ `index.html` のマーカーに記事差し込み
  - `/api/admin/unpublish-article` ブロック削除 + display_state=hidden

#### テンプレ書き換え方式（PC用フリースペース 1/2 の代替）

カラーミー API は「PC用フリースペース 1/2」を直接編集できない。代わりに
カラーミーテンプレ `index.html` (page_type=index) を `PUT /v1/templates/{id}/pages/index` で
書き換え、そのなかに以下のマーカーで AI 制御範囲を明示する:

```html
<!-- BEGIN:AI_GROUP_ARTICLES -->
<!-- BEGIN:AI_GROUP_ARTICLE_<group_id> -->
<section class="ai-group-article" data-published="2026-05-06">
  <h2>...グループ名...</h2>
  <p class="ai-group-article__date"><small>2026-05-06 公開</small></p>
  ...本文HTML...
</section>
<!-- END:AI_GROUP_ARTICLE_<group_id> -->
<!-- END:AI_GROUP_ARTICLES -->
```

- マーカー範囲外は絶対に触らない（手動編集との衝突防止）
- 公開フローは **テンプレ 1086 に直接反映**（2026-05-07 から）
  - 当初は 1086 → 1064 の二段階を想定していたが、OAuth アプリ `ai-hub-admin`
    が 1064 にアクセスできないため、1086 を本番テンプレとして適用する運用に変更
  - 1086 / 1064 のデザインは 2026-04-16 時点で同期済み
  - カラーミー管理画面 → ショップ作成 → テンプレートで「**1086 を適用**」する手順を必ず実施
- グループ作成時 display_state は `hidden`、本番反映時に `showing` に切り替える

#### 移管元の環境変数名（値の取得・変更・移送は明示承認が必要）

| Env | 役割 |
|---|---|
| `ADMIN_PASS` | 管理ログイン用パスワード |
| `ADMIN_SESSION_SECRET` | 管理ログインCookie署名用。未設定時は `ADMIN_PASS` を使用 |
| `COLORME_ACCESS_TOKEN` | グッぼる本店操作用 OAuth トークン |
| `COLORME_PREVIEW_TEMPLATE_ID` | 既定 1086 |
| `COLORME_LIVE_TEMPLATE_ID` | 既定 1064 |
| `ANTHROPIC_API_KEY` | 記事案生成 |
| `OPENAI_API_KEY` | DALL-E 3 画像生成 |
| `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` | 画像アップロード先 |
| `SUPABASE_BUCKET` | 既定 `ai-hub-public` (public=true で作成済) |

### 受講資料タブ

`/admin` の「📝 受講資料」タブで `content/lectures/*.md` を一覧・新規作成・編集・削除できる。

**操作**:
- 左カラム: 既存資料一覧（日付の新しい順）
- 右カラム: frontmatter (title/date/role/gen_by/summary) と Markdown 本文のエディタ
- **slug** はファイル名（例: `2026-04-ai-kihon`）。小文字英数とハイフンのみ
- 「💾 保存して再ビルド」で `/lectures/<slug>.html` に即反映
- 受講プランと関係する資料を追加・改名するときは、受講プランカードから該当する受講資料へ、受講資料側から受講プランへ戻れる導線を同時に更新する

**追加機能**:
- **Markdownライブプレビュー**（右半分に即時描画、入力から400ms後に更新）
- **画像/PDFアップロード** → `content/assets/` に保存して本文の現在カーソル位置に Markdown を自動挿入。許容拡張子: png/jpg/jpeg/gif/webp/svg/pdf、最大10MB、同名は連番で自動回避
- **複製して新規** ボタン: 現在の編集内容をテンプレに新規モード化（slugだけ空に）

**API**:
- `GET /api/lectures` 一覧
- `GET /api/lectures/{slug}` 取得
- `POST /api/lectures` 新規（同名があれば 409）
- `PUT /api/lectures/{slug}` 更新
- `DELETE /api/lectures/{slug}` 削除
- `POST /api/lectures/preview` Markdown→HTML プレビュー
- `GET /api/assets` アセット一覧
- `POST /api/assets` アセットアップロード (multipart)
- `DELETE /api/assets/{name}` アセット削除

### Shopify Admin タブ

`/admin` の「🛒 Shopify」タブで、`.env` に登録した Shopify ストアを直接操作できる。

**前提**: `.env` に以下を設定（`.env.example` 参照）。
```
SHOPIFY_ACCESS_TOKEN=shpat_...
SHOPIFY_STORE_DOMAIN=84c617.myshopify.com
```

**機能**:
- 接続確認（ストア名・通貨・プラン表示）
- 商品一覧（タイトル絞り込み・在庫数つき）
- 注文一覧（status フィルタ）
- 顧客検索（メール・名前・電話）
- 在庫拠点（Location）一覧

**重要**: 本番ストアに直接書き込めるトークンを使うので、`.env` は絶対にコミットしない（`.gitignore` で除外済）。書き込み系（在庫更新等）はAPI実装済だがUI上はまだ読み取りに徹している。書き込み操作を増やす場合は確認モーダルを必ず挟む方針。

<!-- cloudflare-target-contract:v1 -->
<!-- BEGIN:cloudflare-target-contract -->
## Cloudflare公開先の確定（再発防止）

- 公開先の正本は `C:\Project\docs\cloudflare-targets.json`。Cloudflareアカウント、`wrangler` 設定、過去のデプロイ、一時フォルダ、worktreeから公開先を推測しない。
- Cloudflareへ書き込む直前に、台帳の`workingDirectory`へ移動して `powershell -ExecutionPolicy Bypass -File C:\Project\scripts\assert-cloudflare-target.ps1 -ProjectRoot "C:\Project\AI相談" -TargetKey "<target-key>" -ForDeploy` を実行する。Targetが`verified`以外、実行場所不一致、Wrangler名不一致、Vercel deploy経路残存なら停止する。
- このプロジェクトの確認済みTarget: `default / workers-static-assets / aiclimb`。公開URL: https://aiclimb.aiclimb.workers.dev。`C:\Project\AI相談\cloudflare-runtime` から `-TargetKey 'default'` を指定してガードを通す。。公開面は `cloudflare-runtime/public` のStatic Assetsを優先し、管理/API/運用系だけを選択的にWorker先行にする。
- `_tmp`、`_worktrees`、`*-worktree`、`*-cloudflare-worktree` は候補・検証用であり、本番の正本ではない。公開ページをWorker経由にする場合は、静的アセットがWorkerより先に返らない設定と回帰テストを必須にする。
- Vercelは読取専用の移管元。`vercel.json`、`.vercel`、Vercel runtime URLが残れば警告し、Vercel CLI/Action/Secretを使う有効なdeploy経路はエラーで停止する。Vercelへの変更・削除は行わない。
- 共通の実行・本番完了条件は `C:\Project\docs\execution-first.md`、Vercel変更凍結は `C:\Project\docs\vercel-change-freeze.md` を参照する。凍結に抵触するpushは行わず、確認済みTargetと事業全機能の移管完了を区別する。
- 本番後は台帳の確認パス（/、/health、/blog/、/blog/2026-08-30-switchbot-ai-mind-clip.html、/admin）を実URLで確認し、期待版・管理/API経路・canonicalを記録する。
<!-- END:cloudflare-target-contract -->

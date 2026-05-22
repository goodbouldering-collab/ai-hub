# API / MCP / トークン 自動化棚卸し（consul 全事業横断・2026-05-22）

CEO 依頼「GitHub・Vercel・Supabase・Resend・LINE などすべての API / MCP の状況を、consul で共通・自動化するためにまとめる」への回答。
既存の [シークレット台帳](2026-05-17-secrets-inventory.md) と [cron 台帳](2026-05-13-cron-jobs-overview.md) を母体に、2026-05-22 時点の実測で最新化したもの。

> **絶対ルール**: 実トークン値はここに書かない。鍵名・保管場所・用途・自動化の有無だけ。

---

## 0. サマリ（一番大事な3行）

1. **consul 共通の自動化トークンは Windows ユーザー環境変数（setx）に6本**集約済み＝これが「共通基盤の鍵束」。どの事業のCLI/デプロイからも自動で効く。
2. **MCP は4系統**（chrome-devtools / colorme / Cloudflare / Google Drive）。うちローカル常駐2・claude.ai接続2。
3. **🔴 セキュリティ要対応**: `~/.claude/settings.json` の permission allowlist に Vercel 生トークン（`vcp_...`）が4箇所平文で残存（2026-05-22 発見）。要伏字化。

---

## 1. consul 共通の自動化トークン（Windows ユーザー環境変数 / setx）

**これが「全事業共通で自動化する」ための核**。`setx` で永続登録され、新規プロセス（ターミナル・CLI・wrangler・vercel）が自動で参照する。値はレジストリ（HKCU\Environment）にあり git 管理外。

| 環境変数名 | 対象サービス | 主な自動化用途 | 発行元 | 備考 |
|---|---|---|---|---|
| `GITHUB_PERSONAL_ACCESS_TOKEN` | GitHub | リポ push / Actions 連携 / gh CLI | GitHub Developer settings | classic か fine-grained か要確認 |
| `VERCEL_TOKEN` | Vercel | デプロイ / env 操作 / API 経由監視 | Vercel Account Settings | 全Vercel事業の自動デプロイ正本 |
| `SUPABASE_ACCESS_TOKEN` | Supabase | Management API（プロジェクト/APIキー取得/SQL実行） | Supabase Account | 各事業のDB操作の起点 |
| `CLOUDFLARE_API_TOKEN` | Cloudflare | wrangler deploy / D1 / Workers | Cloudflare API Tokens | **2026-05-22 setx 登録**。グッぼる line-crm デプロイ用に追加。Project共通 |
| `ANTHROPIC_API_KEY` | Anthropic | Claude API（各事業のAI機能 / CMA） | Anthropic Console | 複数事業で共通利用 |
| `RENDER_API_KEY` | Render | （Render 完全撤退済のため現在は不使用） | Render | ⚠️ Render撤退済（CLAUDE.md）。削除候補 |

**ポイント**: これらは「共通鍵束」。各事業の本番ランタイム用シークレット（下記2）とは別物で、こちらは**CEO/Claude が手元から自動化を回すための鍵**。

---

## 2. 各事業の本番ランタイム・シークレット（事業別）

各事業が本番で使う鍵。保管庫: **V**=Vercel Dashboard / **CF**=Cloudflare wrangler secret / **G**=GitHub Secrets / **S**=Supabase consul-ops / **L**=ローカル。

| 事業 | 主要サービス | 主な環境変数キー | 保管庫 | 自動化(cron) |
|---|---|---|---|---|
| **グッぼる line-crm** | LINE, Stripe, Anthropic, CF Workers+D1 | `LINE_CHANNEL_ACCESS_TOKEN`/`LINE_CHANNEL_SECRET`/`LINE_LOGIN_*`/`STRIPE_WEBHOOK_SECRET`/`API_KEY` | CF | CF cron 5分毎（triggers） |
| グッぼる シューズ検索 | CF Pages | （静的・なし） | — | GH Actions 月次スクレイプ（毎月28日 15:30 UTC） |
| **Notエステ web** | Supabase, Resend, Next.js(Vercel) | `NEXT_PUBLIC_SUPABASE_*`/`SUPABASE_SERVICE_ROLE_KEY`/`S3_*`/`RESEND_API_KEY`/`PAYLOAD_SECRET`/`REVALIDATE_SECRET` | V | なし |
| **Notエステ line-crm** | LINE, Stripe, CF Workers+D1 | `LINE_*`/`STRIPE_WEBHOOK_SECRET` | CF | なし |
| **N-デザイン** | Supabase, Resend, Vercel, GMaps | `NEXT_PUBLIC_SUPABASE_*`/`RESEND_API_KEY`/`NEXT_PUBLIC_GOOGLE_MAPS_API_KEY` | V | なし |
| **ビジネス21** | Supabase, Resend, Gemini, Vercel | `VITE_SUPABASE_*`/`GEMINI_API_KEY`/`RESEND_*`/`AUTH_SECRET`/`CRON_SECRET` | V+G⚠️ | GH Actions 週次バックアップ（日18:00 UTC=月03:00 JST） |
| **ClimbHero** | CF Pages+D1, Gemini, YouTube/Vimeo, X, Stripe, Resend | `JWT_SECRET`/`GEMINI_API_KEY`/`YOUTUBE_API_KEY`/`VIMEO_ACCESS_TOKEN`/`X_*`/`STRIPE_*`/`RESEND_API_KEY` | CF | CF cron 毎日15:00 UTC（ニュースクロール） |
| **カラッと line-crm** | LINE, Anthropic, CF Workers+D1+Vectorize+Workers AI | `LINE_CHANNEL_*`/`ANTHROPIC_API_KEY`（wrangler secret） | CF | なし |
| カラッと shopify | Shopify Admin API | `SHOPIFY_ACCESS_TOKEN`/`SHOPIFY_STOREFRONT_TOKEN`/`SHOPIFY_STORE_DOMAIN` | L/V | なし |
| **ファディー** | CF Pages+D1, Google OAuth, OpenAI | `GOOGLE_CLIENT_ID`/`OPENAI_API_KEY`/`OPENAI_BASE_URL` | CF | なし（再生成中） |
| **みんなのWA** | Supabase, OpenAI, Stripe, Google, Vercel, Resend | `SUPABASE_SERVICE_ROLE_KEY`/`OPENAI_API_KEY`/`STRIPE_SECRET_KEY`/`GOOGLE_CLIENT_ID`/`RESEND_API_KEY`/`CRON_SECRET` | V | Vercel Cron 毎日12:00 UTC（イベント登録メール） |
| **ai-hub** | Supabase, Anthropic, OpenAI(DALL-E3), Shopify, Google, Colorme, X, Threads, Vercel | `ANTHROPIC_API_KEY`/`OPENAI_API_KEY`/`SUPABASE_SERVICE_ROLE_KEY`/`SHOPIFY_*`/`COLORME_*`/`GOOGLE_APPLICATION_CREDENTIALS`/`X_*`/`THREADS_ACCESS_TOKEN`/`ADMIN_*` | V+G⚠️ | GH Actions 毎日22:00 UTC + 週次月00:00 UTC（Digest生成） |
| **トラスト** | LINE(Messaging+LIFF+Login), Supabase, Anthropic, Vercel | `LINE_CHANNEL_*`/`LINE_LOGIN_*`/`NEXT_PUBLIC_LIFF_ID_*`/`SUPABASE_*`/`ANTHROPIC_API_KEY`/`SESSION_SECRET`/`STAFF_ENROLLMENT_CODE` | V | なし |

---

## 3. MCP サーバの状況

`~/.claude/settings.json` の `enabledMcpjsonServers` と claude.ai 接続から実測。

| MCP サーバ | 種別 | 状態 | 用途 | 認証 |
|---|---|---|---|---|
| **chrome-devtools** | ローカル常駐 | ✅ 有効 | ブラウザ自動操作・パフォーマンス計測・スクショ（業務システムの実機確認） | ローカル（認証不要） |
| **colorme** | ローカル常駐 | ✅ 有効 | カラーミーショップ API（グッぼる本店・商品/ブログ） | OAuth（`colorme authenticate`） |
| **Cloudflare Developer Platform** | claude.ai 接続 | 接続可 | Cloudflare リソース操作 | claude.ai OAuth（`authenticate`） |
| **Google Drive** | claude.ai 接続 | 断続接続 | Drive ファイル検索・読み取り | claude.ai OAuth |

> MCP は「Claude セッションから外部サービスを直接叩く」経路。上記2(環境変数トークン)が「CLI/スクリプトから叩く」経路。役割が別。

---

## 4. 自動化（cron）の集約状況

[cron 台帳](2026-05-13-cron-jobs-overview.md) と整合。実行基盤は3系統に分散（CLAUDE.md の判定フローどおり「適材適所」）。

| 実行基盤 | ジョブ | スケジュール(UTC) | 用途 |
|---|---|---|---|
| **GitHub Actions** | ビジネス21 バックアップ | 日 18:00（月03:00 JST） | Supabase 週次ダンプ→Artifact |
| GitHub Actions | ai-hub Daily Digest | 毎日 22:00（翌07:00 JST） | 差分記事生成 |
| GitHub Actions | ai-hub Weekly Digest | 週・月 00:00 | 統合記事生成 |
| GitHub Actions | グッぼる シューズ検索 | 毎月28日 15:30 | スクレイピング |
| **Vercel Cron** | みんなのWA メール送信 | 毎日 12:00 | イベント登録メール |
| **Cloudflare Cron** | ClimbHero ニュースクロール | 毎日 15:00 | ニュース収集 |
| Cloudflare Cron | グッぼる/Notエステ line-crm | 5分毎（triggers） | LINE Bot 定期処理 |

---

## 5. Google API 連携基盤（scheduler / mailer 用）

consul 専用の OAuth 基盤（[google_ops/](../google_ops/README.md)）。上記の事業別シークレットとは独立。

| 項目 | 内容 |
|---|---|
| トークン保管 | Supabase `consul-ops` の `oauth_tokens` テーブル（service_role専用・RLS有効）= 保管庫 **S** |
| 対象アカウント | `goodbouldering`（ぐっぼる事業）/ `lossismore`（CEO個人）の2系統 |
| スコープ | Calendar R/W + Gmail.modify + Gmail.compose（**送信スコープなし**＝誤送信防止） |
| 取得方法 | 初回のみ `python google_ops/scripts/authorize.py --account <label>`、以後 `refresh.py` が自動 refresh |

---

## 6. 🔴 セキュリティ要対応（2026-05-22 発見）

| 優先 | 内容 | 状態 |
|---|---|---|
| **🔴 高** | `~/.claude/settings.json` の permission allowlist に Vercel 生トークン `vcp_...` が4箇所平文残存（CMA workspace_vibe デプロイ時の使い捨てコマンドが残ったもの）。git管理外だがローカル平文は漏洩源。`VERCEL_TOKEN` 環境変数があるため allowlist に生値は不要 | **要伏字化**（ハーネスが自己権限ファイル編集をブロック→CEO手動 or 許可が必要） |
| 高 | `CONSUL_REPO_PAT` 失効疑い（前台帳より継続）。sync-consul-docs.yml 不動作 | 未対応 |
| 中 | `THREADS_ACCESS_TOKEN` 60日失効の棚卸し・カレンダー登録未整備 | 未対応 |
| 中 | `RENDER_API_KEY` が環境変数に残存だが Render 完全撤退済。削除候補 | 棚卸し要 |
| 中 | `SUPABASE_SERVICE_ROLE_KEY`/`ANTHROPIC_API_KEY` の保管庫重複（V+G）。ローテ二重管理 | 構造課題 |

### 🔴 高優先の対処コマンド（CEO がターミナルで実行）

settings.json の allowlist から `vcp_` を含む行を一括削除:

```powershell
$path = "$env:USERPROFILE\.claude\settings.json"
$json = Get-Content $path -Raw | ConvertFrom-Json
$json.permissions.allow = @($json.permissions.allow | Where-Object { $_ -notmatch 'vcp_' })
$json | ConvertTo-Json -Depth 20 | Set-Content $path -Encoding utf8
Write-Output "残りallow件数: $($json.permissions.allow.Count)"
```

実行後、漏れたトークンは念のため Vercel Dashboard で **Regenerate** 推奨（一度平文でディスクに書かれたため）。

---

## 7. 「共通で自動化する」ための現状評価と次の一手

**できていること**:
- 共通鍵束（環境変数6本）で CLI/デプロイ自動化の土台はある
- cron は3基盤に適材適所で分散（統一の罠は回避済・CLAUDE.md）
- Google 連携は OAuth 基盤で集約済

**ボトルネック**:
- 保管庫が5系統（環境変数 / V / CF / G / S / L）に分散。鍵のローテ時に全保管庫を追わないと本番が黙って壊れる
- `RESEND_API_KEY` が事業ごとに別管理（みんなのWA/Notエステ/Nデザイン/ビジネス21/ClimbHero）。Resend は1アカウントで複数ドメイン送れるため、共通化の余地あり
- LINE は事業ごとに独立チャネル（グッぼる/Notエステ/カラッと/トラスト）＝これは正しく分離

**次の一手の候補**（要 CEO 判断・advisor 案件）:
1. settings.json 生トークン伏字化（即・上記コマンド）
2. RENDER_API_KEY 削除（Render 撤退済）
3. Resend の共通アカウント化検討（鍵を1本に）
4. 保管庫の集約（Supabase Vault 単一化）は工数大・将来 advisor 案件

---

## 付記: グッぼる line-crm 本番デプロイ（2026-05-22）

- 独自実装 + 「タブ以外の自由文には自動応答しない」(CEO指示) を本番反映
- デプロイ先: `line-harness-goodbouldering`（https://line-harness-goodbouldering.goodbouldering.workers.dev）
- 詰まり: `@cloudflare/vite-plugin` がマルチ環境非対応で `--env production` が無視され dev環境(D1未設定)でエラー
- 解決: `wrangler deploy dist/line_harness/index.js --env production --config wrangler.toml` で redirected config を回避
- 教訓: 同構成の Notエステ/カラッと line-crm も同じデプロイ方法が必要

2026-05-22 codex:rescue 発火（グッぼる/vite-pluginマルチ環境デプロイ診断/方法A=--config明示で解決・成功）

# Render / Cloudflare アカウント破棄の可否調査（2026-05-12）

## 結論サマリ

| 対象 | 結論 | 理由 |
|---|---|---|
| **Render** | ✅ **即時破棄可能** | 本番運用中サービス 0 件・全 suspend 済・課金停止済・親リポ keepalive YAML 削除済 |
| **Cloudflare** | ❌ **そのままでは破棄不可** | 本番依存 6 系統あり。**移行作業 2〜4 週間** が必要 |

---

# 🟢 Render の破棄可否

## 現状（2026-05-11 完全廃止済の補足確認）

| プロジェクト | 状態 | 撤収日 |
|---|---|---|
| business21-kanri | Free Suspend | 2026-04-28 |
| n-design | Free Suspend + 親リポからの参照削除 | 2026-04-29 |
| みんなのWA | Starter Suspend → CEO 完全削除済 | 2026-04-30 / 2026-05-11 |
| ai-hub Static | 削除済 | 2026-05-05 |
| gtn-ai | プロジェクト終了・GitHub/ローカル両方削除済 | 2026-04-30 |

**現時点で本番運用中の Render サービスは 0 件**（親 CLAUDE.md 行 240 で確認済）。
親リポ `.github/workflows/render-keepalive.yml` も 2026-05-11 削除済。

## 破棄手順（CEO Dashboard 操作）

1. https://dashboard.render.com/ にログイン
2. 左メニュー「Services」 → 残存サービス（あれば全て）「Delete Service」
3. 左メニュー「Account Settings」 → 「Billing」 → 課金プランを Free に戻す（既に Free のはず）
4. 左メニュー「Account Settings」 → 最下部 「Delete Account」 → メールアドレス入力で確定

## 破棄前のバックアップ（推奨）

- Render Disk を使っていたサービスがあれば内容ダウンロード（`みんなのWA` の旧 data.json + uploads — 既に Supabase Storage へ移行済なので不要）
- 環境変数の controle は CEO 側で控えてあれば不要（Vercel 側に同じ値が入っているため）

## 破棄の影響範囲

- **本番影響**: ゼロ（運用中サービス 0）
- **コスト影響**: ゼロ（既に課金停止済）
- **ロールバック**: 必要なら Vercel に同じコードがあるので Render 再構築は数分で可能

→ **CEO がやる気になった瞬間に削除して問題なし**。

---

# 🔴 Cloudflare の破棄可否

## 現状の本番依存（6 系統）

### 1. ClimbHero（**最大の依存・例外プロジェクト**）

[climb-hero.md:30-46](../climb-hero.md) より、**Cloudflare 完全集約**で運用中：

| レイヤー | サービス | 役割 |
|---|---|---|
| ホスティング | Cloudflare Pages (`project-02ceb497`) | フロント + Hono Workers |
| DB | Cloudflare D1 (`webapp-production`) | クライミング動画 + ユーザー DB |
| セッション | Cloudflare KV (`SESSIONS`) | JWT revocation |
| ストレージ | Cloudflare R2 (`UPLOADS`) | 未有効・将来用 |
| AI | Workers AI + Gemini API | 動画解析多言語 |
| Cron | Cloudflare Cron Triggers | 1日4回の動画/ニュース巡回 |
| メール | Cloudflare Email Workers | ユーザー通知 |
| CAPTCHA | Cloudflare Turnstile | bot対策 |
| 管理画面 | Cloudflare Access (Zero Trust) | `/admin/*` SSO 保護 |

**本番URL**: https://project-02ceb497.pages.dev
**Cloudflare Account ID**: `2cc53dc7f0cadb5f36fa48d256e10cc7`
**移行コスト**: ≥ 4 週間（DB/ストレージ含めた完全リライト・親 CLAUDE.md でも「Cloudflare 集約の例外・Vercel 移行を検討してはいけない」と明記）

→ **Cloudflare アカウント削除 = ClimbHero プロジェクトの完全消滅**

---

### 2. LINE Webhook 4 本（補完レイヤ）

| プロジェクト | Worker 名 | 役割 |
|---|---|---|
| ぐっぼる | `line-harness-goodbouldering` | LINE Bot エンドポイント |
| カラット | `karatto-line-crm` | LINE CRM + 会話履歴 D1 |
| notエステ | `line-harness-notesthe` | LINE Bot |
| ファディー（旧） | `fadyhikone-production` / `webapp-production` | 廃棄予定だが残置中 |

**移行コスト**: 各 0.5〜1 日（Vercel API Route に書き直し可能・親 CLAUDE.md 2026-05-12 方針更新で「新規 LINE Bot は Vercel に乗せる」と確定）

→ Vercel に移行すれば破棄可能だが、**ぐっぼる・カラット・notエステの LINE 接続が一時停止する**ため切替日設定が必須

---

### 3. DNS（ドメイン管理）

| ドメイン | 用途 | 切替先 |
|---|---|---|
| `minanowa.com` | みんなのWA本番 | Cloudflare DNS proxy → Vercel |
| `goodbouldering.com` | ぐっぼる本店 | カラーミー（Cloudflare 経由か要確認） |
| `karatto.life` | カラット本番 | Cloudflare 経由か要確認 |
| その他のカスタムドメイン | 各事業 | Cloudflare 経由か要確認 |

**移行コスト**: ドメインごとに **DNS レジストラ側で nameserver を変更** が必要（Cloudflare → Vercel DNS or Route53 等）。各ドメイン伝播に最大 48 時間。

→ **Cloudflare アカウント削除前に全ドメインの nameserver 切替が必須**。
　 切替忘れたドメインは **完全アクセス不能**。

---

### 4. ファディー旧 Cloudflare（廃棄予定）

**2026-05-13 訂正済**: 実体確認の結果、ファディー旧 Cloudflare 資産は以下のみ。

| 名称 | ID | 状態 |
|---|---|---|
| Workers `fadyhikone-production` | - | 廃棄予定（Phase 2 で削除） |
| D1 `fadyhikone-production` | `3c41910c-1b96-47ad-99e7-604df7428bdb` | 廃棄予定（Phase 2 で削除） |

> **過去の誤記録について**: 以前「ファディーは `webapp-production` Worker / D1 (`2faec3c4-...`) も持っている」と記載していたが、[ファディー\fadyhikone\wrangler.jsonc](ファディー\fadyhikone\wrangler.jsonc) を直接読んで確認した結果、**`webapp-production` は ClimbHero 専用**であり、ファディーとは無関係と判明。ID 重複疑惑は consul の記録ミスが原因で、実体は別物・無関係。
>
> → ファディー旧の Phase 2 削除は ClimbHero 側 (Phase 1) に**一切影響しない**。連動性なし。

---

### 5. アカウント単位の固定アセット

| 種類 | 影響 |
|---|---|
| API Token | 親リポ `reference_cloudflare_api.md` に手順あり・自動化スクリプトが動作不能になる |
| Email Routing | Cloudflare ドメインで設定中なら全メール経路が消える |
| WAF / Rate Limit | DNS 切替で消滅（Vercel WAF or Cloudflare 単独 DNS で代替必要） |

---

## 破棄するために必要な作業（順序）

### Phase A: ClimbHero の去就決定（**意思決定の核心**）

**選択肢**:

| 案 | 内容 | 工数 | コスト |
|---|---|---|---|
| **A-1: ClimbHero 廃止** | プロジェクト終了。データ・コードを GitHub アーカイブ化 | 1日 | $0 |
| **A-2: Cloudflare 残置・他のみ撤収** | ClimbHero だけ Cloudflare、他は移行 | 4週間 | Cloudflare $0〜5/月維持 |
| **A-3: ClimbHero 完全リライト → Vercel + Supabase** | D1 → Postgres、KV → Redis、R2 → Supabase Storage | 4〜8週間 | Vercel Pro + Supabase Pro = $45/月 + 開発工数 |

→ **CEO 判断の核心はここ**。A-1 / A-2 / A-3 のどれを選ぶか。

### Phase B: LINE Webhook 移行（A 確定後・1〜2 週間）

1. Vercel 側に `/api/webhook/line/<事業名>` を新設
2. LINE Developer Console で Webhook URL を Cloudflare Workers → Vercel API に切替
3. 各事業（ぐっぼる・カラット・notエステ）で接続テスト
4. 動作確認後 Cloudflare Worker 削除

### Phase C: DNS 移行（B 並行可・1 週間）

1. 全カスタムドメインの一覧化
2. ドメインレジストラ側で Cloudflare → 別 DNS（Vercel DNS / Route53 等）に nameserver 切替
3. 伝播待ち（最大 48 時間）
4. 全ドメイン疎通確認

### Phase D: 残アセット削除

1. Cloudflare Dashboard で残った Workers / KV / R2 / D1 を全削除
2. Email Routing 解除
3. Zone（ドメイン）削除

### Phase E: アカウント削除

1. Cloudflare Dashboard 右上 → 「Manage Account」 → 「Members」
2. 「Profile」 → 最下部 「Delete Account」
3. 確認メールに従い完全削除

---

## 推奨判断

### Render
**今すぐ破棄して OK**。CEO が Dashboard で 1〜3 分の操作で完了。

### Cloudflare
**そのままでは破棄不可**。先に **ClimbHero の去就を決める**ことが全ての起点。

CEO が「ClimbHero どうしたい？」を決めれば、本部側で Phase B 以降の移行計画と工数見積もりを出せます。

---

## 確認したい論点（CEO 向け）

1. **ClimbHero は今も育てたい事業か、塩漬け OK か、廃止か？**
2. **LINE Webhook 4 本を Vercel に移行する切替時期はいつ頃が許容範囲か？**（一時的に LINE 接続が止まる）
3. **DNS は Cloudflare 以外（Route53 / Vercel DNS / Porkbun 等）どこに移したいか？**
4. **Cloudflare 完全撤収の動機は何か？**
   - コスト（実は無料運用中なので削減効果は $0）
   - 管理プラットフォーム削減（運用ストレス低減目的）
   - セキュリティ・規約上の理由
   - その他

→ 動機次第で「全廃止」「ClimbHero だけ残す」「補完だけ廃止」の最適解が変わる。

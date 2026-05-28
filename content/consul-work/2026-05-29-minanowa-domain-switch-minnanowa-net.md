# みんなのWA：独自ドメイン切替（`minanowa.com` → `minnanowa.net`）

## 経緯

- CEO 希望は `minnanowa.com`（正しい綴り）だったが、Verisign 公式 RDAP で `active` / 期限 2027-01-08 / 2026-01-05 に更新実行済の他社所有ドメインと確定（Xserver 画面の「期限切れ」表示は誤り）
- 代替候補を 10 案 + 追加 10 案調査し、CEO が `minnanowa.net` を選択

## 実施内容（2026-05-29）

### 1. ドメイン取得

- レジストラ: **Vercel Registrar**（N-デザインと同じ運用）
- 価格: 初年度 **$13.50** / 更新 $13.50/年・auto-renew ON
- 期限: 2027-05-29
- 備考: Vercel CLI が "An unexpected error happened" を返したが、これは表示バグで実際は登録成功（`vercel domains inspect` で確認・2分後に正常に detail 表示）

### 2. Vercel Project 紐付け（プロジェクト `minanowa` / `prj_zVxZrMg0XkvuRqoWi9tr3iBXJNZm`）

- `minnanowa.net`（本番正本）
- `www.minnanowa.net`

### 3. 301 リダイレクト構造

| 元 | 先 | コード |
|---|---|---|
| minnanowa.net | （本番アプリ） | 200 |
| www.minnanowa.net | minnanowa.net | 301 |
| minanowa.com | minnanowa.net | 301 |
| www.minanowa.com | minnanowa.net | 301 |

設定は Vercel API `PATCH /v9/projects/:id/domains/:domain` で実施（CLI には UI コマンドなし）。順序が重要だった：既存の `www.minanowa.com → minanowa.com` 構造があったため、まず www 側を先に minnanowa.net に向け直してから minanowa.com の redirect 元に変える必要があった。

### 4. Resend 認証

- API 経由で `minnanowa.net` ドメイン追加（domainId: `5dccd676-95b8-4029-87ed-1d3f0653f105`）
- 3 つの DNS レコード（DKIM TXT, SPF MX, SPF TXT）を **Vercel-DNS** に Vercel REST API 経由で追加
- 追加直後に Resend `/verify` を叩いて 15 秒後 `status: verified` 確認
- Vercel-DNS 内部の伝播が早く、一発で通った

### 5. Vercel 本番環境変数

- 旧 `MAIL_FROM` 削除 → 新 `MAIL_FROM = "みんなのWA <noreply@minnanowa.net>"` を登録
- PowerShell コンソールエンコーディング起因の UTF-8 文字化けで「みんなのWA」が「????WA」に化けた1回目を発見、即削除して **WebRequest を UTF-8 バイト列で直接 POST** することで再登録（正しく保存確認）

### 6. コード変更（commit `a0f3fd4`）

| ファイル | 内容 |
|---|---|
| `lib/mailer.js` | FROM フォールバック・メール本文フッターリンクを `minnanowa.net` に |
| `api/auth/guest-register.js` | host フォールバックを `minnanowa.net` に |
| `api/password-reset/request.js` | 同上 |
| `api/cron/send-event-registration-mails.js` | 同上 |
| `api/admin/test-send-registration-mail.js` | テストURL差替 |
| `media/cards/sample.json` | OGカードフッター |
| `みんなのWA/CLAUDE.md` | 本番URL記述更新 |

push まで完了（安全ゲート: ビルドステップなし・秘密情報なし）。Vercel が自動本番デプロイ実行。

### 7. Cloudflare DNS proxy OFF

- 旧 `minanowa.com` の Cloudflare DNS は依然として CNAME `cname.vercel-dns.com` を持っていたが、**proxied=True**（オレンジ雲）になっており、TLS renegotiate エラーで応答不能になっていた
- Cloudflare API（`$env:CLOUDFLARE_API_TOKEN`）で minanowa.com / www.minanowa.com の CNAME を **proxied=False（DNS only）**に変更
- DNS 伝播後（TTL=auto = 5 分相当）、`https://minanowa.com → 301 → https://minnanowa.net` が動作する見込み

## 関連数値

| 項目 | 金額 |
|---|---|
| Vercel Registrar 初年度 `minnanowa.net` | $13.50（約 ¥2,100） |
| 5年運用合計（$13.50 × 5） | $67.50（約 ¥10,500） |

`minnanowa.com` は CEO 希望だったが、所有者が韓国のレジストラ（ConnectWave）経由で能動的に更新しているため買い取り交渉は数十万円〜数百万円規模になる可能性が高く、対費用効果で `.net` 路線が妥当と判断。

## 残課題

1. **DNS 伝播後の `minanowa.com → minnanowa.net` 301 動作確認**（5〜30 分待ち）
2. **README.md の `admin@minanowa.com`**：Supabase Auth 実アカウントなのでドメインだけ書き換えるとログイン不能。アカウント切替は別タスクで扱う（Supabase Dashboard で `admin@minnanowa.net` 作成 → 旧アカウント無効化）
3. **Cloudflare 上の旧 Resend レコード**（minanowa.com 配下の MX/DKIM/SPF）：当面は残置でも害なし。minanowa.com の運用完全停止時に削除
4. **minanowa.com のレジストラ Transfer-in を Vercel へ**（手動操作・$11.25・5-7日プロセス）。やる/やらないは CEO 判断
5. **イベントURL短縮実装**（次タスクとして Codex 委任中・別作業ログ）

## 検証

```
=== minnanowa.net ===
HTTP/1.1 200 OK  ← 本番アプリ応答

=== minnanowa.com（DNS伝播待ち時点）===
（Cloudflare の古い IP に解決中・DNS伝播後に 301 動作開始）
```

## 委任ログ

- なし（このタスクは Claude 単独で完了。Codex 委任は別タスク=イベントURL短縮）

🌐 Deploy URL: https://minnanowa.net

# カラット Shopify 実データ接続セットアップ（2026-05-11）

## 完了済（コード側）

- ✅ Shopify Dev MCP（`@shopify/dev-mcp@1.13.0`）親 `.mcp.json` 登録
- ✅ Shopify CLI v3.94.3 グローバルインストール
- ✅ [カラッと/shopify/scripts/](../../カラッと/shopify/scripts/) に Admin GraphQL クライアント雛形（fetch-products / fetch-orders / fetch-customers）
- ✅ `npm install` 済（`@shopify/admin-api-client@1.1.2` + `dotenv@16.4.5`）
- ✅ `.mcp.json` から架空パッケージ `@shopify/admin-api-mcp` を除去（公式未提供だったため）
- ✅ CLAUDE.md を実態に合わせて修正

## CEO 作業（ブラウザ＋ターミナル）

### A. Admin API トークン発行（5分）

1. <https://84c617.myshopify.com/admin> にログイン
2. **設定** → **アプリと販売チャネル**
3. 右上の **アプリ開発を許可** → **アプリ開発を許可する**
4. **アプリを作成** → 名前: `claude-code-admin`（任意）
5. **設定** タブ → **Admin APIアクセススコープを設定** → 以下にチェック
   - `read_products` / `write_products`
   - `read_orders` / `write_orders`
   - `read_themes` / `write_themes`
   - `read_inventory` / `write_inventory`
   - `read_customers` / `write_customers`
   - `read_content` / `write_content`
6. **保存** → 上タブ **APIアクセス** → **Admin APIアクセストークンを表示**
7. `shpat_...` で始まるトークンをコピー（**1回限り表示**・控え必須）

### B. `.env` 作成（1分）

```powershell
cd C:\VSCode\Project\カラッと\shopify
Copy-Item .env.example .env
notepad .env
```

`SHOPIFY_ACCESS_TOKEN=shpat_xxxx...` を実トークンに置換して保存。

### C. 動作確認（30秒）

```powershell
cd C:\VSCode\Project\カラッと\shopify\scripts
npm run fetch:products
```

商品20件分のJSONが標準出力に出ればOK。エラーなら `.env` パスかスコープを再確認。

### D. テーマ pull（2分・任意）

```powershell
cd C:\VSCode\Project\カラッと\shopify\theme
shopify theme pull --store=84c617.myshopify.com
```

ブラウザが開いて Shopify ログイン認証 → テーマ一覧から「ライブテーマ」を選択 → Liquid ファイルがローカルに展開される。

### E. テーマ編集の本番反映（要注意）

**直接 push は禁止**。必ず開発用テーマで検証：

```powershell
shopify theme push --unpublished --store=84c617.myshopify.com
# → 管理画面でプレビュー → 問題なければ「公開」
```

## 残タスク（B 完了後に着手）

- [ ] `scripts/register-webhook.mjs`（注文作成・顧客登録の Webhook を `karatto-line-crm` Worker に向ける）
- [ ] `karatto-line-crm` 側に `/shopify/webhook/*` ルート追加（HMAC 検証付き）
- [ ] 書き込み系スクリプト雛形（`update-product-price.mjs` 等）— 必要になった時点で

## 注意事項

- **`.env` は絶対コミットしない**（既に `.gitignore` 済だが `git status` で要確認）
- **トークンは失くしたら再発行**（同じ値は二度と出ない）
- **本番テーマへの直接 push は禁止**。`--unpublished` 経由が原則
- Admin API レート制限: GraphQL コスト制 / REST 2req/sec。バルクは `bulkOperationRunMutation`

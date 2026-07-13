# AI相談「すべての実績」自動同期

## 目的

全事業で完成・公開したサイトを、AI相談トップの「すべての実績」へURLとサイト画面付きで追加する。
同じ事業名、slug、URL、Vercel project ID は1件に統合し、URL変更時は旧URLを `aliases` に残す。

## 自動処理

- 各事業の本番公開完了フックが、確認済みURLとサイト情報を `.github/workflows/portfolio-sync.yml` へ渡す。
- workflowは毎日、台帳・URL・サイト画像出力・重複を再検証する。
- `VERCEL_TOKEN` をGitHub Actionsへ管理者が明示設定した環境では、Vercel Teamの公開プロジェクト探索も補助的に行う。ローカル認証を自動移送しない。
- `config/portfolio-sync.yaml` の `include: false` だけを掲載対象外とする。
- 未登録の公開HTMLサイトは、タイトルとdescriptionを取得して新規追加する。
- 既存名・slug・URL・project IDが一致すればカードを更新し、重複追加しない。
- カード画像は確認済み本番URLのWeb画面キャプチャを自動生成する。
- 変更時は `site/dist/index.html` を再ビルドしてmainへcommitし、Vercel本番デプロイへつなぐ。

## 公開直後のフック

Vercel、Cloudflare Pages、カラーミー、Shopifyの別を問わず、本番URL確認後にメタデータを付けて実行する。

```powershell
gh workflow run portfolio-sync.yml --repo goodbouldering-collab/ai-hub `
  -f name="サイト名" `
  -f url="https://example.jp" `
  -f slug="example" `
  -f category="企業サイト" `
  -f tech="Cloudflare Pages,Workers" `
  -f summary="誰の何の悩みを解決するサイトか"
```

掲載禁止・顧客契約上非公開・認証専用・社内資料の場合は、先に `config/portfolio-sync.yaml` へ
`include: false` と理由を追加する。公開URLを推測して登録しない。

## ローカル確認

```powershell
$env:VERCEL_TOKEN="..."
python scripts/sync_portfolio.py
python -m unittest tests.test_portfolio_sync
python site/build_site.py
python scripts/verify_portfolio_output.py
```

`sync_portfolio.py` は既定でdry-run。保存する場合だけ `--write` を付ける。Vercel全体を探索せず登録フックだけ試す場合は `--no-vercel` を付ける。

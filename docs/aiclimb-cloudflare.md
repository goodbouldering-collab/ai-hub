# AIClimb Cloudflare公開配信

## 目的

公開ページをCloudflareのエッジから高速配信しながら、認証、決済、管理画面、既存APIの運用を止めない。

## 現在の構成

| 経路 | 実行場所 | 理由 |
|---|---|---|
| 公開HTML・CSS・JavaScript・画像 | Cloudflare Workers Static Assets | 配信を高速化し、Vercelの転送量を減らす |
| `/health` | Cloudflare Worker | Vercel障害と分離して配信状態を監視する |
| `/admin`、`/api`、`/ops` | Vercelへ直接移動 | Cloudflareが認証Cookieや申込本文を中継しない |
| `/watch`、`/seo-llmo-diagnosis` | Vercelへ直接移動 | 既存の動的APIと同一originで動作させる |
| 25MiBを超える講習動画 | Vercelへ直接移動 | Workers Static Assetsの1ファイル上限を超えるため |

公開正本は `https://aiclimb.aiclimb.workers.dev`。SEO canonical、OG URL、sitemapもこのURLへ統一する。管理画面、API、決済処理は安全性を優先し、`https://aiclimb.vercel.app` へ直接移動して実行する。

## 安全性

- Cloudflare側へAPIキーや認証情報を複製しない。
- Cloudflare WorkerはAuthorization、Cookie、申込本文を読み取らず、Vercelへ送信しない。
- 公開ページ内の管理、API、決済リンクをCloudflareで開いた場合は、固定したVercel originへの`307`だけを返す。
- リダイレクト先は固定originと元のpath/queryから組み立て、任意サイトへ転送できないようにする。

## 検証

```powershell
npm.cmd run cloudflare:check
npx.cmd wrangler deploy --dry-run
```

本番では最低限、次を確認する。

1. `/health` が `200` とCloudflare配信JSONを返す。
2. `/`、ブログ、講習資料、画像が `200` で表示される。
3. `/admin` と `/api/admin/ping` がVercelへ直接移動し、その後に未認証時の `401` を返す。
4. 講習動画がVercelへ直接移動し、Rangeリクエストに `video/webm` を返す。
5. PC幅とスマートフォン幅で表示崩れ、横スクロール、コンソールエラーがない。

## ロールバック

Cloudflare側で問題が起きた場合は、直前の正常なWorker Versionへロールバックする。緊急時は公開案内をVercel本番へ戻せるが、Worker削除は最終手段とし、先にVercel本番の正常性を確認する。

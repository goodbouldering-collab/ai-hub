# AIClimb Cloudflare並行配信

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

Cloudflareの確認URLは `https://aiclimb.aiclimb.workers.dev`。SEO canonical、OG URL、決済の戻り先は、独自ドメインを取得するまで `https://aiclimb.vercel.app` を正本とする。

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

正規URLはVercelのままなので、Cloudflare側で問題が起きても利用者向け本番は影響を受けない。Cloudflare確認URLを止める必要がある場合は、直前の正常なWorker Versionへロールバックする。Worker削除は最終手段とし、先にVercel本番の正常性を確認する。

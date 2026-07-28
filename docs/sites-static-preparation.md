# Sites 向け静的ファイル準備

`site/dist` の既存ページ構造を保ったまま、Codex Sites の静的配信元
`public` を生成します。

## 実行

```powershell
# site/dist を検査するだけ（public は変更しない）
node scripts/prepare_sites_public.mjs --check

# 現在の site/dist を public にコピー
node scripts/prepare_sites_public.mjs

# Python の既存サイト生成後にコピー
node scripts/prepare_sites_public.mjs --build

# Workerを含むSites本番ビルド
npm run build

# 単体テスト
npm run test:sites
npm run test:worker
```

通常実行では `site/build_site.py` を起動しません。サイト生成も必要な場合だけ
`--build` を指定します。PythonがPATHにないWindowsでは、実行前に
`PYTHON`へ実行ファイルの絶対パスを設定します。

## コピーしないパス

以下は Sites へ静的コピーせず、既存バックエンドや外部配信先へ委ねます。

- `admin/`
- `api/`
- `img/`
- `ops/`
- `watch/`
- `media/`
- `videos/`
- `lectures/assets/codex-app-onboarding.webm`

コピー対象は1ファイル25MiB以下に制限します。上限超過、シンボリックリンク、
想定外の入出力パスを検出した場合は、既存の `public` を削除する前に失敗します。
出力先はリポジトリ直下の `public` に固定し、静的ページの相対パスをそのまま維持します。

## 段階移行中の経路

公開HTML・画像はSitesから配信し、次の経路は既存のVercel本番へHTTPメソッド、
生のリクエスト本文、Cookie、Range応答を維持して中継します。

- `/api/**`
- `/admin**`
- `/img/**`
- `/ops**`
- `/watch**`
- `/media/**`
- `/videos/**`
- `/lectures/assets/codex-app-onboarding.webm`

これにより、Vercel固有の管理API、Square／Stripeの決済API、定期収集、大容量動画を止めずに
公開面からSitesへ移行できます。完全移行は各APIをWorkers互換へ移してから行います。

サロンの公開CTAは `/api/square/ai-salon-checkout` へPOSTし、Sites Workerから
Vercel本番のSquare APIへ中継します。Squareが月額2,200円の定期課金を作成し、
決済確認済みの `/api/square/ai-salon-access` だけがLINE招待URLを返します。
静的HTMLへOpenChat招待URLを埋め込まないでください。

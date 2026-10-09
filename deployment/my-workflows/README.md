# 管理ブログ・リールの制作と保存キー

2026-10-09。myblog/myreel UIと同一originの暗号化APIキー保存を既存公開Workerの前段で扱う。認証判定は既存Workerの `/api/admin/ping` に委譲し、その他のURLはそのまま既存Workerへ渡す。

- 既存Worker: `deployment/ai-news/published-worker.mjs`、SHA256 `f00d0e407205042faaee8f9cf4f269e5b8c9aa7eaec14e5396896c83fb75a0c3`。直前の公開版と一致を確認。
- UI再生成: `node scripts/build-my-workflows-assets.mjs`。
- bundle再生成: esbuild 0.28.1で `deployment/my-workflows/worker.mjs --bundle --platform=node --format=esm --outfile=deployment/my-workflows/published-worker.mjs`。
- 検証: `node --test deployment/my-workflows/worker.test.mjs`。ソースとbundleの既存ログイン、匿名拒否、キー保存・再利用、管理UI、公開asset引継ぎを合成データで確認する。
- キー: 既存ADMIN_SESSION_SECRETから派生した鍵でAES-GCM暗号化。365日・HttpOnly・Secure・SameSite Strict。同じサイト/ブラウザでブログ・リール共用。値はJSON/画面/ログに出さない。
- 公開は台帳workingDirectoryから。確定統合SHAの本bundleを登録設定へ明示し、直前ガード成功後に配備する。公開assetsは直前公開 `.codex-workers-ai-release-20261009/public` の556ファイルをverification.jsonの全SHAと照合して保持する。古いprofile/glass資産へ戻さない。
- 実キーでの生成・管理者本人の画面受入・実投稿は別確認。秘密値・認証方式・DNS・顧客データは変更しない。

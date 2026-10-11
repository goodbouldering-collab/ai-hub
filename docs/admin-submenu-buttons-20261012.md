# 管理画面のサブメニューをボタン化

最終更新: 2026-10-12。ローカル検証済み、統合・本番公開は未実施。

ブログの各制作工程、ブログ・リール切替、指令室、内部資料のヘッダー下ナビゲーションを、共通テーマの枠付きボタンに統一した。現在地は青緑の塗りと白文字。最小高さ44px、8px間隔、狭い画面では折り返す。リンクとしての動作、行き先、認証、保存処理は変更しない。

## 検証

- `node --test deployment/admin-workspace/worker.test.mjs deployment/admin-workspace/routes.test.mjs deployment/my-workflows/worker.test.mjs`: 10件成功。
- `npm --prefix cloudflare-runtime test`: 7件成功。
- `node .github/scripts/check-cloudflare-deployment.mjs`: PASS。既存の部分移行の警告は継続。
- 既存のAI相談用Chromeを再利用。PC1536pxと390pxでブログ編集、390pxで指令室・ブログ制作の枠、現在地、折り返し、横はみ出しなしを確認。記事一覧へのボタン遷移も確認。
- 最新の公開資産はPR #157のreel講座を含む612件。全ハッシュを照合して保持し、管理Workerだけを更新する。容量不足を避け、変更しない資産は同一ボリュームのハードリンクで準備する。出力先は新規ディレクトリのみとし、リンク後の資産を編集しない。
- Node24.15.0、esbuild0.25.12、Wrangler4.143.1。APIキー実入力・生成・保存は今回の確認対象外。既存のAPI移行残件は維持する。

## 公開記録

工程と証拠は登録公開元 `work/genspark-profile-edit/tmp/delivery/20261012-admin-submenu-buttons.json` および同名フォルダへ保存する。確定Git blobから再生成し、中央のCloudflare公開先ガードを通して公開後、本番の認証済み画面・公開資産・認証境界を確認する。

確認対象: https://aiclimb.aiclimb.workers.dev/admin/blog-editor

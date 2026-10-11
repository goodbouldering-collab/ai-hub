# 管理画面のサブメニューをボタン化

最終更新: 2026-10-12。ローカル検証・PR統合・本番公開・認証済み画面確認済み。

ブログの各制作工程、ブログ・リール切替、指令室、内部資料のヘッダー下ナビゲーションを、共通テーマの枠付きボタンに統一した。現在地は青緑の塗りと白文字。最小高さ44px、8px間隔、狭い画面では折り返す。リンクとしての動作、行き先、認証、保存処理は変更しない。

## 検証

- `node --test deployment/admin-workspace/worker.test.mjs deployment/admin-workspace/routes.test.mjs deployment/my-workflows/worker.test.mjs`: 10件成功。
- `npm --prefix cloudflare-runtime test`: 7件成功。
- `node .github/scripts/check-cloudflare-deployment.mjs`: PASS。既存の部分移行の警告は継続。
- 既存のAI相談用Chromeを再利用。PC1536pxと390pxでブログ編集、390pxで指令室・ブログ制作の枠、現在地、折り返し、横はみ出しなしを確認。記事一覧へのボタン遷移も確認。
- 最新の公開資産はPR #157のreel講座を含む612件。全ハッシュを照合して保持し、管理Workerだけを更新する。容量不足を避け、変更しない資産は同一ボリュームのハードリンクで準備する。出力先は新規ディレクトリのみとし、リンク後の資産を編集しない。
- Node24.15.0、esbuild0.25.12、Wrangler4.143.1。APIキー実入力・生成・保存は今回の確認対象外。既存のAPI移行残件は維持する。

## 公開記録

PR #159の2つのCloudflareチェックが成功し、`481044571f00276bca81d6bf50e411fb6e251583` へ統合。確定Git blob35入力から再生成したWorkerのSHA一致を確認し、中央ForDeployガードを通して公開した。初回Cloudflare versionは `de71230d-3bfd-4d1d-98d4-35150272c220`。公開元の別作業13ファイルと既存ステージを保全。

既存のAI相談用Chromeの認証済み画面で、PC1536px・390pxのブログ編集、390pxのブログ制作と指令室を確認。枠付きボタン、現在地、44px以上の高さ、折り返し、横はみ出しなし、記事一覧と制作への遷移を確認した。ブラウザの検証用幅指定は解除済み。

公開トップ・ニュース・ブログ・記事・faviconのSHA一致、旧記事の転送、health200・login200、未認証の管理画面303・管理API401を計12経路で確認。公開612資産は不変。今回の未完了はない。既存の保存先移行・実キー生成確認は別の残件として継続する。

最新の配備SHA・versionと工程証拠は登録公開元 `work/genspark-profile-edit/tmp/delivery/20261012-admin-submenu-buttons.json` および同名フォルダを参照。画面証拠は `live-desktop.png`、`live-mobile.png`、`live-ui.json`。プレビュー `http://127.0.0.1:4098/admin/blog-editor` は親PID56760、10月14日02:01:28 JST終了予定。手動worktreeはこのプレビューと証拠のため保持し、停止後に固有ファイルを確認して整理する。

確認対象: https://aiclimb.aiclimb.workers.dev/admin/blog-editor

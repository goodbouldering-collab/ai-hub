# 管理画面の直下整理とCloudflare移行

更新: 2026-10-11。管理UI・原文閲覧の本番確認済み。共有保存等のAPI移行は残件として継続。

管理ホームから全機能を直接開く。ブログ制作は `/admin/blog-create`、リールは `/admin/reel`、記事編集は `/admin/blog-editor`、相場は `/admin/market`、運用記録は `/admin/ops`。旧URLは認証後に転送し、クエリを保持する。内部資料も `/admin/daily-operation` 等へ移動。原文は `/admin/document?file=...`、収集記事は `/admin/watch?path=...` を使う。

`deployment/admin-workspace/routes.mjs` を入口・旧URL・表示切替の共通台帳とする。ヘッダーだけでなく本文、フォーム、ボタン、カード、サブメニューを共通テーマへ統一。既存エディターのID・JavaScriptと認証・キー保存は維持する。制作アプリのCSS/moduleは従来の保護されたasset URLで読み、画面URLだけを直下へ整理する。

未配信だった指令室の各画面、SNS/チャット画面、運用本部をWorkerへ組み込んだ。運用原文148件と保存時点の活動記録は認証の内側で閲覧できる。原文1件は資格情報に似た文字列の自動検出で今回の配信から除外。元ファイルは変更せず、値を記録・送信していない。実秘密かどうかは未確認で、確認後に内容を整理して移行する。

ブログ・リールの事業プロフィール読込を同一Workerへ移し、外部プロフィール取得失敗で初期化が止まる問題を解消する。生成・キー保存の実行結果は別検証とする。

## 未完了の機能

- 予定・タスク・指示・プロンプトの共有保存と同期APIは未移行。UIと資料閲覧の移行を、バックエンド完了と混同しない。
- SNS実投稿、AIチャット、分析更新APIの移行・接続も残る。旧503を認証付きの具体的な未完了応答に変更し、偽の成功やデータ0件として表示しない。
- R2画像保存・外部記事公開・生成キーの接続は `/admin/migration` で設定有無と未検証を区別する。秘密設定、DBデータ、DNS、外部サービスへの投稿は変更していない。

## 再生成・検証

```powershell
node scripts/build-admin-workspace-assets.mjs
npx --yes esbuild@0.25.12 deployment/admin-workspace/worker.mjs --bundle --format=esm --platform=node --outfile=deployment/admin-workspace/published-worker.mjs
node --test deployment/admin-workspace/worker.test.mjs deployment/admin-workspace/routes.test.mjs
npm --prefix cloudflare-runtime test
```

公開前の基準は登録元 `.diagnosis-above-blog-20261011-final/public` の600ファイル。`flat-release-baseline.json` の全SHAと照合し、確定統合SHAのGit blobから `build_admin_flat_release.mjs` で生成する。公開HTML・画像・記事・SEO・ニュース配置を変更しない。登録元の台帳設定とForDeployガードを使う。

実績・残件の証拠: 登録元 `tmp/delivery/20261011-admin-flat-cloudflare/` と同名JSON。JevにはURL変換コードと合成データのテストだけを送り、原文・秘密値は送らない。正確性6.4→7.7、互換性7.1→8.2。通常テストと画面確認を完了条件とする。

## 本番検証と引継ぎ

PR #143を統合後、文書追補を含むmain `f36684208334f47e9839da5ff7b7a125413ff874` から配備。初回version `0f674cb9-3080-45d6-917d-91ca19aec0ce`。管理・認証・ルート・資料・既存制作10件とCloudflare7件のテスト成功。Node24.15.0、esbuild0.25.12、Wrangler4.90.0を使用。確定Git blob188入力からの再生成でWorker SHA256 `6573af7470b8e4b8fc6a887c47b5fd5dd8c8b82c5aaebfb839428922b4e6fade` が一致した。

既存の事業Chrome（browser 3）でログイン済みセッションを再利用し、33画面を1440px/390pxで確認。各画面の共通ヘッダー1個・横はみ出しなし・共通titleを照合。旧記事編集URLはslugを保持して直下へ転送。原文148件の読込、日付検索、直下の原文ビューア、旧 `/watch/2026-04-11.html` から `/admin/watch?path=2026-04-11.html` への転送と本文を確認した。公開トップ・ブログ一覧・既存記事・ニュースは従来SHAと一致。health/loginは200、認証なしの管理画面は303、資料/APIは401。外部投稿・生成・キー保存は実行していない。

登録元の既存ステージ差分をバイト一致で保持。その他の変更ファイル13件をhash照合し、Present.mdは三者マージで保持。最終配備SHA/versionと完了検査は登録元 `tmp/delivery/20261011-admin-flat-cloudflare.json`、HTTP・Chrome・公開元保全の証拠は同名ディレクトリに保存。公開URL: https://aiclimb.aiclimb.workers.dev/admin 。

次は `/admin/migration` の未接続項目について、既存データの移行元・保存先binding・秘密設定の有無を照合し、共有保存/同期APIから進める。原文の除外1件は安全な内容整理後に別途移行する。ローカルプレビューは127.0.0.1:4078、親PID58292、2026-10-13 20:31:37 JST終了予定。隔離worktreeはこのプレビューと検証証拠の保持のため残す。

並行作業PR #145のサロン表示順変更後、最終配備のbaseline契約を `.salon-menu-last-20261011-final/public`（source `6df9fa68d49dbe14311c6e07e29042016efb0f26`）へ更新。管理WorkerのコードとSHAは不変で、後続公開の600資産も保持する。

# 管理画面の直下整理とCloudflare移行

更新: 2026-10-11。実装・ローカル検証中。公開結果は工程記録で更新する。

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

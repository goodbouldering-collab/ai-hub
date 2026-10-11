# OpenAI APIキー設定の案内

更新: 2026-10-12。管理ページの表示とローカル検証が完了。Git統合・公開はこの後に実施する。

対象は `/admin/blog-create` の「接続設定」と `/admin/reel` の共通APIキー設定。見出し、公式キー発行URL、発行手順、入力・保存、状態表示の順に整理する。PCは2列、スマートフォンは1列。発行先は別タブで開き、管理画面に戻ってキーを保存できる。

- 公式根拠: [OpenAI quickstart](https://developers.openai.com/api/docs/quickstart#create-and-export-an-api-key) の「Create an API Key」リンクから [キー発行画面](https://platform.openai.com/api-keys) を確認。
- 変更は2画面のHTMLと管理共通テーマ、そこから再生成するWorker。入力・保存・削除・状態表示の既存ID、認証と暗号化保存APIは保持する。
- キーや資格情報は取得・発行・変更しない。今回の検証は表示、外部リンク、既存の合成データによる認証・保存テスト。実キー保存・生成の動作確認は引き続き未実施。
- 管理専用画面のため計測タグ追加は対象外。既存の公開612資産、記事・ニュース・申込先は維持する。

再生成: `node scripts/build-my-workflows-assets.mjs` → esbuild 0.25.12で `deployment/my-workflows/worker.mjs` と `deployment/admin-workspace/worker.mjs` をそれぞれ既存のpublished-worker.mjsへbundle。

検証: `node --test deployment/admin-workspace/worker.test.mjs deployment/admin-workspace/routes.test.mjs deployment/my-workflows/worker.test.mjs`、`npm --prefix cloudflare-runtime test`、`node .github/scripts/check-cloudflare-deployment.mjs`。公式公開元は中央台帳の `work/genspark-profile-edit/cloudflare-runtime`、TargetKey `default`。

工程記録: 登録元 `tmp/delivery/20261012-openai-key-settings.json` と同名フォルダ。PR #149の公開基準 `.home-refresh-release-first/public` と612資産の全SHAを照合してから公開する。

検証結果: 管理・認証・キー保存の合成データテスト10件、Cloudflare7件、公開経路検査が成功。既存AI相談Chrome（browser 2）でPC1440px・スマートフォン390pxのブログ設定を確認し、横はみ出しなし、発行URLの表示、入力・保存・状態欄の縦並びを確認。リールにも同じ設定案内を表示。実キーの入力や保存は行っていない。

ローカル表示: http://127.0.0.1:4093/admin/blog-create 。読取専用・合成認証。親PID43120、終了予定2026-10-14 00:24:50 JST。検証用worktree `work/openai-key-settings-20261012` はプレビューと作業証拠のため保持する。

# OpenAI APIキー設定の案内

更新: 2026-10-12。管理ページの表示を本番へ公開し、ログイン済みChromeでPC・スマートフォンの画面確認済み。

対象は `/admin/blog-create` の「接続設定」と `/admin/reel` の共通APIキー設定。見出し、公式キー発行URL、発行手順、入力・保存、状態表示の順に整理する。PCは2列、スマートフォンは1列。発行先は別タブで開き、管理画面に戻ってキーを保存できる。

- 公式根拠: [OpenAI quickstart](https://developers.openai.com/api/docs/quickstart#create-and-export-an-api-key) の「Create an API Key」リンクから [キー発行画面](https://platform.openai.com/api-keys) を確認。
- 変更は2画面のHTMLと管理共通テーマ、そこから再生成するWorker。入力・保存・削除・状態表示の既存ID、認証と暗号化保存APIは保持する。
- キーや資格情報は取得・発行・変更しない。今回の検証は表示、外部リンク、既存の合成データによる認証・保存テスト。実キー保存・生成の動作確認は引き続き未実施。
- 管理専用画面のため計測タグ追加は対象外。既存の公開612資産、記事・ニュース・申込先は維持する。

再生成: `node scripts/build-my-workflows-assets.mjs` → esbuild 0.25.12で `deployment/my-workflows/worker.mjs` と `deployment/admin-workspace/worker.mjs` をそれぞれ既存のpublished-worker.mjsへbundle。

検証: `node --test deployment/admin-workspace/worker.test.mjs deployment/admin-workspace/routes.test.mjs deployment/my-workflows/worker.test.mjs`、`npm --prefix cloudflare-runtime test`、`node .github/scripts/check-cloudflare-deployment.mjs`。公式公開元は中央台帳の `work/genspark-profile-edit/cloudflare-runtime`、TargetKey `default`。

工程記録: 登録元 `tmp/delivery/20261012-openai-key-settings.json` と同名フォルダ。PR #149/#151の公開基準 `.home-refresh-release-final/public` と612資産の全SHAを照合して保持した。

検証結果: 管理・認証・キー保存の合成データテスト10件、Cloudflare7件、公開経路検査が成功。既存AI相談Chrome（browser 2）でPC1440px・スマートフォン390pxのブログ設定を確認し、横はみ出しなし、発行URLの表示、入力・保存・状態欄の縦並びを確認。リールにも同じ設定案内を表示。実キーの入力や保存は行っていない。

ローカル表示: http://127.0.0.1:4093/admin/blog-create 。読取専用・合成認証。親PID43120、終了予定2026-10-14 00:24:50 JST。検証用worktree `work/openai-key-settings-20261012` はプレビューと作業証拠のため保持する。

## 公開・本番確認

- 実装PR #150を統合。初回配備SHA `fe22d4734fa66aae1aebe46299be2759df980e92`、Cloudflare version `92ebba98-e724-4511-a43b-2ed28e83a8a3`。台帳のworkingDirectoryでForDeployガードを通過。
- コミット済み30入力からUIと2段のWorkerを再生成し、Git blobとSHAが一致。最終Worker SHA256 `5e880e7aeebe0fbb64756d8ff240f7b4a9f98c93d0cd2c05c6c160ec1bf78fc2`。公開612資産は変更なし。Node24.15.0、esbuild0.25.12、Wrangler4.143.1。
- 本番ブログとリールでPC・390px表示を確認。横はみ出しなし、スマートフォンは1列、入力欄・保存ボタン・状態表示を確認。公式リンクのクリックで `https://platform.openai.com/api-keys` が別タブに開く。キー発行や保存操作はしていない。
- HTTP12経路を確認。トップ、ニュース、ブログ、既存記事、faviconのSHA一致。旧記事.htmlは既存どおり307、管理画面は未認証303、管理APIは401。healthとloginは200。
- 登録公開元の別作業13ファイルとステージ済み差分をバイト照合して保全。Present.mdは三者マージ。今回変更した管理UI以外のAPI・公開本文・記事画像は保持する。
- 本文書の統合後の最終配備SHA・version・機械検査は工程JSONを参照。画面・HTTP・再生成・保全の証拠も同名フォルダに保存。

次の作業: 実キー保存・再訪・生成の確認は今回の表示改善から分離した既存の残件。このデザイン変更の表示・リンクに残件なし。

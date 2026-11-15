# みんなのWA実績更新と公開元の固定（2026-11-15）

既存minanowaカード1件の画像と技術表記だけ更新。公開資産782件中index.htmlとimg/portfolio/minanowa.jpgの2件だけ変更、他780件（最新Codex記事・ブログ一覧・サイトマップを含む）は完全一致。

## 配備経路
通常Wranglerのassetsを古い.profile-release/publicから.current-release/publicへ変更。build.commandがscripts/prepare_current_release.mjsを実行し、deployment/current-release.jsonの全資産manifest、現行WorkerのGit正本hash、写真を照合して生成する。作成途中/既存出力が不一致なら上書きせず停止する。

基準はPR249 ea44742a由来の.codex-update-release-20261115/public。Workerはその旧runtimeを使わず、PR250のdeployment/meo-diagnosis/published-worker.mjs（SHA256 8fc4f305bfe8cb6c64c7a126983dd61ca73bd86001b019104e7b91ae3ae634a5）を保持。管理認証・既存binding・DBは変更なし。

配備時に本番トップ、AIニュース、ブログ一覧、サイトマップ、当該画像を読み、確認済み直前版または今回版と一致しなければ停止する。新しい日次記事を古いreleaseで巻き戻さない。別途Cloudflare正本ガードと現行Worker/binding照合を実施する。

## 次回の日次更新
site/templates/ai-news/home.htmlにも同一カード更新を反映し、content/ai-news/release-baseline.jsonは今回782資産へ更新済み。日次buildの--base-assetsは今回の.current-release/publicを使う。日次内容を更新して配備する際はdeployment/current-release.jsonを最新の検証済み本番基準へリベースし、次の候補manifestを記録する。旧profile-releaseを再使用したり、buildの本番照合を無効化しない。基準ディレクトリはmanifest照合済みの保存資産であり、無検証のdirty publicから作らない。

## 検証
Python関連63件、Cloudflare7件、巻戻り防止3件成功。今回資産から既存日次ビルドを再実行し、782件全hash一致を確認。ローカル環境の不足依存をtmp/python-depsに補充、最初の実行失敗を解消済み。公開記録は登録元tmp/delivery/20261115-portfolio-release-preserve-news.json。統合・配備結果と画面証拠は同記録で追跡。

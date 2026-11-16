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

## 3枚ヒーローへの更新（2026-11-15）
みんなのWA PR102/ceed1398の本番PC画像を既存minanowa画像へ差替え。登録名・URL・slug・techは保持。画像SHA256は3e205377660d96591b96a976502da426105d752691c054f9db898a09d3d369fa。キャッシュキー20261115-scenesを公開カード・日次テンプレ・限定生成関数で統一。
基準はPR251/525097e6の782資産を検証して保存した.codex-update-release-20261115-portfolio/public。今回公開差分は画像とトップの2件だけ、他780資産およびWorker8fc4f305は不変。既存12試験・巻戻り防止3試験と本番5URL照合成功。今回の工程記録はtmp/delivery/20261115-minanowa-scenes.json。公開実績はその記録で追跡する。

## 2026-11-17 みんなのWA v4実績画像
本番PCキャプチャで既存minanowa画像1件を更新。公開差分はトップのキャッシュキーと画像の2件のみ、最新記事を含む他780資産・Workerを維持。PR252現行資産782件と本番5URLを再照合してから基準化。検証・統合・公開の記録: tmp/delivery/20261117-minanowa-v4.json。

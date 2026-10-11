# ブログ直下のAIニュース

対象: https://aiclimb.aiclimb.workers.dev/ 。既存の「今日のAIニュース5とCodex」をブログの直下へ配置し、ブログと同じ文字色、見出しサイズ、細い区切り線、緑の「もっと見る」に整える。

本文、更新日、トップのニュース3見出し、詳細のニュース5件とCodex、ブログ3件、講習、診断、管理、日次更新は保持する。`core/editorial_feed.py` の生成順序とホームに限定したCSSを変更する。詳細ページのデザインは変更しない。

## 検証

- Python34件、Cloudflare7件、既存の `verify_ai_news_feature.py` 成功。
- PR #137の独立事業修正版（本番ホームのハッシュ一致を確認）の600資産とWorkerをハッシュ検査。`scripts/build_news_layout_release.py` がindex.htmlだけを変更し、599資産・Workerの一致、移動したブログとニュースの内容一致、その他のHTMLのバイト一致、再生成の冪等性を確認する。
- アプリ内ブラウザで1440pxと390pxを検証。横はみ出しなし。「もっと見る」からニュース5件とCodex詳細への遷移成功。既存Chromeタブは接続が応答せず、再選択後も同じため代替経路を使用。
- Jevは自動承認審査により外部への未公開コード送信が拒否されたため未実施。ローカル検証と差分点検を実施した。
- 作業用Pythonの一時依存は事業ルートtmp/news-layout-deps。既存venvは旧PCのPythonを参照するため使用不可。設定・依存ファイルの変更はしていない。

## 公開

本番公開・画面確認済み。PR [#138](https://github.com/goodbouldering-collab/ai-hub/pull/138) を統合し、公開SHA `44e290c294797fc645da1bfae14ae5e939c41c60` の7入力をGit blobから抽出して再生成した。登録公開元 `work/genspark-profile-edit/cloudflare-runtime` で中央ForDeployガードを通し、Wrangler4.143.1でWorker `aiclimb` のindex.htmlだけを更新した。Cloudflare version `23a1118f-f132-44f4-84d0-608a3e506c84`。

公開資産は登録元 `.news-below-blog-20261011-final`、入力スナップショットは `.news-below-blog-20261011-source`。直前のPR #137の公開版とホームのSHA一致を確認してから生成・公開した。599資産とWorkerを保持し、登録元の別作業17ファイル・ステージ済み差分も保全した。

本番ホーム、ニュース詳細、ブログ一覧は公開資産とのSHA一致を確認。health200、admin/login200、admin303、認証なしAPI401、旧記事URLから正規URLへの転送も確認した。PC1440pxとスマートフォン390pxの実画面でブログ→ニュース順、横はみ出しなし、ニュース5件とCodexへの遷移、モバイルメニュー開閉を検証。詳細ページや管理APIの変更はない。

今回の工程記録: 事業ルート `tmp/delivery/20261011-news-below-blog.json`。Git/PR/証拠/本番応答検査は `DELIVERY_VERIFIED`。証拠: 登録元 `tmp/delivery/20261011-news-below-blog/` のdeploy.txt、live-feature.txt、live-http.json、live-browser.json、live-desktop.png、live-mobile.png。文書の事後更新は別の文書PRで共有し、公開SHAを変更しない。

プレビュー http://127.0.0.1:4036/ 、起動時親PID26044、2026-10-13 19:44:35 JST終了予定。今回の依頼の残件なし。既存の管理認証やGoogle設定など他作業の未完了事項は、その作業記録を継続する。

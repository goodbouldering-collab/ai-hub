# ブログ直下のAIニュース

対象: https://aiclimb.aiclimb.workers.dev/ 。既存の「今日のAIニュース5とCodex」をブログの直下へ配置し、ブログと同じ文字色、見出しサイズ、細い区切り線、緑の「もっと見る」に整える。

本文、更新日、トップのニュース3見出し、詳細のニュース5件とCodex、ブログ3件、講習、診断、管理、日次更新は保持する。`core/editorial_feed.py` の生成順序とホームに限定したCSSを変更する。詳細ページのデザインは変更しない。

## 検証

- Python32件、Cloudflare7件、既存の `verify_ai_news_feature.py` 成功。
- 公開済みSEO版の600資産とWorkerをハッシュ検査。`scripts/build_news_layout_release.py` がindex.htmlだけを変更し、599資産・Workerの一致、移動したブログとニュースの内容一致、その他のHTMLのバイト一致、再生成の冪等性を確認する。
- アプリ内ブラウザで1440pxと390pxを検証。横はみ出しなし。「もっと見る」からニュース5件とCodex詳細への遷移成功。既存Chromeタブは接続が応答せず、再選択後も同じため代替経路を使用。
- Jevは自動承認審査により外部への未公開コード送信が拒否されたため未実施。ローカル検証と差分点検を実施した。
- 作業用Pythonの一時依存は事業ルートtmp/news-layout-deps。既存venvは旧PCのPythonを参照するため使用不可。設定・依存ファイルの変更はしていない。

## 公開

現在はローカル検証済み、公開前。登録公開元は `work/genspark-profile-edit/cloudflare-runtime`、target `default`、Worker `aiclimb`。統合SHAの入力だけを新規出力へ再生成し、中央ForDeployガードを通す。

今回の工程記録: 事業ルート `tmp/delivery/20261011-news-below-blog.json`。証拠: `tmp/news-below-blog/evidence/`。プレビュー http://127.0.0.1:4036/ 、起動時親PID26044、2026-10-13 19:44:35 JST終了予定。

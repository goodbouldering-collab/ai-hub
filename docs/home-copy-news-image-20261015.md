# トップ文言とニュース画像 2026-10-15

## 変更

トップの案内文末尾を「AI対応サイトの作成も可能。」へ変更。AIニュースを通常記事と同じ画像・タイトルの行にする。既存 practice.webp を利用し、共通のPC160px・スマホ96px列をそのまま使う。特定ビューポートだけの変更ではない。ブログ一覧にも適用。記事本文・日付・ニュース4件・Codex本文は保持する。

core/hero_copy.py と site/build_portal.py、保存テンプレートで文言を保持。core/editorial_feed.py と config/editorial-feed.json、共通CSSで一覧画像を生成する。

## 検証と公開

Python17件、Cloudflare7件、公開経路検査成功。IAB834px/390pxで画像読込・通常記事との寸法一致・横はみ出しなしを確認。通常Chromeは接続一覧になく、IABを利用。

scripts/build_home_annotation_release.py が固定baseline全624資産を照合し、index.htmlとblog/index.htmlだけを変更する。残る622資産と管理WorkerのSHA256は不変。生成は冪等。

公開前時点の記録。本番工程の確定結果（PR、統合SHA、公開version、画面・API検証）は登録公開元 D:/Project/AI相談/work/genspark-profile-edit/tmp/delivery/20261015-home-copy-news-image.json と同名証拠フォルダを正本とする。未完了工程を公開済みと扱わない。

確認URL: https://aiclimb.aiclimb.workers.dev/ と /blog/ と /ai-news/。

ローカル候補 http://127.0.0.1:4102/ は親PID51060、2026-10-17 05:28:39 +09:00まで（再起動・異常終了を除く）。Python3.12、Node24.15.0。公開後の次の作業は確定manifestを次回baselineとして照合すること。

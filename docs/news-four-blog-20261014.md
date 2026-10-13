# AIニュース4・ブログ形式への変更

2026-10-14。ユーザー指定に従い5件から4件へ変更し、写真をなくしてブログ一覧へ統合。

トップは専用ニュース枠を廃し、通常記事と同じ行構造・見出し・日付・区切り線を使用。ニュース行に写真列を設けず、詳細ページのニュース/Codex写真も除去。通常ブログの写真、講習7メニュー、Square同期内容、詳細URLと旧URLの301を維持する。

既存の編集順に先頭4件を採用。5件目のMicrosoft Maia 300は今回の表示対象から外すがGit履歴に保持。新しいニュース調査やCodex本文更新は行わず、既存4記事の本文・出典・日付とCodex Markdown本文の一致を確認。4件が揃わない日次更新は前回正常版を維持する。

基準は f52a30bc と登録元 .square-menu-release-20261014-final/public の616資産。トップ/ブログ/ニュースの本番SHAを照合済み。候補はindex.html、blog/index.html、ai-news/index.htmlのみ変更、613資産と管理Workerは不変。

Python26件、Cloudflare7件、通常再生成と限定再生成のverify_ai_news_featureが成功。IABのPC1440pxとスマホ390pxで表示・写真除去・横はみ出しなしを確認。Chromeは既存AI相談タブを確認し、直前作業の撮影障害により画面検証はIABを使用。

PR #176統合、本番反映・確認済み。初回公開SHA `a1d94ab9`、Cloudflare version `a6a98b88-af03-4f4b-9306-225c0afc8e1c`。4公開資産SHA一致、health200／admin303／ping401、本番IABのPC1440px・スマホ390pxで4件・写真なし・ブログからの遷移・横はみ出しなしを確認。工程記録: 登録元 tmp/delivery/20261014-news-four-blog.json。プレビュー http://127.0.0.1:4016/ 、親PID1704、終了予定2026-10-16 04:21:40 JST。プレビューのため作業コピーを保持する。

最終の記録統合SHAと配備versionは工程記録を参照。Node24.15.0／Python3.12.14／Wrangler4.127.1。公開入力は統合SHAのgit archiveから取り出し、既存dirty/stagedを混ぜず再生成。次回は本工程の最終release/verification.jsonを最新本番と照合する。Jevレビューは低重要度の一般的指摘のみで、具体的な追加変更根拠はなく、通常の検証結果を優先した。

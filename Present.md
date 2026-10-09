# AI相談の現在地

最終更新: 2026-10-09

AI講座・業務改善相談の案内、ブログ、制作実績を提供する。確認済み公開URLは https://aiclimb.aiclimb.workers.dev 。独自ドメイン未設定のため、このURLを使用する。公開先は共通Cloudflare台帳の `work/genspark-profile-edit/cloudflare-runtime`。事業ルートには別作業の差分があるため、一括同期しない。

今回の作業: 「その資料、毎回添付していませんか？ CodexとWorkers AIで減らせる手間」を公開・本番検証済み。承認稿と説明画像5点を掲載し、トップ・ブログ一覧・サイトマップを更新。具体的な相談案件と個人名は非掲載。

- 公開ソースSHA: `d3cb6fae41734f91e7716e5e1aaed26c793e9645`。PR https://github.com/goodbouldering-collab/ai-hub/pull/115 をmainへ統合。
- Cloudflare version: `f816955e-1b06-48f1-8db7-b1621ce3ab59`。Wrangler 4.143.1。登録公開元から新規6資産・既存3資産を反映、547資産とWorkerを保持。
- 検証: 記事・ホーム21テスト、Worker7テスト、SEO・ニュース構造・中央ForDeploy成功。本番12資産のSHA256一致、health 200・admin 303・未認証API 401。
- 画面: 許可されたCodex内ブラウザで1440px/390px表示、画像・メニュー・トップと一覧からの記事遷移を確認。横はみ出しなし。専用Chrome Profile 1は接続未確認。
- 公開URL: https://aiclimb.aiclimb.workers.dev/blog/2026-10-09-codex-workers-ai-workflow
- 記録: [記事公開記録](docs/blog/2026-10-09-codex-workers-ai/README.md)。ルート `tmp/delivery/20261009-codex-workers-ai-blog.json` は公開後の文書更新前に `DELIVERY_VERIFIED`。
- 残件・次回: 記事公開の残件なし。次回は `.codex-workers-ai-release-20261009/verification.json` を本番と照合してbaselineにする。制作worktreeはプレビュー親PID 47448（2026-10-11 13:08:01 JST終了予定）と検証証拠のため保持。別作業の未コミット差分は保全。

直前の公開: 10月9日版AIニュース5件とCodex公式週次（October 5–9, 2026）・CLI 0.162.0を公開・本番検証済み。ニュース・Codex本文、最新シェル、550ファイルのbaseline manifestを更新した。公開差分はトップ・独立ニュース・サイトマップの3ファイル、残り547ファイルとWorker・認証・API設定は同一。

- 公開ソースSHA: `2d3743e821288e9f26f2403afeadb2d355e28c9d`。PR https://github.com/goodbouldering-collab/ai-hub/pull/113 をmainへ統合。
- Cloudflare version: `364e48f9-b247-4290-9fb0-9cffa1bbd474`。Wrangler 4.143.1で既存bindingを保持。
- 検証: 51テスト・assets・中央ForDeploy・live成功。本番23資産のSHA256一致、旧3URLの301、ブログ除外、ヒーロー直下3見出し、未認証APIの401を確認。
- 画面: 専用Chrome Profile 1の接続は未確認。許可されたCodex内ブラウザでトップ・独立ページを1440px/390pxで確認し、横はみ出しなし、「もっと見る」の遷移成功。
- 公開URL: https://aiclimb.aiclimb.workers.dev/ai-news/ と https://aiclimb.aiclimb.workers.dev/ 。
- 証拠: `outputs/daily-20261009/production-summary.json`、`.daily-news-release-20261009/verification.json`。ルート `tmp/delivery/daily-ai-news-20261009.json` は文書更新前にDELIVERY_VERIFIED。
- 日次運用: PCとCodexアプリの既存処理で継続。baselineは上記の最新ブログ公開版を優先。別のGitHub定期ジョブは再開していない。

さらに前の公開履歴: ブログ冒頭のリール6記事を本文末尾へ移動した版。`site/build_site.py` の今後の出力順序も修正済みで、動画・画像・本文の内容を維持している。

- 実装: `core/blog_video_order.py`、`scripts/build_blog_reels_last_release.py`、`deployment/blog-reels-last.json`、記事原稿・表示順テスト。
- 検証: 記事テスト16件、Workerテスト7件成功。全550ファイルのハッシュを検証。
- 共有・公開: PR https://github.com/goodbouldering-collab/ai-hub/pull/111 をmainへ統合し、Cloudflareへ公開済み。
- 前回公開ソースSHA: `59173c7369e2615af5c912fa9df7c5a4119291c3`。
- 前回Workerバージョン: `91cb1628-ef35-4673-be08-29dcba4b16bc`。
- 公開成果物: `work/genspark-profile-edit/.blog-reels-last-20261009/verification.json`。
- 本番検証: 対象6記事とトップ・ブログ一覧がHTTP 200、配信内容のSHA256が成果物と一致。
- 代表URL: https://aiclimb.aiclimb.workers.dev/blog/2026-07-22-ai-site-publishing-stages.html
- 工程証拠: `work/genspark-profile-edit/tmp/delivery/20261009-blog-reels-last.json`。

実画面確認も完了。専用Chrome Profile 1の接続が利用できないため、2026-10-09本人指定の代替手順でCodex内ブラウザを使用。公開6記事のDOMで動画が本文の最後の表示要素となることを確認し、横長・縦長の代表2記事はスクロール後の画面でも確認した。公開閲覧のためサービスログインは不要。

今回のリール移動は公開・検証済み。`work/blog-reels-last-20261009` は検証証拠と別作業のAGENTS.md差分があり、証拠の保全整理まで保持。READMEの旧ホスティング記述だけから公開先を判断せず、共通台帳を参照する。他作業の未コミット差分・未解決事項は既存運用記録で継続管理する。

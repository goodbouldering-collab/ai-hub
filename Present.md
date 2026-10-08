# AI相談の現在地

最終更新: 2026-10-09

AI講座・業務改善相談の案内、ブログ、制作実績を提供する。確認済み公開URLは https://aiclimb.aiclimb.workers.dev 。独自ドメイン未設定のため、このURLを使用する。公開先は共通Cloudflare台帳の `work/genspark-profile-edit/cloudflare-runtime`。事業ルートには別作業の差分があるため、一括同期しない。

今回、ブログ冒頭のリール6記事を本文末尾へ移動した。`site/build_site.py` の今後の出力順序も修正。既存公開550ファイルを照合し、対象HTML6件だけを変更、残り544件とWorkerは同一。動画・画像・本文の内容を維持している。

- 実装: `core/blog_video_order.py`、`scripts/build_blog_reels_last_release.py`、`deployment/blog-reels-last.json`、記事原稿・表示順テスト。
- 検証: 記事テスト16件、Workerテスト7件成功。全550ファイルのハッシュを検証。
- 共有・公開: PR https://github.com/goodbouldering-collab/ai-hub/pull/111 をmainへ統合し、Cloudflareへ公開済み。
- 公開ソースSHA: `59173c7369e2615af5c912fa9df7c5a4119291c3`。
- Workerバージョン: `91cb1628-ef35-4673-be08-29dcba4b16bc`。
- 公開成果物: `work/genspark-profile-edit/.blog-reels-last-20261009/verification.json`。
- 本番検証: 対象6記事とトップ・ブログ一覧がHTTP 200、配信内容のSHA256が成果物と一致。
- 代表URL: https://aiclimb.aiclimb.workers.dev/blog/2026-07-22-ai-site-publishing-stages.html
- 工程証拠: `work/genspark-profile-edit/tmp/delivery/20261009-blog-reels-last.json`。

残課題は専用Chrome Profile 1での実画面確認。実在する `AI相談 - Chrome.lnk` は起動済みだが、操作ツールとの接続が確認できず、ユーザーへ接続を依頼済み。公開済み・HTML検証済みであり、画面検証済みとは扱わない。

次は接続後に本文末尾のリールを画面確認し、工程記録を完了する。`work/blog-reels-last-20261009` は検証証拠と未完了確認のため保持。READMEの旧ホスティング記述だけから公開先を判断せず、共通台帳を参照する。他作業の未コミット差分・未解決事項は既存運用記録で継続管理する。

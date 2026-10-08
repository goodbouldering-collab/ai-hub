# AI相談の現在地

最終更新: 2026-10-09

AI講座・業務改善相談の案内、ブログ、制作実績を提供する。確認済み公開URLは https://aiclimb.aiclimb.workers.dev 。独自ドメイン未設定のため、このURLを使用する。公開先は共通Cloudflare台帳の `work/genspark-profile-edit/cloudflare-runtime`。事業ルートには別作業の差分があるため、一括同期しない。

10月9日版AIニュース5件とCodex公式週次（October 5–9, 2026）・CLI 0.162.0の更新を作成し、ローカル検証済み。公開は下記の基準版から行う予定で、この記録時点では未実施。ニュース・Codex本文、最新シェル、550ファイルのbaseline manifestを更新した。候補の公開差分はトップ・独立ニュース・サイトマップの3ファイル、残り547ファイルとWorkerは同一。指定テスト51件とassets検証成功。記録は `outputs/daily-20261009/`、次はPR統合・確定SHAの再生成・中央ガード・公開と本番確認。

基準となる直前の正常公開版は、ブログ冒頭のリール6記事を本文末尾へ移動した版。`site/build_site.py` の今後の出力順序も修正済みで、動画・画像・本文の内容を維持している。

- 実装: `core/blog_video_order.py`、`scripts/build_blog_reels_last_release.py`、`deployment/blog-reels-last.json`、記事原稿・表示順テスト。
- 検証: 記事テスト16件、Workerテスト7件成功。全550ファイルのハッシュを検証。
- 共有・公開: PR https://github.com/goodbouldering-collab/ai-hub/pull/111 をmainへ統合し、Cloudflareへ公開済み。
- 公開ソースSHA: `59173c7369e2615af5c912fa9df7c5a4119291c3`。
- Workerバージョン: `91cb1628-ef35-4673-be08-29dcba4b16bc`。
- 公開成果物: `work/genspark-profile-edit/.blog-reels-last-20261009/verification.json`。
- 本番検証: 対象6記事とトップ・ブログ一覧がHTTP 200、配信内容のSHA256が成果物と一致。
- 代表URL: https://aiclimb.aiclimb.workers.dev/blog/2026-07-22-ai-site-publishing-stages.html
- 工程証拠: `work/genspark-profile-edit/tmp/delivery/20261009-blog-reels-last.json`。

実画面確認も完了。専用Chrome Profile 1の接続が利用できないため、2026-10-09本人指定の代替手順でCodex内ブラウザを使用。公開6記事のDOMで動画が本文の最後の表示要素となることを確認し、横長・縦長の代表2記事はスクロール後の画面でも確認した。公開閲覧のためサービスログインは不要。

今回のリール移動は公開・検証済み。`work/blog-reels-last-20261009` は検証証拠と別作業のAGENTS.md差分があり、証拠の保全整理まで保持。READMEの旧ホスティング記述だけから公開先を判断せず、共通台帳を参照する。他作業の未コミット差分・未解決事項は既存運用記録で継続管理する。

# 2026-10-25 Codex更新の公開準備

Codex CLI 0.164.0の依頼文保存、コマンド引数による設定、対応ターミナルの画像履歴、再開時設定復元を公式リリースに基づき編集した。初回公開日とOGPメタデータを保持し、ヒーロー画像・目次・初回公開日の表示は追加しない。

- 公式: https://github.com/openai/codex/releases/tag/rust-v0.164.0 と https://learn.chatgpt.com/docs/whats-new.md 。既存検証器が抽出するリンク付き週はOctober 5–9, 2026。新しい週の見出しを勝手にsource_periodへ代入せず、CLI最新安定版とのfingerprint差分を更新対象とした。
- 編集JSON: 事業outputs/daily-20261025/codex-editorial.json。--editorial-fileを指定し、既存の取得・fingerprint・update_articleを使用。追加API・Anthropicを実行していない。
- 基準: 登録公開元tmp/threads-social-release-20261025-final/public、source b3d808cbe8aa33743ffd85d31a0cab844926f38a。781資産manifestと本番5経路のハッシュを照合。最新SNS4件、録音記事、ニュース4件・ブログ内入口を保持。
- シェルとmanifestを直前正常版へ更新。トップの入口要約を既存ブログ一覧と同じ現行の説明へ統一。日次ニュース本文・dateは不変。候補差分はindex.html、ai-news/index.html、blog/index.html、sitemap.xmlの4資産で、777資産は不変。
- 検証: test_daily_ai_news 15件、test_codex_update_log_updater 32件成功。assets検証成功。現行4件仕様の合格であり、未承認5件仕様の合格ではない。
- 管理Worker: 本番GETとGit blobのSHA-256が78f655ae35822f27c7f6c9b575fc1881a339d5d43521b30611c24a7e701bb1bcで一致。認証/APIを変更しない。
- Vercel: 2026-10-25に読取専用connectorで接続チームとプロジェクトを確認。チーム1件・project0件。リポジトリの切断済み設定と照合。Vercel変更は実施しない。
- 公開前は候補。統合SHAの再生成、中央ガード、本番HTMLハッシュ、IAB画面検証を経て工程記録に実績を追記する。

日次ニュース5候補は別途outputs/daily-20261025/news-candidates.jsonへ保存。5件・独立入口と現行4件・ブログ入口の不一致が解消するまで公開ニュースを維持する。

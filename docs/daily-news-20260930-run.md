# AIニュース 2026-09-30

- 直近48時間の公式発表5件、5発表元・5URL。Anthropic Sonnet 5.5、NVIDIA安全基盤、ウェルモ介護記録、菩提樹AI番頭、GMO TECH店舗集客。発表日と提供・開催予定を区別、説明各65字以下。出典本文とHTTP200を日付別outputsへ保存。
- Codex公式の検証済みfetch/fingerprint/update_articleでCLI rust-v0.159.1へ更新。最新の週次期間はSeptember 21–25, 2026。fingerprint 82f032f6297f12fb050e27859c5e5e4f5bdea3e98f475fe31194a43e515a85d7。同梱・Bedrockカタログの既定モデル変更のみ記載。初回公開日・OGPを保持、前版を過去要約へ。
- 最新正常本番は登録元.home-updates-release-20260930/public、source49ef3e61、version1dc771fc-da76-4737-99a6-c64402bb39f8。全531manifest・主要9本番SHA一致。homeシェルとmanifest追随。
- 日次preserveモードが無関係なhome処理でCSS順序を変える問題を修正。通常のデザイン生成は保持。変更前531資産を完全再現し、更新後はトップ・ai-news・sitemapの3資産だけ変更、他528資産は不変。今朝のニュース/最新ブログ配置と講師ボタン削除を維持。
- test_daily_ai_news/test_codex_update_log_updater/test_ai_news_feature_build/test_home_updatesの53テスト、--assets、Git diff --check、Cloudflare policy検証に成功。
- GitHub hooks空、現在mainチェックはGitHub Actionsのみ、コミット済みdeployment-platform.jsonのVercel連携disconnectedと実行経路ガード成功を照合。Vercelの実行・変更はしない。別の定期ジョブは再開しない。
- 中央台帳の公開元work/genspark-profile-edit/cloudflare-runtimeからガードし、統合SHA再生成後に既存同一Workerで公開する。現行と前回検証版のWorker etag一致、bundle SHA f00d0e407205042faaee8f9cf4f269e5b8c9aa7eaec14e5396896c83fb75a0c3。
- 本番結果は登録元.daily-news-release-20260930/production-summary.jsonとoutputs/daily-20260930/へ保存。次回baselineは公開成功記録と実URLを照合して選ぶ。
- ブラウザ: DesktopのAI相談 - Chrome.lnk（Profile 1）を照合して起動。CUA接続1/3は他事業、profileNameなし。PC/iPhoneの目視・横はみ出し未確認。

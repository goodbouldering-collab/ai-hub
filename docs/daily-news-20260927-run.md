# 2026年9月27日 AIニュース・Codex更新

9月27日朝の直近48時間に発表された公式ニュース5件を選定。発表日は全件9月25日、発表元・URLは5種類、説明は各90字以内。提供日・開催日と発表日を区別。日本での活用案は編集者の見解。

Codexは検証済みfetch_source/fetch_latest_cli_release/digest_fingerprint/update_articleで週次September 21–25とrust-v0.157.1を照合。公式本文は変更要点を特定できていないため、新機能を推測せずその状態を記載。初回日・OGPを保持し、前回CURRENTを履歴へ保存。

最新正常公開版は登録元 `.restored-contextual-release-20260926/public`、統合SHA `689ffabf011346e27d796a80527eb0f8d032bf7e`、Cloudflare version `8b85400f-c609-45f3-b7fc-ad79ca72e081`。全515資産manifest、主要13資産の本番SHAを照合。最新写真・料金・ヒーロー・診断文をシェルに継承。

日次ビルダーがcompact CSSを末尾に移動する問題を修正し、適用順維持の回帰テストを追加。更新前の515資産はバイト一致。更新後の差分はトップ、独立ニュース、sitemapの3資産のみ。残り512資産、ブログ除外、3種類の301転送は保持。

Workerは最新本番本文と公開版compiled/public-entry.jsのSHA256 `f00d0e407205042faaee8f9cf4f269e5b8c9aa7eaec14e5396896c83fb75a0c3`、853926 bytes一致を確認。日次の保存bundleも同内容へ追随。認証/APIの別改修は行わない。

検証: 指定2群と資産保全を合わせ50テスト成功、verify_ai_news_feature.py --assets成功。Vercelチームの公式projects一覧は空、凍結対象のdeploy経路を追加していない。

調査証拠・候補・公開後記録は `outputs/daily-20260927/`。ジャストシステム公式ページはWeb取得で本文・日付を確認し、Python側の旧TLS互換エラーを記録（証明書検証は変更しない）。ブラウザはリクエストヘッダーポリシー取得エラーにより接続未確認。

公開時は統合SHAと台帳登録元HEADを一致させ、同SHAで再生成、中央ガード、同一Worker配備、--liveとHTMLハッシュ照合を行う。結果は登録元 `.daily-news-release-20260927/production-summary.json` に保存する。公開前の本書だけを本番完了証拠にしない。

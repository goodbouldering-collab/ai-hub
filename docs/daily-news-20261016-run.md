# 2026-10-16 Codex更新と日次ニュースの保留

Codex公式安定版0.163.0（2026-10-15 21:30 UTC公開）を検証済みfetch/fingerprint/update_articleで更新。週次はOctober 5–9, 2026。設定検索・返答中の追加指示・起点キー・Windows貼り付けを紹介し、0.162.1を過去要約へ移した。初回公開日、OGP、ニュース本文は維持。

日次ニュースは本人指定の現行4件・ブログ統合と定期5件・ブログ除外が衝突するため、10月16日の5候補をルートoutputs/daily-20261016/daily-ai-news.proposed.jsonへ保存し公開しない。現行ニュース日付10月13日を保持。Codex更新は独立して進める。

直前正常公開版は登録元.operations-sections-release-20261015/public、source65711e6f、version2c721ba3、762資産。全manifest、本番4資産SHA、更新前再生成差分0を確認。.page-art-releaseの同762資産ともバイト一致。シェルは最新公開と再現一致のため変更不要。公開差分はトップ・独立ページ・ブログ一覧・sitemapの4資産だけ、他758資産と管理Workerは保持。

検証スクリプトの画像なし条件はPR182後の公開状態と不一致だったため、ホームとブログ一覧のニュース画像保持・一致を検証する条件へ更新。詳細ページの画像なし条件は維持。

47テスト、assets、Cloudflare policy、2CI、ForDeploy、dry-run成功。PR #192を統合し、公開元HEADと統合SHA `4bb2b282aadad29a964ae6a7851b5580c449d4a5` の一致を確認。72 Git blob入力をcore.autocrlf=falseで抽出して再生成し、候補762資産と全一致。commitは `48896f7ed2628fd714930a2dde047c75dbf6e73f`。

Cloudflare version `62dacca2-3600-4eec-9045-fc26ad8d961b`、deployment `2a5bbcb5-640a-4616-8c74-03a05d7012b8`、100%。既存Workerのetag/bindings/runtime不変。--live、9配信SHA、旧3URL301、health・旧記事200、adminログイン遷移後200、ping401成功。

Codexアプリ内ブラウザでPC1440×1000／iPhone390×844のトップニュース入口と詳細・Codex新内容、ニュース/Codex共通見出し30px/800、メニュー開閉、横はみ出しなしを確認。ニュースリンクの遷移を確認、viewport reset。正しい事業用Chromeは未接続のため、その経路の画面確認は未実施。別事業のChromeは使用していない。スクリーンショットはツール内で目視し、ローカル保存なし。

Codex分の工程検査は文書後続統合前にDELIVERY_VERIFIED成功。日次全体は仕様blockerを保持し未完了。10月15日付LINE WORKS、Sakana AI、リコー、IBM/CTC、レノボ（AI Watch報道）の5候補を保存。直近48時間、公式4件・専門報道1件、説明各90字以内。公開ニュース本文・日付は変更していない。

既存dirty/staged差分はバックアップと3方向統合で保持。公開した4資産以外、758資産と管理Workerを保持。次回baselineは `.codex-update-release-20261016/public` とverification.json/production-summary.json。現在の正常公開版と再照合して使う。

証拠は事業ルート `outputs/daily-20261016/README.md` と同日のJSON群。Codex工程記録は登録公開元 `tmp/delivery/20261016-daily-ai-news-codex-component.json`、全体保留記録は事業ルート `tmp/delivery/20261016-daily-ai-news.json`。文書だけの後続統合ではサイトを再デプロイしない。

# 2026-09-22 AIニュース日次更新

## 調査と原稿

日本時間9月22日朝、直近48時間（9月20日朝以降）の公式発表5件を採用。7日への拡大なし。つながりAIの高齢者支援、Huaweiの実践教育、リクエストの建設業AI教材、GotoAIのKari、Huaweiの通信設備運用。5URL、4発表元（Huaweiのみ2件）、全HTTP200、各説明最大64文字。日本での活用提案は編集者の見解として区別した。Kariの公表9/20と提供9/21を区別し、料金・対象端末は記載していない。

Codexは検証済みfetch_source/fetch_latest_cli_release/digest_fingerprint/update_articleでchanged=false。公式週次September 14–18, 2026、最新安定版rust-v0.155.1、fingerprint 9af1427bd9891c47f1a24793480e2beb4579e25eaf84b6f5da587710bc40bf7d。CURRENT、過去要約、date_modified=2026-09-19、初回日、OGPをバイト一致で維持。

## 公開基準と保全

現在本番のversion6060cf6d-4cc9-475c-bc5b-3d90642142e1、source69507375a65597f681cfa10a8c1d42cf23fd58f2をAPIで確認。最新正常版work/genspark-profile-edit/.daily-news-release-20260921/publicの全513資産manifest一致、本番主要13資産SHA一致、更新前再生成差分0。今回のmanifestをこの基準へ更新した。既存シェルは再生成一致を確認したためそのまま維持。

候補差分はindex.html、ai-news/index.html、sitemap.xmlの3資産のみ。他510資産不変、ブログ一覧・旧3URL301設定不変。ヒーロー直下の最新3見出しともっと見る、Instagram欄、人物イラスト、配色、共通H2書式を保持。

現行公開WorkerのAPI取得本文とdeployment/ai-news/published-worker.mjsはSHA256 baab871b7ffa55b70f49098d155bc7dfaad96cedb0fc5742334b9dbe9f305506、848871 bytesで一致。Worker/API/認証は変更しない。

## 検証と公開手順

指定test_daily_ai_news、test_codex_update_log_updater、test_ai_news_feature_build計48件成功。verify_ai_news_feature.py --assets成功。

Vercel公式チーム一覧とprojects=[]、.github/deployment-platform.jsonのgitIntegration=disconnected、有効Vercel deploy経路なしを確認。別GitHub定期ジョブは変更しない。専用worktreeからPR・チェック・main統合後、登録元をff-onlyで統合SHAに一致させ、コミット済み入力だけから再生成する。登録元既存10パスのindex/worktree diffとハッシュを更新前後に比較する。

中央台帳の登録cwd work/genspark-profile-edit/cloudflare-runtimeでForDeployガード後、既存設定・同一Worker・keep-varsを用い、確定成果物だけを配備する。本番--liveと主要13資産SHA照合の結果は登録元outputs/daily-20260922と.daily-news-release-20260922/production-summary.jsonへ保存する。

ブラウザ：デスクトップAI相談 - Chrome.lnkのProfile 1を確認。CUAにはChrome3/4/2が接続されているがprofileNameがなく専用プロフィールを照合できない。AI相談タブが存在するだけでは一致証明にならないため操作せず、PC/iPhone目視・横はみ出し・consoleは未確認。

## 証跡

outputs/daily-20260922/sources/に公式取得原文、HTTP結果を保存。baseline-live.json、baseline-rebuild-diff.json、codex-check.json、candidate-verification.json、asset-verification.json、tests.txt、worker-before.json、unrelated-before.json。

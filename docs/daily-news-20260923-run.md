# 2026-09-23 ニュース更新と省スペースUI

対象はトップのヒーロー直下と独立 `/ai-news/`。今朝公開されたcyber版の配色・画像・診断導線を保持し、ニュース入口を細い区切り線の行へ整理。本文はPCで2列、800px以下で1列とし、本文・出典を残して余白を縮小。調査範囲はキーボード操作可能なdetailsに収める。ニュースとCodexの大見出しは同じ指定を共有する。

## 調査

- 日本時間9月23日夜に直近48時間を調査。9月22〜23日の5発表元・5URLを選定。7日拡大なし。説明は各65字以下。
- ぽこぽ「ぽこフレ」開発（認識範囲・一部送信あり）、Uravation研修追加（実施9/21・発表9/23）、博士.com動画AI編集、ナレッジセンスのスライド改善予定、Huawei実践教育。提供済みと開発・改善予定を区別。
- 各原文を取得しHTTP200・発表日を照合。JSONの各URLが出典。原文とハッシュは `outputs/daily-20260923/sources/`。
- Codexは公式fetch_source・fetch_latest_cli_release・digest_fingerprint・update_articleを使用。September 21–25, 2026 / rust-v0.156.1 / fingerprint `24702815cac32ad06270a5d41df1c9deb0538ceacaadd68632abdb9b13432b7e`。Sol/Lunaの選択を更新し直前版を履歴へ。初回日・OGPを保持。価格数値や利用条件を推測しない。

## 公開基準と検証

- 登録公開元 `work/genspark-profile-edit` のmain `87a036f3f76f77f74512e535af7f7e24d1bb3817` から専用worktreeを作成。元ルート分岐mainと登録元の無関係10パスを保持。
- 最新正常版 `.editorial-release-cyber-20260923/public`、Cloudflare version `be631579-44ea-4c78-8bb1-550bf2b12ee0` を使用。513資産manifest一致、主要13資産の本番SHA一致。最新シェル取り込み後、変更前再生成は全513資産バイト一致。
- 候補差分はindex.html、ai-news/index.html、sitemap.xmlのみ。他510資産不変。ブログ除外・旧3URLの301を保持。
- Workerは今朝の公開compiled/public-entry.jsをdeployment/ai-news/published-worker.mjsへ同期。APIで取得した現行本文と848795bytes、SHA `fbc934d13a936b36487b99378b0b03267d39bed44efd9edbc01fd2837a09c50e` 一致。認証/API変更を加えない。
- 指定2スイートとasset保全スイート、翌日シェルのCSS重複防止を含む49テスト成功。`verify_ai_news_feature.py --assets`成功。
- Vercel公式チームprojects=[]、有効なVercel deploy workflowなし。既存の別定期ジョブは再開・変更しない。利用可能ラベルにcodex/codex-automationなし。
- 中央台帳の登録cwdでForDeploy成功。旧ルートcloudflare-runtimeから公開しない。

## 制限

- AI相談Chromeショートカットは存在するが、CUA接続のプロフィール名がなく照合できない。PC/iPhoneの目視・横はみ出しは未確認。HTTP/構造検証と区別する。
- JEVへビルドコードとCSSを送る処理は、内部ソースの外部送信に明示承認がないとして自動承認レビューに拒否された。再送せずローカルレビューと回帰テストで確認。送信予定引数はtask（省スペースUI要件）、files（builderとcompact.css）、repositoryContext（資産保全とテスト結果）。評価スコアなし。

公開工程のSHA、PR、ガード、配備ID、live検証、ハッシュ照合は登録元 `.daily-news-compact-release-20260923/production-summary.json` と `outputs/daily-20260923/`、ルート `tmp/delivery/daily-ai-news-20260923-compact.json` に記録する。成功前に本番反映済みとは扱わない。

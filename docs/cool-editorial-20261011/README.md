# 画像・診断ボタン・管理画面の整理

更新: 2026-10-11。本番反映済み。公開面を本番確認済み。管理画面の本番ログイン後確認のみ未完了。

- 案内用画像21点を、落ち着いた写実表現へ差し替え。白・チャコール・深い青、自然光、木と石の質感で統一。実在する講師写真・会場写真・実績スクリーンショット・記事本文の根拠画像は維持。
- トップの診断案内は「あなたのAI実力を試す」「サイトのAI対応を調べる」の2ボタンに集約。遷移先は既存の診断を継続。
- トップのブログ最新3件は画像・日付・タイトルだけ。ブログ一覧10記事には既存の要約を保持。
- 管理画面は巡波の共通メニューを参考に「ホーム／制作・発信／内部資料／運営・分析」の4区分に整理。相場・接続などの専門項目は折りたたみ、既存機能へのリンクを保持。
- 内部資料は運営・ブログ/リール制作・素材の使い分けの3手順書。検索・本文閲覧・Markdown保存が可能。既存セッション認証の内側で配信し、公開Static Assetsへ置かない。

## 制作とソース

画像は内蔵image_genで新規生成。人物と場面は架空のイメージ。採用した全プロンプト・ハッシュ・altは [artwork-manifest.json](artwork-manifest.json) と `config/photo-art.json` に記録。元PNGは事業ルート `assets/cool-editorial-20261011/`、配信用WebPは `site/static/design-system/studio/images/photo-20261011/`。21点、1536×1024、合計2,479,212 bytes。

公開面は `core/editorial_home.py`、`core/editorial_feed.py`、`core/diagnosis_copy.py`。日次生成でも同じ変換を適用し、既存CSSの順序を保持する。

管理画面は `deployment/admin-workspace/{worker,shell,pages}.mjs`。既存の公開済み `deployment/my-workflows/published-worker.mjs` を包み、API・認証・キー保存・既存編集画面を維持する。資料本文はpages.mjsで管理する。認証設定不調時は503で閉じ、未認証はログインへ戻す。

```powershell
npx --yes esbuild@0.25.12 deployment/admin-workspace/worker.mjs --bundle --format=esm --platform=node --outfile=deployment/admin-workspace/published-worker.mjs
node --test deployment/admin-workspace/worker.test.mjs
python -B -X utf8 -m unittest tests.test_diagnosis_buttons tests.test_editorial_home tests.test_editorial_feed tests.test_home_updates tests.test_ai_news_feature_build tests.test_daily_ai_news tests.test_compact_home
npm --prefix cloudflare-runtime test
```

## 検証・公開の条件

Python44件・管理Worker4件・Cloudflare7件成功。管理テストはソースとbundle両方で実際の既存ログイン処理に仮資格情報を渡し、全資料・ダウンロードの認証、無効セッション、HEAD、404/405/503、公開ページと既存APIの維持を確認。

PC1440px・スマートフォン390pxの実Chromeでトップ、診断ボタン、管理ホーム、制作画面、資料検索と本文を確認。横はみ出しなし。ローカル用の仮認証で確認し、本番パスワード・キーの抽出や変更はしていない。本番のログイン後確認は本人の管理ログイン待ち。

Jev外部レビューは自動承認レビューでコード送信を拒否されたため未実施。外部送信せずローカル検証で代替。

公開候補は10月11日版の検証済み `.daily-news-release-20261011-final/public` を `deployment/admin-workspace/release-baseline.json` 全577ファイルのSHA256と照合して生成する。`scripts/build_cool_editorial_release.py` に `--base-assets`、空の `--output`、`--source-sha` を渡す。変更はindex.html・blog/index.htmlの2件、画像21件追加、575件不変。ニュース・講習料金・申込リンク・記事本文と既存の別作業差分を混ぜない。

登録公開元 `C:/Project/AI相談/work/genspark-profile-edit/cloudflare-runtime` で統合SHAを確認し、Git blobから入力を抽出して再生成する。中央ForDeployガードの後、`wrangler-profile-release.jsonc` と新releaseのruntime・publicを明示して `--no-bundle --keep-vars` で公開する。設定のmainも新bundleを指す。日次更新の次の公開基準は今回の最終releaseに切り替える。

ローカルプレビュー: http://127.0.0.1:4034/ 。親PID26088、2026-10-13 12:34:17 JST終了予定。仮認証で実キー保存・外部生成・投稿は行わない。

## 公開結果

PR #131を統合し、SHA `c76e9014a2a1f5069398218c13ac495c02fe0d94` の38入力をGit blobから抽出して再生成。Worker再ビルドのSHA256一致、中央ForDeployガード成功。2026-10-11 12:48 JST、Wrangler4.143.1でWorker `aiclimb` へ公開。version `b315aad6-7bf5-4345-9baf-68d767a77045`、100%配信。

公開後29資産のSHA一致、health/login200、未認証7経路の保護を確認。PC1440px・iPhone390pxの既存Chromeで、新画像、引用のない一覧、2診断リンク、メニュー、横はみ出しなしを確認。

次回基準は登録元 `.cool-editorial-release-20261011-final/public`。`verification.json`、`tmp/delivery/20261011-cool-editorial-images/{live-http.json,browser.json,deploy.txt,integration.json}` に証拠。事業ルートの `tmp/delivery/20261011-cool-editorial-images.json` は、本番管理ログイン後の確認だけ `pending` / `DELIVERY_INCOMPLETE`。本人の通常ログイン後に管理ホーム・制作・内部資料の検索と保存を確認する。

今回の公開後記録は文書のみの更新で、公開コードの変更を含まない。Webの公開SHAは上記を維持する。

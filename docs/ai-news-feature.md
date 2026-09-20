# AIニュースとCodexの独立ページ

- 公開ページ: https://aiclimb.aiclimb.workers.dev/ai-news/
- トップ入口: ヒーロー直下の `#ai-news`。最新3件の見出しと「もっと見る」。
- ブログ一覧には掲載しない。旧 `/blog/codex-update-log`、`.html`、末尾スラッシュは301転送する。
- 初回公開日の表示は除去。ニュースとCodexの大見出しは同じ書式。

## 編集・日次更新

ニュースの正本は `content/daily-ai-news.json`、Codexの正本は
`content/ai-news/codex-update-log.md`。ブログディレクトリへ戻さない。
Codexは `scripts/update_codex_update_log.py` の公式取得・fingerprint・差分更新を使う。
ニュースの調査期間説明は JSON の `research_note` に保存する。
ニュース日付とCodex更新日は独立し、初回公開日・OGP・過去要約を保つ。

```powershell
python scripts/build_ai_news_feature.py --output outputs/ai-news-preview
python scripts/verify_ai_news_feature.py --assets outputs/ai-news-preview
```

公開中のレイアウトを保持するシェルは `site/templates/ai-news/`。
他のトップ改修を公開したときは、このシェルにも同じ変更を統合してから日次更新する。
古いシェルで最新のトップ・ブログ一覧を上書きしない。
ホーム・ブログ一覧・サイトマップのシェルは2026-09-13取得の公開版から採用。
今回の本文は2026-09-12のニュース。日付だけを進めない。

## コミットと公開

`C:/Project/docs/deployment-source-integrity.md` の順序を守る。
依頼対象をコミットし、正本のローカル main に統合してから、そのSHAで再ビルドする。
Vercel自動デプロイの停止を証明できないためGitHubへpushしない。

移管中の混在した `cloudflare-runtime/public` は配信入力に使わない。
前回公開版 `.daily-release-20260912/public` を
`content/ai-news/release-baseline.json` の全455ファイルのSHA256で照合し、
次のコマンドで新しい配信ディレクトリを作る。

```powershell
python scripts/build_ai_news_feature.py --base-assets cloudflare-runtime/.daily-release-20260912/public --output cloudflare-runtime/.ai-news-release-20260913/public
python scripts/prepare_ai_news_runtime.py --output cloudflare-runtime/.ai-news-release-20260913/runtime
```

この基準スナップショットは今回専用。次の日次更新では、直前の正常公開版を
新しい基準として取り込み、シェル・manifestを更新してコミットする。
配信差分はトップ、独立ページ、ブログ一覧、サイトマップ、転送設定の5ファイルだけ。

Workerは今回変更しない。`prepare_ai_news_runtime.py` は固定したGit基点と、
すでに公開済みのSEO静的配信・ログイン画面タイトルの差分だけから再現する。
元の未コミットWorkerファイルを配信入力に使わず、すべての再現コードを今回コミットする。
中央Wrangler設定は、コミットした `content/ai-news/runtime-config.jsonc` と完全一致を確認する。
再現Workerのバンドルと現在公開中のWorkerを照合し、不一致なら停止する。
認証情報は読み出し・複製せず、既存bindingを `--keep-vars` で保持する。

公開直前に台帳の `cloudflare-runtime` から中央ガードを通し、
同じディレクトリで再現Workerをscript引数、確定成果物をassets引数としてデプロイする。
公開後に `python scripts/verify_ai_news_feature.py --live` と配信SHAの照合を行う。
PC・iPhone幅の画面確認は、AI相談のChromeプロフィールを接続・照合できる場合に実施する。

## 今回の検証

生成HTMLでヒーロー直後の配置、見出しリンク3件、本文ニュース5件、
ブログ除外、日付行除去、H2共通書式、canonical、過去要約、目次なしを確認。
2026-09-13のツール一覧にはAI相談のプロフィールを確認できる接続がなく、
画面の目視確認は未実施。構造の検証と画面確認を区別する。

## 2026-09-14 日次更新の基準

最新正常公開版 `.news-compact-release-20260914/public`（source 6ee68a9、Version c5f1e8b4-73f6-4a28-b0db-3973b95a17cf）の463資産を現行manifestへ取り込んだ。
更新前の全資産再ビルド差分0、主要7資産の本番HTTPハッシュ一致を確認。現在のシェルは最新のコンパクトなニュース入口、共通テーマ、自己紹介改修を維持するため変更不要。
上記9月12日baselineのコマンドは初回移行の履歴。今回のbase-assetsは `.news-compact-release-20260914/public`、公開候補は `.daily-news-release-20260914/public` を使う。次回はその時点の直前正常版と本番を改めて照合する。
詳細: `docs/daily-news-20260914-run.md`。

## 2026-09-15 日次更新・公開元変更を検出

中央台帳のworkingDirectoryは `work/genspark-profile-edit/cloudflare-runtime`、configPathは同ディレクトリの `wrangler-profile-release.jsonc` へ変更された。旧 `cloudflare-runtime` でのForDeployガードは場所不一致で失敗する。旧公開手順を使わず、このタスクではデプロイを停止した。

最新正常版は `work/genspark-profile-edit/.profile-release/public`、Version `f61bacfd-ef9e-4a3a-b635-366afcafa5f9`、source `f61ff022171e9d8feb22a012ce0f40f6610a7f35`。全463資産と主要7資産の本番HTTPハッシュを照合した。manifestとhome/page/blogシェルをこの版へ更新し、別作業で公開されたプロフィールリンクを保持した。

ローカルmainには未公開のglassデザイン変更も含まれるため、日次だけの候補では以下を使う。この指定は検証済みbaselineが必須で、デザイン一括適用を省き、公開5ファイル以外の差分を拒否する。既定のデザインビルド動作は維持。

```powershell
python scripts/build_ai_news_feature.py --base-assets C:/Project/AI相談/work/genspark-profile-edit/.profile-release/public --output outputs/daily-20260915/candidate --preserve-baseline-presentation
python scripts/verify_ai_news_feature.py --assets outputs/daily-20260915/candidate
```

新しいシェルは公開済みの装飾・CSSを含む。homeは `{{AI_NEWS_FEATURE}}` を置換する形式。更新前再ビルドは463資産すべてバイト一致（トップのCRLFも保持）。9月15日候補はトップ・ニュース・サイトマップの3資産だけ変更。

再開には、登録公開元側へ日次ビルドの必要ソースを限定統合し、その正本ブランチ・HEAD・公開Workerとの一致を確認する必要がある。分岐したローカルmain全体や未公開glass変更を一括投入しない。最新台帳と本番を再確認し、ガード成功後のみ公開する。詳細は `docs/daily-news-20260915-run.md`。


## 2026-09-16 現行正本への日次機能の限定統合

GitHub main 5305e73と登録公開元が一致し、glassとAI教室画像が公開済みであることを確認。ローカル旧main全体は混ぜず、独立ニュースのコード・原稿・シェル・テストのみ限定統合した。

基準は登録公開元 `work/genspark-profile-edit/.glass-release/public`、Version 955d1282-9f75-4a02-856b-ccf92034bbe5、source 9731b48。463資産manifest一致、本番主要11資産ハッシュ一致、更新前再生成差分0。今回の候補はトップ・ニュース・サイトマップの3件だけ更新。

Workerの再ビルドでパスやバンドラ差を混ぜないため、既存公開バンドルを `deployment/ai-news/published-worker.mjs` としてコミットした。848125 bytes・SHA256 f8fe944c03900ade5ad50f89339c4a435ae79d67e0a0ae3be583a1151fa72782、Cloudflare APIと一致。中央設定のno_bundle=trueを使い、明示entry引数でこの同一Workerを配備する。認証値は読み出し・複製せずkeep-varsで既存bindingを保持。

手順：対象をGitHub mainへ統合し、登録公開元をff-onlyで同じSHAへ更新する。cleanな登録元から `scripts/build_ai_news_feature.py --base-assets .glass-release/public --output .daily-news-release-20260916/public --preserve-baseline-presentation` を実行する。登録cwd `work/genspark-profile-edit/cloudflare-runtime` で中央ForDeployガード成功後、登録 `wrangler-profile-release.jsonc` と明示entry `../deployment/ai-news/published-worker.mjs`、assets `../.daily-news-release-20260916/public` を使う。確定SHA再生成と候補全ハッシュ一致、Worker同一性、本番検証を記録する。

次回のbaselineは今回の正常公開版を再照合して採用する。旧9月12〜15日の基準を再利用しない。Vercel既存チームprojects空・旧project404・有効deploy経路なしを確認できたため今回はmainへのpushが可能。GitHubの別定期処理は設定を変更しない（Codex旧workflowは確認時点で既存active、daily digestはdisabled_manually）。詳細はdocs/daily-news-20260916-run.md。

9月16日の実行結果：Vercel経路・中央ガードは通過したが、自動承認レビューがGitHub mainへのpushを拒否したため未公開。上記手順は承認後の再開用。現行本番のニュースは9月14日版のまま。


## 2026-09-17 最新公開デザインを保持した日次候補

最新正常公開版は登録元の `.editorial-release-fluid-20260916/public`。
source `1a28cf5e4f67f9257f655a8790ba987a3f0dbb3a`、Cloudflare version
`16685c01-2f38-41a3-9d2c-7da45fc495a9`を現行APIで確認した。
全472資産manifestと本番主要11資産のSHA256一致、更新前の全資産再生成差分0を確認。
home/page/blog/sitemapシェルとmanifestはこの版へ更新済み。
9月12日・14日・15日の古いbaselineは今回使わない。

```powershell
python scripts/build_ai_news_feature.py --base-assets C:/Project/AI相談/work/genspark-profile-edit/.editorial-release-fluid-20260916/public --output outputs/daily-20260917/committed-candidate --preserve-baseline-presentation
python scripts/verify_ai_news_feature.py --assets outputs/daily-20260917/committed-candidate
```

公開候補はトップ・独立ページ・サイトマップの3資産のみ変更。他469資産はバイト一致。
Cloudflareから取得した現行Workerと `deployment/ai-news/published-worker.mjs` は
SHA256 `fb64c0aac7095ea29bc1e0a4b775e27ecb8b3c8a49eb0399ddd2dbfe0531617b`、848795 bytesで一致。
古いprofile/glassバンドルを使わない。登録cwdと設定は中央台帳に従い、公開の直前に再確認する。

9月16日の自動承認レビューは共有main統合と旧ブログ原稿の移動について追加の具体的承認を要求した。
今回も共有main・登録公開元・本番は変更せず、ローカル専用ブランチにレビュー可能な候補を保持する。
承認後は最新main・本番・Workerを再照合し、統合済みSHAと登録元HEADを一致させ、
そのSHAから再生成・中央ForDeployガード・公開・本番ハッシュ照合へ進む。
詳しくは `docs/daily-news-20260917-run.md`。


## 2026-09-18 最新正常公開版を基準にする

今回のbaselineは登録元 `.editorial-release-human-glass-20260918/public`、source 4d627efe、
version d45f0d92-4a8f-4264-bf57-7bbf3c316264。全477資産と本番12資産を照合し、更新前再生成差分0。
home/page/blog/sitemapシェルとmanifestを更新。Codexの簡素な冒頭も最新mainから維持する。
更新候補はトップ・ニュース・サイトマップの3資産のみで他474資産不変。
このbaselineも次回は再確認する。過去の固定baselineをそのまま使わない。

```powershell
python scripts/build_ai_news_feature.py --base-assets C:/Project/AI相談/work/genspark-profile-edit/.editorial-release-human-glass-20260918/public --output outputs/daily-20260918/committed-candidate --preserve-baseline-presentation
python scripts/verify_ai_news_feature.py --assets outputs/daily-20260918/committed-candidate
```

最新公開と同一のWorkerはdeployment/ai-news/published-worker.mjs。
現在は9月16日の自動承認レビュー拒否に伴う具体的承認待ちで、共有mainと本番は変更していない。
承認後は中央台帳の登録元で統合済みSHAへ一致させ、再生成・ガード・Worker照合を経て公開する。
詳細はdocs/daily-news-20260918-run.md、証跡はoutputs/daily-20260918/。


## 2026-09-19 最新正常公開版

基準は登録元 `.editorial-release-cloudflare-blog-20260919/public`、source 9d2ae3f、version a44d7d29-13ed-43d2-bf87-429fb088567b。
485資産manifest、本番12資産SHA、更新前差分0を確認。最新main37989bcの未公開soft studioを混ぜない。
home/page/blog/sitemapシェルとmanifest更新、ニュース候補は3資産のみ変更。
`--preserve-baseline-presentation`で生成し、公開前に最新本番との照合をやり直す。
Workerはdeployment/ai-news/published-worker.mjs、現行API取得本文と同一SHA。
共有main統合・公開は9/16自動承認レビュー拒否に対する具体的承認待ち。
記録docs/daily-news-20260919-run.md、証跡outputs/daily-20260919/。

## 2026-09-20 日次候補

最新本番version a44d7d29-13ed-43d2-bf87-429fb088567b（source 9d2ae3f）の正常公開版を再検証した。
基準は work/genspark-profile-edit/.editorial-release-cloudflare-blog-20260919/public、485資産manifest一致、主要12資産本番SHA一致、更新前再生成差分0。
シェルとmanifestはこの現行基準に追随する。2026-09-12の固定baselineは使用しない。
9月20日候補はトップ・独立ページ・サイトマップのみ変更。Instagram欄を保持してニュース入口をヒーロー直下へ配置。
台帳登録cwdの中央ガードは成功。共有main統合・公開は過去の自動承認レビュー拒否が未解消のため未実施。
記録: docs/daily-news-20260920-run.md。確定SHA再生成の証跡: outputs/daily-20260920/committed-build.json。

## 2026-09-21 日次更新

最新正常公開は9月20日の人物イラスト版（source bb8b554、version 4f1e68b3）。513資産を本番と照合してシェルとmanifestを更新。詳細はdaily-news-20260921-run.md。
前述の古いpush停止記録ではなく、今回の明示指示に従いPR・検証・統合・Cloudflare公開まで行う。Vercelチームprojects空とgitIntegration disconnectedを確認済み。
台帳登録cwdはwork/genspark-profile-edit/cloudflare-runtime。中央設定を変更せず、同一本番bundle deployment/ai-news/published-worker.mjs をscript引数、確定SHAから生成したassetsをassets引数に指定する。Worker/API/認証は変更しない。

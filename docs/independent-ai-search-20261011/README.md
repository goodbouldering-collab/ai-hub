# AI相談の独立事業情報・検索設定（2026-10-11）

## 連絡先整備の公開版

AI相談はクライミングコンサルとは独立した別事業。本人指定の公開電話080-3828-3985、〒522-0043 滋賀県彦根市小泉町34-8 2階を使用する。階数は[Notエステ公式アクセス案内](https://notesthe.com/company/access)とも照合したが、他事業の電話は流用しない。本人はAI相談の常設表示と来店対応を確認している。岡町12の講習会場とは区別する。

正規URL: https://aiclimb.aiclimb.workers.dev/ 。独自ドメイン未設定。PR #137で独立事業情報とGSCタグを公開し、PR #140で電話・階数を統一した。連絡先整備の公開SHAは `9798893e7d62f79684af3178229f33e850b2aa32`、Cloudflare versionは `e193c0f6-3d6c-419a-b50a-62bc460d0cf0`。登録公開元の `.ai-business-contact-20261011-final` がこの公開の600資産、同 `-source` が確定SHAの入力である。後続の配置変更・公開版はその作業記録で照合し、文書更新のために旧版を再配信しない。

## 実装・検証・保全

- 47公開ページのJSON-LD・canonical・GSCタグ・事業連絡先、robots/sitemap/llmsを整合。親組織の誤った関係を除去し、講師とAI相談の関係、既存料金・記事日付は保持。`config/search-presence.json` を公開事業情報の正本とする。
- 電話リンクはホーム運営欄のメール前に1行。本文ガードは同欄の指定された住所・電話だけを許可し、日次再生成を含め、その他の本文・画像・CSS・JavaScript・Worker変更を拒否する。
- 最新ニュース配置版PR #138の600資産を `deployment/search-presence/contact-baseline.json` に固定。今回の変更は47 HTMLの電話/住所schemaとホーム連絡先、llms.txtの48資産。残り552資産・ニュース配置・GSCタグ・robots・sitemap・llms-full・Workerは同一。
- Python58件、Cloudflare7件、管理Worker4件、構成チェックが成功。旧598資産・異なるWorker・既存出力の拒否も確認。統合済みSHAからの再生成600資産とWorkerは候補に完全一致した。
- 登録元17差分・ステージ内容・未公開JPC・事業ルートcheckoutを保全。中央公開先ガード後に公開し、初回fetch failedは同一成果物とガード再検査で再試行成功。51資産hash（変更48＋robots/sitemap/llms-full）、47正規URL、電話/階数/独立事業/GSC、旧資料URL転送、管理保護9経路、health・ログイン画面200はHTTP検証成功。既存事業用ChromeのPC1536pxと390×844pxで、公開フッターの2階住所とtel:+818038283985を確認。証拠は `tmp/independent-ai-search-20261011/live-contact-desktop.jpg` と `live-contact-mobile.jpg`。

検証: `tmp/independent-ai-search-20261011/contact-verify.txt`、`contact-comparison.json`。Git統合・確定生成・公開・HTTPの証拠: `work/genspark-profile-edit/tmp/delivery/20261011-ai-business-contact/`。候補のsource_shaラベルと本番公開SHAを混同しない。前回判断の履歴は[旧SEO記録](../seo-meo-20261011/README.md)、ニュース配置は[公開記録](../news-below-blog-20261011.md)を参照。

## Google側の結果

Search Consoleは承認済みアカウントで所有権確認に成功。サイトマップ送信は受付済みだが、最終再読込でも一覧には「取得できませんでした」・検出0が残る。20:05 JSTのGSC公開URL検査（sitemap.xml）ではクロール許可・ページ取得・登録許可が成功し、robots・47 URLのXMLも正常。サイトマップ処理は待ち、原因未特定であり、全47 URLの読込・登録成功とは扱わない。トップは既にインデックス登録済み。旧クロールのReview15件の無効警告は残るが、現行HTMLにReviewはない。更新後のトップへインデックス登録を1回リクエストし、優先クロールキュー受付を確認した（gsc-home-reindex-requested.jpg）。再送を連打しない。証拠は `gsc-ownership-confirmed.jpg`、`gsc-sitemap-submitted-pending.jpg`、`gsc-sitemap-live-fetch-success.jpg/.txt`。

前回クライミングコンサルのGBPへ追加したAI5サービス・説明・対応地域・予約リンクは復元完了。同一事業という旧判断は失効した。AI相談の新GBP（プロフィールID `8474055285715858305`）をITコンサルタントとして作成。名称・カテゴリ・住所・電話・Web・説明・5サービスの料金と説明を保存し、管理画面の再読込で照合した。予約設定は「オーナー確認を行って予約機能を設定しましょう」と表示され、動画確認後の残件になった。5サービスの料金・説明は再読込で照合済み（gbp-ai-services-saved.txt/jpg）。追加属性「実店舗の営業あり」「オンライン予約可」「要予約」も保存・再読込で照合した。営業時間は未確認のため入力をスキップし、管理UIは「営業時間不定で営業している」と表示する。実際の営業時間が確定したら整合させる。写真は未登録。

新GBPはGoogleの動画によるオーナー確認待ちで、確認済み・マップ一般公開済みとは扱わない。本人の現地操作は `tmp/independent-ai-search-20261011/gbp-video-handoff.md` にまとめた。Googleの撮影案内は「1〜2分」「屋外から」「事前録画不可」。撮影開始ボタンの画面まで確認し、記録は開始していない（gbp-ai-video-handoff.jpg）。非公開アカウント識別情報はGitへ保存しない。Wikidataは一致項目と独立した信頼できる出典を確認できず、未作成・sameAs未追加。検索順位の変化は未測定。

## 残件

本人の動画確認後に予約リンクを設定し、営業時間・実写写真の確定とサイトマップ処理結果を確認する。今回のGoogle画面証拠は `tmp/independent-ai-search-20261011/` に保存。既存の本番管理ログイン後の画面確認、実キー保存・再訪・生成、未公開JPC差分は継続する。画像刷新・2診断・ブログ引用削除・管理4メニュー・最新ニュース配置は保持した。

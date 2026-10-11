# AI相談の独立事業情報・Search Console整備（2026-10-11）

## 事業情報の根拠

本人回答により、AI相談はクライミングコンサルとは独立した別事業として扱う。前回SEO・MEO作業の同一事業という判断は失効した。所在地はNotエステと同じ〒522-0043 滋賀県彦根市小泉町34-8 2階、公開事業電話は本人指定の080-3828-3985。階数は[Notエステ公式アクセス案内](https://notesthe.com/company/access)でも照合した。Notエステの電話番号は流用しない。本人はAI相談の常設表示があり、この拠点で来店対応すると確認している。岡町12の講習会場とは区別する。

正規URLは https://aiclimb.aiclimb.workers.dev/ 。独自ドメインは未設定。管理画面・内部資料・顧客情報は公開検索対象へ含めない。

## 独立事業への訂正：公開済み

PR #137、SHA `1393e7ee24e8a0f0a7374d18e2faebdd48f6ddb6`、Cloudflare version `047680d8-076f-458c-b899-49d10f044f4d`。登録公開元 `.independent-ai-search-20261011-final` から配信した。47公開HTMLの独立事業JSON-LD・承認済みGSCタグと管理保護9経路はHTTP検証済み。

AI相談のProfessionalServiceから親組織関係とクライミングコンサルのOrganizationノードを除去し、由井辰美とAI相談の関係を維持。llmsの運営元をAI相談、ホームの運営表記を「AI相談（彦根）」へ訂正した。Python55件・Cloudflare7件・管理Worker4件・構成チェック成功。旧r2との差分は47 HTMLとllms.txtの48資産で、本文変更はホームの運営表記1箇所だった。

## 電話・階数の追補：公開前

`config/search-presence.json` のbusiness.telephoneとaddressを正本とし、JSON-LDの#business、llms、ホーム運営欄へ同じ情報を出力する。電話の表示は080-3828-3985、クリック先はtel:+818038283985、構造化データは+81-80-3828-3985。住所末尾へ2階を追加し、メールの前に電話リンク1行を置く。生成元と日次テンプレートも整合させる。

本文変更ガードはホームのsite-footer内の単一footer-napだけを対象に、既存の運営名訂正、指定された旧住所の置換と電話1行の追加を許可する。他の本文・画像・JavaScript・CSS・Workerの変更は拒否する。旧住所や電話の重複を許容せず、再処理で電話を増やさない。

並行統合されたPR #138のニュース配置を保持するため、SHA `44e290c294797fc645da1bfae14ae5e939c41c60`、version `23a1118f-f132-44f4-84d0-608a3e506c84` の `.news-below-blog-20261011-final` を新baselineにした。600資産・Worker・本番ホームhashを照合済み。`deployment/search-presence/contact-baseline.json` に全hashを固定し、旧598資産の基準は履歴として保持する。

候補と検証証拠は `tmp/independent-ai-search-20261011/contact-candidate/`、`contact-verify.txt`、`contact-comparison.json`。候補生成時のsource_shaは作業基点を表す未コミット版ラベルであり、公開SHAではない。公開時は今回の統合SHAのGit blobから再生成し、全600資産とWorkerの候補一致を確認する。Python回帰58件・Cloudflare7件・管理Worker4件・構成チェックが成功。最新baseline比48資産のみ更新し、552資産・Worker・ニュース配置・その他schema・GSCタグ・robots・sitemap・llms-fullを保持。実ポータル生成関数も電話と階数が一致し、旧598資産・異なるWorker・既存出力の拒否を確認した。

## Google側の状態

承認済みアカウントでSearch Consoleの所有権確認に成功した。サイトマップ送信は受付済みだが、一覧は「取得できませんでした」・検出0。20:05 JSTのGSC公開URL検査（sitemap.xml）は「クロール許可はい／ページ取得成功／登録許可はい」を確認。robots・47 URLのXMLも正常で、サイトマップ処理のみ待ち・原因未特定。再送を連打せず、Googleのサイトマップ読込成功やインデックス登録済みとは混同しない。証拠は `tmp/independent-ai-search-20261011/gsc-sitemap-live-fetch-success.jpg` と同名txt。非公開のアカウント識別情報はGitへ保存しない。

クライミングコンサルの既存GBPへ前回追加したAI5サービス・説明・対応地域・予約リンクは、本人承認に従って復元完了。別事業であるAI相談の情報を同じGBPへ戻さない。

AI相談の新規GBPはITコンサルタントとして登録手続きに到達し、Googleから動画による確認を要求されている。常設表示について一度自動承認審査で住所手順が止まったが、本人が「常設表示あり」と確認し、同じ正規UIから再開した。本人による動画確認が終わるまで、所有権確認済み・マップ一般公開済みとは扱わない。営業時間やその他の未確認情報を補わない。

Wikidataは同一項目と独立した信頼できる出典が未確認で、新規作成・sameAs追加をしない。実際のGoogle順位変化は未測定。

## 次の工程と保持する残件

今回分だけを検証・commit・push・PR・必須チェック・統合し、登録元の別作業差分を保全して再生成する。中央台帳の公開先ガード後に公開し、47正規URL、変更資産hash、住所・電話schemaとフッター、GSCタグ、llms、ニュース配置、旧受講資料URL、管理保護経路を確認する。

既存の本番管理ログイン後の画面確認、実キー保存・再訪・生成の未検証状態、未公開JPC差分は今回の検証で解消した扱いにしない。日次ニュース、画像刷新、2診断ボタン、ブログ引用の削除、管理4メニューを保持する。

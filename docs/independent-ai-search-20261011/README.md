# AI相談の独立事業情報・Search Console整備（2026-10-11）

## 今回の訂正

本人回答により、AI相談はクライミングコンサルとは独立した別事業として扱う。前回SEO・MEO作業の同一事業という判断は失効した。既存の住所、講師、連絡先、サービス料金を根拠なく変更せず、誤った事業関係だけを訂正する。

正規URLは https://aiclimb.aiclimb.workers.dev/ 。独自ドメインは未設定。管理画面・内部資料・顧客情報は公開検索対象へ含めない。

## 実装と検証

- `config/search-presence.json` から旧運営元設定を除去し、承認済みアカウントのSearch Console公開確認タグを設定。
- `core/search_presence.py` でAI相談のProfessionalServiceから親組織を除去し、クライミングコンサルのOrganizationノードを除去。由井辰美とAI相談の関係は維持する。
- ホームの運営表記1箇所だけを「AI相談（彦根）」へ変更。`site/build_portal.py` と日次用ホームテンプレートにも反映する。
- 検証ガードは、ホームのsite-footer内にある旧運営表記の完全一致1箇所だけを本文編集として許可する。それ以外の本文・画像・JavaScript・CSS・Workerの変更は従来どおり拒否する。
- `llms.txt` の運営元のみAI相談へ変更。`llms-full.txt`、robots、sitemapは現行公開r2と同一。
- Python回帰55件、Cloudflare7件、管理Worker4件が成功。Cloudflare構成チェックはPASS。既存のpartial_migration警告は継続し、台帳の登録公開元とガードを使用する。
- 固定baseline598資産から600資産の候補を生成。現行r2との差分48件は47公開HTMLの事業情報・確認タグとllms.txtで、残り552資産とWorkerは同一。本文変更はホームの1箇所に限定し、他の構造化データとheadタグを比較した。

候補: `tmp/independent-ai-search-20261011/candidate/`。候補のsource_shaは作業開始HEAD `aa855bd2e45b1ea354ac2c10c620dc5901c8167f` を示す未コミット版ラベルであり、公開SHAではない。公開時は今回の統合SHAのGit blobから再生成し、候補全600資産・Workerとのhash一致を確認する。

検証証拠: `tmp/independent-ai-search-20261011/verify.txt`、`comparison-r2.json`、`candidate/verification.json`。工程記録: `tmp/delivery/20261011-independent-ai-search.json`。

## Google側の状態

Search Consoleの所有権追加と確認タグ公開は本人承認済み。タグは実装・ローカル検証済みだが、Googleでの所有権確認とサイトマップ受付は未確認。承認済みアカウントで公開後に確認し、結果を記録する。非公開のアカウント識別情報はGitへ保存しない。

クライミングコンサルの既存GBPへ前回追加したAI相談情報は、本人承認により復元する。説明・地域・5サービス・予約リンクのUI復元は作業中であり、完了とは扱わない。

AI相談の新規GBPは未作成。実際の事業住所、固定看板、そこでの来客対応、顧客先への訪問対応の実態について本人回答を待つ。講習会場と事業所在地を混同せず、オンライン専業の場合や未確認の看板・営業時間を根拠に登録しない。Wikidataは同一項目と独立した信頼できる出典が未確認で、新規作成・sameAs追加をしない。

## 公開状態と次の工程

現在公開中のSEO版はSHA `364d7d0ee00d5aa64e8be191e471b807bb653812`、Cloudflare version `1561c92a-22d9-4e35-8cff-4331b94f64d5`。登録公開元は `work/genspark-profile-edit`、現行成果物は `.search-presence-release-20261011-r2-final`。今回の修正版はローカル検証済み・本番公開前。

今回分だけをcommit・push・PR・必須チェック・統合し、登録元の別作業差分を保全して再生成する。中央台帳の公開先ガード後にデプロイし、47正規URL、変更資産hash、確認タグ、独立事業schema、フッター、llms、旧受講資料URL、管理保護経路を確認する。Google所有権確認とサイトマップ送信の結果は別に記録する。

既存の本番管理ログイン後の画面確認、実キー保存・再訪・生成の未検証状態、未公開JPC差分は今回の検証で解消した扱いにしない。日次ニュース、画像刷新、2診断ボタン、ブログ引用の削除、管理4メニューは保持する。

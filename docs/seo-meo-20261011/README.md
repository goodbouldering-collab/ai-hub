# AI相談 SEO・MEO整備（2026-10-11）

## 目的と公開範囲

彦根・滋賀でAIの相談先や講習を探す人に、サービス、講師、運営元、申込先が正しく伝わる状態を作る。AI相談は公開フッターにある通りクライミングコンサルのサービスとして扱う。別のGoogleビジネスを重複作成しない。

確認済み公開URL: https://aiclimb.aiclimb.workers.dev/ 。独自ドメインは未設定。既存本文、画像、料金、申込先、管理機能は変更せず、公開済み598資産を基準に検索用メタデータを更新する。

## 実装

- `config/search-presence.json` を名称・住所・対応地域・講師・正規URLの設定元とする。
- `core/search_presence.py` がJSON-LDの事業、運営組織、人物、WebSite、記事、講座、パンくずの参照を整理する。ブログ一覧はCollectionPage、講師ページはProfilePageに補正。記事の日付・内容、既存Course/Offerの内容を保持し、伴走支援の月額と制作の最低価格をpriceSpecificationで明示する。創業者と断定する根拠のない関係は除去。
- canonicalを実際のリダイレクト後URLへ統一し、OG/Twitter画像・説明・URLを一致させる。管理画面・内部資料・watch・検証ページは検索対象へ混ぜない。
- sitemapは公開47ページのみ。lastmodは確認できた記事日付だけを採用し、全ページを当日更新扱いにしない。
- `llms.txt` は公開情報への案内、`llms-full.txt` は公開ページのタイトル・説明・URL一覧。非公開資料や管理情報は含めない。
- 日次ニュース生成の最後に同じ整備を適用し、再生成で設定が失われないようにする。
- Search Console確認タグの受入口は用意したが、所有権追加の実行時確認が未回答のため `google_site_verification: null`。タグ公開・所有権確認・サイトマップ送信は未実施。

## 検証と公開方法

`scripts/build_search_presence_release.py` は `deployment/search-presence/release-baseline.json` の598資産とWorkerハッシュを照合する。HTMLの本文、既存JavaScript/CSS、画像、Workerの変化を拒否する。公開時は統合SHAのGit blobから4入力を取り出し、登録公開元の新規ディレクトリへ生成する。

```powershell
python -B -X utf8 scripts/build_search_presence_release.py --base-assets <検証済みbaseline/public> --output <新規出力> --source-sha <統合済み40文字SHA>
```

初期候補は47公開ページと2検証ページのhead更新、robots/sitemap更新、llms2ファイル追加。192 HTMLすべてのbodyが一致し、既存547資産・Workerが不変。生成候補と統合SHAからの本番生成物は区別する。Python回帰52件・Cloudflare7件・管理Worker4件・Cloudflare構成チェック成功。構成チェックの既存migration部分移行フラグ警告は今回の変更外。工程証拠は登録公開元 `tmp/delivery/20261011-seo-meo-entity/`、開始記録は事業ルート同名JSON。

## Googleビジネスプロフィール

既存の確認済み「クライミングコンサル」を使用。既存名称・カテゴリ・所在地・ウェブサイト・営業時間を保持し、AI相談の説明、滋賀県の対応地域、提供中の5サービスを整備する。電話番号は未確認のため追加しない。講習会場と事業所在地を混同しない。

公開ホームページの料金を転記する。個別相談5,500円/60分、エージェント講習5,500円/120分、コーディング講習11,000円/120分。伴走支援は月額88,000円・6ヶ月を説明欄で明記し単発価格にしない。制作は99,000円からの開始価格。準備中のオンラインサロンは追加しない。審査待ちと公開済みを区別する。

説明・対応地域・5サービスを保存し、サービスは審査待ち（画面表示は最大1日）。対応地域は審査待ち表示が消えている。AI個別相談の予約URLを追加し、編集欄を再度開いて同一URLを確認した。予約先は「60分・5,500円・来店/オンライン」の表示を確認済み。Squareの既存店舗ヘッダーはNotエステ彦根だが、個別サービスはAI相談。店舗設定は変更していない。画面証拠は事業ルート `tmp/seo-meo-20261011/gbp-*.jpg`。通常ログイン済みの事業用Chromeを再利用。顧客データ、アカウント識別情報、確認用トークンはこの記録に保存しない。

## Wikidata・検索施策の判断

AI相談・クライミングコンサル・由井辰美について一致を確認できたWikidata項目がない。別人のTatsumi Yui、別事業のグッぼる項目をsameAsへ流用しない。独立した信頼できる出典と同一性を確認できるまで新規項目を作らない。

Googleの公式説明ではllms.txtは検索順位を上げる特別な設定ではない。本文と構造化データの一致、クロール可能な正規URL、正確な事業情報を優先する。FAQリッチリザルトは2026年5月に終了しており、表示保証を説明しない。地域順位は関連性・距離・知名度などに依存し、設定完了を順位上昇の実測と混同しない。

公式資料:

- [Google AI検索最適化](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)
- [地域検索の掲載順位](https://support.google.com/business/answer/7091?hl=ja)
- [構造化データ方針](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)
- [Google検索ドキュメント更新](https://developers.google.com/search/updates)
- [Wikidata Notability](https://www.wikidata.org/wiki/Wikidata:Notability)

## 残件

Search Console所有権追加の回答後に確認タグを公開し、確認・サイトマップ送信へ進む。Google側の審査・反映と検索順位の変化は未確認。継続監視や新規広告・DNS変更は今回追加していない。

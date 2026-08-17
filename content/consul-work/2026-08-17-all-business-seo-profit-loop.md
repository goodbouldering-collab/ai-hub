# 全事業 SEO・MEO・構造化データ・利益導線 基準監査（2026-08-17）

> これは順位保証ではなく、Googleと利用者が到達・理解・信頼・行動できる状態の技術基準監査です。
> Google向けLLMO専用マークアップやllms.txtは加点していません。一次情報、明確な運営主体、検索意図への回答、計測可能なCVを重視します。

## 結論

- 台帳: 24事業 / 公開到達監査: 16 / 到達不可: 1 / URL未確定: 7
- GSCとGA4を両方マッピング済み: 3/16
- 優先順位は順位予測ではなく、索引阻害・計測欠損・CV欠損・地域実体不足から決めています。

## 全事業一覧

| 優先 | 事業 | URL | 基準点 | Git | 最大の欠損 |
|---|---|---|---:|---|---|
| critical | 巡波 | https://yomogi.vercel.app | 44 | dirty 2 | robots.txt を取得できない。 |
| high | NOKOSU | https://nokosu-ten.vercel.app | 49 | dirty 17 | SPAの初期HTMLにH1なし。レンダリング後DOMを別途確認する。 |
| high | ClimbHero | https://project-02ceb497.pages.dev | 58 | dirty 67 | SPAの初期HTMLにH1なし。レンダリング後DOMを別途確認する。 |
| high | トラスト | https://trusthikone.vercel.app | 65 | dirty 34 | robots.txt を取得できない。 |
| high | カラッと | https://karatto.life | 75 | 非Git | SPAの初期HTMLにH1なし。レンダリング後DOMを別途確認する。 |
| high | かたづけや | https://out-weld-tau.vercel.app | 80 | dirty 14 | canonicalがない。正規URLを明示する。 |
| high | ハイロックス本郷 | https://hyrox-zeta.vercel.app | 84 | 非Git | 対面事業だがLocalBusinessの具体型が確認できない。住所・電話・営業時間と可視情報を一致させる。 |
| high | Lungeup | https://lungeupsales.goodbouldering.chatgpt.site | 87 | dirty 11 | robots.txt を取得できない。 |
| high | みんなのWA | https://minnanowa.net | 93 | dirty 51 | 対面事業だがLocalBusinessの具体型が確認できない。住所・電話・営業時間と可視情報を一致させる。 |
| high | ビジネス21 | https://business21.vercel.app | 97 | dirty 84 | altなし画像が3/73件。意味のある画像だけ説明を付ける。 |
| high | Nデザイン | https://n-design.work | 100 | dirty 42 | GSC/GA4の事業台帳マッピングが未完了。順位だけでなく問い合わせ・予約・購入まで測れない。 |
| optimize | プロギング | https://plogging.jp | 81 | 非Git | canonicalがない。正規URLを明示する。 |
| optimize | グッぼる | https://goodbouldering.com | 92 | dirty 14 | OGPのtitle/description/imageが不足。SNS再編集時の認知損失になる。 |
| monitor | Notエステ | https://notesthe.com | 83 | 非Git | 測定待ち（2026-08-19まで）: WordPressトップの空title修正とBeautySalon JSON-LD追加後、GSCの28日比較を待つ |
| monitor | AI相談 | https://aiclimb.vercel.app | 97 | dirty 20 | 測定待ち（2026-08-24まで）: AI相談トップの検索意図・地域語・CTA・可視内容一致JSON-LDを本番反映後、GSC/GA4設定と28日比較を待つ |
| blocked | PROFIT | https://profit-hikone.vercel.app | 50 | dirty 14 | 実装保留: 最終ブランド・法務確認までnoindexを維持する（PROFIT/AGENTS.md） |
| confirm_scope | Climb | 未登録 | - | dirty 1 | 公開URL未登録。公開対象か、YouTube/SNS専用か、開発中かを確定する。 |
| confirm_scope | ファディー | 未登録 | - | 非Git | 公開URL未登録。公開対象か、YouTube/SNS専用か、開発中かを確定する。 |
| confirm_scope | 俺のトレード | 未登録 | - | dirty 11 | 公開URL未登録。公開対象か、YouTube/SNS専用か、開発中かを確定する。 |
| confirm_scope | ZAIKO_SON | 未登録 | - | dirty 68 | 公開URL未登録。公開対象か、YouTube/SNS専用か、開発中かを確定する。 |
| confirm_scope | リビルドマッチ | 未登録 | - | dirty 18 | 公開URL未登録。公開対象か、YouTube/SNS専用か、開発中かを確定する。 |
| confirm_scope | おやすみ設計ラボ | 未登録 | - | 非Git | 公開URL未登録。公開対象か、YouTube/SNS専用か、開発中かを確定する。 |
| confirm_scope | スポーツ睡眠ラボ | 未登録 | - | 非Git | 公開URL未登録。公開対象か、YouTube/SNS専用か、開発中かを確定する。 |
| excluded | 実行司令室 | https://climbing-consult-daily-command.goodbouldering.chatgpt.site | 0 | 非Git | 公開URLへ到達できない（HTTP 401）。 |

## 優先修正キュー

### 1. 巡波（critical / 44点）

- 公開URL: https://yomogi.vercel.app
- robots.txt を取得できない。
- sitemap.xml を取得できない。
- meta description長を要確認（29文字）。悩み、手段、成果、次の行動を要約する。
- H1が2件。ページ主題を1つ明確にする。
- canonicalがない。正規URLを明示する。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 2. NOKOSU（high / 49点）

- 公開URL: https://nokosu-ten.vercel.app
- SPAの初期HTMLにH1なし。レンダリング後DOMを別途確認する。
- canonicalがない。正規URLを明示する。
- JSON-LDがない。見えている事実だけを適切な型で記述する。
- 運営主体を示すOrganization/LocalBusiness/WebSite等が確認できない。
- 対面事業だがLocalBusinessの具体型が確認できない。住所・電話・営業時間と可視情報を一致させる。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 3. ClimbHero（high / 58点）

- 公開URL: https://project-02ceb497.pages.dev
- SPAの初期HTMLにH1なし。レンダリング後DOMを別途確認する。
- canonicalがない。正規URLを明示する。
- JSON-LDがない。見えている事実だけを適切な型で記述する。
- 運営主体を示すOrganization/LocalBusiness/WebSite等が確認できない。
- 主要CTA（相談・予約・申込・購入）が検出できない。検索流入の次の行動を1つに絞る。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 4. トラスト（high / 65点）

- 公開URL: https://trusthikone.vercel.app
- robots.txt を取得できない。
- sitemap.xml を取得できない。
- canonicalがない。正規URLを明示する。
- JSON-LDがない。見えている事実だけを適切な型で記述する。
- 運営主体を示すOrganization/LocalBusiness/WebSite等が確認できない。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 5. カラッと（high / 75点）

- 公開URL: https://karatto.life
- SPAの初期HTMLにH1なし。レンダリング後DOMを別途確認する。
- JSON-LDがない。見えている事実だけを適切な型で記述する。
- 運営主体を示すOrganization/LocalBusiness/WebSite等が確認できない。
- 料金・費用の判断材料が弱い。価格非公開なら見積条件や相談の流れを示す。
- altなし画像が9/27件。意味のある画像だけ説明を付ける。

### 6. かたづけや（high / 80点）

- 公開URL: https://out-weld-tau.vercel.app
- canonicalがない。正規URLを明示する。
- JSON-LDがない。見えている事実だけを適切な型で記述する。
- 運営主体を示すOrganization/LocalBusiness/WebSite等が確認できない。
- 対面事業だがLocalBusinessの具体型が確認できない。住所・電話・営業時間と可視情報を一致させる。
- GSC/GA4の事業台帳マッピングが未完了。順位だけでなく問い合わせ・予約・購入まで測れない。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 7. ハイロックス本郷（high / 84点）

- 公開URL: https://hyrox-zeta.vercel.app
- JSON-LD: Answer, Country, FAQPage, Person, Question, Service, WebSite
- 対面事業だがLocalBusinessの具体型が確認できない。住所・電話・営業時間と可視情報を一致させる。
- 地域・住所・営業時間・アクセス等の可視情報が弱い。MEOの関連性を高める一次情報が必要。
- 連絡・予約先への機械判定可能なリンクが見つからない。
- 料金・費用の判断材料が弱い。価格非公開なら見積条件や相談の流れを示す。
- GSC/GA4の事業台帳マッピングが未完了。順位だけでなく問い合わせ・予約・購入まで測れない。

### 8. Lungeup（high / 87点）

- 公開URL: https://lungeupsales.goodbouldering.chatgpt.site
- JSON-LD: Organization, Person
- robots.txt を取得できない。
- sitemap.xml を取得できない。
- canonicalがない。正規URLを明示する。
- GSC/GA4の事業台帳マッピングが未完了。順位だけでなく問い合わせ・予約・購入まで測れない。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 9. みんなのWA（high / 93点）

- 公開URL: https://minnanowa.net
- JSON-LD: AdministrativeArea, Answer, FAQPage, ImageObject, Organization, PostalAddress, Question, SpeakableSpecification, WebPage, WebSite
- 対面事業だがLocalBusinessの具体型が確認できない。住所・電話・営業時間と可視情報を一致させる。
- altなし画像が1/2件。意味のある画像だけ説明を付ける。
- GSC/GA4の事業台帳マッピングが未完了。順位だけでなく問い合わせ・予約・購入まで測れない。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 10. ビジネス21（high / 97点）

- 公開URL: https://business21.vercel.app
- JSON-LD: AdministrativeArea, Answer, BusinessAudience, ContactPoint, EntryPoint, FAQPage, GeoCoordinates, HowTo, HowToStep, LocalBusiness, NGO, OpeningHoursSpecification, Organization, PostalAddress, Question, SearchAction, Service, SpeakableSpecification, WebSite
- altなし画像が3/73件。意味のある画像だけ説明を付ける。
- GSC/GA4の事業台帳マッピングが未完了。順位だけでなく問い合わせ・予約・購入まで測れない。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 11. Nデザイン（high / 100点）

- 公開URL: https://n-design.work
- JSON-LD: AdministrativeArea, Answer, City, ContactPoint, FAQPage, GeneralContractor, GeoCoordinates, HomeAndConstructionBusiness, LocalBusiness, Offer, OfferCatalog, OpeningHoursSpecification, Person, Place, PostalAddress, PriceSpecification, QuantitativeValue, Question, SearchAction, Service, WebSite
- GSC/GA4の事業台帳マッピングが未完了。順位だけでなく問い合わせ・予約・購入まで測れない。
- 実装条件: 既存差分があるため、隔離worktreeまたは変更所有者の確認後に着手。

### 12. プロギング（optimize / 81点）

- 公開URL: https://plogging.jp
- canonicalがない。正規URLを明示する。
- JSON-LDがない。見えている事実だけを適切な型で記述する。
- 運営主体を示すOrganization/LocalBusiness/WebSite等が確認できない。
- altなし画像が6/17件。意味のある画像だけ説明を付ける。

## 利益につなげる共通計測

各事業で `organic landing -> engaged session -> key event -> lead/booking/purchase -> confirmed revenue` を追う。
検索順位や表示回数だけで成功判定しない。地域事業はGoogle Business Profileの通話、経路、Webクリック、予約も同じ事業IDへ集約する。

## 次回ループ

1. critical/highから、Gitがcleanで事実確認済みの1事業だけ選ぶ。
2. 検索意図・競合・一次情報を調査し、title/H1/本文/内部リンク/JSON-LD/CTAを同時に直す。
3. build/test後に本番へ反映し、実URL・robots・sitemap・JSON-LD・CTAを再監査する。
4. 7日で索引・エラー、28日でGSC、28〜56日でGA4/CV/売上を比較する。
5. 利益または有効リードが増えた施策だけを横展開し、悪化した変更は戻す。

生成時刻: 2026-08-17T06:07:59+09:00

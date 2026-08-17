# 全事業 SEO/MEO/JSON-LD/利益改善ループ（2026-08-17）

## 結論

今回は**公開変更なし**です。24事業を再監査し、GSC/GA4・公開URL・Git・レンダリング後DOM・前回記録を突き合わせましたが、法務・ブランド・正本URL・正本Git・計測・反映経路の全条件を満たす実装候補がありませんでした。

「直せそう」だけで本番を触らず、次回に安全に実装できる条件を残しました。GBP、価格、レビュー、認証、顧客データ、DB、公開投稿は変更していません。

## Google公式仕様の確認

- [Google Search Essentials](https://developers.google.com/search/docs/essentials)：技術要件やベストプラクティスを満たしても、クロール・インデックス・順位・表示は保証されない。人の役に立つ一次情報と、検索語をtitle/H1/alt/link textへ自然に置くことを優先する。
- [構造化データの一般ガイドライン](https://developers.google.com/search/docs/appearance/structured-data/sd-policies)：JSON-LDは可視内容と一致する事実だけに限定し、正しくてもリッチリザルトを保証しない。
- [Google Business Profileの表示ガイドライン](https://support.google.com/business/answer/3038177)：実在情報を正確に表現する。名称・カテゴリ・住所・営業時間・口コミは自動変更しない。

LLMO専用マークアップ、順位保証、FAQリッチリザルトを成果前提にはしていません。

## 監査結果

- 台帳: 24事業、公開URL登録: 17、初期HTMLで到達: 16、到達不可: 1、URL未登録: 7
- レンダリング後DOM: 16件を確認。ClimbHeroは15秒で遷移が終わらず、正本URL/描画確認を保留。
- 明確な正本URL不一致: 巡波の台帳URL https://yomogi.vercel.app/ は別ブランド「キャバ娘よもぎとシェルボーなずな」を表示。
- 検索可能なまま構造化データ/正規URLが欠ける主な候補: プロギング、トラスト、NOKOSU、かたづけや、LungeUp。
- noindexを維持すべき対象: PROFIT（ブランド・法務保留）、実行司令室（移行済み内部画面）。

詳細:

- [初期HTML/robots/sitemap/canonical/CTA/JSON-LD/Git基準監査](C:/Project/コンサル/work/2026-08-17-all-business-seo-profit-loop.md)
- [レンダリング後DOM監査JSON](C:/Project/コンサル/work/seo-profit-loop/2026-08-17-rendered-dom.json)

## GSC・GA4の28日比較

GSCは goodbouldering アカウントで7プロパティを更新しました。グッぼるでは「ザイル」2,196表示・CTR 0.5%、「ハイアングル」828表示・CTR 0.6%などの需要が確認できましたが、カテゴリだけを変更する既定と正式なカラーミー反映経路の未確認により、今回は修正しません。

GA4はすべて利益判定不可です。

| 事業 | 直近28日 | 欠損 | 利益判定 |
|---|---:|---|---|
| グッぼる | 39,359 sessions | (not set) 19.4%、conversion/session 4.63 | 不可 |
| プロギング | 5,247 sessions | conversions 0 | 不可 |
| Notエステ | 620 sessions | conversion/session 3.72、engagement 98.9% | 不可 |

conversionsを有効問い合わせ・予約・購入・確定売上と同一視していません。lossismore は token_lossismore.json がなく、GSC取得を再認証待ちとして記録しました。

## 選定結果

| 候補 | 判断 | 今回変更しない理由 |
|---|---|---|
| グッぼる | 次回最優先 | dirty 14、Git remote未設定、カラーミーの正本カテゴリ更新/本番反映経路が未確認。GA4成果イベントも異常。 |
| Notエステ | クールダウン | 2026-08-19までGSC比較待ち。非Gitかつ計測異常。 |
| プロギング | 反映経路待ち | GSCあり。ただし非Gitで、canonical/JSON-LDの正式な反映経路が未確認。 |
| 巡波 | 正本URL確認待ち | 台帳URLが別ブランドを表示。 |
| PROFIT | 法務・ブランド待ち | noindex,nofollowを維持する明示指示がある。 |
| NOKOSU | Git正本待ち | masterにコミットがなく全ファイル未追跡。隔離worktree不可。 |
| かたづけや | 現行刷新のcommit待ち | dirty 14の本番刷新を上書きする恐れがある。 |
| トラスト / ClimbHeroほか | 事実・法務・正本待ち | 既存差分や正本URL、ブランド/法務条件が未解決。 |

検索意図・競合上位・地域語の深掘りは、上記ゲートを通った1事業にだけ実施します。保留事業への推測ベースの本文、価格、実績、資格、レビュー追加はしていません。

## ローカル・プレビュー・本番

- ローカル: 監査スクリプト、GSC/GA4品質監査、JSON構文を実行済み。
- プレビュー: なし（サイト変更なし）。
- 本番: 17公開URLの到達/表示を読み取り監査済み。**本番反映はなし**。

## 次回の1手

グッぼるを実装対象にできる状態へ整えるには、次の4点だけを確認する。

1. カラーミーのカテゴリ更新を反映できる正本GitまたはAPI/管理画面の経路を確定する。
2. 既存差分を巻き込まないコミット基点を作る。
3. GA4で「購入完了」または「有効問い合わせ」を1イベントに絞り、売上照合方法を決める。
4. カテゴリ本文に用いる在庫数・試履き交換条件・フィッティング実績を当日時点の一次情報で再確認する。

成果物:

- [基準監査Markdown](C:/Project/コンサル/work/2026-08-17-all-business-seo-profit-loop.md)
- [基準監査JSON](C:/Project/コンサル/work/seo-profit-loop/2026-08-17-baseline.json)
- [レンダリング後DOM JSON](C:/Project/コンサル/work/seo-profit-loop/2026-08-17-rendered-dom.json)
- [GA4品質監査JSON](C:/Project/コンサル/work/seo-profit-loop/2026-08-17-ga4-data-quality.json)
- [機械可読な実行記録](C:/Project/コンサル/work/seo-profit-loop/2026-08-17-run.json)

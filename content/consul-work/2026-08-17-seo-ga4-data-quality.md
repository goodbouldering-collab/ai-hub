# SEO利益判断用 GA4データ品質監査（2026-08-17）

## 結論

現状のGA4 `conversions` は、3事業とも利益の優先順位づけにそのまま使わない。GSCの表示・クリックは施策候補抽出に使えるが、問い合わせ・購入・売上との接続は計測修正後に行う。

| 事業 | sessions | (not set)/空欄 | conversions/session | 利益判断 |
|---|---:|---:|---:|---|
| グッぼる | 39359 | 19.4% | 4.63 | 停止 |
| プロギング | 5247 | 4.0% | 0.00 | 停止 |
| Notエステ | 620 | 1.3% | 3.72 | 停止 |

## 検出事項

### グッぼる

- **high / landing_page_completeness**: (not set)/空欄が19.4%（7620/39359 sessions）。LP別評価に偏りが出る。
- **critical / conversion_grain**: conversions/session=4.63（182072/39359）。conversionが問い合わせ・購入ではなく複数の行動イベントを数えている可能性が高い。利益指標に使えない。

### プロギング

- **critical / conversion_coverage**: 5247 sessionsに対しconversions=0。購入計測が未設定・未連携・無売上のどれかを区別できない。SEOの利益評価ができない。

### Notエステ

- **critical / conversion_grain**: conversions/session=3.72（2309/620）。conversionが問い合わせ・購入ではなく複数の行動イベントを数えている可能性が高い。利益指標に使えない。
- **high / engagement_distribution**: セッション加重engagement rate=98.9%。イベント設定が過敏、または自動イベントを成果扱いしている可能性がある。

## 最小修正

1. 事業ごとに利益イベントを1〜3個だけ定義する（例: 予約完了、問い合わせ送信、購入）。
2. `generate_lead` / `purchase`等のイベント名、発火条件、重複防止、金額・通貨、thank-you到達を実機で確認する。
3. 内部アクセス、管理画面、決済戻り、自動更新、ボットを除外する。
4. LPが`(not set)`になる流入をsource/medium・hostname・session_start有無で分解する。
5. 7日間のテスト後、実予約・注文台帳と日別件数を照合し、差が許容範囲になってから利益ループへ採用する。

## 自動テスト

- `(not set)` session率: 5%超で警告、20%超で利益判断停止。
- ecommerceでpurchase/key eventが0のままsessionsが100超: 計測確認。
- conversions/sessionが1超: イベント粒度確認。
- engagement rateが98%超または2%未満: 実装・ボット・イベント定義確認。

## 前提

GA4 Data APIのLP別集計を使用。`conversions`は設定済みイベント数であり、確認済み売上や有効リード件数とは限らない。直近28日の全LP行を集計した。

# グッぼる コアアップデート被弾からの回復 — 対策①②の具体策

- 日付: 2026-05-25
- 前提: [2026-05-25-gubble-seo-api-diagnosis-confirmed.md](2026-05-25-gubble-seo-api-diagnosis-confirmed.md) で真因＝Googleコアアップデート(3月+5月)と確定
- 最大の出血点: **PRODUCT_SNIPPETS のクリックが 5071→2417 でほぼ半減**
- 対象実コード: `グッぼる/カラーミー/template_backup/1064_MONO_current/product.html` ほか（カラーミーのSmartyテンプレ・EUC-JP配信）

---

## 重要な前提：構造化データは「ゼロから作る」ではない

product.html には既に高度な JSON-LD が実装済み:
Product / Offer(AggregateOffer分岐あり) / priceValidUntil / availability /
OfferShippingDetails / MerchantReturnPolicy / AggregateRating / Review[] / Person。

→ 対策②は**新規実装でなく「既存実装のどこが評価を落としたかの点検と修正」**。

---

## 【2026-05-25 追記】実コード＆本番HTML検証の結果：構造化データは健全。コード修正は不要

代表商品3ページの本番HTMLのJSON-LDを実取得して検証した結論:
- JSON-LD は有効JSON・テンプレ変数(`<{}>`)も完全展開・name/price/availability 全て正常
- `priceValidUntil` = 2099-12-31（過去日問題なし＝点検2 不該当）
- aggregateRating は `<{if $review_use_flg && $review_item_num}>` で正しくガード（点検1 不該当）
- ratingValue default:'5' は該当ブロック内のみで実害経路なし（点検3 軽微）
- → **点検1〜4すべて不該当。構造化データに技術的欠陥はゼロ**

さらに searchAppearance 期間比較で判明:
- PRODUCT_SNIPPETS は **表示回数 62,193→38,496（-38%）**・クリック 4952→2527（-49%）
- 「CTRが落ちた」のではなく **Googleが商品リッチリザルトを出す頻度を4割絞った**
- = コアアップデートによるドメイン品質評価の引き下げ。**コード修正では戻らない**

→ **対策はコード修正(②)ではなく、品質評価そのものを上げる E-E-A-T(①) に一本化する。**
（下記②は「念のため点検したが該当なし」として記録保持。実装作業は発生しない）

## 対策②：PRODUCT_SNIPPETS 立て直し（※検証の結果、該当なし・実装不要と判明）

リッチリザルト(商品スニペット)は要件を1つでも外すとGoogleが表示を止める。半減＝要件落ちの疑い。
既存テンプレで**点検すべき具体的な穴**（コードを読んで抽出した実際の懸念）:

### 点検1: `aggregateRating` の reviewCount が 0 のとき
```
"ratingValue": "<{$avg_rating|default:'5'|escape:'javascript'}>",
"reviewCount": "<{$review_item_num|escape:'javascript'}>"
```
- `<{if $review_use_flg && $review_item_num}>` でガードはされているが、**reviewCountが"0"や空で出力されるとGoogleは構造化データエラー**として商品スニペットを丸ごと無効化することがある
- レビューゼロ商品が多数なら、**その商品群が一斉にスニペット対象外**になる→クリック半減と整合
- 修正: reviewCount が 1 以上のときだけ aggregateRating を出す（0件商品はrating自体を出さない）

### 点検2: `priceValidUntil` が過去日になっていないか
```
"priceValidUntil": "<{$priceValidUntil|date_format:'%Y-%m-%d'...}>"
```
- これが**過去日**だとGoogleは「価格情報が古い」と判断しOffer無効化→商品スニペット消滅
- `$priceValidUntil` がどう生成されているか要確認。未設定や固定日で過去になっていないか

### 点検3: `ratingValue` default:'5' のハードコード
- レビューが無いのに `default:'5'` で5.0を出すと**ガイドライン違反（実体のない評価）**。手動対策やスニペット剥奪のリスク
- 修正: デフォルト5を廃止。実レビューが無ければ rating を出さない

### 点検4: AggregateOffer分岐時に offerCount/価格が正しいか
- サイズ展開のある靴は AggregateOffer になる。`lowPrice`/`highPrice`/`offerCount` のいずれかが空/0だと無効

### 検証手順（developer）
1. Google「リッチリザルト テスト」(search.google.com/test/rich-results) で代表商品URLを数点チェック
2. GSC左メニュー「商品スニペット」レポートで**エラー/警告の急増時期**を確認（5月の更新前後で増えていれば確定）
3. 上記点検1〜4で該当する条件分岐を修正 → リッチリザルトテスト再通過を確認

---

## 対策①：E-E-A-T強化（コアアップデート回復の本筋・グッぼるの武器）

コアアップデートは「専門性・権威性・信頼性・経験」を評価する。グッぼるは武器が揃っているのに
**構造化データ上でGoogleに伝えきれていない**のが穴。

### 強化1: Organization/店舗の権威を構造化（最優先）
現状 product.html の JSON-LD は Product 中心で、**運営者(Organization)の権威情報が薄い**。
トップ or 全ページ共通で以下を出す:
```jsonld
{
  "@type": "Store",  // or LocalBusiness
  "name": "グッぼる",
  "foundingDate": "2013",
  "founder": {"@type":"Person","name":"由井辰美","description":"クライミング歴30年以上"},
  "knowsAbout": ["クライミングシューズフィッティング","ボルダリング","リードクライミング"],
  "address": {...彦根の実店舗...},
  "slogan": "年間300件超の対面フィッティング実績"
}
```
- 実店舗13年・年間300件フィッティング・30年オーナーは**一次経験(Experience)の最強の証拠**。構造化して明示

### 強化2: 商品ページに「専門店としての一次情報」をテキストで厚く
- カテゴリページには既に「3mm刻み」「年間300件」等が入っている（確認済）。**商品個別ページにも**、その靴をスタッフが実際に履いた所感・どの岩場/グレードで使ったか・足型別の推奨を1〜2段落
- これがAI検索(LLMO)とコアアップデート両方に効く。他店がコピーできない一次情報

### 強化3: 著者性(authorship)
- Review の author は購入者だが、商品説明や選び方ガイドの**書き手＝専門家**であることを示す（Person+知見）

---

## 【2026-05-25 追記】対策① E-E-A-T の実装案（コード修正不要が確定したので、これが本命）

コアアップデートは「専門性・権威性・信頼性・経験(E-E-A-T)」で評価する。グッぼるは武器が
揃っているのにGoogleに構造化で伝えきれていない。以下を**全ページ共通**で追加する想定の実装案。

### A. Store/Organization の権威を構造化（トップ or 全ページ共通の<head>）
```jsonld
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "SportingGoodsStore",
  "name": "グッぼる",
  "url": "https://goodbouldering.com/",
  "foundingDate": "2013",
  "founder": {
    "@type": "Person",
    "name": "由井辰美",
    "jobTitle": "オーナー",
    "description": "クライミング歴30年以上。世界中の岩場を登るクライマー兼フィッター"
  },
  "knowsAbout": ["クライミングシューズフィッティング","ボルダリング","リードクライミング","クラッククライミング"],
  "slogan": "年間300件超の対面フィッティング実績",
  "description": "2013年開業・滋賀県彦根市の実店舗。クライミング/ボルダリング専門の販売とフィッティングに13年特化。常時100モデル超・約230点在庫、3mm刻みのサイズ展開。",
  "address": {"@type":"PostalAddress","addressRegion":"滋賀県","addressLocality":"彦根市","addressCountry":"JP"}
}
</script>
```
※住所の番地等は事業の正本（config/店舗情報）で補完。creator/founderの実在性がE-E-A-Tの核。

### B. 商品ページに「一次経験(Experience)」をテキストで明示（最重要・他店がコピー不可）
商品individual ページの説明に、以下の型で1〜2段落を足す（writerが各靴で書き分け）:
- **この靴を実際に履いた所感**（スタッフ/オーナーの一次体験）
- **どの岩場・どのグレード帯で使ったか**（瑞牆/小川山/湯河原幕岩 等の固有名＋V◯）
- **足型別の推奨**（幅広/細め、ヒールの効き、ダウントゥの強さ）
- 例: 「スクワマは小川山のスラブでこそ真価。V5前後のフリクション勝負で…幅は狭め、エジプシャン気味の足に合う」

→ これは AI検索(LLMO) とコアアップデート両方に効く。グッぼる本店経由でしか得られない一次情報＝
gubble.md のトーン方針（クライミング歴30年・固有名そのまま・本気のクライマー向け）と完全一致。

### C. 著者性(authorship)
- 「選び方ガイド」「商品所感」の書き手＝専門家であることを Person で明示（Bと連動）

> A は developer 案件（テンプレ<head>に1ブロック追加・CEO承認必要）。
> B/C は writer/marketer 案件（原稿生成→既存商品説明欄に流し込み）。Bが回復の主エンジン。

## 実行の段取り（CEO承認後）

**※2026-05-25 検証で②(コード修正)は不要と確定。段取りはE-E-A-T一本に更新:**

| 順 | 担当 | 作業 | 効果 |
|---|---|---|---|
| 1 | writer | 主力シューズ(スクワマ/ソリューション/フューリア等)の商品説明に一次経験テキスト(①B)を書く | **回復の主エンジン**・他店コピー不可のE-E-A-T |
| 2 | developer | Store/founder 構造化データ(①A)を全ページ<head>に追加（CEO承認・要） | 権威性をGoogleに明示 |
| 3 | — | seo-weekly.yml の週次ダイジェストで回復を観測（5月コアアップデート完了後＋次回更新時） | 回復確認 |

> 構造化データのコード修正(②)は検証の結果**該当なし＝着手しない**。
> ①Bはconsul内の原稿作業→既存商品説明欄への流し込み。事業フォルダのコード書き込みは①Aのみで、CEO承認が前提。

# Design QA — ヒーロー文字拡大・AIオンラインサロン洗練

- source visual truth:
  - ユーザー注釈: ヒーローの「経験×AI」、`AI利用率`、安心項目の文字拡大
  - ユーザー注釈: `#seven-day-courses .salon-panel` を、内容を省略せず洗練
  - `C:\Users\yui\.codex\visualizations\2026\07\22\019f8743-9c47-7ac3-89d9-245798ea7829\hero-text-size-20260730\before-906x992.png`
  - `C:\Users\yui\.codex\visualizations\2026\07\22\019f8743-9c47-7ac3-89d9-245798ea7829\hero-text-size-20260730\before-390x844.png`
  - `C:\Users\yui\.codex\visualizations\2026\07\22\019f8743-9c47-7ac3-89d9-245798ea7829\hero-text-size-20260730\before-salon-906x794.png`
  - `C:\Users\yui\.codex\visualizations\2026\07\22\019f8743-9c47-7ac3-89d9-245798ea7829\hero-text-size-20260730\before-salon-390x844.png`
- implementation screenshots:
  - `C:\Users\yui\.codex\visualizations\2026\07\22\019f8743-9c47-7ac3-89d9-245798ea7829\hero-text-size-20260730\after-906x992.png`
  - `C:\Users\yui\.codex\visualizations\2026\07\22\019f8743-9c47-7ac3-89d9-245798ea7829\hero-text-size-20260730\after-390x844.png`
  - `C:\Users\yui\.codex\visualizations\2026\07\22\019f8743-9c47-7ac3-89d9-245798ea7829\hero-text-size-20260730\after-salon-906x794.png`
  - `C:\Users\yui\.codex\visualizations\2026\07\22\019f8743-9c47-7ac3-89d9-245798ea7829\hero-text-size-20260730\after-salon-390x844.png`
- comparison inputs:
  - `compare-hero-906-scaled.png`
  - `compare-hero-390.png`
  - `compare-salon-906-scaled.png`
  - `compare-salon-390.png`
- viewport and density: 906 × 992、906 × 794、390 × 844 CSS px、DPR 約1
- state: 公開トップ先頭、サロンアンカー到達、モバイルメニュー閉／開／サロン選択後

## Full-view comparison evidence

ヒーローは画像、見出し、本文、CTA、位置関係を維持し、注釈対象だけを拡大した。PCでは `AI利用率` 13px、補足13px、主文22px、3原則14px、安心項目15px。390pxでは順に12px、11px、約18.7px、12px、14pxとなり、すべて横はみ出し0。

サロンは全コピー、図解、4つの開催情報、3つの参加手順、4つの時刻、欠席週の説明、Square CTA、自動更新・LINE案内を保持した。重複していた個別カード背景と角丸を、1枚の外枠と細い区切り線へ整理した。パネル高は906px幅で約697pxから613px、390px幅で約898pxから815pxへ短縮した。

## Focused region comparison evidence

- ヒーロー: `経験×AI` と3原則の視線移動が明確になり、背景画像やCTAとの衝突なし。
- `AI利用率`: 大きな6%との関連を保ったまま、ラベル単体でも読める大きさへ変更。
- 安心項目: 390pxでは自然な2行、906pxでは1行を維持。
- サロン上段: 左の価値提案、右の3価値をフラットな情報階層へ整理。
- 開催情報: WHEN / PLACE / FEE / STYLE は横1列を維持。
- 参加方法: 図解と3手順を1ブロックにまとめ、図解キャプションもモバイルで表示。
- 60分の流れ: 4つのカードを1本の進行表へ整理。
- モバイルの `BEST PRACTICE`: ellipsisを廃止し、全文表示。

## Required fidelity surfaces

- Typography: 注釈対象を拡大。サロン本文は縮小で詰めず、主要本文11〜15px、補助ラベル9px以上を確保。
- Copy: `.salon-panel` 内の全表示文言、画像、フォーム、POST先を回帰テストで固定。
- Spacing rhythm: 外枠、区切り線、余白の3段階に整理し、カードの重なり感を削減。
- Color: 既存の青、白、濃紺、薄い罫線だけを使用。
- Image quality: 既存SVGを維持し、縦横比を変更していない。
- Responsive: 320 / 360 / 390 / 720 / 900 / 906 / 1280pxでページ、ヒーロー、サロンの横はみ出し0。

## Comparison history

1. P2: ヒーロー補助文字が8〜12.5pxで小さかった。PC13〜22px、モバイル11〜約18.7pxへ拡大して解消。
2. P2: サロン内で複数の枠、背景、角丸が同じ強さで重なっていた。フラットな区切り線へ統合して解消。
3. P2: モバイルの `BEST PRACTICE` がellipsisで省略される可能性があった。省略指定を解除して解消。
4. P2: 320px幅でヒーロー3原則に8pxの内部はみ出しがあった。11pxの最小幅専用調整で0に解消。

## Primary interactions tested

- 390px: メニューを開くと右側パネルが `translateX(100%)` から0へ移動。
- `aria-expanded=true`、`aria-hidden=false`、bodyスクロール固定を確認。
- AIオンラインサロンが公開メニュー最下段にあることを確認。
- サロン選択後に `#seven-day-courses` へ移動し、メニューが閉じることを確認。
- 906px以上: 通常ナビ表示、モバイルトグル非表示。
- ブラウザ console warning / error: 0件。

## Findings

対象範囲に未解決のP0 / P1 / P2はない。内容省略、横スクロール、文字の重なり、画像の歪み、CTAのはみ出しは確認されなかった。

final result: passed

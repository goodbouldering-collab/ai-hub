# Design QA — 公開トップ・フッター余白標準化

- source screenshot: `C:\Users\yui\AppData\Local\Temp\ai-consult-footer-qa-20260722\source-production-footer-821.png`
- implementation screenshot (tablet): `C:\Users\yui\AppData\Local\Temp\ai-consult-footer-qa-20260722\implementation-local-footer-tablet.png`
- implementation screenshot (mobile): `C:\Users\yui\AppData\Local\Temp\ai-consult-footer-qa-20260722\implementation-local-footer-mobile.png`
- implementation screenshot (desktop): `C:\Users\yui\AppData\Local\Temp\ai-consult-footer-qa-20260722\implementation-local-footer-desktop.png`
- viewport: comparison 810 × 645 CSS px (`clientWidth: 795`, screenshot 795 × 633); mobile 390 × 844; desktop 1440 × 900
- state: 公開トップの最終CTA直後からフッター末尾まで。比較時は `.site-footer` を画面上端へスクロール。

## Full-view comparison evidence

修正前の本番画面と修正後のローカル画面を、同じタブ・同じ表示幅・同じスクロール状態で並べて比較した。周辺の最終CTA、フッターの文言、リンク、配色、コピーライトは維持し、ユーザー注釈の対象である余白とレスポンシブ列だけを変更した。

修正前はフッターの左右 `padding` が `0`、前セクションとの `margin-top` が `64px`、さらに上 `padding` が `48px` で、縦に約112pxの空白が重なっていた。修正後は外側 `margin-top: 0` と可変上余白 `40.52px` に一本化し、左右 `18px` を確保した。

## Focused region comparison evidence

タブレット幅のフッターを同一比較入力で確認した。

- before: `padding: 48px 0 16px`; 3列 `307.945 / 192.476 / 230.974px`; gap `32px`
- after: `padding: 40.52px 18px 16px`; 2列 `367.45 / 367.45px`; gap `24.312px`; ブランド領域は2列を横断
- horizontal overflow: なし（`scrollWidth == clientWidth == 795`）

スマホは `36px 14px 16px`、1列、gap `24px`。PCは上 `48px`、3列、gap `32px`、既存の最大幅 `1000px` を維持した。

## Required fidelity surfaces

- Typography / copy: フッターの見出し、説明、住所、メール、CTA文言を変更していない。
- Spacing rhythm: 左右余白、上下余白、列間隔を3つのCSS変数に集約した。
- Responsive layout: PC 3列、900px以下 2列、680px以下 1列へ段階的に切り替わる。
- Color / component fidelity: 白背景、既存の文字色、CTA、罫線を維持した。
- Adjacent layout: 最終CTAとの過剰な二重余白だけを解消し、セクション順と高さの意図は保持した。

## Comparison history

1. P2: タブレット幅でも3列が維持され、各列の文字が詰まり、左右のコンテンツが画面端に接していた。900px以下を2列に変更し、`minmax(0, ...)` と左右余白を追加して解消。
2. P2: 前セクションとの `64px` margin とフッター上 `48px` padding が重なり、大きな空白帯になっていた。marginを0にし、単一の可変paddingへ統一して解消。
3. P2: 既存のフッター用ブレークポイントが760pxで、サイト共通の900px / 680pxと不一致だった。共通ブレークポイント側で上書きし、タブレット・スマホの切り替えを標準化。

## Findings

対象範囲に未解決のP0/P1/P2はない。タブレット、iPhone幅、PC幅のすべてで横スクロールは発生せず、文字の欠けや列の衝突もない。

## Primary interactions tested

- 公開トップのフッターCTA・ページ内リンク・メールリンクの `href` 保持
- スマホのメニューボタン開閉（`aria-expanded` false → true → false）
- スマホメニューの白背景と濃色文字のコントラスト
- PC / タブレット / iPhone幅の固定ヘッダーとフッター表示
- ブラウザ console warning / error: 0件

final result: passed

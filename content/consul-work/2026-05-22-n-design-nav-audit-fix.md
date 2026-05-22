# N-デザイン トップのナビ総点検と修正（番号二重基準・サービス導線）

日付: 2026-05-22
事業: Nデザイン（n-design）
対象: `components/section-nav.tsx`, `components/header.tsx`
本番: https://n-design-lemon.vercel.app

## 依頼

TOPのセクション / サイドバーメニュー / TOPメニュー / 固定メニュー / ハンバーガーメニューが
正しいか確認して修正。

## 点検結果

### アンカー整合（問題なし）
ナビ（section-nav・header 共通）が参照する8アンカー
`hero/why/works/services/price/flow/news/contact` は全てページ内に存在し、
DOM順（top座標 0→900→3068→4896→6400→8534→9598→13708）とも一致。リンク切れ・順序逆転なし。
※ news=blog-previews が id="news" を持つ点に注意（ラベル「ブログ」）。

### 問題1: 番号体系の二重基準（修正）
- セクション見出し（SectionHeader number=）: DOM順で why=01, profile=02, works=03 … contact=12 の**1〜12連番**（コミット #9 で連番化済＝正本）
- ナビ（サイド/ヘッダー）: 8グループ集約の **01〜08**
- 同じ why が「見出し01」「ナビ02」と食い違い、ヒーロー下に番号ズレが露見

### 問題2: サービスがTOPメニューに無い（修正）
- デスクトップ header の primaryDesktopHrefs に /#services が無く、「サービス」が
  「メニュー▾」ドロップダウン配下に隠れていた（主要導線なのに直接押せない）

## 修正（CEO方針: ナビを見出しに合わせる → 飛び番号回避のためナビ番号は撤去）

- `section-nav.tsx`: items から num を削除、ラベルスパン内の番号表示を撤去。
  見出し1〜12連番を番号の正本とし、集約ナビはラベルのみ表示にして二重基準を構造的に解消。
- `header.tsx`: primaryDesktopHrefs に `/#services` 追加。サービスを直接表示に昇格。
  トップ・強みは集約して「メニュー」ドロップダウンに残す。

## 検証（本番実測 chrome-devtools）

- typecheck / build 通過。安全ゲート: ①build通過 ②秘密情報なし ③2ファイルのみ選択コミット
  （build再生成の generated.ts は破棄）
- デスクトップTOPメニュー: 施工事例/**サービス**/料金・補助金/ご依頼の流れ/ブログ/お問い合わせ/会社概要 — 横一列に崩れず収まる
- サイドナビ: ラベルのみ表示・番号なし（sideHasNumber=false 実測）
- ハンバーガー: 全12項目（トップ〜管理ログイン）整然と表示・DOM順一致
- 見出し側 WHY は「01」のまま（正本維持）

## 結果

- commit 3c0fbb9 → origin/main push 済（Vercel自動デプロイ・本番反映確認済）
- 本番: https://n-design-lemon.vercel.app

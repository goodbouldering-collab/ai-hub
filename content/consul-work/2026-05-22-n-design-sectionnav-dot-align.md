# N-デザイン サイド縦ステップナビのドット列ズレ修正

日付: 2026-05-22
事業: Nデザイン（n-design）
対象: `C:\VSCode\Project\N-デザイン\components\section-nav.tsx`
本番: https://n-design-lemon.vercel.app

## 症状（CEOスクショ提供）

左サイドの縦スクロールスパイ・ナビ（01〜08 + 管理ログイン）で、アクティブ項目
（例: 08 お問い合わせ）のドットだけ列から右にはみ出して見える＝縦の列がズレる。

## 原因（chrome-devtools で実測して特定）

- 各ドットは `relative inline-block` のインライン要素で、アクティブ時のみ
  `h-2 w-2`(8px) に加えて `h-2.5 w-2.5`(10px) と `ring-4`(外周4px) が後勝ちで適用
- `flex items-center` の左揃え基準でドットの左端は揃うが、幅が8px↔10pxで
  変わるため**中心が1px右へずれ**、さらに ring 外周が列からはみ出して見えた
- 実測: 非アクティブ中心X=24px / アクティブ中心X=25px（spread 1px）

## 修正

ドットを固定幅の箱 `flex h-3 w-3 shrink-0 items-center justify-center` に入れ、
内側の実ドット（block rounded-full）だけサイズ変化＋ring を持たせる。これで
箱中心 = ドット中心が常に固定され、サイズ変化・リングが中心基準で広がる。
区切り線の左位置（ml-[3px]→ml-[5px]）と幅も箱中心に合わせて調整。管理ログインの
ドットも同じ固定箱構造に統一。

## 検証

- `npm run typecheck` / `npm run build` 通過
- 安全ゲート: ①ビルド通過 ②秘密情報なし ③section-nav.tsx のみ選択コミット
  （作業ツリーに別作業の generated.ts / package.json末尾改行差が混在していたため巻き込まず）
- 本番デプロイ後 chrome-devtools 実測: 全9ドットの中心X=26px で**完全一致（spread 0）**
- スクショで縦一直線を目視確認

## 結果

- commit 34a2159 → origin/main push 済（Vercel自動デプロイ・反映確認済）
- 本番: https://n-design-lemon.vercel.app

# 2026-05-11 ビジネス21 スライド — フルブリード可変レイアウト v3

## CEO 指示の遷移

1. (第1段) 「PC同様に横向きで画面いっぱい使えるよう再構築」
   → 真因「スマホ横持ち余白問題」を SlideShell の overlay 化で解決 (v2.1)
2. (第2段) 「フルブリード可変レイアウトに作り直す」
   → 16:9 + scale() 維持自体を捨て、コンテナ完全追従に再設計 (v3, 本ログ)

CEO 選択: 通常表示もフルブリード / スマホでは内部スクロール許容 / 実装は Container Queries 採用。

## v2 → v3 設計変更

| 項目 | v2 | v3 |
|---|---|---|
| 論理サイズ | 1280×720 固定 | なし (コンテナ追従) |
| フィット方式 | `transform: scale()` で全体縮小 | `width: 100%; height: 100%` で埋める |
| アスペクト | 常に 16:9 維持・必ず黒帯 | 黒帯ゼロ・画面アスペクト追従 |
| 文字スケール | scale() で一律縮小 | `zoom` プロパティ + `@container slide` で段階制御 |
| スマホ縦持ち警告 | 「横向きにしてください」オーバーレイ | 廃止 (縦でも縦長スライドとして表示) |
| 内部スクロール | 不可 (`overflow: hidden`) | 許容 (`overflow-y: auto`) |

## 中核アイデア: `zoom` + Container Queries

scale() の代わりに **CSS `zoom`** を採用。`transform: scale()` と違い zoom は
**レイアウトに反映される** (親要素の高さが zoom 後のサイズで計算される)
ため、本来「リフロー型レイアウト」と相性が良い。

```css
.slide-cq-container {
  container-type: size;   /* CQ 起点 */
  container-name: slide;
}
/* 段階的に zoom を適用 — slideDesign.tsx の固定 px (text-[19px] 等) を
   書き換えずに一括スケール */
@container slide (max-width: 1600px) { .slide-bleed-body { zoom: 1.05; } }
@container slide (max-width: 1280px) { .slide-bleed-body { zoom: 0.95; } }
@container slide (max-width: 1100px) { .slide-bleed-body { zoom: 0.85; } }
@container slide (max-width: 960px)  { .slide-bleed-body { zoom: 0.75; } }
@container slide (max-width: 800px)  { .slide-bleed-body { zoom: 0.65; } }
@container slide (max-width: 640px)  { .slide-bleed-body { zoom: 0.55; } }
@container slide (max-width: 480px)  { .slide-bleed-body { zoom: 0.45; } }
@container slide (min-width: 1920px) { .slide-bleed-body { zoom: 1.2; } }
@container slide (min-width: 2400px) { .slide-bleed-body { zoom: 1.4; } }
```

これにより **`slideDesign.tsx` (923行) と各デッキ (約1962行) の本体コードは一切書き換えずに**
フルブリード対応が完了。

### zoom サポート状況 (2026-05 時点)

| ブラウザ | 状態 |
|---|---|
| Chrome / Edge | ✅ 古くからサポート (`-webkit-zoom` も含め) |
| Safari (Mac/iOS) | ✅ サポート |
| Firefox | ✅ FF 132 (2024-11) で標準化、現行は問題なし |

`zoom` は CSS 公式仕様 (CSSWG Drafts) に取り込み済みで baseline newly available。
今回の用途 (社内営業ツール) では十分。

### Tailwind 既存 `text-[Npx]` との整合性

子要素 `text-[19px]` 等の絶対 px は zoom 倍率で実効サイズが変わる:
- zoom 1.0 → 19px
- zoom 0.55 → 約 10.5px (スマホ横持ち想定)
- zoom 1.2 → 約 22.8px (4K想定)

`em` ベースに書き直すより、zoom 採用のほうがコード差分が最小で済む。

## 通常時 (管理画面埋め込み) の高さ

CEO 指示「通常もコンテナ追従」を反映。
通常時のコンテナサイズ:
```
height: min(82dvh, calc(100vw * 9 / 16))
min-height: 420px
```
- 横長画面 (PC): 82dvh を取る
- スマホ縦持ち: 横幅 × 9/16 (≈ 16:9 換算) で適切な縦長に
- 極小画面: 420px 下限で潰れない

これは「アスペクト 16:9 を強制しない代わりに、極端な縦長/横長を避けるセーフティ」。

## 修正ファイル

- [components/admin/SlideShell.tsx](../../ビジネス21/components/admin/SlideShell.tsx) — 全面書き直し (約 580 → 約 500 行)
  - `SLIDE_W=1280` / `SLIDE_H=720` 削除
  - `scale` state / `recalcScale` / `useLayoutEffect` 削除
  - `isPortrait` / 縦持ち警告オーバーレイ削除 (フルブリードで縦でも見える)
  - container-type: size による CQ 起点宣言
  - `@container slide` メディアクエリで zoom 段階適用

未編集 (zoom で吸収):
- `components/admin/slideDesign.tsx` (923 行)
- `components/admin/IntroSlideDeck.tsx` (602 行)
- `components/admin/PitchSlideDeck.tsx` (682 行)
- `components/admin/SendingPitchSlideDeck.tsx` (678 行)

## 検証状況

- ✅ TypeScript `tsc --noEmit` 通過
- ⏳ `next build` (CEO 動作確認後に実施予定)
- ⏳ 実機検証 (PC/iPhone 横持ち/縦持ち)

## 動作確認のお願い

- [ ] PC: `http://localhost:3007/admin/sales/intro` で 16:9 ではなく画面アスペクトに追従するか
- [ ] PC `F` キーで全画面 → 1920×1080 で黒帯ゼロ
- [ ] iPhone 横持ち全画面: 844×390 を完全に埋める (黒帯なし・文字が縮んで見やすい)
- [ ] iPhone 縦持ち全画面: 縦長レイアウトで表示、内部スクロールで全コンテンツ確認可
- [ ] サムネイル一覧 (G)・タイマー (T)・キーボード操作が従来通り
- [ ] 文字が読みやすいか・要素が崩れないか・画像のアスペクト比が破綻していないか

## リスク

| リスク | 想定原因 | 対処 |
|---|---|---|
| 一部スライドで内容が縦に溢れスクロール多発 | デッキ側が `h-full` 前提で組まれている | 内部スクロール許容済 (CEO 同意) |
| 縦長アスペクトで写真が引き伸ばされる | デッキ側で `object-cover` や `aspect-video` が前提 | 実機検証で見つかれば該当部品を個別調整 |
| zoom 効かないブラウザ | 想定外の古環境 | フォールバック (`@supports not (zoom: 1)`) は未実装 — 必要なら追加 |
| 全画面 fixed inset 0 が AdminChrome を干渉 | `body.slide-fullscreen-active` の CSS で対処済 | 維持 |

## コミット候補メッセージ

```
feat(business-21/slide): フルブリード可変レイアウトに刷新 (16:9 黒帯廃止)

- 論理 1280×720 + transform: scale() を廃止
- container-type: size + @container slide による段階的 zoom スケール
- 通常表示もコンテナ追従、全画面時は 100vw × 100dvh フル占有
- スマホ縦持ち警告を撤去 (縦長表示・内部スクロール許容)
- slideDesign.tsx / 各デッキ本体は zoom で吸収、書き換えゼロ
```

## 次のアクション (CEO 判断待ち)

1. CEO が動作確認 → OK ならコミット
2. NG なら個別スライドの調整 (画像オーバーフロー・縦長時のレイアウト等)
3. v2.1 (overlay バー) で必要十分だった場合は v3 をロールバックし v2.1 で行く判断もアリ

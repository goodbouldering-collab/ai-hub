# ビジネス21 スライド iPhone 対応 — 実装結果 (2026-05-11)

## 完了状況

✅ 実装完了・lint クリーン・型エラーなし・`npm run build` 完走

## 変更ファイル (1 ファイルのみ)

`c:\VSCode\Project\ビジネス21\components\admin\SlideShell.tsx`

**当初予定では `slideDesign.tsx` の clamp 化も含めるつもりだったが、論理ステージ自体を縦持ち時に縮小する方式に切り替えたことで `slideDesign.tsx` を触らずに済んだ**。リスク最小化。各 Deck (Intro / Pitch / Sending) も無変更。

## 何を変えたか

### 1. 論理ステージサイズの動的切替

| モード | 論理サイズ | 用途 |
|---|---|---|
| 横持ち / PC (従来) | 1280 × 720 (16:9) | コンテナ実寸が横長 (w/h >= 0.85) |
| **縦持ち / iPhone (新規)** | **420 × 747 (9:16)** | コンテナ実寸が縦長 (w/h < 0.85) |

`recalcScale()` でアスペクト比を判定して `isPortrait` 状態を立て、ステージの width/height/aspect-ratio を切り替える。

### 2. 文字サイズの実効値 (数字根拠)

| 端末 | scale | `text-[18px]` の見た目 | `text-[44px]` の見た目 |
|---|---|---|---|
| iPhone 13 縦 (390×844) 改修前 | 0.305 | **5.49px ❌** | 13.42px |
| iPhone 13 縦 (390×844) 改修後 | **0.90** | **16.2px ✅** | 39.6px |
| iPhone 13 横 (844×390) 改修前 | 0.66 | 11.88px | 29.0px |
| iPhone 13 横 (844×390) 改修後 | 0.66 | 11.88px | 29.0px (変更なし) |
| PC (1280×720) | 1.00 | 18px | 44px (変更なし) |

横持ちと PC は完全に従来動作を維持。縦持ちでのみ論理ステージが縮んで scale が約3倍になり、本文が読めるサイズに着地。

### 3. 縦持ち時の細かな調整

- スライド内側のパディング: `px-14 pt-12 pb-8` → `px-8 pt-10 pb-6` (論理 420 幅に合わせて縮小)
- スライドタイトル: `text-[44px]` → `text-[36px]` (論理 420 幅で 1 行に収まりやすく)
- 本文エリア: `text-[18px]` → `text-[17px]` (僅かに縮小)
- credit (フッター): `flex-wrap` で 2 段表示OK、`gap-x-3 gap-y-1` で間隔調整
- 下部ドットインジケータ: 多数のドット → **「03 / 13」のページ番号表示に切替** (13個のドットが iPhone で潰れる問題を回避)
- 表示エリア外枠: `max-h-[80vh] mx-auto` で過度な縦伸びを防止

## 触っていないファイル (重要)

- `slideDesign.tsx` (プリミティブ部品群)
- `IntroSlideDeck.tsx` / `PitchSlideDeck.tsx` / `SendingPitchSlideDeck.tsx` (各 Deck コンテンツ)
- `app/admin/(shell)/sales/{intro,company,sending}/page.tsx` (配信ページ)

## 温存されている機能 (PC プレゼン体験は完全維持)

✅ F キー / ⛶ ボタン = 全画面 (擬似フルスクリーン含む)
✅ G キー = サムネイル一覧
✅ T キー = プレゼンタイマー
✅ 1-9 キー = ジャンプ
✅ ← → / Space / PageUp/Down / Home / End = 移動
✅ スワイプ移動
✅ ホイール移動 (フルスクリーン時のみ)
✅ URL ?slide=N / ?intro=N / ?pitch=N / ?sending=N 同期
✅ 上部バー (deckTitle / eyebrow / タイマー / グリッド / 全画面ボタン)
✅ アニメーション (slideIn / tileIn / reveal / countUp 等)

## 既知の制約 (CEO に共有しておく)

iPhone 縦持ち時、論理ステージが 420×747 と狭くなるため:

1. **各 Deck の `grid-cols-3` / `grid-cols-2` レイアウトは窮屈になる**
   - 写真ギャラリー (`PhotoShowcase`) は 3 列のまま 420 幅に押し込まれる → 各写真が約 130px に
   - 比較表 (`CompareRow`) の 3 カラムも同様
   - これは「文字が読める」を最優先した結果のトレードオフ
2. **`HeroSplit` の `max-w-[60%]` テキストエリア**は論理 420 × 60% = 252px に押し込まれる → タイトル `text-[44px]` は確実に折り返す
3. **完全対応は LP 化が必要** (Intro 13 枚 LP 化 = 16h)。本タスクは「とりあえず読める」レベルへの最小修正

## ビルド検証結果

```
$ npx tsc --noEmit         → エラーなし
$ npx eslint <2 files>     → 警告なし
$ npm run build            → 完走・全ルート生成成功
```

## CEO 確認用のテスト手順

1. dev サーバー起動
   ```bash
   cd "c:/VSCode/Project/ビジネス21"
   npm run dev
   # → http://localhost:3009
   ```
2. PC ブラウザで http://localhost:3009/admin/sales/intro を開く
3. Chrome DevTools で「iPhone 13」エミュレート (縦持ち) に切替
4. 文字が読めるか、ページ番号「01 / 13」が下部に出るか確認
5. F・G・T・1-9 キーが PC モードでまだ動くか確認 (1280px 幅以上で表示)

## ロールバック手順

問題があれば git で 1 コミット戻すだけで完了:
```bash
cd "c:/VSCode/Project/ビジネス21"
git checkout components/admin/SlideShell.tsx
```

(注: developer は git commit していない。CEO 確認後に手動でコミット推奨)

## 次のステップ (推奨)

| 順序 | アクション | 工数 |
|---|---|---|
| 1 | CEO が iPhone 実機で確認 | 0.5h |
| 2 | 問題なければ git commit + Vercel デプロイ | 0.5h |
| 3 | Intro 13 枚 LP 化 (advisor 提言の Phase 2) | 16h |
| 4 | 公開ルート `/sales/intro/<token>` 切出し | 4h |

## 参考

- 設計方針: [2026-05-11-business-21-slides-iphone-plan.md](2026-05-11-business-21-slides-iphone-plan.md)
- developer 依頼書: [2026-05-11-business-21-slides-iphone-dev-brief.md](2026-05-11-business-21-slides-iphone-dev-brief.md)
- 事業情報: [../business-21.md](../business-21.md)

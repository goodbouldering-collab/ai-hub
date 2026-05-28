# developer 依頼書 — B21 スライド プリミティブ clamp 化 (2026-05-11)

## このファイルの使い方

別セッションで developer エージェントを起動するときに、このファイルへのパスを渡せば必要な情報が全部入っている状態にする。

```
依頼例:
「c:\VSCode\Project\consul\work\2026-05-11-business-21-slides-iphone-dev-brief.md を読んで、書いてある通りに作業して」
```

## 前提認識

- 本番システム (外国人技能実習・監理団体) なので**慎重に**
- CEO 承認のうえ着手している
- 設計方針の親ドキュメント: [work/2026-05-11-business-21-slides-iphone-plan.md](2026-05-11-business-21-slides-iphone-plan.md)

## 触ってよいファイル (2 つだけ)

| パス | 役割 |
|---|---|
| `c:\VSCode\Project\ビジネス21\components\admin\slideDesign.tsx` | スライドプリミティブ部品群 |
| `c:\VSCode\Project\ビジネス21\components\admin\SlideShell.tsx` | スライド共通基盤 |

## 絶対に触らないファイル

- `IntroSlideDeck.tsx` / `PitchSlideDeck.tsx` / `SendingPitchSlideDeck.tsx` (各 Deck コンテンツ)
- `app/admin/(shell)/sales/{intro,company,sending}/page.tsx` (配信ページ)
- その他すべての B21 配下ファイル

## やること (実装スコープ)

### 1. SlideShell.tsx の論理ステージ viewport 化

**現状 (lines 71-72, 222-250, 304-322)**:
- `SLIDE_W = 1280` / `SLIDE_H = 720` 固定
- `recalcScale()` でコンテナ実寸に対して `Math.min(w/SLIDE_W, h/SLIDE_H)` の scale を算出
- ステージに `transform: scale(${scale})` を適用、論理サイズは 1280×720 固定

**変更**:
- `transform: scale()` 方式を**廃止**
- ステージは `width: 100%; aspect-ratio: 16/9` でコンテナにフィット (PC では今と同じ見た目)
- iPhone 縦持ち時 (実 width < 640px) は `aspect-ratio` を解除して `height: auto` にし、コンテンツが**縦に伸びる**形にする
- 内側のパディング (現状 `px-14 pt-12 pb-8` = 56px/48px/32px) を `px-[clamp(16px,4vw,56px)] pt-[clamp(20px,4vw,48px)] pb-[clamp(16px,3vw,32px)]` 相当に
- `recalcScale` / `useLayoutEffect` の ResizeObserver は不要になるので削除

**温存する機能 (絶対に壊さない)**:
- F キー = 全画面 (擬似フルスクリーン含む)
- G キー = サムネイル一覧
- T キー = プレゼンタイマー
- 1-9 キー = 該当スライドへジャンプ
- ← → / Space / PageUp/Down / Home / End = 移動
- スワイプ移動 (touchStart/touchEnd)
- ホイール移動 (フルスクリーン時のみ)
- URL ?slide=N / ?intro=N / ?pitch=N / ?sending=N 同期
- 上部バー (deckTitle / eyebrow / タイマー / グリッド / 全画面ボタン)
- 下部コントロール (前へ・ドット・次へ)
- credit (フッターのクレジット表示)

### 2. SlideShell.tsx の下部ドットインジケータ iPhone 対応

**現状 (lines 431-444)**:
- 全スライドぶんのドットを `flex` で並べる (Intro 13枚なら 13個並ぶ)
- iPhone 縦持ちで潰れる

**変更**:
- 画面幅 640px 未満では**ドット群を非表示**にして、代わりに `text-[12px]` で「3 / 13」のページ番号表示に切替
- sm: 以降は現状のドット群を表示

### 3. slideDesign.tsx のフォントサイズ clamp 化

**置換テーブル** (Grep で見つけたものを全部置換):

| 検索 (現状) | 置換 (新規) |
|---|---|
| `text-[12px]` | `text-[clamp(11px,2.4vw,12px)]` |
| `text-[13px]` | `text-[clamp(12px,2.6vw,13px)]` |
| `text-[14px]` | `text-[clamp(12px,2.6vw,14px)]` |
| `text-[15px]` | `text-[clamp(13px,2.8vw,15px)]` |
| `text-[16px]` | `text-[clamp(13px,2.8vw,16px)]` |
| `text-[18px]` | `text-[clamp(15px,3.2vw,18px)]` |
| `text-[19px]` | `text-[clamp(15px,3.4vw,19px)]` |
| `text-[20px]` | `text-[clamp(15px,3.4vw,20px)]` |
| `text-[26px]` | `text-[clamp(18px,4.5vw,26px)]` |
| `text-[44px]` | `text-[clamp(24px,6vw,44px)]` |
| `text-[56px]` | `text-[clamp(32px,8vw,56px)]` |
| `text-[64px]` | `text-[clamp(36px,9vw,64px)]` |

**SlideShell.tsx 内も同様に置換** (特に line 328 の `text-[44px]`、line 332 の `text-[18px]`)

**注意**:
- `text-[9px]` `text-[10px]` `text-[11px]` (`Eyebrow` 等の極小表示) は**そのまま**。iPhone で読めなくて問題ない用途
- Tailwind の標準クラス (`text-xs` `text-sm` 等) は触らない
- `text-` の後ろがピクセル値リテラルの場合のみ置換する

### 4. slideDesign.tsx の grid を iPhone 1 列化

| 部品 (関数名) | 現状 | 変更 |
|---|---|---|
| `PhotoShowcase` (line 608〜) | `columns=2/3/4` を `grid-cols-2/3/4` 固定 | iPhone 縦は強制 `grid-cols-1`、`sm:` で指定 columns に |
| `ImageMosaic` (line 642〜) | `grid-cols-[1.6fr_1fr]` | iPhone 縦は `grid-cols-1`、`sm:grid-cols-[1.6fr_1fr]` |
| `HeroSplit` (line 777〜) | `max-w-[60%]` でテキスト左寄せ | iPhone 縦は `max-w-full`、`sm:max-w-[60%]` |
| `ImageCarousel` (line 665〜) サムネ | `gridTemplateColumns: repeat(${Math.min(total, 8)}, ...)` | iPhone 縦は最大 4 列、`sm:` で 8 列 |
| `FlagWall` (line 853〜) | `grid-cols-3 sm:grid-cols-5` | **変更不要** (既に対応済み) |
| `CompareRow` (line 209〜) | `grid-cols-[1.4fr_1fr_1fr]` | iPhone 縦は `grid-cols-1` で項目を縦並びに、`sm:` で現状 |

`HeroSplit` は背景画像の上にテキストが乗っているので、iPhone 縦持ち時は**背景画像の高さを `aspect-[4/3]` に、テキストはその下に通常配置**に変更する (現状 `absolute` で重なっている部分を `static` に切替)。

## やってはいけないこと

- ❌ 各 Deck (`IntroSlideDeck.tsx` 等) のレイアウト変更
- ❌ コンテンツの追加・削除・並び替え
- ❌ アニメーション (`animate-tile-in` `animate-reveal` 等) の削除
- ❌ Image Optimization (`unoptimized` 属性) の変更
- ❌ Tailwind 以外の依存追加
- ❌ [set-ports.js](set-ports.js) / `clients.code-workspace` への波及
- ❌ git commit / push (CEO が手動で行う)

## 検証手順

### Step 1: ローカルで型 + ビルド確認

```bash
cd c:\VSCode\Project\ビジネス21
npm run lint
npm run build
```

両方通ること。

### Step 2: dev サーバーで PC 表示確認

```bash
npm run dev
# http://localhost:3007/admin/sales/intro を Chrome で開く
```

確認項目:
- [ ] 上部バー / 下部コントロールが現状と同じ見た目
- [ ] F キーで全画面になる
- [ ] G キーで一覧が出る、もう一度 G で閉じる
- [ ] T キーでタイマーが動く
- [ ] 1〜9 キーでジャンプできる
- [ ] ← → で前後移動できる
- [ ] credit (フッター) が表示されている
- [ ] アニメーションが効いている (タイル進入・カウントアップ等)

### Step 3: Chrome DevTools で iPhone 13 (390×844) シミュレート

- [ ] タイトル文字が 24px 以上で読める
- [ ] 本文文字が 15px 以上で読める
- [ ] 横スクロールが出ない
- [ ] `PhotoShowcase` が 1 列で縦に並ぶ
- [ ] `ImageMosaic` が縦並びになる
- [ ] `HeroSplit` の写真とテキストが上下に分かれる
- [ ] 下部のページ番号 (例「3 / 13」) が表示される (ドットは非表示)

### Step 4: PR 作成 + Vercel Preview

- ブランチ名: `feat/slides-iphone-clamp`
- PR タイトル: `feat(slides): プリミティブを clamp() ベースに変更し iPhone 縦持ち対応`
- PR 本文に Vercel Preview URL を貼る
- **CEO が iPhone 実機で確認するまでマージしない**

## 想定工数

4 時間 (実装 2h + 検証 2h)

## 完了報告フォーマット

完了時、以下を [work/](work/) に追記:

```
ファイル: work/2026-05-11-business-21-slides-iphone-result.md
内容:
- 変更した 2 ファイルの diff サマリ (行数増減)
- PR URL
- Vercel Preview URL
- 検証項目のチェック結果
- 想定外に触れざるを得なかった箇所があれば理由付きで明記
```

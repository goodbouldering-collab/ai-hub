# ビジネス21 スライド iPhone 対応 — 設計方針 (2026-05-11)

## 確定方針 (CEO 承認済み)

| 項目 | 確定内容 |
|---|---|
| 主用途 | URL を送ってクライアントが iPhone (縦持ち優先) で閲覧 |
| 対応レベル | 縦持ちも横持ちも快適 |
| Intro (13枚) | **LP 型 (縦スクロール 1 本) に全面リニューアル** |
| Pitch | スライド維持のまま viewport ベースに移植 |
| Sending | 保留 (受注実績が出てから着手判断) |
| 配信ルート | `/admin/sales/*` のまま (公開ルート分離はいったん保留) |
| 今回スコープ | **プリミティブ clamp 化のみ (4h)**。LP 化は別セッション |

## 致命傷の数字根拠

- SlideShell は論理 1280×720 固定 → `transform: scale()` 縮小
- iPhone 13 (390px) で **scale ≒ 0.305**
- `text-[18px]` (本文) → **5.49px** に潰れる (Apple HIG 推奨 15px の 37%)
- `text-[44px]` (タイトル) → **13.4px** (推奨を下回る)
- `text-[12px]` (フッター) → **3.6px** (判読不能)

## advisor の段階計画 (全体像・参考)

```
今週: プリミティブ clamp 化 (4h) + Intro LP 化 (16h) + 公開ルート切出し (4h) = 24h
来週: Pitch viewport 移植 (13h)
保留: Sending リニューアル (10〜15h)
```

→ 今回は **「今週ぶんの最初の 4h」だけ実施**。

## 今回着手する変更箇所 (プリミティブ clamp 化)

### 対象ファイル
- `c:\VSCode\Project\ビジネス21\components\admin\slideDesign.tsx` (924行)
- `c:\VSCode\Project\ビジネス21\components\admin\SlideShell.tsx` (488行)

### 変更内容 (実装は別セッション)

#### 1. SlideShell.tsx の論理ステージを viewport 連動に
- 現状: `SLIDE_W = 1280` / `SLIDE_H = 720` 固定 + `transform: scale()`
- 変更: コンテナの実サイズで描画 (scale 廃止)。横持ち PC では `max-width: 1280px; aspect-ratio: 16/9`、iPhone 縦持ちでは `width: 100%; height: auto` で**コンテンツが下に伸びる**形にする
- 上下バー (上部バー / 下部コントロール) はそのまま。F=全画面・G=一覧・T=タイマー・1-9 ジャンプは PC で温存
- iPhone 縦持ち時は左右ホットゾーン (`w-[10%]`) を**下部の「前へ / 次へ」ボタンに集約**(現状は上下バーにあるので追加変更は最小)

#### 2. slideDesign.tsx のフォントサイズを clamp() 化
固定 px を以下の clamp() に置換 (横持ち PC は現状維持、iPhone で読めるサイズに):

| 現状 | 置換後 |
|---|---|
| `text-[12px]` | `text-[clamp(11px,2.4vw,12px)]` |
| `text-[13px]` / `text-[14px]` | `text-[clamp(12px,2.6vw,14px)]` |
| `text-[15px]` / `text-[16px]` | `text-[clamp(13px,2.8vw,16px)]` |
| `text-[18px]` / `text-[19px]` / `text-[20px]` | `text-[clamp(15px,3.4vw,20px)]` |
| `text-[26px]` | `text-[clamp(18px,4.5vw,26px)]` |
| `text-[44px]` (タイトル) | `text-[clamp(24px,6vw,44px)]` |
| `text-[56px]` / `text-[64px]` (BigStat) | `text-[clamp(36px,9vw,64px)]` |

#### 3. slideDesign.tsx の grid を sm: ブレークポイントで分岐
- `PhotoShowcase`: `columns=3` (デフォルト) は iPhone 縦で `grid-cols-1`、sm: 以降で `grid-cols-2`、md: で `grid-cols-3`
- `FlagWall`: 現状 `grid-cols-3 sm:grid-cols-5` → 既に対応済み。OK
- `ImageMosaic`: `grid-cols-[1.6fr_1fr]` → iPhone 縦は `grid-cols-1` で写真を縦並びに
- `HeroSplit`: `max-w-[60%]` → iPhone 縦は `max-w-full` で全幅、文字は写真の下に降ろす

#### 4. SlideShell の上部バー・下部コントロールの iPhone 対応
- 上部バーの `eyebrow` (現状 `text-[9px] sm:text-[10px]`) は OK
- 下部のスライドドットインジケータが 13個並ぶと iPhone で潰れる → 縦持ち時は「3 / 13」の数字表示に切替

### 変更しないもの (重要)
- 各 Deck (`IntroSlideDeck.tsx` / `PitchSlideDeck.tsx` / `SendingPitchSlideDeck.tsx`) のコンテンツ自体は今回触らない
- Intro の LP 化は別セッション (16h 想定)
- 公開ルート `/sales/<token>` 切出しは保留
- PC プレゼン体験 (F=全画面、G=一覧、T=タイマー、1-9=ジャンプ、← →=送り) は完全温存

## 確認テスト項目 (実装後)

| 端末 | 確認内容 |
|---|---|
| iPhone 13 縦 (390×844) | タイトル 24px 以上、本文 15px 以上で読める。横スクロール出ない |
| iPhone 13 横 (844×390) | 従来通り 16:9 でフィット |
| iPad 縦 (810×1080) | 余白が極端にならない |
| PC (1920×1080) | F キー全画面、G キー一覧、← →送り、T タイマー、1-9 ジャンプが全部動く |
| PC プレビュー (max-w-7xl) | 現状の見た目を維持 |

## 撤退・見直し基準 (advisor 提言)

- Intro LP 化完了後 1か月でクリック率が送付の 50% 未満 → 形式ではなく営業フロー側 (誰に・いつ送るか) を疑う
- プリミティブ clamp 化で iPhone 縦持ち時に既存 Deck が崩れる箇所が 10個 を超えるなら、LP 化を先行させた方が早い可能性 → 再判断

## 次のアクション

1. **本ドキュメントで方針確定** ← イマココ
2. CEO が実装着手を承認したら、別セッションで developer に依頼:
   - スコープ: 「`slideDesign.tsx` の clamp 化 + `SlideShell.tsx` の論理ステージ viewport 化」のみ
   - 触ってよいファイル: `slideDesign.tsx` / `SlideShell.tsx` の 2 ファイルだけ
   - 触ってはいけないファイル: `IntroSlideDeck.tsx` / `PitchSlideDeck.tsx` / `SendingPitchSlideDeck.tsx`
   - PR 化 → Vercel Preview URL を iPhone 実機で確認 → CEO 承認後にマージ

## 参考ファイル

- 共通基盤: `c:\VSCode\Project\ビジネス21\components\admin\SlideShell.tsx`
- プリミティブ: `c:\VSCode\Project\ビジネス21\components\admin\slideDesign.tsx`
- Intro Deck: `c:\VSCode\Project\ビジネス21\components\admin\IntroSlideDeck.tsx`
- Pitch Deck: `c:\VSCode\Project\ビジネス21\components\admin\PitchSlideDeck.tsx`
- Sending Deck: `c:\VSCode\Project\ビジネス21\components\admin\SendingPitchSlideDeck.tsx`
- 配信ページ: `c:\VSCode\Project\ビジネス21\app\admin\(shell)\sales\{intro,company,sending}\page.tsx`
- 事業情報: `c:\VSCode\Project\consul\business-21.md`

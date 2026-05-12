# 2026-05-11 ビジネス21 スライド全画面再構築

## CEO 指示

「ビジネス21のスライドをPC同様に横向きで画面いっぱい使って再生できるようにはじめから再構築して」

## 真因の特定

CEO との確認で、本質課題は「スマホ横持ちでも 16:9 が画面いっぱい使えない」点。
当初提案された「ゼロから全部再構築（SlideShell + 3デッキで約 2000 行）」を、
**SlideShell.tsx の部分修正のみで解決可能**と判断（CEO 同意済）。

## 原因

`SlideShell.tsx` は全画面時 (`fullscreenActive`) も以下の構造を維持していた：

```
┌─────────────────────────────────┐
│ 上部バー (タイトル + ツール)        │ ← shrink-0 で常時固定領域
├─────────────────────────────────┤
│                                 │
│ ステージ (flex-1 min-h-0)         │ ← 残り領域を 16:9 で scale フィット
│                                 │
├─────────────────────────────────┤
│ 下部コントロール (ナビ + ドット)     │ ← shrink-0 で常時固定領域
└─────────────────────────────────┘
```

iPhone 横持ち (約 19.5:9 ≈ 844×390px) の場合：
- 縦 390px から上下バー約 96px を引いた **294px** が 16:9 ステージの高さ上限
- 計算上 `scale = min(844/1280, 294/720) = 0.408`
- 1280×720 のステージが **522×294px** に縮む（画面の 41% しか使えない）

PC フルスクリーン (1920×1080) では同様の計算で `scale ≈ 1.36` だが、
上下バー約 100px を引いても 980px なので **scale = 980/720 = 1.36** で実用上問題なし。
スマホ特有の縦狭問題だった。

## 修正内容（c:/VSCode/Project/ビジネス21/components/admin/SlideShell.tsx）

### 1. UI 表示 state 追加

```tsx
const [uiVisible, setUiVisible] = useState(true);
const uiHideTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

const flashUi = useCallback(() => {
  setUiVisible(true);
  if (uiHideTimer.current) clearTimeout(uiHideTimer.current);
  uiHideTimer.current = setTimeout(() => setUiVisible(false), 3000);
}, []);
```

### 2. 全画面突入時に自動非表示タイマー起動

```tsx
useEffect(() => {
  if (fullscreenActive) flashUi();
  else { setUiVisible(true); /* clear timer */ }
  return () => { /* cleanup */ };
}, [fullscreenActive, flashUi]);
```

### 3. コンテナ・ステージ構造の変更

- **コンテナ**: 全画面時は `flex flex-col` を外し、子要素を absolute 配置にできるよう変更
- **上部バー**: 全画面時 `absolute top-0 left-0 right-0 z-30 transition-opacity opacity-0/100`
- **下部コントロール**: 全画面時 `absolute bottom-0 left-0 right-0 z-30 transition-opacity opacity-0/100`
- **ステージ親**: 全画面時 `absolute inset-0` で **100vw × 100dvh** 占有

### 4. UI 一時表示のトリガー

- マウス移動 (`onMouseMove`) — PC プレゼン時
- タップ開始 (`onTouchStart` で `flashUi()`) — スマホ操作時
- フェードアウトまで 3 秒

### 5. 全画面ヒント (← → · F · G · T) も uiVisible 連動でフェード

## 修正後の挙動

| 状況 | 結果 |
|---|---|
| PC 全画面 | 1920×1080 をフルに使う。マウス静止 3 秒で UI フェードアウト |
| iPhone 横持ち全画面 | 844×390 をフルに使う。`scale ≈ 0.541` (16:9 ≈ 693×390px、画面占有率 81%)。残り 21% は左右黒帯（16:9 維持の宿命） |
| iPhone 縦持ち | 既存の「端末を横向きにしてください」オーバーレイで強制誘導（維持） |

## 動作確認のお願い

ローカル devサーバー: `http://localhost:3007/admin/sales/intro` ほか
（VSCode 起動時に自動起動済み）

- [ ] PC: `F` キーで全画面 → 上下バーが 3 秒で消え、戻りはマウス移動 / `F` で解除
- [ ] iPhone 横持ち: 右上 `Maximize2` ボタンで擬似全画面 → 16:9 が画面 81% を占有
- [ ] スワイプでページ送り、タップで UI 一時表示
- [ ] サムネイル一覧 (`G`)・タイマー (`T`)・キーボード操作が従来通り

問題なければコミット (まだ未コミット)。

## コミット候補メッセージ

```
feat(business-21/slide): 全画面時に上下バーを overlay 化しスマホ横持ちでも 16:9 を画面いっぱいに

- SlideShell 全画面時の上下バー / コントロールを absolute overlay 化
- 3 秒経過で自動フェードアウト・マウス移動/タップで一時表示
- ステージ親を absolute inset-0 化し画面 100% 占有
- iPhone 横持ち占有率 41% → 81% に改善 (16:9 維持の左右黒帯のみ)
```

## 未対応 (CEO の方針確認次第)

- 「画面 100% (16:9 以外も埋める)」が必要なら、デッキ側を「フルブリード対応」に作り直す必要あり (現状は 1280×720 固定論理サイズ)。今回の修正範囲外

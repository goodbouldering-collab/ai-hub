# 制作物: AIハブ ヒーロー画像 SVG実装設計仕様書

## 用途

- `ai-hub-jp.vercel.app/` トップページ Hero セクションの右カラム画像
- 既存の `<img>` or `<div>` 枠をインラインSVGに差し替える
- 外部デザイナーには渡さない。Claude（実装担当）がこの仕様書でSVGを直接コーディングする

## サイズ・形式

- **viewBox**: `0 0 460 575`（4:5 比率 = 460 × 575px）
- **実装形式**: インラインSVG（`<svg>` タグをJSXに直書き）。外部ファイル読み込みでも可
- **border-radius**: 20px（親要素 `overflow: hidden` か SVG側 `<clipPath>` で角丸を実現）
- **最大幅**: 460px（既存枠の制約どおり）

---

## 配色（ブランド準拠）

### 背景レイヤー

| 役割 | カラーコード | 用途 |
|---|---|---|
| 最深背景 | `#0B0D14` | SVG全面の背景色。サイト背景と同一にして境界を溶かす |
| 中間背景（床面） | `#131A2E` | 人物が立つ「床」面。矩形で敷く |
| グリッド線 | `#1E2A45` | 奥行きグリッド線（後述）。opacity 0.6 |

### AI光・エネルギー系

| 役割 | カラーコード | 用途 |
|---|---|---|
| AI光 プライマリ | `#6E8BFF` | データ粒子・流れ線の始点色 |
| AI光 ミドル | `#9B7BFF` | グラデの中間 |
| AI光 エンド | `#C77DFF` | データ粒子・流れ線の終点色・glow |
| glow 外側 | `#C77DFF` + opacity 0.15 | `<feGaussianBlur>` で滲ませる発光リング |
| データ粒子 小 | `#6E8BFF` | r=3〜5 の円 |
| データ粒子 大 | `#9B7BFF` | r=8〜12 の円。中心に `#C77DFF` を重ねて内側発光 |

### 人物（アニメ調フラット）

| 部位 | カラーコード | 補足 |
|---|---|---|
| 肌（顔・手首） | `#E8C49A` | 浅い小麦色。ジブリ系の中間トーン |
| 肌影（顎下・首） | `#D4A877` | 肌色より30%暗く。1枚のみ使用 |
| 頭髪（白髪混じり） | `#8C929E` | 中年〜年配感。純白は使わない |
| シャツ（インナー） | `#2A3A5C` | ネイビー。背景に溶けず、かつ浮かない |
| ジャケット（アウター） | `#1C2840` | シャツより暗いネイビー。カジュアルビジネス |
| ジャケット内ライン | `#3A5080` | 折り返し・縫い目を1本線で表現 |
| ズボン | `#1A2035` | ほぼ背景色。下半身を溶かして上半身に集中 |
| アウトライン（輪郭線） | `#F0F4FF` + opacity 0.9 | stroke-width 2〜2.5。鉛筆描き風 |
| 目（白目） | `#F0F4FF` |  |
| 目（瞳） | `#2A3A5C` | 小さく丸く。過度なハイライトなし |
| 眉 | `#8C929E` + opacity 0.9 | 太さ stroke-width 3 |
| 口 | `#C49070` | 薄く閉じた口。笑顔は「口角が 3px 上がる程度」 |

### ドキュメントスタック（背景オブジェクト）

| 役割 | カラーコード | 用途 |
|---|---|---|
| 書類（山積み） | `#1E2A45` | 薄い矩形。複数枚ずらして重ねる |
| 書類の線 | `#2A3A5C` | stroke-width 1 の水平線。テキスト行を表現 |
| 書類スタック 右下 | `#6E8BFF` + opacity 0.12 | 「解決済み」書類を青みがかった色に |
| チェックマーク | `#2DCBA1` | 書類に重ねる `✓`。#2DCBA1 は既存サイトのセカンダリアクセント |

---

## 構図（レイヤー順・奥→手前）

```
Layer 1 (最奥): 背景グリッド
Layer 2:        glow リング（人物後方に円形発光）
Layer 3:        データストリーム（斜め流れ線）
Layer 4:        書類スタック（人物の左後方）
Layer 5:        人物（中央〜やや下寄り）
Layer 6:        データ粒子（人物の周囲・手元）
Layer 7 (最前): チェックマーク＋ラベル（小テキスト）
```

### 各レイヤーの配置（viewBox 0 0 460 575 基準）

#### Layer 1: 背景グリッド（奥行き感）

透視グリッドを `<line>` で描く。消失点は `(230, 200)`（上部中央）。
- 水平線: y=320, 360, 400, 440, 480, 520。x は 0→460。opacity 0.3
- 収束線（放射状）: 消失点から左端・右端・底角に向かって 8本。opacity 0.2
- 色: `#1E2A45`

これだけで「床面に立っている」奥行きが出る。

#### Layer 2: glow リング（人物の後光）

```
cx=230, cy=280
rx=160, ry=180 の楕円（縦長）
fill: radialGradient
  center: #9B7BFF opacity 0.25
  edge:   #0B0D14 opacity 0
```

`<feGaussianBlur stdDeviation="18"/>` を filter として適用。
人物の背後に青紫の柔らかい発光円が浮かぶ。

#### Layer 3: データストリーム（動きの核）

斜め左上→右下、または左下→右上方向の `<path>` 曲線を 6〜8 本。

描き方:
```
M 60 480 C 140 380 200 300 280 180   ← ベジェ曲線
```
- stroke: `url(#streamGrad)` （グラデ: `#6E8BFF` → `#C77DFF`）
- stroke-width: 1.5〜2
- fill: none
- opacity: 0.55
- stroke-dasharray: `8 6`（破線。「流れ」感を出す）

`<linearGradient id="streamGrad">` を `<defs>` に定義しておく。

**アニメーション（後述）を入れる場合**: stroke-dashoffset に CSS animation。

#### Layer 4: 書類スタック

画面左下（x=30〜130, y=400〜540）に書類の束を描く。

1枚の書類 = 角丸矩形 `<rect rx="4">` 幅90 高さ110
- 5枚を y 方向に -8px ずつオフセット（後ろの紙が上に出る）
- 下 3枚: fill `#1E2A45`
- 上 2枚: fill `#1A2840`
- 各矩形に水平 `<line>` 4本（y = 矩形top + 22/34/46/58）。stroke `#2A3A5C` width 1

右端の 1枚（スタック最上面）: `#6E8BFF` opacity 0.18。左下に小さな `✓` を配置（後述）。

#### Layer 5: 人物

**全身縦: 約 310px（y=150〜520）。中心 x=250（わずかに右寄り）**

ジブリ/フラットアニメの描き方原則:
- パーツは `<path>` または単純図形の組み合わせ。ベジェは控えめに
- アウトライン（輪郭線）は全パーツに `stroke="#F0F4FF" stroke-width="2.2" stroke-linejoin="round" stroke-linecap="round"`
- 内側の陰影は影色で別 `<path>` を1枚重ねるだけ（グラデなし）
- 表情は「目+眉+口」3パーツのみ。ノーズハイライト不要

```
[頭]
  cx=248, cy=200
  顔の輪郭: 楕円 rx=46, ry=52 (やや縦長)  fill=#E8C49A
  頭髪: 頭上をカバーする <path>。前髪は直線的に切り落とした形。fill=#8C929E
  左目: cx=232, cy=200  r=8 (白目) + r=4 (瞳)
  右目: cx=264, cy=200  r=8 (白目) + r=4 (瞳)
  眉: 目の 12px 上を水平に 14px。stroke=#8C929E width=3
  口: 顎から 25px上。cx=248, 横幅 14px。わずかに口角 up

[首〜胴体]
  首: rect x=240 y=240 w=16 h=20 fill=#E8C49A (輪郭線あり)
  胴体: <path> で台形。肩幅 110px（y=260）→ 腰幅 85px（y=390）
    fill=#1C2840 (ジャケット)
    内側に fill=#2A3A5C のシャツ領域を narrow に差し込む（胸ポケ風）

[両腕]
  左腕: 体左端から斜め下に伸ばす。肘で少し曲がる。手先は y=370付近
    <path> で細長い四辺形。fill=#1C2840
    手首: 小楕円 fill=#E8C49A
  右腕: 体右端から斜め前に伸ばす。手先は y=350付近（書類に触れる位置）
    手首: 小楕円 fill=#E8C49A

[下半身]
  腰から足元はシンプルに。ズボン fill=#1A2035 で背景に溶け込ませる
  高さ y=390〜520。足先は省略または小さなブーツシルエットで止める
```

#### Layer 6: データ粒子

人物の右手周辺（x=280〜400, y=280〜420）と頭上（x=180〜300, y=80〜160）に散布。

- 小粒子: `<circle r="3">` fill `#6E8BFF`。10〜14個
- 中粒子: `<circle r="6">` fill `#9B7BFF`。4〜6個
- 発光粒子: 中粒子の上に同心円 `<circle r="10">` fill `#C77DFF` opacity 0.3 + `filter:url(#glowFilter)`
- `<defs>` に `<filter id="glowFilter"><feGaussianBlur stdDeviation="4"/></filter>` を定義

粒子の配置例（x, y）:
```
小: (290,310), (330,295), (360,320), (310,370), (380,355)
    (295,390), (340,410), (285,285), (370,290), (400,340)
中: (315,330), (355,310), (345,380), (390,370)
```

#### Layer 7: チェックマーク＋ラベル

書類スタック最上面の右下付近（x=95, y=490）に:
```xml
<text x="95" y="490" font-size="20" fill="#2DCBA1" opacity="0.9">✓</text>
<text x="112" y="490" font-family="Inter,sans-serif" font-size="11"
      fill="#2DCBA1" opacity="0.75">完了</text>
```

人物の右手が触れているあたり（x=310, y=355）に小さなラベル:
```xml
<rect x="300" y="338" width="72" height="22" rx="11"
      fill="#6E8BFF" opacity="0.18"/>
<text x="307" y="353" font-family="Inter,sans-serif" font-size="10"
      fill="#6E8BFF">自動化中...</text>
```

---

## アニメ調を出す5つのSVGテクニック

1. **アウトライン統一**: 全パーツに同じ stroke (`#F0F4FF`, width 2〜2.5, round cap/join)。線画の「手書き感」がアニメっぽさの最重要因子
2. **影は1枚・グラデなし**: 球体感を出さない。顎下・首の陰影は「影色パス1枚を重ねる」だけ。フラット映えする
3. **目の比率**: 目の直径を顔高さの20%程度にやや大きめに。アニメ顔は目が大きい。`r=8` (白目) が目安
4. **丸い輪郭・直線の髪**: 顔は楕円基調。髪は直線的なカット（「ぱっつん」「坊主寄り短髪」）で描くと、曲線多用のリアルCGと区別できる。中年のうっすら白髪混じりショートを推奨
5. **限定パレット**: 1レイヤーに使う色は3色以内。このイラスト全体で肌系2・服系3・AI光系3・背景系3の計11色。それ以上増やさない

---

## アニメーション仕様（CSS / SMIL）

実装はSVGに `<style>` タグを埋め込み、または外部CSSで制御。**3種のみ**。増やさない。

### 1. データストリーム流れ（ループ）

```css
.stream-line {
  stroke-dasharray: 8 6;
  stroke-dashoffset: 0;
  animation: streamFlow 3s linear infinite;
}
@keyframes streamFlow {
  to { stroke-dashoffset: -56; } /* (8+6)*4 = 56 で1サイクル */
}
```

`.stream-line` を Layer 3 の各 `<path>` に付与。速度は各線でずらす（`animation-delay: 0s / 0.5s / 1.0s / 1.5s`）。

### 2. 発光粒子の脈動（ブリージング）

```css
.glow-pulse {
  animation: glowPulse 2.4s ease-in-out infinite;
}
@keyframes glowPulse {
  0%, 100% { opacity: 0.3; r: 10; }
  50%       { opacity: 0.6; r: 13; }
}
```

Layer 6 の「発光粒子」（大きい `<circle>` 側）に付与。`r` アニメは SMIL `<animate>` でやる場合:
```xml
<animate attributeName="r" values="10;13;10" dur="2.4s" repeatCount="indefinite"/>
<animate attributeName="opacity" values="0.3;0.6;0.3" dur="2.4s" repeatCount="indefinite"/>
```

### 3. glow リングのゆっくり拡縮（呼吸感）

```css
.bg-glow {
  transform-origin: 230px 280px;
  animation: bgBreathe 4s ease-in-out infinite;
}
@keyframes bgBreathe {
  0%, 100% { transform: scale(1);   opacity: 1; }
  50%       { transform: scale(1.07); opacity: 0.75; }
}
```

Layer 2 の楕円に付与。ゆっくり膨らむ発光が「AIが生きている」感を出す。

---

## SVG defs テンプレート（実装時のコピー元）

```xml
<defs>
  <!-- データストリーム グラデ -->
  <linearGradient id="streamGrad" x1="0%" y1="100%" x2="100%" y2="0%">
    <stop offset="0%"   stop-color="#6E8BFF" stop-opacity="0.8"/>
    <stop offset="100%" stop-color="#C77DFF" stop-opacity="0.8"/>
  </linearGradient>

  <!-- 背景 glow -->
  <radialGradient id="bgGlowGrad" cx="50%" cy="50%" r="50%">
    <stop offset="0%"   stop-color="#9B7BFF" stop-opacity="0.25"/>
    <stop offset="100%" stop-color="#0B0D14" stop-opacity="0"/>
  </radialGradient>

  <!-- 粒子 glow filter -->
  <filter id="glowFilter" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="4" result="blur"/>
    <feMerge>
      <feMergeNode in="blur"/>
      <feMergeNode in="SourceGraphic"/>
    </feMerge>
  </filter>

  <!-- 背景 glow filter（大きめぼかし） -->
  <filter id="bgGlowFilter" x="-30%" y="-30%" width="160%" height="160%">
    <feGaussianBlur in="SourceGraphic" stdDeviation="18"/>
  </filter>

  <!-- 角丸クリップ（SVG全体） -->
  <clipPath id="heroClip">
    <rect width="460" height="575" rx="20" ry="20"/>
  </clipPath>
</defs>
```

---

## レイアウト確認図（ASCII）

```
460px
┌────────────────────────────┐
│ ···· 頭上 データ粒子 ·····  │ ← y=80〜150
│                             │
│        ╭───────╮           │
│        │  顔  │           │ ← y=165〜250
│        │  目眉 │           │
│        ╰───────╯           │
│       ╭──────────╮         │
│       │  胴体(上) │  ●●   │ ← y=255〜350  右手周辺に粒子
│       │  ジャケット│●●●   │
│       ╰──────────╯  [自動  │ ← ラベルバッジ
│       ╭──────────╮  化中] │
│  書類  │ 胴体(下) │        │ ← y=355〜520
│  ┃┃┃  │ ズボン   │        │
│ ✓完了  ╰──────────╯        │
│                             │
│ ═══════════════════════════ │ ← y=510 床面（グリッド収束）
└────────────────────────────┘
  消失点グリッド（透視線・奥）
```

---

## 避けるべき要素

| 要素 | 理由 |
|---|---|
| 暖色系（オレンジ・ピンク）アクセント | Notエステ系サイトとのトーン混濁 |
| リアルな陰影（グラデ多用・立体球体感） | アニメ調から外れ、完成品がCG合成っぽくなる |
| 顔のパーツ過密（鼻穴・耳の詳細・まつ毛） | ジブリ/フラット系の「省略の美」に反する |
| 書類スタックの立体的なドロップシャドウ | SVGが重くなる + デザイントーン(Linear型)と不一致 |
| 笑顔の誇張（歯が見える・満面スマイル） | 「IT苦手だが前向きな社長」の共感ライン。疲れが抜けてほっとした表情が適切 |
| AI要素のロボット感（回路基板・ギア・アイロボット） | 「人間がAIと協働」ではなく「機械に囲まれた人」に見える |
| テキスト要素の多用 | SVGにテキストを入れすぎるとモバイルで潰れる。上記2箇所（✓完了 / 自動化中...）のみ |

---

## 実装チェックリスト（developer渡し）

- [ ] `<svg viewBox="0 0 460 575" xmlns="...">` でインラインSVG開始
- [ ] `<clipPath id="heroClip">` で全体を角丸20pxでクリップ
- [ ] `<defs>` に上記グラデ・フィルタを全定義してから本体描画
- [ ] レイヤー順（Layer 1→7）を SVG のソース順と一致させる（下に書いたものが上に描画）
- [ ] アニメーションはCSS `@keyframes` / SMIL `<animate>` の2択で統一。JavaScript不要
- [ ] `prefers-reduced-motion` メディアクエリで全アニメを止める分岐を入れる
- [ ] SVG内のフォントは `font-family="Inter, 'Noto Sans JP', sans-serif"` のシステムフォントに留める（Webフォント読み込みをSVG内からしない）
- [ ] ファイルサイズ目安: インラインで 6〜10KB 以内（gzip前）。超えたら粒子数を減らす

---

## 委任関係

- コピー文（ラベル文言・alt テキスト）→ **writer**（現在の「自動化中...」は仮テキスト）
- CSSアニメのFPS調整・パフォーマンス検証 → **developer**
- このイラストのCV影響（AB テスト設計）→ **marketer**

## 参照

- ブランドカラー正本: [consul/work/2026-05-11-ai-hub-top-wireframe.md](consul/work/2026-05-11-ai-hub-top-wireframe.md) 配色方針セクション
- サイト世界観・トーン: [consul/ai-hub.md](consul/ai-hub.md)
- 既存ヒーロー枠の実装位置: `C:\VSCode\Project\ai-hub\` の Hero セクションコンポーネント

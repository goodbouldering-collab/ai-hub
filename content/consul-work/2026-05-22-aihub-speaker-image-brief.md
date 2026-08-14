# AIハブ 講師ビジュアル 生成指示書

## CEOが今すぐ動ける最短手順

1. **推奨はコンセプト案B「クライミング×テクノロジーの融合」**。下記「B. 推奨プロンプト（英語・1280×960px横長）」をそのままコピーして **DALL-E 3**（ChatGPTのImage生成）または **Midjourney** に貼る
2. 生成した画像を Supabase Storage `ai-hub-public` にアップロードし、ファイル名は `speaker-hero-2026.webp`（または .jpg）にする
3. [ai-hub/content/speaker.md](ai-hub/content/speaker.md) の frontmatter `avatar_url:` に生成画像のパブリックURLを記入し、`python site/build_site.py` → `git push` で本番反映

---

## 用途

- サイト: https://aiclimb.vercel.app
- セクション: 講師紹介セクション（トップページ Hero 直下 or 独立ページ `/speaker/`）
- 閲覧者: AI講習の受講検討者（滋賀県内の中小事業者）・取引先・メディア関係者
- 目的: 講師の顔写真の代替となる「世界観の象徴画像」。実写不要・アーティスティック寄り

---

## サイトデザイン文脈（参照元: [consul/work/2026-05-11-ai-hub-top-wireframe.md](consul/work/2026-05-11-ai-hub-top-wireframe.md)）

| 項目 | 値 |
|---|---|
| 背景色 | `#0A0F1C`（深いネイビーブラック） |
| カード背景 | `#131A2E` |
| 見出し文字 | `#F0F4FF` |
| アクセント1 | `#4D7FFF`（ブルー） |
| アクセント2 | `#2DCBA1`（テール） |
| グラデーション（サイト全体のポイントカラー） | `#2563eb` → `#8b5cf6` → `#ec4899`（青→紫→ピンク） |
| フォント | Noto Serif JP（見出し）/ Inter（数字・英語） |
| 禁止要素 | オレンジ単色・ドロップシャドウ多用・暖色系ホワイト・個人ポートフォリオ的「柔らかさ」 |

---

## コンセプト案3つ

---

### 案A: AIと人間の意志が交差する抽象空間

**狙い・雰囲気**
「自分でコードを書き、自分で動かす実装者講師」の本質を視覚化する。人間の手（クライミングで鍛えた指）とAIの光の粒子（ニューラルネットワーク的なノード）が交差する瞬間を抽象的に描く。「AIは道具であり、主役は人間」というスタンスを体現する構図。色調はサイトのグラデーション（青→紫→ピンク）に完全同化する。ポートフォリオ感がなく、未来テック企業のキービジュアルに近い格を持たせる。

**生成プロンプト（英語・Midjourney/DALL-E両対応）**

```
Abstract digital art, close-up of a human hand reaching upward toward a luminous neural network constellation.
The hand appears weathered and strong, as if belonging to a long-time climber and practitioner.
Floating data nodes and glowing connection lines form a cosmic web above the hand.
Color palette: deep navy black background (#0A0F1C), electric blue (#2563EB) to violet (#8B5CF6) to magenta-pink (#EC4899) gradient luminescence.
Light particles scatter like chalk dust.
Cinematic, ultra-detailed, 8K quality.
No text, no typography, no faces, no logos.
Aspect ratio 4:3 landscape orientation.
Style: contemporary digital art, sci-fi editorial, cold and precise yet with organic imperfection.

--ar 4:3 --style raw --q 2 --v 7
```

**DALL-E向け追記（日本語ヒント）**
「AIと人間の協働を象徴する抽象アート。手と光のネットワークが交差する。背景は深いネイビー黒。青→紫→ピンクのグラデーション発光。テキスト不要。横長4:3。」

**避けるべき要素**
- 温かい色（オレンジ・黄色・ベージュ）
- 笑顔アイコン・ロボットキャラクター
- 過度にリアルな顔・人体の全身像
- 白背景・明るいトーン

---

### 案B: クライミング×テクノロジーの融合（推奨）

**狙い・雰囲気**
由井辰美の最大の個性「クライミング歴30年 × AI実装者」を直接表現する。岩壁のテクスチャ（ボルダリングのホールドの形状）にデジタル回路やコードの光が走る構図。「現場主義」「手を動かす実践者」というキャラを視覚的に一撃で伝える。AIハブの改修後方向性（アーティスティック・最先端）にも最も合致する。講師セクションに置いたとき、プロフィール文「クライミング歴30年」との連動で閲覧者の理解が最速で完成する。

**生成プロンプト（英語・Midjourney/DALL-E両対応）**

```
Cinematic abstract artwork: textured rock surface of a bouldering wall, seen from a climber's close perspective.
The rock texture is overlaid with glowing circuit board patterns and flowing code streams, as if the stone and digital technology have fused together.
Chalk dust particles float in the air, dissolving into data particles and light fragments.
Color palette: base tones of deep charcoal and slate gray for the rock, illuminated by electric blue (#2563EB), violet (#8B5CF6), and neon pink (#EC4899) streaks of light flowing through the cracks.
Background fades into deep navy (#0A0F1C).
Mood: raw, powerful, cutting-edge, and slightly otherworldly.
No human face, no text, no logos.
Photorealistic digital art, 8K, ultra-detailed macro photography aesthetic.
Aspect ratio 4:3 landscape.

--ar 4:3 --style raw --q 2 --v 7
```

**DALL-E向け追記（日本語ヒント）**
「ボルダリング壁の岩肌クローズアップに、青→紫→ピンクの電子回路の光が走る合成アート。チョークの粉がデータ粒子に変わっていく。テキスト・顔・ロゴなし。横長4:3。暗いネイビー背景。」

**避けるべき要素**
- 人物・顔のアップ
- クライミング器具（カラビナ・ロープ）の過度な描写（スポーツイメージではなくビジネスイメージ優先）
- 明るい昼間の色調

---

### 案C: 彦根の地域性×デジタルの融合

**狙い・雰囲気**
「滋賀県彦根」という地方都市発信であることを強みとして前面に出す。彦根城の石垣や琵琶湖の水面を連想させる和のテクスチャを、AIの光の網で覆う構図。「地域密着×最先端テクノロジー」という逆張りの強みをビジュアルで体現する。みんなのWAや地域コミュニティ事業との文脈整合性が高い。講師の肩書き「彦根の経営コンサル」を知っている訪問者に刺さりやすいが、AIツールで再現精度がやや低い（和の情景はプロンプトが難しい）。

**生成プロンプト（英語・Midjourney/DALL-E両対応）**

```
Abstract digital-traditional fusion artwork: a Japanese castle stone wall (Edo period masonry style) seen at dusk, overlaid with a luminous network of AI data streams and glowing digital nodes.
The lake surface in the distance reflects both the setting sun and electric blue digital light.
The boundary between ancient stone and modern technology is deliberately blurred.
Color palette: stone gray and earthen brown as base, illuminated by electric blue (#2563EB), deep violet (#8B5CF6), and rose-pink (#EC4899).
Sky transitions from deep navy (#0A0F1C) to a faint gradient of aurora-like light.
No human figures, no text, no logos, no anime style.
Mood: contemplative, rooted, quietly futuristic.
Ultra-detailed digital art, 8K, wide cinematic composition.
Aspect ratio 16:9 landscape.

--ar 16:9 --style raw --q 2 --v 7
```

**DALL-E向け追記（日本語ヒント）**
「日本の城の石垣（江戸時代様式）に、青→紫→ピンクのAI光のネットワークが走る融合アート。遠くに夕暮れの湖。和とデジタルの境界が曖昧。人物・テキスト・ロゴなし。横長16:9。」

**避けるべき要素**
- 桜・富士山などのステレオタイプな日本的要素
- 「ジャパニーズ」感が前面に出すぎる民族的表現
- アニメ・ゲームアート的な彩色

---

## 推奨1案とその理由

**推奨: 案B「クライミング×テクノロジーの融合」**

理由を3点で述べる。

**1. 講師の個性を最速で伝える**
「クライミング歴30年のAI講師」という属性は、日本中を探しても極めて少ない組み合わせである。案Aは抽象度が高く、見た目だけでは「クライミング」「実践者」が伝わらない。案Cは地域性が強く、滋賀・彦根を知らない訪問者に文脈が届かない。案Bは岩壁というビジュアルモチーフだけで「クライマー」を即座に伝え、そこに走るデジタル光で「テクノロジー実践者」を重ねる。二つの要素が1枚の画像で完結する。

**2. サイトのダークトーン・グラデーションと最も調和する**
案Bはベースが岩の暗いグレーから深いネイビーへの移行で、サイト背景色`#0A0F1C`との境界が自然に溶け込む。白フェードや切り抜き処理が不要で、そのまま `object-fit: cover` で配置できる。案Cの「夕暮れ空」は暖色が混入するリスクがあり、サイトの禁止要素に触れる可能性がある。

**3. 「アーティスティックで最先端」への改修方向に合致する**
岩肌のリアルなテクスチャ + デジタルエフェクトの合成は、2024〜2026年のブランドビジュアルトレンド（物質性とデジタル性の融合）に正確に乗っている。ポートフォリオ的な柔らかさがなく、テック企業や先進的な経営者のブランドイメージを出せる。

---

## 配置仕様

### 推奨サイズ・形式

| 用途 | サイズ | アスペクト比 | 形式 |
|---|---|---|---|
| 講師セクション横並び（デスクトップ） | 1280 x 960 px | 4:3 | WebP（品質85）|
| 講師セクション全幅背景（モバイル） | 750 x 562 px | 4:3 | WebP（品質80）|
| OGP / SNS シェア時 | 1200 x 630 px | 1.91:1 | JPG |

4:3を基本とする。生成ツールが16:9しか出せない場合は中央クロップで対応可。

### Supabase Storage 配置

- バケット: `ai-hub-public`（パブリック・既存）
- ファイルパス（推奨）:
  - 本命: `speaker/speaker-hero-2026.webp`
  - OGP用: `speaker/speaker-hero-ogp-2026.jpg`
- アクセスURL形式: `https://<project-ref>.supabase.co/storage/v1/object/public/ai-hub-public/speaker/speaker-hero-2026.webp`

### 講師セクションでの配置パターン

**パターン1（推奨・デスクトップ）: 左右分割**
```
+-----------------------------+-----------------------------------+
|                             |  由井辰美                          |
|  [講師ビジュアル画像]         |  クライミングコンサル代表             |
|  4:3 横長                   |  ──────────────────               |
|  左カラム 50%               |  クライミング歴30年・9事業            |
|  高さ: 360〜480px           |  彦根拠点                           |
|                             |  ▶ 講習・資料を見る                  |
+-----------------------------+-----------------------------------+
```
- 画像は `border-radius: 12px` でわずかに丸める（完全角丸は避ける）
- ホバーエフェクトなし（静的でよい。動かすと安っぽくなる）

**パターン2（モバイル）: 全幅背景 + テキストオーバーレイ**
```
+------------------------------------------+
|  [講師ビジュアル画像・全幅背景]              |
|  （上から60%は画像・下から40%はグラデ黒）   |
|                                          |
|  由井辰美                                 |
|  クライミング歴30年・9事業                  |
|  ▶ 講習・資料を見る                        |
+------------------------------------------+
```
- 背景画像に `linear-gradient(to bottom, transparent 50%, #0A0F1C 100%)` を重ねてテキスト可読性を確保

**パターン3（将来・独立ページ `/speaker/`）: ヒーロー全幅**
- 画面幅100vw・高さ60vh で配置
- 画像は `object-fit: cover; object-position: center` で中央クロップ

### speaker.md frontmatter 差し替え

```yaml
avatar_url: "https://<project-ref>.supabase.co/storage/v1/object/public/ai-hub-public/speaker/speaker-hero-2026.webp"
```

既存の `build_portal.py` の `_render_speaker_section()` は `avatar_url` が空でない場合に `<img>` を描画する実装になっているため、URLを入れるだけで反映される。

---

## 著作権・商用利用上の注意

### ツール別の商用利用可否（2026年5月時点）

| ツール | 商用利用 | 注意点 |
|---|---|---|
| **DALL-E 3**（ChatGPT Plus / API） | 可（OpenAI利用規約で生成画像の権利はユーザーに帰属） | API経由の場合は使用量課金。ChatGPT Plus内なら月額内 |
| **Midjourney**（Pro / Mega プラン） | 可（Proプラン以上で商用利用可。Basicプランは企業年収$20,000超で商用不可） | Basicプランの場合は商用利用前にProへアップグレード |
| **Adobe Firefly** | 可（商用利用保証が明記されている） | Adobeアカウント要 |
| **Claude（Anthropic）** | 可（利用規約の範囲内） | このセッション自体は画像を生成しないため参考のみ |

### 利用上の推奨事項

- **生成ログを保存する**: プロンプトと生成画像を [consul/work/](consul/work/) に記録しておく。将来「どのツールで生成したか」が問われたときの根拠になる
- **モデル・人物の肖像権は不要**: 今回のプロンプトはすべて「顔・人物なし」で設計しているため、肖像権問題は発生しない
- **岩壁・建築の著作権**: 実在の岩壁や建物を写実的に再現した場合は建築物の著作権に注意が必要だが、今回は「ボルダリング壁の抽象的なテクスチャ」レベルの指示のため問題が生じる可能性は低い
- **再販・第三者への提供は禁止**: 生成画像はAIハブサイト内の使用に限定する。他事業のビジュアルとして転用する場合は再生成を推奨する

---

## 参照ファイル

- サイトデザイン方針: [consul/work/2026-05-11-ai-hub-top-wireframe.md](consul/work/2026-05-11-ai-hub-top-wireframe.md)
- 既存アバター指示書: [consul/work/2026-05-20-ai-hub-avatar-prompt.md](consul/work/2026-05-20-ai-hub-avatar-prompt.md)（200x200px円形アバター用・本ファイルとは別用途）
- 講師コンテンツ: [ai-hub/content/speaker.md](ai-hub/content/speaker.md)
- 事業情報: [consul/ai-hub.md](consul/ai-hub.md)

## 委任先

- 生成画像のサイト実装（`build_portal.py` 改修・レイアウト変更） → **developer**
- 講師セクションのコピー文（プロフィール・キャッチコピー） → **writer**（[ai-hub.md](ai-hub.md) のトーン参照）
- 配置パターンのCV率評価 → **marketer**

# 全11事業 ファビコン設計指示書

**作成日**: 2026-05-28
**作成者**: designer（by クライミングコンサル）
**用途**: 外部デザイナー・Midjourney / DALL-E / Gemini画像生成・Figma / SVG手書き、いずれにも渡せる粒度の仕様書
**対象事業**: グッぼる / プロギング / Notエステ / N-デザイン / ビジネス21 / カラット / ClimbHero / ファディー / みんなのWA / AIハブ / トラスト（計11事業）

---

## PART 0: ファビコン固有の絶対制約（全事業共通）

以下は11事業すべてに適用する不変ルール。個別仕様より優先する。

### 形の鉄則
- **最終的に16×16pxまで縮む**。16pxで潰れるものは採用しない
- **1事業=1モチーフ**。2つ以上の要素を並列に詰め込まない（例: 「家+握手+盾」を全部入れるのは論外）
- 文字を使うなら**1〜2文字まで**。英語フルネームも日本語社名も全てNG
- **細い線（strokeのみ・塗りなし）、多段グラデーション、テクスチャは潰れるので禁止**
- アウトライン頼みにしない。**塗りベース（fill主体）**で形を成立させる
- 余白は最小限。モチーフをキャンバスの60〜75%まで大きく取る

### 背景の鉄則
- 背景は**単色塗り**または**角丸の単色塗り（rounded square, rx=20〜25%相当）**が基本
- 透過背景版（背景なしのモチーフのみ）も必ず併記する
- ダーク/ライト両対応: ブラウザタブは白背景にも黒背景にもなる。どちらでも視認できる高コントラストを確保

### 配信形式（全事業共通）
| ファイル | サイズ | 備考 |
|---|---|---|
| `favicon.svg` | ベクター正本 | 全サイズの親。これを起こしてから書き出す |
| `favicon-32x32.png` | 32×32px | ブラウザタブの主用途 |
| `favicon-16x16.png` | 16×16px | 極小時の品質確認用 |
| `favicon.ico` | 16+32px多重 | 旧ブラウザ対応・`<link rel="shortcut icon">` |
| `apple-touch-icon.png` | 180×180px | iOS ホーム追加。背景塗りを付ける（透過NG） |
| `icon-192.png` | 192×192px | PWA manifest（Android） |
| `icon-512.png` | 512×512px | PWA manifest（スプラッシュ・ストア） |

**書き出しフロー**: `favicon.svg`（ベクター正本）→ 各PNGに書き出し → `favicon.ico`生成（ImageMagick: `convert favicon-32x32.png favicon-16x16.png favicon.ico`）

---

## PART 1: グルーピングとモチーフ被り防止方針

11事業を4グループに分類し、色とモチーフの被りを管理する。

### グループA: クライミング系（3事業）
グッぼる / プロギング / ClimbHero

**方針**: 3事業ともクライミングモチーフだが、「静物（ホールド形状）」「動き（ロープ/人）」「メディア（再生ボタン）」で必ず描き分ける。色は暖色帯・寒色帯・中間で分散させ、同じ色相にしない。

### グループB: 彦根ローカル系（4事業）
N-デザイン / みんなのWA / ファディー / トラスト

**方針**: 全員が「地域×人」系。N-デザインは家、トラストは盾（or抽象的な家）、みんなのWAは輪、ファディーはFレターで完全に差別化。色は青×緑（N-デザイン）、橙×茶（みんなのWA）、ネイビー×白（ファディー）、エメラルド×白（トラスト）で4色分散。

**N-デザイン vs トラスト「家モチーフ被り」対策**:
- N-デザイン: 「N」の頭文字を三角屋根で象る。要素は「文字+屋根」の組み合わせ型
- トラスト: 盾形（shield）を採用し家を回避。不動産仲介+福祉GHという2業態の「守る・守られる」がモチーフ
- 16pxで見たとき: N-デザインは"N"と読める、トラストは盾と読める。混同しない

### グループC: 美容/商取引（2事業）
Notエステ / カラット

**方針**: 両者ともに「高級感・質感」が共通テーマだが、Notエステはゴールド系×曲線（蝶/花びら）、カラットはダイヤモンド形×透明感（薄い背景に濃いシルエット）で質感の方向性を分ける。

### グループD: BtoB/基盤（2事業）
ビジネス21 / AIハブ

**方針**: 両者ともにシアン〜インディゴ帯を使う計画。ビジネス21は「人・橋」モチーフ（数字21を使う案も可）、AIハブは「ハブ=放射状ノード」で幾何学的に。同じ青系でも彩度・明度を意図的にずらし、ビジネス21を「明るい空色」、AIハブを「深い宇宙色」で差別化する。

---

## PART 2: 各事業ファビコン設計仕様

---

### 01. グッぼる（クライミングジム+ショップ+カフェ）

**【コンセプト1行】**
「本気のクライマーが選ぶ場所」の力強さを、ホールドの断面シルエット一発で伝える

**【メインモチーフ】**
クライミングホールド（ジャグ型またはピンチ型）の正面シルエット。16pxで「丸っこい塊に穴」と読める輪郭にする。カラビナやロープは補助として使うが、16pxでは消す前提でSVGレイヤーを分けておく。

**【配色】**
- 背景: `#1a1a1a`（チャコールブラック。岩の質感・暗さ・重力感。クライミングは物理の極地なので黒が正直）
- 前景（ホールド）: `#f97316`（バーントオレンジ。クライミングチョークの白でなくホールドの塗装色。32×32で視認する最小面積でも飛んでくる暖色）
- ハイライト（省略可）: `#fcd34d`（環境光のエッジに1〜2pxだけ、16pxでは省略）

根拠: グッぼる本店サイト（goodbouldering.com）のトーンは「岩・チョーク・汗」。金属光沢や淡いパステルは文脈外。黒+オレンジは工業・スポーツブランドの王道高コントラスト色。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, simple background, no text, climbing hold silhouette (jug type), bold orange (#f97316) shape on dark charcoal (#1a1a1a) rounded square background, seen straight-on, solid fill, no gradient, crisp edges, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#1a1a1a"/>` で背景
- ホールドのジャグ型: 縦55×横65程度の横長丸みパスを中央よりやや上（cy=45）に配置
- 下部に穿孔（スクリューホール）: `<circle cx="50" cy="48" r="8" fill="#1a1a1a"/>` で塗りを抜く
- 塗り一色で完結（グラデなし）

**【避けるべきこと】**
- ロープとカラビナとホールドを全部入れる（32pxで何も判別できなくなる）
- ジムの「G」文字を入れる（事業名がひらがな「ぐっぼる」なので英字との整合性が取れない）
- 淡い緑系（クライミングフォームの色）を使う（弱い・業種が伝わらない）

---

### 02. プロギング（クライミング系・グッぼる同型）

**【コンセプト1行】**
グッぼると同じクライミング系だが「ロープのルート」で動きを表現し、明確に別事業と識別させる

**【メインモチーフ】**
クライミングロープのジグザグ（ルートを上から見たS字）シルエット。太い曲線2〜3本で「登る動線」を表す。ホールド単体ではなくロープ/ルートという「行為」にフォーカスすることでグッぼると差別化。

**【配色】**
- 背景: `#0f172a`（ディープネイビー。夜岩・屋外クライミングの空の色。グッぼるの黒と隣接するが青みで差別化）
- 前景（ロープ）: `#22d3ee`（シアン。ロープの鮮やかな色を忠実に。青系背景に白ではなく明るいシアンで視認性確保）

根拠: plogging.jp の業態はグッぼると同系だが、独自ドメインを持つ別ブランド。ロープモチーフ+ネイビー×シアンはグッぼるのチャコール×オレンジと色相・彩度の両軸でずれており混同しない。ロープの動きが「プロギング（行為系）」の語感とも合致。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, simple background, no text, climbing rope zigzag silhouette (bold S-curve viewed from above), bright cyan (#22d3ee) thick strokes on deep navy (#0f172a) rounded square background, solid fill, bold line weight, no gradient, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#0f172a"/>` で背景
- ロープ: `<path d="M25,80 Q35,55 50,50 Q65,45 75,20" stroke="#22d3ee" stroke-width="12" fill="none" stroke-linecap="round"/>` を基本形に、stroke-width=12で太く
- 16pxで「S字の曲線」と読めるよう振れ幅を大きく（小さいS字は消える）

**【避けるべきこと】**
- グッぼると同じホールドモチーフを使う（2事業が同一ブランドに見える）
- ロープを細い線で描く（16pxで完全に消える）
- プロギングの英語表記「Plogging」から「P」の文字を入れる（ぐっぼるに「G」がないとの非対称が生まれる）

---

### 03. Notエステ（エステサロン）

**【コンセプト1行】**
深いゴールドの上品さを、蝶の片翼シルエット一枚で表す

**【メインモチーフ】**
蝶の片翼（左右対称にせず右翼のみ）。フルの蝶は美容系で陳腐化しているが、片翼だけにすることで抽象度が上がり「Not（普通ではない）」というブランド名の異端性とも合う。翼の縁に大きな切れ込みはなく、丸みある単純な三角〜扇型で16pxに耐える形に単純化する。

**【配色】**
- 背景: `#1c1000`（極暗いウォームブラック。ゴールドを最大限に引き立てる最暗背景）
- 前景（翼）: `#b8860b`（指定の深ゴールド。暗背景との組み合わせで高コントラスト確保）
- ハイライトエッジ: `#e8b86f`（翼の縁に1〜2px、32px以上でのみ使用）

根拠: 指定色`#b8860b`（ダークゴールデンロッド）は明度が低いため、白背景に置くと視認性が下がる。ダークバック+ゴールドは「夜の高級感」のど真ん中で、エステ×女性客のターゲットに刺さる。ピンク`#f4c2c2`はアクセントカラーとして指定あるが16pxでは省略、180×512px版では翼内部のハイライトに使う。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, simple background, no text, single butterfly wing (right wing only, simplified bold silhouette), rich dark gold (#b8860b) shape on deep warm black (#1c1000) rounded square background, solid fill, elegant, no gradient, crisp edges, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#1c1000"/>` で背景
- 翼パス: 左端(25,70)を付け根に、頂点(60,20)を通り、右端(78,60)に降りてくる大きな扇型パス
- 内部に1本の翼脈（縦線のみ・16pxでは省略）
- 塗り`fill="#b8860b"`、stroke="none"で完全塗りつぶし

**【避けるべきこと】**
- フルの蝶（左右対称）を入れる（美容系ファビコンの最大公約数・差別化ゼロ）
- ピンク`#f4c2c2`を背景やメイン色にする（16pxで眼に優しすぎて視認性が崩壊）
- 細い花びら輪郭やレース模様（16pxで完全消滅）

---

### 04. N-デザイン（滋賀県彦根市の工務店）

**【コンセプト1行】**
「N」の縦画を三角屋根に置き換え、文字と建物が同時に読める一石二鳥の形

**【メインモチーフ】**
変形「N」字：左縦棒・右縦棒を地面に立てた柱とし、斜め棒の代わりに三角屋根のシルエットを被せる構造。16pxで「N」または「家」どちらかに読めれば成功。文字の縦棒を太くし（最低3〜4px幅）、屋根は等辺三角形で単純化。

**【配色】**
- 背景: `#2563eb`（指定のプライマリブルー。明るく信頼感がある。工務店＝地域の信頼が売り物）
- 前景（N+屋根）: `#ffffff`（白。青背景に白は最大コントラスト。16pxで確実に読める）
- アクセント（省略可）: `#10b981`（指定のエメラルドグリーン。屋根の頂点または棟に1点のみ・32px以上で使用）

根拠: `#2563eb`は指定色でありN-デザインのブランドカラーとして既にサイトで使用中。青+白は「清潔・信頼・地方工務店らしさ」の直球。グリーンのワンポイントは「自然素材・環境」という訴求とも一致する。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, simple background, no text, bold letter "N" with triangular roof replacing the diagonal stroke (house + letter hybrid), white (#ffffff) shape on bright blue (#2563eb) rounded square background, solid fill, thick strokes, no gradient, clean geometric, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#2563eb"/>` で背景
- 左縦棒: `<rect x="18" y="38" width="14" height="48" fill="#fff"/>` （底面が合う）
- 右縦棒: `<rect x="68" y="38" width="14" height="48" fill="#fff"/>`
- 三角屋根: `<polygon points="11,42 50,12 89,42" fill="#fff"/>`（N字の斜め棒を廃止して屋根に置換）
- 棟の緑点（省略可）: `<circle cx="50" cy="14" r="4" fill="#10b981"/>`

**【避けるべきこと】**
- 窓・ドア・煙突を描き込む（32pxで全部消える。家の「記号」にとどめる）
- N文字と家を並列に置く（どちらも読めなくなる。ハイブリッド形が前提）
- トラストと同じ盾や家形を採用する（グループB内での被りを招く）

---

### 05. ビジネス21（外国人技能実習・監理団体）

**【コンセプト1行】**
「21」という数字を太くシンプルに据え、BtoB業務システムの堅牢さと固有識別性を両立させる

**【メインモチーフ】**
数字「21」の太字組み合わせ。「2」と「1」を横に並べるのではなく、「21」全体を1つの塊として太いウェイトで中央配置。文字系モチーフは通常ファビコン向きでないが、「2+1=2文字以内」ルールの上限であり、業種（行政書類・制度番号・監理団体番号）との相性が良く、グループD内でAIハブとのモチーフ被りがない点で合理的。

**【配色】**
- 背景: `#0ea5e9`（指定グラデの中間色スカイブルー。単色で代表させる。グラデは16px以下で情報として機能しない）
- 前景（21）: `#ffffff`（白。青背景に白の最大コントラスト）
- サブカラー（省略可）: `#4f46e5`（指定のインディゴ。「2」と「1」の下線または影を32px以上でのみ使用）

根拠: 指定色のシアン→インディゴグラデを16pxで使うと色相差が1〜2pxに圧縮され判別不能になる。代表色を単一`#0ea5e9`に絞ることで視認性を担保し、同時に「コンプライアンス・行政・海外との橋渡し」という業種の誠実さを青系で表す。「21」は事業名の最終識別子として機能し、他10事業のどのファビコンとも被らない。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, high contrast, centered, simple background, bold number "21" in white (#ffffff) on sky blue (#0ea5e9) rounded square background, heavy font weight, solid fill, no decorative elements, no gradient, business-like, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#0ea5e9"/>` で背景
- テキスト: `<text x="50" y="68" text-anchor="middle" font-family="Arial Black, sans-serif" font-size="52" font-weight="900" fill="#fff">21</text>`（font-size 52でキャンバスに対し60〜65%の占有率）
- SVGのtextはフォント依存するため、本番はアウトライン化してパスに変換する（フォント埋め込みかoutlineが必須）

**【避けるべきこと】**
- 握手のイラストを入れる（16pxで手のシルエットは識別不能・国籍・人物を描くとステレオタイプリスクもある）
- 橋のシルエット（複雑なパスが16pxで消える）
- 指定グラデをそのままファビコンに使う（グラデは16pxで「ただの中間色」になる）

---

### 06. カラット（Shopify ストア）

**【コンセプト1行】**
ダイヤモンドの断面形（◇）一発で「価値・輝き・Carat」を同時に表す

**【メインモチーフ】**
ダイヤモンドのカットを正面から見た形（逆三角形ではなくファセット付き上面形: 六角形または八角形の幾何学形）。単なる◇よりもカット線を1〜2本入れることで「本物の宝石感」を出す。16pxでカット線が消えた場合は◇のシルエットだけで十分。

**【配色】**
- 背景: `#0c0c1a`（極暗いネイビーブラック。宝石の展示ケースの黒背景を連想させる）
- 前景（ダイヤ）: `#e0f2fe`（極薄い水色。透明な宝石が光を通す質感。白ではなくわずかに青みを持たせることで「カット面」の感触が出る）
- カット線（省略可）: `#7dd3fc`（水色やや濃いめ。ファセット境界線・32px以上でのみ使用）

根拠: 「カラット=carat」はダイヤモンドの重量単位であり宝石との連想は自明。Shopifyストアという購買文脈で「価値・特別感」を直球で伝える必要がある。暗背景+淡い水色は高級ジュエリーブランドの王道。「カラッと」という語感のカジュアルさとのギャップが差別化になる。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, simple background, no text, diamond gem silhouette (top-view faceted cut, octagonal), pale ice blue (#e0f2fe) on very dark navy black (#0c0c1a) rounded square background, solid fill with 1-2 subtle facet lines in (#7dd3fc), no gradient, luxury, crisp geometry, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#0c0c1a"/>` で背景
- ダイヤ上面（八角形）: `<polygon points="50,15 68,22 78,38 78,62 68,78 50,85 32,78 22,62 22,38 32,22" fill="#e0f2fe"/>`
- 中心のテーブルカット面: `<polygon points="50,30 62,36 62,64 50,70 38,64 38,36" fill="#bae6fd"/>`（内側を少し暗くして立体感）
- 16pxに書き出す際、内側多角形は削除して外形のみ残す

**【避けるべきこと】**
- 一般的な◇（Playing card diamond）を使う（安っぽい・宝石感が出ない）
- 黄色いゴールドカラーを使う（Notエステの深ゴールドと混同する）
- 4点の突起が鋭すぎる星型（宝石でなく星に見える）

---

### 07. ClimbHero（クライミング動画共有・グローバル）【刷新案】

既存ファビコン: 未確認（`public/favicon.svg`は存在せず、`favicon.ico`のみ確認）。本仕様は**刷新案**として位置づける。

**【コンセプト1行】**
「動画×クライミング」を「ホールド+再生ボタンの融合形」で表し、グローバルプラットフォームの即視性を確保する

**【メインモチーフ】**
ホールドの形状（丸みある塊）の内部に再生ボタン（右向き三角▶）を内包させたハイブリッド形。ホールドの外縁はグッぼるより大きく取り（キャンバス70%）、内部の▶は外縁から20%の余白で収める。16pxで「丸い塊の中に▶」と読める単純構成。

**【配色】**
- 背景: `#18181b`（ほぼ黒のジンク。動画プラットフォームの夜モードUI感。YouTubeの黒よりわずかに明るい）
- 外縁（ホールド）: `#dc2626`（レッド。クライミングの闘志・ヒーローというブランドの赤。グッぼるのオレンジと色相15〜20度のずれがあり区別できる）
- 再生▶: `#ffffff`（白）

根拠: ClimbHeroはグローバル配信・多言語・動画キュレーションというプラットフォーム性格を持つ。「英雄（Hero）」のレッドは動画系プラットフォーム（YouTube）との無意識の連想もあり、グローバルユーザーへの即時理解を促す。グッぼるのオレンジ`#f97316`と赤`#dc2626`は同じ暖色帯だが、色相・業種・モチーフの3軸で差別化できている（オレンジ=静物ホールド vs 赤=動画再生）。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, simple background, no text, climbing hold (rounded jug shape) silhouette with play button triangle (right-pointing arrow) embedded inside, red (#dc2626) hold outline on near-black (#18181b) rounded square background, white (#ffffff) play triangle fill, bold and clean, no gradient, readable at 16x16 pixels, global video platform feel
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#18181b"/>` で背景
- ホールド外縁: 楕円寄りの丸みパス（cx=50,cy=50, rx=36, ry=30程度）`fill="#dc2626"`
- 再生▶: `<polygon points="40,34 40,66 70,50" fill="#fff"/>` （三角の重心をやや右寄りに調整）
- ホールド穿孔（スクリューホール）は16px版では省略、32px以上で`<circle cx="50" cy="50" r="0"/>`（▶と重なるため割愛）

**【避けるべきこと】**
- 山のシルエット（ClimbHeroはアウトドアではなく動画プラットフォーム。山は業種を誤読させる）
- グッぼると同じオレンジ+黒配色（同じクライミング系で2事業が同一ブランドに見える）
- フィルムリールや映写機のアイコン（クライミング要素が消える）

---

### 08. ファディー（彦根プロジェクト・再生成中）

**【コンセプト1行】**
事業実体が形成途中だからこそ「F」の頭文字一文字で凛と立ち、後から業種が追加されても通用する汎用性を持たせる

**【メインモチーフ】**
「F」の太字1文字。事業詳細が薄い現在、特定業種のモチーフを入れるとブランド確定後の刷新コストが増える。「F」はFadie, Future, Firstなど多義的に解釈でき、地域系（彦根）との相性でNordic感のあるシンプル幾何学書体を選ぶ。ただの文字でなく、「F」の横棒を斜めにカットするか短くすることでロゴ感を出す。

**【配色】**
- 背景: `#1e293b`（スレートネイビー。深くて静か。「再生成中」=白紙という潔さをネイビーで表す。彦根ローカル系の中では最も沈んだ色で他3事業と差別化）
- 前景（F）: `#f8fafc`（ほぼ白の最明色。最大コントラスト確保）
- サブライン（省略可）: `#38bdf8`（薄いスカイブルー。「F」の横棒下に細い水平線を1本だけ・32px以上でのみ使用）

根拠: グループB（彦根ローカル系）の4事業で、ファディーだけが業種を確定していない。他3事業が家/輪/盾という具象モチーフを使う中、「F」のレタリングは**意図的な抽象**として機能し、リブランド耐性が最も高い。ネイビー×白はポルトガルのfadoとの語感的連想でも違和感がない（地中海のシンプルさ）。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single letter "F", high contrast, centered, simple background, bold geometric sans-serif capital letter "F" with slightly shortened lower crossbar for a distinctive logo feel, off-white (#f8fafc) on deep slate navy (#1e293b) rounded square background, solid fill, no gradient, versatile, timeless, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#1e293b"/>` で背景
- 「F」のパス: 縦棒（x=28, y=18, width=14, height=64）+ 上横棒（x=28, y=18, width=44, height=12）+ 中横棒（x=28, y=46, width=32, height=10）（下横棒は省略してロゴ感を出す）
- 全パス `fill="#f8fafc"`

**【避けるべきこと】**
- 彦根城や琵琶湖シルエットを入れる（地域固有すぎてブランド刷新後に使えない）
- 現時点で決まっていない業種モチーフ（店舗・花・食器など）を入れて後で後悔する
- 装飾的なセリフ体「F」（16pxでセリフが消えて全く別の文字に見える）

---

### 09. みんなのWA（彦根 異業種交流コミュニティ）【刷新案】

既存ファビコン: `favicon.svg`（オレンジ〜茶グラデの角丸矩形に2つの円弧で「和」を表す形。概念は良いが多段グラデーション+細い線が16pxで潰れるリスクがある）

**刷新方針**: 既存の「2つの円が交わる」コンセプトを引き継ぎつつ、細い線を太くし、グラデーションを単色に置き換えて16px耐性を持たせる。

**【コンセプト1行】**
交わる2つの太い輪で「異業種の出会い・和（WA）」を視覚化する。既存コンセプトを潰さず実装を強化する

**【メインモチーフ】**
2つの円が横に重なるヴェン図形（交差部を白く抜く）。円の直径はキャンバスの40%程度、stroke-width=10〜12で太く。16pxで「2つの丸」と読める最低限の単純さに落とす。既存SVGの「小さな白い交点circle」は継承してアイデンティティを残す。

**【配色】**
- 背景: `#b45309`（濃いアンバー。既存グラデの終端色`#9a3412`に近い暖色。単色に置き換えることで16px耐性を得る）
- 輪（stroke）: `#fef3c7`（極薄いクリーム。既存の`#fffbeb`を継承。白ではなく温かみのある白を保持）
- 交点: `#fff`（白点・中心に小さく）

根拠: 既存ファビコンは概念設計として優れている。グラデーションを単色に落とすだけで16px耐性が大幅に改善できる。コミュニティらしい「温かみのある橙」はグループB内でファディーのネイビー・N-デザインの青・トラストのエメラルドとの4色分散の中でも違和感なく機能する。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, simple background, no text, two overlapping circles (Venn diagram style, heavy stroke weight 10-12pt), cream/ivory (#fef3c7) thick ring outlines on amber brown (#b45309) rounded square background, white dot at intersection center, no fill inside circles, no gradient, warm community feel, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#b45309"/>` で背景（既存グラデを単色に置換）
- 左円: `<circle cx="36" cy="50" r="24" fill="none" stroke="#fef3c7" stroke-width="10"/>`
- 右円: `<circle cx="64" cy="50" r="24" fill="none" stroke="#fef3c7" stroke-width="10"/>`
- 交点白点: `<circle cx="50" cy="50" r="4" fill="#fff"/>`
- 16px書き出し時はstroke-widthを相対的に維持（ビューポートスケールで自動縮小される）

**【避けるべきこと】**
- 既存の多段グラデーションをそのまま継承する（16pxで色相情報が失われる）
- 「和」の漢字を入れる（1文字以内ルール内だが、漢字の複雑な画数が16pxで判読不能）
- 人物シルエットを複数配置する（グループ感を出そうとして全員が潰れる）

---

### 10. AIハブ（CEOポータル + AI集約パイプライン）

**【コンセプト1行】**
中心から6方向に均等放射するノード図で「ハブ=全事業の集約点」を一発で表す

**【メインモチーフ】**
中心の大きな丸（半径8〜10）から6本の放射線が伸び、各端点に小さな丸（半径4〜5）がある「ハブ＆スポーク」構造。神経細胞やWi-Fiシンボルに近いが、均等6方向にすることで「意図的な設計」感が出る。16pxで「中心丸+短い放射線」と読めれば十分。

**【配色】**
- 背景: `#0a0a1a`（宇宙黒。AIを「知識の宇宙」に喩える最暗色。ビジネス21のスカイブルー`#0ea5e9`と対極の深さで差別化）
- 中心ノード: `#818cf8`（インディゴ/パープル。AIの「知性・非日常・未来」を紫系で表現。青系でありながらビジネス21のシアンとは色相を30〜40度ずらす）
- 放射線+外周ノード: `#c7d2fe`（薄いラベンダー。中心より明るくすることで「中心→外への流れ」の方向性が生まれる）

根拠: AIハブはCEOポータルという「全事業の集約点」という役割を持つ（ai-hub.md記載）。ハブ&スポーク構造はその役割をそのまま視覚化している。宇宙黒+インディゴ紫はAI/テックのデファクトカラーを踏みつつ、ビジネス21のシアン系・N-デザインの青系とは色相帯が異なり混同しない。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, simple background, no text, hub and spoke diagram (large center circle with 6 evenly radiating lines ending in small circles), indigo purple (#818cf8) center node on deep space black (#0a0a1a) rounded square background, lavender (#c7d2fe) lines and outer nodes, solid fill, no gradient, neural network / AI hub feel, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#0a0a1a"/>` で背景
- 中心円: `<circle cx="50" cy="50" r="9" fill="#818cf8"/>`
- 放射線（6本、60度ずつ）: stroke="#c7d2fe" stroke-width="4" の6本
  - 例: `<line x1="50" y1="50" x2="50" y2="22" stroke="#c7d2fe" stroke-width="4"/>` を6方向に回転
- 外周ノード（6個）: `<circle cx="50" cy="22" r="4.5" fill="#c7d2fe"/>` を6方向に配置
- `<g transform="rotate(N, 50, 50)">` で60度ずつ繰り返す（N=0,60,120,180,240,300）

**【避けるべきこと】**
- 「AI」の文字を入れる（2文字ルールの上限・日本語ブランドなので英字2文字では伝わらない・ノード形の方が言語非依存で優れる）
- 立方体（3D cube）を使う（ClimbHero系の指定候補にもあったが、16pxで正六面体は頂点がノイズになる）
- 放射線を8本以上にする（16pxで隙間が消えて「黒い円」に見える。6本が限界）

---

### 11. トラスト（不動産仲介 + 障害福祉グループホーム）

**【コンセプト1行】**
「守る・信頼」をシールド（盾）1枚で表し、N-デザインの家モチーフとの混同を完全回避する

**【メインモチーフ】**
シールド（盾）の正面シルエット。上部が丸みを帯びた逆台形で、16pxで「縦長の丸い四角」として認識できる最単純形。内部に細い「T」の頭文字か、または中央の縦線1本（Shield chevron）を入れることでトラストの「T」を暗示させる（細い線は32px以上でのみ使用）。

**【配色】**
- 背景: `#ffffff`（白。不動産仲介+福祉という「公共性が高い2業態」に対して清潔感と開放性を優先。他10事業の中で白背景は唯一であり視認上の差別化になる）
- 前景（盾）: `#10b981`（指定のエメラルドグリーン。「安心・健康・福祉・成長」を表す緑。不動産の「買い手に寄り添う」姿勢とも合う）
- 内部ライン（省略可）: `#2563eb`（指定の青。盾内部の「T」字または縦線・32px以上でのみ使用）

根拠: N-デザインが`#2563eb`青+白で「家+N」を表すのに対し、トラストが白背景+`#10b981`緑+盾形を使うことで、3軸（背景色・前景色・モチーフ形）全てで差別化される。白背景は「ライトモードのブラウザで非常に映える」反面、ダークタブでは背景が沈むため、透過SVG版も必ず用意する（その場合は緑の盾だけが浮かぶ）。

**【画像生成AI用プロンプト（英語）】**
```
favicon, app icon, flat vector, minimal, single symbol, high contrast, centered, bold shield silhouette (security / trust / protection symbol, rounded top pentagonal shape), emerald green (#10b981) solid fill on white (#ffffff) square background, single thin vertical chevron line inside shield in blue (#2563eb), clean geometric, no gradient, trustworthy and professional, readable at 16x16 pixels
```

**【SVG実装メモ】**
- `<rect width="100" height="100" rx="22" fill="#ffffff"/>` で背景（ダーク対応版は `fill="#1e293b"` 別ファイル）
- 盾パス: `<path d="M50,16 L82,30 L82,58 Q82,80 50,90 Q18,80 18,58 L18,30 Z" fill="#10b981"/>` （上部が台形・下部が丸みで合流する形）
- 内部縦線（T暗示）: `<line x1="50" y1="34" x2="50" y2="72" stroke="#2563eb" stroke-width="5"/>` （32px以上でのみ）
- ダーク背景版（透過）: 背景rectを削除し盾fillを`#10b981`のまま使用

**【避けるべきこと】**
- 家のシルエットを入れる（N-デザインと即座に混同する。不動産=家という連想を断ち切ることが設計の核心）
- 握手マークを使う（ビジネス21で排除した理由と同様・16pxで手の形は識別不能）
- 盾を複雑にしすぎる（ライオンや紋章系の装飾は16pxでノイズになる。単純な外形が全て）

---

## PART 3: 書き出しサイズと実装チェックリスト

### 必要な書き出しサイズ一覧（全11事業共通）

| ファイル名 | サイズ | 形式 | 用途 | 優先度 |
|---|---|---|---|---|
| `favicon.svg` | ベクター | SVG | 正本・全PNG書き出しの親 | 最優先 |
| `favicon-32x32.png` | 32×32px | PNG (透過) | ブラウザタブ・メイン用途 | 最優先 |
| `favicon-16x16.png` | 16×16px | PNG (透過) | 品質確認・旧ブラウザ | 最優先 |
| `favicon.ico` | 16+32 多重 | ICO | `<head>`直置き・旧ブラウザ | 高 |
| `apple-touch-icon.png` | 180×180px | PNG (**背景あり**) | iOS ホーム追加（透過NG） | 高 |
| `icon-192.png` | 192×192px | PNG | PWA manifest (Android) | 中 |
| `icon-512.png` | 512×512px | PNG | PWA manifest スプラッシュ | 中 |
| `og-icon.png` | 任意（512〜1024px） | PNG | OGP画像等の補助素材 | 低 |

### Next.js (App Router) への実装例

```html
<!-- app/layout.tsx の metadata に追加 -->
export const metadata: Metadata = {
  icons: {
    icon: [
      { url: '/favicon-16x16.png', sizes: '16x16', type: 'image/png' },
      { url: '/favicon-32x32.png', sizes: '32x32', type: 'image/png' },
    ],
    apple: '/apple-touch-icon.png',
  },
}
```

```html
<!-- または app/layout.tsx の <head> に直書き -->
<link rel="icon" type="image/svg+xml" href="/favicon.svg" />
<link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
<link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
<link rel="apple-touch-icon" sizes="180x180" href="/apple-touch-icon.png" />
```

### SVGからPNGへの変換コマンド（Inkscape CLIまたはImageMagick）

```bash
# Inkscape (推奨・アンチエイリアス品質が高い)
inkscape favicon.svg --export-width=32 --export-filename=favicon-32x32.png
inkscape favicon.svg --export-width=16 --export-filename=favicon-16x16.png
inkscape favicon.svg --export-width=180 --export-filename=apple-touch-icon.png
inkscape favicon.svg --export-width=192 --export-filename=icon-192.png
inkscape favicon.svg --export-width=512 --export-filename=icon-512.png

# ICO生成 (ImageMagick)
magick convert favicon-32x32.png favicon-16x16.png favicon.ico
```

### 品質チェックリスト（実画像生成後に必ず確認）

```
[ ] 16px PNG を実際のブラウザタブ（白背景・通常モード）で表示して形が読める
[ ] 16px PNG を実際のブラウザタブ（ダーク/黒背景）で表示して形が読める
[ ] 32px PNG で意図したモチーフ・色が正確に確認できる
[ ] apple-touch-icon.png（180px）を iPhone ホーム追加して確認
[ ] 他10事業のファビコンと横並びにして「重複・混同なし」を確認
[ ] 白背景での視認性 OK（特にトラスト=白背景事業は逆を確認）
[ ] 透過背景版と背景あり版どちらも存在する
```

---

## PART 4: 次アクション一覧（CEOが選べる実施優先度）

実画像生成・SVG実装をどの事業から進めるか、以下の基準で一覧化した。CEOが優先度を選択して実行チームに渡す。

### ティア1: 即時実施推奨（既存サイトが本番稼働中・ファビコン未整備の可能性が高い）

| 事業 | 理由 | 難易度 |
|---|---|---|
| **N-デザイン** | 本番ドメイン`n-design.work`が稼働中（2026-05-15取得）。SVGメモが最も実装しやすい（矩形+三角形のみ） | 易（SVG手書き15分） |
| **みんなのWA** | `minanowa.com`稼働中・既存`favicon.svg`あり（刷新=単色化のみ）。既存コンセプト継承で手戻りゼロ | 易（既存SVG単色化10分） |
| **トラスト** | `trust-nine-tau.vercel.app`稼働中・ファビコン未設定の可能性大。盾パスは単純 | 易（SVG手書き20分） |

### ティア2: 近日実施（本番稼働中・ブランド確認後）

| 事業 | 理由 | 難易度 |
|---|---|---|
| **グッぼる** | `goodbouldering.com`がメインアセット。ホールド形状の単純化度合いのジャッジが必要 | 中（ホールドパスの造形） |
| **Notエステ** | `notesthe.vercel.app`稼働中。蝶翼パスはやや複雑・Midjourney使用推奨 | 中（翼パス or AI生成） |
| **ビジネス21** | `business21.vercel.app`稼働中。「21」テキストSVGは実装容易だがアウトライン化が必要 | 中（フォントアウトライン化） |
| **AIハブ** | `ai-hub-jp.vercel.app`稼働中・CEO向けポータルのトップ表示に直結 | 中（放射状ノードの座標計算） |

### ティア3: 次フェーズ（本番デプロイ前または業種が確定後）

| 事業 | 理由 | 難易度 |
|---|---|---|
| **ファディー** | Vercel枠のみ・未デプロイ。「F」レターは最単純だが事業確定を待って刷新しやすい形が吉 | 易（確定後即実施可） |
| **カラット** | `karatto.life`稼働中だがShopifyストアのfaviconはShopify管理画面から設定（PNG直接アップ） | 易（PNG512pxをShopify管理画面でアップ） |
| **プロギング** | `plogging.jp`稼働中・カラーミーベースのためfavicon設定はShop管理画面から | 中（カラーミーfavicon設定手順を確認） |
| **ClimbHero** | `project-02ceb497.pages.dev`稼働中・Cloudflare Pages設定で反映。刷新案採用の判断はCEO承認後 | 中（Cloudflare Pages公開ディレクトリへの配置） |

---

**以上。このドキュメントはビジュアル実制作のインプット専用。実際の画像生成・SVG作成・ファイル配置はdesignerの委任範囲外（実制作担当者 or Midjourney/DALL-E等へ渡すこと）。**

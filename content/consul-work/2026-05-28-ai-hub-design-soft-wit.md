# 制作物: AIハブ デザイン磨き指示書「しっとり柔らかく・専門性高く・黒の中のウィット」

## 用途
`site/build_portal.py` の `PORTAL_CSS` 定数を直接書き換える。
実装者は該当変数・セレクタを検索して当てはめること（フルリライトではなく差分パッチ）。

---

## 1. 硬さの原因診断（現状の問題点）

現状コードを精査して特定した「硬さの原因」5点。修正値は次節で詳述。

| # | 場所 | 現状値 | 問題の正体 |
|---|---|---|---|
| 1 | `--text: #0B0D14`（ライト）/ `--text: #F4F6FB`（ダーク） | 純黒・純白に近い | コントラスト比 21:1 近辺。ニュース記事なら適切だが「しっとり」には硬すぎ。目が疲れる |
| 2 | `line-height: 1.7`（body）/ `line-height: 1.85`（lead） | 行間がやや狭い | 日本語混在コンテンツでは 1.8〜1.95 が「ゆったり読める」ラインになる |
| 3 | `font-weight: 800`が多用されすぎ | h1/section-title/biz-card-name/pkg-title 全部 800 | ウェイト最強位をあちこちで連発すると、全部が「叫んでいる」ように見える。階層が失われ全体が硬い |
| 4 | `box-shadow` が単層かつ y が大きい | `0 10px 40px rgba(15,23,42,0.08)` | 影が1本で硬い。現実世界の影は拡散光+環境光の多層。ふわっとさせるには2〜3層化 |
| 5 | `transition: .2s` が支配的 | ほぼ全インタラクションが `.2s ease` | 短すぎると「ぱちぱちした」印象。`.3s〜.4s cubic-bezier(.22,1,.36,1)` にすると「しっとり動く」 |

---

## 2. カラーパレット改訂

### 2-A. ライトテーマ（`：root`）

現状の「青みがかった白に純黒」という組み合わせを、温度のある「磁器白に墨色」に移行する。

```css
:root {
  /* --- 文字色: 純黒から「深墨」へ --- */
  --text:      #1A1D2E;   /* 現: #0B0D14 → 青みのある深い墨。コントラスト比: 約16:1（十分）・目が柔らかく受け取る */
  --text-soft: #4A5270;   /* 現: #404A63 → 少し青みを増し「思慮深い」印象に */
  --muted:     #6E7A94;   /* 現: #5A6478 → 少し明るくして見切れ感を低減 */

  /* --- 背景: 白から「和紙白」へ --- */
  --bg-base:  #F5F6FA;    /* 現: #F7F8FC → わずかに彩度を下げる。印刷用紙のやわらかさ */
  --bg-white: #FEFEFE;    /* 現: #FFFFFF → 純白を1段下げ目の刺激を低減 */
  --bg-elev:  #FFFFFF;    /* 変更なし（カード自体は白を維持） */

  /* --- 影: 単層→多層ふわっと --- */
  --shadow-card:       0 2px 4px rgba(26,29,46,0.04), 0 8px 24px rgba(26,29,46,0.07);
  --shadow-card-hover: 0 4px 8px rgba(26,29,46,0.06), 0 20px 56px rgba(26,29,46,0.13), 0 0 0 1px rgba(84,104,255,0.18);

  /* --- ボーダー: 少し薄く、圧迫感を減らす --- */
  --line:        rgba(26,29,46,0.08);   /* 現: 0.10 → 少し薄く */
  --line-strong: rgba(26,29,46,0.13);   /* 現: 0.16 → 同様 */
}
```

### 2-B. ダークテーマ（`：root[data-theme="dark"]`）

「ただの黒」から「深夜の書斎」へ。墨・藍・チャコールに温度を持たせる。

```css
:root[data-theme="dark"] {
  /* --- 背景色群: 青みがかった墨の3層 --- */
  --bg-base:  #0C0E18;   /* 現: #0B0D14 → ほぼ同値だが青みを一段深く。「墨」 */
  --bg-white: #111422;   /* 現: #11131D → 藍味ある深夜色。「濡れた舗装」 */
  --bg-elev:  #171A2B;   /* 現: #161925 → カード面。「暗室の作業台」 */

  /* ★最重要変更: 文字色をクリームに近づける */
  --text:      #E8EAF2;  /* 現: #F4F6FB → 純白でなく「温かい灰白」。目の疲労が大幅に減る */
  --text-soft: #9BA5BE;  /* 現: #A6AEC4 → わずかに温度を持たせる */
  --muted:     #5E6880;  /* 現: #6B7488 → 少し明るく（暗すぎる muted は読めなくなる） */

  /* --- 影: ダークは影を深く・でもふわっと --- */
  --shadow-card:       0 2px 8px rgba(0,0,0,0.24), 0 10px 32px rgba(0,0,0,0.32);
  --shadow-card-hover: 0 4px 12px rgba(0,0,0,0.32), 0 20px 60px rgba(0,0,0,0.48), 0 0 0 1px rgba(139,160,255,0.20);

  /* --- グロー: 少し落ち着かせる --- */
  --glow: 0 0 48px rgba(110,139,255,0.28);  /* 現: 0.35 → 輝きすぎを抑制 */

  /* --- ボーダー --- */
  --line:        rgba(255,255,255,0.07);  /* 現: 0.08 → わずかに薄く */
  --line-strong: rgba(255,255,255,0.12);  /* 現: 0.14 → 同様 */
}
```

**ダークテーマの「温度」の根拠**:
- `#0C0E18` は RGB(12, 14, 24)。B チャンネルが R/G の2倍。純黒(0,0,0)と異なり「藍の深さ」がある
- 文字を `#E8EAF2`（わずかに紫みがかったクリーム）にすることでダーク背景との差が「冷たい白 vs 深い黒」でなく「温かみのある対比」になる
- この色遣いは Raycast / Linear / Vercel ダッシュボードの高品質ダークUIで使われている手法

---

## 3. タイポグラフィ調整

### font-weight の階層化（最重要）

現状は h1/section-title/card-name すべて `font-weight: 800`。階層がなく「全部が主役」になっている。

```css
/* 現状 → 改訂後 */
.hero h1               { font-weight: 800; }  /* 維持: ページ最上位なのでそのまま */
.section-title         { font-weight: 700; }  /* 現: 800 → 1段下げ。h1 との差を作る */
.biz-card-name         { font-weight: 700; }  /* 現: 800 → 同上 */
.pkg-title             { font-weight: 700; }  /* 現: 800 → 同上 */
.service-name          { font-weight: 700; }  /* 現: 800 → 同上 */
.diag-result-name      { font-weight: 800; }  /* 維持: 診断結果は強調してよい */
```

### 行間・字間

```css
body {
  line-height: 1.82;           /* 現: 1.7 → 日本語混在に余裕を持たせる */
  letter-spacing: -0.004em;   /* 現: -0.005em → 微調整のみ */
}

.hero .lead {
  line-height: 1.95;           /* 現: 1.85 → もっとゆったり */
  font-size: clamp(14px, 1.5vw, 16.5px);  /* 現: 16px → 0.5px 拡大 */
}

.pkg-desc {
  line-height: 1.82;           /* 現: 1.7 → 一致させる */
}

.section-sub {
  line-height: 1.9;            /* 現: 1.8 → わずかに広く */
  font-size: 15px;             /* 現: 14.5px → 読みやすさ向上 */
}
```

---

## 4. インタラクション・トランジション磨き

現状の `.2s ease` を「しっとり動く」に変える。

```css
/* カードのトランジションを全面改訂 */
.biz-card,
.service-card,
.pkg-card {
  transition:
    transform    .38s cubic-bezier(.22, 1, .36, 1),
    box-shadow   .38s cubic-bezier(.22, 1, .36, 1),
    border-color .28s ease;
  /* 現: .35s cubic-bezier(.22,1,.36,1) → 微妙に長く。イージングは維持（apple-spring系で良い） */
}

/* ホバー時の浮き上がりを少し控えめに（現: -6px は少し大げさ）*/
.biz-card:hover,
.service-card:hover {
  transform: translateY(-4px) rotate(0.2deg);  /* 現: -6px 0.3deg → 落ち着かせる */
}

.pkg-card:hover {
  transform: translateY(-4px);                 /* 現: -6px → 同上 */
}

/* ナビゲーション・ボタンは俊敏なままでよい（情報操作系は速い方が良いUX）*/
.site-nav a.nav-link { transition: color .18s ease; }  /* 変更なし相当 */

/* ヒーロー主CTAのパルスアニメーション: 輝き幅を抑制 */
@keyframes cta-pulse {
  0%, 100% { box-shadow: 0 8px 28px rgba(110,139,255,.32), inset 0 1px 0 rgba(255,255,255,.22); }
  50%       { box-shadow: 0 12px 40px rgba(139,160,255,.50), inset 0 1px 0 rgba(255,255,255,.28); }
  /* 現: 0.62 → 0.50 に落としてパルスを「脈打つ」から「呼吸する」に */
}
```

---

## 5. ウィットの出し方（5案以上、やりすぎないライン付き）

### 前提: AIハブのウィット座標

由井辰美というキャラクターの座標：
- 滋賀・彦根 × AI × クライミング歴30年
- 「9事業を回す」という数の異常さ（普通の人は1〜2）
- CEO かつ実装者という二重性
- 「異端OK、数字根拠」というタグライン自体がウィット

このキャラに合うウィット = **「上品な自嘲」「数字による意外性」「専門用語を道具として使う知的な遊び」**。
絶対に NG = 絵文字連打・ゆるいキャラ系・「楽しもう！」系のゆるさ。

---

### 案1: eyebrow ラベルに「コマンドライン的文体」を入れる（工数: 超低・効果: 中）

現状の eyebrow（ヒーロー上部の小ラベル）は `SHIGA, JAPAN · AI CONSULTING` など。
これを CLI / コードコメント的テキストに変える。

**変更前** （現状の Python での生成箇所）:
```
SHIGA, JAPAN · AI CONSULTING
```

**変更後** （`PORTAL_CSS` の eyebrow スタイルはそのまま。Python 側の文字列だけ変える）:
```
git commit -m "9事業, 経営歴30年, 異端OK"
```
または
```
$ ./run.py --mode consult --target 中小事業者
```
または
```
// 経営者であり実装者である矛盾を、矛盾のままで動かす
```

**ライン**: monospace フォント（`var(--mono)`）で出ているので視覚的に「コード」として読める。1行で収まる量に抑える。「おしゃれ風CLI」に見えるぎりぎりの量が限界。段落にしたら終わり。

---

### 案2: stat（実績数値）のラベルに「地の文的なツッコミ」を入れる（工数: 低・効果: 高）

現状の `.stat .label` は「事業数」「年間相談件数」などの平板なラベル。
ラベルに1行の副テキストを仕込み、数字の背景を語るとウィットになる。

```
30年    ← .stat .num
クライミング歴   ← .stat .label 現状
「経営よりクライミングが長い」   ← 追加する .stat .subtext
```

```
9       ← num
同時稼働の事業数   ← label
「全部自分で触っている」   ← subtext
```

CSS:
```css
.stat .subtext {
  font-size: 10.5px;
  color: var(--muted);
  font-style: italic;
  margin-top: 3px;
  line-height: 1.4;
  font-family: var(--mono);
  letter-spacing: 0;
}
```

**ライン**: 1行10〜16文字以内。parenthetical（括弧書き的）なトーンを保つ。感嘆符は使わない。

---

### 案3: ヒーロー・リードコピーのブラッシュアップ案（工数: 低・効果: 最高）

これはデザインより**コピー**の問題だが、「ウィット」の最大の出どころはここ。
現状の `OWNER_SUBTITLE` / `OWNER_TAGLINE` を変える提案。

現状:
```
クライミング歴30年・9事業を回す滋賀の Web 経営コンサル   ← subtitle
異端OK、数字根拠で経営を変える                        ← tagline
```

改訂案（知的な遊びを入れる）:
```
9事業を回しながら岩を登っている、滋賀の Web 経営コンサル。  ← 順番の入れ替えだけで「岩も登る」が副業感を出す
異端OK、数字根拠。コードも書く。                         ← 「コードも書く」の追加がコンサルらしくない意外性
```

または hero .lead の終わり方を変える:
```
現状推定: 「〜補助金申請からAIの現場定着まで一気通貫で伴走します。」
改訂案: 「〜補助金申請からAI定着まで一貫して動く。受注後に「ベンダーに投げる」は一度もない。」
```

**ライン**: 「コードも書く」「岩を登る」は事実ベース。事実の組み合わせ方がウィット。架空のキャラ作りや誇張はしない。

---

### 案4: FAQ セクションの問いに「クライアントが実際に言わないが思っていること」を入れる（工数: 低・効果: 中）

現状の FAQ は `FAQ_QA` リストで定義。問いが模範的すぎると「しっとり」でなく「固い」。

追加提案の問いと答え（口調ごと変える）:

```python
("「AIを使えば安くなる」と社内でやんわり言われているが、本当？",
 "ケースによります。自動化で月40時間削れた事業もあれば、導入費用の回収に2年かかった例もある。"
 "どちらが当てはまるかは業務の棚卸しを30分やれば9割わかります。最初の相談でその棚卸しをやります。"),

("彦根まで来ないと相談できない？",
 "オンラインで完結します。ただし最初の1回だけは彦根に来てもらった方がいい、という経験則があります。理由は「事務所を見せてもらうと業務の9割が分かる」から。"),
```

**ライン**: 答えは「数字根拠 + 経験則の組み合わせ」で終わらせる。共感や励ましで終わらせない。

---

### 案5: カード hover 時の「静かな光彩」でウィットを視覚化する（工数: 低・効果: 小〜中）

現状の `biz-card::before` は `radial-gradient` が hover で出る。
これを「事業カードごとに色を変える」ことで、均一な「青」発光でなく各事業の個性を出す。

現状:
```css
.biz-card::before {
  background: radial-gradient(420px 160px at 0% 0%, var(--card-glow, rgba(139,160,255,.12)) 0%, transparent 60%);
```

変更: `--card-glow` はすでに変数化されているので Python 側で事業ごとに設定するだけ。
例）`color_map` の `green`/`orange`/`pink` をそれぞれのカードに割り当て、`--card-glow` に渡す。

Python での実装箇所: `_render_businesses()` 内の `style=` 属性に `--card-glow: <色>` を追記。

**ライン**: 発光色は薄く。`rgba(色, .10)` を超えない。ビカビカした発光は逆効果。

---

### 案6: スクロール reveal のタイミング設計（工数: 低・効果: 中）

現状の `.reveal` は全要素が同じ `translateY(18px)` で上から出てくる。
統一感があるが単調。

変更案: セクションによって「上から」「左から」「スケール」を使い分ける。

```css
/* 統計数値は「スケールアップ」で出す（数字が「育つ」印象）*/
.stats-strip .stat.reveal {
  transform: scale(.92);
}
.stats-strip .stat.reveal.is-in {
  transform: scale(1);
}

/* 引用・testimonial は「左から」スライドイン */
.testimonial.reveal {
  transform: translateX(-16px);
}
.testimonial.reveal.is-in {
  transform: translateX(0);
}
```

**ライン**: 3種類以上混在させない。統計=スケール、引用=横スライド、その他=縦スライドの3種で十分。

---

## 6. 優先順位 TOP5（工数小×効果大）

| 順位 | 変更内容 | 工数 | 効果の根拠 |
|---|---|---|---|
| **1位** | ダーク `--text: #E8EAF2`（純白→クリーム）+ライト `--text: #1A1D2E`（純黒→深墨） | 2変数変更のみ | 全画面で即視覚変化。「目が刺さる感」の最大原因を除去。コントラスト比は十分維持（WCAG AA適合）|
| **2位** | `--shadow-card` を多層化（ライト・ダーク両方） | 4変数変更 | カードの「貼り付け感」が消える。影の質感は高級感と直結。実装2分 |
| **3位** | `font-weight: 800` → `700` をカード名・section-title に適用 | セレクタ6箇所の値変更 | h1 との対比が生まれ「しっとりした専門性」に。タイポ階層は読みやすさと格の両方に効く |
| **4位** | `body { line-height: 1.82; }` + `.hero .lead { line-height: 1.95; }` | 2箇所変更 | 文字が「呼吸する」ようになる。特に日本語混在コンテンツで体感差が大きい |
| **5位** | stat `.subtext` を追加して数字に「自嘲的な一言」を足す（案2） | HTML生成の `.stat` テンプレート変更 + CSS追加 | コンテンツで「ウィット」を最も直接的に出せる。デザインだけではウィットは出ない |

---

## 7. やりすぎてはいけないライン

- **文字サイズを下げない**: 「上品に見せたい」心理から本文を 12px 台にする誘惑がある。読めなくなるだけで専門性は出ない
- **グラデーションを増やさない**: 現状の青→紫グラデは効いている。新たに別色グラデを追加すると散漫になる
- **アニメーションを増やさない**: 案6のような reveal 種類分けは最大3種まで。増やすほど「動きがうるさい」に変わる
- **ウィットコピーは1画面に1箇所**: stat の subtext（案2）とヒーロー eyebrow（案1）を同時に入れる場合でも、FAQにも仕込むなら他を抑制する。「あ、ここもか」という発見の快楽は1ページで3回が上限
- **ダークのグローを強化しない**: 現状の `--glow` は `rgba(...,.35)` ですでに効いている。`0.50` 以上に上げると「ゲームっぽい」に変わる

---

## 8. 実装の引数・変数まとめ（コピペ用）

```css
/* ==== PATCH: 2026-05-28 しっとり磨き ==== */
/* ライト */
:root {
  --text:            #1A1D2E;
  --text-soft:       #4A5270;
  --muted:           #6E7A94;
  --bg-base:         #F5F6FA;
  --bg-white:        #FEFEFE;
  --line:            rgba(26,29,46,0.08);
  --line-strong:     rgba(26,29,46,0.13);
  --shadow-card:     0 2px 4px rgba(26,29,46,0.04), 0 8px 24px rgba(26,29,46,0.07);
  --shadow-card-hover: 0 4px 8px rgba(26,29,46,0.06), 0 20px 56px rgba(26,29,46,0.13), 0 0 0 1px rgba(84,104,255,0.18);
}
/* ダーク */
:root[data-theme="dark"] {
  --bg-base:         #0C0E18;
  --bg-white:        #111422;
  --bg-elev:         #171A2B;
  --text:            #E8EAF2;
  --text-soft:       #9BA5BE;
  --muted:           #5E6880;
  --line:            rgba(255,255,255,0.07);
  --line-strong:     rgba(255,255,255,0.12);
  --shadow-card:     0 2px 8px rgba(0,0,0,0.24), 0 10px 32px rgba(0,0,0,0.32);
  --shadow-card-hover: 0 4px 12px rgba(0,0,0,0.32), 0 20px 60px rgba(0,0,0,0.48), 0 0 0 1px rgba(139,160,255,0.20);
  --glow:            0 0 48px rgba(110,139,255,0.28);
}

/* タイポ */
body { line-height: 1.82; }
.hero .lead { line-height: 1.95; }
.section-sub { line-height: 1.9; font-size: 15px; }
.section-title { font-weight: 700; }
.biz-card-name { font-weight: 700; }
.pkg-title { font-weight: 700; }
.service-name { font-weight: 700; }

/* インタラクション */
.biz-card, .service-card, .pkg-card {
  transition: transform .38s cubic-bezier(.22,1,.36,1), box-shadow .38s cubic-bezier(.22,1,.36,1), border-color .28s ease;
}
.biz-card:hover, .service-card:hover { transform: translateY(-4px) rotate(0.2deg); }
.pkg-card:hover { transform: translateY(-4px); }

/* stat subtext（ウィット） */
.stat .subtext {
  font-size: 10.5px; color: var(--muted); font-style: italic;
  margin-top: 3px; line-height: 1.4; font-family: var(--mono); letter-spacing: 0;
}
```

---

## 参照

- 現状ソース: `c:\VSCode\Project\ai-hub\site\build_portal.py` の `PORTAL_CSS` 定数（L344〜）
- 事業情報: `c:\VSCode\Project\consul\ai-hub.md`
- ウィットコピーの詳細肉付けは **writer** に委任
- 実装後の CSS diff レビューは `/codex:review` を推奨（5ファイル以下の差分）

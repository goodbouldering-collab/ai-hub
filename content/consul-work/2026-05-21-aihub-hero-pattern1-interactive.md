# 2026-05-21 AIハブ ヒーロー刷新（パターン1）+ iPhone対応 + インタラクティブ強化

## 何をやったか（1ターンで3件まとめて）

1. **ヒーローをコピーパターン1（地域密着×実利／ローカルSEO最優先型）に刷新**
2. **iPhone（390px）のヒーローはみ出しを修正**
3. **TOPページのインタラクティブ強化**（タイプライター / ダークモード / 診断チャット）

対象: [ai-hub/site/build_portal.py](ai-hub/site/build_portal.py)（静的ジェネレータ）。本番 https://aiclimb.vercel.app/

## コピー方針（CEO 提供 3 パターンの 1 番目）

ターゲットを **社長限定 → 現場決定権を持つトップ・リーダー層**（社長/店舗オーナー/部門責任者）に拡張。
AI を「ツール」ではなく **「業務の着地点・仕組み」** として提示。地域共創（みんなのWA連動）を意識。
3 パターン全文は [work/2026-05-21-aihub-hero-copy-3patterns.md](2026-05-21-aihub-hero-copy-3patterns.md) に保存。

**CEO 指示: 上から順に適用・ヒーロー1つをその都度上書き。** 現在パターン1。次は「次」と言われたらパターン2→3へ差し替える。

### 採用コピー（パターン1）
- eyebrow: 「📍 彦根・滋賀・湖東エリア｜現場リーダー限定の対面ワークショップ」
- h1: 「滋賀・彦根の現場を動かすリーダーへ。ツールを試す時間は終わり。その場で業務が変わる『AI仕組み化』対面完成ワークショップ」
- sub-catch（太字）: 「店舗オーナー・部門責任者・現場のトップ限定。難しいITの勉強は一切不要。あなたの現場に最適な『〇〇（着地点）』をその場で構築します。」
- lead: 「彦根周辺や湖東エリアで…ボトルネックを解消する『仕組み』そのものをその場で完成させる完全実践型の対面講座です。地域の横のつながりを強めながら…」
- 主CTA「受講プランを見る →」(#packages) / 副CTA「無料相談する」(mailto) / バッジ「🛠 ITの勉強は一切不要」「📍 彦根・湖東で対面開催」

ローカルSEOキーワード（彦根/滋賀/湖東 × リーダー/責任者/オーナー × 仕組み化/業務効率化/ワークショップ）を見出しに自然配置。

## iPhone はみ出し修正（根本原因と対処）

**原因**: `body{overflow-x:hidden}` で横スクロール自体は出ないが、ヒーロー内コンテンツが画面外へ。具体的には:
- h1 の `.accent`/`.underline` に `white-space:nowrap` があり長文が画面外へ突き抜けていた（「ワークショッ」で見切れ）
- `.eyebrow` が長文バッジで幅442pxまで広がっていた
- `.hero-text` に幅制約（min-width:0/max-width）がなかった

**対処**:
- h1: `white-space:nowrap` を `.accent`/`.underline` から除去 → `overflow-wrap:anywhere`、`font-size: clamp(32→26px下限, 5.2→4.6vw, 60→52px)`、`line-height:1.25`
- `.eyebrow`: 560px以下で `display:flex` + 折返し可 + `border-radius:16px` + font 11.5px
- `.hero-text`: `min-width:0; max-width:100%`
- `.hero-blob`: 560px以下で縮小（260→180px）

**検証**: iPhone 390×844 で `scrollW===docW===390`・heroOffenders=空（はみ出しゼロ）を chrome-devtools で実測確認。

## インタラクティブ強化（実装詳細）

### タイプライター（新規）
- sub-catch の「〇〇（着地点）」部分に `.type-rotate` span。`data-words="新しい業務体制｜集客の仕組み｜人手不足の解決策｜業務効率化の着地点"` を順に打ち替え（タイプ→ホールド1.6s→削除→次語）。
- キャレット点滅 CSS。`prefers-reduced-motion: reduce` で完全無効（静的表示）。
- 検証: ロジックが「新しい業務体制」→「集客の仕組み」と切り替わることを確認。

### ダークモード切替（新規）
- ヘッダーに `.theme-toggle`（🌙/☀️）。PC はナビ内、モバイルは独立配置。
- `:root[data-theme="dark"]` で CSS 変数群を上書き（既存セレクタ非改変）。
- リテラル白を使う箇所（header.scrolled / menu-drop / mobile-nav / hero-badge / pkg-card / service-card / biz-card / pkg-cat / pkg-subsidy）を個別ダーク上書き。
- `body` 背景を `var(--bg-white)/var(--bg-base)` に置換（旧: `#ffffff/#f8fafc` 固定）。
- localStorage `aihub-theme` で永続 + 初回はシステム設定（prefers-color-scheme）追従。
- 検証: light→dark 切替で `data-theme` 変化・トグル☀️化・背景ダーク化を実画面確認。

### 診断チャット（新規）
- PACKAGES 末尾に「🔍 60秒診断｜あなたに合うプランは？」ボタン → `#diagnoseModal`。
- 3問（課題 / スパン / 補助金）に答えると consultation/workshop/package のスコアを集計し、最多のおすすめコースを提示。「このプランを見る →」で #packages へ。
- 検証: package系3回答 → 「AI伴走パック 6回」を正しく判定。モーダル開閉・結果表示を実画面確認。

### STATS / FAQ（既存活用）
- STATS の数字カウントアップ（IntersectionObserver + easeOutCubic）は既存実装が稼働中。
- FAQ は既に `<details>/<summary>` のネイティブアコーディオン（+→×回転）。
- サービスカードのホバー浮き上がりも既存実装で十分強いため追加せず。

## ナビ調整
- グローバルナビに「受講プラン(#packages)」を追加、「つくれるもの」はメニュードロップへ移動。

## git / デプロイ

- ai-hub: `c3ec1bc`（本体変更）→ daily digest と衝突したため `bb22b2b` で merge（`outputs/agents_status.json` のみ衝突・再生成で解決）→ push 済み。
- `site/dist/index.html` は `.gitignore` 対象だが `git add -f` で commit（毎日 Actions が再生成する運用）。
- 安全ゲート: Python構文OK / HTML内JS構文OK / 秘密情報なし / http://直書きなし。
- 本番反映＆検証: iPhone はみ出しゼロ・ダーク・診断・タイプライター全て確認済み。

## 残課題
- ヒーローコピー パターン2 / 3 は CEO が「次」と言ったら順次差し替え（全文 work/ に保存済み）。
- メタタイトルの SEO 最適化（CEO 推奨『彦根・滋賀の現場リーダー限定「AI業務仕組み化」対面完成ワークショップ』）は未適用 — 必要なら別途。
- トークンローテーション（前タスクの ADMIN_TOKEN ほか漏洩分）の完了確認は引き続き CEO 側。

## 委任ログ
Claude 単独で完遂。Codex 委任なし。入口判定では「5+ファイル横断・複数機能」で Codex rescue 候補だったが、ヒーロー文脈を保持している自分が小さい修正を順に当てる方が速いと判断し単独実行。結果 ai-hub 1機能コミット（+merge1）。

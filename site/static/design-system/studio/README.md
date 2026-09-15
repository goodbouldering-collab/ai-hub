# AI相談 Studio assets

2026-09-14。トップ、公開記事、管理画面に共通で使うデザイン資産。

- 背景：生成り `#f5f3ed`、面：`#fffefa`、文字：`#172c2a`。
- 主色：深い青緑 `#205751`、補助：セージ `#dfe5d8`。陶器・紙の質感とアーチを共通モチーフにする。
- 派手な色数ではなく、大きな見出し、非対称の丸み、余白、控えめな動きで楽しさを出す。
- `studio.css` は全ページの共通表示層。`studio.js` は公開記事を含む共通の読了表示、カードの光、画像レイヤーの移動、トップのカルーセル操作を担当。動きを減らす設定では装飾の動きを停止する。
- 講師本人、実際の会場、実績サイトの写真は維持する。

## 画像

OpenAI built-in ImageGenで新規生成。外部APIキー不使用。すべて1536×1024 PNG。原本をそのまま保存。

| ファイル | 使用箇所 | 意図 |
|---|---|---|
| `images/hero.png` | トップ | 地域の仕事を、学びと仕組みでつなぐ |
| `images/learn.png` | AIエージェント講習・AI個別講習 | 手を動かして学ぶ |
| `images/build.png` | AIコーディング講習・AI伴走支援 | 小さく作り、組み合わせる |
| `images/connect.png` | AIオンラインサロン・AIアプリサイト制作 | 人・地域・活動がつながる |

### 制作指示（再生成用）

共通：finished premium website illustration, landscape 3:2. Quietly playful contemporary Japanese creative studio. Warm ivory #f2eee5, deep petrol teal #174744, desaturated sage, tiny terracotta accent, brushed silver. Tactile matte ceramic and folded paper, soft daylight, art-directed product photography. Large simple sculptural forms, refined adult atmosphere. No people, robots, AI brains, circuitry, neon, rainbow, text, letters, logos, or watermarks. Production asset, not a webpage mockup.

- Hero：A folded-paper path ascends three broad steps through a tall teal arch, connecting a cream notebook-like building, a blank laptop, coffee, and a silver sphere balanced above a curved ribbon. A small abstract Japanese regional town and lake in the distance. Center-right diagonal composition. Metaphor for local people turning ideas into real work with AI.
- Learn：A cream notebook and blank laptop on a plinth with a pencil and a sweeping teal ribbon arch. A sculptural still life representing an inviting entrance to practical learning.
- Build：Interlocking folded-paper steps and teal arches, a brushed-silver connecting tube and sphere, and a small terracotta cube. A sculptural still life representing ideas assembled into a working system.
- Connect：Three small paper houses on a teal platform, connected by a flowing ribbon, with a terracotta disk and silver sphere. A miniature landscape representing people and local activities becoming connected.

生成後に主題の編集はしていない。Web側でトリミングのみ指定。コース画像は遅延読み込み。

## Glass atelier（2026-09-15）

共通背景は淡い青緑、半透明の面には白い縁とぼかしを重ねる。本文は濃い青緑を保ち、暗いCTAは白文字。ヘッダー、カード、記事、講師紹介、管理、ログインへ同じ素材を使う。

ヒーローと講師紹介の主画像に、既存のlearn/connect画像を小さなガラスフレームで重ねる。装飾はaria-hidden、alt空、pointer-events:none。マウス移動で最大6pxの奥行きを付け、タッチ・動き抑制・非表示時には停止する。写真本人や文章・料金・リンクを置き換えない。

検証: `scripts/verify_glass_art.py` は全HTMLの内容と操作、非装飾資産、管理HTML、認証コード、再装飾の冪等性を比較。`node --test tests/studio-glass-motion.test.mjs` は入力方式と動き停止を検査する。

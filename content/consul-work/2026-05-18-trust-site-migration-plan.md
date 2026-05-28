# トラスト 公開サイト全機能移設＋管理ハブ全面構築 計画書

- 作成日: 2026-05-18
- 対象事業: トラスト（株式会社トラストエージェント）
- 対象リポ: `C:\VSCode\Project\トラスト\`（本番 `https://trust-nine-tau.vercel.app`）
- 出典サイト: `https://www.trustagent2015.com/`（現行・カラーミー系の不動産ポータル）
- CEO 指示（2026-05-18）:
  1. 賃貸物件検索・売買物件検索の**2機能のみ当面は外部リンク**（将来は内部移設）
  2. それ以外の**全機能・全コンテンツを本リポへ移設**
  3. `/admin` を「ブログ・ヒーローテキスト編集など**あらゆる機能を編集できる管理ハブ**」に
  4. **まずコピー（実サイトの全コンテンツ取り込み）から**
  5. DB は**スキーマ確定後に設置**（先行してUI・フォールバックを作る・N-デザイン二層戦略を踏襲）
  6. 今回は**計画まで**（実装は次段階・CEO 承認後）

---

## 1. 現行サイトの全体マップ（取り込み済み）

### A. 外部リンクのまま（当面）＝中身は移設しない

| 区分 | 現行URL（trustagent2015.com 配下） | 扱い |
|---|---|---|
| 賃貸：条件/沿線/地域/所在地/学校区/地図検索 | `/rent/search` `/rent/railway` `/rent/area` `/rent/location` `/rent/school` `/rent/map` | **外部リンク**（将来内部移設の余地を残す） |
| 賃貸：物件リクエスト・お気に入り・最近見た | `/rent_request` `/rent_favorites` `/rent_recently` | 外部リンク |
| 売買：条件/沿線/地域/所在地/学校区/地図検索 | `/sale/search` ほか同型 | 外部リンク |
| 売買：物件リクエスト・お気に入り・最近見た | `/sale_request` `/sale_favorites` `/sale_recently` | 外部リンク |
| 査定 | `/sale_assessment` | 外部リンク（物件系に付随するため当面外部） |
| ローンシミュレーション | `/loan_simulation` | 外部リンク（物件系ツール・当面外部。※将来は内部実装候補） |

> 物件検索は現行ポータル（カラーミー/不動産専用 CMS と推定）が在庫DBと連動しているため、在庫データ移行を伴う。**在庫DBスキーマが固まるまでは外部リンクで温存**し、フェーズ2以降で内部 Supabase へ移設する。

### B. 本リポへ全面移設＝コピー対象

| 区分 | 現行URL | 移設後ルート（案） | 中身の状態 |
|---|---|---|---|
| トップLP（ヒーロー/新着/おすすめ/特徴） | `/` | `/` | ✅ 取り込み済（要再構成） |
| 会社案内 | `/company` | `/company` | ✅ 取り込み済 |
| アクセス | `/company/access` | `/company/access` | ✅ 取り込み済（地図・道順） |
| お知らせ一覧・詳細 | `/news` `/news/detail/:id` | `/news` `/news/[slug]` | 一覧3件確認済・**詳細本文は移設時に個別取り込み** |
| スタッフブログ | （トップに導線あり） | `/blog` `/blog/[slug]` | **記事個別URLを移設時に取り込み** |
| 引越しの豆知識 | `/moving_knowledge` | `/guide/moving-knowledge` | ✅ 4記事の構成取り込み済（本文清書要） |
| 引越しの諸手続き一覧 | `/moving_procedure` | `/guide/moving-procedure` | 移設時に本文取り込み |
| 不動産用語集 | `/real_estate_dictionary` | `/guide/dictionary` | 移設時に用語データ取り込み |
| お問い合わせ | `/contact` | `/contact` | フォーム再実装（Supabase contacts） |
| プライバシーポリシー | `/privacy_policy` | `/privacy` | ✅ 全文取り込み済 |
| 利用規約 | `/terms` | `/terms` | 移設時に本文取り込み |
| サイトマップ | `/site_map` | `/sitemap`（HTML）+ `sitemap.xml` | 構造取り込み済 |

### C. 既存（home-shift = グループホーム事業）はそのまま共存

- `/home-shift`（LIFF・LINE Bot）、`/admin` の home-shift 系タブは現行のまま。
- 今回の移設で `/admin` を**全社管理ハブ**に拡張し、不動産サイト管理 + home-shift 管理を統合する。

---

## 2. 目標アーキテクチャ

```
trust-nine-tau.vercel.app/
├─ /                       公開トップ（ヒーロー/新着/おすすめ物件カード/特徴/CTA）
│                          ※おすすめ物件は当面「外部ポータルへのリンクカード」
├─ /company /company/access  会社案内・アクセス
├─ /news  /news/[slug]      お知らせ（DB: news）
├─ /blog  /blog/[slug]      スタッフブログ（DB: blog_posts）
├─ /guide/moving-knowledge   引越し豆知識（DB or 静的: guide_articles）
├─ /guide/moving-procedure   引越し諸手続き
├─ /guide/dictionary         不動産用語集（DB: glossary_terms）
├─ /contact /contact/thanks  問い合わせ（DB: contacts）
├─ /privacy /terms /sitemap  規程・サイトマップ
├─ （外部リンク）賃貸/売買物件検索・査定・ローン → trustagent2015.com
│
├─ /admin                  ★全社管理ハブ（要ログイン・isAdmin ガード）
│   ├─ ダッシュボード        全体サマリ（不動産サイト + home-shift）
│   ├─ ヒーロー/トップ編集    キャッチコピー・ヒーロー画像・CTA文言
│   ├─ お知らせ管理          news の CRUD
│   ├─ ブログ管理            blog_posts の CRUD（リッチ本文・画像・SEO）
│   ├─ お役立ち記事管理      guide_articles / glossary_terms の CRUD
│   ├─ 会社情報編集          代表挨拶・理念・概要表（constants の DB 化）
│   ├─ 問い合わせ管理        contacts の閲覧・対応ステータス
│   ├─ おすすめ物件リンク管理  トップに出す外部物件URLの登録（在庫DB前の暫定）
│   ├─ ─ 以下 home-shift ─
│   ├─ スタッフ管理 / シフト管理 / 希望管理（既存）
│   └─ （将来）物件在庫管理   ← 在庫DBスキーマ確定後に追加
└─
```

### データ戦略（N-デザイン二層戦略を踏襲）

- Supabase 接続可能 → DB から
- 不可（スキーマ確定前）→ フォールバック（`lib/data/*.ts` の静的データ＝取り込んだコピー）
- **今回コピーで作る静的データがそのままフォールバックの初期値兼 seed になる**

---

## 3. 想定スキーマ（確定はCEO承認後・たたき台）

| テーブル | 主カラム | 用途 |
|---|---|---|
| `trust_site_news` | id, slug, title, body, published_at, is_published | お知らせ |
| `trust_site_blog_posts` | id, slug, title, body, cover_image, category, meta_description, faq(jsonb), published_at | スタッフブログ |
| `trust_site_guide_articles` | id, slug, category(moving/procedure), title, body, sort_order | お役立ち記事 |
| `trust_site_glossary` | id, term, reading, body, category | 不動産用語集 |
| `trust_site_contacts` | id, name, email, tel, body, status, created_at | 問い合わせ |
| `trust_site_settings` | key, value(jsonb) | ヒーロー文言・会社情報・CTA等の編集可能設定 |
| `trust_site_external_listings` | id, type(rent/sale), title, summary, price, url, sort_order | トップ掲載の外部物件リンク（在庫DB前の暫定） |

- 既存 home-shift は `trust_home_shift` schema。不動産サイト系は **`trust_site` schema** に隔離（同一 Supabase プロジェクト相乗り・n-design と衝突しない）。
- snake_case ⇄ camelCase は `lib/supabase-mappers.ts` 経由（親 CLAUDE.md 規約）。

---

## 4. フェーズ分解（実装順・各フェーズで build/test 緑 → push）

### フェーズ0：計画承認（このドキュメント）
- CEO がスコープ・ルート設計・スキーマたたき台を承認 → フェーズ1着手。

### フェーズ1：コピー（静的データ化）★最優先・DB不要
1. 実サイト全ページの本文を順次取り込み（news 詳細・blog 各記事・諸手続き・用語集・利用規約）
2. `lib/data/` に静的データとして格納（`news-data.ts` `blog-data.ts` `guide-data.ts` `glossary-data.ts` `site-settings.ts`）
3. これがフォールバック兼 seed の正本になる
4. **成果物確認単位**: 取り込んだコピーを [work/](work/) にレビュー用 Markdown で出す → CEO 文面確認

### フェーズ2：公開ページ実装（静的データ表示）
1. 共通：Header のナビを実サイト構成に拡張（物件検索＝外部リンク、それ以外＝内部）
2. `/company` `/company/access` `/news` `/blog` `/guide/*` `/privacy` `/terms` `/contact` を静的データで実装
3. デザインは既存の N-デザイン言語（glass/fade-up/primary）を踏襲
4. SEO：JSON-LD（BlogPosting/FAQPage/Speakable）を記事系に付与（親 CLAUDE.md 規約）
5. build 緑 → push → 本番反映（DBなしで完全動作）

### フェーズ3：管理ハブ拡張（静的データ編集はまだ不可・骨格）
1. `/admin` に新タブ追加（ヒーロー編集/お知らせ/ブログ/お役立ち/会社情報/問い合わせ/外部物件リンク）
2. 各タブは「現在の静的データを表示」+「DB接続後に編集可能化」のプレビュー骨格
3. N-デザイン admin のタブ式 UX を踏襲

### フェーズ4：スキーマ確定 → DB 設置（CEO 手動 Supabase 作業）
1. フェーズ3 までで UI が固まった時点でスキーマを確定
2. `supabase/site/migrations/0001_init.sql` 作成 → CEO が Dashboard 適用
3. seed = フェーズ1 の静的データを流し込む

### フェーズ5：DB 配線（二層戦略の上層を有効化）
1. 公開ページを「DB 優先・なければ静的フォールバック」に切替
2. `/admin` の各タブを実 CRUD 化（ブログ投稿・ヒーロー文言編集が実際に効く）
3. 問い合わせフォーム → `trust_site_contacts` 保存 + 管理画面で対応

### フェーズ6（将来）：物件検索の内部移設
- 在庫DBスキーマ設計（賃貸/売買物件・画像・条件検索インデックス）
- 外部リンクを内部 `/rent` `/sale` 検索へ置換
- 査定・ローンシミュレーションも内部実装

---

## 5. 既存資産の流用方針

- **N-デザイン**（`C:\VSCode\Project\N-デザイン\`）が同型の「コーポレート＋ブログ＋施工事例＋admin タブ式」構成。
  - admin タブ UI、`lib/supabase-mappers.ts`、二層データ戦略、JSON-LD、`components/admin/*`（image-uploader/rich-textarea/tabs）を**設計パターンとして流用**（コードのコピペではなくトラスト用に再実装）。
- 既存 [トラスト/components/](トラスト/components/)（Header/Footer/AdminShell/FadeIn）と `config/constants.ts` を土台に拡張。
- home-shift 系（認証・LIFF・制約チェッカー）は不変。

---

## 6. リスク・確認事項（CEO 判断が要る点）

1. **物件検索を当面外部リンクにする UX**: トップの「おすすめ物件」も外部ポータルへ飛ぶ形になる。会社サイトとして物件導線が外部に出る点の許容可否。
   → 暫定で `trust_site_external_listings` に手動登録した数件を「おすすめ」として内部表示し、詳細は外部へ、という折衷も可能。どちらにするか。
2. **ブログ/お知らせの既存記事の著作権・移設範囲**: 現行サイトの全記事を移設してよいか（自社作成コンテンツ前提で進める想定）。
3. **会社情報の DB 化**: 現在 `config/constants.ts` が正本。管理画面から編集可能にすると正本が DB に移る。constants はフォールバック値として残す設計でよいか。
4. **schema 名**: `trust_site`（不動産サイト）/ `trust_home_shift`（既存）で分離。この命名で確定してよいか。
5. **査定・ローンシミュレーション**: 物件系ツールとして当面外部。将来内部実装の優先度（フェーズ6 で物件検索と同時か、それより前か）。

---

## 7. 次アクション

- 本計画を CEO がレビュー → 上記6の確認事項に回答 → フェーズ1（コピー）から着手。
- フェーズ1 は DB 不要・既存機能に無干渉で進められるため、承認が出れば即着手可能。

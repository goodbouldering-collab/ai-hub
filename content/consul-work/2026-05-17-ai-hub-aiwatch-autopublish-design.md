# AIハブ — AI Watch 記事 自動生成・自動投稿 設計書

**作成日**: 2026-05-17（日）
**対象**: AIハブ（`C:\VSCode\Project\ai-hub\`）
**CEO 確定方針（2026-05-17）**:
- カラーミー本店記事：**生成まで自動・公開は CEO 承認**（daily が下書きキューに溜める → `/ops` でワンクリック公開）
- SNS（X / Threads）：**今回スコープに含める**（キー投入済前提）。記事公開と連動して自動投稿
- ゴール：**設計＋実装まで**（実装は ai-hub リポ書き込み = step ごと CEO GO 必須）

---

## 0. 現状の正確な把握（実測ベース・誤診断しない）

| 系統 | 実体 | 自動/手動 |
|---|---|---|
| RSS収集→要約→ランキング→AI Watchサイト生成 | `run.py`（daily.yml JST07:00） | ✅ **完全自動** |
| カラーミー記事 **生成** | `api/admin/generate-articles.ts`（`generateArticleDrafts(theme)`） | ❌ 管理画面で手動テーマ入力 |
| カラーミー記事 **公開** | `api/admin/publish-article.ts`（**実装完成済・本番投入可**） | ❌ 管理画面で手動ボタン |
| SNS 投稿（X / Threads） | **コード・APIゼロ**（手順書 `2026-05-11-ai-hub-sns-mvp-keys-howto.md` のみ。`portal.sns_posts` SQL も実ファイル無し） | ❌ 未実装 |
| `/ops` ダッシュ | `api/ops/index.ts` + `site/static/ops/index.html`（シェルのみ） | 記事キューUI無し |

**設計の核心ギャップ**:
1. daily が選んだ Top 記事 → 「カラーミー記事テーマ」へ繋ぐパイプが無い（`generateArticleDrafts` は手動テーマ前提）
2. 生成ドラフトを **CEO 承認待ちで溜める永続層が無い**（Vercel FS は読取専用 → Supabase 必須）
3. SNS 投稿はクライアント実装からゼロ

---

## 1. 設計思想（3 原則）

### 原則1: 「生成は自動・公開は承認」の境界を物理的に作る

無人で本番ストア（カラーミー goodbouldering.com）に書くと、AI 誤生成がそのまま客の目に触れる。
→ **ドラフトは Supabase テーブル `ai_drafts` に `status='pending'` で溜まるだけ**。
カラーミー本番テンプレ（1086）への書き込みは **CEO が `/ops` でボタンを押した瞬間だけ**発火。
これは既存 `publish-article.ts` をそのまま叩く（公開ロジックは完成済・再実装しない）。

### 原則2: SNS 投稿は「記事公開の従属イベント」にする（独立して暴れさせない）

SNS 単独自動投稿は誤爆リスクが高い（X Free は月500・取り消し不可）。
→ SNS 投稿は **CEO が記事を承認公開した時に、同じ記事の要約から1回だけ**発火。
冪等性のため `ai_drafts.sns_posted_at` を立て、二重投稿を物理的に防ぐ。
daily が SNS を自発投稿することはしない（人間の公開操作がトリガー）。

### 原則3: 既存資産を壊さない・再実装しない

- `run.py` の収集パイプライン：触らない（収集済データを読むだけ）
- `publish-article.ts`：触らない（`/ops` から内部呼び出し）
- `generateArticleDrafts`：プロンプトは流用、呼び出し方だけ「Top記事をテーマ化」に拡張
- Supabase：`ops_prompts`（inventory で確立済）と同じ service_role 専用パターンを踏襲

---

## 2. アーキテクチャ全体図

```
[daily.yml JST07:00]
  └ run.py（既存・無改造）
       └ outputs/top10.json 生成（既存）
  └ ★新規 step: scripts/build_article_drafts.py
       ├ top10.json の上位 N 件を読む
       ├ 各記事を Claude でカラーミー記事化（既存 SYSTEM_PROMPT 流用）
       └ Supabase ai_drafts に status='pending' で INSERT（冪等：source_hash UNIQUE）

[CEO がスマホで /ops を開く（Basic 認証）]
  └ ① 承認待ちドラフト一覧（ai_drafts where status='pending'）
       ├ [プレビュー] 本文HTML確認
       ├ [公開] ボタン → /api/ops/publish-draft
       │     ├ publish-article.ts のロジックでカラーミー1086へ投入（既存流用）
       │     ├ ai_drafts.status='published', published_at=now
       │     └ SNS 自動投稿（sns_posted_at が null のときだけ1回）
       │           ├ X: tweet（要約+本店URL）
       │           └ Threads: post（同上）
       │           └ ai_drafts.sns_posted_at=now（冪等ロック）
       └ [却下] ボタン → status='rejected'（カラーミーにもSNSにも一切出ない）
```

ポイント: **自動と手動の境界は `/ops` の[公開]ボタン1点**。そこより上流は全自動、そこから先（カラーミー＋SNS）は承認後に一括発火。

---

## 3. データモデル（Supabase）

プロジェクト: `zrawhzwtppmlxyhngnju`（AIハブ既存）。schema は `public`。

### 3-1. `ai_drafts`（記事ドラフトキュー）

```sql
create table if not exists public.ai_drafts (
  id           uuid primary key default gen_random_uuid(),
  source_hash  text not null unique,          -- top10.json items[].hash（冪等キー）
  source_url   text not null,                 -- 元ニュースURL（トレーサビリティ）
  source_title text not null,                 -- 元記事タイトル
  title        text not null,                 -- 生成記事タイトル（カラーミー用）
  html         text not null,                 -- 生成本文HTML（<h2>始まり）
  summary      text not null,                 -- 30-60字要約（SNS本文の素材）
  status       text not null default 'pending'
               check (status in ('pending','published','rejected')),
  parent_group_id int,                        -- 公開時に確定（/ops で選択 or 既定値）
  group_id        text,                       -- 同上
  published_at    timestamptz,
  sns_posted_at   timestamptz,                -- SNS 冪等ロック（null=未投稿）
  sns_result      jsonb,                      -- {x:{ok,id|err}, threads:{ok,id|err}}
  created_at      timestamptz not null default now(),
  updated_at      timestamptz not null default now()
);
create index if not exists ai_drafts_status_idx on public.ai_drafts(status, created_at desc);
alter table public.ai_drafts enable row level security;
-- service_role 専用（anon/authenticated に policy を作らない＝完全非公開）
```

`source_hash` UNIQUE で daily が同じニュースを二重ドラフト化しない（冪等の要）。

### 3-2. `sns_posts`（投稿履歴・監査ログ）

手順書が言及していた `portal.sns_posts` を `public.sns_posts` として実装（schema を分けない＝既存 ai_drafts と同居・運用簡素）。

```sql
create table if not exists public.sns_posts (
  id          uuid primary key default gen_random_uuid(),
  draft_id    uuid references public.ai_drafts(id) on delete set null,
  platform    text not null check (platform in ('x','threads')),
  status      text not null check (status in ('ok','error')),
  remote_id   text,                           -- 投稿ID（X: tweet id, Threads: media id）
  text        text not null,                  -- 実投稿本文（後追い検証用）
  error       text,
  created_at  timestamptz not null default now()
);
alter table public.sns_posts enable row level security;
```

---

## 4. 新規・改修ファイル一覧（実装スコープ）

| # | パス | 種別 | 内容 |
|---|---|---|---|
| 1 | `supabase/migrations/20260517_ai_drafts.sql` | 新規 | §3 の2テーブル DDL |
| 2 | `scripts/build_article_drafts.py` | 新規 | top10.json上位N→Claude記事化→Supabase INSERT（冪等） |
| 3 | `.github/workflows/daily.yml` | 改修 | `run.py` 後に step 追加（drafts ビルド・Secrets 注入） |
| 4 | `api/_lib/supabase_drafts.ts` | 新規 | ai_drafts CRUD（service_role・既存 storage.ts と同パターン） |
| 5 | `api/_lib/sns.ts` | 新規 | X / Threads 投稿クライアント（**ゼロ実装・Codex候補**） |
| 6 | `api/ops/drafts.ts` | 新規 | GET 承認待ち一覧 / POST 却下（withAdmin） |
| 7 | `api/ops/publish-draft.ts` | 新規 | 公開: カラーミー投入＋SNS連動（publish-article ロジック流用） |
| 8 | `site/static/ops/index.html` | 改修 | 「承認待ち記事」ブロック追加（一覧・プレビュー・公開・却下） |
| 9 | `api/_lib/config.ts` | 改修 | SNS env / `AI_DRAFTS_TOP_N` / 既定 group_id 解決を追加 |

> 5（SNS クライアント）は OAuth1.0a 署名（X）と 2段階 POST（Threads media→publish）が要る純技術実装。consul のトーン管理は不要 → **Codex に出す候補**（§8）。

---

## 5. パイプライン詳細

### 5-1. `build_article_drafts.py`（自動・daily 内）

```
1. outputs/top10.json を読む（run.py が既に生成済）
2. items[:AI_DRAFTS_TOP_N]（既定 N=2）を対象
3. 各 item について Supabase に source_hash 存在チェック → あればスキップ（冪等）
4. 無ければ generate-articles の SYSTEM_PROMPT 相当で Claude 呼び出し
   - テーマ = item.title_ja or item.title（AI ニュースをグッぼる文脈に翻案）
   - ★注意: SYSTEM_PROMPT は「クライミング用品店ブログ」想定。
     AI ニュースをそのまま流すとズレる → プロンプトに
     「このAIトピックをクライミング/ボルダリング層向け読み物に翻案」と1行足す
5. {title, html, summary} を ai_drafts に status='pending' INSERT
6. 失敗は1件ずつ try/except（1件コケても残りは処理・daily を落とさない）
```

Python から Supabase は `supabase-py`（requirements.txt に追加）か REST 直叩き。
既存 `migrate_sqlite_to_supabase.py` が `supabase` を使っているか要確認 → 同じ依存に揃える。

### 5-2. `/api/ops/publish-draft`（CEO 承認後・手動トリガー）

```
POST { draftId, parentGroupId, groupId, target:"live" }
 1. ai_drafts から draft 取得（status='pending' でなければ 409）
 2. publish-article.ts のコアロジックでカラーミー1086へ投入
    （renderArticleBlock + upsertArticle + updateTemplatePage を関数抽出して共有）
 3. status='published', published_at=now, parent/group 確定 を UPDATE
 4. if sns_posted_at is null:
      - sns.ts で X / Threads に投稿（本文 = summary + " " + 本店記事URL）
      - 各結果を sns_posts に INSERT
      - ai_drafts.sns_posted_at=now, sns_result=jsonb で記録
    （カラーミー成功・SNS失敗でも記事公開は確定。SNSは sns_posts に error 残し /ops で再試行可）
 5. 200 { published:true, sns:{x,threads} }
```

**トランザクション境界**: カラーミー投入成功＝公開確定。SNS はベストエフォート（失敗しても記事は出る・履歴に残し再送可能）。SNS 失敗で記事公開を巻き戻さない（カラーミーに冪等 rollback API が無いため）。

---

## 6. 自動化の安全境界（誤爆防止の設計判断）

| リスク | 設計上の歯止め |
|---|---|
| AI 誤記事が本番カラーミーに無人で出る | 公開は必ず `/ops` の人手ボタン。daily は `pending` INSERT のみ |
| 同じニュースで毎日ドラフト量産 | `source_hash` UNIQUE 制約（DB レベルで物理的に重複拒否） |
| SNS 二重投稿（X は取消不可・Free 月500） | `sns_posted_at` not null チェック。再公開しても SNS は飛ばない |
| daily が SNS を勝手に投稿 | SNS 発火点は `publish-draft`（人手公開）のみ。daily に SNS コード無し |
| SNS キー未投入で 500 連発 | `config.ts` で env 欠落時は `sns:{skipped:true}` を返し記事公開は成功させる |
| Claude 生成が AI ニュース直訳でグッぼる文脈とズレ | プロンプトに翻案指示を明示（§5-1 step4 注記）。pending で人間が必ず目視 |
| Vercel FS 読取専用でドラフト保存不可 | 永続層を Supabase に置く（ローカル JSON 書込は本番で物理不可・inventory で実証済の制約） |

---

## 7. daily.yml 改修（最小差分）

`run.py` step の後ろに追加（既存 commit-back step の **前**）:

```yaml
      - name: Build article drafts (Supabase)
        env:
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_SERVICE_ROLE_KEY: ${{ secrets.SUPABASE_SERVICE_ROLE_KEY }}
          AI_DRAFTS_TOP_N: "2"
        run: python scripts/build_article_drafts.py
        continue-on-error: true   # ドラフト生成失敗で digest 全体を落とさない
```

`continue-on-error: true` 採用理由：ドラフト生成はおまけ。これがコケても AI Watch 本体（収集・サイト生成・commit back）は完遂させる。失敗は次回 daily で source_hash が無いので自動リトライされる（冪等性が保険になる）。

---

## 8. 実装の進め方（Claude / Codex 役割分担）

CLAUDE.md 入口判定に基づく宣言（着手前）:

| ブロック | 担当 | 理由 |
|---|---|---|
| Supabase DDL（#1）・config（#9）・daily.yml（#3） | **Claude** | 既存パターン踏襲・短い・事業文脈の理解が要る |
| `build_article_drafts.py`（#2）・ops API（#6,7）・/ops UI（#8） | **Claude** | publish-article 流用・既存コード文脈の維持が要る |
| `api/_lib/sns.ts`（#5）X OAuth1.0a 署名 + Threads 2段階POST | **Codex 候補** | 純技術・署名実装は誤りやすく独立検証向き・consul文脈不要 |

→ #5 着手時に `/codex:rescue` で SNS クライアントのゼロ実装を出し、Claude が結合レビュー（CLAUDE.md「Codex成果物は必ずClaude側レビュー」）。
→ ai-hub リポ書き込み = **step ごと CEO GO**。安全ゲート（build通過・秘密情報直書きなし）通過後 push。

---

## 9. 実行順序（step ごと CEO 承認）

| 順 | 作業 | リポ書込 | 前提 |
|---|---|---|---|
| **S1** | Supabase DDL 適用（`20260517_ai_drafts.sql` 作成 → CEO が Supabase で実行） | ai-hub（SQL作成のみ・実行はCEO） | 設計承認 |
| **S2** | `config.ts` 拡張＋`supabase_drafts.ts`＋`build_article_drafts.py` 実装 | ai-hub（要CEO GO） | S1 |
| **S3** | `daily.yml` 改修＋GitHub Secrets 確認（`SUPABASE_*` 既存か） | ai-hub（要CEO GO） | S2 |
| **S4** | `sns.ts`（Codex）＋`ops/drafts.ts`＋`ops/publish-draft.ts` | ai-hub（要CEO GO） | S2 |
| **S5** | `/ops` UI に承認待ちブロック追加 | ai-hub（要CEO GO） | S4 |
| **S6** | 動作確認（daily 手動 dispatch → pending 確認 → /ops で公開 → カラーミー/SNS 反映実測） | — | S5 |

---

## 10. CEO 確認ポイント（実装着手前に回答が要る 5 点）

| # | 確認事項 | デフォルト案（回答なければこれで進める） |
|---|---|---|
| Q1 | カラーミー記事の **公開先 parent_group_id / group_id** は固定か、/ops で都度選ぶか | **既定値を `config.ts` に持ち、/ops で上書き可**。既定 group_id は要ヒアリング（現状の手動公開で使っている値があるはず） |
| Q2 | daily が1日に生成するドラフト件数 `AI_DRAFTS_TOP_N` | **2 件/日**（多すぎると承認が回らない・少なすぎると枯れる、の中間） |
| Q3 | SNS 本文フォーマット | `{summary}\n\n▼続きはこちら\n{本店記事URL}\n#クライミング #ボルダリング`（X 280/Threads 500 内に収める） |
| Q4 | GitHub Secrets に `SUPABASE_URL` / `SUPABASE_SERVICE_ROLE_KEY` は既に登録済か（daily.yml が使えるか） | S3 着手時に `gh secret list` で実測（無ければ CEO が登録） |
| Q5 | SNS キー（`X_*` / `THREADS_*`）は本当に Vercel 投入済か | S4 着手時に `/ops` 接続チェックで実測。未投入なら SNS は `skipped` で記事公開だけ動く設計なので**ブロッカーにしない** |

---

**最終更新**: 2026-05-17（v1・設計完了。§10 の Q1-Q5 と §9 の step ごと CEO GO 待ち）

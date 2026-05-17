-- /ops プロンプト・ライブラリ用テーブル
-- 2026-05-17 CEO 指示: 投稿/動画台本/ブログ等の定型プロンプトを画面から CRUD する
--
-- 背景: Vercel Functions の FS は読み取り専用のため config/*.json への
--       画面書き込みは不可。AIハブが既に使う Supabase に永続化する。
--
-- 実行方法（CEO 承認時）: Supabase ダッシュボード → SQL Editor に貼って実行
--   対象プロジェクト: 既存共有 zrawhzwtppmlxyhngnju（ai-hub が利用中のもの）

create table if not exists public.ops_prompts (
  id          uuid        primary key default gen_random_uuid(),
  category    text        not null default 'general',
  title       text        not null,
  body        text        not null default '',
  created_at  timestamptz not null default now(),
  updated_at  timestamptz not null default now()
);

create index if not exists ops_prompts_category_idx on public.ops_prompts (category);
create index if not exists ops_prompts_updated_idx  on public.ops_prompts (updated_at desc);

-- RLS: service_role のみアクセス（/api/ops/prompts は SUPABASE_SERVICE_ROLE_KEY で接続）。
-- anon/authenticated には一切公開しない（社内運用データのため）。
alter table public.ops_prompts enable row level security;
-- ポリシーを1つも作らない = service_role 以外は全拒否（service_role は RLS をバイパス）。

-- 初期サンプル（任意・消してよい）。CEO のよく使うジャンルの雛形。
insert into public.ops_prompts (category, title, body) values
  ('投稿',     'Instagram 投稿（クライミングジム告知）',
   E'# 役割\nあなたはクライミングジムの SNS 担当。\n\n# 依頼\n以下のイベント情報から Instagram 投稿文を3案。各案: 1) フック1行 2) 本文（120字前後・絵文字control的に） 3) ハッシュタグ8個。\n\n# イベント情報\n（ここに日時・内容・対象を貼る）'),
  ('動画台本', 'YouTube Shorts 台本（30秒・ムーブ解説）',
   E'# 役割\nクライミング歴30年のコーチ。\n\n# 依頼\n指定の課題/ムーブを初心者向けに 30 秒 Shorts 台本化。構成: フック(3秒)→失敗例→コツ3点→締め(CTA)。各カットに秒数と画ヅラ指示を付ける。\n\n# 対象ムーブ\n（ここに記入）'),
  ('ブログ',   'ブログ記事（SEO+LLMO 構造化）',
   E'# 役割\nコンテンツSEO ライター。\n\n# 依頼\n指定テーマで 2000 字前後の記事。H2/H3 構造・結論先出し・FAQ を3つ末尾に。BlogPosting/FAQPage の JSON-LD も別途出力。一次情報があれば数字で根拠を入れる。\n\n# テーマ\n（ここに記入）')
on conflict do nothing;

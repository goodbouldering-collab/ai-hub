-- portal スキーマの作成（存在しない場合のみ）
create schema if not exists portal;

-- SNS 投稿ログテーブル
create table if not exists portal.sns_posts (
  id              bigserial primary key,
  created_at      timestamptz not null default now(),
  text            text        not null,
  image_url       text,
  x_status        text        not null default 'pending'
                    check (x_status in ('pending','ok','error','skipped')),
  x_post_id       text,
  x_error         text,
  threads_status  text        not null default 'pending'
                    check (threads_status in ('pending','ok','error','skipped')),
  threads_post_id text,
  threads_error   text
);

-- RLS は service_role キーのみ使用するため有効化しない
-- （クラウド管理画面は service_role でアクセスする設計）

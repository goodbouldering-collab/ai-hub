-- AI相談の実行指令室。公開サイト／Data APIには公開しないサービス専用領域。
create schema if not exists command_center;

create schema if not exists command_center;

create table if not exists command_center.projects (
  business_id text primary key,
  display_name text not null,
  status text not null,
  status_label text not null,
  production_url text not null default '',
  hint text not null default '',
  last_review_date text not null default '',
  owner_id text not null default 'site-owner',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists command_center.tasks (
  id text primary key,
  business_id text not null,
  title text not null,
  reason text not null default '',
  priority integer not null default 2,
  status text not null default 'planned',
  due_date text not null default '',
  effort text not null default '',
  blocker text not null default '',
  category text not null default '',
  owner_id text not null default 'site-owner',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists command_center.directives (
  id text primary key,
  business_id text not null,
  mode text not null,
  instruction text not null,
  owner_id text not null default 'site-owner',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists command_center.directive_executions (
  id text primary key,
  directive_id text not null,
  owner_id text not null,
  business_id text not null,
  mode text not null,
  instruction text not null,
  status text not null,
  summary text not null default '',
  result text not null default '',
  error text not null default '',
  thread_id text not null default '',
  version integer not null default 1,
  has_changes boolean not null default false,
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  updated_at timestamptz not null default now()
);

create table if not exists command_center.trades (
  id text primary key,
  traded_at text not null,
  market text not null,
  symbol text not null,
  direction text not null,
  status text not null default 'open',
  entry_price numeric not null default 0,
  quantity numeric not null default 0,
  risk_amount numeric not null default 0,
  pnl numeric not null default 0,
  memo text not null default '',
  owner_id text not null default 'site-owner',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists command_center.trade_plans (
  id text primary key,
  market text not null,
  symbol text not null,
  name text not null default '',
  trade_style text not null default 'cash',
  direction text not null default 'long',
  signal_score integer not null default 0,
  reference_price numeric not null default 0,
  quantity numeric not null default 0,
  stop_price numeric not null default 0,
  target_price numeric not null default 0,
  max_loss numeric not null default 0,
  thesis text not null default '',
  invalidation text not null default '',
  source_as_of text not null default '',
  status text not null default 'draft',
  trade_id text not null default '',
  owner_id text not null default 'site-owner',
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create index if not exists command_center_tasks_status_due_idx
  on command_center.tasks(status, due_date);
create index if not exists command_center_tasks_business_idx
  on command_center.tasks(business_id);
create index if not exists command_center_directives_created_idx
  on command_center.directives(created_at desc);
create index if not exists command_center_trades_status_date_idx
  on command_center.trades(status, traded_at desc);
create index if not exists command_center_trade_plans_status_created_idx
  on command_center.trade_plans(status, created_at desc);
create index if not exists command_center_executions_owner_updated_idx
  on command_center.directive_executions(owner_id, updated_at desc);
create index if not exists command_center_executions_directive_idx
  on command_center.directive_executions(directive_id, version desc);

alter table command_center.projects enable row level security;
alter table command_center.tasks enable row level security;
alter table command_center.directives enable row level security;
alter table command_center.directive_executions enable row level security;
alter table command_center.trades enable row level security;
alter table command_center.trade_plans enable row level security;

-- No browser role receives grants. Vercel server functions use service_role only.
revoke all privileges on schema command_center from anon, authenticated, public;
revoke all privileges on all tables in schema command_center from anon, authenticated, public;
grant usage on schema command_center to service_role;
grant all privileges on all tables in schema command_center to service_role;

alter default privileges in schema command_center
  revoke all on tables from anon, authenticated, public;
alter default privileges in schema command_center
  grant all on tables to service_role;

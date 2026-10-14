-- Private data: only an authenticated Worker or the guarded migration CLI may read it.
-- Keep source rows verbatim; mappers, not SQL rows, form the browser response.
CREATE TABLE IF NOT EXISTS auxiliary_records (
  namespace TEXT NOT NULL CHECK(namespace IN (
    'command_center.projects','command_center.tasks','command_center.directives',
    'command_center.directive_executions','command_center.trades','command_center.trade_plans',
    'command_center.relay_state','command_center.relay_requests','command_center.relay_nonces',
    'ai_watch.articles','portal.sns_posts')),
  record_key TEXT NOT NULL,
  owner_id TEXT NOT NULL,
  payload TEXT NOT NULL CHECK(json_valid(payload)),
  revision INTEGER NOT NULL DEFAULT 1 CHECK(revision > 0),
  PRIMARY KEY(namespace, record_key)
);
CREATE INDEX IF NOT EXISTS auxiliary_owner ON auxiliary_records(namespace, owner_id);

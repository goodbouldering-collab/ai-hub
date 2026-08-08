import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

test("command center storage uses a private schema and six RLS-protected tables", async () => {
  const sql = await readFile(new URL("supabase/migrations/20260808_command_center.sql", root), "utf8");
  assert.match(sql, /create schema if not exists command_center/i);
  for (const table of ["projects", "tasks", "directives", "directive_executions", "trades", "trade_plans"]) {
    assert.match(sql, new RegExp(`create table (?:if not exists )?command_center\\.${table}`, "i"), table);
    assert.match(sql, new RegExp(`alter table command_center\\.${table} enable row level security`, "i"), `${table} RLS`);
  }
  assert.match(sql, /grant all privileges on all tables in schema command_center to service_role/i);
  assert.match(sql, /revoke all privileges on all tables in schema command_center from anon, authenticated, public/i);
  assert.match(sql, /owner_id\s+text\s+not null/i);
  assert.doesNotMatch(sql, /grant .*\b(?:anon|authenticated)\b.*on .*command_center\./i);
});

test("command center repository exposes server-only typed actions", async () => {
  const source = await readFile(new URL("api/_lib/command-center-db.ts", root), "utf8");
  assert.match(source, /from "\.\/supa\.js"/);
  assert.match(source, /schema\("command_center"\)/);
  for (const fn of [
    "loadCommandCenter", "updateCommandCenterTask", "createCommandCenterTask",
    "createCommandCenterDirective", "recordCommandCenterExecution", "createTradePlan",
    "updateTradePlan", "createTrade", "closeTrade", "deleteClosedTrade", "upsertCommandCenterSnapshot",
  ]) assert.match(source, new RegExp(`export (?:async )?function ${fn}`), fn);
  assert.match(source, /owner_id/);
  assert.doesNotMatch(source, /NEXT_PUBLIC_SUPABASE_SERVICE_ROLE_KEY/);
});

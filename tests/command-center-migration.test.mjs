import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

test("command center storage migration declares all durable tables", async () => {
  const migration = await readFile(new URL("supabase/migrations/20260808_command_center.sql", root), "utf8");
  for (const table of ["projects", "tasks", "directives", "directive_executions", "trades", "trade_plans"]) {
    assert.match(migration, new RegExp(`command_center\\.${table}\\b`), table);
  }
  assert.match(migration, /row level security|enable row level security/i);
  assert.doesNotMatch(migration, /grant\s+(select|insert|update|delete).*\b(anon|authenticated)\b/i);
});

test("migration handler does not expose row data in its response", async () => {
  const source = await readFile(new URL("api/admin/command-center-migrate.ts", root), "utf8");
  assert.match(source, /withAdmin/);
  assert.match(source, /hash|checksum/i);
  assert.doesNotMatch(source, /console\.(log|info|error)\([^\n]*(row|snapshot|payload)/i);
});

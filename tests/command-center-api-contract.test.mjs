import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

const apiFiles = [
  "command-center-data.ts", "command-center-calendar.ts", "command-center-market.ts",
  "command-center-brief.ts", "command-center-rankings.ts", "command-center-migrate.ts", "command-center-relay.ts",
  "command-center-screen.ts", "command-center-security.ts", "command-center-market-sources.ts",
];

test("all command center APIs are admin-gated and private", async () => {
  for (const file of apiFiles) {
    const source = await readFile(new URL(`api/admin/${file}`, root), "utf8");
    assert.match(source, /withAdmin/, file);
    assert.match(source, /no-store|private/, `${file} cache policy`);
  }
});

test("command center data API keeps the old actions and does not call the retired D1 route", async () => {
  const source = await readFile(new URL("api/admin/command-center-data.ts", root), "utf8");
  for (const action of [
    "update_task", "create_task", "create_directive", "record_execution", "create_trade",
    "create_trade_plan", "approve_trade_plan", "cancel_trade_plan", "execute_trade_plan", "close_trade", "delete_trade",
  ]) assert.match(source, new RegExp(action), action);
  assert.doesNotMatch(source, /\/api\/dashboard|COMMAND_CENTER_SERVICE_TOKEN/);
  assert.match(source, /Cache-Control|cache-control/);
});

test("calendar is busy-only and migration/relay paths are explicitly protected", async () => {
  const calendar = await readFile(new URL("api/admin/command-center-calendar.ts", root), "utf8");
  assert.match(calendar, /busy_only/);
  assert.doesNotMatch(calendar, /summary|description|attendee|location/);
  const migration = await readFile(new URL("api/admin/command-center-migrate.ts", root), "utf8");
  assert.match(migration, /COMMAND_ROOM_MIGRATION_URL/);
  assert.match(migration, /COMMAND_CENTER_MIGRATION_TOKEN/);
  const relay = await readFile(new URL("api/admin/command-center-relay.ts", root), "utf8");
  assert.match(relay, /HMAC|createHmac|x-command-room-relay-signature/);
  assert.match(relay, /nonce/);
  assert.match(relay, /allowlist|REQUEST_PATHS|allowed/i);
});

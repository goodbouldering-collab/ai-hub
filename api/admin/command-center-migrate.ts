import { createHash } from "node:crypto";
import { withAdmin } from "../_lib/http.js";
import { countCommandCenterRows, upsertCommandCenterSnapshot } from "../_lib/command-center-db.js";
import type { CommandCenterMigrationSnapshot } from "../_lib/command-center-types.js";

function env(name: string): string { return String(process.env[name] || "").trim(); }
function digest(snapshot: unknown): string { return createHash("sha256").update(JSON.stringify(snapshot)).digest("hex"); }
function countSnapshot(snapshot: CommandCenterMigrationSnapshot) { return Object.fromEntries(Object.entries(snapshot.tables).map(([key, rows]) => [key, Array.isArray(rows) ? rows.length : -1])); }
function validSnapshot(value: unknown): value is CommandCenterMigrationSnapshot {
  if (!value || typeof value !== "object") return false;
  const candidate = value as Partial<CommandCenterMigrationSnapshot>;
  if (candidate.schemaVersion !== 1 || candidate.source !== "execution-command-room" || !candidate.tables || typeof candidate.tables !== "object") return false;
  return ["projects", "tasks", "directives", "directive_executions", "trades", "trade_plans"].every((key) => Array.isArray(candidate.tables?.[key as keyof typeof candidate.tables]));
}

export default withAdmin({ method: "POST" }, async ({ res }) => {
  const sourceUrl = env("COMMAND_ROOM_MIGRATION_URL");
  const token = env("COMMAND_CENTER_MIGRATION_TOKEN");
  if (!sourceUrl || token.length < 32) { res.status(503).json({ error: "migration_not_configured" }); return; }
  const response = await fetch(sourceUrl, { headers: { accept: "application/json", "x-command-room-migration-token": token }, cache: "no-store", signal: AbortSignal.timeout(30_000) });
  if (!response.ok) { res.status(502).json({ error: "migration_source_unavailable", status: response.status }); return; }
  const snapshot = await response.json().catch(() => null);
  if (!validSnapshot(snapshot)) { res.status(422).json({ error: "migration_snapshot_invalid" }); return; }
  const counts = countSnapshot(snapshot);
  const sourceDigest = digest(snapshot);
  const result = await upsertCommandCenterSnapshot(snapshot);
  const verified = await countCommandCenterRows(result.ownerId);
  const mismatches = Object.fromEntries(Object.entries(counts).flatMap(([key, expected]) => Number(expected) === Number(verified[key as keyof typeof verified]) ? [] : [[key, { expected, actual: verified[key as keyof typeof verified] }]]));
  if (Object.keys(mismatches).length) { res.status(409).json({ error: "migration_verification_mismatch", sourceDigest, counts: result.counts, mismatches }); return; }
  res.setHeader("Cache-Control", "private, no-store, max-age=0");
  res.status(200).json({ ok: true, source: "execution-command-room", sourceDigest, exportedAt: snapshot.exportedAt, counts: result.counts, verified });
});

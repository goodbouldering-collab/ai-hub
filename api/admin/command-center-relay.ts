import { createHmac, timingSafeEqual } from "node:crypto";
import { db } from "../_lib/supa.js";
import { withAdmin } from "../_lib/http.js";
import type { VercelReq, VercelRes } from "../_lib/auth.js";

const RELAY_ID = "primary";
const COOKIE_NAME = "command_center_bridge_session";
const REQUEST_PATHS = [
  { method: "POST", pattern: /^\/v1\/runs$/ },
  { method: "GET", pattern: /^\/v1\/runs\/[A-Za-z0-9_-]+$/ },
  { method: "POST", pattern: /^\/v1\/runs\/[A-Za-z0-9_-]+\/(?:interrupt|adjust)$/ },
  { method: "POST", pattern: /^\/v1\/runs\/[A-Za-z0-9_-]+\/approvals\/[^/]+$/ },
];

function secret(): string { return String(process.env.COMMAND_ROOM_BRIDGE_AUTH_SECRET || "").trim(); }
function header(req: VercelReq, name: string): string { const value = req.headers[name]; return Array.isArray(value) ? String(value[0] || "") : String(value || ""); }
function safeEqual(left: string, right: string): boolean { const a = Buffer.from(left); const b = Buffer.from(right); return a.length === b.length && timingSafeEqual(a, b); }
function sign(value: string): string { return createHmac("sha256", secret()).update(value).digest("base64url"); }
function json(res: VercelRes, status: number, payload: unknown, headers: Record<string, string> = {}) { res.setHeader("Cache-Control", "private, no-store, max-age=0"); for (const [key, value] of Object.entries(headers)) res.setHeader(key, value); res.status(status).json(payload); }
function relayTable(name: "relay_state" | "relay_requests" | "relay_nonces"): any { return (db() as any).schema("command_center").from(name); }
function nowIso() { return new Date().toISOString(); }
function base64(value: string): string { return Buffer.from(value, "utf8").toString("base64url"); }
function fromBase64(value: string): string { return Buffer.from(value, "base64url").toString("utf8"); }
function cookie(req: VercelReq): string {
  const raw = header(req, "cookie");
  const entry = raw.split(";").map((part) => part.trim()).find((part) => part.startsWith(`${COOKIE_NAME}=`));
  return entry ? decodeURIComponent(entry.slice(COOKIE_NAME.length + 1)) : "";
}
function session(req: VercelReq): { sid: string; exp: number } | null {
  const [encoded, signature, extra] = cookie(req).split(".");
  if (!encoded || !signature || extra || !secret() || !safeEqual(signature, sign(encoded))) return null;
  try {
    const value = JSON.parse(fromBase64(encoded)) as { v?: number; sid?: string; exp?: number };
    if (value.v !== 1 || !value.sid || !Number.isFinite(value.exp) || Number(value.exp) < Date.now()) return null;
    return { sid: value.sid, exp: Number(value.exp) };
  } catch { return null; }
}
function sessionCookie(sid: string, exp: number): string {
  const encoded = base64(JSON.stringify({ v: 1, sid, exp }));
  return `${COOKIE_NAME}=${encodeURIComponent(`${encoded}.${sign(encoded)}`)}; Path=/api/admin/command-center/relay; HttpOnly; Secure; SameSite=Strict; Max-Age=${Math.max(0, Math.floor((exp - Date.now()) / 1000))}`;
}
function pairHash(code: string): string { return sign(`pair:${code}`); }

async function signedBridge(req: VercelReq, res: VercelRes): Promise<void> {
  const configured = secret();
  if (!configured) { json(res, 503, { error: "relay_secret_missing" }); return; }
  const timestamp = header(req, "x-command-room-relay-timestamp");
  const signature = header(req, "x-command-room-relay-signature");
  const raw = typeof req.body === "string" ? req.body : JSON.stringify(req.body || {});
  const timestampMs = Number(timestamp);
  if (!signature || !Number.isFinite(timestampMs) || Math.abs(Date.now() - timestampMs) > 60_000 || !safeEqual(signature, createHmac("sha256", configured).update(`${timestamp}.${raw}`).digest("base64url"))) { json(res, 401, { error: "relay_auth_required" }); return; }
  let input: Record<string, any>;
  try { input = typeof req.body === "string" ? JSON.parse(req.body || "{}") : (req.body || {}); } catch { json(res, 400, { error: "invalid_json" }); return; }
  const nonce = String(input.nonce || "");
  if (!nonce || nonce.length > 200) { json(res, 401, { error: "relay_nonce_required" }); return; }
  await relayTable("relay_nonces").delete().lt("expires_at", nowIso());
  const nonceResult = await relayTable("relay_nonces").insert({ nonce, expires_at: new Date(Date.now() + 120_000).toISOString() });
  if (nonceResult.error) { json(res, 401, { error: "relay_nonce_reused" }); return; }
  if (input.action === "heartbeat") {
    const existing = await relayTable("relay_state").select("pair_hash,pair_used_at").eq("id", RELAY_ID).maybeSingle();
    const candidateHash = /^\d{6}$/.test(String(input.pairCode || "")) ? pairHash(String(input.pairCode)) : "";
    const preserveUsed = existing.data?.pair_hash && existing.data.pair_hash === candidateHash && existing.data.pair_used_at ? existing.data.pair_used_at : null;
    const upsert = await relayTable("relay_state").upsert({ id: RELAY_ID, heartbeat_at: nowIso(), pair_hash: candidateHash, pair_expires_at: input.pairExpiresAt || null, pair_used_at: preserveUsed, bridge_json: input.bridge || {}, failed_attempts: 0, attempt_reset_at: null }, { onConflict: "id" });
    if (upsert.error) { json(res, 500, { error: "relay_state_failed" }); return; }
    await relayTable("relay_requests").delete().lt("expires_at", nowIso());
    const stale = new Date(Date.now() - 10_000).toISOString();
    const pending = await relayTable("relay_requests").select("id,method,path,body_json").or(`status.eq.pending,and(status.eq.dispatched,updated_at.lt.${stale})`).order("created_at", { ascending: true }).limit(10);
    if (pending.error) { json(res, 500, { error: "relay_request_failed" }); return; }
    for (const item of pending.data || []) await relayTable("relay_requests").update({ status: "dispatched", updated_at: nowIso() }).eq("id", item.id);
    json(res, 200, { ok: true, rotatePairCode: Boolean(preserveUsed), requests: (pending.data || []).map((item: any) => ({ id: item.id, method: item.method, path: item.path, body: item.body_json || {} })) });
    return;
  }
  if (input.action === "complete") {
    const id = String(input.requestId || "");
    if (!id) { json(res, 400, { error: "request_id_required" }); return; }
    const update = await relayTable("relay_requests").update({ status: "completed", status_code: Number(input.statusCode) || 200, response_json: input.response || {}, updated_at: nowIso() }).eq("id", id);
    if (update.error) { json(res, 500, { error: "relay_complete_failed" }); return; }
    json(res, 200, { ok: true }); return;
  }
  json(res, 400, { error: "unknown_bridge_action" });
}

const browserHandler = withAdmin({ method: ["GET", "POST"] }, async ({ req, res, body }) => {
  const stateResult = await relayTable("relay_state").select("*").eq("id", RELAY_ID).maybeSingle();
  const state = stateResult.data;
  if ((req.method || "GET").toUpperCase() === "GET") {
    const url = new URL(req.url || "/api/admin/command-center/relay", "https://aiclimb.vercel.app");
    const requestId = url.searchParams.get("requestId");
    if (!requestId) {
      const heartbeatAt = state?.heartbeat_at || null;
      json(res, 200, { connected: Boolean(heartbeatAt && Date.now() - new Date(heartbeatAt).getTime() <= 15_000), paired: Boolean(session(req)), heartbeatAt, bridge: state?.bridge_json || null }); return;
    }
    const current = session(req);
    if (!current) { json(res, 401, { error: "bridge_pairing_required" }); return; }
    const result = await relayTable("relay_requests").select("status,status_code,response_json").eq("id", requestId).eq("session_id", current.sid).maybeSingle();
    if (!result.data) { json(res, 404, { error: "relay_request_not_found" }); return; }
    json(res, 200, { status: result.data.status, statusCode: result.data.status_code, response: result.data.status === "completed" ? result.data.response_json : null }); return;
  }
  if (body?.action === "pair") {
    const code = String(body.code || "");
    if (!state || !state.pair_hash || !state.pair_expires_at || new Date(state.pair_expires_at).getTime() < Date.now() || state.pair_used_at || !/^\d{6}$/.test(code)) { json(res, 409, { error: "pairing_not_available" }); return; }
    const attempts = Number(state.failed_attempts || 0);
    if (attempts >= 10) { json(res, 429, { error: "too_many_attempts" }); return; }
    if (!safeEqual(pairHash(code), String(state.pair_hash))) { await relayTable("relay_state").update({ failed_attempts: attempts + 1, attempt_reset_at: new Date(Date.now() + 60_000).toISOString() }).eq("id", RELAY_ID); json(res, 401, { error: "invalid_pairing_code" }); return; }
    const sid = crypto.randomUUID(); const exp = Date.now() + 30 * 24 * 60 * 60 * 1000;
    const claim = await relayTable("relay_state").update({ pair_used_at: nowIso(), failed_attempts: 0, attempt_reset_at: null }).eq("id", RELAY_ID).eq("pair_hash", state.pair_hash).is("pair_used_at", null);
    if (claim.error) { json(res, 409, { error: "pairing_code_already_used" }); return; }
    res.setHeader("Set-Cookie", sessionCookie(sid, exp)); json(res, 200, { ok: true, pairedAt: nowIso() }); return;
  }
  if (body?.action === "request") {
    const current = session(req); if (!current) { json(res, 401, { error: "bridge_pairing_required" }); return; }
    const method = String(body.method || "GET").toUpperCase(); const path = String(body.path || "");
    if (!REQUEST_PATHS.some((entry) => entry.method === method && entry.pattern.test(path))) { json(res, 403, { error: "relay_path_not_allowed" }); return; }
    const id = crypto.randomUUID(); const created = nowIso();
    const inserted = await relayTable("relay_requests").insert({ id, session_id: current.sid, method, path, body_json: body.body || {}, status: "pending", status_code: 0, response_json: {}, created_at: created, updated_at: created, expires_at: new Date(Date.now() + 60 * 60_000).toISOString() });
    if (inserted.error) { json(res, 500, { error: "relay_request_insert_failed" }); return; }
    json(res, 202, { id, status: "pending" }); return;
  }
  json(res, 400, { error: "unknown_browser_action" });
});

export default async function handler(req: VercelReq, res: VercelRes) {
  if ((req.method || "GET").toUpperCase() === "POST" && header(req, "x-command-room-relay-signature")) return signedBridge(req, res);
  return browserHandler(req, res);
}

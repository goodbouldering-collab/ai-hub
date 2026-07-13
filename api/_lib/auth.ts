import { createHmac } from "node:crypto";
import type { IncomingMessage, ServerResponse } from "node:http";

export type VercelReq = IncomingMessage & { body?: any; query?: Record<string, string | string[]> };
export type VercelRes = ServerResponse & {
  status: (code: number) => VercelRes;
  json: (body: any) => VercelRes;
  send: (body: any) => VercelRes;
  setHeader: (name: string, value: string | number | readonly string[]) => VercelRes;
};

const ADMIN_COOKIE = "ai_hub_admin_session";
const SESSION_MAX_AGE_SECONDS = 60 * 60 * 24 * 14;

export function requireAdminAuth(req: VercelReq, res: VercelRes): boolean {
  const expectedPass = process.env.ADMIN_PASS || "";
  if (!expectedPass) {
    res.status(500).json({ error: "ADMIN_PASS env not configured" });
    return false;
  }

  if (hasValidAdminSession(req)) {
    return true;
  }

  if (wantsHtml(req) || isAdminPageRequest(req)) {
    const next = safeNextFromRequest(req);
    res.status(303);
    res.setHeader("Location", `/admin/login?next=${encodeURIComponent(next)}`);
    res.send("Redirecting to admin login");
    return false;
  }

  res.status(401).json({ error: "Authentication required" });
  return false;
}

export function hasValidAdminSession(req: VercelReq): boolean {
  if (!sessionSecret()) return false;
  const token = parseCookies(req)[ADMIN_COOKIE];
  if (!token) return false;
  const [expiresRaw, signature] = token.split(".");
  const expires = Number(expiresRaw);
  if (!Number.isFinite(expires) || expires < Date.now() || !signature) return false;
  return timingSafeEqual(signature, signSessionExpiry(expires));
}

export function isAdminPassword(password: string): boolean {
  const expectedPass = process.env.ADMIN_PASS || "";
  return Boolean(expectedPass) && timingSafeEqual(password, expectedPass);
}

export function createAdminSessionCookie(): string {
  const expires = Date.now() + SESSION_MAX_AGE_SECONDS * 1000;
  const token = `${expires}.${signSessionExpiry(expires)}`;
  return [
    `${ADMIN_COOKIE}=${encodeURIComponent(token)}`,
    "Path=/",
    "HttpOnly",
    "Secure",
    "SameSite=Lax",
    `Max-Age=${SESSION_MAX_AGE_SECONDS}`,
  ].join("; ");
}

export function clearAdminSessionCookie(): string {
  return [
    `${ADMIN_COOKIE}=`,
    "Path=/",
    "HttpOnly",
    "Secure",
    "SameSite=Lax",
    "Max-Age=0",
  ].join("; ");
}

export function safeNextPath(value: unknown): string {
  const raw = Array.isArray(value) ? value[0] : value;
  if (typeof raw !== "string" || !raw) return "/admin";
  if (!raw.startsWith("/") || raw.startsWith("//")) return "/admin";
  return raw;
}

function parseCookies(req: VercelReq): Record<string, string> {
  const header = req.headers.cookie;
  const cookieHeader = Array.isArray(header) ? header.join("; ") : header || "";
  const cookies: Record<string, string> = {};
  for (const part of cookieHeader.split(";")) {
    const idx = part.indexOf("=");
    if (idx < 0) continue;
    const name = part.slice(0, idx).trim();
    if (!name) continue;
    try {
      cookies[name] = decodeURIComponent(part.slice(idx + 1).trim());
    } catch {
      cookies[name] = "";
    }
  }
  return cookies;
}

function safeNextFromRequest(req: VercelReq): string {
  try {
    const url = new URL(req.url || "/admin", "https://ai-hub-jp.vercel.app");
    return safeNextPath(url.pathname + url.search);
  } catch {
    return "/admin";
  }
}

function wantsHtml(req: VercelReq): boolean {
  if ((req.method || "GET").toUpperCase() !== "GET") return false;
  const accept = String(req.headers.accept || "");
  return accept.includes("text/html");
}

function isAdminPageRequest(req: VercelReq): boolean {
  if ((req.method || "GET").toUpperCase() !== "GET") return false;
  try {
    const url = new URL(req.url || "/admin", "https://ai-hub-jp.vercel.app");
    const path = url.pathname.replace(/\/$/, "") || "/";
    return [
      "/admin",
      "/api/admin",
      "/admin/apps/blog",
      "/api/admin/apps/blog",
      "/admin/apps/reel",
      "/api/admin/apps/reel",
      "/admin/chat",
      "/api/admin/chat",
      "/admin/gubble-sns",
      "/api/admin/gubble-sns",
      "/admin/sns-post",
      "/api/admin/sns-post",
      "/ops",
      "/api/ops",
    ].includes(path);
  } catch {
    return false;
  }
}

function signSessionExpiry(expires: number): string {
  return createHmac("sha256", sessionSecret()).update(String(expires)).digest("base64url");
}

function sessionSecret(): string {
  return process.env.ADMIN_SESSION_SECRET || process.env.ADMIN_PASS || "";
}

function timingSafeEqual(a: string, b: string): boolean {
  const ba = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ba.length !== bb.length) return false;
  let diff = 0;
  for (let i = 0; i < ba.length; i++) diff |= ba[i] ^ bb[i];
  return diff === 0;
}

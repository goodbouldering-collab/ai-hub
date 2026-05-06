import type { IncomingMessage, ServerResponse } from "node:http";

export type VercelReq = IncomingMessage & { body?: any; query?: Record<string, string | string[]> };
export type VercelRes = ServerResponse & {
  status: (code: number) => VercelRes;
  json: (body: any) => VercelRes;
  send: (body: any) => VercelRes;
  setHeader: (name: string, value: string | number | readonly string[]) => VercelRes;
};

export function requireBasicAuth(req: VercelReq, res: VercelRes): boolean {
  const expectedUser = process.env.ADMIN_USER || "";
  const expectedPass = process.env.ADMIN_PASS || "";
  if (!expectedUser || !expectedPass) {
    res.status(500).json({ error: "ADMIN_USER / ADMIN_PASS env not configured" });
    return false;
  }
  const header = req.headers["authorization"] || "";
  if (typeof header !== "string" || !header.startsWith("Basic ")) {
    res.setHeader("WWW-Authenticate", 'Basic realm="ai-hub admin", charset="UTF-8"');
    res.status(401).send("Authentication required");
    return false;
  }
  const decoded = Buffer.from(header.slice(6), "base64").toString("utf-8");
  const idx = decoded.indexOf(":");
  if (idx < 0) {
    res.setHeader("WWW-Authenticate", 'Basic realm="ai-hub admin", charset="UTF-8"');
    res.status(401).send("Invalid auth");
    return false;
  }
  const user = decoded.slice(0, idx);
  const pass = decoded.slice(idx + 1);
  const ok =
    timingSafeEqual(user, expectedUser) && timingSafeEqual(pass, expectedPass);
  if (!ok) {
    res.setHeader("WWW-Authenticate", 'Basic realm="ai-hub admin", charset="UTF-8"');
    res.status(401).send("Invalid credentials");
    return false;
  }
  return true;
}

function timingSafeEqual(a: string, b: string): boolean {
  const ba = Buffer.from(a);
  const bb = Buffer.from(b);
  if (ba.length !== bb.length) return false;
  let diff = 0;
  for (let i = 0; i < ba.length; i++) diff |= ba[i] ^ bb[i];
  return diff === 0;
}

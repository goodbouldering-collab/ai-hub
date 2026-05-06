/**
 * /api/admin → /admin の HTML を Basic 認証ゲートで返す。
 * vercel.json の rewrites で /admin と /admin/ を /api/admin に転送する。
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { requireBasicAuth, type VercelReq, type VercelRes } from "../_lib/auth.js";

let cachedHtml: string | null = null;

export default async function handler(req: VercelReq, res: VercelRes) {
  if (!requireBasicAuth(req, res)) return;
  if (!cachedHtml) {
    try {
      const p = join(process.cwd(), "site", "static", "admin", "index.html");
      cachedHtml = readFileSync(p, "utf-8");
    } catch (e: any) {
      res.status(500).send("admin html not found: " + e.message);
      return;
    }
  }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.status(200).send(cachedHtml);
}

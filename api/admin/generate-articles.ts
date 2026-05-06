import { requireBasicAuth, type VercelReq, type VercelRes } from "../_lib/auth.js";
import { generateArticleDrafts } from "../_lib/ai.js";

export default async function handler(req: VercelReq, res: VercelRes) {
  if (!requireBasicAuth(req, res)) return;
  if (req.method !== "POST") {
    res.status(405).json({ error: "POST only" });
    return;
  }
  const body = await readJson(req);
  const theme = String(body?.theme || "").trim();
  const count = Math.min(Math.max(Number(body?.count) || 3, 1), 5);
  if (!theme) {
    res.status(400).json({ error: "theme is required" });
    return;
  }
  try {
    const drafts = await generateArticleDrafts(theme, count);
    res.status(200).json({ drafts });
  } catch (e: any) {
    res.status(500).json({ error: e.message || String(e) });
  }
}

async function readJson(req: VercelReq): Promise<any> {
  if (req.body && typeof req.body === "object") return req.body;
  const chunks: Buffer[] = [];
  for await (const c of req as any) chunks.push(c as Buffer);
  const text = Buffer.concat(chunks).toString("utf-8");
  if (!text) return {};
  return JSON.parse(text);
}

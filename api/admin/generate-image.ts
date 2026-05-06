import { requireBasicAuth, type VercelReq, type VercelRes } from "../_lib/auth.js";
import { generateImageBytes } from "../_lib/ai.js";
import { uploadPublicImage } from "../_lib/storage.js";

export default async function handler(req: VercelReq, res: VercelRes) {
  if (!requireBasicAuth(req, res)) return;
  if (req.method !== "POST") {
    res.status(405).json({ error: "POST only" });
    return;
  }
  const body = await readJson(req);
  const prompt = String(body?.prompt || "").trim();
  const filenameHint = String(body?.filenameHint || "group").trim();
  if (!prompt) {
    res.status(400).json({ error: "prompt is required" });
    return;
  }
  try {
    const { bytes, contentType } = await generateImageBytes(prompt);
    const safeName = `${filenameHint.replace(/[^\w-]/g, "_")}.png`;
    const url = await uploadPublicImage(bytes, safeName, contentType);
    res.status(200).json({ url });
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

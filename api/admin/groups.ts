import { requireBasicAuth, type VercelReq, type VercelRes } from "../_lib/auth.js";
import { listGroups, createGroup, updateGroup } from "../_lib/colorme.js";

export default async function handler(req: VercelReq, res: VercelRes) {
  if (!requireBasicAuth(req, res)) return;

  try {
    if (req.method === "GET") {
      const limit = Math.min(Number((req.query as any)?.limit) || 50, 100);
      const offset = Number((req.query as any)?.offset) || 0;
      const data = await listGroups(limit, offset);
      res.status(200).json(data);
      return;
    }
    if (req.method === "POST") {
      const body = await readJson(req);
      const name = String(body?.name || "").trim();
      if (!name) {
        res.status(400).json({ error: "name is required" });
        return;
      }
      const created = await createGroup({
        name,
        image_url: body?.image_url,
        expl: body?.expl,
        display_state: body?.display_state || "hidden",
        parent_group_id: body?.parent_group_id ?? null,
      });
      res.status(200).json(created);
      return;
    }
    if (req.method === "PUT") {
      const body = await readJson(req);
      const id = body?.id;
      if (!id) {
        res.status(400).json({ error: "id is required" });
        return;
      }
      const updated = await updateGroup(id, {
        name: body?.name,
        image_url: body?.image_url,
        expl: body?.expl,
        display_state: body?.display_state,
      });
      res.status(200).json(updated);
      return;
    }
    res.status(405).json({ error: "method not allowed" });
  } catch (e: any) {
    res.status(e.status || 500).json({ error: e.message || String(e), body: e.body });
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

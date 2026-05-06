import { ValidationError, withAdmin } from "../_lib/http.js";
import { listGroups, createGroup, updateGroup } from "../_lib/colorme.js";

export default withAdmin(
  { method: ["GET", "POST", "PUT"] },
  async ({ req, res, body }) => {
    if (req.method === "GET") {
      const limit = Math.min(Number((req.query as any)?.limit) || 50, 100);
      const offset = Number((req.query as any)?.offset) || 0;
      const data = await listGroups(limit, offset);
      res.status(200).json(data);
      return;
    }
    if (req.method === "POST") {
      const name = String(body?.name || "").trim();
      if (!name) throw new ValidationError("name is required");
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
      const id = body?.id;
      if (!id) throw new ValidationError("id is required");
      const updated = await updateGroup(id, {
        name: body?.name,
        image_url: body?.image_url,
        expl: body?.expl,
        display_state: body?.display_state,
      });
      res.status(200).json(updated);
      return;
    }
  },
);

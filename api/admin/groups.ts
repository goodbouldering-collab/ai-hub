import { ValidationError, withAdmin } from "../_lib/http.js";
import {
  createGroup,
  getGroup,
  listChildGroups,
  listTopLevelGroups,
  updateGroup,
} from "../_lib/colorme.js";

/**
 * GET /api/admin/groups?parent=ID  → parent の子グループ一覧 (sort 昇順)
 * GET /api/admin/groups?top=1      → トップレベル（親候補）一覧
 * GET /api/admin/groups?id=ID      → 単一グループ取得（編集時の本文 expl ロード用）
 * POST /api/admin/groups           → 新規作成。parent_group_id 必須・sort=0 先頭配置
 *                                    （他の兄弟は sort+1 にシフト）
 * PUT  /api/admin/groups           → 単一更新 ({id, name?, image_url?, expl?, ...})
 */
export default withAdmin(
  { method: ["GET", "POST", "PUT"] },
  async ({ req, res, body }) => {
    if (req.method === "GET") {
      const q = (req.query || {}) as Record<string, string | undefined>;
      if (q.top) {
        res.status(200).json({ groups: await listTopLevelGroups() });
        return;
      }
      if (q.id) {
        const got = await getGroup(q.id);
        res.status(200).json(got?.group ?? got);
        return;
      }
      const parent = q.parent;
      if (!parent) {
        throw new ValidationError("?parent=ID / ?top=1 / ?id=ID のいずれかを指定してください");
      }
      res.status(200).json({ groups: await listChildGroups(parent) });
      return;
    }

    if (req.method === "POST") {
      const name = String(body?.name || "").trim();
      const parent_group_id = body?.parent_group_id;
      if (!name) throw new ValidationError("name is required");
      if (!parent_group_id) throw new ValidationError("parent_group_id is required");

      // 既存兄弟の sort を +1 シフトして先頭スペースを空ける
      const siblings = await listChildGroups(parent_group_id);
      // 並列で更新（ただし API レート制限を考慮して逐次処理）
      for (const sib of siblings) {
        const cur = Number(sib.sort ?? 0);
        await updateGroup(sib.id, { sort: cur + 1 });
      }

      const created = await createGroup({
        name,
        image_url: body?.image_url,
        expl: body?.expl,
        display_state: body?.display_state || "hidden",
        parent_group_id: Number(parent_group_id),
        sort: 0,
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
        sort: body?.sort,
      });
      res.status(200).json(updated);
      return;
    }
  },
);

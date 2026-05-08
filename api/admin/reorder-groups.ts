/**
 * 子グループの並び替え一括更新。
 * 入力: { parentId: number, orderedIds: number[] }
 *   orderedIds の並び順がそのまま sort=0,1,2,... に対応する。
 *
 * カラーミー API は一括更新エンドポイントが無いため、内部で逐次 PUT する。
 * UI 側は楽観的更新 → 失敗したら原状復帰を選べるよう、結果配列を返す。
 */
import { ValidationError, withAdmin } from "../_lib/http.js";
import { updateGroup } from "../_lib/colorme.js";

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const parentId = body?.parentId;
  const orderedIds = body?.orderedIds;
  if (!parentId) throw new ValidationError("parentId is required");
  if (!Array.isArray(orderedIds) || orderedIds.length === 0) {
    throw new ValidationError("orderedIds (array) is required");
  }
  const results: { id: number; sort: number; ok: boolean; error?: string }[] = [];
  for (let i = 0; i < orderedIds.length; i++) {
    const id = Number(orderedIds[i]);
    try {
      await updateGroup(id, { sort: i });
      results.push({ id, sort: i, ok: true });
    } catch (e: any) {
      results.push({ id, sort: i, ok: false, error: e?.message || String(e) });
    }
  }
  res.status(200).json({ ok: results.every((r) => r.ok), results });
});

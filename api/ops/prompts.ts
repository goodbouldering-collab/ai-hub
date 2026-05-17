/**
 * /api/ops/prompts → プロンプト・ライブラリの CRUD（Basic 認証必須）
 *
 * CEO 指示（2026-05-17）: 投稿・動画台本・ブログ等の定型プロンプトを
 * 画面から追加・編集・複製・削除して次々足せるようにする。
 *
 * 永続化先: Supabase テーブル ops_prompts
 *   理由: Vercel Functions の FS は読み取り専用のため config/*.json への
 *         画面書き込みは不可。AIハブは既に Supabase service_role を運用中。
 *   スキーマ（CEO 承認時に Supabase で実行する SQL は本実装に同梱）:
 *     create table ops_prompts (
 *       id uuid primary key default gen_random_uuid(),
 *       category text not null default 'general',
 *       title text not null,
 *       body text not null default '',
 *       created_at timestamptz not null default now(),
 *       updated_at timestamptz not null default now()
 *     );
 *     alter table ops_prompts enable row level security;  -- service_role のみ（公開しない）
 *
 * メソッド:
 *   GET                       → 全件（category, updated_at desc）
 *   POST   {category,title,body}        → 新規作成
 *   POST   {cloneFrom:<id>}             → 複製（title に「(コピー)」付与）
 *   PUT    {id,category?,title?,body?}  → 更新
 *   DELETE {id}                        → 削除
 */
import { withAdmin, ValidationError } from "../_lib/http.js";
import { db } from "../_lib/supa.js";

const TABLE = "ops_prompts";

type PromptRow = {
  id: string;
  category: string;
  title: string;
  body: string;
  created_at: string;
  updated_at: string;
};

function str(v: unknown, field: string, { required = false, max = 20000 } = {}): string {
  if (v == null || v === "") {
    if (required) throw new ValidationError(`${field} は必須です`);
    return "";
  }
  if (typeof v !== "string") throw new ValidationError(`${field} は文字列で指定してください`);
  const s = v.trim();
  if (s.length > max) throw new ValidationError(`${field} が長すぎます（最大 ${max} 文字）`);
  return s;
}

export default withAdmin(
  { method: ["GET", "POST", "PUT", "DELETE"] },
  async ({ req, res, body }) => {
    const supa = db();
    const method = (req.method || "GET").toUpperCase();

    // ---- GET: 全件 ----
    if (method === "GET") {
      const { data, error } = await supa
        .from(TABLE)
        .select("*")
        .order("category", { ascending: true })
        .order("updated_at", { ascending: false })
        .limit(500); // 運用本部の手書きプロンプト想定。肥大時のメモリ/レイテンシ防止
      if (error) throw new Error(`prompts 取得失敗: ${error.message}`);
      res.status(200).json({ prompts: (data as PromptRow[]) || [] });
      return;
    }

    // ---- POST: 新規 or 複製 ----
    if (method === "POST") {
      const cloneFrom = str(body?.cloneFrom, "cloneFrom");
      if (cloneFrom) {
        const { data: src, error: e1 } = await supa
          .from(TABLE)
          .select("*")
          .eq("id", cloneFrom)
          .single();
        if (e1 || !src) throw new ValidationError("複製元が見つかりません");
        const s = src as PromptRow;
        const { data, error } = await supa
          .from(TABLE)
          .insert({ category: s.category, title: `${s.title}（コピー）`, body: s.body })
          .select()
          .single();
        if (error) throw new Error(`複製失敗: ${error.message}`);
        res.status(201).json({ prompt: data });
        return;
      }
      const category = str(body?.category, "category") || "general";
      const title = str(body?.title, "title", { required: true, max: 200 });
      const text = str(body?.body, "body", { max: 20000 });
      const { data, error } = await supa
        .from(TABLE)
        .insert({ category, title, body: text })
        .select()
        .single();
      if (error) throw new Error(`作成失敗: ${error.message}`);
      res.status(201).json({ prompt: data });
      return;
    }

    // ---- PUT: 更新 ----
    if (method === "PUT") {
      const id = str(body?.id, "id", { required: true, max: 64 });
      const patch: Record<string, string> = { updated_at: new Date().toISOString() };
      if (body?.category != null) patch.category = str(body.category, "category") || "general";
      if (body?.title != null) patch.title = str(body.title, "title", { required: true, max: 200 });
      if (body?.body != null) patch.body = str(body.body, "body", { max: 20000 });
      const { data, error } = await supa
        .from(TABLE)
        .update(patch)
        .eq("id", id)
        .select()
        .single();
      if (error) throw new Error(`更新失敗: ${error.message}`);
      if (!data) throw new ValidationError("更新対象が見つかりません");
      res.status(200).json({ prompt: data });
      return;
    }

    // ---- DELETE ----
    if (method === "DELETE") {
      const id = str(body?.id, "id", { required: true, max: 64 });
      const { error } = await supa.from(TABLE).delete().eq("id", id);
      if (error) throw new Error(`削除失敗: ${error.message}`);
      res.status(200).json({ ok: true });
      return;
    }
  },
);

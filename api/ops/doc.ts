/**
 * /api/ops/doc?file=<slug> → consul-work の MD 1 件を HTML 化して JSON で返す（管理ログイン必須）
 *
 * CEO 指示（2026-05-17）: MD を全文ずらっと展開する旧 /admin/docs はやめる。
 * /ops は要点（タスク）を主に出し、原文は「必要時だけ折りたたみで開く」。
 * このエンドポイントはその折りたたみが開かれたときだけ呼ばれる遅延ロード用。
 *
 * - file 未指定 → 一覧（slug/title/date/category）のみ返す（軽量・本文は返さない）
 * - file 指定   → その 1 件だけ marked で HTML 化して返す
 * marked / gray-matter は既存 /admin/docs と同じ依存（package.json に既存）。
 */
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join, resolve, sep } from "node:path";
import { marked } from "marked";
import matter from "gray-matter";
import { withAdmin, ValidationError } from "../_lib/http.js";

const DIR_CANDIDATES = [
  join(process.cwd(), "content", "consul-work"),
  join(process.cwd(), "..", "content", "consul-work"),
];

function resolveDir(): string | null {
  for (const p of DIR_CANDIDATES) if (existsSync(p)) return p;
  return null;
}

const BIZ_RE =
  /^\d{4}-\d{2}-\d{2}-(gubble|progging|not-este|n-design|business-21|carat|climb-hero|fadie|minanowa|ai-hub|trust|ceo|consulting|service|contact|achievements|render|all)/;

function meta(filename: string) {
  const slug = filename.replace(/\.md$/, "");
  const dm = filename.match(/^(\d{4}-\d{2}-\d{2})/);
  const bm = filename.match(BIZ_RE);
  return {
    slug,
    filename,
    date: dm ? dm[1] : "0000-00-00",
    category: bm ? bm[1] : "general",
  };
}

export default withAdmin({ method: "GET" }, async ({ req, res }) => {
  const dir = resolveDir();
  if (!dir) {
    res.status(200).json({ docs: [], note: "consul-work 未同期" });
    return;
  }

  const url = new URL(req.url || "/", "http://x");
  const fileSlug = url.searchParams.get("file");

  // 一覧（本文なし・軽量）
  if (!fileSlug) {
    const docs = readdirSync(dir)
      .filter((f) => f.endsWith(".md"))
      .map((f) => {
        const m = meta(f);
        const raw = readFileSync(join(dir, f), "utf-8");
        const parsed = matter(raw);
        const h1 = parsed.content.match(/^#\s+(.+)$/m);
        const title =
          (parsed.data.title as string | undefined) ||
          (h1 ? h1[1].trim() : m.slug);
        return { ...m, title };
      })
      .sort((a, b) => b.date.localeCompare(a.date));
    res.status(200).json({ docs });
    return;
  }

  // 個別 1 件（本文を HTML 化）
  const safe = fileSlug.replace(/[^0-9a-zA-Z._-]/g, "");
  if (!safe) throw new ValidationError("file が不正です");
  const filename = safe.endsWith(".md") ? safe : `${safe}.md`;
  const full = resolve(dir, filename);
  // 明示的なディレクトリ封じ込め（文字フィルタの保険・パストラバーサル防止）
  if (full !== resolve(dir, ".") && !full.startsWith(resolve(dir) + sep)) {
    throw new ValidationError("file が不正です");
  }
  if (!existsSync(full)) {
    res.status(404).json({ error: "not found", file: filename });
    return;
  }
  const raw = readFileSync(full, "utf-8");
  const parsed = matter(raw);
  const m = meta(filename);
  const h1 = parsed.content.match(/^#\s+(.+)$/m);
  const title =
    (parsed.data.title as string | undefined) || (h1 ? h1[1].trim() : m.slug);
  const html = await marked.parse(parsed.content);
  res.status(200).json({ ...m, title, html });
});

/**
 * /api/admin/docs → /admin/docs の HTML を返す。
 * consul/work/ から取り込んだ Markdown を一覧表示する。
 *
 * - 認証: withAdmin で管理ログインゲート
 * - データソース: ai-hub/content/consul-work/*.md（GitHub Actions で日次同期される）
 * - 表示: 左サイドバー（日付降順）+ 中央ペイン（進捗ロードマップを初期表示）
 * - 個別ドキュメント: /admin/docs?file=<slug> でクエリ指定
 */
import { readFileSync, readdirSync, existsSync } from "node:fs";
import { join } from "node:path";
import { marked } from "marked";
import matter from "gray-matter";
import { withAdmin } from "../../_lib/http.js";

interface DocEntry {
  slug: string;       // ファイル名（拡張子なし）
  title: string;      // frontmatter.title or 見出し or ファイル名
  date: string;       // ファイル名先頭の YYYY-MM-DD or frontmatter.date
  category: string;   // 事業略称 or "general"
  filename: string;   // 元ファイル名
}

const CONTENT_DIR_CANDIDATES = [
  join(process.cwd(), "content", "consul-work"),
  join(process.cwd(), "..", "content", "consul-work"),
];

function resolveContentDir(): string | null {
  for (const p of CONTENT_DIR_CANDIDATES) {
    if (existsSync(p)) return p;
  }
  return null;
}

function listDocs(contentDir: string): DocEntry[] {
  const files = readdirSync(contentDir).filter((f) => f.endsWith(".md"));
  const entries: DocEntry[] = files.map((filename) => {
    const slug = filename.replace(/\.md$/, "");
    const raw = readFileSync(join(contentDir, filename), "utf-8");
    const parsed = matter(raw);
    const fmDate = parsed.data.date as string | undefined;
    const fmTitle = parsed.data.title as string | undefined;

    // ファイル名から日付を抽出（例: 2026-05-12-xxx.md）
    const dateMatch = filename.match(/^(\d{4}-\d{2}-\d{2})/);
    const date = fmDate || (dateMatch ? dateMatch[1] : "0000-00-00");

    // ファイル名から事業略称を抽出（例: 2026-05-12-gubble-xxx.md → gubble）
    const businessMatch = filename.match(
      /^\d{4}-\d{2}-\d{2}-(gubble|not-este|n-design|business-21|carat|climb-hero|fadie|minanowa|ai-hub|ceo|consulting|service|contact|achievements|render|all)/,
    );
    const category = businessMatch ? businessMatch[1] : "general";

    // タイトル: frontmatter > 最初の # 見出し > ファイル名
    let title = fmTitle || "";
    if (!title) {
      const h1Match = parsed.content.match(/^#\s+(.+)$/m);
      title = h1Match ? h1Match[1].trim() : slug;
    }

    return { slug, title, date, category, filename };
  });

  // 日付降順
  return entries.sort((a, b) => b.date.localeCompare(a.date));
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

function renderHtml(docs: DocEntry[], current: DocEntry | null, bodyHtml: string): string {
  const sidebar = docs
    .map((d) => {
      const active = current && current.slug === d.slug ? "active" : "";
      return `<li class="${active}">
        <a href="/admin/docs?file=${encodeURIComponent(d.slug)}">
          <span class="date">${escapeHtml(d.date)}</span>
          <span class="cat cat-${escapeHtml(d.category)}">${escapeHtml(d.category)}</span>
          <span class="title">${escapeHtml(d.title)}</span>
        </a>
      </li>`;
    })
    .join("\n");

  const breadcrumbs = current
    ? `<nav class="crumbs"><a href="/admin">/admin</a> &raquo; <a href="/admin/docs">docs</a> &raquo; <span>${escapeHtml(current.filename)}</span></nav>`
    : `<nav class="crumbs"><a href="/admin">/admin</a> &raquo; <span>docs</span></nav>`;

  return `<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AIスペシャリスト 由井辰美</title>
<meta name="robots" content="noindex,nofollow">
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  :root {
    --bg: #0d1126; --bg2:#141938; --panel:rgba(255,255,255,.05);
    --border:rgba(255,255,255,.14); --text:#e8ebf5; --muted:#aab1c5;
    --accent:#7aa2ff; --accent2:#c77dff; --ok:#7eeba3; --err:#ff7a90;
    --code-bg: rgba(0,0,0,.35);
  }
  body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Hiragino Sans','Noto Sans JP',sans-serif;
    background:linear-gradient(180deg,#0a0d1a,#0d1126 50%,#0a0d1a);
    color:var(--text); min-height:100vh; line-height:1.65; }
  .layout { display:flex; min-height:100vh; }
  aside { width:340px; flex-shrink:0; padding:18px 14px; border-right:1px solid var(--border);
    overflow-y:auto; max-height:100vh; position:sticky; top:0; background:rgba(13,17,38,.7); backdrop-filter:blur(10px); }
  aside h1 { font-size:14px; font-weight:800; letter-spacing:.05em; text-transform:uppercase;
    background:linear-gradient(100deg,var(--accent),var(--accent2));
    -webkit-background-clip:text; background-clip:text; color:transparent;
    margin-bottom:14px; }
  aside input.filter { width:100%; padding:8px 10px; border-radius:8px;
    background:rgba(255,255,255,.06); border:1px solid var(--border);
    color:var(--text); font:inherit; font-size:12px; margin-bottom:12px; }
  aside ul { list-style:none; }
  aside li { margin-bottom:6px; }
  aside li a { display:block; padding:8px 10px; border-radius:8px; text-decoration:none;
    color:var(--text); border:1px solid transparent; transition:all .15s; }
  aside li a:hover { background:rgba(122,162,255,.1); border-color:rgba(122,162,255,.35); }
  aside li.active a { background:rgba(122,162,255,.18); border-color:rgba(122,162,255,.5); }
  aside li .date { display:inline-block; font-size:10.5px; color:var(--muted); letter-spacing:.02em; margin-right:6px; }
  aside li .cat { display:inline-block; font-size:9.5px; padding:1px 6px; border-radius:999px;
    background:rgba(199,125,255,.2); color:var(--accent2); margin-right:6px; vertical-align:middle; }
  aside li .cat-ceo { background:rgba(126,235,163,.18); color:var(--ok); }
  aside li .cat-consulting { background:rgba(122,162,255,.18); color:var(--accent); }
  aside li .title { display:block; font-size:12.5px; margin-top:3px; }
  main { flex:1; padding:32px 48px; max-width:980px; }
  .crumbs { font-size:12px; color:var(--muted); margin-bottom:16px; }
  .crumbs a { color:var(--accent); text-decoration:none; }
  .crumbs a:hover { text-decoration:underline; }
  article { background:var(--panel); border:1px solid var(--border); border-radius:14px;
    padding:28px 32px; backdrop-filter:blur(10px); }
  article h1 { font-size:26px; font-weight:800; margin-bottom:18px;
    background:linear-gradient(100deg,var(--accent),var(--accent2));
    -webkit-background-clip:text; background-clip:text; color:transparent; }
  article h2 { font-size:20px; font-weight:700; margin:24px 0 12px;
    padding-bottom:6px; border-bottom:1px solid var(--border); }
  article h3 { font-size:16px; font-weight:700; margin:20px 0 10px; color:var(--accent); }
  article p { margin:10px 0; }
  article ul, article ol { margin:10px 0 10px 24px; }
  article li { margin-bottom:4px; }
  article a { color:var(--accent); text-decoration:underline; }
  article code { background:var(--code-bg); padding:2px 6px; border-radius:4px;
    font-family:'SFMono-Regular',Consolas,monospace; font-size:0.9em; }
  article pre { background:var(--code-bg); padding:14px 16px; border-radius:8px;
    overflow-x:auto; margin:14px 0; border:1px solid var(--border); }
  article pre code { background:transparent; padding:0; }
  article blockquote { border-left:3px solid var(--accent);
    padding:6px 14px; margin:12px 0; color:var(--muted); background:rgba(122,162,255,.06); border-radius:0 8px 8px 0; }
  article table { border-collapse:collapse; margin:14px 0; width:100%; font-size:13.5px; }
  article th, article td { border:1px solid var(--border); padding:8px 12px; text-align:left; }
  article th { background:rgba(255,255,255,.04); font-weight:700; color:var(--accent); }
  .placeholder { text-align:center; padding:60px 20px; color:var(--muted); }
  .placeholder h2 { color:var(--text); margin-bottom:8px; }
  .meta { font-size:11.5px; color:var(--muted); margin-bottom:18px; padding:6px 12px;
    background:rgba(0,0,0,.2); border-radius:8px; display:inline-block; }
</style>
</head>
<body>
<div class="layout">
  <aside>
    <h1>経営本部 docs</h1>
    <input class="filter" type="text" placeholder="絞り込み（タイトル / 日付 / 事業）" oninput="filterDocs(this.value)">
    <ul id="doc-list">
      ${sidebar}
    </ul>
  </aside>
  <main>
    ${breadcrumbs}
    <article>
      ${bodyHtml}
    </article>
  </main>
</div>
<script>
function filterDocs(q) {
  const norm = (q || "").toLowerCase().trim();
  const items = document.querySelectorAll("#doc-list li");
  items.forEach((li) => {
    const text = li.textContent.toLowerCase();
    li.style.display = !norm || text.includes(norm) ? "" : "none";
  });
}
</script>
</body>
</html>`;
}

export default withAdmin({ method: "GET" }, async ({ req, res }) => {
  const contentDir = resolveContentDir();
  if (!contentDir) {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res.status(200).send(renderHtml([], null, `
      <div class="placeholder">
        <h2>経営本部ドキュメントがまだ同期されていません</h2>
        <p>GitHub Actions が consul リポを同期するまでお待ちください。</p>
        <p style="margin-top:14px;font-size:12px;">あるいは初回の手動コピー（content/consul-work/）が完了していない可能性があります。</p>
      </div>
    `));
    return;
  }

  const docs = listDocs(contentDir);

  // クエリで個別ファイル指定
  const url = new URL(req.url || "/", "http://x");
  const fileSlug = url.searchParams.get("file");

  let currentDoc: DocEntry | null = null;
  let bodyHtml = "";

  if (fileSlug) {
    currentDoc = docs.find((d) => d.slug === fileSlug) || null;
    if (currentDoc) {
      const raw = readFileSync(join(contentDir, currentDoc.filename), "utf-8");
      const parsed = matter(raw);
      const meta = `<div class="meta">📄 ${escapeHtml(currentDoc.filename)} · ${escapeHtml(currentDoc.date)} · <span class="cat">${escapeHtml(currentDoc.category)}</span></div>`;
      bodyHtml = meta + (await marked.parse(parsed.content));
    } else {
      bodyHtml = `<div class="placeholder"><h2>ドキュメントが見つかりません</h2><p>slug: ${escapeHtml(fileSlug)}</p></div>`;
    }
  } else {
    // トップ: 進捗ロードマップを優先表示
    const roadmap = docs.find((d) => d.slug.includes("ceo-roadmap-progress"));
    if (roadmap) {
      currentDoc = roadmap;
      const raw = readFileSync(join(contentDir, roadmap.filename), "utf-8");
      const parsed = matter(raw);
      const meta = `<div class="meta">📋 進捗ロードマップ · ${escapeHtml(roadmap.date)}</div>`;
      bodyHtml = meta + (await marked.parse(parsed.content));
    } else {
      bodyHtml = `<div class="placeholder">
        <h2>経営本部 ドキュメント一覧</h2>
        <p>${docs.length} 件のドキュメント。左サイドバーから選択してください。</p>
      </div>`;
    }
  }

  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.status(200).send(renderHtml(docs, currentDoc, bodyHtml));
});

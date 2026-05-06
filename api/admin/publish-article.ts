/**
 * AI 生成記事 + 公開日 を、カラーミーテンプレートのトップページ index.html
 * の AI ブロックに埋め込んで PUT する。
 *
 * リクエスト:
 *   {
 *     groupId: number | string,   // カラーミーグループID
 *     title: string,               // 表示タイトル
 *     html: string,                // <h2> 始まりのシンプル HTML
 *     publishedAt: string,         // YYYY-MM-DD
 *     target: "preview" | "live"   // preview=1086 / live=1064
 *   }
 */

import { requireBasicAuth, type VercelReq, type VercelRes } from "../_lib/auth.js";
import { getTemplatePage, updateTemplatePage } from "../_lib/colorme.js";
import {
  ensureOuterBlock,
  extractOuterBlock,
  replaceOuterBlock,
  upsertArticle,
} from "../_lib/template_block.js";

const PREVIEW_TEMPLATE = Number(process.env.COLORME_PREVIEW_TEMPLATE_ID || 1086);
const LIVE_TEMPLATE = Number(process.env.COLORME_LIVE_TEMPLATE_ID || 1064);

export default async function handler(req: VercelReq, res: VercelRes) {
  if (!requireBasicAuth(req, res)) return;
  if (req.method !== "POST") {
    res.status(405).json({ error: "POST only" });
    return;
  }
  const body = await readJson(req);
  const groupId = body?.groupId;
  const title = String(body?.title || "").trim();
  const html = String(body?.html || "").trim();
  const publishedAt = String(body?.publishedAt || "").trim();
  const target = body?.target === "live" ? "live" : "preview";

  if (!groupId || !title || !html || !publishedAt) {
    res.status(400).json({ error: "groupId, title, html, publishedAt are required" });
    return;
  }

  const templateId = target === "live" ? LIVE_TEMPLATE : PREVIEW_TEMPLATE;

  try {
    const page = await getTemplatePage(templateId, "index");
    const currentHtml: string = page?.page?.html || "";
    if (!currentHtml) {
      res.status(500).json({ error: "template index html が空です（取得失敗の可能性）" });
      return;
    }
    const ensured = ensureOuterBlock(currentHtml);
    const outer = extractOuterBlock(ensured);
    const articleHtml = renderArticleBlock({ title, html, publishedAt });
    const newOuter = upsertArticle(outer, String(groupId), articleHtml, "top");
    const newPageHtml = replaceOuterBlock(ensured, newOuter);
    await updateTemplatePage(templateId, "index", { html: newPageHtml });
    res.status(200).json({
      ok: true,
      target,
      templateId,
      blockSize: articleHtml.length,
      pageSize: newPageHtml.length,
    });
  } catch (e: any) {
    res.status(e.status || 500).json({ error: e.message || String(e), body: e.body });
  }
}

function renderArticleBlock(input: { title: string; html: string; publishedAt: string }): string {
  const safeTitle = escapeHtml(input.title);
  const safeDate = escapeHtml(input.publishedAt);
  return `<section class="ai-group-article" data-published="${safeDate}">
<h2>${safeTitle}</h2>
<p class="ai-group-article__date"><small>${safeDate} 公開</small></p>
${input.html}
</section>`;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

async function readJson(req: VercelReq): Promise<any> {
  if (req.body && typeof req.body === "object") return req.body;
  const chunks: Buffer[] = [];
  for await (const c of req as any) chunks.push(c as Buffer);
  const text = Buffer.concat(chunks).toString("utf-8");
  if (!text) return {};
  return JSON.parse(text);
}

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

import { ValidationError, withAdmin } from "../_lib/http.js";
import { templateIdFor } from "../_lib/config.js";
import { getTemplatePage, updateTemplatePage } from "../_lib/colorme.js";
import {
  ensureOuterBlock,
  extractOuterBlock,
  replaceOuterBlock,
  upsertArticle,
} from "../_lib/template_block.js";
import { sanitizeArticleHtml } from "../_lib/sanitize.js";

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const groupId = body?.groupId;
  const title = String(body?.title || "").trim();
  const html = sanitizeArticleHtml(String(body?.html || "").trim());
  const publishedAt = String(body?.publishedAt || "").trim();
  const target: "preview" | "live" = body?.target === "live" ? "live" : "preview";

  if (!groupId || !title || !html || !publishedAt) {
    throw new ValidationError("groupId, title, html, publishedAt are required");
  }

  const templateId = templateIdFor(target);
  const page = await getTemplatePage(templateId, "index");
  const currentHtml: string = page?.page?.html || "";
  if (!currentHtml) {
    throw new Error("template index html が空です（取得失敗の可能性）");
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
});

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

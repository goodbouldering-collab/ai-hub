/**
 * AI 生成記事 + 公開日 を、指定された「対象親グループ」のページ
 * (product_list.html, mode=grp&gid=parentId) のトップに記事ブロックを挿入する。
 *
 * カラーミーは groups 専用テンプレを持たず、商品一覧テンプレ (product_list)
 * を mode に応じて使い回す仕様。そのため Smarty の条件で
 * 「mode=grp かつ gid==parentId のときだけ表示する」よう囲む。
 *
 * リクエスト:
 *   {
 *     parentGroupId: number,       // 対象親グループID（記事を表示したいグループ）
 *     groupId: number | string,    // 個別の子グループ ID（block id 用）
 *     title: string,               // 表示タイトル
 *     html: string,                // <h2> 始まりのシンプル HTML
 *     publishedAt: string,         // YYYY-MM-DD
 *     target: "preview" | "live"
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

const PAGE_TYPE = "product_list"; // groups 専用テンプレが無いので商品一覧テンプレを共用

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const parentGroupId = Number(body?.parentGroupId);
  const groupId = body?.groupId;
  const title = String(body?.title || "").trim();
  const html = sanitizeArticleHtml(String(body?.html || "").trim());
  const publishedAt = String(body?.publishedAt || "").trim();
  const target: "preview" | "live" = body?.target === "live" ? "live" : "preview";

  if (!parentGroupId || !groupId || !title || !html || !publishedAt) {
    throw new ValidationError(
      "parentGroupId, groupId, title, html, publishedAt are required",
    );
  }

  const templateId = templateIdFor(target);
  const page = await getTemplatePage(templateId, PAGE_TYPE);
  const currentHtml: string = page?.template_page?.html || "";
  if (!currentHtml) {
    throw new Error("template product_list html が空です（取得失敗の可能性）");
  }
  const ensured = ensureOuterBlock(currentHtml);
  const outer = extractOuterBlock(ensured);
  const articleHtml = renderArticleBlock({ title, html, publishedAt, parentGroupId });
  const newOuter = upsertArticle(outer, String(groupId), articleHtml, "top");
  const newPageHtml = replaceOuterBlock(ensured, newOuter);
  await updateTemplatePage(templateId, PAGE_TYPE, { html: newPageHtml });
  res.status(200).json({
    ok: true,
    target,
    templateId,
    pageType: PAGE_TYPE,
    blockSize: articleHtml.length,
    pageSize: newPageHtml.length,
  });
});

/**
 * 記事1件分の HTML を Smarty 条件で囲む。
 * ・mode=grp かつ gid==parentGroupId のときだけ表示
 * ・将来このブロックをスタイリングしやすいよう class を付与
 */
function renderArticleBlock(input: {
  title: string;
  html: string;
  publishedAt: string;
  parentGroupId: number;
}): string {
  const safeTitle = escapeHtml(input.title);
  const safeDate = escapeHtml(input.publishedAt);
  return `{if $smarty.get.mode == "grp" && $smarty.get.gid == ${input.parentGroupId}}
<section class="ai-group-article" data-published="${safeDate}">
<h2>${safeTitle}</h2>
<p class="ai-group-article__date"><small>${safeDate} 公開</small></p>
${input.html}
</section>
{/if}`;
}

function escapeHtml(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

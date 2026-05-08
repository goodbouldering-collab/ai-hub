/**
 * product_list テンプレから対象 groupId の AI 記事ブロックを削除し、
 * 同時にカラーミーグループの display_state を hidden に戻す（live 時のみ）。
 */

import { ValidationError, withAdmin } from "../_lib/http.js";
import { templateIdFor } from "../_lib/config.js";
import { getTemplatePage, updateTemplatePage, updateGroup } from "../_lib/colorme.js";
import {
  ensureOuterBlock,
  extractOuterBlock,
  replaceOuterBlock,
  removeArticle,
} from "../_lib/template_block.js";

const PAGE_TYPE = "product_list";

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const groupId = body?.groupId;
  const target: "preview" | "live" = body?.target === "live" ? "live" : "preview";
  const hideGroup = body?.hideGroup !== false;

  if (!groupId) throw new ValidationError("groupId is required");

  const templateId = templateIdFor(target);
  const page = await getTemplatePage(templateId, PAGE_TYPE);
  const currentHtml: string = page?.template_page?.html || "";
  const ensured = ensureOuterBlock(currentHtml);
  const outer = extractOuterBlock(ensured);
  const newOuter = removeArticle(outer, String(groupId));
  const newPageHtml = replaceOuterBlock(ensured, newOuter);
  await updateTemplatePage(templateId, PAGE_TYPE, { html: newPageHtml });

  if (hideGroup && target === "live") {
    try {
      await updateGroup(groupId, { display_state: "hidden" });
    } catch {
      // best-effort; テンプレ側はもう外している
    }
  }
  res.status(200).json({ ok: true, target, templateId, pageType: PAGE_TYPE });
});

/**
 * テンプレートトップから AI 記事ブロックを削除し、
 * 同時にカラーミーグループの display_state を hidden に戻す。
 */

import { requireBasicAuth, type VercelReq, type VercelRes } from "../_lib/auth.js";
import { getTemplatePage, updateTemplatePage, updateGroup } from "../_lib/colorme.js";
import {
  ensureOuterBlock,
  extractOuterBlock,
  replaceOuterBlock,
  removeArticle,
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
  const target = body?.target === "live" ? "live" : "preview";
  const hideGroup = body?.hideGroup !== false;

  if (!groupId) {
    res.status(400).json({ error: "groupId is required" });
    return;
  }
  const templateId = target === "live" ? LIVE_TEMPLATE : PREVIEW_TEMPLATE;
  try {
    const page = await getTemplatePage(templateId, "index");
    const currentHtml: string = page?.page?.html || "";
    const ensured = ensureOuterBlock(currentHtml);
    const outer = extractOuterBlock(ensured);
    const newOuter = removeArticle(outer, String(groupId));
    const newPageHtml = replaceOuterBlock(ensured, newOuter);
    await updateTemplatePage(templateId, "index", { html: newPageHtml });

    if (hideGroup && target === "live") {
      try {
        await updateGroup(groupId, { display_state: "hidden" });
      } catch {
        /* グループ非表示化は best-effort */
      }
    }
    res.status(200).json({ ok: true, target, templateId });
  } catch (e: any) {
    res.status(e.status || 500).json({ error: e.message || String(e), body: e.body });
  }
}

async function readJson(req: VercelReq): Promise<any> {
  if (req.body && typeof req.body === "object") return req.body;
  const chunks: Buffer[] = [];
  for await (const c of req as any) chunks.push(c as Buffer);
  const text = Buffer.concat(chunks).toString("utf-8");
  if (!text) return {};
  return JSON.parse(text);
}

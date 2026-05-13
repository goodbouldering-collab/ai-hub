/**
 * /api/admin/chat
 *   POST { history: [{role:"user"|"assistant", content:string}, ...] }
 *     → { reply: string }
 *   GET  → /admin/chat の HTML を Basic 認証ゲートで返す
 *
 * vercel.json で /admin/chat → /api/admin/chat にルーティング、Basic 認証は withAdmin が担う。
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { ValidationError, withAdmin } from "../_lib/http.js";
import { chatWithContext } from "../_lib/ai.js";
import { buildChatContext } from "../_lib/chat_context.js";

let cachedHtml: string | null = null;

function loadChatHtml(): string {
  if (cachedHtml) return cachedHtml;
  const p = join(process.cwd(), "site", "static", "admin", "chat.html");
  cachedHtml = readFileSync(p, "utf-8");
  return cachedHtml;
}

export default withAdmin(
  { method: ["GET", "POST"] },
  async ({ req, res, body }) => {
    if (req.method === "GET") {
      try {
        res.setHeader("Content-Type", "text/html; charset=utf-8");
        res.status(200).send(loadChatHtml());
      } catch (e: any) {
        res.status(500).send("admin chat html not found: " + e.message);
      }
      return;
    }

    // POST: チャット応答
    const history = body?.history;
    if (!Array.isArray(history) || history.length === 0) {
      throw new ValidationError("history は非空配列で必要です");
    }
    // 最新の user 発話
    const last = history[history.length - 1];
    if (!last || last.role !== "user" || typeof last.content !== "string" || !last.content.trim()) {
      throw new ValidationError("最後のメッセージは role=user で content が必要です");
    }
    // 簡易レート制限的に長すぎる履歴は刈る（直近 12 ターン）
    const trimmed: { role: "user" | "assistant"; content: string }[] = history
      .slice(-12)
      .map((m: any) => ({
        role: (m.role === "assistant" ? "assistant" : "user") as "user" | "assistant",
        content: String(m.content || "").slice(0, 6000),
      }));

    const context = buildChatContext(last.content);
    const reply = await chatWithContext(trimmed, context);
    res.status(200).json({ reply });
  },
);

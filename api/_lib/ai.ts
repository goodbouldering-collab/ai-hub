import Anthropic from "@anthropic-ai/sdk";
import { ConfigError, ValidationError } from "./http.js";
import { claudeModel, requireEnv } from "./config.js";
import { sanitizeArticleHtml } from "./sanitize.js";

export type ArticleDraft = {
  title: string;
  html: string;
  summary: string;
};

const SYSTEM_PROMPT = `あなたはクライミング/ボルダリング用品店「グッぼる」のEC店長コピーライターです。
入力テーマからカラーミーショップの商品グループに添えるブログ記事案を作成します。

出力ルール:
- title: グループ名としても通用する短い日本語（10〜25文字、装飾記号なし）
- html: <h2> から始まり <p>/<ul>/<li>/<strong> 等の最小限のタグのみ使用。CSS や class 属性は一切付けない。1記事あたり <h2> が2〜4個、各セクション 100〜200 文字。最後に <p> で来店誘導 or 詳細リンク誘導の一文。
- summary: 30〜60文字の要約

出力は JSON 配列のみ。前置き・コードフェンス禁止。`;

let _client: Anthropic | null = null;
function client(): Anthropic {
  if (_client) return _client;
  const apiKey = requireEnv("ANTHROPIC_API_KEY");
  _client = new Anthropic({ apiKey });
  return _client;
}

function extractText(message: any): string {
  return (message.content || [])
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text)
    .join("\n")
    .trim();
}

function extractJson(text: string, kind: "array" | "object"): any {
  const open = kind === "array" ? "[" : "{";
  const close = kind === "array" ? "]" : "}";
  const start = text.indexOf(open);
  const end = text.lastIndexOf(close);
  if (start === -1 || end === -1) {
    throw new ValidationError(
      `AI 出力を JSON(${kind}) として解釈できません: ${text.slice(0, 200)}`,
    );
  }
  try {
    return JSON.parse(text.slice(start, end + 1));
  } catch (e: any) {
    throw new ValidationError(`JSON parse failed: ${e.message}`);
  }
}

export async function generateArticleDrafts(theme: string, count = 3): Promise<ArticleDraft[]> {
  const message = await client().messages.create({
    model: claudeModel(),
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: "user",
        content: `テーマ: ${theme}\n\n上記テーマで ${count} 案を JSON 配列 [{title,html,summary}, ...] で返してください。`,
      },
    ],
  });
  const parsed = extractJson(extractText(message), "array");
  if (!Array.isArray(parsed)) throw new ValidationError("AI 出力が配列ではありません");
  return parsed.map((p: any) => ({
    title: String(p.title || "").trim(),
    html: sanitizeArticleHtml(String(p.html || "")),
    summary: String(p.summary || "").trim(),
  }));
}

export async function reviseArticle(
  current: { title: string; html: string },
  instruction: string,
): Promise<{ title: string; html: string }> {
  const message = await client().messages.create({
    model: claudeModel(),
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: "user",
        content: `現在のタイトル: ${current.title}\n現在の本文HTML:\n${current.html}\n\n修正指示: ${instruction}\n\n修正後を JSON {title, html} で返してください。`,
      },
    ],
  });
  const obj = extractJson(extractText(message), "object");
  return {
    title: String(obj.title || current.title).trim(),
    html: sanitizeArticleHtml(String(obj.html || current.html)),
  };
}

export async function generateImageBytes(prompt: string): Promise<{
  bytes: Uint8Array;
  contentType: string;
}> {
  const apiKey = requireEnv("OPENAI_API_KEY");
  const res = await fetch("https://api.openai.com/v1/images/generations", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${apiKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      model: "dall-e-3",
      prompt,
      n: 1,
      size: "1024x1024",
      response_format: "b64_json",
    }),
  });
  if (!res.ok) {
    const txt = await res.text();
    const err: any = new Error(`DALL-E error ${res.status}: ${txt.slice(0, 300)}`);
    err.status = res.status;
    throw err;
  }
  const data = await res.json();
  const b64 = data?.data?.[0]?.b64_json;
  if (!b64) throw new ValidationError("DALL-E 応答に b64_json が無い");
  return { bytes: Buffer.from(b64, "base64"), contentType: "image/png" };
}

// re-export for tests / direct use
export { sanitizeArticleHtml };

// 互換: ConfigError を呼び出し元から見られるようにエクスポート
export { ConfigError };

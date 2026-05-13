import Anthropic from "@anthropic-ai/sdk";
import { ConfigError, ValidationError } from "./http.js";
import { claudeModel, requireEnv } from "./config.js";
import { sanitizeArticleHtml } from "./sanitize.js";

// Vercel Functions の maxDuration=60s に対し 55s で打ち切る。
// SDK と fetch の双方に同じ AbortSignal を渡してリーク防止。
const UPSTREAM_TIMEOUT_MS = 55_000;

export type ArticleDraft = {
  title: string;
  html: string;
  summary: string;
};

function timeoutSignal(ms = UPSTREAM_TIMEOUT_MS): { signal: AbortSignal; cancel: () => void } {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(new Error(`upstream timeout after ${ms}ms`)), ms);
  return {
    signal: ctrl.signal,
    cancel: () => clearTimeout(timer),
  };
}

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
  const t = timeoutSignal();
  try {
    const message = await client().messages.create(
      {
        model: claudeModel(),
        max_tokens: 4096,
        system: SYSTEM_PROMPT,
        messages: [
          {
            role: "user",
            content: `テーマ: ${theme}\n\n上記テーマで ${count} 案を JSON 配列 [{title,html,summary}, ...] で返してください。`,
          },
        ],
      },
      { signal: t.signal },
    );
    const parsed = extractJson(extractText(message), "array");
    if (!Array.isArray(parsed)) throw new ValidationError("AI 出力が配列ではありません");
    return parsed.map((p: any) => ({
      title: String(p.title || "").trim(),
      html: sanitizeArticleHtml(String(p.html || "")),
      summary: String(p.summary || "").trim(),
    }));
  } catch (e: any) {
    if (e?.name === "AbortError" || /aborted|timeout/i.test(String(e?.message || ""))) {
      const err: any = new Error("Claude 応答が制限時間を超過しました（55秒）");
      err.status = 504;
      throw err;
    }
    throw e;
  } finally {
    t.cancel();
  }
}

export async function reviseArticle(
  current: { title: string; html: string },
  instruction: string,
): Promise<{ title: string; html: string }> {
  const t = timeoutSignal();
  try {
    const message = await client().messages.create(
      {
        model: claudeModel(),
        max_tokens: 4096,
        system: SYSTEM_PROMPT,
        messages: [
          {
            role: "user",
            content: `現在のタイトル: ${current.title}\n現在の本文HTML:\n${current.html}\n\n修正指示: ${instruction}\n\n修正後を JSON {title, html} で返してください。`,
          },
        ],
      },
      { signal: t.signal },
    );
    const obj = extractJson(extractText(message), "object");
    return {
      title: String(obj.title || current.title).trim(),
      html: sanitizeArticleHtml(String(obj.html || current.html)),
    };
  } catch (e: any) {
    if (e?.name === "AbortError" || /aborted|timeout/i.test(String(e?.message || ""))) {
      const err: any = new Error("Claude 応答が制限時間を超過しました（55秒）");
      err.status = 504;
      throw err;
    }
    throw e;
  } finally {
    t.cancel();
  }
}

export async function generateImageBytes(prompt: string): Promise<{
  bytes: Uint8Array;
  contentType: string;
}> {
  const apiKey = requireEnv("OPENAI_API_KEY");
  const t = timeoutSignal();
  try {
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
      signal: t.signal,
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
  } catch (e: any) {
    if (e?.name === "AbortError") {
      const err: any = new Error("DALL-E 応答が制限時間を超過しました（55秒）");
      err.status = 504;
      throw err;
    }
    throw e;
  } finally {
    t.cancel();
  }
}

/**
 * 社内ドキュメント参照付きのチャット応答を生成する。
 * context（事業 CLAUDE.md / consul/work 抜粋など）は呼び出し側で組み立てて system に積む。
 */
export async function chatWithContext(
  history: { role: "user" | "assistant"; content: string }[],
  context: string,
): Promise<string> {
  const t = timeoutSignal();
  const systemPrompt =
    "あなたは『AIハブ』の社内アシスタントです。CEO（由井辰美）の 9 事業（グッぼる / Notエステ / Nデザイン / ビジネス21 / カラッと / みんなのWA / ファディー / トラスト / AIハブ）の運用を補佐します。\n" +
    "回答の方針:\n" +
    "- 提示された <context> 内のドキュメントを最優先の根拠にする\n" +
    "- 推測で答えず、根拠が無いときは「ドキュメントに記載なし」と明示する\n" +
    "- 簡潔・箇条書き優先・日本語\n" +
    "- ファイルや箇所を引用するときは consul-work/<filename> 形式で示す\n\n" +
    "<context>\n" + context + "\n</context>";
  try {
    const message = await client().messages.create(
      {
        model: claudeModel(),
        max_tokens: 1500,
        system: systemPrompt,
        messages: history.map((m) => ({ role: m.role, content: m.content })),
      },
      { signal: t.signal },
    );
    return extractText(message);
  } catch (e: any) {
    if (e?.name === "AbortError" || /aborted|timeout/i.test(String(e?.message || ""))) {
      const err: any = new Error("Claude 応答が制限時間を超過しました（55秒）");
      err.status = 504;
      throw err;
    }
    throw e;
  } finally {
    t.cancel();
  }
}

// re-export for tests / direct use
export { sanitizeArticleHtml };

// 互換: ConfigError を呼び出し元から見られるようにエクスポート
export { ConfigError };

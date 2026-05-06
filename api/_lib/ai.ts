import Anthropic from "@anthropic-ai/sdk";

export type ArticleDraft = {
  title: string;        // = グループ名候補
  html: string;         // <h2> から始まる CSS なしのシンプルな HTML
  summary: string;      // 一行要約
};

const SYSTEM_PROMPT = `あなたはクライミング/ボルダリング用品店「グッぼる」のEC店長コピーライターです。
入力テーマからカラーミーショップの商品グループに添えるブログ記事案を作成します。

出力ルール:
- title: グループ名としても通用する短い日本語（10〜25文字、装飾記号なし）
- html: <h2> から始まり <p>/<ul>/<li>/<strong> 等の最小限のタグのみ使用。CSS や class 属性は一切付けない。1記事あたり <h2> が2〜4個、各セクション 100〜200 文字。最後に <p> で来店誘導 or 詳細リンク誘導の一文。
- summary: 30〜60文字の要約

出力は JSON 配列のみ。前置き・コードフェンス禁止。`;

export async function generateArticleDrafts(theme: string, count = 3): Promise<ArticleDraft[]> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) throw new Error("ANTHROPIC_API_KEY not set");
  const client = new Anthropic({ apiKey });

  const message = await client.messages.create({
    model: process.env.AI_HUB_CLAUDE_MODEL || "claude-sonnet-4-6",
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: "user",
        content: `テーマ: ${theme}\n\n上記テーマで ${count} 案を JSON 配列 [{title,html,summary}, ...] で返してください。`,
      },
    ],
  });

  const text = message.content
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text)
    .join("\n")
    .trim();

  // JSON 抽出（モデルが余計な装飾を付けた場合に備える）
  const start = text.indexOf("[");
  const end = text.lastIndexOf("]");
  if (start === -1 || end === -1) {
    throw new Error(`AI 出力を JSON として解釈できません: ${text.slice(0, 200)}`);
  }
  const jsonText = text.slice(start, end + 1);
  let parsed: any;
  try {
    parsed = JSON.parse(jsonText);
  } catch (e: any) {
    throw new Error(`JSON parse failed: ${e.message} / raw: ${jsonText.slice(0, 200)}`);
  }
  if (!Array.isArray(parsed)) throw new Error("AI 出力が配列ではありません");
  return parsed.map((p: any) => ({
    title: String(p.title || "").trim(),
    html: String(p.html || "").trim(),
    summary: String(p.summary || "").trim(),
  }));
}

export async function reviseArticle(
  current: { title: string; html: string },
  instruction: string,
): Promise<{ title: string; html: string }> {
  const apiKey = process.env.ANTHROPIC_API_KEY;
  if (!apiKey) throw new Error("ANTHROPIC_API_KEY not set");
  const client = new Anthropic({ apiKey });

  const message = await client.messages.create({
    model: process.env.AI_HUB_CLAUDE_MODEL || "claude-sonnet-4-6",
    max_tokens: 4096,
    system: SYSTEM_PROMPT,
    messages: [
      {
        role: "user",
        content: `現在のタイトル: ${current.title}\n現在の本文HTML:\n${current.html}\n\n修正指示: ${instruction}\n\n修正後を JSON {title, html} で返してください。`,
      },
    ],
  });

  const text = message.content
    .filter((b: any) => b.type === "text")
    .map((b: any) => b.text)
    .join("\n")
    .trim();
  const start = text.indexOf("{");
  const end = text.lastIndexOf("}");
  if (start === -1 || end === -1) throw new Error("AI 出力を JSON として解釈できません");
  const obj = JSON.parse(text.slice(start, end + 1));
  return {
    title: String(obj.title || current.title).trim(),
    html: String(obj.html || current.html).trim(),
  };
}

/** OpenAI DALL-E 3 で画像生成し、PNG バイト列を返す */
export async function generateImageBytes(prompt: string): Promise<{
  bytes: Uint8Array;
  contentType: string;
}> {
  const apiKey = process.env.OPENAI_API_KEY;
  if (!apiKey) throw new Error("OPENAI_API_KEY not set");

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
    throw new Error(`DALL-E error ${res.status}: ${txt.slice(0, 300)}`);
  }
  const data = await res.json();
  const b64 = data?.data?.[0]?.b64_json;
  if (!b64) throw new Error("DALL-E 応答に b64_json が無い");
  return { bytes: Buffer.from(b64, "base64"), contentType: "image/png" };
}

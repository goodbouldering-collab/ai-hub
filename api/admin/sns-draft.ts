/**
 * POST /api/admin/sns-draft
 * テーマを受け取り、OpenAI で SNS 投稿用の下書きテキストを生成する。
 */

import { ValidationError, withAdmin } from "../_lib/http.js";
import { requestAiText } from "../_lib/openai-text.js";

const SNS_DRAFT_PROMPT = `あなたは SNS 運用のプロです。
クライミング・ボルダリング事業オーナー「由井辰美」のアカウントとして、
X (Twitter) と Threads に同時投稿するテキストを生成します。

ルール:
- 140文字以内（日本語）
- 絵文字を適度に使う（1〜3個）
- ハッシュタグを 1〜2個付ける（#クライミング / #ボルダリング / #AIツール 等から適切なものを選ぶ）
- 実用的・興味を引く内容。宣伝ではなく情報・共感を重視
- 末尾に URL などは入れない（URL は UI 側で付加可能）

出力は投稿テキストのみ。前置き・コードフェンス禁止。`;

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const theme = String(body?.theme || "").trim();
  if (!theme) throw new ValidationError("theme is required");

  const text = await requestAiText({
    max_tokens: 512,
    system: SNS_DRAFT_PROMPT,
    messages: [{ role: "user", content: `テーマ: ${theme}` }],
  });

  res.status(200).json({ text });
});

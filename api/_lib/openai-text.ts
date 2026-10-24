import { requireEnv, openaiModel } from "./config.js";
import { ValidationError } from "./http.js";

export async function requestAiText(options: {
  system: string;
  messages: { role: "user" | "assistant"; content: string }[];
  max_tokens: number;
}, signal?: AbortSignal): Promise<string> {
  const response = await fetch("https://api.openai.com/v1/responses", {
    method: "POST", redirect: "error",
    signal: signal || AbortSignal.timeout(55_000),
    headers: { Authorization: `Bearer ${requireEnv("OPENAI_API_KEY")}`, "Content-Type": "application/json" },
    body: JSON.stringify({ model: openaiModel(), instructions: options.system,
      input: options.messages, max_output_tokens: options.max_tokens * 2, store: false }),
  });
  if (!response.ok) {
    const error = Object.assign(new Error(`OpenAI HTTP ${response.status}`), { status: response.status });
    throw error;
  }
  const data = await response.json();
  if (data.status !== "completed") throw new ValidationError("AI応答が完了していません");
  const text = (data.output || []).filter((item: any) => item.type === "message")
    .flatMap((item: any) => item.content || [])
    .filter((block: any) => block.type === "output_text" && typeof block.text === "string")
    .map((block: any) => block.text).join("\n").trim();
  if (!text) throw new ValidationError("AI応答にテキストがありません");
  return text;
}

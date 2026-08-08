import { withAdmin } from "../_lib/http.js";

type BriefInput = { symbol?: string; name?: string; decision?: string; whyNow?: string; firstRisk?: string; investableWhen?: string; killCondition?: string };
function fallback(input: BriefInput) {
  const label = input.name || input.symbol || "銘柄";
  return { headline: `${label}は${input.decision === "buy_candidate" ? "監視候補" : "条件確認"}`, whyNow: input.whyNow || "価格と出来高の変化を確認します。", invalidation: input.killCondition || input.firstRisk || "前提が崩れたら判断を見直します。", nextCheck: input.investableWhen || "一次情報と現在値を再確認します。" };
}
function outputText(payload: any): string { return payload?.output?.flatMap((item: any) => item.content || []).find((item: any) => item.type === "output_text")?.text || ""; }

export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const input = (body && typeof body === "object" ? body : {}) as BriefInput;
  const basic = fallback(input);
  const key = process.env.OPENAI_API_KEY;
  if (!key) { res.setHeader("Cache-Control", "private, no-store"); res.status(200).json({ ai: false, brief: basic, note: "AI未接続のためルールベースで表示" }); return; }
  try {
    const response = await fetch("https://api.openai.com/v1/responses", { method: "POST", headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" }, signal: AbortSignal.timeout(15_000), body: JSON.stringify({ model: process.env.OPENAI_MODEL || "gpt-5.6-luna", store: false, reasoning: { effort: "low" }, instructions: "与えられた市場データだけを使い、日本語で短い確認メモを作る。売買注文を勧めず、リスクと次の確認を書く。", input: JSON.stringify(input), text: { verbosity: "low", format: { type: "json_schema", name: "market_brief", strict: true, schema: { type: "object", additionalProperties: false, properties: { headline: { type: "string" }, whyNow: { type: "string" }, invalidation: { type: "string" }, nextCheck: { type: "string" } }, required: ["headline", "whyNow", "invalidation", "nextCheck"] } } } }) });
    if (response.ok) {
      const text = outputText(await response.json());
      const brief = text ? JSON.parse(text) : basic;
      res.setHeader("Cache-Control", "private, no-store"); res.status(200).json({ ai: true, brief }); return;
    }
  } catch { /* fallback below */ }
  res.setHeader("Cache-Control", "private, no-store"); res.status(200).json({ ai: false, brief: basic, note: "AI応答を検証できないためルールベースで表示" });
});

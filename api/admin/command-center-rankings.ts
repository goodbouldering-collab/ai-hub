import { withAdmin } from "../_lib/http.js";

type Candidate = { symbol?: string; name?: string; score?: number; decision?: string; whyNow?: string; firstRisk?: string; investableWhen?: string; killCondition?: string };
function clean(value: unknown, max = 180): string { return typeof value === "string" ? value.replace(/\s+/g, " ").trim().slice(0, max) : ""; }
function brief(candidate: Candidate) {
  const score = Number(candidate.score) || 0;
  return { headline: `${clean(candidate.name, 60) || clean(candidate.symbol, 20)}は${score >= 74 ? "監視候補" : score >= 58 ? "条件確認" : "見送り"}`, whyNow: clean(candidate.whyNow) || "値動きの根拠を確認します。", invalidation: clean(candidate.killCondition) || clean(candidate.firstRisk) || "前提が崩れたら見直します。", nextCheck: clean(candidate.investableWhen) || "一次情報と現在値を再確認します。" };
}
export default withAdmin({ method: "POST" }, async ({ res, body }) => {
  const candidates = Array.isArray(body?.candidates) ? body.candidates.slice(0, 16) as Candidate[] : [];
  if (!candidates.length) { res.status(400).json({ error: "candidates_required" }); return; }
  const briefs = Object.fromEntries(candidates.map((candidate) => [clean(candidate.symbol, 20).toUpperCase(), brief(candidate)]));
  res.setHeader("Cache-Control", "private, no-store, max-age=0"); res.status(200).json({ ai: false, providers: [], briefs });
});

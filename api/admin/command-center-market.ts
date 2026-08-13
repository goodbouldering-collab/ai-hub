import { withAdmin } from "../_lib/http.js";
import { buildCommandCenterMarket } from "../_lib/command-center-market.js";
import { callMarketCompass } from "../_lib/market-compass-client.js";

type MarketDependencies = {
  callService: (path: string, init?: RequestInit) => Promise<any>;
  buildLocal: (symbols: string[]) => Promise<any>;
};

const SERVICE_FALLBACK_MESSAGE = "財務スクリーナーへ接続できないため価格データへフォールバックしました。";

function normalizedDecision(value: unknown): "research_candidate" | "watch" | "deprioritize" | "insufficient_data" {
  if (value === "research_candidate" || value === "watch" || value === "deprioritize" || value === "insufficient_data") return value;
  if (value === "buy_candidate") return "research_candidate";
  if (value === "avoid" || value === "sell_candidate") return "deprioritize";
  return "insufficient_data";
}

function sanitizeCandidates(candidates: unknown): any[] {
  if (!Array.isArray(candidates)) return [];
  return candidates
    .filter((candidate): candidate is Record<string, unknown> => Boolean(candidate) && typeof candidate === "object" && typeof (candidate as Record<string, unknown>).symbol === "string")
    .map((candidate) => ({ ...candidate, decision: normalizedDecision(candidate.decision) }));
}

function symbolsFromRequest(rawUrl: string | undefined): string[] {
  const url = new URL(rawUrl || "/api/admin/command-center/market", "https://aiclimb.vercel.app");
  return (url.searchParams.get("symbols") || "")
    .split(",")
    .map((value) => value.trim().toUpperCase())
    .filter((value) => /^[A-Z0-9.\-]{1,12}$/.test(value))
    .slice(0, 24);
}

export function createCommandCenterMarketHandler(dependencies: Partial<MarketDependencies> = {}) {
  const callService = dependencies.callService ?? ((path: string, init?: RequestInit) => callMarketCompass(path, init));
  const buildLocal = dependencies.buildLocal ?? buildCommandCenterMarket;

  return withAdmin({ method: "GET" }, async ({ req, res }) => {
    const symbols = symbolsFromRequest(req.url);
    const localPayload = await buildLocal(symbols);
    const localCandidates = sanitizeCandidates(localPayload?.candidates);
    const localUsCandidates = localCandidates.filter((candidate) => candidate.market === "US");
    const japaneseSymbols = symbols.filter((symbol) => /^\d{4}$/.test(symbol));
    const query = japaneseSymbols.length ? `?symbols=${encodeURIComponent(japaneseSymbols.join(","))}` : "";

    let payload: Record<string, unknown>;
    try {
      const servicePayload = await callService(`/api/v1/market${query}`);
      const serviceCandidates = sanitizeCandidates(servicePayload?.candidates);
      payload = {
        ...localPayload,
        ...servicePayload,
        providerMode: "market_compass_service",
        candidates: [...serviceCandidates, ...localUsCandidates],
      };
    } catch {
      payload = {
        ...localPayload,
        providerMode: "local_fallback",
        candidates: localCandidates,
        missingEvidence: [...new Set([...(Array.isArray(localPayload?.missingEvidence) ? localPayload.missingEvidence : []), SERVICE_FALLBACK_MESSAGE])],
      };
    }

    res.setHeader("Cache-Control", "private, no-store, max-age=0");
    res.setHeader("Pragma", "no-cache");
    res.status(200).json(payload);
  });
}

export default createCommandCenterMarketHandler();

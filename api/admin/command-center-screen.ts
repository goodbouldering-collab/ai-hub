import { ValidationError, withAdmin } from "../_lib/http.js";
import { callMarketCompass } from "../_lib/market-compass-client.js";

type Dependencies = {
  callService: (path: string, init?: RequestInit) => Promise<any>;
};

const OVERALL_STATUSES = new Set(["research_candidate", "watch", "deprioritize", "insufficient_data"]);

function validSymbols(value: unknown): string[] {
  if (!Array.isArray(value) || value.length < 1 || value.length > 24) throw new ValidationError("symbols must contain 1 to 24 Japanese stock codes");
  const symbols = [...new Set(value.map((item) => String(item).trim()).filter(Boolean))];
  if (symbols.length < 1 || symbols.some((symbol) => !/^\d{4}$/.test(symbol))) throw new ValidationError("symbols must be four-digit Japanese stock codes");
  return symbols;
}

function validOverall(value: unknown): string[] | undefined {
  if (value === undefined) return undefined;
  if (!Array.isArray(value) || value.some((item) => !OVERALL_STATUSES.has(String(item)))) throw new ValidationError("filters.overall is invalid");
  return [...new Set(value.map(String))];
}

export function createCommandCenterScreenHandler(dependencies: Partial<Dependencies> = {}) {
  const callService = dependencies.callService ?? ((path: string, init?: RequestInit) => callMarketCompass(path, init));
  return withAdmin({ method: "POST", parseBody: true }, async ({ body, res }) => {
    const symbols = validSymbols(body?.symbols);
    const overall = validOverall(body?.filters?.overall);
    const payload = await callService("/api/v1/screens", {
      method: "POST",
      body: JSON.stringify({ symbols, ...(overall ? { filters: { overall } } : {}) }),
    });
    res.setHeader("Cache-Control", "private, no-store, max-age=0");
    res.status(200).json(payload);
  });
}

export default createCommandCenterScreenHandler();

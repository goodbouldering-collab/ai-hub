import { ValidationError, withAdmin } from "../_lib/http.js";
import { callMarketCompass } from "../_lib/market-compass-client.js";

type Dependencies = {
  callService: (path: string, init?: RequestInit) => Promise<any>;
};

export function createCommandCenterSecurityHandler(dependencies: Partial<Dependencies> = {}) {
  const callService = dependencies.callService ?? ((path: string, init?: RequestInit) => callMarketCompass(path, init));
  return withAdmin({ method: "GET" }, async ({ req, res }) => {
    const url = new URL(req.url || "/api/admin/command-center/security", "https://aiclimb.vercel.app");
    const symbol = (url.searchParams.get("symbol") || "").trim();
    if (!/^\d{4}$/.test(symbol)) throw new ValidationError("symbol must be a four-digit Japanese stock code");
    const payload = await callService(`/api/v1/securities/${encodeURIComponent(symbol)}`);
    res.setHeader("Cache-Control", "private, no-store, max-age=0");
    res.status(200).json(payload);
  });
}

export default createCommandCenterSecurityHandler();

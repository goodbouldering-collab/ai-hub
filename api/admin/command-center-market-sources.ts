import { withAdmin } from "../_lib/http.js";
import { callMarketCompass } from "../_lib/market-compass-client.js";

type Dependencies = {
  callService: (path: string, init?: RequestInit) => Promise<any>;
};

export function createCommandCenterMarketSourcesHandler(dependencies: Partial<Dependencies> = {}) {
  const callService = dependencies.callService ?? ((path: string, init?: RequestInit) => callMarketCompass(path, init));
  return withAdmin({ method: "GET" }, async ({ res }) => {
    const payload = await callService("/api/v1/sources/status");
    res.setHeader("Cache-Control", "private, no-store, max-age=0");
    res.status(200).json(payload);
  });
}

export default createCommandCenterMarketSourcesHandler();

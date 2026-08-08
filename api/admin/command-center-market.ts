import { withAdmin } from "../_lib/http.js";
import { buildCommandCenterMarket } from "../_lib/command-center-market.js";

export default withAdmin({ method: "GET" }, async ({ req, res }) => {
  const url = new URL(req.url || "/api/admin/command-center/market", "https://ai-hub-jp.vercel.app");
  const symbols = (url.searchParams.get("symbols") || "").split(",").map((value) => value.trim().toUpperCase()).filter((value) => /^[A-Z0-9.\-]{1,12}$/.test(value)).slice(0, 24);
  const payload = await buildCommandCenterMarket(symbols);
  res.setHeader("Cache-Control", "private, no-store, max-age=0");
  res.setHeader("Pragma", "no-cache");
  res.status(200).json(payload);
});

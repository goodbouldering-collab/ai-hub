/**
 * /api/admin/gubble-sns-metrics
 * GET -> ぐっぼる SNS / SEO ダッシュボード用の sns-metrics.js を返す。
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

let cachedMetrics: string | null = null;

function loadMetricsJs(): string {
  if (cachedMetrics) return cachedMetrics;
  const p = join(process.cwd(), "site", "static", "admin", "sns-metrics.js");
  cachedMetrics = readFileSync(p, "utf-8");
  return cachedMetrics;
}

export default withAdmin({ method: "GET" }, async ({ res }) => {
  res.setHeader("Content-Type", "text/javascript; charset=utf-8");
  res.status(200).send(loadMetricsJs());
});

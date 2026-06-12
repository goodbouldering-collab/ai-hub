/**
 * /api/admin/gubble-sns
 * GET -> SNS Cross Media Dashboard HTML を返す。
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

let cachedHtml: string | null = null;

function loadDashboardHtml(): string {
  if (cachedHtml) return cachedHtml;
  const p = join(process.cwd(), "site", "static", "admin", "sns-cross-media-dashboard.html");
  cachedHtml = readFileSync(p, "utf-8");
  return cachedHtml;
}

export default withAdmin({ method: "GET" }, async ({ res }) => {
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.status(200).send(loadDashboardHtml());
});

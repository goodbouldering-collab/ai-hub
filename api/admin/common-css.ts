/**
 * /admin/admin-common.css
 * 管理ページ群で共有する固定ヘッダー/管理メニューCSSを返す。
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

let cachedCss: string | null = null;

function loadCss(): string {
  if (cachedCss) return cachedCss;
  const p = join(process.cwd(), "site", "static", "admin", "admin-common.css");
  cachedCss = readFileSync(p, "utf-8");
  return cachedCss;
}

export default withAdmin({ method: "GET" }, async ({ res }) => {
  res.setHeader("Content-Type", "text/css; charset=utf-8");
  res.setHeader("Cache-Control", "private, no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.status(200).send(loadCss());
});

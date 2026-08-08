import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

const VIEWS = new Set(["dashboard", "calendar", "tasks", "businesses", "directives", "studio", "tools", "trade"]);
let cachedHtml: string | null = null;

export default withAdmin({ method: "GET" }, async ({ req, res }) => {
  const rawView = req.query?.view;
  const view = Array.isArray(rawView) ? rawView[0] : rawView;
  const selected = typeof view === "string" && VIEWS.has(view) ? view : "dashboard";
  if (!cachedHtml) cachedHtml = readFileSync(join(process.cwd(), "site", "static", "admin", "command-center.html"), "utf8");
  const html = cachedHtml.replace('data-view="dashboard"', `data-view="${selected}"`);
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "private, no-store, max-age=0");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.status(200).send(html);
});

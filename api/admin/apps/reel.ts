import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../../_lib/http.js";

let cachedHtml: string | null = null;

export default withAdmin({ method: "GET" }, async ({ res }) => {
  if (!cachedHtml) {
    const path = join(process.cwd(), "site", "static", "admin", "apps", "reel.html");
    cachedHtml = readFileSync(path, "utf-8");
  }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "private, no-store");
  res.status(200).send(cachedHtml);
});

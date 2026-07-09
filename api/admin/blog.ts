import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

let cachedHtml: string | null = null;

export default withAdmin({ method: "GET" }, async ({ res }) => {
  if (!cachedHtml) {
    try {
      const p = join(process.cwd(), "site", "static", "admin", "blog.html");
      cachedHtml = readFileSync(p, "utf-8");
    } catch (e: any) {
      res.status(500).send("admin blog html not found: " + e.message);
      return;
    }
  }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.status(200).send(cachedHtml);
});

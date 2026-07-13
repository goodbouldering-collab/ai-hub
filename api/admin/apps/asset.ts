import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../../_lib/http.js";

const CONTENT_TYPES: Record<string, string> = {
  "reel.js": "text/javascript; charset=utf-8",
  "studio-core.js": "text/javascript; charset=utf-8",
  "styles.css": "text/css; charset=utf-8",
  "styles-content.css": "text/css; charset=utf-8",
};

export default withAdmin({ method: "GET" }, async ({ req, res }) => {
  const rawFile = req.query?.file;
  const file = Array.isArray(rawFile) ? rawFile[0] : rawFile;

  if (!file || !CONTENT_TYPES[file]) {
    res.status(404).json({ error: "Studio asset not found" });
    return;
  }

  const path = join(process.cwd(), "site", "static", "admin", "apps", file);
  const body = readFileSync(path);
  res.setHeader("Content-Type", CONTENT_TYPES[file]);
  res.setHeader("Cache-Control", "private, no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.status(200).send(body);
});

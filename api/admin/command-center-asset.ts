import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

const ASSETS: Record<string, { file: string; type: string }> = {
  css: { file: "command-center.css", type: "text/css; charset=utf-8" },
  js: { file: "command-center.js", type: "application/javascript; charset=utf-8" },
};

export default withAdmin({ method: "GET" }, async ({ req, res }) => {
  const rawFile = req.query?.file;
  const file = Array.isArray(rawFile) ? rawFile[0] : rawFile;
  const asset = typeof file === "string" ? ASSETS[file] : undefined;
  if (!asset) { res.status(404).json({ error: "command_center_asset_not_found" }); return; }
  res.setHeader("Content-Type", asset.type);
  res.setHeader("Cache-Control", "private, no-store, max-age=0");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.status(200).send(readFileSync(join(process.cwd(), "site", "static", "admin", asset.file)));
});

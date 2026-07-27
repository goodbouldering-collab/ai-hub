/**
 * 管理ページ共通の固定メニューを返す。
 * HTML側はこの1ファイルを読み込み、ページごとの重複メニューを同じ構造へ置き換える。
 */
import { readFileSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

let cachedScript: string | null = null;

function loadScript(): string {
  if (cachedScript) return cachedScript;
  const path = join(process.cwd(), "site", "static", "admin", "admin-menu.js");
  cachedScript = readFileSync(path, "utf-8");
  return cachedScript;
}

export default withAdmin({ method: "GET" }, async ({ res }) => {
  res.setHeader("Content-Type", "application/javascript; charset=utf-8");
  res.setHeader("Cache-Control", "private, no-store");
  res.status(200).send(loadScript());
});

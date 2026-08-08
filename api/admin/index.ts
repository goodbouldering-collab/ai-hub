/**
 * /api/admin → 日常作業の先頭であるブログ管理を管理ログインゲートで返す。
 * vercel.json の rewrites で /admin と /admin/ を /api/admin に転送する。
 * 大きな管理トップ案内は置かず、共通固定メニューから各作業へ移動する。
 *
 * cachedHtml は同一 Function インスタンス内のホットリロードを高速化するため
 * モジュールスコープに置く。読み込み失敗時は cachedHtml を null のまま残し、
 * 次回リクエストで再試行する設計。
 */
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
      res.status(500).send("admin html not found: " + e.message);
      return;
    }
  }
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.status(200).send(cachedHtml);
});

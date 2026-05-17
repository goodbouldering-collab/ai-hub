/**
 * /api/ops → /ops のメインダッシュボード HTML を返す（Basic 認証必須）
 *
 * 設計（2026-05-17 CEO 指示の集大成ページ）:
 *  - 旧 /admin/docs（consul-work MD を全文展開＝ややこしい）を置換
 *  - スマホで開けば「これからやること / これまでやったこと / 日々のプロンプト」が分かる
 *  - データは既存 outputs/agents_status.json（/api/admin/status 経由）をそのまま使う＝新 DB なし
 *  - 原文 MD は本ページからは出さず、必要時だけ /api/ops/doc?file=... を折りたたみで取得
 *
 * HTML は site/static/ops/index.html に分離（メンテ性のため。docs はインライン巨大化していた反省）。
 * vercel.json の includeFiles に site/static/ops/** を追加すること。
 */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";
import { withAdmin } from "../_lib/http.js";

const HTML_CANDIDATES = [
  join(process.cwd(), "site", "static", "ops", "index.html"),
  join(process.cwd(), "..", "site", "static", "ops", "index.html"),
];

function resolveHtml(): string | null {
  for (const p of HTML_CANDIDATES) {
    if (existsSync(p)) return p;
  }
  return null;
}

export default withAdmin({ method: "GET" }, async ({ res }) => {
  const path = resolveHtml();
  if (!path) {
    res.setHeader("Content-Type", "text/html; charset=utf-8");
    res
      .status(500)
      .send(
        "<!DOCTYPE html><meta charset='utf-8'><body style='font-family:sans-serif;padding:40px'>" +
          "<h1>/ops テンプレートが見つかりません</h1>" +
          "<p>site/static/ops/index.html がデプロイに含まれているか確認してください" +
          "（vercel.json の functions.includeFiles に <code>site/static/ops/**</code> が必要）。</p>",
      );
    return;
  }
  const html = readFileSync(path, "utf-8");
  res.setHeader("Content-Type", "text/html; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.status(200).send(html);
});

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);
const marketViews = ["market", "screener", "security", "trade-plan", "trade-plans", "trades", "market-sources"];

function relativeLuminance(hex) {
  const channels = [1, 3, 5].map((index) => Number.parseInt(hex.slice(index, index + 2), 16) / 255);
  const [red, green, blue] = channels.map((value) => value <= 0.04045 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4);
  return 0.2126 * red + 0.7152 * green + 0.0722 * blue;
}

function contrastRatio(foreground, background) {
  const luminances = [relativeLuminance(foreground), relativeLuminance(background)].sort((left, right) => right - left);
  return (luminances[0] + 0.05) / (luminances[1] + 0.05);
}

test("market compass sections are independent protected views with a shared submenu", async () => {
  const html = await readFile(new URL("site/static/admin/command-center.html", root), "utf8");
  const page = await readFile(new URL("api/admin/command-center-page.ts", root), "utf8");
  const script = await readFile(new URL("site/static/admin/command-center.js", root), "utf8");
  const adminMenu = await readFile(new URL("site/static/admin/admin-menu.js", root), "utf8");
  for (const view of marketViews) {
    assert.match(html, new RegExp(`/admin/command-center/${view}`), `${view} menu`);
    assert.match(adminMenu, new RegExp(`/admin/command-center/${view}`), `${view} mobile admin menu`);
    assert.match(page, new RegExp(`\\b${view.replace("-", "\\-")}\\b`), `${view} page allowlist`);
    assert.match(script, new RegExp(`\\b${view.replace("-", "\\-")}\\b`), `${view} renderer`);
  }
  assert.match(html, /cc-market-nav/);
  assert.doesNotMatch(html, /<details class="cc-market-nav"\s+open>/);
  assert.match(script, /marketNavigation\.open\s*=\s*window\.innerWidth\s*>\s*640/);
  assert.match(script, /renderMarket/);
  assert.match(script, /renderScreener/);
  assert.match(script, /renderSecurity/);
  assert.match(script, /renderTradePlan/);
  assert.match(script, /renderTradePlans/);
  assert.match(script, /renderTrades/);
  assert.match(script, /renderMarketSources/);
});

test("market compass UI exposes all twelve primary-screen checks and verification sources", async () => {
  const script = await readFile(new URL("site/static/admin/command-center.js", root), "utf8");
  for (const label of [
    "売上高・営業利益", "自己資本比率", "配当性向", "連続増配年数", "PER",
    "営業キャッシュフロー", "有利子負債", "EPS", "配当の現金余力",
    "特別利益", "会社予想", "過去PER・PBR比較",
  ]) assert.match(script, new RegExp(label), label);
  for (const source of ["Yahoo!ファイナンス", "IR BANK", "企業IR", "EDINET"]) assert.match(script, new RegExp(source), source);
  assert.match(script, /一次スクリーニング/);
  assert.doesNotMatch(script, /buy_candidate|sell_candidate|買い推奨|売り推奨/);
});

test("market compass page routes and BFF routes are explicit before the generic rewrite", async () => {
  const vercel = JSON.parse(await readFile(new URL("vercel.json", root), "utf8"));
  const sources = vercel.rewrites.map((item) => item.source);
  const genericIndex = sources.indexOf("/admin/command-center/:view");
  for (const view of marketViews) {
    const index = sources.indexOf(`/admin/command-center/${view}`);
    assert.ok(index >= 0 && index < genericIndex, `${view} explicit rewrite`);
  }
  for (const route of [
    "/api/admin/command-center/screen",
    "/api/admin/command-center/security",
    "/api/admin/command-center/market-sources",
  ]) assert.ok(sources.includes(route), route);
});

test("command center does not ship styles for the discarded intro hero", async () => {
  const css = await readFile(new URL("site/static/admin/command-center.css", root), "utf8");
  assert.doesNotMatch(css, /\.cc-hero\b/);
  assert.doesNotMatch(css, /\.cc-private-badge\b/);
});

test("command center supporting text meets WCAG AA contrast on its light surfaces", async () => {
  const css = await readFile(new URL("site/static/admin/command-center.css", root), "utf8");
  const muted = css.match(/--cc-muted:\s*(#[0-9a-f]{6})/i)?.[1];
  assert.ok(muted, "--cc-muted must be a six-digit color");
  assert.ok(contrastRatio(muted, "#ffffff") >= 4.5, `${muted} must reach 4.5:1 on white`);
  assert.ok(contrastRatio(muted, "#f6f8ff") >= 4.5, `${muted} must reach 4.5:1 on the checklist surface`);
});

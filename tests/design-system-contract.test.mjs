import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const root = new URL("../", import.meta.url);

function hexToRgb(hex) {
  const value = hex.replace("#", "");
  const full = value.length === 3 ? value.split("").map((part) => part + part).join("") : value;
  return [0, 2, 4].map((index) => Number.parseInt(full.slice(index, index + 2), 16));
}

function relativeLuminance(hex) {
  const channels = hexToRgb(hex).map((channel) => {
    const value = channel / 255;
    return value <= 0.03928 ? value / 12.92 : ((value + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2];
}

function contrastRatio(foreground, background) {
  const first = relativeLuminance(foreground);
  const second = relativeLuminance(background);
  return (Math.max(first, second) + 0.05) / (Math.min(first, second) + 0.05);
}

function tokenValue(css, name) {
  const match = css.match(new RegExp(`${name}:\\s*(#[0-9a-f]{6})`, "i"));
  assert.ok(match, `missing ${name}`);
  return match[1];
}

test("semantic color tokens preserve readable text and actions", async () => {
  const css = await readFile(new URL("site/static/design-system/tokens.css", root), "utf8");

  const brand = tokenValue(css, "--ai-color-brand-600");
  const ink = tokenValue(css, "--ai-color-ink");
  const muted = tokenValue(css, "--ai-color-muted");
  const canvas = tokenValue(css, "--ai-color-canvas");
  const white = tokenValue(css, "--ai-color-white");

  assert.ok(contrastRatio(brand, white) >= 4.5, "primary CTA must meet WCAG AA");
  assert.ok(contrastRatio(ink, canvas) >= 7, "body copy should meet WCAG AAA");
  assert.ok(contrastRatio(muted, canvas) >= 4.5, "secondary copy must meet WCAG AA");

  for (const name of [
    "--ai-space-1", "--ai-space-2", "--ai-space-3", "--ai-space-4", "--ai-space-6",
    "--ai-radius-control", "--ai-radius-card", "--ai-focus-ring", "--ai-size-tap",
  ]) {
    assert.match(css, new RegExp(`${name}:`), name);
  }
});

test("deployed reference page documents audiences, surfaces, components, states and responsive rules", async () => {
  const html = await readFile(new URL("site/static/design-system/index.html", root), "utf8");
  const css = await readFile(new URL("site/static/design-system/design-system.css", root), "utf8");

  assert.match(html, /<html lang="ja">/);
  assert.match(html, /href="#main-content"[^>]*>本文へ移動/);
  assert.match(html, /href="\/design-system\/tokens\.css/);
  assert.match(html, /href="\/design-system\/design-system\.css/);
  assert.match(html, /<main[^>]*id="main-content"/);

  for (const phrase of [
    "地域の事業者", "学校・福祉施設", "AIが分からない", "公開トップ", "Blog制作",
    "Reel制作", "Command Center", "読み込み中", "該当なし", "確認が必要", "完了",
    "390px", "一画面一つの主行動",
  ]) {
    assert.match(html, new RegExp(phrase), phrase);
  }

  assert.match(html, /aria-live="polite"/);
  assert.match(html, /<label[^>]*for=/);
  assert.match(html, /<button[^>]*disabled/);
  assert.match(css, /@media\s*\(max-width:\s*720px\)/);
  assert.match(css, /@media\s*\(prefers-reduced-motion:\s*reduce\)/);
  assert.match(css, /:focus-visible/);
});

test("public top and every target admin surface consume the canonical token layer", async () => {
  const portal = await readFile(new URL("site/build_portal.py", root), "utf8");
  const adminCss = await readFile(new URL("site/static/admin/admin-common.css", root), "utf8");
  const studioCss = await readFile(new URL("site/static/admin/apps/styles.css", root), "utf8");
  const commandCss = await readFile(new URL("site/static/admin/command-center.css", root), "utf8");

  assert.match(portal, /href='\/design-system\/tokens\.css/);
  assert.match(portal, /--focus-blue:\s*var\(--ai-color-brand-600/);
  assert.match(adminCss, /^@import url\("\/design-system\/tokens\.css"\);/);
  assert.match(adminCss, /--admin-public-blue:\s*var\(--ai-color-brand-600/);
  assert.match(studioCss, /--green:var\(--ai-color-brand-600/);
  assert.match(commandCss, /--cc-blue:\s*var\(--ai-color-brand-600/);
});

test("Command Center keeps a page heading while protected data is loading", async () => {
  const html = await readFile(new URL("site/static/admin/command-center.html", root), "utf8");
  const css = await readFile(new URL("site/static/admin/command-center.css", root), "utf8");

  assert.match(html, /<main class="cc-shell">[\s\S]*<h1 class="cc-visually-hidden">実行指令室<\/h1>/);
  assert.match(css, /\.cc-visually-hidden\s*\{/);
});

test("shared admin navigation exposes the design reference without adding another desktop menu row", async () => {
  const source = await readFile(new URL("site/static/admin/admin-menu.js", root), "utf8");
  const header = {
    className: "site-header",
    id: "site-header",
    innerHTML: "",
    classList: { contains() { return false; } },
    querySelector(selector) {
      if (selector === "#mobile-toggle") return { addEventListener() {}, setAttribute() {}, getAttribute() { return "false"; } };
      if (selector === "#mobile-nav") return { hidden: true, classList: { toggle() {} }, addEventListener() {} };
      return null;
    },
  };
  const document = {
    title: "",
    body: { classList: { add() {}, toggle() {} }, dataset: {}, prepend() {} },
    querySelector() { return header; },
    createElement() { return header; },
    addEventListener() {},
  };
  const window = { location: { pathname: "/admin/apps/blog" }, innerWidth: 1280, addEventListener() {} };

  vm.runInNewContext(source, { document, window });

  const desktop = header.innerHTML.match(/<nav class="site-nav admin-slide-nav"[^>]*>(?<content>[\s\S]*?)<\/nav>/);
  const mobile = header.innerHTML.match(/<div class="mobile-nav-panel mobile-nav-panel--admin">(?<content>[\s\S]*)<\/div>/);
  assert.ok(desktop);
  assert.ok(mobile);
  assert.doesNotMatch(desktop.groups.content, /デザインシステム/);
  assert.match(mobile.groups.content, /href="\/design-system\/"[^>]*>[\s\S]*デザインシステム/);
});

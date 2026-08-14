import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const root = new URL("../", import.meta.url);
const menuSource = await readFile(new URL("site/static/admin/admin-menu.js", root), "utf8");
const adminTitle = "AI相談｜一歩踏み出す人のAI講習・実践支援【彦根・滋賀】";

function classList() {
  const values = new Set();
  return {
    add: (...names) => names.forEach((name) => values.add(name)),
    remove: (...names) => names.forEach((name) => values.delete(name)),
    toggle: (name, force) => {
      const shouldAdd = force === undefined ? !values.has(name) : force;
      if (shouldAdd) values.add(name);
      else values.delete(name);
      return shouldAdd;
    },
    contains: (name) => values.has(name),
  };
}

function runSharedMenu(pathname = "/admin/sns-post") {
  const toggle = {
    attributes: new Map(),
    addEventListener() {},
    setAttribute(name, value) { this.attributes.set(name, value); },
    getAttribute(name) { return this.attributes.get(name) ?? null; },
  };
  const panel = { hidden: true, classList: classList(), addEventListener() {} };
  const header = {
    className: "site-header scrolled",
    id: "site-header",
    innerHTML: "",
    classList: classList(),
    querySelector(selector) {
      if (selector === "#mobile-toggle") return toggle;
      if (selector === "#mobile-nav") return panel;
      return null;
    },
  };
  const body = { classList: classList(), dataset: {}, prepend() {} };
  const document = {
    title: "子ページ固有のタイトル",
    body,
    querySelector(selector) {
      return selector === "header.site-header, header.public-admin-header" ? header : null;
    },
    createElement() { return header; },
    addEventListener() {},
  };
  const window = { location: { pathname }, addEventListener() {} };

  vm.runInNewContext(menuSource, { document, window });
  return { body, header, document };
}

test("shared admin menu has no top item and gives mobile every management destination", () => {
  const { body, header } = runSharedMenu();
  const mobilePanel = header.innerHTML.match(
    /<div class="mobile-nav-panel mobile-nav-panel--admin">(?<content>[\s\S]*)<\/div>\s*<\/div>$/,
  );

  assert.equal(header.className, "site-header admin-shared-header");
  assert.equal(body.dataset.adminMenuReady, "true");
  assert.ok(mobilePanel, "shared header must render a mobile panel");
  assert.doesNotMatch(header.innerHTML, /管理トップ|管理ハブ/);
  assert.match(header.innerHTML, /href="\/admin"[^>]*aria-label="管理ホームへ戻る"/);

  for (const href of [
    "/admin/command-center",
    "/admin/blog",
    "/admin/apps/blog",
    "/admin/apps/reel/",
    "/admin/sns-post",
    "/admin/gubble-sns",
    "/admin/chat",
  ]) {
    assert.match(mobilePanel.groups.content, new RegExp(`href="${href.replaceAll("/", "\\/")}"`));
  }
});

test("nested admin pages show their parent context and a direct way back to the management home", () => {
  const cases = [
    ["/admin/command-center/calendar", "実行指令室 / カレンダー", "/admin/command-center"],
    ["/admin/command-center/market", "実行指令室 / 市場候補", "/admin/command-center"],
    ["/admin/command-center/screener", "実行指令室 / 財務スクリーナー", "/admin/command-center"],
    ["/admin/command-center/security", "実行指令室 / 銘柄詳細", "/admin/command-center"],
    ["/admin/command-center/trade-plan", "実行指令室 / 取引プラン作成", "/admin/command-center"],
    ["/admin/command-center/trade-plans", "実行指令室 / 登録プラン", "/admin/command-center"],
    ["/admin/command-center/trades", "実行指令室 / 取引記録", "/admin/command-center"],
    ["/admin/command-center/market-sources", "実行指令室 / データ収集状況", "/admin/command-center"],
    ["/admin/command-center.html", "実行指令室", "/admin/command-center"],
    ["/admin/blog", "ブログ管理", "/admin/blog"],
    ["/admin/blog.html", "ブログ管理", "/admin/blog"],
    ["/admin/blog/generate", "ブログ管理 / AI記事生成", "/admin/blog"],
    ["/admin/apps/blog", "ブログ制作", "/admin/apps/blog"],
    ["/admin/apps/blog.html", "ブログ制作", "/admin/apps/blog"],
    ["/admin/apps/reel", "リール制作", "/admin/apps/reel/"],
    ["/admin/apps/reel.html", "リール制作", "/admin/apps/reel/"],
    ["/ops/prompts", "OPS / プロンプト", "/ops"],
  ];

  for (const [pathname, context, currentHref] of cases) {
    const { header, document } = runSharedMenu(pathname);
    const expectedContext = context.replaceAll(" / ", "\\s*\\/\\s*");

    assert.match(header.innerHTML, /href="\/admin"[^>]*aria-label="管理ホームへ戻る"/);
    assert.match(header.innerHTML, new RegExp(`<strong>${expectedContext}</strong>`));
    assert.match(
      header.innerHTML,
      new RegExp(`href="${currentHref.replaceAll("/", "\\/")}"[^>]*aria-current="page"`),
    );
    assert.equal(document.title, adminTitle);
  }
});

test("every protected admin page loads the one shared fixed-menu runtime", async () => {
  const pages = [
    "site/static/admin/blog.html",
    "site/static/admin/chat.html",
    "site/static/admin/sns-post.html",
    "site/static/admin/gubble-sns.html",
    "site/static/admin/sns-cross-media-dashboard.html",
    "site/static/admin/index.html",
    "site/static/admin/hub.html",
    "site/static/admin/apps/blog.html",
    "site/static/admin/apps/reel.html",
    "site/static/admin/command-center.html",
    "site/static/ops/index.html",
  ];

  for (const page of pages) {
    const html = await readFile(new URL(page, root), "utf8");
    assert.match(html, new RegExp(`<title>${adminTitle}</title>`));
    assert.match(html, /href="\/admin\/admin-common\.css/);
    assert.match(html, /src="\/admin\/admin-menu\.js"/);
  }
});

test("Blog studio is a protected shared-menu child with the same delivery contract as Reel", async () => {
  const vercel = JSON.parse(await readFile(new URL("vercel.json", root), "utf8"));
  const rewrites = new Map(vercel.rewrites.map((route) => [route.source, route.destination]));
  const blogHandler = await readFile(new URL("api/admin/apps/blog.ts", root), "utf8");
  const assets = await readFile(new URL("api/admin/apps/asset.ts", root), "utf8");

  for (const source of ["/admin/apps/blog", "/admin/apps/blog/", "/admin/apps/blog.html"]) {
    assert.equal(rewrites.get(source), "/api/admin/apps/blog", source);
  }
  assert.match(blogHandler, /withAdmin/);
  assert.match(blogHandler, /"blog\.html"/);
  assert.match(assets, /"blog\.js": "text\/javascript; charset=utf-8"/);
});

test("Blog and Reel studios use canonical child routes and the shared UI shell", async () => {
  for (const [page, script] of [
    ["site/static/admin/apps/blog.html", "blog.js"],
    ["site/static/admin/apps/reel.html", "reel.js"],
  ]) {
    const html = await readFile(new URL(page, root), "utf8");
    assert.match(html, /<body[^>]*admin-shared-menu-offset/);
    assert.match(html, /<header class="site-header" id="site-header">/);
    assert.match(html, /href="\/admin\/apps\/blog"/);
    assert.match(html, /href="\/admin\/apps\/reel"/);
    assert.match(html, /href="\/admin\/apps\/styles\.css"/);
    assert.match(html, /href="\/admin\/apps\/styles-content\.css"/);
    assert.match(html, new RegExp(`src="\\/admin\\/apps\\/${script}"`));
    assert.doesNotMatch(html, /href="\.\//);
    assert.doesNotMatch(html, /src="\.\//);
  }

  const reel = await readFile(new URL("site/static/admin/apps/reel.html", root), "utf8");
  const studioCore = await readFile(new URL("site/static/admin/apps/studio-core.js", root), "utf8");
  const css = await readFile(new URL("site/static/admin/admin-common.css", root), "utf8");

  assert.doesNotMatch(reel, /public-admin-header/);
  assert.match(studioCore, /"\/admin\/apps\/blog"/);
  assert.match(studioCore, /"\/admin\/apps\/reel"/);
  assert.match(css, /body\[data-app="blog"\],\s*body\[data-app="reel"\]/);
  assert.match(css, /body\.admin-studio-page\.admin-shared-menu-offset \.studio-tabs/);
});

test("tablet admin navigation stays in the shared header's single row", async () => {
  const css = await readFile(new URL("site/static/admin/admin-common.css", root), "utf8");

  assert.doesNotMatch(
    css,
    /--admin-shared-quick-height:\s*50px/,
    "a second fixed quick-navigation row must not be restored",
  );
  assert.match(
    css,
    /@media \(min-width: 721px\) and \(max-width: 1100px\) \{[\s\S]*?\.admin-shared-header \.site-nav\.admin-slide-nav \{[\s\S]*?position: static !important;[\s\S]*?display: flex !important;/,
    "tablet navigation must remain inside the header instead of dropping below it",
  );
  assert.match(
    css,
    /@media \(max-width: 720px\) \{[\s\S]*?\.admin-shared-header \.site-nav\.admin-slide-nav \{[\s\S]*?display: none !important;[\s\S]*?\.admin-shared-header \.mobile-toggle \{[\s\S]*?display: inline-grid !important;/,
    "only the narrow mobile layout may replace the single row with the shared drawer",
  );
  assert.match(
    css,
    /@media \(max-width: 720px\) \{[\s\S]*?body\.admin-page \.admin-shared-header \.mobile-toggle,\s*body\.ops-page \.admin-shared-header \.mobile-toggle,[\s\S]*?display: inline-grid !important;/,
    "the narrow mobile drawer must outrank the shared desktop toggle rule",
  );
  assert.match(
    css,
    /body\.admin-page header\.site-header\.admin-shared-header,\s*body\.ops-page header\.site-header\.admin-shared-header \{[\s\S]*?height: var\(--admin-shared-menu-height\) !important;/,
    "the actual fixed header must use the same height as the single-row navigation and drawer",
  );
});

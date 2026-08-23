import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const root = new URL("../", import.meta.url);
const menuSource = await readFile(new URL("site/static/admin/admin-menu.js", root), "utf8");
const adminTitle = "AIClimb｜AIで仕事を軽くする実践相談・伴走支援【彦根・滋賀】";

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
  const toggleListeners = new Map();
  const panelListeners = new Map();
  const documentListeners = new Map();
  const windowListeners = new Map();
  const groupListeners = new Map();
  const focusHistory = [];
  let activeElement = null;
  const toggleText = { textContent: "メニュー" };
  const toggle = {
    attributes: new Map(),
    addEventListener(name, handler) { toggleListeners.set(name, handler); },
    setAttribute(name, value) { this.attributes.set(name, value); },
    getAttribute(name) { return this.attributes.get(name) ?? null; },
    querySelector(selector) { return selector === ".mobile-toggle-text" ? toggleText : null; },
    focus() { activeElement = this; focusHistory.push("toggle"); },
  };
  const drawerFirst = {
    focus() { activeElement = this; focusHistory.push("drawer-first"); },
    getClientRects() { return [{}]; },
    closest(selector) { return selector === "a" ? this : null; },
  };
  const drawerLast = {
    focus() { activeElement = this; focusHistory.push("drawer-last"); },
    getClientRects() { return [{}]; },
  };
  const panel = {
    hidden: true,
    attributes: new Map(),
    classList: classList(),
    addEventListener(name, handler) { panelListeners.set(name, handler); },
    setAttribute(name, value) { this.attributes.set(name, value); },
    querySelectorAll() { return [drawerFirst, drawerLast]; },
    contains(element) { return element === drawerFirst || element === drawerLast; },
    closest() { return null; },
  };
  const mobileGroups = Array.from({ length: 5 }, (_, index) => ({
    open: index === 0,
    addEventListener(name, handler) { groupListeners.set(`${index}:${name}`, handler); },
    querySelector() { return { focus() {} }; },
  }));
  const mobileGroup = mobileGroups[0];
  const brand = {
    focus() { activeElement = this; focusHistory.push("brand"); },
  };
  const header = {
    className: "site-header scrolled",
    id: "site-header",
    innerHTML: "",
    classList: classList(),
    querySelector(selector) {
      if (selector === "#mobile-toggle") return toggle;
      if (selector === "#mobile-nav") return panel;
      if (selector === ".admin-shared-brand") return brand;
      return null;
    },
    querySelectorAll(selector) {
      if (selector === ".admin-menu-mobile-group") return mobileGroups;
      return [];
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
    addEventListener(name, handler) { documentListeners.set(name, handler); },
    get activeElement() { return activeElement; },
  };
  const window = {
    innerWidth: 390,
    location: { pathname },
    addEventListener(name, handler) { windowListeners.set(name, handler); },
  };

  vm.runInNewContext(menuSource, { document, window });
  return {
    body,
    brand,
    header,
    document,
    mobileGroup,
    panel,
    toggle,
    toggleText,
    focusables: { first: drawerFirst, last: drawerLast },
    focusHistory,
    window,
    listeners: {
      document: documentListeners,
      panel: panelListeners,
      toggle: toggleListeners,
      window: windowListeners,
    },
  };
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

test("shared admin menu groups related work by purpose on desktop and mobile", () => {
  const { header } = runSharedMenu("/admin/apps/reel");
  const desktopGroups = header.innerHTML.match(/class="admin-menu-desktop-group/g) ?? [];
  const mobileGroups = header.innerHTML.match(/class="admin-menu-mobile-group/g) ?? [];

  assert.equal(desktopGroups.length, 5, "the fixed row should show five scannable purpose groups");
  assert.equal(mobileGroups.length, 5, "the drawer should reuse the same five purpose groups");

  for (const [id, label, summary] of [
    ["operations", "運営", "予定・指示・資料"],
    ["publishing", "制作・発信", "記事・動画・SNS"],
    ["insights", "分析・相談", "反応・改善・相談"],
    ["market", "相場", "調査・計画・記録"],
    ["utility", "その他", "確認・設定"],
  ]) {
    assert.match(header.innerHTML, new RegExp(`data-menu-group="${id}"`));
    assert.match(header.innerHTML, new RegExp(`>${label}<`));
    assert.match(header.innerHTML, new RegExp(summary));
  }

  assert.match(
    header.innerHTML,
    /<details class="admin-menu-mobile-group is-current-group" data-menu-group="publishing" open>/,
    "the current mobile group should be expanded without exposing every group at once",
  );
  assert.match(header.innerHTML, /href="\/admin\/apps\/reel\/"[^>]*aria-current="page"/);
  assert.match(header.innerHTML, /ブログ管理[\s\S]*記事を編集して公開する/);
  assert.match(header.innerHTML, /SNS投稿[\s\S]*複数のSNSへ投稿する/);
});

test("shared fixed header keeps the public page one click away on desktop and mobile", async () => {
  const { header } = runSharedMenu("/admin/command-center");
  const css = await readFile(new URL("site/static/admin/admin-common.css", root), "utf8");
  const fixedBoundary = css.slice(css.lastIndexOf("/* ---- Fixed admin menu component boundary"));

  assert.match(
    header.innerHTML,
    /<a class="admin-public-page-link" href="\/" aria-label="AIClimb（AI相談）の公開ページを見る">公開ページ<\/a>\s*<button class="mobile-toggle"/,
    "the fixed header must expose a direct public-page link before the menu button",
  );
  assert.match(
    fixedBoundary,
    /\.admin-public-page-link \{[\s\S]*?min-height: 44px !important;[\s\S]*?display: inline-flex !important;/,
    "the direct public-page link must remain a usable fixed-header control",
  );
  assert.match(
    fixedBoundary,
    /@media \(max-width: 900px\) \{[\s\S]*?\.admin-public-page-link \{[\s\S]*?display: inline-flex !important;/,
    "the direct public-page link must stay available beside the mobile menu",
  );
});

test("Escape closes the mobile drawer without losing the selected group", () => {
  const { mobileGroup, toggle, toggleText, listeners } = runSharedMenu("/admin/apps/reel");

  listeners.toggle.get("click")();
  assert.equal(toggle.getAttribute("aria-expanded"), "true");
  assert.equal(toggleText.textContent, "閉じる");
  assert.equal(mobileGroup.open, true);

  listeners.document.get("keydown")({ key: "Escape" });

  assert.equal(toggle.getAttribute("aria-expanded"), "false");
  assert.equal(toggleText.textContent, "メニュー");
  assert.equal(mobileGroup.open, true, "reopening the drawer should retain the user's group context");
});

test("mobile drawer contains keyboard focus and restores it on every non-navigation close path", () => {
  const { brand, document, focusables, focusHistory, panel, toggle, listeners, window } =
    runSharedMenu("/admin/apps/reel");
  const keydown = listeners.document.get("keydown");

  listeners.toggle.get("click")();
  assert.equal(toggle.getAttribute("aria-expanded"), "true");
  assert.equal(panel.attributes.get("aria-hidden"), "false");
  assert.equal(panel.hidden, false);

  focusables.last.focus();
  let prevented = false;
  keydown({ key: "Tab", shiftKey: false, preventDefault() { prevented = true; } });
  assert.equal(prevented, true, "Tab from the final drawer control must wrap to the menu button");
  assert.equal(document.activeElement, toggle);

  prevented = false;
  keydown({ key: "Tab", shiftKey: true, preventDefault() { prevented = true; } });
  assert.equal(prevented, true, "Shift+Tab from the menu button must wrap to the final drawer control");
  assert.equal(document.activeElement, focusables.last);

  listeners.panel.get("click")({ target: panel });
  assert.equal(toggle.getAttribute("aria-expanded"), "false");
  assert.equal(panel.attributes.get("aria-hidden"), "true");
  assert.equal(panel.hidden, true);
  assert.equal(document.activeElement, toggle, "overlay close must return focus to its trigger");

  listeners.toggle.get("click")();
  focusables.first.focus();
  keydown({ key: "Escape", shiftKey: false, preventDefault() {} });
  assert.equal(toggle.getAttribute("aria-expanded"), "false");
  assert.equal(document.activeElement, toggle, "Escape close must return focus to its trigger");

  listeners.toggle.get("click")();
  focusables.first.focus();
  window.innerWidth = 1280;
  listeners.window.get("resize")();
  assert.equal(toggle.getAttribute("aria-expanded"), "false");
  assert.equal(document.activeElement, brand, "desktop resize must move focus to the visible brand link");
  assert.ok(focusHistory.includes("drawer-first"));
});

test("mobile drawer links close shared UI state without cancelling navigation", () => {
  const { body, focusables, panel, toggle, listeners } = runSharedMenu("/admin/apps/reel");
  listeners.toggle.get("click")();
  focusables.first.focus();
  let prevented = false;

  listeners.panel.get("click")({
    target: focusables.first,
    preventDefault() { prevented = true; },
  });

  assert.equal(prevented, false, "the shared menu must leave normal link navigation untouched");
  assert.equal(toggle.getAttribute("aria-expanded"), "false");
  assert.equal(panel.attributes.get("aria-hidden"), "true");
  assert.equal(panel.hidden, true);
  assert.equal(body.classList.contains("admin-shared-menu-open"), false);
});

test("nested admin pages show their parent context and a direct way back to the management home", () => {
  const cases = [
    ["/admin/command-center/calendar", "実行指令室 / カレンダー", "/admin/command-center"],
    ["/admin/command-center/market", "実行指令室 / 市場候補", "/admin/command-center/market"],
    ["/admin/command-center/screener", "実行指令室 / 財務スクリーナー", "/admin/command-center/screener"],
    ["/admin/command-center/security", "実行指令室 / 銘柄詳細", "/admin/command-center/security"],
    ["/admin/command-center/trade-plan", "実行指令室 / 取引プラン作成", "/admin/command-center/trade-plan"],
    ["/admin/command-center/trade-plans", "実行指令室 / 登録プラン", "/admin/command-center/trade-plans"],
    ["/admin/command-center/trades", "実行指令室 / 取引記録", "/admin/command-center/trades"],
    ["/admin/command-center/market-sources", "実行指令室 / データ収集状況", "/admin/command-center/market-sources"],
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
      new RegExp(`href="${currentHref.replaceAll("/", "\\/")}(?:\\?[^\"]*)?"[^>]*aria-current="page"`),
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
  assert.match(css, /body\.admin-studio-page \.studio-command-bar/);
});

test("Blog and Reel studios put the API key form first in the shared right-aligned command bar", async () => {
  for (const page of [
    "site/static/admin/apps/blog.html",
    "site/static/admin/apps/reel.html",
  ]) {
    const html = await readFile(new URL(page, root), "utf8");

    assert.match(html, /class="studio-command-bar"/);
    assert.match(html, /class="studio-api-form api-key-panel"/);
    assert.doesNotMatch(html, /class="topbar"/);
    assert.doesNotMatch(html, /class="studio-tabs"/);
  }

  const css = await readFile(new URL("site/static/admin/admin-common.css", root), "utf8");
  assert.match(
    css,
    /body\.admin-studio-page \.studio-command-bar \{[\s\S]*?display: grid !important;[\s\S]*?grid-template-columns: minmax\(0, 1fr\) minmax\(min-content, 680px\) !important;/,
    "studio pages must share one top command bar instead of retaining independent title and tab rows",
  );
  assert.match(
    css,
    /body\.admin-studio-page \.studio-api-form \{[\s\S]*?grid-column: 2 !important;[\s\S]*?justify-self: end !important;/,
    "the API key form must begin in the shared command bar's right-hand position",
  );
});

test("admin navigation follows the public 900px menu switch", async () => {
  const css = await readFile(new URL("site/static/admin/admin-common.css", root), "utf8");
  const fixedBoundary = css.slice(css.lastIndexOf("/* ---- Fixed admin menu component boundary"));

  assert.doesNotMatch(
    css,
    /--admin-shared-quick-height:\s*50px/,
    "a second fixed quick-navigation row must not be restored",
  );
  assert.match(
    fixedBoundary,
    /@media \(max-width: 900px\) \{[\s\S]*?\.admin-shared-header \.site-nav\.admin-slide-nav \{[\s\S]*?display: none !important;[\s\S]*?\.admin-shared-header \.mobile-toggle \{[\s\S]*?display: inline-flex !important;/,
    "admin must switch to the same hamburger layout as public at 900px",
  );
  assert.match(
    fixedBoundary,
    /\.mobile-toggle \{[\s\S]*?min-width: 94px !important;[\s\S]*?height: 44px !important;[\s\S]*?padding: 0 12px !important;[\s\S]*?gap: 8px !important;/,
    "the hamburger control must use the public text-button dimensions",
  );
  assert.match(
    css,
    /body\.admin-page header\.site-header\.admin-shared-header,\s*body\.ops-page header\.site-header\.admin-shared-header \{[\s\S]*?height: var\(--admin-shared-menu-height\) !important;/,
    "the actual fixed header must use the same height as the single-row navigation and drawer",
  );
  assert.match(menuSource, /class="mobile-toggle-icon"[\s\S]*class="mobile-toggle-text">メニュー/);
  assert.match(menuSource, /window\.innerWidth <= 900/);
});

test("desktop admin navigation uses the public right-aligned header geometry", async () => {
  const css = await readFile(new URL("site/static/admin/admin-common.css", root), "utf8");
  const fixedBoundary = css.slice(css.lastIndexOf("/* ---- Fixed admin menu component boundary"));

  assert.match(fixedBoundary, /\.site-header-inner \{[\s\S]*?max-width: 1400px !important;[\s\S]*?padding: 10px 18px !important;[\s\S]*?gap: 12px !important;/);
  assert.match(fixedBoundary, /\.site-nav\.admin-slide-nav \{[\s\S]*?flex: 0 0 auto !important;[\s\S]*?margin-left: auto !important;/);
  assert.match(fixedBoundary, /\.admin-scroll-menu \{[\s\S]*?width: auto !important;[\s\S]*?justify-content: flex-end !important;/);
});

test("page-local header styles cannot move the shared menu outside its fixed row", async () => {
  const css = await readFile(new URL("site/static/admin/admin-common.css", root), "utf8");

  assert.match(
    css,
    /header\.site-header\.admin-shared-header \.site-header-inner \{[\s\S]*?height: var\(--admin-shared-menu-height\) !important;[\s\S]*?display: flex !important;[\s\S]*?flex-direction: row !important;/,
    "a page-level .site-header-inner rule must not restore a taller, grid-based, or stacked header row",
  );
  assert.match(
    css,
    /header\.site-header\.admin-shared-header \.site-nav\.admin-slide-nav \{[\s\S]*?height: var\(--admin-shared-menu-row-height\) !important;[\s\S]*?display: flex !important;/,
    "the shared navigation must use a definite row height instead of resolving a percentage against page-local layout",
  );
});

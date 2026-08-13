import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import vm from "node:vm";

const root = new URL("../", import.meta.url);
const menuSource = await readFile(new URL("site/static/admin/admin-menu.js", root), "utf8");

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
    "/admin/apps/reel/",
    "/admin/sns-post",
    "/admin/gubble-sns",
    "/admin/chat",
  ]) {
    assert.match(mobilePanel.groups.content, new RegExp(`href="${href.replaceAll("/", "\\/")}"`));
  }
});

test("nested admin pages show their parent context and a direct way back to the management home", () => {
  const { header, document } = runSharedMenu("/admin/command-center/calendar");

  assert.match(header.innerHTML, /href="\/admin"[^>]*aria-label="管理ホームへ戻る"/);
  assert.match(header.innerHTML, /実行指令室\s*\/\s*カレンダー/);
  assert.match(header.innerHTML, /href="\/admin\/command-center"[^>]*aria-current="page"/);
  assert.equal(document.title, "AI相談｜一歩踏み出す人のAI講習・実践支援【彦根・滋賀】");
});

test("every protected admin page loads the one shared fixed-menu runtime", async () => {
  const pages = [
    "site/static/admin/blog.html",
    "site/static/admin/chat.html",
    "site/static/admin/sns-post.html",
    "site/static/admin/gubble-sns.html",
    "site/static/admin/sns-cross-media-dashboard.html",
    "site/static/admin/apps/reel.html",
    "site/static/admin/command-center.html",
    "site/static/ops/index.html",
  ];

  for (const page of pages) {
    const html = await readFile(new URL(page, root), "utf8");
    assert.match(html, /href="\/admin\/admin-common\.css/);
    assert.match(html, /src="\/admin\/admin-menu\.js"/);
  }
});

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

test("command center routes are protected and independent", async () => {
  const vercel = JSON.parse(await readFile(new URL("vercel.json", root), "utf8"));
  const sources = vercel.rewrites.map((item) => item.source);
  for (const route of [
    "/admin/command-center",
    "/admin/command-center/calendar",
    "/admin/command-center/tasks",
    "/admin/command-center/businesses",
    "/admin/command-center/directives",
    "/admin/command-center/studio",
    "/admin/command-center/tools",
    "/admin/command-center/trade",
  ]) assert.ok(sources.includes(route), route);
  assert.equal(sources.includes("/admin/status"), false);
});

test("command center uses protected admin handlers and no old public origin", async () => {
  const menu = await readFile(new URL("site/static/admin/admin-menu.js", root), "utf8");
  const api = await readFile(new URL("api/admin/command-center-data.ts", root), "utf8");
  assert.match(menu, /command-center/);
  assert.match(api, /withAdmin/);
  assert.doesNotMatch(api, /climbing-consult-daily-command\.goodbouldering\.chatgpt\.site/);
});

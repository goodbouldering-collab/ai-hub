import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);

test("command center HTML contains the protected independent shell and all views", async () => {
  const html = await readFile(new URL("site/static/admin/command-center.html", root), "utf8");
  assert.match(html, /noindex/);
  assert.match(html, /data-view="dashboard"/);
  for (const view of ["calendar", "tasks", "businesses", "directives", "studio", "tools", "trade", "market", "screener", "security", "trade-plan", "trade-plans", "trades", "market-sources"]) assert.match(html, new RegExp(`/admin/command-center/${view}`), view);
  assert.match(html, /command-center\.css/);
  assert.match(html, /command-center\.js/);
  assert.doesNotMatch(html, /COMMAND_CENTER_MIGRATION_TOKEN|SUPABASE_SERVICE_ROLE_KEY|climbing-consult-daily-command\.goodbouldering\.chatgpt\.site/);
});

test("command center starts directly with controls after the intro panel is removed", async () => {
  const html = await readFile(new URL("site/static/admin/command-center.html", root), "utf8");
  const script = await readFile(new URL("site/static/admin/command-center.js", root), "utf8");
  const css = await readFile(new URL("site/static/admin/command-center.css", root), "utf8");

  assert.match(html, /<main class="cc-shell">\s*<nav class="cc-local-nav"/);
  assert.doesNotMatch(html, /<header class="cc-hero">/);
  assert.doesNotMatch(html, /cc-generated-at/);
  assert.doesNotMatch(script, /cc-generated-at/);
  assert.match(css, /\.cc-shell\s*\{[^}]*padding:\s*0\s+0\s+64px;/);
  assert.doesNotMatch(css, /@media \(max-width: 640px\)\s*\{[^}]*\.cc-shell\s*\{[^}]*padding-top:/);
});

test("command center assets and page handler are protected", async () => {
  const page = await readFile(new URL("api/admin/command-center-page.ts", root), "utf8");
  const asset = await readFile(new URL("api/admin/command-center-asset.ts", root), "utf8");
  assert.match(page, /withAdmin/);
  assert.match(asset, /withAdmin/);
  assert.match(asset, /command-center\.css/);
});

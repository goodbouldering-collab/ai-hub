import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import path from "node:path";
import test from "node:test";

const repoRoot = path.resolve(import.meta.dirname, "..");

test("rendered salon states the monthly fee and safe LINE membership flow", async () => {
  const html = await readFile(
    path.join(repoRoot, "public", "index.html"),
    "utf8",
  );

  assert.match(html, /月額2,200円/);
  assert.match(html, /LINEメンバーシップ/);
  assert.match(html, /毎週火曜21:00/);
  assert.match(html, /聞くだけOK/);
  assert.match(html, /受付準備中/);
});

test("rendered salon does not expose the retired Stripe-to-OpenChat flow", async () => {
  const html = await readFile(
    path.join(repoRoot, "public", "index.html"),
    "utf8",
  );

  assert.doesNotMatch(html, /Stripe決済完了後にLINE招待を表示/);
  assert.doesNotMatch(html, /line\.me\/ti\/g2\//);
  assert.doesNotMatch(html, /有料登録して参加する/);
});

test("salon is the final item in the public mobile menu", async () => {
  const html = await readFile(
    path.join(repoRoot, "public", "index.html"),
    "utf8",
  );
  const menuStart = html.indexOf("class='mobile-public-links'");
  const menuEnd = html.indexOf("</nav>", menuStart);
  const mobileMenu = html.slice(menuStart, menuEnd);

  assert.ok(menuStart >= 0 && menuEnd > menuStart);
  assert.equal(
    mobileMenu.lastIndexOf("href='/#seven-day-courses'"),
    mobileMenu.lastIndexOf("href="),
  );
});

import assert from "node:assert/strict";
import { readFile, readdir, stat } from "node:fs/promises";
import path from "node:path";
import { test } from "node:test";

const publicRoot = path.resolve("public");

async function walk(directory) {
  const entries = await readdir(directory, { withFileTypes: true });
  const paths = [];
  for (const entry of entries) {
    const fullPath = path.join(directory, entry.name);
    if (entry.isDirectory()) paths.push(...(await walk(fullPath)));
    if (entry.isFile()) paths.push(fullPath);
  }
  return paths;
}

test("runtime configuration keeps public assets off the Worker request quota", async () => {
  const config = JSON.parse(await readFile("wrangler.jsonc", "utf8"));

  assert.equal(config.name, "aiclimb");
  assert.equal(config.main, "./worker/index.mjs");
  assert.equal(config.assets.directory, "./public");
  assert.equal(config.assets.binding, "ASSETS");
  assert.ok(Array.isArray(config.assets.run_worker_first));
  assert.ok(config.assets.run_worker_first.includes("/admin/*"));
  assert.ok(config.assets.run_worker_first.includes("/api/*"));
  assert.ok(!config.assets.run_worker_first.includes("/*"));
});

test("public deployment snapshot contains no Vercel reference or oversized asset", async () => {
  const files = await walk(publicRoot);
  assert.ok(files.length > 100);

  for (const file of files) {
    const relative = path.relative(publicRoot, file).replaceAll("\\", "/");
    const fileStat = await stat(file);
    assert.ok(fileStat.size <= 25 * 1024 * 1024, `${relative} is larger than 25 MiB`);
    assert.ok(!relative.startsWith(".vercel/"), `${relative} must not be public`);

    if (/\.(?:html|css|js|xml|txt)$/i.test(relative)) {
      const content = await readFile(file, "utf8");
      assert.doesNotMatch(content, /(?:aiclimb|ai-hub-jp)\.vercel\.app/i, relative);
    }
  }
});

test("public homepage matches the final Vercel production copy", async () => {
  const homepage = await readFile(path.join(publicRoot, "index.html"), "utf8");

  assert.match(homepage, /使えるAI、教えます。/);
  assert.match(homepage, /<strong>AI<\/strong><span>×<\/span><strong>経験 = 影響力<\/strong>/);
  assert.match(homepage, /プロが教える、あなたの知らないAI/);
  assert.doesNotMatch(homepage, /ちゃんと使えるAIを、一緒につくる。/);
  assert.doesNotMatch(homepage, /AIで作る前に、ゴールをつくる。/);
});

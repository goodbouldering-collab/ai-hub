import assert from "node:assert/strict";
import { readFile, stat } from "node:fs/promises";
import { test } from "node:test";

const videoPath = "site/dist/media/ai-consult-hikone-20260629/ai-consult-hikone-course.webm";

test("the built homepage keeps checkout on the dynamic API route", async () => {
  const html = await readFile("site/dist/index.html", "utf8");

  assert.match(html, /<h1[^>]*>[\s\S]*使えるAI、教えます。/);
  assert.ok(html.includes("method='post' action='/api/square/ai-salon-checkout'"));
});

test("the oversized video is excluded from Workers Static Assets", async () => {
  const [ignoreFile, video] = await Promise.all([
    readFile("site/dist/.assetsignore", "utf8"),
    stat(videoPath),
  ]);

  assert.ok(video.size > 25 * 1024 * 1024);
  assert.match(
    ignoreFile,
    /^media\/ai-consult-hikone-20260629\/ai-consult-hikone-course\.webm$/m,
  );
});

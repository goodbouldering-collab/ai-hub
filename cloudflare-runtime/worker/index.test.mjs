import assert from "node:assert/strict";
import { test } from "node:test";

import worker from "./index.mjs";

const assetHtml = "<!doctype html><title>AI相談</title>";
const env = {
  ASSETS: {
    async fetch(request) {
      return new Response(assetHtml, {
        headers: { "content-type": "text/html; charset=utf-8" },
      });
    },
  },
};

test("health is answered by Cloudflare without an origin", async () => {
  const response = await worker.fetch(
    new Request("https://aiclimb.aiclimb.workers.dev/health"),
    env,
  );

  assert.equal(response.status, 200);
  assert.equal(response.headers.get("x-aiclimb-delivery"), "cloudflare-worker");
  assert.deepEqual(await response.json(), {
    status: "ok",
    service: "aiclimb",
    delivery: "cloudflare-workers-static-assets",
  });
});

test("public pages are served from the bound Cloudflare assets", async () => {
  const response = await worker.fetch(
    new Request("https://aiclimb.aiclimb.workers.dev/"),
    env,
  );

  assert.equal(response.status, 200);
  assert.equal(response.headers.get("x-aiclimb-delivery"), "cloudflare-static-assets");
  assert.equal(await response.text(), assetHtml);
});

test("dynamic administration paths stay on Cloudflare and pause safely", async () => {
  const response = await worker.fetch(
    new Request("https://aiclimb.aiclimb.workers.dev/admin/login?next=%2Fadmin"),
    env,
  );

  assert.equal(response.status, 503);
  assert.equal(response.headers.get("location"), null);
  assert.equal(response.headers.get("x-aiclimb-delivery"), "cloudflare-migration-paused");
  assert.match(await response.text(), /Cloudflare版へ移行中/);
});

test("unknown public writes are rejected before reaching assets", async () => {
  const response = await worker.fetch(
    new Request("https://aiclimb.aiclimb.workers.dev/unknown", {
      method: "POST",
      body: "do-not-forward",
    }),
    env,
  );

  assert.equal(response.status, 405);
  assert.equal(response.headers.get("allow"), "GET, HEAD");
});

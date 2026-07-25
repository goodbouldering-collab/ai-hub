import assert from "node:assert/strict";
import test from "node:test";

const workerModule = await import("../dist/server/index.js");
const worker = workerModule.default;
const ctx = {
  passThroughOnException() {},
  waitUntil() {},
};

test("worker serves the generated homepage at the root URL", async () => {
  const requestedPaths = [];
  const env = {
    ASSETS: {
      async fetch(request) {
        const path = new URL(request.url).pathname;
        requestedPaths.push(path);
        return new Response("<h1>月額2,200円 AIオンラインサロン</h1>", {
          headers: { "content-type": "text/html; charset=utf-8" },
        });
      },
    },
  };

  const response = await worker.fetch(
    new Request("https://ai-sodan.example/"),
    env,
    ctx,
  );

  assert.equal(response.status, 200);
  assert.deepEqual(requestedPaths, ["/index.html"]);
  assert.match(await response.text(), /月額2,200円/);
});

test("worker proxies legacy APIs without changing method or raw body", async () => {
  const originalFetch = globalThis.fetch;
  let upstreamRequest;
  globalThis.fetch = async (request) => {
    upstreamRequest = request;
    return new Response("proxied", {
      status: 202,
      headers: {
        location: "https://ai-hub-jp.vercel.app/admin",
        "set-cookie": "session=test; Path=/; Secure",
      },
    });
  };

  try {
    const response = await worker.fetch(
      new Request("https://ai-sodan.example/api/stripe/webhook?test=1", {
        body: '{"raw":true}',
        headers: {
          "content-type": "application/json",
          "oai-sites-authorization": "Bearer private-sites-token",
        },
        method: "POST",
      }),
      undefined,
      ctx,
    );

    assert.equal(response.status, 202);
    assert.equal(
      upstreamRequest.url,
      "https://ai-hub-jp.vercel.app/api/stripe/webhook?test=1",
    );
    assert.equal(upstreamRequest.method, "POST");
    assert.equal(await upstreamRequest.text(), '{"raw":true}');
    assert.equal(
      upstreamRequest.headers.get("x-forwarded-host"),
      "ai-sodan.example",
    );
    assert.equal(
      upstreamRequest.headers.get("oai-sites-authorization"),
      null,
    );
    assert.equal(response.headers.get("cache-control"), "private, no-store, no-cache, must-revalidate, max-age=0");
    assert.equal(
      response.headers.get("location"),
      "https://ai-hub-jp.vercel.app/admin",
    );
    assert.match(response.headers.get("set-cookie") ?? "", /session=test/);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

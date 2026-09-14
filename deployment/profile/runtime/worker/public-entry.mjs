import { handleAdminAuth } from './admin-auth.mjs';

var __defProp = Object.defineProperty;
var __name = (target, value) => __defProp(target, "name", { value, configurable: true });

// worker/index.mjs
var DYNAMIC_PREFIXES = ["/api", "/admin", "/ops", "/watch"];
var DYNAMIC_FILES = /* @__PURE__ */ new Set([
  "/lectures/2026-05-claude-code-features.html",
  "/media/ai-consult-hikone-20260629/ai-consult-hikone-course.webm"
]);
function isDynamicPath(pathname) {
  if (DYNAMIC_FILES.has(pathname)) return true;
  return DYNAMIC_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)
  );
}
__name(isDynamicPath, "isDynamicPath");
function migrationUnavailable(pathname) {
  if (pathname === "/api" || pathname.startsWith("/api/")) {
    return Response.json({ error: "Cloudflare\u7248\u3078\u79FB\u884C\u4E2D\u3067\u3059\u3002" }, {
      status: 503,
      headers: {
        "cache-control": "no-store",
        "retry-after": "86400",
        "x-aiclimb-delivery": "cloudflare-migration-paused"
      }
    });
  }
  return new Response("Cloudflare\u7248\u3078\u79FB\u884C\u4E2D\u3067\u3059\u3002\u516C\u958B\u307E\u3067\u304A\u5F85\u3061\u304F\u3060\u3055\u3044\u3002", {
    status: 503,
    headers: {
      "cache-control": "no-store",
      "content-type": "text/plain; charset=utf-8",
      "retry-after": "86400",
      "x-aiclimb-delivery": "cloudflare-migration-paused"
    }
  });
}
__name(migrationUnavailable, "migrationUnavailable");
function healthResponse() {
  return Response.json(
    {
      status: "ok",
      service: "aiclimb",
      delivery: "cloudflare-workers-static-assets"
    },
    {
      headers: {
        "cache-control": "no-store",
        "x-aiclimb-delivery": "cloudflare-worker"
      }
    }
  );
}
__name(healthResponse, "healthResponse");
var index_default = {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.pathname === "/health") return healthResponse();
    const adminResponse = await handleAdminAuth(request, env);
    if (adminResponse) return adminResponse;
    if (isDynamicPath(url.pathname)) return migrationUnavailable(url.pathname);
    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method Not Allowed", {
        status: 405,
        headers: { allow: "GET, HEAD" }
      });
    }
    const assetResponse = await env.ASSETS.fetch(request);
    const response = new Response(assetResponse.body, assetResponse);
    response.headers.set("x-aiclimb-delivery", "cloudflare-static-assets");
    return response;
  }
};
export {
  index_default as default
};

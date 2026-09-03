const DYNAMIC_PREFIXES = ["/api", "/admin", "/ops", "/watch", "/seo-llmo-diagnosis"];
const DYNAMIC_FILES = new Set([
  "/lectures/2026-05-claude-code-features.html",
  "/media/ai-consult-hikone-20260629/ai-consult-hikone-course.webm",
]);

function isDynamicPath(pathname) {
  if (DYNAMIC_FILES.has(pathname)) return true;
  return DYNAMIC_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

function migrationUnavailable(pathname) {
  if (pathname === "/api" || pathname.startsWith("/api/")) {
    return Response.json({ error: "Cloudflare版へ移行中です。" }, {
      status: 503,
      headers: {
        "cache-control": "no-store",
        "retry-after": "86400",
        "x-aiclimb-delivery": "cloudflare-migration-paused",
      },
    });
  }
  return new Response("Cloudflare版へ移行中です。公開までお待ちください。", {
    status: 503,
    headers: {
      "cache-control": "no-store",
      "content-type": "text/plain; charset=utf-8",
      "retry-after": "86400",
      "x-aiclimb-delivery": "cloudflare-migration-paused",
    },
  });
}

function healthResponse() {
  return Response.json(
    {
      status: "ok",
      service: "aiclimb",
      delivery: "cloudflare-workers-static-assets",
    },
    {
      headers: {
        "cache-control": "no-store",
        "x-aiclimb-delivery": "cloudflare-worker",
      },
    },
  );
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/health") return healthResponse();
    if (isDynamicPath(url.pathname)) return migrationUnavailable(url.pathname);

    if (request.method !== "GET" && request.method !== "HEAD") {
      return new Response("Method Not Allowed", {
        status: 405,
        headers: { allow: "GET, HEAD" },
      });
    }

    const assetResponse = await env.ASSETS.fetch(request);
    const response = new Response(assetResponse.body, assetResponse);
    response.headers.set("x-aiclimb-delivery", "cloudflare-static-assets");
    return response;
  },
};

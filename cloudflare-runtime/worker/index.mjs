const FROZEN_DYNAMIC_ORIGIN = "https://aiclimb.vercel.app";

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

function redirectToFrozenOrigin(url) {
  const destination = new URL(url.pathname + url.search, FROZEN_DYNAMIC_ORIGIN);
  return new Response(null, {
    status: 307,
    headers: {
      location: destination.toString(),
      "cache-control": "no-store",
      "x-aiclimb-delivery": "direct-to-frozen-origin",
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
    if (isDynamicPath(url.pathname)) return redirectToFrozenOrigin(url);

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

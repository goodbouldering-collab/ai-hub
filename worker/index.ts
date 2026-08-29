const VERCEL_ORIGIN = new URL("https://aiclimb.vercel.app");

function healthResponse(): Response {
  return Response.json(
    {
      status: "ok",
      service: "aiclimb",
      delivery: "cloudflare-workers-static-assets",
    },
    {
      headers: {
        "cache-control": "no-store",
        "x-content-type-options": "nosniff",
        "x-aiclimb-delivery": "cloudflare-worker",
      },
    },
  );
}

function redirectToVercel(incomingUrl: URL): Response {
  const target = new URL(incomingUrl.pathname + incomingUrl.search, VERCEL_ORIGIN);
  return new Response(null, {
    status: 307,
    headers: {
      location: target.toString(),
      "cache-control": "no-store",
      "x-content-type-options": "nosniff",
      "referrer-policy": "no-referrer",
      "x-aiclimb-delivery": "direct-to-vercel",
    },
  });
}

export default {
  async fetch(request: Request): Promise<Response> {
    const incomingUrl = new URL(request.url);
    if (incomingUrl.pathname === "/health") {
      return healthResponse();
    }

    return redirectToVercel(incomingUrl);
  },
} satisfies ExportedHandler<Env>;
